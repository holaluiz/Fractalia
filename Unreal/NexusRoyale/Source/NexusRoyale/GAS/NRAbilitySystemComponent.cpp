#include "GAS/NRAbilitySystemComponent.h"

#include "GAS/AS_Hero.h"
#include "GAS/NRGameplayEffects.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "NexusRoyale.h"
#include "TimerManager.h"

// ------------------------------------------------------------------------------------------------ FNRBonus

FNRBonus& FNRBonus::operator*=(float Fator)
{
	VidaMax *= Fator;
	ManaMax *= Fator;
	Armadura *= Fator;
	DanoFisico *= Fator;
	PoderMagico *= Fator;
	VelocMov *= Fator;
	VelocAtaque *= Fator;
	ReducaoRecarga *= Fator;
	RegenMana *= Fator;
	RegenVida *= Fator;
	BonusCura *= Fator;
	return *this;
}

FNRBonus& FNRBonus::operator+=(const FNRBonus& Outro)
{
	VidaMax += Outro.VidaMax;
	ManaMax += Outro.ManaMax;
	Armadura += Outro.Armadura;
	DanoFisico += Outro.DanoFisico;
	PoderMagico += Outro.PoderMagico;
	VelocMov += Outro.VelocMov;
	VelocAtaque += Outro.VelocAtaque;
	ReducaoRecarga += Outro.ReducaoRecarga;
	RegenMana += Outro.RegenMana;
	RegenVida += Outro.RegenVida;
	BonusCura += Outro.BonusCura;
	return *this;
}

bool FNRBonus::IsZero() const
{
	return VidaMax == 0.f && ManaMax == 0.f && Armadura == 0.f && DanoFisico == 0.f && PoderMagico == 0.f &&
		VelocMov == 0.f && VelocAtaque == 0.f && ReducaoRecarga == 0.f && RegenMana == 0.f && RegenVida == 0.f &&
		BonusCura == 0.f;
}

// ------------------------------------------------------------------------------------------------ Ciclo de vida

UNRAbilitySystemComponent::UNRAbilitySystemComponent()
{
	SetIsReplicatedByDefault(true);
	SetReplicationMode(EGameplayEffectReplicationMode::Mixed);
}

void UNRAbilitySystemComponent::InitializeComponent()
{
	Super::InitializeComponent();
	if (!GetSet<UAS_Hero>())
	{
		AddSet<UAS_Hero>();
	}
}

void UNRAbilitySystemComponent::BeginPlay()
{
	Super::BeginPlay();

	GetGameplayAttributeValueChangeDelegate(UAS_Hero::GetVidaAttribute()).AddUObject(this, &ThisClass::OnVidaAtributo);
	GetGameplayAttributeValueChangeDelegate(UAS_Hero::GetVidaMaxAttribute()).AddUObject(this, &ThisClass::OnVidaAtributo);
	GetGameplayAttributeValueChangeDelegate(UAS_Hero::GetManaAttribute()).AddUObject(this, &ThisClass::OnManaAtributo);
	GetGameplayAttributeValueChangeDelegate(UAS_Hero::GetManaMaxAttribute()).AddUObject(this, &ThisClass::OnManaAtributo);
	GetGameplayAttributeValueChangeDelegate(UAS_Hero::GetVelocMovAttribute()).AddUObject(this, &ThisClass::OnVelocAtributo);

	if (IsOwnerActorAuthoritative())
	{
		if (bReceberDanoDaUnreal && GetOwner())
		{
			GetOwner()->OnTakeAnyDamage.AddDynamic(this, &ThisClass::AoDanoDaUnreal);
		}
		if (bInicializarNoBeginPlay)
		{
			InicializarHeroi(Arquetipo, Build, Nivel);
		}
		if (UWorld* World = GetWorld())
		{
			World->GetTimerManager().SetTimer(TimerRegen, this, &ThisClass::TickRegen, IntervaloRegen, true);
		}
	}
}

void UNRAbilitySystemComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(TimerRegen);
	}
	Super::EndPlay(EndPlayReason);
}

