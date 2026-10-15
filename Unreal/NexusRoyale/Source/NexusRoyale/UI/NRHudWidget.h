#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "NRHudWidget.generated.h"

class UProgressBar;
class UTextBlock;
class UNRAbilitySystemComponent;
class UNRCombateComponent;
class UNRInventoryComponent;

/**
 * HUD do jogador. Duas formas de usar:
 * - direto (UNRCombateComponent cria esta classe): monta sozinho um layout simples no pé da tela;
 * - como base de um WBP_HUD: o Widget Blueprint só precisa ter widgets com estes nomes (todos opcionais):
 *   BarraVida, BarraMana, BarraXP (ProgressBar); TextoVida, TextoMana, TextoNivel, TextoMagias, TextoAviso, Mira,
 *   TextoConsumivel0..2, TextoEquipados (TextBlock).
 * A cada frame o C++ lê os componentes Nexus do pawn do jogador.
 * O relógio da tempestade fica no grafo do próprio WBP (lê o BP_StormController).
 */
UCLASS()
class NEXUSROYALE_API UNRHudWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	virtual bool Initialize() override;

protected:
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UProgressBar> BarraVida;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UProgressBar> BarraMana;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UProgressBar> BarraXP;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoVida;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoMana;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoNivel;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoMagias;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoAviso;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoMensagem;
	/** Mira no centro da tela: as magias saem na direção do que estiver nela. */
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> Mira;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoConsumivel0;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoConsumivel1;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoConsumivel2;
	UPROPERTY(meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> TextoEquipados;

	UFUNCTION(BlueprintPure, Category = "Nexus|HUD")
	UNRAbilitySystemComponent* GetASCDoJogador() const;

	UFUNCTION(BlueprintPure, Category = "Nexus|HUD")
	UNRInventoryComponent* GetInventarioDoJogador() const;

	UFUNCTION(BlueprintPure, Category = "Nexus|HUD")
	UNRCombateComponent* GetCombateDoJogador() const;

private:
	/** Layout padrão, usado quando não há Widget Blueprint (a árvore está vazia). */
	void MontarLayoutPadrao();

	int32 UltimoNivel = 0;
	float TempoAvisoNivel = 0.f;
};
