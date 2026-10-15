#include "Progression/NRMutacoesComponent.h"

#include "Combat/NRCombateComponent.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "NexusRoyale.h"

namespace
{
	FText Pct(float Fracao)
	{
		return FText::AsNumber(FMath::RoundToInt(Fracao * 100.f));
	}

	FText Num(float Valor)
	{
		FNumberFormattingOptions Opcoes;
		Opcoes.MaximumFractionalDigits = 1;
		return FText::AsNumber(Valor, &Opcoes);
	}
}

UNRMutacoesComponent::UNRMutacoesComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	NiveisUltimate = { 8, 10 };
}

void UNRMutacoesComponent::BeginPlay()
{
	Super::BeginPlay();
	TrocasRestantes = TrocasPorPartida;
	if (UNRAbilitySystemComponent* ASC = GetASC())
	{
		UltimoNivel = ASC->Nivel;
		ASC->OnSubiuNivel.AddDynamic(this, &ThisClass::AoSubirNivel);
	}
}

UNRAbilitySystemComponent* UNRMutacoesComponent::GetASC() const
{
	return GetOwner() ? GetOwner()->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr;
}

UNRCombateComponent* UNRMutacoesComponent::GetCombate() const
{
	return GetOwner() ? GetOwner()->FindComponentByClass<UNRCombateComponent>() : nullptr;
}

// ------------------------------------------------------------------------------------------------ Textos

ENRCategoriaMutacao UNRMutacoesComponent::Categoria(ENRMutacao Mutacao)
{
	switch (Mutacao)
	{
	case ENRMutacao::Forca:
	case ENRMutacao::Agilidade:
	case ENRMutacao::Vitalidade:
	case ENRMutacao::Intelecto:
	case ENRMutacao::Espirito:
		return ENRCategoriaMutacao::Atributo;
	case ENRMutacao::BolaDeFogoChamas:
	case ENRMutacao::MuralhaLarga:
		return ENRCategoriaMutacao::Magia;
	case ENRMutacao::UltimateRecarga:
	case ENRMutacao::UltimateArea:
	case ENRMutacao::UltimateMana:
		return ENRCategoriaMutacao::Ultimate;
	default:
		return ENRCategoriaMutacao::Geral;
	}
}

FText UNRMutacoesComponent::Nome(ENRMutacao Mutacao)
{
	switch (Mutacao)
	{
	case ENRMutacao::Forca: return NSLOCTEXT("Nexus", "MutForca", "Força");
	case ENRMutacao::Agilidade: return NSLOCTEXT("Nexus", "MutAgilidade", "Agilidade");
	case ENRMutacao::Vitalidade: return NSLOCTEXT("Nexus", "MutVitalidade", "Vitalidade");
	case ENRMutacao::Intelecto: return NSLOCTEXT("Nexus", "MutIntelecto", "Intelecto");
	case ENRMutacao::Espirito: return NSLOCTEXT("Nexus", "MutEspirito", "Espírito");
	case ENRMutacao::BolaDeFogoChamas: return NSLOCTEXT("Nexus", "MutBolaChamas", "Bola de Fogo: rastro de chamas");
	case ENRMutacao::MuralhaLarga: return NSLOCTEXT("Nexus", "MutMuralhaLarga", "Muralha de Gelo: muralha larga");
	case ENRMutacao::UltimateRecarga: return NSLOCTEXT("Nexus", "MutUltRecarga", "Ultimate: recarga curta");
	case ENRMutacao::UltimateArea: return NSLOCTEXT("Nexus", "MutUltArea", "Ultimate: área maior");
	case ENRMutacao::UltimateMana: return NSLOCTEXT("Nexus", "MutUltMana", "Ultimate: mana de volta");
	case ENRMutacao::VelocidadeForaDeCombate: return NSLOCTEXT("Nexus", "MutVelocidade", "Passos leves");
	case ENRMutacao::CuraConsumiveis: return NSLOCTEXT("Nexus", "MutCura", "Cura reforçada");
	default: return FText::GetEmpty();
	}
}

