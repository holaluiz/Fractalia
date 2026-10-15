; BP_CreepCamp: spawns its creeps when the match starts and checks every second whether the camp was cleared
(event EventBeginPlay
  (if (Networking|HasAuthority)
    (CallFunction|SpawnCamp)
    (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "CheckCamp" :Time 1.0 :bLooping true)))
