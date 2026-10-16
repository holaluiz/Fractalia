#include "Core/NRGameMode.h"

#include "AI/NRBotController.h"
#include "Camera/PlayerCameraManager.h"
#include "Core/NRGameState.h"
#include "Core/NRPlayerState.h"
#include "Core/NRSessaoSubsystem.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NexusRoyale.h"
#include "TimerManager.h"

namespace
{
	/** "BP_Creep_Imp_C" -> "Imp": nome legível de quem eliminou, quando não foi um jogador. */
	FString NomeDaCausa(const AActor* Causa)
	{
		if (!Causa)
		{
			return TEXT("Tempestade");
		}
		FString Nome = Causa->GetClass()->GetName();
		Nome.RemoveFromStart(TEXT("BP_"));
		Nome.RemoveFromEnd(TEXT("_C"));
		Nome.RemoveFromStart(TEXT("Creep_"));
		return Nome;
	}

	/** Jogadores que contam para a partida (humanos e bots conectados; espectadores não). */
	int32 ContarJogadores(const AGameStateBase* GS)
	{
		int32 Total = 0;
		for (const APlayerState* PS : GS->PlayerArray)
		{
			if (Cast<ANRPlayerState>(PS) && !PS->IsInactive() && !PS->IsSpectator())
			{
				++Total;
			}
		}
		return Total;
	}
}

ANRGameMode::ANRGameMode()
{
	GameStateClass = ANRGameState::StaticClass();
	PlayerStateClass = ANRPlayerState::StaticClass();
}

ANRGameState* ANRGameMode::GetNRGameState() const
{
	return GetGameState<ANRGameState>();
}

ENRFaseDaPartida ANRGameMode::GetFase() const
{
	const ANRGameState* GS = GetNRGameState();
	return GS ? GS->Fase : ENRFaseDaPartida::Nenhuma;
}

double ANRGameMode::Agora() const
{
	// O mesmo relógio que os clientes leem (GetServerWorldTimeSeconds); no servidor é o tempo do mundo.
	return GameState ? GameState->GetServerWorldTimeSeconds() : GetWorld()->GetTimeSeconds();
}

int32 ANRGameMode::XPDeAbate(int32 NivelVitima, int32 NivelAssassino) const
{
	const float Base = static_cast<float>(FMath::Max(XPAbateMinimo, XPAbatePorNivel * NivelVitima));
	const float Fator = FMath::Clamp(1.f + XPAbateFatorPorNivel * static_cast<float>(NivelVitima - NivelAssassino),
		XPAbateFatorMinimo, XPAbateFatorMaximo);
	return FMath::RoundToInt(Base * Fator);
}

// ------------------------------------------------------------------------------------------------ Ciclo de vida

void ANRGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);
	if (UNRSessaoSubsystem* Sessao = GetGameInstance() ? GetGameInstance()->GetSubsystem<UNRSessaoSubsystem>() : nullptr)
	{
		JogadoresEsperados = FMath::Max(JogadoresEsperados, Sessao->ConsumirJogadoresEsperados());
	}
}

void ANRGameMode::HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer)
{
	if (GetFase() >= ENRFaseDaPartida::Queda && NewPlayer)
	{
		if (ANRPlayerState* PS = NewPlayer->GetPlayerState<ANRPlayerState>())
		{
			PS->bVivo = false; // não conta como vivo nem como jogador da partida
		}
		NewPlayer->StartSpectatingOnly();
		UE_LOG(LogNexus, Log, TEXT("Partida: %s entrou com a partida em andamento e vai assistir"),
			*GetNameSafe(NewPlayer->PlayerState));
		return;
	}
	Super::HandleStartingNewPlayer_Implementation(NewPlayer);
}

void ANRGameMode::BeginPlay()
{
	Super::BeginPlay();
	MudarFase(ENRFaseDaPartida::Espera, TempoMaximoDeEspera);
	// Um timer curto e não o Tick: as fases mudam em segundos, e assim a regra fica num lugar só (AvaliarFase).
	GetWorldTimerManager().SetTimer(TimerAvaliar, this, &ThisClass::AvaliarFase, 0.25f, true);
}

void ANRGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	GetWorldTimerManager().ClearTimer(TimerAvaliar);
	Super::EndPlay(EndPlayReason);
}

void ANRGameMode::SetPlayerDefaults(APawn* PlayerPawn)
{
	Super::SetPlayerDefaults(PlayerPawn);
	UNRAbilitySystemComponent* ASC = PlayerPawn ? PlayerPawn->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr;
	if (ASC && !ASC->OnMorreuNativo.IsBoundToObject(this))
	{
		ASC->OnMorreuNativo.AddUObject(this, &ThisClass::AoHeroiMorrer);
	}
}

void ANRGameMode::Logout(AController* Exiting)
{
	// Quem sai no meio da partida é eliminado na hora, com a colocação do momento (NETWORKING_ARCHITECTURE.md §7).
	if (ANRPlayerState* PS = Exiting ? Exiting->GetPlayerState<ANRPlayerState>() : nullptr)
	{
		if (PS->bVivo)
		{
			EliminarComCausa(PS, nullptr, TEXT("Desconectou"));
		}
	}
	Super::Logout(Exiting);
}

// ------------------------------------------------------------------------------------------------ Fases

void ANRGameMode::MudarFase(ENRFaseDaPartida NovaFase, float Duracao)
{
	ANRGameState* GS = GetNRGameState();
	if (!GS)
	{
		return;
	}
	const double T = Agora();
	GS->DefinirFase(NovaFase, T, Duracao > 0.f ? T + Duracao : 0.0);
	UE_LOG(LogNexus, Log, TEXT("Partida: fase %s (%d jogadores, %d vivos)"),
		*ANRGameState::NomeDaFase(NovaFase).ToString(), ContarJogadores(GS), GS->ContarVivos());
}

void ANRGameMode::AvaliarFase()
{
	ANRGameState* GS = GetNRGameState();
	if (!GS)
	{
		return;
	}
	const double NaFase = Agora() - GS->InicioDaFase;
	switch (GS->Fase)
	{
	case ENRFaseDaPartida::Espera:
	{
		// "Pronto" por enquanto = todo jogador humano já tem herói. Com o lobby (M4), vira "todos avisaram que
		// carregaram o mapa".
		bool bTodosProntos = true;
		for (FConstPlayerControllerIterator It = GetWorld()->GetPlayerControllerIterator(); It; ++It)
		{
			const APlayerController* PC = It->Get();
			if (PC && !PC->GetPawn())
			{
				bTodosProntos = false;
				break;
			}
		}
		const bool bTodosChegaram = GetNumPlayers() >= JogadoresEsperados;
		if ((bTodosProntos && bTodosChegaram && NaFase >= TempoMinimoDeEspera) || NaFase >= TempoMaximoDeEspera)
		{
			FecharEspera();
		}
		break;
	}
	case ENRFaseDaPartida::Draft:
		if (bPularDraft || (GS->FimDaFase > 0.0 && Agora() >= GS->FimDaFase))
		{
			MudarFase(ENRFaseDaPartida::Queda);
			IniciarQueda();
		}
		break;
	case ENRFaseDaPartida::Queda:
		if (NaFase >= TempoMinimoDeQueda && (!AlguemNoDirigivel() || NaFase >= TempoMaximoDeQueda))
		{
			MudarFase(ENRFaseDaPartida::EmJogo);
		}
		ConferirVitoria();
		break;
	case ENRFaseDaPartida::EmJogo:
		ConferirVitoria();
		break;
	case ENRFaseDaPartida::Final:
		if (NaFase >= DuracaoFinal)
		{
			MudarFase(ENRFaseDaPartida::Resultados, DuracaoResultados);
		}
		break;
	case ENRFaseDaPartida::Resultados:
		if (NaFase >= DuracaoResultados)
		{
			TerminarPartida();
		}
		break;
	default:
		break;
	}
}

