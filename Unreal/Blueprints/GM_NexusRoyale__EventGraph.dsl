; GM_NexusRoyale (filho do ANRGameMode, C++). A máquina de estados da partida (Docs/Game/GAMEPLAY_SYSTEMS.md §1)
; decide QUANDO a queda começa e chama IniciarQueda; este grafo só faz o "como": um dirigível cruza a ilha numa reta
; sorteada com todos os heróis a bordo, e o relógio da tempestade começa (GDD 3 e 13). Roda só no servidor.
; Antes do M1 o BeginPlay disparava a partida por um timer de 0,5 s (evento StartMatch). Os dois foram apagados com
; Unreal/ue_bp_apagar_cadeia.py: gravar um evento com corpo vazio pela DSL não apaga o corpo antigo.

(event Nexus|Partida|EventIniciarQueda
  (bind storm (Actor|GetActorOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Match/BP_StormController.BP_StormController_C"))
  (bind ang (Math|Random|RandomFloatinRange :Min 0.0 :Max 360.0))
  (bind cs (Math|Trig|Cos(Degrees) ang))
  (bind sn (Math|Trig|Sin(Degrees) ang))
  (bind dir (Math|Vector|MakeVector :X cs :Y sn :Z 0.0))
  (bind side (Math|Vector|MakeVector :X (- sn) :Y cs :Z 0.0))
  (bind spread (Variables|Default|GetShipLateralSpread))
  (bind lat (Math|Random|RandomFloatinRange :Min (- spread) :Max spread))
  (bind mid (+ (* side lat) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z (Variables|Default|GetShipAltitude))))
  (bind half (* dir (Variables|Default|GetShipPathHalfLength)))
  (bind start (- mid half))
  (bind end (+ mid half))
  (bind ship (Game|SpawnActorfromClass :Class "/Game/NexusRoyale/Blueprints/Match/BP_DropShip.BP_DropShip_C" :SpawnTransform (Math|Transform|MakeTransform :Location start) :CollisionHandlingOverride "AlwaysSpawn"))
  (Class|BPDropShip|Launch :self ship :Start start :End end)
  (bind heroes (Actor|GetAllActorsOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase.BP_HeroBase_C"))
  (for h heroes
    (Class|BPDropShip|Board :self ship :Hero h))
  (Utilities|IsValid storm
    (:"Is Valid"
      (Class|BPStormController|StartStorm :self storm))
    (:"Is Not Valid")))
