; Jogador: posição (X = norte, Y = leste, cm) e yaw da câmera -> MPC_Mapa.Jogador
(fn AtualizarJogador ()
  (bind pawn (Game|GetPlayerPawn :PlayerIndex 0))
  (Utilities|IsValid pawn
    (:"Is Valid"
      (bind loc (Transformation|GetActorLocation :self pawn))
      ; GetControlRotation do CONTROLLER: o id da DSL cai nessa variante, e com o pawn ela inventava um LastHitBy (nulo)
      (bind rot (Pawn|GetControlRotation :self (Game|GetPlayerController :PlayerIndex 0)))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "Jogador"
        :ParameterValue (Utilities|Struct|MakeLinearColor :R (.x loc) :G (.y loc) :B (.yaw rot) :A 0.0)))
    (:"Is Not Valid")))
