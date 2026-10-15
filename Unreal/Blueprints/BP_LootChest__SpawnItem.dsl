; Pickups em fila na frente do baú (Slot 0..2), já com o item da tabela DT_Itens
(fn SpawnItem (ItemId Kind Rarity Slot)
  (bind side (* (Math|Conversions|ToFloat(Integer) (- Slot 1)) 90.0))
  (bind off (+ (* (Transformation|GetActorForwardVector) 140.0) (* (Transformation|GetActorRightVector) side)))
  (bind loc (+ (Transformation|GetActorLocation) off))
  (bind p (Game|SpawnActorfromClass :Class "/Game/NexusRoyale/Blueprints/Loot/BP_Pickup.BP_Pickup_C" :SpawnTransform (Math|Transform|MakeTransform :Location loc) :CollisionHandlingOverride "AlwaysSpawn"))
  (Class|BPPickup|SetupItem :self p :InItemId ItemId :InKind Kind :InRarity Rarity))
