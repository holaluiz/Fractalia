#include "Core/NRGameState.h"

#include "Core/NRPlayerState.h"
#include "Net/UnrealNetwork.h"
#include "NexusRoyale.h"

void ANRGameState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(ANRGameState, Fase);
	DOREPLIFETIME(ANRGameState, InicioDaFase);
	DOREPLIFETIME(ANRGameState, FimDaFase);
	DOREPLIFETIME(ANRGameState, JogadoresNoInicio);
	DOREPLIFETIME(ANRGameState, bModoTreino);
	DOREPLIFETIME(ANRGameState, Vencedor);
}

int32 ANRGameState::ContarVivos() const
{
	int32 Vivos = 0;
	for (const APlayerState* PS : PlayerArray)
	{
		const ANRPlayerState* NRPS = Cast<ANRPlayerState>(PS);
		if (NRPS && NRPS->bVivo && !NRPS->IsInactive())
		{
			++Vivos;
		}
	}
	return Vivos;
}

float ANRGameState::TempoRestanteDaFase() const
{
	return FimDaFase > 0.0 ? FMath::Max(0.f, static_cast<float>(FimDaFase - GetServerWorldTimeSeconds())) : 0.f;
}

FText ANRGameState::NomeDaFase(ENRFaseDaPartida UmaFase)
{
	switch (UmaFase)
	{
	case ENRFaseDaPartida::Espera: return NSLOCTEXT("Nexus", "FaseEspera", "Espera");
	case ENRFaseDaPartida::Draft: return NSLOCTEXT("Nexus", "FaseDraft", "Draft");
	case ENRFaseDaPartida::Queda: return NSLOCTEXT("Nexus", "FaseQueda", "Queda");
	case ENRFaseDaPartida::EmJogo: return NSLOCTEXT("Nexus", "FaseEmJogo", "Partida");
	case ENRFaseDaPartida::Final: return NSLOCTEXT("Nexus", "FaseFinal", "Final");
	case ENRFaseDaPartida::Resultados: return NSLOCTEXT("Nexus", "FaseResultados", "Resultados");
	default: return FText::GetEmpty();
	}
}

void ANRGameState::DefinirFase(ENRFaseDaPartida NovaFase, double Inicio, double Fim)
{
	InicioDaFase = Inicio;
	FimDaFase = Fim;
	Fase = NovaFase;
	// No servidor o OnRep não roda sozinho; chama aqui para a UI do host reagir igual à dos clientes.
	OnRep_Fase();
}

void ANRGameState::OnRep_Fase()
{
	if (!HasAuthority())
	{
		// O servidor já registra a troca (ANRGameMode::MudarFase); no cliente, a linha prova que a fase chegou.
		UE_LOG(LogNexus, Log, TEXT("Partida (cliente): fase %s"), *NomeDaFase(Fase).ToString());
	}
	OnFaseMudou.Broadcast(Fase);
}
