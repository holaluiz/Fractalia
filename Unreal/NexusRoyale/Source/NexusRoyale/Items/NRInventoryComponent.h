#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Items/NRItemTypes.h"
#include "NRInventoryComponent.generated.h"

class UDataTable;
class UNRAbilitySystemComponent;

UENUM(BlueprintType)
enum class ENRResultadoPegar : uint8
{
	/** Guardou num espaço livre ou somou à pilha. */
	Pegou,
	/** Trocou com o que estava no slot; o antigo sai em ItemLargado (o Blueprint solta no chão). */
	Trocou,
	/** Não coube (slots de consumível cheios); o item fica no chão. */
	Cheio,
	/** Item que não existe na tabela. */
	Invalido
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNRInventarioMudou);

/**
 * Inventário do herói (GDD §8): 4 slots de equipamento, 3 de consumível (teclas 1-3) e os grimórios (E e R).
 * Equipar aplica o bônus do item no UNRAbilitySystemComponent do mesmo ator; trocar remove o bônus antigo.
 */
UCLASS(ClassGroup = (Nexus), meta = (BlueprintSpawnableComponent, DisplayName = "Nexus Inventory"))
class NEXUSROYALE_API UNRInventoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNRInventoryComponent();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	TObjectPtr<UDataTable> TabelaItens;

	/** Comum, Incomum, Raro, Épico, Lendário (GDD §8.1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	TArray<float> MultiplicadorRaridade;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	int32 SlotsConsumivel = 3;

	/** Grimórios guardados para os slots E e R (GDD §4.4). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	int32 MaxGrimorios = 2;

	/** Enquanto come ou bebe, anda com esta fração a menos de velocidade (GDD §8.3: a 50%). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	float LentidaoAoConsumir = 0.5f;

	/** Índice = ENRSlotItem (0, Nenhum, fica sempre vazio). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	TArray<FNRItemGuardado> Equipados;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	TArray<FNRSlotConsumivel> Consumiveis;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Inventario")
	TArray<FNRItemGuardado> Grimorios;

	UPROPERTY(BlueprintAssignable, Category = "Nexus|Inventario")
	FNRInventarioMudou OnInventarioMudou;

	/** Pega um item do chão. Se trocou, ItemLargado/RaridadeLargada dizem o que soltar no chão. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Inventario")
	ENRResultadoPegar Pegar(FName ItemId, int32 Raridade, FName& ItemLargado, int32& RaridadeLargada);

	/**
	 * Versão para o pickup no chão, sem pinos de saída (mais simples na DSL).
	 * true = pegou, destrua o pickup. false = o pickup fica: depois de uma troca, ele passa a mostrar o item que
	 * saiu do slot (ItemQueFicaNoChao/RaridadeQueFicaNoChao); se não coube, continua o mesmo item.
	 * Também deixa uma mensagem para o HUD (MensagemRecente).
	 */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Inventario")
	bool PegarDoChao(FName ItemId, int32 Raridade);

	UFUNCTION(BlueprintPure, Category = "Nexus|Inventario")
	FName ItemQueFicaNoChao() const { return NoChaoId; }

	UFUNCTION(BlueprintPure, Category = "Nexus|Inventario")
	int32 RaridadeQueFicaNoChao() const { return NoChaoRaridade; }

	/** Última mensagem do inventário ("Pegou: …"), vazia depois de alguns segundos. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Inventario")
	FText MensagemRecente() const;

	/** Usa um consumível do slot 0-2. Retorna false se o slot está vazio. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Inventario")
	bool UsarConsumivel(int32 Slot);

	UFUNCTION(BlueprintPure, Category = "Nexus|Inventario")
	bool BuscarItem(FName ItemId, FNRItemRow& Saida) const;

	/** Texto curto do slot de consumível para o HUD ("Comida leve ×3"), vazio se não tem nada. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Inventario")
	FText DescreverConsumivel(int32 Slot) const;

	/** Texto curto do item equipado num slot ("Cota de Placas (Raro)"), vazio se não tem nada. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Inventario")
	FText DescreverEquipado(ENRSlotItem Slot) const;

protected:
	virtual void BeginPlay() override;

private:
	UNRAbilitySystemComponent* GetASC() const;
	float Multiplicador(int32 Raridade) const;
	const FNRItemRow* Linha(FName ItemId) const;
	ENRResultadoPegar Equipar(FName ItemId, int32 Raridade, const FNRItemRow& Item, FName& ItemLargado, int32& RaridadeLargada);
	ENRResultadoPegar GuardarConsumivel(FName ItemId, const FNRItemRow& Item);
	ENRResultadoPegar GuardarGrimorio(FName ItemId, int32 Raridade, FName& ItemLargado, int32& RaridadeLargada);
	void Avisar(const FText& Texto);

	FName NoChaoId;
	int32 NoChaoRaridade = 0;
	FText Mensagem;
	double TempoMensagem = -1000.0;
};
