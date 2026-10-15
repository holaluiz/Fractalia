; GM_NexusRoyale: when the match starts, a drop ship crosses the island on a random line with every hero aboard,
; and the storm clock starts (GDD 3 and 13)
(event EventBeginPlay
  (if (Networking|HasAuthority)
    (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "StartMatch" :Time 0.5 :bLooping false)))

(event Custom|StartMatch
  (bind storm (Actor|GetActorOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Match/BP_StormController.BP_StormController_C"))
  (bind ang (Math|Random|RandomFloatinRange :Min 0.0 :Max 360.0))
  (bind cs (Math|Trig|Cos(Degrees) ang))
  (bind sn (Math|Trig|Sin(Degrees) ang))
  (bind dir (Math|Vector|MakeVector :X cs :Y sn :Z 0.0))
  (bind side (Math|Vector|MakeVector :X (- sn) :Y cs :Z 0.0))
  (bind spread (Variables|Default|GetShipLateralSpread))
  (bind lat (Math|Random|RandomFloatinRange :Min (- spread) :Max spread))
  (bind mid (+ (* side lat) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z (Variables|Default|GetShipAltitude))))
  (bind half (* dir (Variables|Default|GetShipPathHalfLength)))
  (bind start (- mid half))
  (bind end (+ mid half))
  (bind ship (Game|SpawnActorfromClass :Class "/Game/NexusRoyale/Blueprints/Match/BP_DropShip.BP_DropShip_C" :SpawnTransform (Math|Transform|MakeTransform :Location start) :CollisionHandlingOverride "AlwaysSpawn"))
  (Class|BPDropShip|Launch :self ship :Start start :End end)
  (bind heroes (Actor|GetAllActorsOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase.BP_HeroBase_C"))
  (for h heroes
    (Class|BPDropShip|Board :self ship :Hero h))
  (Utilities|IsValid storm
    (:"Is Valid"
      (Class|BPStormController|StartStorm :self storm))
    (:"Is Not Valid")))
