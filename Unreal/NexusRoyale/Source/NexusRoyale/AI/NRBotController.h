#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "NRBotController.generated.h"

/**
 * Controlador dos bots jogadores (D-012). Por enquanto (M1) só ocupa uma vaga: tem PlayerState próprio (entra na
 * contagem de vivos, no placar e na vitória) e possui o mesmo herói dos humanos, mas ainda não pensa. O cérebro
 * (StateTree) chega no M15.
 */
UCLASS()
class NEXUSROYALE_API ANRBotController : public AAIController
{
	GENERATED_BODY()

public:
	ANRBotController();
};
