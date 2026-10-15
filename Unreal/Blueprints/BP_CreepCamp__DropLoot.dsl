; GDD 12: small camp = DropChance (50%) of food or potion; medium camp = a grimoire (Comum-Raro, like the chest), always.
; The pickup lands at DropLocation (where a creep of the camp fell). Kind: 1 grimoire, 2 consumable.
(fn DropLoot ()
  (if (Math|Random|RandomBoolwithWeight :Weight (Variables|Default|GetDropChance))
    (bind dt (Nexus|Itens|TabelaPadrao))
    (bind loc (+ (Variables|Default|GetDropLocation) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 40.0)))
    (bind p (Game|SpawnActorfromClass :Class "/Game/NexusRoyale/Blueprints/Loot/BP_Pickup.BP_Pickup_C" :SpawnTransform (Math|Transform|MakeTransform :Location loc) :CollisionHandlingOverride "AlwaysSpawn"))
    (if (Variables|Default|GetDropGrimoire)
      (bind grim (Nexus|Itens|SortearItem :Tabela dt :Tipo "Grimorio"))
      (bind r (Math|Random|RandomFloat))
      (Class|BPPickup|SetupItem :self p :InItemId grim :InKind 1 :InRarity (select (< r 0.6) 0 (select (< r 0.9) 1 2)))
      (else
        (bind cons (Nexus|Itens|SortearItem :Tabela dt :Tipo "Consumivel"))
        (Class|BPPickup|SetupItem :self p :InItemId cons :InKind 2 :InRarity 0)))))