// ------------------------------------------------------------------------------------------------ Atributos

float UNRAbilitySystemComponent::PontosEfetivos(int32 PontosInvestidos)
{
	const int32 P = FMath::Clamp(PontosInvestidos, 0, 10);
	return FMath::Min(P, 5) * 1.0f + FMath::Clamp(P - 5, 0, 3) * 0.6f + FMath::Clamp(P - 8, 0, 2) * 0.3f;
}

void UNRAbilitySystemComponent::SetBase(const FGameplayAttribute& Atributo, float Valor)
{
	SetNumericAttributeBase(Atributo, Valor);
}

void UNRAbilitySystemComponent::InicializarHeroi(const FNRArquetipoBase& NovoArquetipo, const FNRPontosBuild& NovaBuild, int32 NovoNivel)
{
	if (!IsOwnerActorAuthoritative())
	{
		return;
	}
	if (!GetSet<UAS_Hero>())
	{
		AddSet<UAS_Hero>();
	}
	Arquetipo = NovoArquetipo;
	Build = NovaBuild;
	Nivel = FMath::Clamp(NovoNivel, 1, 10);

	const float For = PontosEfetivos(Build.Forca) + PontosExtras(0);
	const float Agi = PontosEfetivos(Build.Agilidade) + PontosExtras(1);
	const float Vit = PontosEfetivos(Build.Vitalidade) + PontosExtras(2);
	const float Int = PontosEfetivos(Build.Intelecto) + PontosExtras(3);
	const float Esp = PontosEfetivos(Build.Espirito) + PontosExtras(4);
	const float NiveisExtras = static_cast<float>(Nivel - 1);

	SetBase(UAS_Hero::GetForcaAttribute(), For);
	SetBase(UAS_Hero::GetAgilidadeAttribute(), Agi);
	SetBase(UAS_Hero::GetVitalidadeAttribute(), Vit);
	SetBase(UAS_Hero::GetIntelectoAttribute(), Int);
	SetBase(UAS_Hero::GetEspiritoAttribute(), Esp);

	// Os máximos primeiro: na recalculação o AS_Hero mantém a porcentagem de vida e mana.
	SetBase(UAS_Hero::GetVidaMaxAttribute(), Arquetipo.Vida + VidaPorVitalidade * Vit + VidaPorNivel * NiveisExtras);
	SetBase(UAS_Hero::GetManaMaxAttribute(), Arquetipo.Mana + ManaPorIntelecto * Int + ManaPorNivel * NiveisExtras);
	SetBase(UAS_Hero::GetRegenVidaAttribute(), RegenVidaPorVitalidade * Vit);
	SetBase(UAS_Hero::GetRegenManaAttribute(), RegenManaEmCombate + RegenManaPorEspirito * Esp);
	SetBase(UAS_Hero::GetDanoFisicoAttribute(), DanoFisicoPorForca * For + DanoPorNivel * NiveisExtras);
	SetBase(UAS_Hero::GetPoderMagicoAttribute(), PoderMagicoPorIntelecto * Int + DanoPorNivel * NiveisExtras);
	SetBase(UAS_Hero::GetVelocMovAttribute(), VelocMovPorAgilidade * Agi);
	SetBase(UAS_Hero::GetVelocAtaqueAttribute(), VelocAtaquePorAgilidade * Agi);
	SetBase(UAS_Hero::GetReducaoRecargaAttribute(), ReducaoRecargaPorEspirito * Esp);
	SetBase(UAS_Hero::GetBonusCuraAttribute(), CuraPorEspirito * Esp);
	SetBase(UAS_Hero::GetArmaduraAttribute(), 0.f); // armadura só vem de itens (GDD §4.2)

	if (!bInicializado)
	{
		SetBase(UAS_Hero::GetVidaAttribute(), GetVidaMax());
		SetBase(UAS_Hero::GetManaAttribute(), GetManaMax());
		bInicializado = true;
		bMorto = false;
	}
	AtualizarVelocidade();
	OnVidaMudou.Broadcast(GetVida(), GetVidaMax());
	OnManaMudou.Broadcast(GetMana(), GetManaMax());

	UE_LOG(LogNexus, Log, TEXT("%s: %s nivel %d -> Vida %.0f, Mana %.0f, PoderMagico +%.0f%%"),
		*GetNameSafe(GetOwner()), *Arquetipo.Nome.ToString(), Nivel, GetVidaMax(), GetManaMax(),
		GetNumericAttribute(UAS_Hero::GetPoderMagicoAttribute()) * 100.f);
}

