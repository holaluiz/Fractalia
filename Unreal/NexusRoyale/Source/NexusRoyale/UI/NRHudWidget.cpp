#include "UI/NRHudWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Combat/NRCombateComponent.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/ProgressBar.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/CurveTable.h"
#include "EngineUtils.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/Pawn.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "Items/NRInventoryComponent.h"
#include "Items/NRItemLibrary.h"
#include "Progression/NRMutacoesComponent.h"
#include "Styling/CoreStyle.h"
#include "UObject/UnrealType.h"

namespace
{
	FText Barra(float Atual, float Maximo)
	{
		return FText::Format(NSLOCTEXT("Nexus", "Barra", "{0} / {1}"),
			FText::AsNumber(FMath::RoundToInt(Atual)), FText::AsNumber(FMath::RoundToInt(Maximo)));
	}

	FText Segundos(float Valor)
	{
		FNumberFormattingOptions Opcoes;
		Opcoes.MinimumFractionalDigits = 1;
		Opcoes.MaximumFractionalDigits = 1;
		return FText::Format(NSLOCTEXT("Nexus", "Segundos", "{0} s"), FText::AsNumber(Valor, &Opcoes));
	}

	FText MinutosSegundos(float Valor)
	{
		const int32 Total = FMath::CeilToInt(FMath::Max(0.f, Valor));
		return FText::FromString(FString::Printf(TEXT("%d:%02d"), Total / 60, Total % 60));
	}

	// Variáveis de Blueprint lidas pelo nome (BP_StormController, BP_HeroBase, BP_Interactable).
	bool LerBool(const UObject* Objeto, FName Nome, bool& Saida)
	{
		const FBoolProperty* P = Objeto ? FindFProperty<FBoolProperty>(Objeto->GetClass(), Nome) : nullptr;
		if (P)
		{
			Saida = P->GetPropertyValue_InContainer(Objeto);
		}
		return P != nullptr;
	}

	bool LerNumero(const UObject* Objeto, FName Nome, double& Saida)
	{
		const FNumericProperty* P = Objeto ? FindFProperty<FNumericProperty>(Objeto->GetClass(), Nome) : nullptr;
		if (!P)
		{
			return false;
		}
		const void* Valor = P->ContainerPtrToValuePtr<void>(Objeto);
		Saida = P->IsFloatingPoint() ? P->GetFloatingPointPropertyValue(Valor) : static_cast<double>(P->GetSignedIntPropertyValue(Valor));
		return true;
	}

	bool LerVetor(const UObject* Objeto, FName Nome, FVector& Saida)
	{
		const FStructProperty* P = Objeto ? FindFProperty<FStructProperty>(Objeto->GetClass(), Nome) : nullptr;
		if (!P || P->Struct != TBaseStructure<FVector>::Get())
		{
			return false;
		}
		Saida = *P->ContainerPtrToValuePtr<FVector>(Objeto);
		return true;
	}

	UObject* LerObjeto(const UObject* Objeto, FName Nome)
	{
		const FObjectPropertyBase* P = Objeto ? FindFProperty<FObjectPropertyBase>(Objeto->GetClass(), Nome) : nullptr;
		return P ? P->GetObjectPropertyValue_InContainer(Objeto) : nullptr;
	}

	FText LerTexto(const UObject* Objeto, FName Nome)
	{
		const FTextProperty* P = Objeto ? FindFProperty<FTextProperty>(Objeto->GetClass(), Nome) : nullptr;
		return P ? P->GetPropertyValue_InContainer(Objeto) : FText::GetEmpty();
	}

	FString LerString(const UObject* Objeto, FName Nome)
	{
		const FStrProperty* P = Objeto ? FindFProperty<FStrProperty>(Objeto->GetClass(), Nome) : nullptr;
		return P ? P->GetPropertyValue_InContainer(Objeto) : FString();
	}

	float ValorTabela(UCurveTable* Tabela, const TCHAR* Linha, int32 Fase)
	{
		const FRealCurve* Curva = Tabela ? Tabela->FindCurve(FName(Linha), TEXT("HUD"), false) : nullptr;
		return Curva ? Curva->Eval(static_cast<float>(Fase), 0.f) : 0.f;
	}
}

bool UNRHudWidget::Initialize()
{
	const bool bOk = Super::Initialize();
	if (bOk && WidgetTree && !WidgetTree->RootWidget)
	{
		MontarLayoutPadrao();
	}
	return bOk;
}

