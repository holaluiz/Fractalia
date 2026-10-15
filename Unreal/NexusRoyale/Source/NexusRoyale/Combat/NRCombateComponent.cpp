#include "Combat/NRCombateComponent.h"

#include "Combat/NRChuvaMeteoros.h"
#include "Combat/NREstruturaMagica.h"
#include "Combat/NRProjetilMagico.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GAS/AS_Hero.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "InputAction.h"
#include "Items/NRInventoryComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NexusRoyale.h"
#include "Progression/NRMutacoesComponent.h"
#include "TimerManager.h"
#include "UI/NRHudWidget.h"

UNRCombateComponent::UNRCombateComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.1f;

	// Feiticeiro (GDD §4.1): dardo arcano, 60 mágico, 35 m, 1 a cada 1,0 s.
	AtaqueBasico.Nome = NSLOCTEXT("Nexus", "DardoArcano", "Dardo arcano");
	AtaqueBasico.Dano = 60.f;
	AtaqueBasico.Alcance = 3500.f;
	AtaqueBasico.Velocidade = 4500.f;
	AtaqueBasico.Recarga = 1.f;
	AtaqueBasico.Cor = FLinearColor(0.55f, 0.35f, 1.f);
	AtaqueBasico.Tamanho = 0.25f;
	AtaqueBasico.Teleguiado = 12000.f; // "levemente teleguiado": raio de curva de ~17 m a 45 m/s

	// Bola de Fogo (GDD §6): 130 de dano num raio de 3 m, 55 de mana, 7 s.
	MagiaPrincipal.Nome = NSLOCTEXT("Nexus", "BolaDeFogo", "Bola de Fogo");
	MagiaPrincipal.Dano = 130.f;
	MagiaPrincipal.RaioExplosao = 300.f;
	MagiaPrincipal.Alcance = 4000.f;
	MagiaPrincipal.Velocidade = 2500.f;
	MagiaPrincipal.Custo = 55.f;
	MagiaPrincipal.Recarga = 7.f;
	MagiaPrincipal.Cor = FLinearColor(1.f, 0.35f, 0.05f);
	MagiaPrincipal.Tamanho = 0.6f;

	// Muralha de Gelo (GDD §6.3): parede de 6 × 3,5 m a até 15 m, com 400 de vida, por 6 s; 50 de mana, 12 s.
	// Os números ficam nos valores padrão do FNRMagiaEstrutura.
	Magia2.Nome = NSLOCTEXT("Nexus", "MuralhaDeGelo", "Muralha de Gelo");

	// Chuva de Meteoros (GDD §6.4): área de 8 m, 3 meteoros de 120 após 1 s de aviso, chão em chamas por 4 s;
	// 120 de mana, 80 s. Os números ficam nos valores padrão do FNRMagiaChuva.
	Ultimate.Nome = NSLOCTEXT("Nexus", "ChuvaDeMeteoros", "Chuva de Meteoros");
}

void UNRCombateComponent::BeginPlay()
{
	Super::BeginPlay();
	if (UNRAbilitySystemComponent* ASC = GetOwner()->FindComponentByClass<UNRAbilitySystemComponent>())
	{
		ASC->OnMorreu.AddDynamic(this, &ThisClass::AoMorrer);
	}
}

void UNRCombateComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(TimerRecomecar);
	}
	if (Hud)
	{
		Hud->RemoveFromParent();
		Hud = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void UNRCombateComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// O herói só ganha controller e InputComponent depois de ser possuído: tenta até conseguir.
	if (!bInputLigado)
	{
		TentarLigarInput();
	}
	if (!Hud)
	{
		TentarCriarHud();
	}
	if (bInputLigado && Hud)
	{
		SetComponentTickEnabled(false);
	}
}

