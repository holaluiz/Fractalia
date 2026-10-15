; 0 Comum, 1 Incomum, 2 Raro, 3 Epico, 4 Lendario. Common chest: Comum-Raro; golden: Raro-Epico, 5% Lendario (GDD 8.4)
(fn RollRarity ()
  (bind r (Math|Random|RandomFloat))
  (if (Variables|Default|GetGolden)
    (return (select (< r 0.05) 4 (select (< r 0.45) 3 2)))
    (else
      (return (select (< r 0.6) 0 (select (< r 0.9) 1 2))))))
