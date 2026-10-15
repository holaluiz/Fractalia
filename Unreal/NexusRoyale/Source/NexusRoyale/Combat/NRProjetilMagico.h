#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NRProjetilMagico.generated.h"

class UMaterialInterface;
class UPointLightComponent;
class UProjectileMovementComponent;
class USphereComponent;
class UStaticMeshComponent;

/**
 * Projétil de magia (dardo arcano, Bola de Fogo). Voa em linha reta, ignora quem lançou e, ao tocar em algo:
 * - RaioExplosao = 0: ApplyDamage só no ator atingido;
 * - RaioExplosao > 0: ApplyRadialDamage com dano cheio no raio (GDD §6: "explode num raio de 3 m").
 * O dano usa o ApplyDamage da Unreal: os creeps recebem pelo EventAnyDamage e os heróis pelo
 * UNRAbilitySystemComponent (que escuta o OnTakeAnyDamage do dono).
 */
UCLASS(Blueprintable)
class NEXUSROYALE_API ANRProjetilMagico : public AActor
{
	GENERATED_BODY()

public:
	ANRProjetilMagico();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Projetil")
	TObjectPtr<USphereComponent> Esfera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Projetil")
	TObjectPtr<UStaticMeshComponent> Malha;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Projetil")
	TObjectPtr<UPointLightComponent> Luz;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Projetil")
	TObjectPtr<UProjectileMovementComponent> Movimento;

	/** Dano ao acertar (já multiplicado pelo Poder Mágico de quem lançou). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nexus|Projetil")
	float Dano = 60.f;

	/** Raio da explosão em cm. 0 = acerta só o alvo. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nexus|Projetil")
	float RaioExplosao = 0.f;

	/** Material da esfera; precisa de um parâmetro de vetor "Cor". */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nexus|Projetil")
	TObjectPtr<UMaterialInterface> Material;

	/**
	 * Lança na Direcao. Alcance em cm (some depois de voar essa distância). Escala = diâmetro em metros.
	 * Com Alvo e Teleguiado > 0, curva na direção do alvo com essa aceleração (cm/s²).
	 */
	void Lancar(const FVector& Direcao, float Velocidade, float Alcance, const FLinearColor& Cor, float Escala,
	            USceneComponent* Alvo = nullptr, float Teleguiado = 0.f);

protected:
	virtual void BeginPlay() override;

	UFUNCTION()
	void AoSobrepor(UPrimitiveComponent* Componente, AActor* Outro, UPrimitiveComponent* OutroComponente,
	                int32 Indice, bool bVarredura, const FHitResult& Hit);

	UFUNCTION()
	void AoParar(const FHitResult& Hit);

private:
	void Explodir(AActor* Alvo, const FVector& Ponto);

	FLinearColor CorAtual = FLinearColor::White;
	bool bExplodiu = false;
};