void UNRHudWidget::MontarLayoutPadrao()
{
	auto Texto = [this](const TCHAR* Nome, int32 Tamanho, const FLinearColor& Cor = FLinearColor::White)
	{
		UTextBlock* T = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Nome);
		T->SetFont(FCoreStyle::GetDefaultFontStyle("Bold", Tamanho));
		T->SetColorAndOpacity(FSlateColor(Cor));
		T->SetShadowOffset(FVector2D(1.f, 1.f));
		T->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.85f));
		return T;
	};
	auto Caixa = [this](UWidget* Conteudo, float Largura, float Altura)
	{
		USizeBox* S = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
		S->SetWidthOverride(Largura);
		S->SetHeightOverride(Altura);
		S->AddChild(Conteudo);
		return S;
	};
	auto BarraCom = [&](const TCHAR* NomeBarra, const TCHAR* NomeTexto, const FLinearColor& Cor, float Altura,
	                    TObjectPtr<UProgressBar>& SaidaBarra, TObjectPtr<UTextBlock>& SaidaTexto)
	{
		UOverlay* O = WidgetTree->ConstructWidget<UOverlay>(UOverlay::StaticClass());
		SaidaBarra = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), NomeBarra);
		SaidaBarra->SetFillColorAndOpacity(Cor);
		SaidaBarra->SetPercent(1.f);
		UOverlaySlot* SB = O->AddChildToOverlay(SaidaBarra);
		SB->SetHorizontalAlignment(HAlign_Fill);
		SB->SetVerticalAlignment(VAlign_Fill);
		if (NomeTexto)
		{
			SaidaTexto = Texto(NomeTexto, 11);
			UOverlaySlot* ST = O->AddChildToOverlay(SaidaTexto);
			ST->SetHorizontalAlignment(HAlign_Center);
			ST->SetVerticalAlignment(VAlign_Center);
		}
		return Caixa(O, 440.f, Altura);
	};

	UCanvasPanel* Raiz = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Raiz"));
	WidgetTree->RootWidget = Raiz;

	// Pé da tela: nível e XP, vida, mana, magias e consumíveis.
	UVerticalBox* Pe = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Pe"));
	auto Linha = [Pe](UWidget* W, float Espaco)
	{
		UVerticalBoxSlot* S = Pe->AddChildToVerticalBox(W);
		S->SetHorizontalAlignment(HAlign_Center);
		S->SetPadding(FMargin(0.f, Espaco, 0.f, 0.f));
	};
	TextoMensagem = Texto(TEXT("TextoMensagem"), 13, FLinearColor(0.75f, 1.f, 0.75f));
	Linha(TextoMensagem, 0.f);
	TextoNivel = Texto(TEXT("TextoNivel"), 14, FLinearColor(1.f, 0.85f, 0.35f));
	Linha(TextoNivel, 8.f);
	TObjectPtr<UTextBlock> SemTexto;
	Linha(BarraCom(TEXT("BarraXP"), nullptr, FLinearColor(1.f, 0.75f, 0.1f), 7.f, BarraXP, SemTexto), 2.f);
	Linha(BarraCom(TEXT("BarraVida"), TEXT("TextoVida"), FLinearColor(0.85f, 0.12f, 0.1f), 24.f, BarraVida, TextoVida), 6.f);
	Linha(BarraCom(TEXT("BarraMana"), TEXT("TextoMana"), FLinearColor(0.15f, 0.4f, 1.f), 16.f, BarraMana, TextoMana), 3.f);
	TextoMagias = Texto(TEXT("TextoMagias"), 12);
	TextoMagias->SetJustification(ETextJustify::Center);
	Linha(TextoMagias, 6.f);
	UHorizontalBox* Consumiveis = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass());
	TObjectPtr<UTextBlock>* Slots[3] = { &TextoConsumivel0, &TextoConsumivel1, &TextoConsumivel2 };
	const TCHAR* NomesSlots[3] = { TEXT("TextoConsumivel0"), TEXT("TextoConsumivel1"), TEXT("TextoConsumivel2") };
	for (int32 i = 0; i < 3; ++i)
	{
		*Slots[i] = Texto(NomesSlots[i], 11, FLinearColor(0.85f, 0.95f, 0.85f));
		Consumiveis->AddChildToHorizontalBox(*Slots[i])->SetPadding(FMargin(10.f, 0.f));
	}
	Linha(Consumiveis, 3.f);

	UCanvasPanelSlot* SlotPe = Raiz->AddChildToCanvas(Pe);
	SlotPe->SetAnchors(FAnchors(0.5f, 1.f));
	SlotPe->SetAlignment(FVector2D(0.5f, 1.f));
	SlotPe->SetPosition(FVector2D(0.f, -20.f));
	SlotPe->SetAutoSize(true);

	// Canto inferior esquerdo: itens equipados.
	TextoEquipados = Texto(TEXT("TextoEquipados"), 11, FLinearColor(0.8f, 0.85f, 1.f));
	UCanvasPanelSlot* SlotEquip = Raiz->AddChildToCanvas(TextoEquipados);
	SlotEquip->SetAnchors(FAnchors(0.f, 1.f));
	SlotEquip->SetAlignment(FVector2D(0.f, 1.f));
	SlotEquip->SetPosition(FVector2D(24.f, -24.f));
	SlotEquip->SetAutoSize(true);

	// Centro exato: a mira.
	Mira = Texto(TEXT("Mira"), 18, FLinearColor(1.f, 1.f, 1.f, 0.85f));
	Mira->SetText(FText::FromString(TEXT("+")));
	UCanvasPanelSlot* SlotMira = Raiz->AddChildToCanvas(Mira);
	SlotMira->SetAnchors(FAnchors(0.5f, 0.5f));
	SlotMira->SetAlignment(FVector2D(0.5f, 0.5f));
	SlotMira->SetAutoSize(true);

	// Centro: avisos grandes (subiu de nível, eliminado).
	TextoAviso = Texto(TEXT("TextoAviso"), 30);
	TextoAviso->SetJustification(ETextJustify::Center);
	UCanvasPanelSlot* SlotAviso = Raiz->AddChildToCanvas(TextoAviso);
	SlotAviso->SetAnchors(FAnchors(0.5f, 0.32f));
	SlotAviso->SetAlignment(FVector2D(0.5f, 0.5f));
	SlotAviso->SetAutoSize(true);

	// Topo, no centro: relógio da tempestade e, embaixo, o aviso de fora da zona.
	UVerticalBox* Topo = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("Topo"));
	TextoTempestade = Texto(TEXT("TextoTempestade"), 14, FLinearColor(0.88f, 0.75f, 1.f));
	Topo->AddChildToVerticalBox(TextoTempestade)->SetHorizontalAlignment(HAlign_Center);
	TextoForaDaZona = Texto(TEXT("TextoForaDaZona"), 20, FLinearColor(1.f, 0.35f, 0.9f));
	UVerticalBoxSlot* SlotFora = Topo->AddChildToVerticalBox(TextoForaDaZona);
	SlotFora->SetHorizontalAlignment(HAlign_Center);
	SlotFora->SetPadding(FMargin(0.f, 4.f, 0.f, 0.f));
	UCanvasPanelSlot* SlotTopo = Raiz->AddChildToCanvas(Topo);
	SlotTopo->SetAnchors(FAnchors(0.5f, 0.f));
	SlotTopo->SetAlignment(FVector2D(0.5f, 0.f));
	SlotTopo->SetPosition(FVector2D(0.f, 18.f));
	SlotTopo->SetAutoSize(true);

	// Logo abaixo da mira: o que o F faz.
	TextoPrompt = Texto(TEXT("TextoPrompt"), 14, FLinearColor(1.f, 0.95f, 0.7f));
	UCanvasPanelSlot* SlotPrompt = Raiz->AddChildToCanvas(TextoPrompt);
	SlotPrompt->SetAnchors(FAnchors(0.5f, 0.5f));
	SlotPrompt->SetAlignment(FVector2D(0.5f, 0.f));
	SlotPrompt->SetPosition(FVector2D(0.f, 36.f));
	SlotPrompt->SetAutoSize(true);

	// Direita, um pouco abaixo do meio (o minimapa fica no canto de cima): a escolha de mutação.
	TextoMutacoes = Texto(TEXT("TextoMutacoes"), 13, FLinearColor(0.75f, 1.f, 0.85f));
	UCanvasPanelSlot* SlotMutacoes = Raiz->AddChildToCanvas(TextoMutacoes);
	SlotMutacoes->SetAnchors(FAnchors(1.f, 0.5f));
	SlotMutacoes->SetAlignment(FVector2D(1.f, 0.5f));
	SlotMutacoes->SetPosition(FVector2D(-24.f, 60.f));
	SlotMutacoes->SetAutoSize(true);

	// Esquerda, no meio da altura: as mutações já escolhidas.
	TextoMutacoesEscolhidas = Texto(TEXT("TextoMutacoesEscolhidas"), 11, FLinearColor(0.75f, 1.f, 0.85f));
	UCanvasPanelSlot* SlotEscolhidas = Raiz->AddChildToCanvas(TextoMutacoesEscolhidas);
	SlotEscolhidas->SetAnchors(FAnchors(0.f, 0.5f));
	SlotEscolhidas->SetAlignment(FVector2D(0.f, 0.5f));
	SlotEscolhidas->SetPosition(FVector2D(24.f, 0.f));
	SlotEscolhidas->SetAutoSize(true);
}

