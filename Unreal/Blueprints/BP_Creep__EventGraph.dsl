; BP_Creep event graph: remembers the camp spot, thinks every 0.3 s on the server, steers toward MoveGoal, and reacts
; to damage (hit anim + the whole camp aggroes on the attacker) until Health reaches 0
(event EventBeginPlay
  (Variables|Default|SetHomeLocation (Transformation|GetActorLocation))
  (Variables|Default|SetHealth (Variables|Default|GetMaxHealth))
  (if (Networking|HasAuthority)
    (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "Think" :Time 0.3 :bLooping true)))

(event EventTick (DeltaSeconds)
  (if (and (Variables|Default|GetMoving) (not (Variables|Default|GetIsDead)))
    (bind d (- (Variables|Default|GetMoveGoal) (Transformation|GetActorLocation)))
    (bind flat (Math|Vector|MakeVector :X (.x d) :Y (.y d) :Z 0.0))
    (if (> (Math|Vector|VectorLength flat) (Variables|Default|GetStopDistance))
      (Pawn|Input|AddMovementInput :WorldDirection (Math|Vector|Normalize flat) :ScaleValue 1.0 :bForce false)
      (else
        (Variables|Default|SetMoving false)))))

; TODO(GAS): damage arrives through UE ApplyDamage for now; move to the AS_Hero/GE pipeline with the rest of combat
(event Game|Damage|EventAnyDamage (Damage DamageType InstigatedBy DamageCauser)
  (if (not (Variables|Default|GetIsDead))
    ; Compara com a vida JÁ gravada: "hp" é um nó puro e seria recalculado depois do SetHealth (vida nova - dano),
    ; o que matava o creep com qualquer golpe de metade da vida restante ou mais.
    (Variables|Default|SetHealth (- (Variables|Default|GetHealth) Damage))
    (if (<= (Variables|Default|GetHealth) 0.0)
      (CallFunction|Die :Killer InstigatedBy)
      (else
        (bind anim (Components|SkeletalMesh|GetAnimInstance :self (Variables|Character|GetMesh)))
        (Animation|Montage|PlaySlotAnimationasDynamicMontage :self anim :Asset (Variables|Default|GetHitAnim) :SlotNodeName "DefaultSlot")
        (Utilities|IsValid InstigatedBy
          (:"Is Valid"
            (bind attacker (Pawn|GetControlledPawn :self InstigatedBy))
            (for c (Actor|GetAllActorsOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Creeps/BP_Creep.BP_Creep_C")
              (if (< (Math|Vector|Distance(Vector) :V1 (Transformation|GetActorLocation :self c) :V2 (Variables|Default|GetHomeLocation)) 1000.0)
                (CallFunction|Alert :self c :Attacker attacker))))
          (:"Is Not Valid"))))))
