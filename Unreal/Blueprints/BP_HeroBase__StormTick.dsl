; Called by BP_StormController every second while outside the circle: % of max health, ignoring armor (GDD 13).
; The HUD (UNRHudWidget) shows "FORA DA ZONA" with the distance and the % per second.
(fn StormTick (DamagePercent)
  (Nexus|Efeitos|AplicarDanoTempestade :self (Variables|Default|GetHabilidades) :PorcentagemDaVidaMax DamagePercent))