void UNRAbilitySystemComponent::DefinirNivel(int32 NovoNivel)
{
	InicializarHeroi(Arquetipo, Build, NovoNivel);
}

void UNRAbilitySystemComponent::GanharXP(int32 Quantidade)
{
	if (!IsOwnerActorAuthoritative() || bMorto || Quantidade <= 0)
	{
		return;
	}
	XP += Quantidade;
	int32 NovoNivel = Nivel;
	while (NovoNivel < 10 && XPAcumuladoPorNivel.IsValidIndex(NovoNivel - 1) && XP >= XPAcumuladoPorNivel[NovoNivel - 1])
	{
		++NovoNivel;
	}
	UE_LOG(LogNexus, Log, TEXT("%s: +%d XP (total %d)"), *GetNameSafe(GetOwner()), Quantidade, XP);
	if (NovoNivel > Nivel)
	{
		DefinirNivel(NovoNivel);
		OnSubiuNivel.Broadcast(Nivel);
	}
}

void UNRAbilitySystemComponent::DarXP(AActor* QuemMatou, int32 Quantidade)
{
	AActor* Heroi = QuemMatou;
	if (const AController* Controller = Cast<AController>(QuemMatou))
	{
		Heroi = Controller->GetPawn();
	}
	if (UNRAbilitySystemComponent* ASC = Heroi ? Heroi->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr)
	{
		ASC->GanharXP(Quantidade);
	}
}

void UNRAbilitySystemComponent::ProgressoXP(int32& NoNivel, int32& ParaProximo) const
{
	const int32 Base = Nivel >= 2 && XPAcumuladoPorNivel.IsValidIndex(Nivel - 2) ? XPAcumuladoPorNivel[Nivel - 2] : 0;
	const int32 Proximo = Nivel < 10 && XPAcumuladoPorNivel.IsValidIndex(Nivel - 1) ? XPAcumuladoPorNivel[Nivel - 1] : Base;
	NoNivel = XP - Base;
	ParaProximo = Proximo - Base;
}

void UNRAbilitySystemComponent::SubirAteNivel(int32 Piso)
{
	Piso = FMath::Clamp(Piso, 1, 10);
	if (!IsOwnerActorAuthoritative() || bMorto || Piso <= Nivel)
	{
		return;
	}
	if (XPAcumuladoPorNivel.IsValidIndex(Piso - 2))
	{
		XP = FMath::Max(XP, XPAcumuladoPorNivel[Piso - 2]);
	}
	UE_LOG(LogNexus, Log, TEXT("%s: piso de nivel %d (estava no %d)"), *GetNameSafe(GetOwner()), Piso, Nivel);
	DefinirNivel(Piso);
	OnSubiuNivel.Broadcast(Nivel);
}

void UNRAbilitySystemComponent::AplicarPisoDeNivel(const UObject* WorldContextObject, int32 Piso)
{
	const UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull) : nullptr;
	if (!World || Piso <= 1)
	{
		return;
	}
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (UNRAbilitySystemComponent* ASC = It->FindComponentByClass<UNRAbilitySystemComponent>())
		{
			ASC->SubirAteNivel(Piso);
		}
	}
}

void UNRAbilitySystemComponent::SomarBonusVelocForaDeCombate(float Bonus)
{
	BonusVelocForaDeCombate += Bonus;
	AtualizarVelocidade();
}

float UNRAbilitySystemComponent::PontosExtras(int32 Indice) const
{
	return PontosEfetivosExtras.IsValidIndex(Indice) ? PontosEfetivosExtras[Indice] : 0.f;
}

