; F no pickup: o item vai para o inventário do herói (UNRInventoryComponent.PegarDoChao; a mensagem aparece no HUD).
; Se trocou com o que estava no slot, o pickup passa a mostrar o item que saiu; se não coube, fica como está.
(event EventInteract (Hero)
  (bind inv (Actor|GetComponentbyClass :self Hero :ComponentClass "/Script/NexusRoyale.NRInventoryComponent"))
  (bind pegou (Nexus|Inventario|PegarDoChao :self inv :ItemId (Variables|Default|GetItemId) :Raridade (Variables|Default|GetRarity)))
  (if pegou
    (Class|BPHeroBase|ClearInteractable :self Hero :Target self)
    (Actor|DestroyActor)
    (else
      (CallFunction|SetupItem :InItemId (Nexus|Inventario|ItemQueFicaNoChao :self inv) :InKind (Variables|Default|GetKind) :InRarity (Nexus|Inventario|RaridadeQueFicaNoChao :self inv)))))