UNRMutacoesComponent* UNRHudWidget::GetMutacoesDoJogador() const
{
	const APawn* Pawn = GetOwningPlayerPawn();
	return Pawn ? Pawn->FindComponentByClass<UNRMutacoesComponent>() : nullptr;
}

void UNRHudWidget::AtualizarTempestade()
{
	UWorld* World = GetWorld();
	if (!World || (!TextoTempestade && !TextoForaDaZona))
	{
		return;
	}
	if (!Tempestade.IsValid() && World->GetTimeSeconds() >= ProximaBuscaTempestade)
	{
		ProximaBuscaTempestade = World->GetTimeSeconds() + 2.0;
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			if (It->GetClass()->GetName().StartsWith(TEXT("BP_StormController")))
			{
				Tempestade = *It;
				break;
			}
		}
	}

	FText Relogio, Fora;
	AActor* T = Tempestade.Get();
	bool bComecou = false;
	if (T && LerBool(T, TEXT("bStarted"), bComecou) && bComecou)
	{
		bool bFechando = false;
		double Inicio = 0.0, FaseNum = 0.0, Raio = 0.0;
		FVector Centro = FVector::ZeroVector;
		LerBool(T, TEXT("bClosing"), bFechando);
		LerNumero(T, TEXT("StartTime"), Inicio);
		LerNumero(T, TEXT("CurPhase"), FaseNum);
		LerNumero(T, TEXT("CurRadius"), Raio);
		LerVetor(T, TEXT("CurCenter"), Centro);
		UCurveTable* Tabela = Cast<UCurveTable>(LerObjeto(T, TEXT("StormTable")));
		const AGameStateBase* GameState = World->GetGameState();
		const double Agora = (GameState ? GameState->GetServerWorldTimeSeconds() : World->GetTimeSeconds()) - Inicio;
		const int32 Fase = static_cast<int32>(FaseNum);

		// Mesma conta do BP_StormController.UpdateCircle: fase 7 = fechou de vez.
		if (Fase < 1 || Fase > 6)
		{
			Relogio = NSLOCTEXT("Nexus", "TempestadeFechou", "A tempestade fechou");
		}
		else
		{
			const float Alvo = ValorTabela(Tabela, bFechando ? TEXT("ShrinkEnd") : TEXT("ShrinkStart"), Fase);
			Relogio = FText::Format(bFechando
				? NSLOCTEXT("Nexus", "TempestadeFechando", "Fase {0}  ·  a tempestade está fechando: {1}")
				: NSLOCTEXT("Nexus", "TempestadeFechaEm", "Fase {0}  ·  a tempestade fecha em {1}"),
				Fase, MinutosSegundos(static_cast<float>(Alvo - Agora)));
		}

		const APawn* Pawn = GetOwningPlayerPawn();
		const UNRAbilitySystemComponent* ASC = GetASCDoJogador();
		if (Pawn && !Pawn->IsHidden() && !(ASC && ASC->IsMorto()))
		{
			const double Distancia = FVector::Dist2D(Pawn->GetActorLocation(), Centro);
			if (Distancia > Raio)
			{
				Fora = FText::Format(NSLOCTEXT("Nexus", "ForaDaZona", "FORA DA ZONA: {0} m até o círculo  ·  −{1}% da vida por segundo"),
					FText::AsNumber(FMath::CeilToInt((Distancia - Raio) / 100.0)),
					FText::AsNumber(ValorTabela(Tabela, TEXT("DamagePct"), FMath::Min(Fase, 6))));
			}
		}
	}
	if (TextoTempestade) TextoTempestade->SetText(Relogio);
	if (TextoForaDaZona) TextoForaDaZona->SetText(Fora);
}

