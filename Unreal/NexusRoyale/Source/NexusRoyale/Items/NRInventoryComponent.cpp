#include "Items/NRInventoryComponent.h"

#include "Engine/DataTable.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "Items/NRItemLibrary.h"
#include "NexusRoyale.h"

UNRInventoryComponent::UNRInventoryComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	MultiplicadorRaridade = { 1.0f, 1.25f, 1.5f, 1.8f, 2.0f };
}

void UNRInventoryComponent::BeginPlay()
{
	Super::BeginPlay();
	Equipados.SetNum(static_cast<int32>(ENRSlotItem::Amuleto) + 1);
	Consumiveis.SetNum(SlotsConsumivel);
}

UNRAbilitySystemComponent* UNRInventoryComponent::GetASC() const
{
	return GetOwner() ? GetOwner()->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr;
}

float UNRInventoryComponent::Multiplicador(int32 Raridade) const
{
	return MultiplicadorRaridade.IsValidIndex(Raridade) ? MultiplicadorRaridade[Raridade] : 1.f;
}

const FNRItemRow* UNRInventoryComponent::Linha(FName ItemId) const
{
	return TabelaItens ? TabelaItens->FindRow<FNRItemRow>(ItemId, TEXT("UNRInventoryComponent"), false) : nullptr;
}

bool UNRInventoryComponent::PegarDoChao(FName ItemId, int32 Raridade)
{
	FName Largado;
	int32 RaridadeLargada = 0;
	const ENRResultadoPegar Resultado = Pegar(ItemId, Raridade, Largado, RaridadeLargada);
	const FText Nome = UNRItemLibrary::NomeDoItem(TabelaItens, ItemId);
	const FText Raro = UNRItemLibrary::NomeDaRaridade(Raridade);
	NoChaoId = ItemId;
	NoChaoRaridade = Raridade;
	switch (Resultado)
	{
	case ENRResultadoPegar::Pegou:
		Avisar(FText::Format(NSLOCTEXT("Nexus", "Pegou", "Pegou: {0} ({1})"), Nome, Raro));
		return true;
	case ENRResultadoPegar::Trocou:
		NoChaoId = Largado;
		NoChaoRaridade = RaridadeLargada;
		Avisar(FText::Format(NSLOCTEXT("Nexus", "Trocou", "Pegou: {0} ({1}) e largou {2}"), Nome, Raro,
			UNRItemLibrary::NomeDoItem(TabelaItens, Largado)));
		return Largado.IsNone();
	case ENRResultadoPegar::Cheio:
		Avisar(FText::Format(NSLOCTEXT("Nexus", "Cheio", "Consumíveis cheios: {0} ficou no chão"), Nome));
		return false;
	default:
		Avisar(FText::Format(NSLOCTEXT("Nexus", "Invalido", "Item desconhecido: {0}"), FText::FromName(ItemId)));
		return false;
	}
}

void UNRInventoryComponent::Avisar(const FText& Texto)
{
	Mensagem = Texto;
	TempoMensagem = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	UE_LOG(LogNexus, Log, TEXT("%s: %s"), *GetNameSafe(GetOwner()), *Texto.ToString());
}

FText UNRInventoryComponent::MensagemRecente() const
{
	const UWorld* World = GetWorld();
	return World && World->GetTimeSeconds() - TempoMensagem < 3.5 ? Mensagem : FText::GetEmpty();
}

bool UNRInventoryComponent::BuscarItem(FName ItemId, FNRItemRow& Saida) const
{
	if (const FNRItemRow* Item = Linha(ItemId))
	{
		Saida = *Item;
		return true;
	}
	return false;
}

ENRResultadoPegar UNRInventoryComponent::Pegar(FName ItemId, int32 Raridade, FName& ItemLargado, int32& RaridadeLargada)
{
	ItemLargado = NAME_None;
	RaridadeLargada = 0;
	const FNRItemRow* Item = Linha(ItemId);
	if (!Item)
	{
		UE_LOG(LogNexus, Warning, TEXT("Pegar: item '%s' nao esta em %s"), *ItemId.ToString(), *GetNameSafe(TabelaItens));
		return ENRResultadoPegar::Invalido;
	}
	ENRResultadoPegar Resultado = ENRResultadoPegar::Invalido;
	switch (Item->Tipo)
	{
	case ENRTipoItem::Equipamento: Resultado = Equipar(ItemId, Raridade, *Item, ItemLargado, RaridadeLargada); break;
	case ENRTipoItem::Consumivel: Resultado = GuardarConsumivel(ItemId, *Item); break;
	case ENRTipoItem::Grimorio: Resultado = GuardarGrimorio(ItemId, Raridade, ItemLargado, RaridadeLargada); break;
	}
	if (Resultado == ENRResultadoPegar::Pegou || Resultado == ENRResultadoPegar::Trocou)
	{
		OnInventarioMudou.Broadcast();
	}
	return Resultado;
}

