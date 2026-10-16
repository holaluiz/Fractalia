#include "AI/NRBotController.h"

ANRBotController::ANRBotController()
{
	// Sem PlayerState o bot não existiria para o GameState: não contaria como vivo nem poderia vencer.
	bWantsPlayerState = true;
}
