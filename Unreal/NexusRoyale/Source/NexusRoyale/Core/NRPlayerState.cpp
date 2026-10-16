#include "Core/NRPlayerState.h"

#include "Net/UnrealNetwork.h"

void ANRPlayerState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(ANRPlayerState, bVivo);
	DOREPLIFETIME(ANRPlayerState, Abates);
	DOREPLIFETIME(ANRPlayerState, Colocacao);
	DOREPLIFETIME(ANRPlayerState, Nivel);
	DOREPLIFETIME(ANRPlayerState, EliminadoPor);
	DOREPLIFETIME(ANRPlayerState, CausaDaEliminacao);
}

void ANRPlayerState::CopyProperties(APlayerState* PlayerState)
{
	Super::CopyProperties(PlayerState);
	// Nada da partida anterior passa para a próxima: cada partida começa do zero. Quando o lobby existir (M4),
	// "pronto" e as escolhas do draft passam por aqui.
}
