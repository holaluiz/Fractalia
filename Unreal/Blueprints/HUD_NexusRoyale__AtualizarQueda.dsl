; Mapa da queda: ao embarcar no dirigível o mapa em tela cheia abre sozinho (mostra a rota) e fecha no salto.
; bQueda lembra que fomos nós que abrimos, para não fechar um mapa que o jogador abriu com M depois do pouso.
(fn AtualizarQueda ()
  (bind hero (Utilities|Casting|CastToBP_HeroBase :Object (HUD|GetOwningPawn))
    (:then
      (bind abordo (Class|BPHeroBase|GetOnShip :self hero))
      (if (and abordo (not (Variables|Default|GetQueda)))
        (Variables|Default|SetQueda true)
        (CallFunction|MostrarCompleto :Mostrar true))
      (if (and (not abordo) (Variables|Default|GetQueda))
        (Variables|Default|SetQueda false)
        (CallFunction|MostrarCompleto :Mostrar false)))
    (:CastFailed)))
