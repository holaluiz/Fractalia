# Plano de testes

Nenhum marco vira [DONE] sem os testes dele passarem. Resultado de cada rodada em §5.

---

## 1. Ferramentas que já existem

| Ferramenta | Uso |
|---|---|
| `Unreal/ue_py.py` | Roda Python no editor aberto |
| `Unreal/pie_combate.py` | Herói, magias, XP, baú, inventário, mutações no PIE |
| `Unreal/pie_creeps.py` | Acampamentos (aggro, corrente, morte, reaparecimento) |
| `Unreal/pie_gravar.py` | Gravação quadro a quadro (vida, posições, projéteis) |
| `Unreal/pie_state.py`, `pie_press.py` | Estado do PIE; injetar teclas pelo Enhanced Input |
| `Unreal/pie_capture.py`, `ue_capture.py --editor` | Capturas do jogo e da janela (com HUD) |
| `Unreal/ue_release.py` | Empacotar e publicar |

Pegadinhas de teste (memória de vídeo, 3 FPS em segundo plano, globais do Python remoto) no AGENTS.md §5.

## 2. Como testar rede neste PC

| Configuração | Como | Serve para |
|---|---|---|
| PIE listen + 1 cliente | Play com 2 jogadores, "Play As Listen Server", "Run Under One Process" | Replicação básica. **Arriscado** na RX 570 (memória de vídeo): editor recém-aberto, nada mais aberto |
| Host `-game` + clientes sem render | `UnrealEditor.exe <uproject> L_Island?listen -game -log` e `UnrealEditor.exe <uproject> 127.0.0.1 -game -nullrhi -nosound -log` | Vários clientes leves; teste de 20 com bots |
| Jogo empacotado | o build em `D:\NexusRoyale_Builds\<versão>\Windows` com `?listen` / `open <ip>` | Teste final, inclusive em outro PC da rede |
| Rede ruim | `NetEmulation.PktLag 150`, `NetEmulation.PktLoss 5` (console) ou as opções de emulação do PIE | Latência e perda |

Um script `Unreal/rede_testar.py` (M2) abre o host e N clientes sem render e junta os logs.

## 3. Testes de aceitação por marco

### M0.5 Estabilizar a 0.1.x
- [x] O `IMC_Default.uasset` no disco tem botão esquerdo, Q, E, X, F, 1–4 (conferido no arquivo, não só na memória). 15/10, 21:05.
- [~] No jogo empacotado (0.1.2, 22:21): todas as ações mapeadas (`showdebug enhancedinput`) e Q, E, X usados pelo
      usuário (log). Abrir baú, consumível e mutação: não vistos.
- [ ] Medição de desempenho do "depois" (PERFORMANCE.md §2).

### M1 Máquina de estados, morte e vitória
- [x] A partida passa por Espera → (Draft pulado) → Queda → EmJogo, com as fases no log e no HUD.
- [x] Modo treino (1 jogador): morrer → Final ("FIM DO TREINO") → Resultados → o mapa recomeça.
- [x] Com 2 jogadores (host + cliente): quando um morre, o outro vence; a vitória dispara uma vez só.
- [x] Eliminação: colocação certa, abate para o assassino, XP de abate pela fórmula (a do GDD v2, D-002m).
- [ ] Morto não recebe input (feito no `UNRCombateComponent`); **câmera passa para quem matou: sem verificar.**
- [x] No Final, ninguém toma dano (golpe de 100.000 no vencedor não fez nada).
- [x] Um cliente que desconecta na partida conta como eliminado ("Desconectou"); a contagem de vivos fica certa.
- [x] Quem entra com a partida em andamento vira espectador (sem herói, sem contar como vivo).
- [x] No recomeço com cliente conectado, todos vão juntos (`ServerTravel`) e a Espera aguarda o cliente.

### M2 Autoridade do loop atual (host + 1 cliente)
- [ ] O cliente vê o dirigível, embarca, salta (pedido ao servidor) e plana.
- [ ] O cliente abre um baú: o sorteio acontece no servidor; os dois veem os mesmos pickups.
- [ ] O cliente pega um item: o inventário dele muda; o host não pode ler o inventário do cliente pela UI.
- [ ] O cliente mata um creep (pelo host, até o M5): XP e nível do cliente certos; nível aparece no placar dos dois.
- [ ] Creep visto pelo cliente: anda, bate, morre com animação.
- [ ] **Um cliente não consegue** abrir baú longe, pegar item longe, saltar fora da ilha, nem se dar XP.
- [ ] A zona faz dano no cliente pelo servidor.

### M3 Sessões e menu
- [ ] Hospedar na LAN; outro processo acha a sala e entra.
- [ ] Entrar por IP direto.
- [ ] ESC abre o menu sem pausar; "Sair" do cliente volta ao menu; "Sair" do host avisa e encerra para todos.

