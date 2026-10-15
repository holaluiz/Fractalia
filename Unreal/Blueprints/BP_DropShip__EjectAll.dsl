; End of the route: everyone still aboard is dropped
(fn EjectAll ()
  (while (> (Utilities|Array|Length (Variables|Default|GetPassengers)) 0)
    (CallFunction|Eject :Hero (Utilities|Array|Get(acopy) (Variables|Default|GetPassengers) 0))))
