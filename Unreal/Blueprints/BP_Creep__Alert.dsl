; A camp mate was hit: an idle creep takes the attacker as its target
(fn Alert (Attacker)
  (if (not (Variables|Default|GetIsDead))
    (Utilities|IsValid (Variables|Default|GetTarget)
      (:"Is Valid")
      (:"Is Not Valid"
        (Variables|Default|SetTarget Attacker)))))
