#pragma once

#include "CoreMinimal.h"
#include "GameplayEffect.h"
#include "NRGameplayEffects.generated.h"

/**
 * Efeitos "mecânicos" do jogo, definidos em C++ porque os números vêm sempre por SetByCaller
 * (nomes em NRSetByCaller). Quem aplica é o UNRAbilitySystemComponent; o Blueprint não precisa
 * mexer neles. Efeitos de conteúdo (magias, mutações) continuam como assets GE_* em Blueprint.
 */
namespace NRSetByCaller
{
	extern NEXUSROYALE_API const FName Dano;
	extern NEXUSROYALE_API const FName DanoVerdadeiro;
	extern NEXUSROYALE_API const FName Cura;
	extern NEXUSROYALE_API const FName Mana;
	extern NEXUSROYALE_API const FName Duracao;
	extern NEXUSROYALE_API const FName VidaMax;
	extern NEXUSROYALE_API const FName ManaMax;
	extern NEXUSROYALE_API const FName Armadura;
	extern NEXUSROYALE_API const FName DanoFisico;
	extern NEXUSROYALE_API const FName PoderMagico;
	extern NEXUSROYALE_API const FName VelocMov;
	extern NEXUSROYALE_API const FName VelocAtaque;
	extern NEXUSROYALE_API const FName ReducaoRecarga;
	extern NEXUSROYALE_API const FName RegenMana;
	extern NEXUSROYALE_API const FName RegenVida;
	extern NEXUSROYALE_API const FName BonusCura;
}

/** Instantâneo: Dano (passa pela armadura) e DanoVerdadeiro (não passa). */
UCLASS(MinimalAPI)
class UGE_NR_Dano : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_Dano();
};

/** Instantâneo: Cura (multiplicada por 1 + BonusCura no AS_Hero). */
UCLASS(MinimalAPI)
class UGE_NR_Cura : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_Cura();
};

/** Cura ao longo do tempo: Duracao por SetByCaller, um tique de Cura a cada 0,25 s. */
UCLASS(MinimalAPI)
class UGE_NR_CuraContinua : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_CuraContinua();
};

/** Instantâneo: soma Mana. */
UCLASS(MinimalAPI)
class UGE_NR_Mana : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_Mana();
};

/** Mana ao longo do tempo: Duracao por SetByCaller, um tique de Mana a cada 0,25 s. */
UCLASS(MinimalAPI)
class UGE_NR_ManaContinua : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_ManaContinua();
};

/** Bônus de atributos sem duração (itens equipados). Cada atributo vem por SetByCaller. */
UCLASS(MinimalAPI)
class UGE_NR_Bonus : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_Bonus();
};

/** Bônus de atributos temporário (Poção de Pressa, lentidão ao consumir). Duracao por SetByCaller. */
UCLASS(MinimalAPI)
class UGE_NR_BonusTemporario : public UGameplayEffect
{
	GENERATED_BODY()
public:
	UGE_NR_BonusTemporario();
};
