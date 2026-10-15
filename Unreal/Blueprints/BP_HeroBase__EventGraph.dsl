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

; TODO(GAS): hits from creeps (UE ApplyDamage) only add up in DamageTaken and print until AS_Hero exists
(event Game|Damage|EventAnyDamage (Damage DamageType InstigatedBy DamageCauser)
  (Variables|Default|SetDamageTaken (+ (Variables|Default|GetDamageTaken) Damage))
  (Development|PrintString :InString (Utilities|String|Append "Dano: -" (Utilities|String|ToString(Float) Damage)) :TextColor (Math|Color|MakeColor :R 1.0 :G 0.3 :B 0.2 :A 1.0) :Duration 1.0))
