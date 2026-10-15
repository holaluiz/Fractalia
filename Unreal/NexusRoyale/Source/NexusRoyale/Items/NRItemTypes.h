#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "NRItemTypes.generated.h"

class UStaticMesh;

UENUM(BlueprintType)
enum class ENRTipoItem : uint8
{
	Equipamento,
	Grimorio,
	Consumivel
};

/** Slots de equipamento (GDD §8.1). */
UENUM(BlueprintType)
enum class ENRSlotItem : uint8
{
	Nenhum,
	Armadura,
	Cabeca,
	Anel,
	Amuleto
};

/** Atributo da build usado pelos amuletos "por ponto" (GDD §8.1). */
UENUM(BlueprintType)
enum class ENRAtributoBuild : uint8
{
	Nenhum,
	Forca,
	Agilidade,
	Vitalidade,
	Intelecto,
	Espirito
};

/**
 * Uma linha de DT_Itens (importada de Unreal/Data/DT_Itens.csv). Os números são da raridade Comum;
 * as outras multiplicam (UNRInventoryComponent::MultiplicadorRaridade). Frações: 0,04 = +4%.
 * Se EscalaComAtributo não for Nenhum, os bônus valem POR PONTO EFETIVO daquele atributo.
 */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRItemRow : public FTableRowBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item") FText Nome;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item") ENRTipoItem Tipo = ENRTipoItem::Equipamento;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item") ENRSlotItem Slot = ENRSlotItem::Nenhum;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item") TSoftObjectPtr<UStaticMesh> Malha;
	/** Só aparece em baú dourado, elite e drop aéreo (GDD §8.1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Item") bool bLendario = false;

	// Equipamento
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float VidaMax = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float ManaMax = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float Armadura = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float DanoFisico = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float PoderMagico = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float VelocMov = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float VelocAtaque = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float ReducaoRecarga = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") float RegenMana = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Equipamento") ENRAtributoBuild EscalaComAtributo = ENRAtributoBuild::Nenhum;

	// Consumível
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") float Cura = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") float CuraDuracao = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") float Mana = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") float ManaDuracao = 0.f;
	/** Bônus de velocidade temporário (Poção de Pressa: 0,25 por 6 s). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") float Pressa = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") float PressaDuracao = 0.f;
	/** Quantos cabem num slot de consumível. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Consumivel") int32 Pilha = 1;

	// Grimório
	/** Nome da magia que o grimório ensina (as magias ainda não existem; etapa 1, passo 2). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Grimorio") FName Magia;

	/** Bônus do equipamento para uma raridade e os pontos efetivos do atributo de escala. */
	FNRBonus CalcularBonus(float Multiplicador, float PontosDoAtributo) const;
};

/** Um slot de consumível (teclas 1 a 3). */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRSlotConsumivel
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Inventario") FName ItemId;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Inventario") int32 Quantidade = 0;
};

/** Um item equipado ou um grimório guardado. */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRItemGuardado
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Inventario") FName ItemId;
	/** 0 Comum, 1 Incomum, 2 Raro, 3 Épico, 4 Lendário. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Inventario") int32 Raridade = 0;
	UPROPERTY(BlueprintReadOnly, Category = "Inventario") FActiveGameplayEffectHandle Efeito;
};