void UNRAbilitySystemComponent::AdicionarPontosEfetivos(int32 Indice, float Pontos)
{
	if (!IsOwnerActorAuthoritative() || Indice < 0 || Indice > 4)
	{
		return;
	}
	if (PontosEfetivosExtras.Num() < 5)
	{
		PontosEfetivosExtras.SetNumZeroed(5);
	}
	PontosEfetivosExtras[Indice] += Pontos;
	InicializarHeroi(Arquetipo, Build, Nivel);
}

float UNRAbilitySystemComponent::GetVida() const { return GetNumericAttribute(UAS_Hero::GetVidaAttribute()); }
float UNRAbilitySystemComponent::GetVidaMax() const { return GetNumericAttribute(UAS_Hero::GetVidaMaxAttribute()); }
float UNRAbilitySystemComponent::GetMana() const { return GetNumericAttribute(UAS_Hero::GetManaAttribute()); }
float UNRAbilitySystemComponent::GetManaMax() const { return GetNumericAttribute(UAS_Hero::GetManaMaxAttribute()); }
float UNRAbilitySystemComponent::GetArmadura() const { return GetNumericAttribute(UAS_Hero::GetArmaduraAttribute()); }

float UNRAbilitySystemComponent::GetPontosEfetivos(int32 Indice) const
{
	switch (Indice)
	{
	case 0: return GetNumericAttribute(UAS_Hero::GetForcaAttribute());
	case 1: return GetNumericAttribute(UAS_Hero::GetAgilidadeAttribute());
	case 2: return GetNumericAttribute(UAS_Hero::GetVitalidadeAttribute());
	case 3: return GetNumericAttribute(UAS_Hero::GetIntelectoAttribute());
	case 4: return GetNumericAttribute(UAS_Hero::GetEspiritoAttribute());
	default: return 0.f;
	}
}

bool UNRAbilitySystemComponent::IsEmCombate() const
{
	const UWorld* World = GetWorld();
	return World && World->GetTimeSeconds() - UltimoCombate < TempoEmCombate;
}

void UNRAbilitySystemComponent::MarcarCombate()
{
	if (const UWorld* World = GetWorld())
	{
		UltimoCombate = World->GetTimeSeconds();
	}
}

void UNRAbilitySystemComponent::AtualizarVelocidade()
{
	if (ACharacter* Personagem = Cast<ACharacter>(GetAvatarActor()))
	{
		bEmCombateAntes = IsEmCombate();
		const float Bonus = GetNumericAttribute(UAS_Hero::GetVelocMovAttribute()) + (bEmCombateAntes ? 0.f : BonusVelocForaDeCombate);
		Personagem->GetCharacterMovement()->MaxWalkSpeed = Arquetipo.Velocidade * 100.f * FMath::Max(0.1f, 1.f + Bonus);
	}
}

// ------------------------------------------------------------------------------------------------ Efeitos

FGameplayEffectSpecHandle UNRAbilitySystemComponent::CriarSpec(TSubclassOf<UGameplayEffect> Classe, AActor* Instigador) const
{
	FGameplayEffectContextHandle Contexto = MakeEffectContext();
	if (Instigador)
	{
		Contexto.AddInstigator(Instigador, Instigador);
	}
	return MakeOutgoingSpec(Classe, 1.f, Contexto);
}

void UNRAbilitySystemComponent::AplicarDano(float Quantidade, AActor* Instigador, bool bDeJogador, bool bIgnorarArmadura)
{
	if (!IsOwnerActorAuthoritative() || bMorto || Quantidade <= 0.f)
	{
		return;
	}
	if (bDeJogador)
	{
		MarcarCombate();
		if (const APawn* Atacante = Cast<APawn>(Instigador))
		{
			if (UNRAbilitySystemComponent* Outro = Atacante->FindComponentByClass<UNRAbilitySystemComponent>())
			{
				Outro->MarcarCombate();
			}
		}
	}
	FGameplayEffectSpecHandle Spec = CriarSpec(UGE_NR_Dano::StaticClass(), Instigador);
	if (Spec.IsValid())
	{
		Spec.Data->SetSetByCallerMagnitude(NRSetByCaller::Dano, bIgnorarArmadura ? 0.f : Quantidade);
		Spec.Data->SetSetByCallerMagnitude(NRSetByCaller::DanoVerdadeiro, bIgnorarArmadura ? Quantidade : 0.f);
		ApplyGameplayEffectSpecToSelf(*Spec.Data.Get());
	}
}