void UNRHudWidget::AtualizarPrompt()
{
	if (!TextoPrompt)
	{
		return;
	}
	FText Prompt;
	APawn* Pawn = GetOwningPlayerPawn();
	const UNRAbilitySystemComponent* ASC = GetASCDoJogador();
	if (Pawn && !Pawn->IsHidden() && !(ASC && ASC->IsMorto()))
	{
		// O interativo atual do herói; sem ele (o último pickup sumiu), o primeiro sobreposto, como o F faz.
		AActor* Alvo = Cast<AActor>(LerObjeto(Pawn, TEXT("CurrentInteractable")));
		if (!IsValid(Alvo) || LerTexto(Alvo, TEXT("Prompt")).IsEmpty())
		{
			Alvo = nullptr;
			TArray<AActor*> Perto;
			Pawn->GetOverlappingActors(Perto);
			for (AActor* Ator : Perto)
			{
				if (IsValid(Ator) && !LerTexto(Ator, TEXT("Prompt")).IsEmpty())
				{
					Alvo = Ator;
					break;
				}
			}
		}
		if (Alvo)
		{
			// Pickup (BP_Pickup): "Pegar: Anel do Foco (Raro)".
			FText Acao = LerTexto(Alvo, TEXT("Prompt"));
			const FString Item = LerString(Alvo, TEXT("ItemName"));
			double Raridade = 0.0;
			if (!Item.IsEmpty() && LerNumero(Alvo, TEXT("Rarity"), Raridade))
			{
				Acao = FText::Format(NSLOCTEXT("Nexus", "PromptItem", "{0}: {1} ({2})"), Acao, FText::FromString(Item),
					UNRItemLibrary::NomeDaRaridade(static_cast<int32>(Raridade)));
			}
			Prompt = FText::Format(NSLOCTEXT("Nexus", "PromptF", "[F] {0}"), Acao);
		}
	}
	TextoPrompt->SetText(Prompt);
}

