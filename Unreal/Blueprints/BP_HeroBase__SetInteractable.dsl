; Called by BP_Interactable when the hero enters its sphere. The HUD (UNRHudWidget) reads CurrentInteractable.Prompt
; and shows "[F] ..." under the crosshair.
(fn SetInteractable (Target)
  (Variables|Default|SetCurrentInteractable Target))
