; Health hit 0: death pose (single-node anim holds the last frame), no more collision/movement, OnCreepKilled for XP
; (GDD 7.2: XP goes to whoever lands the last hit; Killer = the damage instigator's controller), gone after 3 s.
; BP_CreepCamp notices on its next check and starts the respawn timer.
(fn Die (Killer)
  (Variables|Default|SetIsDead true)
  (Variables|Default|SetMoving false)
  (Variables|Default|SetTarget)
  (Pawn|Components|CharacterMovement|DisableMovement :self (Variables|Character|GetCharacterMovement))
  (Collision|SetActorEnableCollision :bNewActorEnableCollision false)
  (Components|Animation|PlayAnimation :self (Variables|Character|GetMesh) :NewAnimToPlay (Variables|Default|GetDeathAnim) :bLooping false)
  (Nexus|Heroi|DarXP :QuemMatou Killer :Quantidade (Variables|Default|GetXPReward))
  (Default|CallOnCreepKilled :Killer Killer :XP (Variables|Default|GetXPReward))
  (Actor|SetLifeSpan :InLifespan 3.0))