void ANRGameMode::FecharEspera()
{
	ANRGameState* GS = GetNRGameState();
	GS->JogadoresNoInicio = ContarJogadores(GS);
	GS->bModoTreino = GS->JogadoresNoInicio <= 1;
	UE_LOG(LogNexus, Log, TEXT("Partida: %d jogadores%s"), GS->JogadoresNoInicio,
		GS->bModoTreino ? TEXT(" (modo treino: termina quando o jogador morre)") : TEXT(""));
	if (bPularDraft)
	{
		MudarFase(ENRFaseDaPartida::Queda);
		IniciarQueda();
	}
	else
	{
		MudarFase(ENRFaseDaPartida::Draft);
	}
}

bool ANRGameMode::AlguemNoDirigivel() const
{
	// O BP_HeroBase.EnterShip esconde o herói (SetActorHiddenInGame) enquanto ele está a bordo, e o ExitShip mostra.
	// bHidden replica, então este teste vale igual no servidor e no cliente.
	for (const APlayerState* PS : GameState->PlayerArray)
	{
		const ANRPlayerState* NRPS = Cast<ANRPlayerState>(PS);
		const APawn* Pawn = NRPS ? NRPS->GetPawn() : nullptr;
		if (Pawn && NRPS->bVivo && Pawn->IsHidden())
		{
			return true;
		}
	}
	return false;
}

void ANRGameMode::TerminarPartida()
{
	GetWorldTimerManager().ClearTimer(TimerAvaliar);
	UE_LOG(LogNexus, Log, TEXT("Partida: fim, recomeçando o mapa"));
	// Até o lobby existir (M4), a partida seguinte começa no mesmo mapa. Com clientes conectados, o ServerTravel
	// leva todos juntos; sozinho (standalone, inclusive no PIE), basta reabrir o nível.
	if (GetNetMode() == NM_Standalone)
	{
		UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
	}
	else
	{
		// Os clientes reconectam sozinhos depois do ServerTravel, mas demoram a carregar: a próxima Espera aguarda
		// todos os humanos de agora (UNRSessaoSubsystem sobrevive à troca de mapa).
		if (UNRSessaoSubsystem* Sessao = GetGameInstance() ? GetGameInstance()->GetSubsystem<UNRSessaoSubsystem>() : nullptr)
		{
			// Espectadores também reconectam e voltam a jogar na próxima (GetNumPlayers não os conta).
			Sessao->DefinirJogadoresEsperados(GetNumPlayers() + GetNumSpectators());
		}
		GetWorld()->ServerTravel(TEXT("?Restart"), false);
	}
}

// ------------------------------------------------------------------------------------------------ Eliminação e vitória

void ANRGameMode::AoHeroiMorrer(UNRAbilitySystemComponent* ASC, AActor* Assassino)
{
	const APawn* Pawn = ASC ? Cast<APawn>(ASC->GetOwner()) : nullptr;
	if (ANRPlayerState* PS = Pawn ? Pawn->GetPlayerState<ANRPlayerState>() : nullptr)
	{
		EliminarJogador(PS, Assassino);
	}
}

void ANRGameMode::EliminarJogador(ANRPlayerState* Vitima, AActor* Assassino)
{
	EliminarComCausa(Vitima, Assassino, FString());
}

