; One creep per CreepClasses entry, evenly spaced on a SpawnRadius circle around the camp, facing out
(fn SpawnCamp ()
  (Utilities|Array|Clear (Variables|Default|GetCreeps))
  (bind classes (Variables|Default|GetCreepClasses))
  (bind step (/ 360.0 (Math|Conversions|ToFloat(Integer) (Utilities|Array|Length classes))))
  (bind r (Variables|Default|GetSpawnRadius))
  (for cls classes
    (bind ang (* step (Math|Conversions|ToFloat(Integer) (Utilities|Array|Length (Variables|Default|GetCreeps)))))
    (bind off (Math|Vector|MakeVector :X (* (Math|Trig|Cos(Degrees) ang) r) :Y (* (Math|Trig|Sin(Degrees) ang) r) :Z 100.0))
    (bind rot (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw ang))
    (bind c (Game|SpawnActorfromClass :Class cls :SpawnTransform (Math|Transform|MakeTransform :Location (+ (Transformation|GetActorLocation) off) :Rotation rot) :CollisionHandlingOverride "AdjustIfPossibleButAlwaysSpawn"))
    (Utilities|Array|Add (Variables|Default|GetCreeps) c)))
