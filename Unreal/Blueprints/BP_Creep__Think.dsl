; BP_Creep.Think: every 0.3 s on the server (timer from BeginPlay). With a target: drop it once it is LeashRadius from the
; camp (GDD 12: 15 m), hit it inside AttackRange (UE ApplyDamage until GAS) or chase it. Without one: walk home and take
; the first hero inside AggroRadius. EventTick steers toward MoveGoal (no NavMesh needed inside the leash).
; Pure IsValid is not reachable from the DSL ("Utilities|IsValid" is the exec macro), hence the continuations.
(fn Think ()
  (if (not (Variables|Default|GetIsDead))
    (bind home (Variables|Default|GetHomeLocation))
    (bind myLoc (Transformation|GetActorLocation))
    (bind t (Variables|Default|GetTarget))
    (Utilities|IsValid t
      (:"Is Valid"
        (bind tLoc (Transformation|GetActorLocation :self t))
        (if (> (Math|Vector|Distance(Vector) :V1 tLoc :V2 home) (Variables|Default|GetLeashRadius))
          (CallFunction|ResetLeash)
          (elif (< (Math|Vector|Distance(Vector) :V1 tLoc :V2 myLoc) (Variables|Default|GetAttackRange))
            (Variables|Default|SetMoving false)
            (bind look (Math|Rotator|FindLookatRotation :Start myLoc :Target tLoc))
            (Transformation|SetActorRotation :NewRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (.yaw look)) :bTeleportPhysics false)
            (bind now (Utilities|Time|GetGameTimeinSeconds))
            (if (> (- now (Variables|Default|GetLastAttackTime)) (Variables|Default|GetAttackCooldown))
              (Variables|Default|SetLastAttackTime now)
              (bind anim (Components|SkeletalMesh|GetAnimInstance :self (Variables|Character|GetMesh)))
              (Animation|Montage|PlaySlotAnimationasDynamicMontage :self anim :Asset (Variables|Default|GetAttackAnim) :SlotNodeName "DefaultSlot")
              (Game|Damage|ApplyDamage :DamagedActor t :BaseDamage (Variables|Default|GetAttackDamage) :EventInstigator (Pawn|GetController) :DamageCauser self))
            (else
              (Variables|Default|SetMoveGoal tLoc)
              (Variables|Default|SetStopDistance (* (Variables|Default|GetAttackRange) 0.8))
              (Variables|Default|SetMoving true)))))
      (:"Is Not Valid"
        (Variables|Default|SetMoveGoal home)
        (Variables|Default|SetStopDistance 60.0)
        (Variables|Default|SetMoving (> (Math|Vector|Distance2D(Vector) :V1 myLoc :V2 home) 60.0))
        (for h (Actor|GetAllActorsOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase.BP_HeroBase_C")
          (if (< (Math|Vector|Distance(Vector) :V1 (Transformation|GetActorLocation :self h) :V2 myLoc) (Variables|Default|GetAggroRadius))
            (Variables|Default|SetTarget h)))))))
