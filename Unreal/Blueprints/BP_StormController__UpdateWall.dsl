; SM_StormWall is a 1 m radius x 1 m tall cylinder: XY scale = radius in metres
(fn UpdateWall ()
  (bind c (Variables|Default|GetCurCenter))
  (bind r (Variables|Default|GetCurRadius))
  (Transformation|SetActorLocation :NewLocation (Math|Vector|MakeVector :X (.x c) :Y (.y c) :Z (Variables|Default|GetWallBaseZ)) :bSweep false :bTeleport true)
  (bind sc (Math|Float|Max(Float) (/ r 100.0) 0.01))
  (Transformation|SetRelativeScale3D :self (Variables|Default|GetWall) :NewScale3D (Math|Vector|MakeVector :X sc :Y sc :Z (Variables|Default|GetWallHeightScale))))
