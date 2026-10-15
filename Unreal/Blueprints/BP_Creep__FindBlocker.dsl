; BlockingStructure = the spell structure (Ice Wall: NREstruturaMagica) between this creep and TargetLocation that the
; creep is pressed against, or none. Checked in the structure's local space (X = thickness, Y = width), so any size
; and rotation works: within its capsule radius + 40 cm of a face, inside the width, and on the other side from the
; target. Creeps walk in a straight line (no NavMesh), so without this they would push the wall until it melts.
(fn FindBlocker (TargetLocation)
  (Variables|Default|SetBlockingStructure)
  (bind myLoc (Transformation|GetActorLocation))
  (bind reach (+ (Components|Capsule|GetScaledCapsuleRadius :self (Variables|Character|GetCapsuleComponent)) 40.0))
  (for s (Actor|GetAllActorsOfClass :ActorClass "/Script/NexusRoyale.NREstruturaMagica")
    (bind xf (Transformation|GetActorTransform :self s))
    (bind me (Math|Transform|InverseTransformLocation :T xf :Location myLoc))
    (bind it (Math|Transform|InverseTransformLocation :T xf :Location TargetLocation))
    (bind ext (Components|Box|GetScaledBoxExtent :self (Class|NREstruturaMagica|GetCaixa :self s)))
    (if (and (not (Nexus|Estrutura|EstaDesfazendo :self s))
             (and (< (Math|Float|Absolute(Float) :A (.x me)) (+ (.x ext) reach))
                  (and (< (Math|Float|Absolute(Float) :A (.y me)) (+ (.y ext) reach))
                       (< (* (.x me) (.x it)) 0.0))))
      (Variables|Default|SetBlockingStructure s))))
