#include "Items/NRItemLibrary.h"

#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"

namespace
{
	const FNRItemRow* BuscarLinha(UDataTable* Tabela, FName ItemId)
	{
		return Tabela ? Tabela->FindRow<FNRItemRow>(ItemId, TEXT("UNRItemLibrary"), false) : nullptr;
	}
}

FName UNRItemLibrary::SortearItem(UDataTable* Tabela, ENRTipoItem Tipo, bool bPermitirLendario)
{
	if (!Tabela)
	{
		return NAME_None;
	}
	TArray<FName> Candidatos;
	Tabela->ForeachRow<FNRItemRow>(TEXT("UNRItemLibrary::SortearItem"), [&](const FName& Id, const FNRItemRow& Item)
	{
		if (Item.Tipo == Tipo && (bPermitirLendario || !Item.bLendario))
		{
			Candidatos.Add(Id);
		}
	});
	return Candidatos.Num() > 0 ? Candidatos[FMath::RandRange(0, Candidatos.Num() - 1)] : NAME_None;
}

UStaticMesh* UNRItemLibrary::CarregarMalha(UDataTable* Tabela, FName ItemId)
{
	const FNRItemRow* Item = BuscarLinha(Tabela, ItemId);
	return Item ? Item->Malha.LoadSynchronous() : nullptr;
}

UDataTable* UNRItemLibrary::TabelaPadrao()
{
	static TSoftObjectPtr<UDataTable> Tabela(FSoftObjectPath(TEXT("/Game/NexusRoyale/Data/DT_Itens.DT_Itens")));
	return Tabela.LoadSynchronous();
}

FText UNRItemLibrary::NomeDoItem(UDataTable* Tabela, FName ItemId)
{
	const FNRItemRow* Item = BuscarLinha(Tabela, ItemId);
	return Item ? Item->Nome : FText::FromName(ItemId);
}

ENRTipoItem UNRItemLibrary::TipoDoItem(UDataTable* Tabela, FName ItemId)
{
	const FNRItemRow* Item = BuscarLinha(Tabela, ItemId);
	return Item ? Item->Tipo : ENRTipoItem::Equipamento;
}

FText UNRItemLibrary::NomeDaRaridade(int32 Raridade)
{
	switch (Raridade)
	{
	case 0: return NSLOCTEXT("Nexus", "Comum", "Comum");
	case 1: return NSLOCTEXT("Nexus", "Incomum", "Incomum");
	case 2: return NSLOCTEXT("Nexus", "Raro", "Raro");
	case 3: return NSLOCTEXT("Nexus", "Epico", "Épico");
	default: return NSLOCTEXT("Nexus", "Lendario", "Lendário");
	}
}

FLinearColor UNRItemLibrary::CorDaRaridade(int32 Raridade)
{
	switch (Raridade)
	{
	case 0: return FLinearColor(0.6f, 0.6f, 0.6f);
	case 1: return FLinearColor(0.2f, 0.9f, 0.2f);
	case 2: return FLinearColor(0.2f, 0.5f, 1.0f);
	case 3: return FLinearColor(0.7f, 0.3f, 1.0f);
	default: return FLinearColor(1.0f, 0.75f, 0.1f);
	}
}
