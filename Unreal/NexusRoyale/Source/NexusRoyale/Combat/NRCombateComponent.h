#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NRCombateComponent.generated.h"

class ANRProjetilMagico;
class UAnimationAsset;
class UInputAction;
class UMaterialInterface;
class UNRHudWidget;

/** Uma magia que dispara um projétil (GDD §4.1 e §6). Distâncias em cm, tempos em segundos. */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRMagiaProjetil
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FText Nome;
	/** Dano base; é multiplicado por (1 + Poder Mágico) de quem lança. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Dano = 60.f;
	/** 0 = acerta só o alvo. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float RaioExplosao = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Alcance = 3500.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Velocidade = 4000.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Custo = 0.f;
	/** Antes da Redução de Recarga. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Recarga = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FLinearColor Cor = FLinearColor(0.6f, 0.4f, 1.f);
	/** Diâmetro da esfera em voo, em metros. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Tamanho = 0.25f;
	/** Aceleração em cm/s² na direção do inimigo mais perto da mira (até ConeTeleguiado graus). 0 = reto. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Teleguiado = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float ConeTeleguiado = 12.f;
};

/**
 * Combate do herói no MVP (etapa 1 do GDD §15), sem Gameplay Abilities ainda:
 * - botão esquerdo: ataque básico do Feiticeiro (dardo arcano); Q: Bola de Fogo; 1-3: consumíveis;
 * - as teclas vêm de Input Actions do IMC_Default e são ligadas aqui, no InputComponent do herói;
 * - cria o HUD (UNRHudWidget) do jogador local;
 * - na morte: animação de morte em todas as malhas, sem movimento nem input, e a partida recomeça
 *   depois de TempoParaRecomecar segundos.
 */
UCLASS(ClassGroup = (Nexus), meta = (BlueprintSpawnableComponent, DisplayName = "Nexus Combate"))
class NEXUSROYALE_API UNRCombateComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNRCombateComponent();

	// ---------------------------------------------------------------- Magias
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	FNRMagiaProjetil AtaqueBasico;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	FNRMagiaProjetil MagiaPrincipal;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TSubclassOf<ANRProjetilMagico> ClasseProjetil;

	/** Material das esferas dos projéteis (parâmetro de vetor "Cor"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TObjectPtr<UMaterialInterface> MaterialProjetil;

	/** Tocada em todas as malhas do herói quando ele morre (segura o último quadro). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TObjectPtr<UAnimationAsset> AnimMorte;

	// ---------------------------------------------------------------- Input
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoAtaque;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoMagiaPrincipal;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoConsumivel1;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoConsumivel2;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoConsumivel3;

	// ---------------------------------------------------------------- Partida
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Partida")
	TSubclassOf<UNRHudWidget> ClasseHud;

	/** Segundos entre a morte e o recomeço do nível. 0 = não recomeça. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Partida")
	float TempoParaRecomecar = 6.f;

	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarAtaqueBasico();
	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarMagiaPrincipal();
	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarConsumivel(int32 Slot);

	/** Segundos até poder usar de novo: 0 = ataque básico, 1 = magia principal. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Combate")
	float RecargaRestante(int32 Slot) const;

	/** Segundos até o recomeço depois da morte (0 se não estiver morto). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Partida")
	float TempoAteRecomecar() const;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	bool Lancar(const FNRMagiaProjetil& Magia, double& ProximoUso);
	/** O pawn vivo mais perto da linha de mira, dentro do cone e do alcance (para o teleguiado). */
	USceneComponent* AlvoNaMira(const FVector& Origem, const FVector& Direcao, float Alcance, float ConeGraus) const;
	bool PodeAgir() const;
	void TentarLigarInput();
	void TentarCriarHud();
	void Recomecar();

	UFUNCTION()
	void AoMorrer(AActor* Assassino);

	void AoAtaque() { UsarAtaqueBasico(); }
	void AoMagiaPrincipal() { UsarMagiaPrincipal(); }
	void AoConsumivel1() { UsarConsumivel(0); }
	void AoConsumivel2() { UsarConsumivel(1); }
	void AoConsumivel3() { UsarConsumivel(2); }

	UPROPERTY(Transient)
	TObjectPtr<UNRHudWidget> Hud;

	double ProximoBasico = 0.0;
	double ProximoPrincipal = 0.0;
	bool bInputLigado = false;
	FTimerHandle TimerRecomecar;
};