void UNRHudWidget::AtualizarMutacoes()
{
	const UNRMutacoesComponent* Mutacoes = GetMutacoesDoJogador();
	FText Painel, Lista;
	if (Mutacoes)
	{
		if (Mutacoes->TemEscolhaPendente())
		{
			TArray<FString> Linhas;
			FString Titulo = FText::Format(NSLOCTEXT("Nexus", "MutacaoTitulo", "MUTAÇÃO DO NÍVEL {0}"), Mutacoes->NivelDaEscolha()).ToString();
			if (Mutacoes->NiveisPendentes.Num() > 1)
			{
				Titulo += FText::Format(NSLOCTEXT("Nexus", "MutacaoFila", "  (+{0} na fila)"), Mutacoes->NiveisPendentes.Num() - 1).ToString();
			}
			Linhas.Add(Titulo);
			for (int32 i = 0; i < Mutacoes->Opcoes.Num(); ++i)
			{
				const ENRMutacao M = Mutacoes->Opcoes[i];
				Linhas.Add(FText::Format(NSLOCTEXT("Nexus", "MutacaoOpcao", "[Alt+{0}] {1}: {2}"),
					i + 1, UNRMutacoesComponent::Nome(M), Mutacoes->Descrever(M)).ToString());
			}
			Linhas.Add(Mutacoes->TrocasRestantes > 0
				? FText::Format(NSLOCTEXT("Nexus", "MutacaoTrocar", "[Alt+4] trocar as opções ({0} restante)"), Mutacoes->TrocasRestantes).ToString()
				: NSLOCTEXT("Nexus", "MutacaoSemTroca", "(sem trocas de opções)").ToString());
			Painel = FText::FromString(FString::Join(Linhas, TEXT("\n")));
		}
		if (Mutacoes->Escolhidas.Num() > 0)
		{
			// Atributos repetidos viram uma linha só ("Intelecto +4").
			TArray<ENRMutacao> Ordem;
			TMap<ENRMutacao, int32> Vezes;
			for (ENRMutacao M : Mutacoes->Escolhidas)
			{
				if (!Vezes.Contains(M))
				{
					Ordem.Add(M);
				}
				++Vezes.FindOrAdd(M);
			}
			TArray<FString> Linhas;
			Linhas.Add(NSLOCTEXT("Nexus", "MutacoesEscolhidas", "Mutações:").ToString());
			for (ENRMutacao M : Ordem)
			{
				Linhas.Add(UNRMutacoesComponent::Categoria(M) == ENRCategoriaMutacao::Atributo
					? FString::Printf(TEXT("%s +%d"), *UNRMutacoesComponent::Nome(M).ToString(),
						FMath::RoundToInt(Mutacoes->PontosPorAtributo * Vezes[M]))
					: UNRMutacoesComponent::Nome(M).ToString());
			}
			Lista = FText::FromString(FString::Join(Linhas, TEXT("\n")));
		}
	}
	if (TextoMutacoes) TextoMutacoes->SetText(Painel);
	if (TextoMutacoesEscolhidas) TextoMutacoesEscolhidas->SetText(Lista);
}

