; Com o mapa em tela cheia aberto, o minimapa some (como no Fortnite)
(fn MostrarCompleto (Mostrar)
  (Variables|Default|SetAberto Mostrar)
  (if Mostrar
    (Class|Widget|SetVisibility :self (Variables|Default|GetCompleto) :Visibility "HitTestInvisible")
    (Class|Widget|SetVisibility :self (Variables|Default|GetMini) :Visibility "Collapsed")
    (else
      (Class|Widget|SetVisibility :self (Variables|Default|GetCompleto) :Visibility "Collapsed")
      (Class|Widget|SetVisibility :self (Variables|Default|GetMini) :Visibility "HitTestInvisible"))))
