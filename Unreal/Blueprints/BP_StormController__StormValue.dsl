; Reads one value of CT_Storm (row = ShrinkStart/ShrinkEnd/Radius/DamagePct/LevelFloor, key = phase 0..6)
(fn StormValue (Row Phase)
  (DataTable|EvaluateCurveTableRow :CurveTable (Variables|Default|GetStormTable) :RowName Row :InXY Phase
    (:RowFound
      (return _outxy))
    (:RowNotFound
      (return 0.0))))
