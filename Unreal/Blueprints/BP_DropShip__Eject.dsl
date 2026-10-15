; Drops the hero DropOffset cm below the hull
(fn Eject (Hero)
  (if (Utilities|Array|ContainsItem (Variables|Default|GetPassengers) Hero)
    (Utilities|Array|RemoveItem (Variables|Default|GetPassengers) Hero)
    (bind drop (- (Transformation|GetActorLocation) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z (Variables|Default|GetDropOffset))))
    (Class|BPHeroBase|ExitShip :self Hero :DropLocation drop)))
