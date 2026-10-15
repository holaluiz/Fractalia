; Todo tick: passa os valores globais para a MPC_Mapa (lida pelo M_UI_Mapa e suas instâncias).
; Dividido em três funções porque a DSL não continua o fluxo depois de um IsValid com ramos.
(fn Atualizar ()
  (CallFunction|AtualizarJogador)
  (CallFunction|AtualizarTempestade)
  (CallFunction|AtualizarRota))
