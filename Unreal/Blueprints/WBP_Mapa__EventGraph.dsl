; WBP_Mapa: o mesmo widget faz o minimapa e o mapa em tela cheia (também usado como mapa da queda).
; O desenho é do material (MI_UI_Minimapa ou MI_UI_MapaCompleto, escolhido pelo HUD com DefinirMaterial antes de
; entrar na tela); o Atualizar só passa os valores globais para a MPC_Mapa.
(event UserInterface|EventConstruct
  (Class|Image|SetBrush :self (Variables|WBP_Mapa|GetImagem)
    :Brush (Utilities|Struct|MakeSlateBrush :ResourceObject (Variables|Default|GetMaterialMapa))))

(event UserInterface|EventTick (MyGeometry InDeltaTime)
  (CallFunction|Atualizar))