UNRAbilitySystemComponent* UNRHudWidget::GetASCDoJogador() const
{
	const APawn* Pawn = GetOwningPlayerPawn();
	return Pawn ? Pawn->FindComponentByClass<UNRAbilitySystemComponent>() : nullptr;
}

UNRInventoryComponent* UNRHudWidget::GetInventarioDoJogador() const
{
	const APawn* Pawn = GetOwningPlayerPawn();
	return Pawn ? Pawn->FindComponentByClass<UNRInventoryComponent>() : nullptr;
}

UNRCombateComponent* UNRHudWidget::GetCombateDoJogador() const
{
	const APawn* Pawn = GetOwningPlayerPawn();
	return Pawn ? Pawn->FindComponentByClass<UNRCombateComponent>() : nullptr;
}

void UNRHudWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	const UNRAbilitySystemComponent* ASC = GetASCDoJogador();
	const UNRCombateComponent* Combate = GetCombateDoJogador();
	FText Aviso;
	FLinearColor CorAviso = FLinearColor::White;

	if (ASC)
	{
		const float Vida = ASC->GetVida(), VidaMax = ASC->GetVidaMax();
		const float Mana = ASC->GetMana(), ManaMax = ASC->GetManaMax();
		if (BarraVida) BarraVida->SetPercent(VidaMax > 0.f ? Vida / VidaMax : 0.f);
		if (BarraMana) BarraMana->SetPercent(ManaMax > 0.f ? Mana / ManaMax : 0.f);
		if (TextoVida) TextoVida->SetText(Barra(Vida, VidaMax));
		if (TextoMana) TextoMana->SetText(Barra(Mana, ManaMax));

		int32 NoNivel = 0, ParaProximo = 0;
		ASC->ProgressoXP(NoNivel, ParaProximo);
		if (BarraXP) BarraXP->SetPercent(ParaProximo > 0 ? static_cast<float>(NoNivel) / ParaProximo : 1.f);
		if (TextoNivel)
		{
			TextoNivel->SetText(ParaProximo > 0
				? FText::Format(NSLOCTEXT("Nexus", "NivelXP", "Nível {0}  ·  {1} / {2} XP"), ASC->Nivel, NoNivel, ParaProximo)
				: FText::Format(NSLOCTEXT("Nexus", "NivelMax", "Nível {0} (máximo)"), ASC->Nivel));
		}

		if (UltimoNivel > 0 && ASC->Nivel > UltimoNivel)
		{
			TempoAvisoNivel = 2.5f;
		}
		UltimoNivel = ASC->Nivel;
		TempoAvisoNivel = FMath::Max(0.f, TempoAvisoNivel - InDeltaTime);
		if (TempoAvisoNivel > 0.f)
		{
			const UNRMutacoesComponent* Mutacoes = GetMutacoesDoJogador();
			Aviso = Mutacoes && Mutacoes->TemEscolhaPendente()
				? FText::Format(NSLOCTEXT("Nexus", "SubiuNivelMutacao", "Nível {0}!\nEscolha uma mutação: Alt+1, Alt+2 ou Alt+3"), ASC->Nivel)
				: FText::Format(NSLOCTEXT("Nexus", "SubiuNivel", "Nível {0}!"), ASC->Nivel);
			CorAviso = FLinearColor(1.f, 0.8f, 0.2f);
		}
		if (ASC->IsMorto())
		{
			const float Falta = Combate ? Combate->TempoAteRecomecar() : 0.f;
			Aviso = Falta > 0.f
				? FText::Format(NSLOCTEXT("Nexus", "EliminadoRecomeca", "VOCÊ FOI ELIMINADO\nRecomeçando em {0}"), FText::AsNumber(FMath::CeilToInt(Falta)))
				: NSLOCTEXT("Nexus", "Eliminado", "VOCÊ FOI ELIMINADO");
			CorAviso = FLinearColor(1.f, 0.25f, 0.2f);
		}
	}
	if (TextoAviso)
	{
		TextoAviso->SetText(Aviso);
		TextoAviso->SetColorAndOpacity(FSlateColor(CorAviso));
	}
	if (Mira)
	{
		// Sem mira no dirigível (herói escondido) e depois da morte.
		const APawn* Pawn = GetOwningPlayerPawn();
		const bool bMirando = Pawn && !Pawn->IsHidden() && !(ASC && ASC->IsMorto());
		Mira->SetVisibility(bMirando ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	}

	if (Combate && TextoMagias)
	{
		// "[Q] Bola de Fogo (55 de mana): pronta" / "4,2 s" / "sem mana" / "nível 6" (ultimate ainda presa).
		auto Magia = [&](const TCHAR* Tecla, int32 Indice, const FText& Nome, float Custo, bool bLiberada)
		{
			FText Estado;
			const float Recarga = Combate->RecargaRestante(Indice);
			if (!bLiberada)
			{
				Estado = FText::Format(NSLOCTEXT("Nexus", "LiberaNoNivel", "nível {0}"), Combate->NivelUltimate);
			}
			else if (Recarga > 0.f)
			{
				Estado = Segundos(Recarga);
			}
			else if (ASC && ASC->GetMana() < Custo)
			{
				Estado = NSLOCTEXT("Nexus", "SemMana", "sem mana");
			}
			else
			{
				Estado = NSLOCTEXT("Nexus", "Pronta", "pronta");
			}
			return FText::Format(NSLOCTEXT("Nexus", "Magia", "[{0}] {1} ({2} de mana): {3}"),
				FText::FromString(Tecla), Nome, FText::AsNumber(FMath::RoundToInt(Custo)), Estado);
		};
		TextoMagias->SetText(FText::Format(NSLOCTEXT("Nexus", "Magias", "[Botão esq.] {0}     {1}\n{2}     {3}"),
			Combate->AtaqueBasico.Nome,
			Magia(TEXT("Q"), 1, Combate->MagiaPrincipal.Nome, Combate->MagiaPrincipal.Custo, true),
			Magia(TEXT("E"), 2, Combate->Magia2.Nome, Combate->Magia2.Custo, true),
			Magia(TEXT("X"), 3, Combate->Ultimate.Nome, Combate->Ultimate.Custo, Combate->UltimateLiberada())));
	}

	if (const UNRInventoryComponent* Inventario = GetInventarioDoJogador())
	{
		if (TextoMensagem)
		{
			TextoMensagem->SetText(Inventario->MensagemRecente());
		}
		UTextBlock* Slots[3] = { TextoConsumivel0, TextoConsumivel1, TextoConsumivel2 };
		for (int32 i = 0; i < 3; ++i)
		{
			if (Slots[i])
			{
				const FText Item = Inventario->DescreverConsumivel(i);
				Slots[i]->SetText(FText::Format(NSLOCTEXT("Nexus", "TeclaConsumivel", "[{0}] {1}"),
					FText::AsNumber(i + 1), Item.IsEmpty() ? NSLOCTEXT("Nexus", "Vazio", "-") : Item));
			}
		}
		if (TextoEquipados)
		{
			TArray<FString> Linhas;
			const ENRSlotItem SlotsEquipamento[4] = { ENRSlotItem::Armadura, ENRSlotItem::Cabeca, ENRSlotItem::Anel, ENRSlotItem::Amuleto };
			for (ENRSlotItem SlotEquip : SlotsEquipamento)
			{
				const FText Item = Inventario->DescreverEquipado(SlotEquip);
				if (!Item.IsEmpty())
				{
					Linhas.Add(Item.ToString());
				}
			}
			TextoEquipados->SetText(FText::FromString(FString::Join(Linhas, TEXT("\n"))));
		}
	}

	AtualizarTempestade();
	AtualizarPrompt();
	AtualizarMutacoes();
}
