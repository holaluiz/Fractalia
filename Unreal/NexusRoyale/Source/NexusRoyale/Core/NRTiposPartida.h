#pragma once

#include "CoreMinimal.h"
#include "NRTiposPartida.generated.h"

/**
 * Fases da partida (Docs/Game/GAMEPLAY_SYSTEMS.md, §1). Só o ANRGameMode (servidor) muda a fase; o ANRGameState
 * replica. A ordem do enum é a ordem da partida: dá para comparar com < e >.
 */
UENUM(BlueprintType)
enum class ENRFaseDaPartida : uint8
{
	Nenhuma,
	/** Ilha de Espera: jogadores entrando e carregando. */
	Espera,
	/** Draft de habilidades (M6). Até lá, a fase é pulada. */
	Draft,
	/** Dirigível: embarque, salto e queda. A tempestade já está correndo. */
	Queda,
	/** Partida: loot, PvE, PvP, tempestade. */
	EmJogo,
	/** Sobrou 1 vivo (ou, no modo treino, nenhum): combate congelado, vencedor anunciado. */
	Final,
	/** Tabela da partida; depois volta ao lobby (ou recomeça o mapa). */
	Resultados
};
