; Rota do dirigível (BP_DropShip StartPoint -> EndPoint) enquanto ele existir -> MPC_Mapa.RotaInicio, RotaFim e RotaLigada
(fn AtualizarRota ()
  (bind ship (Actor|GetActorOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Match/BP_DropShip.BP_DropShip_C"))
  (Utilities|IsValid ship
    (:"Is Valid"
      (bind a (Class|BPDropShip|GetStartPoint :self ship))
      (bind e (Class|BPDropShip|GetEndPoint :self ship))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "RotaInicio"
        :ParameterValue (Utilities|Struct|MakeLinearColor :R (.x a) :G (.y a) :B 0.0 :A 0.0))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "RotaFim"
        :ParameterValue (Utilities|Struct|MakeLinearColor :R (.x e) :G (.y e) :B 0.0 :A 0.0))
      (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "RotaLigada" :ParameterValue 1.0))
    (:"Is Not Valid"
      (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "RotaLigada" :ParameterValue 0.0))))
