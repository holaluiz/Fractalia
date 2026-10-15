#pragma once

#include "CoreMinimal.h"
#include "Combat/NRMagiaTypes.h"
#include "Components/ActorComponent.h"
#include "NRCombateComponent.generated.h"

class ANRChuvaMeteoros;
class ANREstruturaMagica;
class ANRProjetilMagico;
class UAnimationAsset;
class UInputAction;
class UMaterialInterface;
class UNRAbilitySystemComponent;
class UNRHudWidget;

/**
 * Combate do herói no MVP (etapa 1 do GDD §15), ainda sem Gameplay Abilities:
 * - botão esquerdo: ataque básico do Feiticeiro (dardo arcano); Q: Bola de Fogo; E: Muralha de Gelo;
 *   X: Chuva de Meteoros (ultimate, liberada no NivelUltimate); 1-3: consumíveis;
 * - as teclas vêm de Input Actions do IMC_Default e são ligadas aqui, no InputComponent do herói;
 * - cria o HUD (UNRHudWidget) do jogador local;
 * - na morte: animação de morte em todas as malhas, sem movimento nem input, e a partida recomeça
 *   depois de TempoParaRecomecar segundos.
 *
 * Por que ainda não é GA_* (GDD §16): o kit é fixo e a partida é solo, então GA não muda o comportamento e custaria
 * refazer custo, recarga e mira com tags e efeitos. A migração faz sentido na etapa 2, quando os grimórios trocarem
 * E e R na partida, as mutações mudarem as magias e entrar a rede (predição e replicação vêm prontas no GAS).
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

	/** Q (GDD §4.4): escolhida na montagem. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	FNRMagiaProjetil MagiaPrincipal;

	/** E (GDD §4.4). No MVP fica fixa com a Muralha de Gelo; quando os grimórios virarem magias, o slot passa a vir deles. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	FNRMagiaEstrutura Magia2;

	/** X (GDD §4.4 e §14): Chuva de Meteoros. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	FNRMagiaChuva Ultimate;

	/** Nível em que a ultimate é liberada (GDD §4.4: nível 6). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate", meta = (ClampMin = "1", ClampMax = "10"))
	int32 NivelUltimate = 6;

	/** Fração da mana da ultimate devolvida logo depois de lançar (mutação "a ultimate devolve 50% da mana gasta"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	float ManaDevolvidaUltimate = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TSubclassOf<ANRProjetilMagico> ClasseProjetil;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TSubclassOf<ANREstruturaMagica> ClasseEstrutura;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TSubclassOf<ANRChuvaMeteoros> ClasseChuva;

	/** Material das esferas dos projéteis, dos meteoros e do aviso no chão (parâmetro de vetor "Cor"). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TObjectPtr<UMaterialInterface> MaterialProjetil;

	/** Material das estruturas (parâmetro de vetor "Cor"). Vazio = usa o MaterialProjetil. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TObjectPtr<UMaterialInterface> MaterialEstrutura;

	/** Tocada em todas as malhas do herói quando ele morre (segura o último quadro). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Combate")
	TObjectPtr<UAnimationAsset> AnimMorte;

	// ---------------------------------------------------------------- Input
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoAtaque;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoMagiaPrincipal;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoMagia2;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoUltimate;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoConsumivel1;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoConsumivel2;
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoConsumivel3;
	/**
	 * Alt+4: troca as opções de mutação (GDD §7.4, 1 por partida). Com Alt apertado, as teclas 1-3 escolhem a mutação
	 * em vez de usar o consumível (se houver escolha pendente no UNRMutacoesComponent).
	 */
	UPROPERTY(EditAnywhere, Category = "Nexus|Input") TObjectPtr<UInputAction> AcaoTrocarMutacoes;

	// ---------------------------------------------------------------- Partida
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Partida")
	TSubclassOf<UNRHudWidget> ClasseHud;

	/** Segundos entre a morte e o recomeço do nível. 0 = não recomeça. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Partida")
	float TempoParaRecomecar = 6.f;

	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarAtaqueBasico();
	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarMagiaPrincipal();
	/** Ergue a Muralha de Gelo no chão sob a mira (até Magia2.Alcance). */
	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarMagia2();
	/** Chuva de Meteoros no chão sob a mira (até Ultimate.Alcance). Só a partir do NivelUltimate. */
	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarUltimate();
	UFUNCTION(BlueprintCallable, Category = "Nexus|Combate") bool UsarConsumivel(int32 Slot);

	/** Segundos até poder usar de novo: 0 = ataque básico, 1 = Q, 2 = E, 3 = ultimate (X). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Combate")
	float RecargaRestante(int32 Slot) const;

	UFUNCTION(BlueprintPure, Category = "Nexus|Combate")
	bool UltimateLiberada() const;

	/** Segundos até o recomeço depois da morte (0 se não estiver morto). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Partida")
	float TempoAteRecomecar() const;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	bool Lancar(const FNRMagiaProjetil& Magia, double& ProximoUso);
	/** Vivo, fora do dirigível, recarga cumprida e mana suficiente (não gasta nada). */
	bool Pronta(float Custo, double ProximoUso) const;
	/** Gasta a mana e começa a recarga (com a Redução de Recarga). */
	bool Pagar(float Custo, float Recarga, double& ProximoUso);
	/** Câmera do jogador (ou os olhos do pawn, sem controller). */
	void PontoDeVista(FVector& Olho, FRotator& Visao) const;
	/**
	 * Ponto do chão sob a mira, a no máximo Alcance e no mínimo DistanciaMinima do herói (no plano).
	 * Direcao = do herói até o ponto, no plano. Falha se não achar chão (água sem colisão, fora da ilha).
	 */
	bool PontoNoChao(float Alcance, float DistanciaMinima, FVector& Ponto, FVector& Normal, FVector& Direcao) const;
	/** O pawn vivo mais perto da linha de mira, dentro do cone e do alcance (para o teleguiado). */
	USceneComponent* AlvoNaMira(const FVector& Origem, const FVector& Direcao, float Alcance, float ConeGraus) const;
	UNRAbilitySystemComponent* ASCDoDono() const;
	bool PodeAgir() const;
	void TentarLigarInput();
	void TentarCriarHud();
	void Recomecar();

	UFUNCTION()
	void AoMorrer(AActor* Assassino);

	void AoAtaque() { UsarAtaqueBasico(); }
	void AoMagiaPrincipal() { UsarMagiaPrincipal(); }
	void AoMagia2() { UsarMagia2(); }
	void AoUltimate() { UsarUltimate(); }
	void AoConsumivel1() { UsarSlot(0); }
	void AoConsumivel2() { UsarSlot(1); }
	void AoConsumivel3() { UsarSlot(2); }
	void AoTrocarMutacoes();
	/** Tecla 1-3: com Alt e mutação pendente, escolhe a mutação; senão, usa o consumível. */
	void UsarSlot(int32 Slot);
	bool AltApertado() const;

	UPROPERTY(Transient)
	TObjectPtr<UNRHudWidget> Hud;

	double ProximoBasico = 0.0;
	double ProximoPrincipal = 0.0;
	double ProximoMagia2 = 0.0;
	double ProximoUltimate = 0.0;
	bool bInputLigado = false;
	FTimerHandle TimerRecomecar;
};
