; Item da tabela DT_Itens: a malha e o nome vêm do ItemId. Kind: 0 equipamento, 1 grimório, 2 consumível
(fn SetupItem (InItemId InKind InRarity)
  (Variables|Default|SetItemId InItemId)
  (bind dt (Nexus|Itens|TabelaPadrao))
  (bind mesh (Nexus|Itens|CarregarMalha :Tabela dt :ItemId InItemId))
  (CallFunction|Setup :Mesh mesh :Label (Utilities|String|ToString(Text) (Nexus|Itens|NomeDoItem :Tabela dt :ItemId InItemId)) :InKind InKind :InRarity InRarity))