void UNRAbilitySystemComponent::AplicarDanoTempestade(float PorcentagemDaVidaMax)
{
	AplicarDano(GetVidaMax() * PorcentagemDaVidaMax / 100.f, nullptr, false, true);
}

void UNRAbilitySystemComponent::AoDanoDaUnreal(AActor* Atingido, float Dano, const UDamageType* Tipo, AController* Instigador, AActor* Causador)
{
	// O instigador "de verdade" é o pawn de quem atacou (o causador pode ser um projétil).
	AActor* Atacante = Instigador && Instigador->GetPawn() ? Instigador->GetPawn() : Causador;
	AplicarDano(Dano, Atacante, Instigador && Instigador->IsPlayerController());
}

bool UNRAbilitySystemComponent::GastarMana(float Custo)
{
	if (!IsOwnerActorAuthoritative() || bMorto)
	{
		return false;
	}
	if (Custo <= 0.f)
	{
		return true;
	}
	if (GetMana() < Custo)
	{
		return false;
	}
	ApplyModToAttribute(UAS_Hero::GetManaAttribute(), EGameplayModOp::AddBase, -Custo);
	return true;
}

void UNRAbilitySystemComponent::AplicarContinuo(TSubclassOf<UGameplayEffect> Instantaneo, TSubclassOf<UGameplayEffect> Continuo,
                                                FName Nome, float Quantidade, float Duracao)
{
	if (!IsOwnerActorAuthoritative() || bMorto || Quantidade <= 0.f)
	{
		return;
	}
	const bool bContinuo = Duracao > IntervaloRegen;
	FGameplayEffectSpecHandle Spec = CriarSpec(bContinuo ? Continuo : Instantaneo, GetOwner());
	if (!Spec.IsValid())
	{
		return;
	}
	if (bContinuo)
	{
		// Um tique a cada 0,25 s (período dos efeitos contínuos): a quantidade se divide entre os tiques.
		const float Tiques = FMath::Max(1.f, FMath::RoundToFloat(Duracao / 0.25f));
		Spec.Data->SetSetByCallerMagnitude(NRSetByCaller::Duracao, Tiques * 0.25f + 0.01f);
		Spec.Data->SetSetByCallerMagnitude(Nome, Quantidade / Tiques);
	}
	else
	{
		Spec.Data->SetSetByCallerMagnitude(Nome, Quantidade);
	}
	ApplyGameplayEffectSpecToSelf(*Spec.Data.Get());
}

void UNRAbilitySystemComponent::Curar(float Quantidade, float Duracao)
{
	AplicarContinuo(UGE_NR_Cura::StaticClass(), UGE_NR_CuraContinua::StaticClass(), NRSetByCaller::Cura, Quantidade, Duracao);
}

void UNRAbilitySystemComponent::RestaurarMana(float Quantidade, float Duracao)
{
	AplicarContinuo(UGE_NR_Mana::StaticClass(), UGE_NR_ManaContinua::StaticClass(), NRSetByCaller::Mana, Quantidade, Duracao);
}

