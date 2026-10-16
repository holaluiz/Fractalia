#pragma once

#include "CoreMinimal.h"
#include "Core/NRTiposPartida.h"
#include "GameFramework/GameModeBase.h"
#include "NRGameMode.generated.h"

class ANRGameState;
class ANRPlayerState;
class UNRAbilitySystemComponent;

/**
 * Máquina de estados da partida (D-004; Docs/Game/GAMEPLAY_SYSTEMS.md §1). Existe só no servidor: é aqui que se decide
 * fase, eliminação, abate e vitória. Os clientes enxergam o resultado pelo ANRGameState e pelos ANRPlayerState.
 *
 * Por que AGameModeBase e não AGameMode: o MatchState do AGameMode é feito para partidas por rodada (spawn atrasado,
 * ReadyToStartMatch, reinício) e brigaria com as fases do battle royale. Um enum próprio com prazos no relógio do
 * servidor é mais simples de testar e é o mesmo padrão que já funciona na tempestade.
 *
 * Nada de regra fica no Blueprint filho (GM_NexusRoyale): ele só implementa IniciarQueda (dirigível + tempestade).
 * Num servidor dedicado (D-003) este código roda igual; o host do listen server não é tratado de forma especial.
 */
UCLASS()
class NEXUSROYALE_API ANRGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ANRGameMode();

	// ---------------------------------------------------------------- Tempos das fases (s)
	/** A Espera dura pelo menos isto, para os jogadores nascerem e a replicação inicial chegar. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float TempoMinimoDeEspera = 3.f;

	/** Depois disto a partida começa mesmo com alguém ainda carregando (D-006). */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float TempoMaximoDeEspera = 60.f;

	/**
	 * Humanos que a Espera aguarda (além do tempo mínimo). 0 = só quem já está conectado. Num recomeço com clientes, o
	 * GameMode anterior deixa o número no UNRSessaoSubsystem; no M4 é o lobby que diz quantos vêm.
	 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	int32 JogadoresEsperados = 0;

	/** Até o draft existir (M6), a fase Draft é pulada. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	bool bPularDraft = true;

	/** A Queda termina quando ninguém mais está no dirigível, mas nunca antes disto. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float TempoMinimoDeQueda = 2.f;

	/** Rede de segurança: depois disto a partida começa mesmo com alguém no dirigível. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float TempoMaximoDeQueda = 150.f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float DuracaoFinal = 5.f;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float DuracaoResultados = 15.f;

	/** Segundos entre a morte e a câmera ir para quem matou. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Partida")
	float AtrasoCameraNoAssassino = 2.f;

	// ---------------------------------------------------------------- XP de abate (Docs/Game/BALANCE.md §4)
	// XP = max(Minimo, PorNivel × NívelVítima) × clamp(1 + FatorPorNivel × (NívelVítima − NívelAssassino), Min, Max).
	// Os valores padrão reproduzem o GDD v2 §7.2 (só bônus, nunca redução). A redução proposta (FatorMinimo 0,4,
	// FatorMaximo 2,0) espera a decisão D-002m do usuário.
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Balanceamento") int32 XPAbateMinimo = 100;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Balanceamento") int32 XPAbatePorNivel = 80;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Balanceamento") float XPAbateFatorPorNivel = 0.2f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Balanceamento") float XPAbateFatorMinimo = 1.f;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Nexus|Balanceamento") float XPAbateFatorMaximo = 10.f;

	UFUNCTION(BlueprintPure, Category = "Nexus|Balanceamento")
	int32 XPDeAbate(int32 NivelVitima, int32 NivelAssassino) const;

	// ---------------------------------------------------------------- Ganchos do Blueprint
	/** Entrada na fase Queda: o GM_NexusRoyale cria o dirigível, embarca os heróis e liga a tempestade. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Nexus|Partida")
	void IniciarQueda();

	// ---------------------------------------------------------------- Regras (servidor)
	/**
	 * Tira um jogador da partida (morte ou desconexão). Uma vez só por jogador; ignorado fora da Queda e do EmJogo.
	 * Assassino pode ser um herói, um creep, um projétil ou vazio (tempestade).
	 */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Partida")
	void EliminarJogador(ANRPlayerState* Vitima, AActor* Assassino);

	/**
	 * Desenvolvimento: cria um bot que ocupa uma vaga (PlayerState próprio, mesmo herói) e entra pelo PlayerStart.
	 * Aceito até a primeira eliminação; recalcula o modo treino. No M4 o lobby passa a criar os bots.
	 */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Desenvolvimento")
	APawn* AdicionarBotDeTeste();

	/** Desenvolvimento: durante a Espera, passa a aguardar Quantos humanos (teste de rede antes do lobby do M4). */
	UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "Nexus|Desenvolvimento")
	void EsperarJogadores(int32 Quantos);

	UFUNCTION(BlueprintPure, Category = "Nexus|Partida")
	ENRFaseDaPartida GetFase() const;

protected:
	virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	/** Quem entra com a partida já em andamento (Queda em diante) não ganha herói: assiste (GAMEPLAY_SYSTEMS.md §2). */
	virtual void HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer) override;
	/** Todo herói que nasce (humano ou bot) passa por aqui: é onde o GameMode passa a ouvir a morte dele. */
	virtual void SetPlayerDefaults(APawn* PlayerPawn) override;
	virtual void Logout(AController* Exiting) override;

private:
	/** Roda a cada 0,25 s no servidor e decide se a fase atual terminou. */
	void AvaliarFase();
	/** Única porta de troca de fase: registra no log e (M14) na telemetria. */
	void MudarFase(ENRFaseDaPartida NovaFase, float Duracao = 0.f);
	void AoHeroiMorrer(UNRAbilitySystemComponent* ASC, AActor* Assassino);
	/** EliminarJogador com a causa escrita por quem chama ("Desconectou"); vazia = descobre pelo assassino. */
	void EliminarComCausa(ANRPlayerState* Vitima, AActor* Assassino, const FString& Causa);
	void ConferirVitoria();
	void CongelarCombate();
	void FecharEspera();
	void TerminarPartida();
	/** Algum herói vivo ainda está no dirigível (o BP_HeroBase fica escondido enquanto está a bordo). */
	bool AlguemNoDirigivel() const;
	void MostrarAssassino(TWeakObjectPtr<APlayerController> VitimaPC, TWeakObjectPtr<AActor> Alvo);
	ANRGameState* GetNRGameState() const;
	double Agora() const;

	FTimerHandle TimerAvaliar;
	bool bAlguemEliminado = false;
	int32 BotsCriados = 0;
};
