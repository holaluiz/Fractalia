; Landed: back to normal movement
(fn EndSkydive ()
  (bind cm (Variables|Character|GetCharacterMovement))
  (Class|CharacterMovementComponent|SetGravityScale :self cm :GravityScale (Variables|Default|GetDefaultGravityScale))
  (Class|CharacterMovementComponent|SetAirControl :self cm :AirControl (Variables|Default|GetDefaultAirControl))
  (Variables|Default|SetSkydiving false))