void UNRCombateComponent::TentarLigarInput()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	if (!Pawn || !Pawn->IsLocallyControlled() || !Pawn->IsPlayerControlled())
	{
		return;
	}
	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(Pawn->InputComponent);
	if (!Input)
	{
		return;
	}
	// Triggered: segurar o botão esquerdo dispara de novo a cada recarga.
	if (AcaoAtaque) Input->BindAction(AcaoAtaque, ETriggerEvent::Triggered, this, &ThisClass::AoAtaque);
	if (AcaoMagiaPrincipal) Input->BindAction(AcaoMagiaPrincipal, ETriggerEvent::Started, this, &ThisClass::AoMagiaPrincipal);
	if (AcaoMagia2) Input->BindAction(AcaoMagia2, ETriggerEvent::Started, this, &ThisClass::AoMagia2);
	if (AcaoUltimate) Input->BindAction(AcaoUltimate, ETriggerEvent::Started, this, &ThisClass::AoUltimate);
	if (AcaoConsumivel1) Input->BindAction(AcaoConsumivel1, ETriggerEvent::Started, this, &ThisClass::AoConsumivel1);
	if (AcaoConsumivel2) Input->BindAction(AcaoConsumivel2, ETriggerEvent::Started, this, &ThisClass::AoConsumivel2);
	if (AcaoConsumivel3) Input->BindAction(AcaoConsumivel3, ETriggerEvent::Started, this, &ThisClass::AoConsumivel3);
	if (AcaoTrocarMutacoes) Input->BindAction(AcaoTrocarMutacoes, ETriggerEvent::Started, this, &ThisClass::AoTrocarMutacoes);
	bInputLigado = true;
	UE_LOG(LogNexus, Log, TEXT("%s: teclas de combate ligadas"), *GetNameSafe(Pawn));
}

void UNRCombateComponent::TentarCriarHud()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	if (!PC || !Pawn->IsLocallyControlled())
	{
		return;
	}
	UClass* Classe = ClasseHud ? ClasseHud.Get() : UNRHudWidget::StaticClass();
	Hud = CreateWidget<UNRHudWidget>(PC, Classe);
	if (Hud)
	{
		Hud->AddToViewport(5);
	}
}

bool UNRCombateComponent::PodeAgir() const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	if (!Pawn || Pawn->IsHidden()) // escondido = ainda no dirigível
	{
		return false;
	}
	const UNRAbilitySystemComponent* ASC = ASCDoDono();
	return !ASC || !ASC->IsMorto();
}

UNRAbilitySystemComponent* UNRCombateComponent::ASCDoDono() const
{
	const AActor* Dono = GetOwner();
	return Dono ? Dono->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr;
}

bool UNRCombateComponent::Pronta(float Custo, double ProximoUso) const
{
	const UWorld* World = GetWorld();
	if (!World || !PodeAgir() || World->GetTimeSeconds() < ProximoUso)
	{
		return false;
	}
	const UNRAbilitySystemComponent* ASC = ASCDoDono();
	return Custo <= 0.f || (ASC && ASC->GetMana() >= Custo);
}

bool UNRCombateComponent::Pagar(float Custo, float Recarga, double& ProximoUso)
{
	UNRAbilitySystemComponent* ASC = ASCDoDono();
	if (Custo > 0.f && (!ASC || !ASC->GastarMana(Custo)))
	{
		return false;
	}
	const float Reducao = ASC ? FMath::Clamp(ASC->GetNumericAttribute(UAS_Hero::GetReducaoRecargaAttribute()), 0.f, 0.5f) : 0.f;
	ProximoUso = GetWorld()->GetTimeSeconds() + Recarga * (1.f - Reducao);
	return true;
}

bool UNRCombateComponent::UltimateLiberada() const
{
	const UNRAbilitySystemComponent* ASC = ASCDoDono();
	return !ASC || ASC->Nivel >= NivelUltimate;
}

bool UNRCombateComponent::UsarAtaqueBasico()
{
	return Lancar(AtaqueBasico, ProximoBasico);
}

bool UNRCombateComponent::UsarMagiaPrincipal()
{
	return Lancar(MagiaPrincipal, ProximoPrincipal);
}

