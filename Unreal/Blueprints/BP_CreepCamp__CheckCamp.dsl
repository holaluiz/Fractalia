; Every 1 s: once no creep is left alive, the camp comes back RespawnDelay seconds later (GDD 12: 90 s for small camps)
(fn CheckCamp ()
  (if (not (Variables|Default|GetRespawnPending))
    (Variables|Default|SetAliveCount 0)
    (for c (Variables|Default|GetCreeps)
      (Utilities|IsValid c
        (:"Is Valid"
          (if (not (Class|BPCreep|GetIsDead :self c))
            (Variables|Default|SetAliveCount (+ (Variables|Default|GetAliveCount) 1))))
        (:"Is Not Valid")))
    (if (== (Variables|Default|GetAliveCount) 0)
      (Variables|Default|SetRespawnPending true)
      (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "Respawn" :Time (Variables|Default|GetRespawnDelay) :bLooping false))))