FText UNRMutacoesComponent::Descrever(ENRMutacao Mutacao) const
{
	const UNRAbilitySystemComponent* ASC = GetASC();
	const UNRCombateComponent* Combate = GetCombate();
	const float P = PontosPorAtributo;
	switch (Mutacao)
	{
	case ENRMutacao::Forca:
		return FText::Format(NSLOCTEXT("Nexus", "DescForca", "+{0} pontos: +{1}% de dano físico"),
			Num(P), Pct(ASC ? ASC->DanoFisicoPorForca * P : 0.f));
	case ENRMutacao::Agilidade:
		return FText::Format(NSLOCTEXT("Nexus", "DescAgilidade", "+{0} pontos: +{1}% de velocidade de ataque e +{2}% de velocidade"),
			Num(P), Pct(ASC ? ASC->VelocAtaquePorAgilidade * P : 0.f), Pct(ASC ? ASC->VelocMovPorAgilidade * P : 0.f));
	case ENRMutacao::Vitalidade:
		return FText::Format(NSLOCTEXT("Nexus", "DescVitalidade", "+{0} pontos: +{1} de vida e +{2} de vida/s"),
			Num(P), Num(ASC ? ASC->VidaPorVitalidade * P : 0.f), Num(ASC ? ASC->RegenVidaPorVitalidade * P : 0.f));
	case ENRMutacao::Intelecto:
		return FText::Format(NSLOCTEXT("Nexus", "DescIntelecto", "+{0} pontos: +{1} de mana e +{2}% de poder mágico"),
			Num(P), Num(ASC ? ASC->ManaPorIntelecto * P : 0.f), Pct(ASC ? ASC->PoderMagicoPorIntelecto * P : 0.f));
	case ENRMutacao::Espirito:
		return FText::Format(NSLOCTEXT("Nexus", "DescEspirito", "+{0} pontos: +{1} de mana/s, −{2}% de recarga e +{3}% de cura"),
			Num(P), Num(ASC ? ASC->RegenManaPorEspirito * P : 0.f), Pct(ASC ? ASC->ReducaoRecargaPorEspirito * P : 0.f),
			Pct(ASC ? ASC->CuraPorEspirito * P : 0.f));
	case ENRMutacao::BolaDeFogoChamas:
		return FText::Format(NSLOCTEXT("Nexus", "DescBolaChamas", "deixa o chão em chamas por {0} s ({1} de dano/s)"),
			Num(DuracaoChamasBolaDeFogo), Num(Combate ? Combate->MagiaPrincipal.DanoChamasPorSegundo : 0.f));
	case ENRMutacao::MuralhaLarga:
		return FText::Format(NSLOCTEXT("Nexus", "DescMuralhaLarga", "+{0}% de largura ({1} m → {2} m)"),
			Pct(LarguraExtraMuralha), Num(Combate ? Combate->Magia2.Tamanho.Y / 100.f : 0.f),
			Num(Combate ? Combate->Magia2.Tamanho.Y * (1.f + LarguraExtraMuralha) / 100.f : 0.f));
	case ENRMutacao::UltimateRecarga:
		return FText::Format(NSLOCTEXT("Nexus", "DescUltRecarga", "−{0}% de recarga da ultimate"), Pct(ReducaoRecargaUltimate));
	case ENRMutacao::UltimateArea:
		return FText::Format(NSLOCTEXT("Nexus", "DescUltArea", "+{0}% de área da ultimate"), Pct(AreaExtraUltimate));
	case ENRMutacao::UltimateMana:
		return FText::Format(NSLOCTEXT("Nexus", "DescUltMana", "a ultimate devolve {0}% da mana gasta"), Pct(ManaDevolvidaUltimate));
	case ENRMutacao::VelocidadeForaDeCombate:
		return FText::Format(NSLOCTEXT("Nexus", "DescVelocidade", "+{0}% de velocidade fora de combate"), Pct(VelocidadeForaDeCombate));
	case ENRMutacao::CuraConsumiveis:
		return FText::Format(NSLOCTEXT("Nexus", "DescCura", "+{0}% de cura de consumíveis"), Pct(CuraExtraConsumiveis));
	default:
		return FText::GetEmpty();
	}
}

// ------------------------------------------------------------------------------------------------ Sorteio

