#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerState.h"
#include "NRPlayerState.generated.h"

/**
 * O que é "da partida" para cada jogador ou bot (D-005): continua existindo depois que o herói morre, e todos os
 * clientes recebem (placar, espectador, resultados). O AbilitySystemComponent continua no herói; o nível fica aqui só
 * como espelho para os outros jogadores (a fonte da verdade é o ASC, no servidor).
 *
 * Só o servidor escreve (ANRGameMode e o ASC do herói).
 */
UCLASS()
class NEXUSROYALE_API ANRPlayerState : public APlayerState
{
	GENERATED_BODY()

public:
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	/** Seamless travel (lobby -> partida -> lobby): o que precisa sobreviver à troca de mapa. */
	virtual void CopyProperties(APlayerState* PlayerState) override;

	/** Começa vivo; o GameMode marca a eliminação (uma vez só). */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	bool bVivo = true;

	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	int32 Abates = 0;

	/** 1 = vencedor. 0 = ainda na partida. Na eliminação, recebe o número de vivos antes da morte. */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	int32 Colocacao = 0;

	/** Espelho do nível do ASC do herói (placar e espectador). */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	int32 Nivel = 1;

	/** Quem deu o golpe final (vazio: tempestade, creep ou desconexão). */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	TObjectPtr<APlayerState> EliminadoPor;

	/** Nome de quem eliminou quando não foi um jogador ("Tempestade", "Imp"...). */
	UPROPERTY(Replicated, BlueprintReadOnly, Category = "Nexus|Partida")
	FString CausaDaEliminacao;
};
