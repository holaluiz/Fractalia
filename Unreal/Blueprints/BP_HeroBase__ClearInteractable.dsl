(fn ClearInteractable (Target)
  (if (== (Variables|Default|GetCurrentInteractable) Target)
    (Variables|Default|SetCurrentInteractable)))
