; Called by BP_StormController every second while outside the circle: % of max health, ignoring armor (GDD 13)
(fn StormTick (DamagePercent)
  (Nexus|Efeitos|AplicarDanoTempestade :self (Variables|Default|GetHabilidades) :PorcentagemDaVidaMax DamagePercent)
  (Development|PrintString :InString (Utilities|String|Append "Tempestade: -" (Utilities|String|Append (Utilities|String|ToString(Float) DamagePercent) "% da vida")) :TextColor (Math|Color|MakeColor :R 0.6 :G 0.2 :B 1.0 :A 1.0) :Duration 1.0))
