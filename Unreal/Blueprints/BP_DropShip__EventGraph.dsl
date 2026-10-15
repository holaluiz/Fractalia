(event EventTick (DeltaSeconds)
  (if (Variables|Default|GetFlying)
    (CallFunction|FlyTick)))
