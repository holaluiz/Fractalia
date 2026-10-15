; Tempestade: círculo atual (CurCenter/CurRadius) e o próximo (Centers[fase], raio da fase em CT_Storm) -> MPC_Mapa
(fn AtualizarTempestade ()
  (bind storm (Actor|GetActorOfClass :ActorClass "/Game/NexusRoyale/Blueprints/Match/BP_StormController.BP_StormController_C"))
  (Utilities|IsValid storm
    (:"Is Valid"
      (bind c (Class|BPStormController|GetCurCenter :self storm))
      (Rendering|Material|SetVectorParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "Tempestade"
        :ParameterValue (Utilities|Struct|MakeLinearColor :R (.x c) :G (.y c) :B (Class|BPStormController|GetCurRadius :self storm) :A 0.0))
      (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "TempestadeLigada" :ParameterValue 1.0)
      (bind fase (Class|BPStormController|GetCurPhase :self storm))
      (bind centros (Class|BPStormController|GetCenters :self storm))
      (if (and (> fase 0) (< fase (Utilities|Array|Length centros)))
        (bind cn (Utilities|Array|Get(acopy) centros fase))
        (bind rn (Class|BPStormController|StormValue :self storm :Row "Radius" :Phase fase))
        (Rendering|Material|SetVectorParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "Proxima"
          :ParameterValue (Utilities|Struct|MakeLinearColor :R (.x cn) :G (.y cn) :B (* rn 100.0) :A 0.0))
        (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "ProximaLigada" :ParameterValue 1.0)
        (else
          (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "ProximaLigada" :ParameterValue 0.0))))
    (:"Is Not Valid"
      (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "TempestadeLigada" :ParameterValue 0.0)
      (Rendering|Material|SetScalarParameterValue :Collection "/Game/NexusRoyale/UI/Mapa/MPC_Mapa.MPC_Mapa" :ParameterName "ProximaLigada" :ParameterValue 0.0))))