bool UNRCombateComponent::UsarMagia2()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	FVector Ponto, Normal, Direcao;
	if (!Pawn || !Pronta(Magia2.Custo, ProximoMagia2) ||
	    !PontoNoChao(Magia2.Alcance, Magia2.DistanciaMinima, Ponto, Normal, Direcao) ||
	    !Pagar(Magia2.Custo, Magia2.Recarga, ProximoMagia2))
	{
		return false;
	}
	const FRotator Frente(0.f, Direcao.Rotation().Yaw, 0.f);
	Pawn->SetActorRotation(Frente);

	// De frente para o herói: a espessura (X) fica na linha de mira e a largura (Y), atravessada nela.
	FActorSpawnParameters Params;
	Params.Owner = Pawn;
	Params.Instigator = Pawn;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	UClass* Classe = ClasseEstrutura ? ClasseEstrutura.Get() : ANREstruturaMagica::StaticClass();
	ANREstruturaMagica* Estrutura = GetWorld()->SpawnActor<ANREstruturaMagica>(Classe, Ponto, Frente, Params);
	if (!Estrutura)
	{
		return false;
	}
	UMaterialInterface* Material = MaterialEstrutura ? MaterialEstrutura.Get() : MaterialProjetil.Get();
	Estrutura->Erguer(Magia2.Tamanho, Magia2.Vida, Magia2.Duracao, Magia2.Cor, Material);
	UE_LOG(LogNexus, Log, TEXT("%s: %s a %.1f m"), *GetNameSafe(Pawn), *Magia2.Nome.ToString(),
		FVector::Dist2D(Pawn->GetActorLocation(), Ponto) / 100.f);
	return true;
}

bool UNRCombateComponent::UsarUltimate()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	FVector Ponto, Normal, Direcao;
	if (!Pawn || !UltimateLiberada() || !Pronta(Ultimate.Custo, ProximoUltimate) ||
	    !PontoNoChao(Ultimate.Alcance, 0.f, Ponto, Normal, Direcao) ||
	    !Pagar(Ultimate.Custo, Ultimate.Recarga, ProximoUltimate))
	{
		return false;
	}
	Pawn->SetActorRotation(FRotator(0.f, Direcao.Rotation().Yaw, 0.f));

	FActorSpawnParameters Params;
	Params.Owner = Pawn;
	Params.Instigator = Pawn;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	UClass* Classe = ClasseChuva ? ClasseChuva.Get() : ANRChuvaMeteoros::StaticClass();
	// O aviso no chão segue a inclinação do terreno.
	ANRChuvaMeteoros* Chuva = GetWorld()->SpawnActor<ANRChuvaMeteoros>(Classe, Ponto, FRotationMatrix::MakeFromZ(Normal).Rotator(), Params);
	if (!Chuva)
	{
		return false;
	}
	UNRAbilitySystemComponent* ASC = ASCDoDono();
	const float Poder = ASC ? ASC->GetNumericAttribute(UAS_Hero::GetPoderMagicoAttribute()) : 0.f;
	Chuva->Iniciar(Ultimate, 1.f + Poder, MaterialProjetil);
	if (ASC && ManaDevolvidaUltimate > 0.f)
	{
		ASC->RestaurarMana(Ultimate.Custo * ManaDevolvidaUltimate);
	}
	UE_LOG(LogNexus, Log, TEXT("%s: %s a %.1f m"), *GetNameSafe(Pawn), *Ultimate.Nome.ToString(),
		FVector::Dist2D(Pawn->GetActorLocation(), Ponto) / 100.f);
	return true;
}

bool UNRCombateComponent::UsarConsumivel(int32 Slot)
{
	if (!PodeAgir())
	{
		return false;
	}
	UNRInventoryComponent* Inventario = GetOwner()->FindComponentByClass<UNRInventoryComponent>();
	return Inventario && Inventario->UsarConsumivel(Slot);
}

bool UNRCombateComponent::AltApertado() const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	const APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	return PC && (PC->IsInputKeyDown(EKeys::LeftAlt) || PC->IsInputKeyDown(EKeys::RightAlt));
}

void UNRCombateComponent::UsarSlot(int32 Slot)
{
	UNRMutacoesComponent* Mutacoes = GetOwner()->FindComponentByClass<UNRMutacoesComponent>();
	if (Mutacoes && Mutacoes->TemEscolhaPendente() && AltApertado())
	{
		Mutacoes->Escolher(Slot);
		return;
	}
	UsarConsumivel(Slot);
}

void UNRCombateComponent::AoTrocarMutacoes()
{
	UNRMutacoesComponent* Mutacoes = GetOwner()->FindComponentByClass<UNRMutacoesComponent>();
	if (Mutacoes && AltApertado())
	{
		Mutacoes->TrocarOpcoes();
	}
}

