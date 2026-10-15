#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NREstruturaMagica.generated.h"

class UBoxComponent;
class UMaterialInstanceDynamic;
class UMaterialInterface;
class UStaticMeshComponent;

/**
 * Estrutura erguida por magia de campo (GDD §6.2; BP_SpellStructure_* no §16): hoje a Muralha de Gelo; depois,
 * pilar, domo e farol. É uma caixa com vida e duração que bloqueia passagem, projéteis e o dano em área.
 * - Recebe dano pelo ApplyDamage da Unreal (projéteis, meteoros). O dano de quem a ergueu não conta: ela bloqueia
 *   os tiros do dono, mas não se desfaz com eles (como as construções no Fortnite).
 * - Sobe do chão ao nascer e afunda ao se desfazer (vida zerada ou fim da duração).
 * - A malha usa custom depth com stencil 4 (magia), como os projéteis: fica fora do filtro de aquarela.
 */
UCLASS(Blueprintable)
class NEXUSROYALE_API ANREstruturaMagica : public AActor
{
	GENERATED_BODY()

public:
	ANREstruturaMagica();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Estrutura")
	TObjectPtr<UBoxComponent> Caixa;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Estrutura")
	TObjectPtr<UStaticMeshComponent> Malha;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Estrutura")
	float Vida = 400.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Estrutura")
	float VidaMax = 400.f;

	/**
	 * Monta a estrutura com o centro da base no chão (a posição do ator). Tamanho = espessura (X), largura (Y) e
	 * altura (Z) em cm. Material precisa de um parâmetro de vetor "Cor".
	 */
	UFUNCTION(BlueprintCallable, Category = "Nexus|Estrutura")
	void Erguer(const FVector& Tamanho, float NovaVida, float Duracao, const FLinearColor& Cor, UMaterialInterface* Material);

	/** Some na hora (com a animação de afundar). */
	UFUNCTION(BlueprintCallable, Category = "Nexus|Estrutura")
	void Desfazer();

	UFUNCTION(BlueprintPure, Category = "Nexus|Estrutura")
	float TempoRestante() const;

	UFUNCTION(BlueprintPure, Category = "Nexus|Estrutura")
	bool EstaDesfazendo() const { return bDesfazendo; }

	virtual float TakeDamage(float Dano, struct FDamageEvent const& Evento, AController* Instigador, AActor* Causador) override;

protected:
	virtual void Tick(float DeltaTime) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	void AtualizarCor();

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> MID;

	FLinearColor CorBase = FLinearColor::White;
	float Altura = 350.f;
	/** Segundos desde que começou a subir (ou a afundar, quando bDesfazendo). */
	float TempoAnim = 0.f;
	bool bDesfazendo = false;
	FTimerHandle TimerDuracao;
};
