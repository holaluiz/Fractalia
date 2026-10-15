#pragma once

#include "CoreMinimal.h"
#include "Combat/NRMagiaTypes.h"
#include "GameFramework/Actor.h"
#include "NRChuvaMeteoros.generated.h"

class UMaterialInstanceDynamic;
class UMaterialInterface;
class UPointLightComponent;
class UStaticMesh;
class UStaticMeshComponent;

/**
 * Chuva de Meteoros (GDD §6.4), no ponto do chão onde o ator nasce:
 * - aviso: um disco na cor da escola pisca durante Aviso segundos (telegrafia do GDD §9) enquanto os meteoros caem;
 * - cada meteoro explode no RaioMeteoro e aplica DanoMeteoro × multiplicador. Cada alvo sofre no máximo um meteoro
 *   na magia inteira. Vale para pawns e estruturas mágicas; quem lançou fica de fora;
 * - a partir do primeiro impacto o disco vira chão em chamas por DuracaoChamas: DanoChamasPorSegundo nos pawns dentro
 *   da área, em pulsos de 0,5 s.
 * O dano usa o ApplyDamage da Unreal, como os projéteis: os creeps recebem pelo EventAnyDamage e os heróis pelo ASC.
 * Malhas com custom depth stencil 4 (magia), fora do filtro de aquarela.
 */
UCLASS(Blueprintable)
class NEXUSROYALE_API ANRChuvaMeteoros : public AActor
{
	GENERATED_BODY()

public:
	ANRChuvaMeteoros();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Chuva")
	TObjectPtr<USceneComponent> Raiz;

	/** Aviso e, depois do primeiro impacto, o chão em chamas. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Chuva")
	TObjectPtr<UStaticMeshComponent> Disco;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Chuva")
	TObjectPtr<UPointLightComponent> Luz;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Chuva")
	TObjectPtr<UStaticMesh> MalhaMeteoro;

	/** Começa a magia. MultiplicadorDano = 1 + Poder Mágico de quem lançou. Material precisa do parâmetro de vetor "Cor". */
	void Iniciar(const FNRMagiaChuva& Config, float MultiplicadorDano, UMaterialInterface* Material);

	/**
	 * Só o chão em chamas, já queimando, sem aviso nem meteoros (a Bola de Fogo com a mutação de chamas).
	 * Usa a mesma queima da chuva: DanoPorSegundo × MultiplicadorDano em pulsos de 0,5 s, quem lançou fica de fora.
	 */
	void IniciarSoChamas(float Raio, float Duracao, float DanoPorSegundo, float MultiplicadorDano, const FLinearColor& Cor,
	                     UMaterialInterface* Material);

	/** Quantos alvos diferentes os meteoros já acertaram. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Chuva")
	int32 AlvosAtingidos() const { return Atingidos.Num(); }

protected:
	virtual void Tick(float DeltaTime) override;

private:
	/** Disco e luz do tamanho do Cfg.RaioArea, na cor do Cfg.Cor. */
	void PrepararDisco(UMaterialInterface* Material);
	float InstanteImpacto(int32 Indice) const;
	void Impacto(int32 Indice);
	void QueimarChao();

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> Meteoros;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> MIDDisco;

	FNRMagiaChuva Cfg;
	float Multiplicador = 1.f;
	float Tempo = 0.f;
	/** Em coordenadas do mundo, um por meteoro. */
	TArray<FVector> Impactos;
	TArray<FVector> Partidas;
	int32 ProximoImpacto = 0;
	float ProximaQueima = 0.f;
	bool bIniciada = false;
	/** Só para comparar identidade (nunca é desreferenciado): a magia dura poucos segundos. */
	TSet<const AActor*> Atingidos;
};
