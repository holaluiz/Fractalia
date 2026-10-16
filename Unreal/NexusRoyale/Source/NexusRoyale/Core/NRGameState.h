#pragma once

#include "CoreMinimal.h"
#include "Core/NRTiposPartida.h"
#include "GameFramework/GameStateBase.h"
#include "NRGameState.generated.h"

class ANRPlayerState;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNRFaseMudou, ENRFaseDaPartida, NovaFase);

/**
 * Estado da partida que todos os clientes enxergam (D-004). Quem decide é o ANRGameMode, só no servidor; aqui ficam
 * apenas os dados replicados e leituras para a UI.
 *
 * Os tempos são horários do servidor (GetServerWorldTimeSeconds), o mesmo relógio que o BP_StormController usa: o
 * cliente calcula "faltam N s" sozinho, sem o servidor mandar um contador a cada segundo.
 */
UCLASS()
class NEXUSROYALE_API ANRGameState : public AGameStateBase
{
	GENERATED_BODY()

public:
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

	UPROPERTY(ReplicatedUsing = OnRep_Fase, BlueprintReadOnly, Category = "Nexus|Partida")
	ENRFaseDaPartida Fase = ENRFaseDaPartida::Nenhuma;

	/** Horário do servidor em que a fase começou. */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	double InicioDaFase = 0.0;

	/** Horário do servidor em que a fase termina por tempo (0 = sem prazo, termina por condição). */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	double FimDaFase = 0.0;

	/** Jogadores (humanos e bots) quando a Espera terminou. */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	int32 JogadoresNoInicio = 0;

	/**
	 * Partida começou com 1 jogador (desenvolvimento): ela não acaba quando ele é "o último vivo"; acaba quando ele morre.
	 * Mantém o loop solo de antes do M1.
	 */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	bool bModoTreino = false;

	/** Definido na fase Final. Vazio = ninguém venceu (modo treino, ou os últimos morreram juntos). */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	TObjectPtr<ANRPlayerState> Vencedor;

	/** Avisa a UI local quando a fase muda (no servidor e nos clientes). */
	UPROPERTY(BlueprintAssignable, Category = "Nexus|Partida")
	FNRFaseMudou OnFaseMudou;

	/** Vivos, contados nos PlayerStates (nunca num contador solto: uma desconexão não deixa o número errado). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Partida")
	int32 ContarVivos() const;

	/** Segundos até o fim da fase (0 se a fase não tem prazo). */
	UFUNCTION(BlueprintPure, Category = "Nexus|Partida")
	float TempoRestanteDaFase() const;

	UFUNCTION(BlueprintPure, Category = "Nexus|Partida")
	static FText NomeDaFase(ENRFaseDaPartida UmaFase);

	/** Só o ANRGameMode chama (servidor). */
	void DefinirFase(ENRFaseDaPartida NovaFase, double Inicio, double Fim);

protected:
	UFUNCTION()
	void OnRep_Fase();
};
