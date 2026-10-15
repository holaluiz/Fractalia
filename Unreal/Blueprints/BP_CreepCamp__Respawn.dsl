; Respawn timer fired: the camp is back
(fn Respawn ()
  (Variables|Default|SetRespawnPending false)
  (CallFunction|SpawnCamp))
