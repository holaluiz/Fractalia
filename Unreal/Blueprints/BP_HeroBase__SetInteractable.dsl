; Called by BP_Interactable when the hero enters its sphere. TODO(HUD): prompt na tela em vez de PrintString
(fn SetInteractable (Target)
  (Variables|Default|SetCurrentInteractable Target)
  (Development|PrintString :InString (Utilities|String|Append "[F] " (Utilities|String|ToString(Text) (Class|BPInteractable|GetPrompt :self Target))) :Duration 2.0))
