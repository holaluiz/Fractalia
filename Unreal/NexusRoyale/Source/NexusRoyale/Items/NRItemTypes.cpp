#include "Items/NRItemTypes.h"

FNRBonus FNRItemRow::CalcularBonus(float Multiplicador, float PontosDoAtributo) const
{
	FNRBonus Bonus;
	Bonus.VidaMax = VidaMax;
	Bonus.ManaMax = ManaMax;
	Bonus.Armadura = Armadura;
	Bonus.DanoFisico = DanoFisico;
	Bonus.PoderMagico = PoderMagico;
	Bonus.VelocMov = VelocMov;
	Bonus.VelocAtaque = VelocAtaque;
	Bonus.ReducaoRecarga = ReducaoRecarga;
	Bonus.RegenMana = RegenMana;
	const float Escala = EscalaComAtributo == ENRAtributoBuild::Nenhum ? 1.f : PontosDoAtributo;
	Bonus *= Multiplicador * Escala;
	return Bonus;
}