### M4 Lobby de 20 e staging
- [ ] Todos veem as mesmas 20 vagas; o host adiciona/remove bot, expulsa, muda opções.
- [ ] "Começar" só com as 20 vagas preenchidas e todos prontos.
- [ ] Seamless travel para o mapa; todos nascem na Ilha de Espera; a fase espera todos carregarem (ou 60 s).
- [ ] Um bot ocupa uma vaga e entra na partida com PlayerState.

### M5 GAS
- [ ] As 4 habilidades portadas funcionam no host e no cliente, com custo, recarga e dano pelo servidor.
- [ ] **Um cliente não consegue** ativar habilidade sem mana, em recarga, ou que ele não tem.
- [ ] Efeitos visuais aparecem para todos (Gameplay Cues).

### M6 Draft
- [ ] **Dois jogadores não conseguem pegar a mesma habilidade** (inclusive pedindo no mesmo quadro).
- [ ] A escolha aparece travada para todos na hora.
- [ ] Tempo esgotado → o servidor escolhe; o draft nunca trava.
- [ ] Duração medida com 4 e com 20 (bots) dentro do alvo (BALANCE.md §3).
- [ ] As escolhas viram as habilidades do herói ao nascer.

### M7–M9 Armas, inventário, loot
- [ ] Disparo validado no servidor (cadência, munição, linha de visão); **um cliente não consegue** inventar dano.
- [ ] Inventário replica certo ao dono; trocar arma aparece na mão para todos.
- [ ] Morte solta a bolsa com tudo; outro jogador pega; os dois veem o mesmo conteúdo.

### M10–M13 Creeps, XP/atributos, queda, zona
- [ ] Acampamento dorme sem ninguém perto e acorda quando alguém chega.
- [ ] Pontos de atributo: só o servidor aplica; **um cliente não consegue** inventar ponto.
- [ ] Rota do dirigível muda a cada partida; salto só sobre a ilha.
- [ ] Dano da zona vem do servidor; o HUD mostra a fase certa no host e no cliente.

### M14–M16 Morte, bots, UI
- [ ] Espectador não recebe informação além do que o espectado vê.
- [ ] Resultados batem com a telemetria da partida.
- [ ] Bots obedecem às mesmas regras (sem mira perfeita, sem ver através de parede).
- [ ] Teclas remapeadas ficam salvas entre aberturas do jogo.

### M18 Estresse de 20
- [ ] 20 vagas (host + clientes sem render + bots) do lobby aos resultados, sem erro de Blueprint.
- [ ] Servidor dentro do orçamento (PERFORMANCE.md §3); banda medida.
- [ ] Com 150 ms e 5% de perda: jogável, sem dessincronizar inventário, draft ou vitória.

## 4. Regressão (a cada versão empacotada)

Abrir o jogo empacotado → menu → hospedar → partida com bots → queda → baú → creep → nível → zona → morte →
resultados. Conferir o log do jogo: sem "Accessed None", sem erro de Blueprint, sem material falhando no SM6.

## 5. Registro de testes

| Data | Marco | Teste | Resultado |
|---|---|---|---|
| 15/10 | (0.1.1, antes deste plano) | PIE e jogo empacotado (AGENTS.md, seção 9) | Passou, exceto as teclas no empacotado (bug 1.9) |
| 15/10 21:05 | M0.5 | `ue_mvp_setup.py` rodado; nomes das 9 ações procurados no `IMC_Default.uasset` | Passou (8,3 KB → 12,5 KB). Jogo empacotado: pendente |
| 15/10 21:08–21:13 | M1 | PIE solo + 2 bots de teste (`pie_partida.py`): Espera 3 s → Queda → EmJogo; bot 1 morto por mim (#3, +100 XP, nível 2); bot 2 morto sem assassino (#2) → vitória (#1); 100.000 de dano no Final sem efeito; Final 5 s → Resultados 15 s → recomeço; modo treino: morte → "FIM DO TREINO" → resultados. Capturas `Export/Previews/teste_m1_*.png` | Passou. Achado: causa "HeroBase" em vez de "Tempestade" (corrigido) |
| 15/10 21:26–21:34 | M1 | PIE listen server + 1 cliente `-nullrhi` (`rede_testar.py`): cliente entra em ~6 s; fases e morte chegam ao cliente; `ServerTravel ?Restart` leva o cliente junto | Passou. Achados: a Espera não aguardava o cliente no recomeço; cliente atrasado ganhava herói; o `ue_py.py` caía no cliente (os três corrigidos) |
| 15/10 21:52–21:57 | M1 | De novo, depois das correções: partida de 2 humanos (vitória do host, abate e XP); recomeço aguardando o cliente sozinho (7,3 s); cliente fechado na Queda → "Desconectou", vitória do host; cliente atrasado → espectador | Passou. Nenhum erro de Blueprint nos logs |
| 15/10 22:21 | M0.5 + M1 | 0.1.2 empacotada aberta com `-ExecCmds="showdebug enhancedinput"`, captura `Export/Previews/teste_012_empacotado_teclas.png`; o usuário jogou | Teclas mapeadas no jogo cozido; Muralha (E) e Chuva (X) lançadas pelo teclado; HUD "Treino"; fases no log |

