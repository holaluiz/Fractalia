; Every 1 s: once no creep is left alive, the camp drops its loot where a creep fell (DropLoot, GDD 12)
; and comes back RespawnDelay seconds later (GDD 12: 90 s small, 150 s medium)
(fn CheckCamp ()
  (if (not (Variables|Default|GetRespawnPending))
    (Variables|Default|SetAliveCount 0)
    (Variables|Default|SetDropLocation (Transformation|GetActorLocation))
    (for c (Variables|Default|GetCreeps)
      (Utilities|IsValid c
        (:"Is Valid"
          (if (Class|BPCreep|GetIsDead :self c)
            (Variables|Default|SetDropLocation (Transformation|GetActorLocation :self c))
            (else
              (Variables|Default|SetAliveCount (+ (Variables|Default|GetAliveCount) 1)))))
        (:"Is Not Valid")))
    (if (== (Variables|Default|GetAliveCount) 0)
      (Variables|Default|SetRespawnPending true)
      (CallFunction|DropLoot)
      (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "Respawn" :Time (Variables|Default|GetRespawnDelay) :bLooping false))))