ENRResultadoPegar UNRInventoryComponent::Equipar(FName ItemId, int32 Raridade, const FNRItemRow& Item, FName& ItemLargado, int32& RaridadeLargada)
{
	const int32 Indice = static_cast<int32>(Item.Slot);
	if (Item.Slot == ENRSlotItem::Nenhum || !Equipados.IsValidIndex(Indice))
	{
		return ENRResultadoPegar::Invalido;
	}
	UNRAbilitySystemComponent* ASC = GetASC();
	FNRItemGuardado& Atual = Equipados[Indice];
	const bool bTrocou = !Atual.ItemId.IsNone();
	if (bTrocou)
	{
		ItemLargado = Atual.ItemId;
		RaridadeLargada = Atual.Raridade;
		if (ASC)
		{
			ASC->RemoverBonus(Atual.Efeito);
		}
	}
	const float Pontos = (ASC && Item.EscalaComAtributo != ENRAtributoBuild::Nenhum)
		? ASC->GetPontosEfetivos(static_cast<int32>(Item.EscalaComAtributo) - 1) : 0.f;
	Atual.ItemId = ItemId;
	Atual.Raridade = Raridade;
	Atual.Efeito = ASC ? ASC->AplicarBonus(Item.CalcularBonus(Multiplicador(Raridade), Pontos)) : FActiveGameplayEffectHandle();
	return bTrocou ? ENRResultadoPegar::Trocou : ENRResultadoPegar::Pegou;
}

ENRResultadoPegar UNRInventoryComponent::GuardarConsumivel(FName ItemId, const FNRItemRow& Item)
{
	// Primeiro soma numa pilha do mesmo item que ainda tenha espaço; depois usa um slot vazio.
	for (FNRSlotConsumivel& Slot : Consumiveis)
	{
		if (Slot.ItemId == ItemId && Slot.Quantidade < FMath::Max(1, Item.Pilha))
		{
			++Slot.Quantidade;
			return ENRResultadoPegar::Pegou;
		}
	}
	for (FNRSlotConsumivel& Slot : Consumiveis)
	{
		if (Slot.Quantidade <= 0)
		{
			Slot.ItemId = ItemId;
			Slot.Quantidade = 1;
			return ENRResultadoPegar::Pegou;
		}
	}
	return ENRResultadoPegar::Cheio;
}

ENRResultadoPegar UNRInventoryComponent::GuardarGrimorio(FName ItemId, int32 Raridade, FName& ItemLargado, int32& RaridadeLargada)
{
	// TODO(magias): grimório repetido sobe o rank da magia, e o jogador escolhe se troca o E ou o R (GDD §4.4).
	FNRItemGuardado Novo;
	Novo.ItemId = ItemId;
	Novo.Raridade = Raridade;
	if (Grimorios.Num() < MaxGrimorios)
	{
		Grimorios.Add(Novo);
		return ENRResultadoPegar::Pegou;
	}
	ItemLargado = Grimorios[0].ItemId;
	RaridadeLargada = Grimorios[0].Raridade;
	Grimorios.RemoveAt(0);
	Grimorios.Add(Novo);
	return ENRResultadoPegar::Trocou;
}

bool UNRInventoryComponent::UsarConsumivel(int32 Indice)
{
	if (!Consumiveis.IsValidIndex(Indice) || Consumiveis[Indice].Quantidade <= 0)
	{
		return false;
	}
	FNRSlotConsumivel& Slot = Consumiveis[Indice];
	const FNRItemRow* Item = Linha(Slot.ItemId);
	UNRAbilitySystemComponent* ASC = GetASC();
	if (!Item || !ASC || ASC->IsMorto())
	{
		return false;
	}
	if (Item->Cura > 0.f)
	{
		ASC->Curar(Item->Cura, Item->CuraDuracao);
	}
	if (Item->Mana > 0.f)
	{
		ASC->RestaurarMana(Item->Mana, Item->ManaDuracao);
	}
	if (Item->Pressa != 0.f && Item->PressaDuracao > 0.f)
	{
		FNRBonus Pressa;
		Pressa.VelocMov = Item->Pressa;
		ASC->AplicarBonus(Pressa, Item->PressaDuracao);
	}
	// Anda mais devagar enquanto come ou bebe (GDD §8.3).
	const float TempoDeUso = FMath::Max(Item->CuraDuracao, Item->ManaDuracao);
	if (LentidaoAoConsumir > 0.f && TempoDeUso > 0.f)
	{
		FNRBonus Lentidao;
		Lentidao.VelocMov = -LentidaoAoConsumir;
		ASC->AplicarBonus(Lentidao, TempoDeUso);
	}
	Avisar(FText::Format(NSLOCTEXT("Nexus", "Usou", "Usou: {0}"), Item->Nome));
	if (--Slot.Quantidade <= 0)
	{
		Slot = FNRSlotConsumivel();
	}
	OnInventarioMudou.Broadcast();
	return true;
}

FText UNRInventoryComponent::DescreverConsumivel(int32 Indice) const
{
	if (!Consumiveis.IsValidIndex(Indice) || Consumiveis[Indice].Quantidade <= 0)
	{
		return FText::GetEmpty();
	}
	const FNRSlotConsumivel& Slot = Consumiveis[Indice];
	const FNRItemRow* Item = Linha(Slot.ItemId);
	const FText Nome = Item ? Item->Nome : FText::FromName(Slot.ItemId);
	return FText::Format(NSLOCTEXT("Nexus", "SlotConsumivel", "{0} x{1}"), Nome, FText::AsNumber(Slot.Quantidade));
}

FText UNRInventoryComponent::DescreverEquipado(ENRSlotItem SlotItem) const
{
	const int32 Indice = static_cast<int32>(SlotItem);
	if (!Equipados.IsValidIndex(Indice) || Equipados[Indice].ItemId.IsNone())
	{
		return FText::GetEmpty();
	}
	const FNRItemGuardado& Guardado = Equipados[Indice];
	const FNRItemRow* Item = Linha(Guardado.ItemId);
	const FText Nome = Item ? Item->Nome : FText::FromName(Guardado.ItemId);
	return FText::Format(NSLOCTEXT("Nexus", "ItemEquipado", "{0} ({1})"), Nome, UNRItemLibrary::NomeDaRaridade(Guardado.Raridade));
}
