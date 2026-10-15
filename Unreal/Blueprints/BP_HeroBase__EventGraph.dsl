; BP_HeroBase: remembers camera/movement defaults, runs the skydive while falling from the ship
(event EventBeginPlay
  (Variables|Default|SetDefaultCameraDistance (Class|SpringArmComponent|GetTargetArmLength :self (Variables|Camera|GetCameraBoom)))
  (bind cm (Variables|Character|GetCharacterMovement))
  (Variables|Default|SetDefaultGravityScale (Class|CharacterMovementComponent|GetGravityScale :self cm))
  (Variables|Default|SetDefaultAirControl (Class|CharacterMovementComponent|GetAirControl :self cm)))

(event EventTick (DeltaSeconds)
  (if (Variables|Default|GetSkydiving)
    (CallFunction|UpdateSkydive)))

(event EventOnLanded (Hit)
  (if (Variables|Default|GetSkydiving)
    (CallFunction|EndSkydive)))

; Total of UE ApplyDamage taken (tests read it). The real damage goes to the GAS through the Habilidades component.
(event Game|Damage|EventAnyDamage (Damage DamageType InstigatedBy DamageCauser)
  (Variables|Default|SetDamageTaken (+ (Variables|Default|GetDamageTaken) Damage)))