FActiveGameplayEffectHandle UNRAbilitySystemComponent::AplicarBonus(const FNRBonus& Bonus, float Duracao)
{
	if (!IsOwnerActorAuthoritative() || Bonus.IsZero())
	{
		return FActiveGameplayEffectHandle();
	}
	const bool bTemporario = Duracao > 0.f;
	FGameplayEffectSpecHandle Spec = CriarSpec(bTemporario ? UGE_NR_BonusTemporario::StaticClass() : UGE_NR_Bonus::StaticClass(), GetOwner());
	if (!Spec.IsValid())
	{
		return FActiveGameplayEffectHandle();
	}
	FGameplayEffectSpec& S = *Spec.Data.Get();
	if (bTemporario)
	{
		S.SetSetByCallerMagnitude(NRSetByCaller::Duracao, Duracao);
	}
	S.SetSetByCallerMagnitude(NRSetByCaller::VidaMax, Bonus.VidaMax);
	S.SetSetByCallerMagnitude(NRSetByCaller::ManaMax, Bonus.ManaMax);
	S.SetSetByCallerMagnitude(NRSetByCaller::Armadura, Bonus.Armadura);
	S.SetSetByCallerMagnitude(NRSetByCaller::DanoFisico, Bonus.DanoFisico);
	S.SetSetByCallerMagnitude(NRSetByCaller::PoderMagico, Bonus.PoderMagico);
	S.SetSetByCallerMagnitude(NRSetByCaller::VelocMov, Bonus.VelocMov);
	S.SetSetByCallerMagnitude(NRSetByCaller::VelocAtaque, Bonus.VelocAtaque);
	S.SetSetByCallerMagnitude(NRSetByCaller::ReducaoRecarga, Bonus.ReducaoRecarga);
	S.SetSetByCallerMagnitude(NRSetByCaller::RegenMana, Bonus.RegenMana);
	S.SetSetByCallerMagnitude(NRSetByCaller::RegenVida, Bonus.RegenVida);
	S.SetSetByCallerMagnitude(NRSetByCaller::BonusCura, Bonus.BonusCura);
	return ApplyGameplayEffectSpecToSelf(S);
}

void UNRAbilitySystemComponent::RemoverBonus(FActiveGameplayEffectHandle Efeito)
{
	if (IsOwnerActorAuthoritative() && Efeito.IsValid())
	{
		RemoveActiveGameplayEffect(Efeito);
	}
}

// ------------------------------------------------------------------------------------------------ Regeneração e eventos

void UNRAbilitySystemComponent::TickRegen()
{
	if (bMorto || !bInicializado)
	{
		return;
	}
	if (BonusVelocForaDeCombate != 0.f && IsEmCombate() != bEmCombateAntes)
	{
		AtualizarVelocidade();
	}
	const float RegenVida = GetNumericAttribute(UAS_Hero::GetRegenVidaAttribute());
	if (RegenVida > 0.f && GetVida() < GetVidaMax())
	{
		ApplyModToAttribute(UAS_Hero::GetVidaAttribute(), EGameplayModOp::AddBase, RegenVida * IntervaloRegen);
	}
	float RegenMana = GetNumericAttribute(UAS_Hero::GetRegenManaAttribute());
	if (!IsEmCombate())
	{
		RegenMana += RegenManaForaDeCombate - RegenManaEmCombate;
	}
	if (RegenMana > 0.f && GetMana() < GetManaMax())
	{
		ApplyModToAttribute(UAS_Hero::GetManaAttribute(), EGameplayModOp::AddBase, RegenMana * IntervaloRegen);
	}
}

void UNRAbilitySystemComponent::NotificarDano(float DanoFinal, AActor* Instigador, bool bMatou)
{
	OnDanoRecebido.Broadcast(DanoFinal, Instigador);
	if (bMatou && !bMorto)
	{
		bMorto = true;
		UE_LOG(LogNexus, Log, TEXT("%s morreu (assassino: %s)"), *GetNameSafe(GetOwner()), *GetNameSafe(Instigador));
		OnMorreu.Broadcast(Instigador);
	}
}

void UNRAbilitySystemComponent::OnVidaAtributo(const FOnAttributeChangeData& Dados)
{
	OnVidaMudou.Broadcast(GetVida(), GetVidaMax());
}

void UNRAbilitySystemComponent::OnManaAtributo(const FOnAttributeChangeData& Dados)
{
	OnManaMudou.Broadcast(GetMana(), GetManaMax());
}

void UNRAbilitySystemComponent::OnVelocAtributo(const FOnAttributeChangeData& Dados)
{
	AtualizarVelocidade();
}
