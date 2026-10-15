#include "GAS/NRGameplayEffects.h"

#include "GAS/AS_Hero.h"

namespace NRSetByCaller
{
	const FName Dano(TEXT("Dano"));
	const FName DanoVerdadeiro(TEXT("DanoVerdadeiro"));
	const FName Cura(TEXT("Cura"));
	const FName Mana(TEXT("Mana"));
	const FName Duracao(TEXT("Duracao"));
	const FName VidaMax(TEXT("VidaMax"));
	const FName ManaMax(TEXT("ManaMax"));
	const FName Armadura(TEXT("Armadura"));
	const FName DanoFisico(TEXT("DanoFisico"));
	const FName PoderMagico(TEXT("PoderMagico"));
	const FName VelocMov(TEXT("VelocMov"));
	const FName VelocAtaque(TEXT("VelocAtaque"));
	const FName ReducaoRecarga(TEXT("ReducaoRecarga"));
	const FName RegenMana(TEXT("RegenMana"));
	const FName RegenVida(TEXT("RegenVida"));
	const FName BonusCura(TEXT("BonusCura"));
}

namespace
{
	/** Período dos efeitos contínuos (cura e mana ao longo do tempo). */
	constexpr float PeriodoContinuo = 0.25f;

	FGameplayEffectModifierMagnitude PorNome(FName Nome)
	{
		FSetByCallerFloat SetByCaller;
		SetByCaller.DataName = Nome;
		return FGameplayEffectModifierMagnitude(SetByCaller);
	}

	void Somar(UGameplayEffect* Efeito, const FGameplayAttribute& Atributo, FName Nome)
	{
		FGameplayModifierInfo Info;
		Info.Attribute = Atributo;
		Info.ModifierOp = EGameplayModOp::AddBase;
		Info.ModifierMagnitude = PorNome(Nome);
		Efeito->Modifiers.Add(Info);
	}

	void SomarBonus(UGameplayEffect* Efeito)
	{
		Somar(Efeito, UAS_Hero::GetVidaMaxAttribute(), NRSetByCaller::VidaMax);
		Somar(Efeito, UAS_Hero::GetManaMaxAttribute(), NRSetByCaller::ManaMax);
		Somar(Efeito, UAS_Hero::GetArmaduraAttribute(), NRSetByCaller::Armadura);
		Somar(Efeito, UAS_Hero::GetDanoFisicoAttribute(), NRSetByCaller::DanoFisico);
		Somar(Efeito, UAS_Hero::GetPoderMagicoAttribute(), NRSetByCaller::PoderMagico);
		Somar(Efeito, UAS_Hero::GetVelocMovAttribute(), NRSetByCaller::VelocMov);
		Somar(Efeito, UAS_Hero::GetVelocAtaqueAttribute(), NRSetByCaller::VelocAtaque);
		Somar(Efeito, UAS_Hero::GetReducaoRecargaAttribute(), NRSetByCaller::ReducaoRecarga);
		Somar(Efeito, UAS_Hero::GetRegenManaAttribute(), NRSetByCaller::RegenMana);
		Somar(Efeito, UAS_Hero::GetRegenVidaAttribute(), NRSetByCaller::RegenVida);
		Somar(Efeito, UAS_Hero::GetBonusCuraAttribute(), NRSetByCaller::BonusCura);
	}

	void ComDuracao(UGameplayEffect* Efeito, bool bPeriodico)
	{
		Efeito->DurationPolicy = EGameplayEffectDurationType::HasDuration;
		Efeito->DurationMagnitude = PorNome(NRSetByCaller::Duracao);
		if (bPeriodico)
		{
			Efeito->Period = FScalableFloat(PeriodoContinuo);
			Efeito->bExecutePeriodicEffectOnApplication = false;
		}
	}
}

UGE_NR_Dano::UGE_NR_Dano()
{
	DurationPolicy = EGameplayEffectDurationType::Instant;
	Somar(this, UAS_Hero::GetDanoAttribute(), NRSetByCaller::Dano);
	Somar(this, UAS_Hero::GetDanoVerdadeiroAttribute(), NRSetByCaller::DanoVerdadeiro);
}

UGE_NR_Cura::UGE_NR_Cura()
{
	DurationPolicy = EGameplayEffectDurationType::Instant;
	Somar(this, UAS_Hero::GetCuraAttribute(), NRSetByCaller::Cura);
}

UGE_NR_CuraContinua::UGE_NR_CuraContinua()
{
	ComDuracao(this, true);
	Somar(this, UAS_Hero::GetCuraAttribute(), NRSetByCaller::Cura);
}

UGE_NR_Mana::UGE_NR_Mana()
{
	DurationPolicy = EGameplayEffectDurationType::Instant;
	Somar(this, UAS_Hero::GetManaAttribute(), NRSetByCaller::Mana);
}

UGE_NR_ManaContinua::UGE_NR_ManaContinua()
{
	ComDuracao(this, true);
	Somar(this, UAS_Hero::GetManaAttribute(), NRSetByCaller::Mana);
}

UGE_NR_Bonus::UGE_NR_Bonus()
{
	DurationPolicy = EGameplayEffectDurationType::Infinite;
	SomarBonus(this);
}

UGE_NR_BonusTemporario::UGE_NR_BonusTemporario()
{
	ComDuracao(this, false);
	SomarBonus(this);
}
