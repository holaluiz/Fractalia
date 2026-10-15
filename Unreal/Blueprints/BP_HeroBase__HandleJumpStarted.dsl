; Space: jump off the ship (only once it is over the island, within the ship's DropRadius of the centre),
; otherwise a normal jump. TODO(rede): virar RPC no servidor
(fn HandleJumpStarted ()
  (if (Variables|Default|GetOnShip)
    (bind ship (Variables|Default|GetCurrentShip))
    (bind d (Math|Vector|Distance2D(Vector) (Transformation|GetActorLocation :self ship) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 0.0)))
    (if (< d (Class|BPDropShip|GetDropRadius :self ship))
      (Class|BPDropShip|Eject :self ship :Hero self)
      (else
        (Development|PrintString :InString "Espere o dirigível sobrevoar a ilha" :Duration 1.5)))
    (else
      (Character|Jump))))
