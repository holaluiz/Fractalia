; Position from the shared clock; at the end the server drops everyone and removes the ship
(fn FlyTick ()
  (bind s (Variables|Default|GetStartPoint))
  (bind e (Variables|Default|GetEndPoint))
  (bind t (- (GameState|GetServerWorldTimeSeconds :self (Game|GetGameState)) (Variables|Default|GetLaunchTime)))
  (bind a (/ (* t (Variables|Default|GetSpeed)) (Math|Vector|Distance(Vector) :V1 s :V2 e)))
  (if (>= a 1.0)
    (if (Networking|HasAuthority)
      (Variables|Default|SetFlying false)
      (CallFunction|EjectAll)
      (Actor|DestroyActor))
    (else
      (Transformation|SetActorLocation :NewLocation (Math|Vector|Lerp(Vector) s e a) :bSweep false :bTeleport false))))
