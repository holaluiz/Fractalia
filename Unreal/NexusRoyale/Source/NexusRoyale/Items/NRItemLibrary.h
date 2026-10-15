#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Items/NRItemTypes.h"
#include "NRItemLibrary.generated.h"

class UDataTable;
class UStaticMesh;

/** Funções de itens para os Blueprints de loot (baú, pickup, HUD). */
UCLASS()
class NEXUSROYALE_API UNRItemLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** /Game/NexusRoyale/Data/DT_Itens (criada pelo ue_gas_setup.py a partir de Unreal/Data/DT_Itens.csv). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Itens")
	static UDataTable* TabelaPadrao();

	/** Sorteia o id de uma linha de DT_Itens do tipo pedido (lendários só se bPermitirLendario). */
	UFUNCTION(BlueprintCallable, Category = "Nexus|Itens")
	static FName SortearItem(UDataTable* Tabela, ENRTipoItem Tipo, bool bPermitirLendario = false);

	/** Carrega a malha do item (síncrono; os itens são pequenos). */
	UFUNCTION(BlueprintCallable, Category = "Nexus|Itens")
	static UStaticMesh* CarregarMalha(UDataTable* Tabela, FName ItemId);

	UFUNCTION(BlueprintPure, Category = "Nexus|Itens")
	static FText NomeDoItem(UDataTable* Tabela, FName ItemId);

	UFUNCTION(BlueprintPure, Category = "Nexus|Itens")
	static ENRTipoItem TipoDoItem(UDataTable* Tabela, FName ItemId);

	/** 0 Comum, 1 Incomum, 2 Raro, 3 Épico, 4 Lendário. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Itens")
	static FText NomeDaRaridade(int32 Raridade);

	/** Cinza, verde, azul, roxo, dourado (GDD §8.1). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Itens")
	static FLinearColor CorDaRaridade(int32 Raridade);
};