void ANRGameMode::EliminarComCausa(ANRPlayerState* Vitima, AActor* Assassino, const FString& Causa)
{
	ANRGameState* GS = GetNRGameState();
	if (!Vitima || !GS || !Vitima->bVivo)
	{
		return;
	}
	if (GS->Fase != ENRFaseDaPartida::Queda && GS->Fase != ENRFaseDaPartida::EmJogo)
	{
		// Fora da partida (Espera, Final, Resultados) ninguém é eliminado: a vitória já decidida não muda.
		UE_LOG(LogNexus, Log, TEXT("Partida: eliminação de %s ignorada na fase %s"),
			*Vitima->GetPlayerName(), *ANRGameState::NomeDaFase(GS->Fase).ToString());
		return;
	}

	const int32 VivosAntes = GS->ContarVivos();
	Vitima->bVivo = false;
	Vitima->Colocacao = VivosAntes;
	bAlguemEliminado = true;

	// Um projétil ou uma área chegam como "assassino": quem matou é o pawn que os criou (Instigator).
	APawn* PawnAssassino = Cast<APawn>(Assassino);
	if (!PawnAssassino && Assassino)
	{
		PawnAssassino = Assassino->GetInstigator();
	}
	// Dano sem instigador (a tempestade) chega com a própria vítima como instigador: o MakeEffectContext do GAS põe o
	// dono do ASC quando ninguém é informado. Tratado como "sem assassino" (testado no M1: saía "HeroBase").
	if (PawnAssassino && PawnAssassino == Vitima->GetPawn())
	{
		PawnAssassino = nullptr;
		Assassino = nullptr;
	}
	ANRPlayerState* PSAssassino = PawnAssassino ? PawnAssassino->GetPlayerState<ANRPlayerState>() : nullptr;
	if (PSAssassino == Vitima)
	{
		PSAssassino = nullptr; // a própria magia não dá abate
	}
	Vitima->EliminadoPor = PSAssassino;
	Vitima->CausaDaEliminacao = !Causa.IsEmpty() ? Causa
		: PSAssassino ? PSAssassino->GetPlayerName() : NomeDaCausa(PawnAssassino ? PawnAssassino : Assassino);

	int32 XPGanho = 0;
	if (PSAssassino)
	{
		++PSAssassino->Abates;
		if (UNRAbilitySystemComponent* ASCAssassino = PawnAssassino->FindComponentByClass<UNRAbilitySystemComponent>())
		{
			const APawn* PawnVitima = Vitima->GetPawn();
			const UNRAbilitySystemComponent* ASCVitima = PawnVitima ? PawnVitima->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr;
			XPGanho = XPDeAbate(ASCVitima ? ASCVitima->Nivel : Vitima->Nivel, ASCAssassino->Nivel);
			ASCAssassino->GanharXP(XPGanho);
		}
	}
	UE_LOG(LogNexus, Log, TEXT("Partida: %s eliminado (#%d) por %s (+%d XP)"),
		*Vitima->GetPlayerName(), Vitima->Colocacao, *Vitima->CausaDaEliminacao, XPGanho);

	if (APlayerController* PC = Vitima->GetPlayerController())
	{
		FTimerHandle Timer;
		const FTimerDelegate Camera = FTimerDelegate::CreateUObject(this, &ThisClass::MostrarAssassino,
			TWeakObjectPtr<APlayerController>(PC), TWeakObjectPtr<AActor>(PawnAssassino));
		GetWorldTimerManager().SetTimer(Timer, Camera, FMath::Max(0.01f, AtrasoCameraNoAssassino), false);
	}
	ConferirVitoria();
}

void ANRGameMode::MostrarAssassino(TWeakObjectPtr<APlayerController> VitimaPC, TWeakObjectPtr<AActor> Alvo)
{
	APlayerController* PC = VitimaPC.Get();
	if (!PC)
	{
		return;
	}
	// Só assiste a heróis: um creep não tem câmera própria. Sem assassino herói vivo, assiste a qualquer herói vivo.
	AActor* Destino = Alvo.Get();
	if (Destino && (Destino->IsActorBeingDestroyed() || !Destino->FindComponentByClass<UNRAbilitySystemComponent>()))
	{
		Destino = nullptr;
	}
	if (const UNRAbilitySystemComponent* ASC = Destino ? Destino->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr)
	{
		if (ASC->IsMorto())
		{
			Destino = nullptr;
		}
	}
	for (int32 i = 0; !Destino && i < GameState->PlayerArray.Num(); ++i)
	{
		const ANRPlayerState* PS = Cast<ANRPlayerState>(GameState->PlayerArray[i]);
		if (PS && PS->bVivo && PS->GetPawn())
		{
			Destino = PS->GetPawn();
		}
	}
	if (!Destino)
	{
		return;
	}
	FViewTargetTransitionParams Transicao;
	Transicao.BlendTime = 0.8f;
	PC->SetViewTarget(Destino, Transicao);
	if (!PC->IsLocalController())
	{
		// O SetViewTarget do servidor não chega sozinho a um cliente remoto em todas as situações.
		PC->ClientSetViewTarget(Destino, Transicao);
	}
}

