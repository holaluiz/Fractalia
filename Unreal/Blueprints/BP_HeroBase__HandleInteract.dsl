; F: interact with the chest/pickup in range. TODO(rede): virar RPC no servidor
(fn HandleInteract ()
  (bind it (Variables|Default|GetCurrentInteractable))
  (Utilities|IsValid it
    (:"Is Valid"
      (Class|BPInteractable|Interact :self it :Hero self))
    (:"Is Not Valid")))
