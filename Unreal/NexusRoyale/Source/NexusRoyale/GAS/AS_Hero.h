#pragma once

#include "CoreMinimal.h"
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "AS_Hero.generated.h"

/**
 * Atributos do herói (GDD §4.2, §5, §9 e §16).
 *
 * - Vida, VidaMax, Mana, ManaMax e Armadura: valores absolutos.
 * - RegenVida e RegenMana: por segundo. RegenMana é a regeneração EM combate; o bônus de fora de combate
 *   fica no UNRAbilitySystemComponent.
 * - Forca, Agilidade, Vitalidade, Intelecto e Espirito: PONTOS EFETIVOS (já com o retorno decrescente).
 * - DanoFisico, PoderMagico, VelocMov, VelocAtaque, ReducaoRecarga e BonusCura: bônus em fração
 *   (0,27 = +27%). Todos somam entre si, inclusive o do nível (GDD §9).
 * - Dano, DanoVerdadeiro e Cura: meta-atributos. Não replicam; o PostGameplayEffectExecute converte em Vida.
 *   Dano passa pela armadura; DanoVerdadeiro (tempestade) não.
 */
UCLASS()
class NEXUSROYALE_API UAS_Hero : public UAttributeSet
{
	GENERATED_BODY()

public:
	UAS_Hero();

	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;
	virtual void PreAttributeBaseChange(const FGameplayAttribute& Attribute, float& NewValue) const override;
	virtual void PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue) override;
	virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;

	/** Fator da armadura: redução = F·A / (1 + F·A). Com 0,04 e 10 de armadura, 28,6% (GDD §9). */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Balanceamento")
	float FatorArmadura = 0.04f;

	// --- Vida e mana
	UPROPERTY(BlueprintReadOnly, Category = "Vida", ReplicatedUsing = OnRep_Vida)
	FGameplayAttributeData Vida;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Vida)

	UPROPERTY(BlueprintReadOnly, Category = "Vida", ReplicatedUsing = OnRep_VidaMax)
	FGameplayAttributeData VidaMax;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, VidaMax)

	UPROPERTY(BlueprintReadOnly, Category = "Vida", ReplicatedUsing = OnRep_RegenVida)
	FGameplayAttributeData RegenVida;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, RegenVida)

	UPROPERTY(BlueprintReadOnly, Category = "Mana", ReplicatedUsing = OnRep_Mana)
	FGameplayAttributeData Mana;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Mana)

	UPROPERTY(BlueprintReadOnly, Category = "Mana", ReplicatedUsing = OnRep_ManaMax)
	FGameplayAttributeData ManaMax;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, ManaMax)

	UPROPERTY(BlueprintReadOnly, Category = "Mana", ReplicatedUsing = OnRep_RegenMana)
	FGameplayAttributeData RegenMana;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, RegenMana)

	// --- Atributos da build (pontos efetivos)
	UPROPERTY(BlueprintReadOnly, Category = "Build", ReplicatedUsing = OnRep_Forca)
	FGameplayAttributeData Forca;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Forca)

	UPROPERTY(BlueprintReadOnly, Category = "Build", ReplicatedUsing = OnRep_Agilidade)
	FGameplayAttributeData Agilidade;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Agilidade)

	UPROPERTY(BlueprintReadOnly, Category = "Build", ReplicatedUsing = OnRep_Vitalidade)
	FGameplayAttributeData Vitalidade;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Vitalidade)

	UPROPERTY(BlueprintReadOnly, Category = "Build", ReplicatedUsing = OnRep_Intelecto)
	FGameplayAttributeData Intelecto;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Intelecto)

	UPROPERTY(BlueprintReadOnly, Category = "Build", ReplicatedUsing = OnRep_Espirito)
	FGameplayAttributeData Espirito;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Espirito)

	// --- Combate (bônus em fração, exceto Armadura)
	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_DanoFisico)
	FGameplayAttributeData DanoFisico;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, DanoFisico)

	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_PoderMagico)
	FGameplayAttributeData PoderMagico;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, PoderMagico)

	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_Armadura)
	FGameplayAttributeData Armadura;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Armadura)

	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_VelocMov)
	FGameplayAttributeData VelocMov;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, VelocMov)

	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_VelocAtaque)
	FGameplayAttributeData VelocAtaque;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, VelocAtaque)

	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_ReducaoRecarga)
	FGameplayAttributeData ReducaoRecarga;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, ReducaoRecarga)

	UPROPERTY(BlueprintReadOnly, Category = "Combate", ReplicatedUsing = OnRep_BonusCura)
	FGameplayAttributeData BonusCura;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, BonusCura)

	// --- Meta-atributos (só no servidor)
	UPROPERTY(BlueprintReadOnly, Category = "Meta")
	FGameplayAttributeData Dano;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Dano)

	UPROPERTY(BlueprintReadOnly, Category = "Meta")
	FGameplayAttributeData DanoVerdadeiro;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, DanoVerdadeiro)

	UPROPERTY(BlueprintReadOnly, Category = "Meta")
	FGameplayAttributeData Cura;
	ATTRIBUTE_ACCESSORS_BASIC(UAS_Hero, Cura)

protected:
	UFUNCTION() void OnRep_Vida(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_VidaMax(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_RegenVida(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Mana(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_ManaMax(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_RegenMana(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Forca(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Agilidade(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Vitalidade(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Intelecto(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Espirito(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_DanoFisico(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_PoderMagico(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_Armadura(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_VelocMov(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_VelocAtaque(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_ReducaoRecarga(const FGameplayAttributeData& OldValue);
	UFUNCTION() void OnRep_BonusCura(const FGameplayAttributeData& OldValue);

private:
	/** Mantém Vida/Mana dentro de [0, máximo]; os máximos nunca ficam abaixo de 1. */
	void ClampVital(const FGameplayAttribute& Attribute, float& NewValue) const;
};
