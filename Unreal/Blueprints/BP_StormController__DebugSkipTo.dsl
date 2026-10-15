; Test helper: jumps the storm clock to Seconds after the start (e.g. 200 = phase 1 closing)
(fn DebugSkipTo (Seconds)
  (Variables|Default|SetStartTime (- (CallFunction|ServerTime) Seconds)))