float UNRCombateComponent::RecargaRestante(int32 Slot) const
{
	const UWorld* World = GetWorld();
	if (!World)
	{
		return 0.f;
	}
	const double Proximos[4] = { ProximoBasico, ProximoPrincipal, ProximoMagia2, ProximoUltimate };
	const double Proximo = Proximos[FMath::Clamp(Slot, 0, 3)];
	return static_cast<float>(FMath::Max(0.0, Proximo - World->GetTimeSeconds()));
}

float UNRCombateComponent::TempoAteRecomecar() const
{
	const UWorld* World = GetWorld();
	return World && TimerRecomecar.IsValid() ? FMath::Max(0.f, World->GetTimerManager().GetTimerRemaining(TimerRecomecar)) : 0.f;
}

bool UNRCombateComponent::Lancar(const FNRMagiaProjetil& Magia, double& ProximoUso)
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	UWorld* World = GetWorld();
	if (!Pawn || !World || !Pronta(Magia.Custo, ProximoUso) || !Pagar(Magia.Custo, Magia.Recarga, ProximoUso))
	{
		return false;
	}
	const UNRAbilitySystemComponent* ASC = ASCDoDono();
	const float Poder = ASC ? ASC->GetNumericAttribute(UAS_Hero::GetPoderMagicoAttribute()) : 0.f;

	// Mira: da câmera até o que estiver no centro da tela (ou o alcance, se não houver nada).
	FVector Olho;
	FRotator Visao;
	PontoDeVista(Olho, Visao);
	FVector Alvo = Olho + Visao.Vector() * (Magia.Alcance + 1000.f);
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(NRMira), false, Pawn);
	if (World->LineTraceSingleByChannel(Hit, Olho, Alvo, ECC_Visibility, Params))
	{
		Alvo = Hit.ImpactPoint;
	}

	Pawn->SetActorRotation(FRotator(0.f, Visao.Yaw, 0.f));
	const FVector Origem = Pawn->GetActorLocation() + Pawn->GetActorForwardVector() * 60.f + FVector(0.f, 0.f, 40.f);
	FVector Direcao = (Alvo - Origem).GetSafeNormal();
	if (FVector::DotProduct(Direcao, Visao.Vector()) < 0.2f) // alvo colado no herói: segue a câmera
	{
		Direcao = Visao.Vector();
	}

	const FTransform Transform(Direcao.Rotation(), Origem);
	UClass* Classe = ClasseProjetil ? ClasseProjetil.Get() : ANRProjetilMagico::StaticClass();
	ANRProjetilMagico* Projetil = World->SpawnActorDeferred<ANRProjetilMagico>(Classe, Transform, Pawn, Pawn,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Projetil)
	{
		return false;
	}
	Projetil->Dano = Magia.Dano * (1.f + Poder);
	Projetil->RaioExplosao = Magia.RaioExplosao;
	Projetil->DuracaoChamas = Magia.DuracaoChamas;
	Projetil->DanoChamasPorSegundo = Magia.DanoChamasPorSegundo * (1.f + Poder);
	if (MaterialProjetil)
	{
		Projetil->Material = MaterialProjetil;
	}
	Projetil->FinishSpawning(Transform);
	USceneComponent* Perseguir = Magia.Teleguiado > 0.f ? AlvoNaMira(Origem, Direcao, Magia.Alcance, Magia.ConeTeleguiado) : nullptr;
	Projetil->Lancar(Direcao, Magia.Velocidade, Magia.Alcance, Magia.Cor, Magia.Tamanho, Perseguir, Magia.Teleguiado);
	return true;
}

void UNRCombateComponent::PontoDeVista(FVector& Olho, FRotator& Visao) const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	Olho = Pawn ? Pawn->GetActorLocation() : FVector::ZeroVector;
	Visao = Pawn ? Pawn->GetActorRotation() : FRotator::ZeroRotator;
	if (const AController* Controller = Pawn ? Pawn->GetController() : nullptr)
	{
		Controller->GetPlayerViewPoint(Olho, Visao);
	}
}