bool UNRMutacoesComponent::Disponivel(ENRMutacao Mutacao, int32 NivelOferta) const
{
	if (Mutacao == ENRMutacao::Nenhuma || Mutacao == ENRMutacao::Total)
	{
		return false;
	}
	const ENRCategoriaMutacao Cat = Categoria(Mutacao);
	if (Cat == ENRCategoriaMutacao::Atributo)
	{
		return GetASC() != nullptr; // atributos podem repetir
	}
	if (Escolhidas.Contains(Mutacao))
	{
		return false;
	}
	switch (Cat)
	{
	case ENRCategoriaMutacao::Magia:
		return GetCombate() != nullptr;
	case ENRCategoriaMutacao::Ultimate:
		return GetCombate() != nullptr && NiveisUltimate.Contains(NivelOferta);
	default:
		return GetASC() != nullptr;
	}
}

float UNRMutacoesComponent::Peso(ENRMutacao Mutacao) const
{
	switch (Categoria(Mutacao))
	{
	case ENRCategoriaMutacao::Atributo:
	{
		// "Peso para combinar com a sua build": quem investiu 8 pontos vê o atributo 3× mais que um sem pontos.
		const UNRAbilitySystemComponent* ASC = GetASC();
		int32 Investidos = 0;
		if (ASC)
		{
			const FNRPontosBuild& B = ASC->Build;
			const int32 Pontos[5] = { B.Forca, B.Agilidade, B.Vitalidade, B.Intelecto, B.Espirito };
			Investidos = Pontos[static_cast<int32>(Mutacao) - static_cast<int32>(ENRMutacao::Forca)];
		}
		return 1.f + Investidos / 4.f;
	}
	case ENRCategoriaMutacao::Magia: return 2.5f;
	case ENRCategoriaMutacao::Ultimate: return 2.f;
	default: return 1.5f;
	}
}

ENRMutacao UNRMutacoesComponent::SortearDe(TArray<ENRMutacao>& Lista) const
{
	float Total = 0.f;
	for (ENRMutacao M : Lista)
	{
		Total += Peso(M);
	}
	float Sorteio = FMath::FRandRange(0.f, Total);
	for (int32 i = 0; i < Lista.Num(); ++i)
	{
		Sorteio -= Peso(Lista[i]);
		if (Sorteio <= 0.f)
		{
			const ENRMutacao M = Lista[i];
			Lista.RemoveAt(i);
			return M;
		}
	}
	return Lista.Pop();
}

void UNRMutacoesComponent::GerarOpcoes(const TArray<ENRMutacao>& Evitar)
{
	Opcoes.Reset();
	const int32 Nivel = NivelDaEscolha();
	if (Nivel <= 0)
	{
		return;
	}
	TArray<ENRMutacao> Candidatas, Reserva;
	for (uint8 i = 1; i < static_cast<uint8>(ENRMutacao::Total); ++i)
	{
		const ENRMutacao M = static_cast<ENRMutacao>(i);
		if (Disponivel(M, Nivel))
		{
			(Evitar.Contains(M) ? Reserva : Candidatas).Add(M);
		}
	}
	auto EhUltimate = [](ENRMutacao M) { return Categoria(M) == ENRCategoriaMutacao::Ultimate; };
	if (NiveisUltimate.Contains(Nivel))
	{
		// Níveis 8 e 10: uma das opções é sempre de ultimate (se ainda sobrar alguma).
		TArray<ENRMutacao> Ultimates = Candidatas.FilterByPredicate(EhUltimate);
		if (Ultimates.Num() == 0)
		{
			Ultimates = Reserva.FilterByPredicate(EhUltimate);
		}
		if (Ultimates.Num() > 0)
		{
			const ENRMutacao M = SortearDe(Ultimates);
			Opcoes.Add(M);
			Candidatas.Remove(M);
			Reserva.Remove(M);
		}
	}
	while (Opcoes.Num() < OpcoesPorNivel && Candidatas.Num() > 0)
	{
		Opcoes.Add(SortearDe(Candidatas));
	}
	// Na troca, se não há opções novas que cheguem, completa com as antigas.
	while (Opcoes.Num() < OpcoesPorNivel && Reserva.Num() > 0)
	{
		Opcoes.Add(SortearDe(Reserva));
	}

	TArray<FString> Nomes;
	for (ENRMutacao M : Opcoes)
	{
		Nomes.Add(Nome(M).ToString());
	}
	UE_LOG(LogNexus, Log, TEXT("%s: mutacoes do nivel %d: %s"), *GetNameSafe(GetOwner()), Nivel, *FString::Join(Nomes, TEXT(" | ")));
}

