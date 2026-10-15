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
#include "GameFramework/Pawn.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "Items/NRInventoryComponent.h"
#include "Styling/CoreStyle.h"

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
			Aviso = FText::Format(NSLOCTEXT("Nexus", "SubiuNivel", "Nível {0}!"), ASC->Nivel);
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
		const float RecargaQ = Combate->RecargaRestante(1);
		FText EstadoQ;
		if (RecargaQ > 0.f)
		{
			EstadoQ = Segundos(RecargaQ);
		}
		else if (ASC && ASC->GetMana() < Combate->MagiaPrincipal.Custo)
		{
			EstadoQ = NSLOCTEXT("Nexus", "SemMana", "sem mana");
		}
		else
		{
			EstadoQ = NSLOCTEXT("Nexus", "Pronta", "pronta");
		}
		TextoMagias->SetText(FText::Format(NSLOCTEXT("Nexus", "Magias", "[Botão esq.] {0}     [Q] {1} ({2} de mana): {3}"),
			Combate->AtaqueBasico.Nome, Combate->MagiaPrincipal.Nome, FText::AsNumber(FMath::RoundToInt(Combate->MagiaPrincipal.Custo)), EstadoQ));
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
}
