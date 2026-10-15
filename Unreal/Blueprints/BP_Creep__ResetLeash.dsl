; The target left the leash (GDD 12: 15 m from the camp): drop it, heal to full and walk home
(fn ResetLeash ()
  (Variables|Default|SetTarget)
  (Variables|Default|SetHealth (Variables|Default|GetMaxHealth))
  (Variables|Default|SetMoveGoal (Variables|Default|GetHomeLocation))
  (Variables|Default|SetStopDistance 60.0)
  (Variables|Default|SetMoving true))