// ------------------------------------------------------------------------------------------------ Escolha

void UNRMutacoesComponent::AoSubirNivel(int32 NovoNivel)
{
	for (int32 Nivel = UltimoNivel + 1; Nivel <= NovoNivel; ++Nivel)
	{
		NiveisPendentes.Add(Nivel);
	}
	UltimoNivel = FMath::Max(UltimoNivel, NovoNivel);
	if (Opcoes.Num() == 0 && NiveisPendentes.Num() > 0)
	{
		GerarOpcoes(TArray<ENRMutacao>());
	}
}

bool UNRMutacoesComponent::Escolher(int32 Indice)
{
	if (!GetOwner() || !GetOwner()->HasAuthority() || !Opcoes.IsValidIndex(Indice))
	{
		return false;
	}
	const ENRMutacao M = Opcoes[Indice];
	Escolhidas.Add(M);
	Aplicar(M);
	UE_LOG(LogNexus, Log, TEXT("%s: escolheu a mutacao %s (nivel %d)"), *GetNameSafe(GetOwner()), *Nome(M).ToString(), NivelDaEscolha());
	if (NiveisPendentes.Num() > 0)
	{
		NiveisPendentes.RemoveAt(0);
	}
	Opcoes.Reset();
	OnMutacaoEscolhida.Broadcast(M);
	if (NiveisPendentes.Num() > 0)
	{
		GerarOpcoes(TArray<ENRMutacao>());
	}
	return true;
}

bool UNRMutacoesComponent::TrocarOpcoes()
{
	if (!GetOwner() || !GetOwner()->HasAuthority() || TrocasRestantes <= 0 || Opcoes.Num() == 0)
	{
		return false;
	}
	--TrocasRestantes;
	const TArray<ENRMutacao> Antigas = Opcoes;
	GerarOpcoes(Antigas);
	return true;
}

void UNRMutacoesComponent::Aplicar(ENRMutacao Mutacao)
{
	UNRAbilitySystemComponent* ASC = GetASC();
	UNRCombateComponent* Combate = GetCombate();
	switch (Mutacao)
	{
	case ENRMutacao::Forca:
	case ENRMutacao::Agilidade:
	case ENRMutacao::Vitalidade:
	case ENRMutacao::Intelecto:
	case ENRMutacao::Espirito:
		if (ASC)
		{
			ASC->AdicionarPontosEfetivos(static_cast<int32>(Mutacao) - static_cast<int32>(ENRMutacao::Forca), PontosPorAtributo);
		}
		break;
	case ENRMutacao::BolaDeFogoChamas:
		if (Combate)
		{
			Combate->MagiaPrincipal.DuracaoChamas = DuracaoChamasBolaDeFogo;
		}
		break;
	case ENRMutacao::MuralhaLarga:
		if (Combate)
		{
			Combate->Magia2.Tamanho.Y *= 1.f + LarguraExtraMuralha;
		}
		break;
	case ENRMutacao::UltimateRecarga:
		if (Combate)
		{
			Combate->Ultimate.Recarga *= 1.f - ReducaoRecargaUltimate;
		}
		break;
	case ENRMutacao::UltimateArea:
		if (Combate)
		{
			const float Fator = FMath::Sqrt(1.f + AreaExtraUltimate);
			Combate->Ultimate.RaioArea *= Fator;
			Combate->Ultimate.RaioMeteoro *= Fator;
		}
		break;
	case ENRMutacao::UltimateMana:
		if (Combate)
		{
			Combate->ManaDevolvidaUltimate += ManaDevolvidaUltimate;
		}
		break;
	case ENRMutacao::VelocidadeForaDeCombate:
		if (ASC)
		{
			ASC->SomarBonusVelocForaDeCombate(VelocidadeForaDeCombate);
		}
		break;
	case ENRMutacao::CuraConsumiveis:
		if (ASC)
		{
			FNRBonus Bonus;
			Bonus.BonusCura = CuraExtraConsumiveis;
			ASC->AplicarBonus(Bonus);
		}
		break;
	default:
		break;
	}
}
