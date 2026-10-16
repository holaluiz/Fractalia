#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NRSessaoSubsystem.generated.h"

/**
 * A "sala" do jogo, que sobrevive à troca de mapa (vive no GameInstance). No M3 é aqui que entram hospedar, procurar,
 * entrar e sair (D-010: a UI e o gameplay falam com este subsistema, nunca com a Steam ou a EOS direto).
 *
 * Por enquanto (M1) guarda só quantos jogadores humanos a próxima partida deve esperar na fase Espera. Sem isso, num
 * recomeço com clientes conectados a Espera fechava antes de eles terminarem de carregar o mapa (testado em 15/10: o
 * cliente leva ~9 s), e a partida começava como "treino" com eles chegando atrasados.
 */
UCLASS()
class NEXUSROYALE_API UNRSessaoSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	/** Lê e zera: cada valor vale para uma partida só. Só faz sentido no servidor. */
	int32 ConsumirJogadoresEsperados()
	{
		const int32 Valor = JogadoresEsperados;
		JogadoresEsperados = 0;
		return Valor;
	}

	void DefinirJogadoresEsperados(int32 Quantos) { JogadoresEsperados = FMath::Max(0, Quantos); }

private:
	int32 JogadoresEsperados = 0;
};
