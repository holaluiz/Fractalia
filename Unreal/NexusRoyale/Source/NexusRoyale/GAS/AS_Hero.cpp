#include "GAS/AS_Hero.h"

#include "GameplayEffect.h"
#include "GameplayEffectExtension.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "Net/UnrealNetwork.h"

UAS_Hero::UAS_Hero()
{
	// Valores neutros; o UNRAbilitySystemComponent::InicializarHeroi coloca os do arquétipo e da build.
	InitVida(1.f);
	InitVidaMax(1.f);
	InitMana(0.f);
	InitManaMax(1.f);
}

void UAS_Hero::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);

	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Vida, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, VidaMax, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, RegenVida, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Mana, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, ManaMax, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, RegenMana, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Forca, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Agilidade, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Vitalidade, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Intelecto, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Espirito, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, DanoFisico, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, PoderMagico, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, Armadura, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, VelocMov, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, VelocAtaque, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, ReducaoRecarga, COND_None, REPNOTIFY_Always);
	DOREPLIFETIME_CONDITION_NOTIFY(UAS_Hero, BonusCura, COND_None, REPNOTIFY_Always);
}

void UAS_Hero::ClampVital(const FGameplayAttribute& Attribute, float& NewValue) const
{
	if (Attribute == GetVidaAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.f, GetVidaMax());
	}
	else if (Attribute == GetManaAttribute())
	{
		NewValue = FMath::Clamp(NewValue, 0.f, GetManaMax());
	}
	else if (Attribute == GetVidaMaxAttribute() || Attribute == GetManaMaxAttribute())
	{
		NewValue = FMath::Max(NewValue, 1.f);
	}
}

void UAS_Hero::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
	Super::PreAttributeChange(Attribute, NewValue);
	ClampVital(Attribute, NewValue);
}

void UAS_Hero::PreAttributeBaseChange(const FGameplayAttribute& Attribute, float& NewValue) const
{
	Super::PreAttributeBaseChange(Attribute, NewValue);
	ClampVital(Attribute, NewValue);
}

void UAS_Hero::PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue)
{
	Super::PostAttributeChange(Attribute, OldValue, NewValue);

	// Quando o máximo muda (item, nível, build), a vida/mana atual mantém a mesma porcentagem.
	UAbilitySystemComponent* ASC = GetOwningAbilitySystemComponent();
	if (!ASC || !ASC->IsOwnerActorAuthoritative() || OldValue <= 0.f || FMath::IsNearlyEqual(OldValue, NewValue))
	{
		return;
	}
	if (Attribute == GetVidaMaxAttribute())
	{
		ASC->ApplyModToAttribute(GetVidaAttribute(), EGameplayModOp::Override, GetVida() * NewValue / OldValue);
	}
	else if (Attribute == GetManaMaxAttribute())
	{
		ASC->ApplyModToAttribute(GetManaAttribute(), EGameplayModOp::Override, GetMana() * NewValue / OldValue);
	}
}

void UAS_Hero::PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data)
{
	Super::PostGameplayEffectExecute(Data);

	const FGameplayAttribute& Attribute = Data.EvaluatedData.Attribute;
	UNRAbilitySystemComponent* ASC = Cast<UNRAbilitySystemComponent>(&Data.Target);
	AActor* Instigador = Data.EffectSpec.GetContext().GetOriginalInstigator();

	if (Attribute == GetDanoAttribute() || Attribute == GetDanoVerdadeiroAttribute())
	{
		const bool bArmadura = Attribute == GetDanoAttribute();
		float Bruto = bArmadura ? GetDano() : GetDanoVerdadeiro();
		SetDano(0.f);
		SetDanoVerdadeiro(0.f);
		if (Bruto <= 0.f)
		{
			return;
		}
		if (bArmadura)
		{
			const float A = FMath::Max(0.f, GetArmadura());
			Bruto *= 1.f - (FatorArmadura * A) / (1.f + FatorArmadura * A);
		}
		const float VidaAntes = GetVida();
		SetVida(FMath::Clamp(VidaAntes - Bruto, 0.f, GetVidaMax()));
		if (ASC)
		{
			ASC->NotificarDano(VidaAntes - GetVida(), Instigador, VidaAntes > 0.f && GetVida() <= 0.f);
		}
	}
	else if (Attribute == GetCuraAttribute())
	{
		const float Valor = GetCura() * (1.f + GetBonusCura());
		SetCura(0.f);
		if (Valor > 0.f && GetVida() > 0.f)
		{
			SetVida(FMath::Clamp(GetVida() + Valor, 0.f, GetVidaMax()));
		}
	}
	else if (Attribute == GetVidaAttribute())
	{
		SetVida(FMath::Clamp(GetVida(), 0.f, GetVidaMax()));
	}
	else if (Attribute == GetManaAttribute())
	{
		SetMana(FMath::Clamp(GetMana(), 0.f, GetManaMax()));
	}
}

void UAS_Hero::OnRep_Vida(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Vida, OldValue); }
void UAS_Hero::OnRep_VidaMax(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, VidaMax, OldValue); }
void UAS_Hero::OnRep_RegenVida(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, RegenVida, OldValue); }
void UAS_Hero::OnRep_Mana(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Mana, OldValue); }
void UAS_Hero::OnRep_ManaMax(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, ManaMax, OldValue); }
void UAS_Hero::OnRep_RegenMana(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, RegenMana, OldValue); }
void UAS_Hero::OnRep_Forca(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Forca, OldValue); }
void UAS_Hero::OnRep_Agilidade(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Agilidade, OldValue); }
void UAS_Hero::OnRep_Vitalidade(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Vitalidade, OldValue); }
void UAS_Hero::OnRep_Intelecto(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Intelecto, OldValue); }
void UAS_Hero::OnRep_Espirito(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Espirito, OldValue); }
void UAS_Hero::OnRep_DanoFisico(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, DanoFisico, OldValue); }
void UAS_Hero::OnRep_PoderMagico(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, PoderMagico, OldValue); }
void UAS_Hero::OnRep_Armadura(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, Armadura, OldValue); }
void UAS_Hero::OnRep_VelocMov(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, VelocMov, OldValue); }
void UAS_Hero::OnRep_VelocAtaque(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, VelocAtaque, OldValue); }
void UAS_Hero::OnRep_ReducaoRecarga(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, ReducaoRecarga, OldValue); }
void UAS_Hero::OnRep_BonusCura(const FGameplayAttributeData& OldValue) { GAMEPLAYATTRIBUTE_REPNOTIFY(UAS_Hero, BonusCura, OldValue); }
