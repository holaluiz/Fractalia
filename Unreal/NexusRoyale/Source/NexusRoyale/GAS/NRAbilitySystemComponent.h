#pragma once

#include "CoreMinimal.h"
#include "AbilitySystemComponent.h"
#include "NRAbilitySystemComponent.generated.h"

class UAS_Hero;

/** Valores base do arquétipo (GDD §4.1). */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRArquetipoBase
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arquetipo")
	FText Nome = NSLOCTEXT("Nexus", "Feiticeiro", "Feiticeiro");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arquetipo")
	float Vida = 400.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arquetipo")
	float Mana = 260.f;

	/** Velocidade de corrida em m/s. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arquetipo")
	float Velocidade = 6.f;
};

/** Pontos INVESTIDOS na montagem (GDD §4.2): 20 no total, no máximo 10 por atributo. */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRPontosBuild
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0", ClampMax = "10"))
	int32 Forca = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0", ClampMax = "10"))
	int32 Agilidade = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0", ClampMax = "10"))
	int32 Vitalidade = 4;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0", ClampMax = "10"))
	int32 Intelecto = 8;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build", meta = (ClampMin = "0", ClampMax = "10"))
	int32 Espirito = 6;
};

/** Bônus somados aos atributos por um item ou efeito. Frações: 0,04 = +4%. */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRBonus
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float VidaMax = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float ManaMax = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float Armadura = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float DanoFisico = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float PoderMagico = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float VelocMov = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float VelocAtaque = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float ReducaoRecarga = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float RegenMana = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float RegenVida = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonus") float BonusCura = 0.f;

	FNRBonus& operator*=(float Fator);
	FNRBonus& operator+=(const FNRBonus& Outro);
	bool IsZero() const;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNRBarraMudou, float, Atual, float, Maximo);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNRDanoRecebido, float, Dano, AActor*, Instigador);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNRMorreu, AActor*, Assassino);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNRSubiuNivel, int32, NovoNivel);

class UDamageType;

/**
 * AbilitySystemComponent do herói. Fica no próprio BP_HeroBase (no battle royale não há respawn,
 * então não precisa morar no PlayerState).
 *
 * - Cria o AS_Hero e calcula os atributos a partir de arquétipo + build + nível (InicializarHeroi).
 *   Os coeficientes por ponto são do GDD §4.2, §5 e §7.1 e podem ser ajustados no painel Details.
 * - Regenera vida e mana (RegenMana em combate; RegenManaForaDeCombate fora dele).
 * - Expõe ao Blueprint: AplicarDano, AplicarDanoTempestade, Curar, RestaurarMana, AplicarBonus.
 * - Avisa o Blueprint por eventos: OnVidaMudou, OnManaMudou, OnDanoRecebido, OnMorreu.
 */
UCLASS(ClassGroup = (Nexus), meta = (BlueprintSpawnableComponent, DisplayName = "Nexus Ability System"))
class NEXUSROYALE_API UNRAbilitySystemComponent : public UAbilitySystemComponent
{
	GENERATED_BODY()

public:
	UNRAbilitySystemComponent();

	virtual void InitializeComponent() override;
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	// ---------------------------------------------------------------- Herói
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	FNRArquetipoBase Arquetipo;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	FNRPontosBuild Build;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	int32 Nivel = 1;

	/** Se ligado, o BeginPlay chama InicializarHeroi com o Arquetipo e a Build acima (só no servidor). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	bool bInicializarNoBeginPlay = true;

	/** Recalcula todos os atributos. Na primeira vez, enche vida e mana. Só no servidor. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	void InicializarHeroi(const FNRArquetipoBase& NovoArquetipo, const FNRPontosBuild& NovaBuild, int32 NovoNivel = 1);

	/** Muda o nível (1 a 10) e recalcula; vida e mana mantêm a porcentagem. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	void DefinirNivel(int32 NovoNivel);

	/** XP acumulado na partida. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	int32 XP = 0;

	/** Soma XP e sobe quantos níveis o XP acumulado permitir (GDD §7.1). Só no servidor. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	void GanharXP(int32 Quantidade);

	/** XP de quem deu o golpe final (controller ou pawn). Os creeps chamam no Die. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	static void DarXP(AActor* QuemMatou, int32 Quantidade);

	/** Progresso dentro do nível atual, para a barra do HUD. No nível 10, ParaProximo = 0. */
	UFUNCTION(BlueprintPure, Category = "Nexus|Heroi")
	void ProgressoXP(int32& NoNivel, int32& ParaProximo) const;

	/** Sobe até o Piso (o XP vai junto, para a barra não andar para trás). Abaixo do piso não faz nada. Só no servidor. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	void SubirAteNivel(int32 Piso);

	/**
	 * Piso de nível do fim de fase da tempestade (GDD §7.3): todo herói vivo abaixo do Piso sobe até ele.
	 * O BP_StormController chama no CheckPhaseEvents, com o LevelFloor do CT_Storm.
	 */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi", meta = (WorldContext = "WorldContextObject"))
	static void AplicarPisoDeNivel(const UObject* WorldContextObject, int32 Piso);

	/**
	 * Pontos efetivos somados por fora da build (mutações de atributo, GDD §7.4: "+2 pontos efetivos").
	 * Índice 0 Força, 1 Agilidade, 2 Vitalidade, 3 Intelecto, 4 Espírito. Recalcula na hora.
	 */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	void AdicionarPontosEfetivos(int32 Indice, float Pontos);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	TArray<float> PontosEfetivosExtras;

