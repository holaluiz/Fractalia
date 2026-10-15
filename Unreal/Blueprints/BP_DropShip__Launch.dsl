; Server: fly from Start to End at Speed (cm/s); passengers ride along attached
(fn Launch (Start End)
  (Variables|Default|SetStartPoint Start)
  (Variables|Default|SetEndPoint End)
  (Variables|Default|SetLaunchTime (GameState|GetServerWorldTimeSeconds :self (Game|GetGameState)))
  (bind rot (Math|Rotator|FindLookatRotation :Start Start :Target End))
  (Transformation|SetActorLocationAndRotation :NewLocation Start :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (.yaw rot)) :bSweep false :bTeleport true)
  (Variables|Default|SetFlying true))
