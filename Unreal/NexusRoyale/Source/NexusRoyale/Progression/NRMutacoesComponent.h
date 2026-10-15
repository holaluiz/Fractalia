#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NRMutacoesComponent.generated.h"

class UNRAbilitySystemComponent;
class UNRCombateComponent;

/**
 * Mutações do GDD §7.4 que o kit atual consegue usar (Feiticeiro de Fogo: Bola de Fogo, Muralha de Gelo, Chuva de
 * Meteoros). Ficam de fora, até existirem: esquiva com 2 cargas, +1 slot de consumível, abates revelam o inimigo e as
 * mutações das magias que o Feiticeiro de Fogo não tem.
 */
UENUM(BlueprintType)
enum class ENRMutacao : uint8
{
	Nenhuma,
	Forca,
	Agilidade,
	Vitalidade,
	Intelecto,
	Espirito,
	/** Bola de Fogo: deixa chão em chamas por 3 s. */
	BolaDeFogoChamas,
	/** Muralha de Gelo: +50% de largura. */
	MuralhaLarga,
	/** −20% de recarga da ultimate. */
	UltimateRecarga,
	/** +30% de área da ultimate. */
	UltimateArea,
	/** A ultimate devolve 50% da mana gasta. */
	UltimateMana,
	/** +8% de velocidade fora de combate. */
	VelocidadeForaDeCombate,
	/** +15% de cura de consumíveis. */
	CuraConsumiveis,
	Total UMETA(Hidden)
};

UENUM(BlueprintType)
enum class ENRCategoriaMutacao : uint8
{
	Atributo,
	Magia,
	Ultimate,
	Geral
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNRMutacaoEscolhida, ENRMutacao, Mutacao);

/**
 * Mutações (GDD §7.4): a cada nível, do 2 ao 10, aparecem OpcoesPorNivel mutações e o jogador escolhe uma com
 * Alt+1/2/3, ou deixa para depois, sem limite de tempo. As escolhas acumulam numa fila (subir dois níveis de uma vez
 * deixa duas). Há TrocasPorPartida trocas de opções por partida (Alt+4). As teclas chegam pelo UNRCombateComponent.
 *
 * - Atributo: +2 pontos efetivos (podem repetir), com peso maior nos atributos em que a build investiu.
 * - Magia e Geral: uma vez cada.
 * - Ultimate: só nos NiveisUltimate (8 e 10), e então uma das opções é sempre de ultimate, se ainda houver.
 * Os efeitos mexem nos números do UNRCombateComponent e do UNRAbilitySystemComponent do mesmo ator.
 */
UCLASS(ClassGroup = (Nexus), meta = (BlueprintSpawnableComponent, DisplayName = "Nexus Mutacoes"))
class NEXUSROYALE_API UNRMutacoesComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNRMutacoesComponent();

	// ---------------------------------------------------------------- Regras (GDD §7.4)
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes", meta = (ClampMin = "1", ClampMax = "4"))
	int32 OpcoesPorNivel = 3;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes")
	int32 TrocasPorPartida = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes")
	TArray<int32> NiveisUltimate;

	// ---------------------------------------------------------------- Números (GDD §7.4)
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float PontosPorAtributo = 2.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float DuracaoChamasBolaDeFogo = 3.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float LarguraExtraMuralha = 0.5f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float ReducaoRecargaUltimate = 0.2f;
	/** Fração de ÁREA: o raio cresce √(1 + AreaExtraUltimate), e o raio de cada meteoro junto. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float AreaExtraUltimate = 0.3f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float ManaDevolvidaUltimate = 0.5f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float VelocidadeForaDeCombate = 0.08f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes|Numeros") float CuraExtraConsumiveis = 0.15f;

	// ---------------------------------------------------------------- Estado
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes")
	TArray<ENRMutacao> Escolhidas;

	/** Opções da escolha da vez (vazio = nenhuma escolha pendente). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes")
	TArray<ENRMutacao> Opcoes;

	/** Níveis cuja mutação ainda não foi escolhida, na ordem. O primeiro é o das Opcoes. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes")
	TArray<int32> NiveisPendentes;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Mutacoes")
	int32 TrocasRestantes = 1;

	UPROPERTY(BlueprintAssignable, Category = "Nexus|Mutacoes")
	FNRMutacaoEscolhida OnMutacaoEscolhida;

	/** Escolhe a opção Indice (0 a 2) da escolha da vez e aplica o efeito. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Mutacoes")
	bool Escolher(int32 Indice);

	/** Sorteia outras opções para a escolha da vez (gasta uma das TrocasRestantes). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Mutacoes")
	bool TrocarOpcoes();

	UFUNCTION(BlueprintPure, Category = "Nexus|Mutacoes")
	bool TemEscolhaPendente() const { return Opcoes.Num() > 0; }

	/** Nível da escolha da vez (0 se não houver). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Mutacoes")
	int32 NivelDaEscolha() const { return NiveisPendentes.Num() > 0 ? NiveisPendentes[0] : 0; }

	UFUNCTION(BlueprintPure, Category = "Nexus|Mutacoes")
	static FText Nome(ENRMutacao Mutacao);

	/** O efeito, com os números deste herói ("+50 de mana e +8% de poder mágico"). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Mutacoes")
	FText Descrever(ENRMutacao Mutacao) const;

	UFUNCTION(BlueprintPure, Category = "Nexus|Mutacoes")
	static ENRCategoriaMutacao Categoria(ENRMutacao Mutacao);

protected:
	virtual void BeginPlay() override;

private:
	UFUNCTION()
	void AoSubirNivel(int32 NovoNivel);

	/** Sorteia as Opcoes do primeiro nível pendente, sem repetir as de Evitar (se der). */
	void GerarOpcoes(const TArray<ENRMutacao>& Evitar);
	bool Disponivel(ENRMutacao Mutacao, int32 NivelOferta) const;
	float Peso(ENRMutacao Mutacao) const;
	/** Tira uma da Lista, com chance proporcional ao Peso. */
	ENRMutacao SortearDe(TArray<ENRMutacao>& Lista) const;
	void Aplicar(ENRMutacao Mutacao);
	UNRAbilitySystemComponent* GetASC() const;
	UNRCombateComponent* GetCombate() const;

	int32 UltimoNivel = 1;
};
