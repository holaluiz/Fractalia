; HUD_NexusRoyale: cria o minimapa (canto superior direito, 260 px, 150 m em volta do jogador) e o mapa em tela
; cheia (900 px, ilha inteira), escondido até a tecla M (IA_Mapa -> AlternarMapa, ligado por ue_mapa_ui_build.py input).
; Ordem importa: SetPositionInViewport E SetDesiredSizeInViewport zeram as âncoras para (0,0)
; (UGameViewportSubsystem::SetWidgetSlotPosition/SetWidgetSlotDesiredSize, UE 5.8). Então: posição, tamanho,
; âncoras e alinhamento, nesta ordem. Com o tamanho por último (até 15/10), as âncoras voltavam a (0,0) e o
; minimapa ficava fora da tela, à esquerda, e o mapa completo com só um quarto à vista.
(event EventBeginPlay
  (bind pc (HUD|GetOwningPlayerController))
  (Input|EnableInput :self self :PlayerController pc)
  (bind mini (UserInterface|CreateWidget :Class "/Game/NexusRoyale/UI/Mapa/WBP_Mapa.WBP_Mapa_C" :OwningPlayer pc))
  (Class|WBPMapa|DefinirMaterial :self mini :NovoMaterial "/Game/NexusRoyale/UI/Mapa/MI_UI_Minimapa.MI_UI_Minimapa")
  (UserInterface|Viewport|AddtoViewport :self mini :ZOrder 5)
  (UserInterface|Viewport|SetPositioninViewport :self mini :Position (Math|Vector2D|MakeVector2D :X -24.0 :Y 24.0) :bRemoveDPIScale false)
  (UserInterface|Viewport|SetDesiredSizeinViewport :self mini :Size (Math|Vector2D|MakeVector2D :X 260.0 :Y 260.0))
  (UserInterface|Viewport|SetAnchorsinViewport :self mini
    :Anchors (Utilities|Struct|MakeAnchors :Minimum (Math|Vector2D|MakeVector2D :X 1.0 :Y 0.0) :Maximum (Math|Vector2D|MakeVector2D :X 1.0 :Y 0.0)))
  (UserInterface|Viewport|SetAlignmentinViewport :self mini :Alignment (Math|Vector2D|MakeVector2D :X 1.0 :Y 0.0))
  (Class|Widget|SetVisibility :self mini :Visibility "HitTestInvisible")
  (Variables|Default|SetMini mini)

  (bind full (UserInterface|CreateWidget :Class "/Game/NexusRoyale/UI/Mapa/WBP_Mapa.WBP_Mapa_C" :OwningPlayer pc))
  (Class|WBPMapa|DefinirMaterial :self full :NovoMaterial "/Game/NexusRoyale/UI/Mapa/MI_UI_MapaCompleto.MI_UI_MapaCompleto")
  (UserInterface|Viewport|AddtoViewport :self full :ZOrder 10)
  (UserInterface|Viewport|SetPositioninViewport :self full :Position (Math|Vector2D|MakeVector2D :X 0.0 :Y 0.0) :bRemoveDPIScale false)
  (UserInterface|Viewport|SetDesiredSizeinViewport :self full :Size (Math|Vector2D|MakeVector2D :X 900.0 :Y 900.0))
  (UserInterface|Viewport|SetAnchorsinViewport :self full
    :Anchors (Utilities|Struct|MakeAnchors :Minimum (Math|Vector2D|MakeVector2D :X 0.5 :Y 0.5) :Maximum (Math|Vector2D|MakeVector2D :X 0.5 :Y 0.5)))
  (UserInterface|Viewport|SetAlignmentinViewport :self full :Alignment (Math|Vector2D|MakeVector2D :X 0.5 :Y 0.5))
  (Variables|Default|SetCompleto full)
  (CallFunction|MostrarCompleto :Mostrar false))

(event EventTick (DeltaSeconds)
  (CallFunction|AtualizarQueda))
