; Server: fires OnPhaseEnded (with the level floor from CT_Storm) and OnPhaseStarted when the phase changes.
; The level floor (GDD 7.3) is applied right here: every hero below it goes up to it (UNRAbilitySystemComponent).
(fn CheckPhaseEvents ()
  (bind p (Variables|Default|GetCurPhase))
  (bind last (Variables|Default|GetLastPhase))
  (if (!= p last)
    (if (> last 0)
      (bind floor (CallFunction|StormValue :Row "LevelFloor" :Phase last))
      (Nexus|Heroi|AplicarPisoDeNivel :Piso (Math|Float|Truncate floor))
      (Default|CallOnPhaseEnded :Phase last :LevelFloor (Math|Float|Truncate floor)))
    (if (<= p 6)
      (Default|CallOnPhaseStarted :Phase p))
    (Variables|Default|SetLastPhase p)))
