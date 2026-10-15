; F: interact with the chest/pickup in range. TODO(rede): virar RPC no servidor
; Sem alvo atual (o último pickup sumiu e os vizinhos já estavam sobrepostos, sem nova entrada): pega um sobreposto.
(fn HandleInteract ()
  (bind it (Variables|Default|GetCurrentInteractable))
  (Utilities|IsValid it
    (:"Is Valid"
      (Class|BPInteractable|Interact :self it :Hero self))
    (:"Is Not Valid"
      (CallFunction|InteractNearby))))
