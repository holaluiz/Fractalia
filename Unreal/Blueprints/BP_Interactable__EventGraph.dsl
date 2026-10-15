; Base of everything the hero can use with F: tells the hero when it enters/leaves the sphere
(event Collision|EventActorBeginOverlap (OtherActor)
  (bind hero (Utilities|Casting|CastToBP_HeroBase :Object OtherActor)
    (:then
      (Class|BPHeroBase|SetInteractable :self hero :Target self))
    (:CastFailed)))

(event Collision|EventActorEndOverlap (OtherActor)
  (bind hero (Utilities|Casting|CastToBP_HeroBase :Object OtherActor)
    (:then
      (Class|BPHeroBase|ClearInteractable :self hero :Target self))
    (:CastFailed)))