bool UNRCombateComponent::PontoNoChao(float Alcance, float DistanciaMinima, FVector& Ponto, FVector& Normal, FVector& Direcao) const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	const UWorld* World = GetWorld();
	if (!Pawn || !World)
	{
		return false;
	}
	FVector Olho;
	FRotator Visao;
	PontoDeVista(Olho, Visao);
	const FVector Heroi = Pawn->GetActorLocation();

	// Onde a mira bate (a câmera fica atrás do herói, então soma a distância até ele).
	FCollisionQueryParams Params(SCENE_QUERY_STAT(NRMiraChao), false, Pawn);
	FHitResult Hit;
	const FVector Fim = Olho + Visao.Vector() * (Alcance + FVector::Dist(Olho, Heroi) + 500.f);
	const bool bAcertou = World->LineTraceSingleByChannel(Hit, Olho, Fim, ECC_Visibility, Params);
	const FVector Mirado = bAcertou ? Hit.ImpactPoint : Fim;

	// Limita a distância no plano. Mirando o céu ou longe demais, fica no alcance máximo.
	FVector NoPlano = Mirado - Heroi;
	NoPlano.Z = 0.f;
	const float Distancia = NoPlano.Size();
	Direcao = Distancia > 1.f ? NoPlano / Distancia : FRotator(0.f, Visao.Yaw, 0.f).Vector();
	const float Usada = FMath::Clamp(Distancia, FMath::Min(DistanciaMinima, Alcance), Alcance);
	const bool bNoMirado = bAcertou && FMath::IsNearlyEqual(Usada, Distancia, 1.f);
	const FVector XY = Heroi + Direcao * Usada;

	// Desce até o chão. Só cenário: ignora pawns, para não erguer em cima da cabeça de um creep.
	const float Referencia = bNoMirado ? Mirado.Z : Heroi.Z;
	if (!World->LineTraceSingleByObjectType(Hit, FVector(XY.X, XY.Y, Referencia + 400.f), FVector(XY.X, XY.Y, Referencia - 5000.f),
	                                        FCollisionObjectQueryParams(ECC_WorldStatic), Params))
	{
		return false;
	}
	Ponto = Hit.ImpactPoint;
	Normal = Hit.ImpactNormal;
	return true;
}

USceneComponent* UNRCombateComponent::AlvoNaMira(const FVector& Origem, const FVector& Direcao, float Alcance, float ConeGraus) const
{
	const APawn* Eu = Cast<APawn>(GetOwner());
	USceneComponent* Melhor = nullptr;
	float MelhorCos = FMath::Cos(FMath::DegreesToRadians(ConeGraus));
	for (TActorIterator<APawn> It(GetWorld()); It; ++It)
	{
		APawn* Outro = *It;
		// Sem colisão = morto (creeps) ou ainda no dirigível (heróis).
		if (Outro == Eu || Outro->IsHidden() || !Outro->GetActorEnableCollision())
		{
			continue;
		}
		const UNRAbilitySystemComponent* ASC = Outro->FindComponentByClass<UNRAbilitySystemComponent>();
		if (ASC && ASC->IsMorto())
		{
			continue;
		}
		const FVector Para = Outro->GetActorLocation() - Origem;
		const float Distancia = Para.Size();
		if (Distancia < 1.f || Distancia > Alcance)
		{
			continue;
		}
		const float Cos = FVector::DotProduct(Para / Distancia, Direcao);
		if (Cos > MelhorCos)
		{
			MelhorCos = Cos;
			Melhor = Outro->GetRootComponent();
		}
	}
	return Melhor;
}

void UNRCombateComponent::AoMorrer(AActor* Assassino)
{
	ACharacter* Heroi = Cast<ACharacter>(GetOwner());
	if (!Heroi)
	{
		return;
	}
	if (UCharacterMovementComponent* Movimento = Heroi->GetCharacterMovement())
	{
		Movimento->StopMovementImmediately();
		Movimento->DisableMovement();
	}
	if (AnimMorte)
	{
		TArray<USkeletalMeshComponent*> Malhas;
		Heroi->GetComponents(Malhas);
		for (USkeletalMeshComponent* Malha : Malhas)
		{
			Malha->PlayAnimation(AnimMorte, false);
		}
	}
	if (APlayerController* PC = Cast<APlayerController>(Heroi->GetController()))
	{
		Heroi->DisableInput(PC);
		if (TempoParaRecomecar > 0.f)
		{
			GetWorld()->GetTimerManager().SetTimer(TimerRecomecar, this, &ThisClass::Recomecar, TempoParaRecomecar, false);
		}
	}
}

void UNRCombateComponent::Recomecar()
{
	UE_LOG(LogNexus, Log, TEXT("Recomeçando a partida"));
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}