	/** Bônus de velocidade só fora de combate (mutação "+8% de velocidade fora de combate"). Fração. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Nexus|Heroi")
	float BonusVelocForaDeCombate = 0.f;

	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Heroi")
	void SomarBonusVelocForaDeCombate(float Bonus);

	/** Pontos investidos -> pontos efetivos: 1-5 valem 1,0; 6-8 valem 0,6; 9-10 valem 0,3 (GDD §4.2). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Heroi")
	static float PontosEfetivos(int32 PontosInvestidos);

	// ---------------------------------------------------------------- Efeitos
	/** Dano normal (passa pela armadura). bDeJogador marca os dois lados como "em combate" (GDD §5). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	void AplicarDano(float Quantidade, AActor* Instigador, bool bDeJogador = false, bool bIgnorarArmadura = false);

	/** Tempestade: porcentagem da vida máxima, ignorando a armadura (GDD §13). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	void AplicarDanoTempestade(float PorcentagemDaVidaMax);

	/** Gasta mana na hora (custo de magia). Sem mana suficiente, não gasta nada e devolve false. */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	bool GastarMana(float Custo);

	/** Se ligado, todo ApplyDamage da Unreal no dono (creeps, projéteis) vira AplicarDano. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Efeitos")
	bool bReceberDanoDaUnreal = true;

	/** Cura Quantidade ao longo de Duracao segundos (0 = na hora). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	void Curar(float Quantidade, float Duracao = 0.f);

	/** Restaura Quantidade de mana ao longo de Duracao segundos (0 = na hora). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	void RestaurarMana(float Quantidade, float Duracao = 0.f);

	/** Soma um bônus aos atributos. Duracao <= 0 = até ser removido (itens). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	FActiveGameplayEffectHandle AplicarBonus(const FNRBonus& Bonus, float Duracao = 0.f);

	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Efeitos")
	void RemoverBonus(FActiveGameplayEffectHandle Efeito);

	// ---------------------------------------------------------------- Leitura
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") float GetVida() const;
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") float GetVidaMax() const;
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") float GetMana() const;
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") float GetManaMax() const;
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") float GetArmadura() const;
	/** Pontos efetivos atuais de um atributo da build (0 Força, 1 Agilidade, 2 Vitalidade, 3 Intelecto, 4 Espírito). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") float GetPontosEfetivos(int32 Indice) const;
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") bool IsMorto() const { return bMorto; }
	/** Causou ou recebeu dano de jogador nos últimos TempoEmCombate segundos (GDD §5). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Atributos") bool IsEmCombate() const;

	// ---------------------------------------------------------------- Eventos
	UPROPERTY(BlueprintAssignable, Category = "Nexus|Eventos") FNRBarraMudou OnVidaMudou;
	UPROPERTY(BlueprintAssignable, Category = "Nexus|Eventos") FNRBarraMudou OnManaMudou;
	UPROPERTY(BlueprintAssignable, Category = "Nexus|Eventos") FNRDanoRecebido OnDanoRecebido;
	UPROPERTY(BlueprintAssignable, Category = "Nexus|Eventos") FNRMorreu OnMorreu;
	UPROPERTY(BlueprintAssignable, Category = "Nexus|Eventos") FNRSubiuNivel OnSubiuNivel;

	/** Chamado pelo AS_Hero depois de descontar a vida (servidor). */
	void NotificarDano(float DanoFinal, AActor* Instigador, bool bMatou);
	/** Marca combate agora (quem causa dano a um jogador também entra em combate). */
	void MarcarCombate();

	// ---------------------------------------------------------------- Balanceamento (GDD)
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float VidaPorVitalidade = 30.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float RegenVidaPorVitalidade = 0.4f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float ManaPorIntelecto = 25.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float PoderMagicoPorIntelecto = 0.04f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float DanoFisicoPorForca = 0.04f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float VelocAtaquePorAgilidade = 0.03f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float VelocMovPorAgilidade = 0.015f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float RegenManaPorEspirito = 0.5f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float ReducaoRecargaPorEspirito = 0.025f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float CuraPorEspirito = 0.04f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float VidaPorNivel = 80.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float ManaPorNivel = 20.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float DanoPorNivel = 0.06f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float RegenManaEmCombate = 2.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float RegenManaForaDeCombate = 8.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float TempoEmCombate = 5.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento") float IntervaloRegen = 0.25f;
	/** XP acumulado para chegar aos níveis 2 a 10 (GDD §7.1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Nexus|Balanceamento")
	TArray<int32> XPAcumuladoPorNivel = { 100, 250, 450, 710, 1040, 1450, 1950, 2550, 3270 };

private:
	UFUNCTION()
	void AoDanoDaUnreal(AActor* Atingido, float Dano, const UDamageType* Tipo, AController* Instigador, AActor* Causador);

	void TickRegen();
	void AtualizarVelocidade();
	void SetBase(const FGameplayAttribute& Atributo, float Valor);
	FGameplayEffectSpecHandle CriarSpec(TSubclassOf<UGameplayEffect> Classe, AActor* Instigador) const;
	void AplicarContinuo(TSubclassOf<UGameplayEffect> Instantaneo, TSubclassOf<UGameplayEffect> Continuo, FName Nome,
	                     float Quantidade, float Duracao);

	void OnVidaAtributo(const FOnAttributeChangeData& Dados);
	void OnManaAtributo(const FOnAttributeChangeData& Dados);
	void OnVelocAtributo(const FOnAttributeChangeData& Dados);

	float PontosExtras(int32 Indice) const;

	FTimerHandle TimerRegen;
	double UltimoCombate = -1000.0;
	bool bMorto = false;
	bool bInicializado = false;
	/** Para refazer a velocidade quando o herói entra ou sai de combate. */
	bool bEmCombateAntes = false;
};