void ANRGameMode::ConferirVitoria()
{
	ANRGameState* GS = GetNRGameState();
	if (!GS || (GS->Fase != ENRFaseDaPartida::Queda && GS->Fase != ENRFaseDaPartida::EmJogo))
	{
		return; // a vitória só é decidida uma vez: depois do Final, nada aqui roda de novo
	}
	const int32 Vivos = GS->ContarVivos();
	if (GS->bModoTreino ? Vivos > 0 : Vivos > 1)
	{
		return;
	}
	ANRPlayerState* Vencedor = nullptr;
	if (!GS->bModoTreino)
	{
		for (APlayerState* PS : GS->PlayerArray)
		{
			ANRPlayerState* NRPS = Cast<ANRPlayerState>(PS);
			if (NRPS && NRPS->bVivo && !NRPS->IsInactive())
			{
				Vencedor = NRPS;
				break;
			}
		}
	}
	if (Vencedor)
	{
		Vencedor->Colocacao = 1;
	}
	GS->Vencedor = Vencedor;
	UE_LOG(LogNexus, Log, TEXT("Partida: vencedor %s"), Vencedor ? *Vencedor->GetPlayerName() : TEXT("(ninguém)"));
	MudarFase(ENRFaseDaPartida::Final, DuracaoFinal);
	CongelarCombate();
}

void ANRGameMode::CongelarCombate()
{
	// No Final ninguém mais toma dano (de herói, creep ou tempestade): o resultado não muda depois de anunciado.
	for (APlayerState* PS : GameState->PlayerArray)
	{
		const APawn* Pawn = PS ? PS->GetPawn() : nullptr;
		if (UNRAbilitySystemComponent* ASC = Pawn ? Pawn->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr)
		{
			ASC->DefinirInvulneravel(true);
		}
	}
}

// ------------------------------------------------------------------------------------------------ Desenvolvimento

void ANRGameMode::EsperarJogadores(int32 Quantos)
{
	if (GetFase() == ENRFaseDaPartida::Espera)
	{
		JogadoresEsperados = FMath::Max(0, Quantos);
		UE_LOG(LogNexus, Log, TEXT("Partida: a Espera aguarda %d humanos"), JogadoresEsperados);
	}
}

APawn* ANRGameMode::AdicionarBotDeTeste()
{
	ANRGameState* GS = GetNRGameState();
	if (!GS || bAlguemEliminado || GS->Fase >= ENRFaseDaPartida::Final)
	{
		UE_LOG(LogNexus, Warning, TEXT("Partida: bot de teste recusado (já houve eliminação ou a partida acabou)"));
		return nullptr;
	}
	FActorSpawnParameters Parametros;
	Parametros.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ANRBotController* Bot = GetWorld()->SpawnActor<ANRBotController>(ANRBotController::StaticClass(), FTransform::Identity, Parametros);
	if (!Bot)
	{
		return nullptr;
	}
	++BotsCriados;
	if (Bot->PlayerState)
	{
		Bot->PlayerState->SetPlayerName(FString::Printf(TEXT("Bot %d"), BotsCriados));
		Bot->PlayerState->SetIsABot(true);
	}

	// Ao lado do PlayerStart (em roda), para não nascer dentro de outro herói.
	const AActor* Inicio = FindPlayerStart(Bot);
	const FVector Base = Inicio ? Inicio->GetActorLocation() : FVector::ZeroVector;
	const FVector Local = Base + FRotator(0.f, 72.f * BotsCriados, 0.f).Vector() * 300.f;
	APawn* Pawn = SpawnDefaultPawnAtTransform(Bot, FTransform(Inicio ? Inicio->GetActorRotation() : FRotator::ZeroRotator, Local));
	if (Pawn)
	{
		Bot->Possess(Pawn);
		SetPlayerDefaults(Pawn);
	}
	if (GS->Fase > ENRFaseDaPartida::Espera)
	{
		// Bot entrando depois da Espera (só em teste): a contagem do início e o modo treino acompanham.
		GS->JogadoresNoInicio = ContarJogadores(GS);
		GS->bModoTreino = GS->JogadoresNoInicio <= 1;
	}
	UE_LOG(LogNexus, Log, TEXT("Partida: %s entrou (pawn %s)"), *GetNameSafe(Bot->PlayerState), *GetNameSafe(Pawn));
	return Pawn;
}
