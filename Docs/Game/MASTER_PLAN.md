# MASTER_PLAN: plano central do Nexus Royale

> **Documento de controle.** Status de cada marco: `[TODO]` `[IN PROGRESS]` `[BLOCKED]` `[TESTING]` `[DONE]`.
> Nenhum marco vira `[DONE]` sem os testes do [TEST_PLAN.md](TEST_PLAN.md) passarem.
>
> **Ao terminar uma tarefa:** (1) atualize este arquivo; (2) atualize o documento do assunto; (3) entrada no
> [CHANGELOG_AI.md](CHANGELOG_AI.md); (4) decisão nova no [DECISIONS.md](DECISIONS.md); (5) problema aberto no
> [KNOWN_ISSUES.md](KNOWN_ISSUES.md); (6) diga quais arquivos e assets mudaram; (7) como foi testado; (8) a próxima ação.
> E siga também o [AGENTS.md](../../AGENTS.md) (seção 3 e diário da seção 9).

Criado em 2026-10-15 (Marco 0). Substitui o [PLANO.md](../../PLANO.md) como plano central (D-001).

---

## Agora

- **Feito em 15/10 (noite):** M0 (auditoria e documentos); M0.5 corrigido no projeto (teclas salvas no `IMC_Default`,
  conferido no arquivo); M1 implementado e testado em PIE (solo, com bots e em rede com um cliente sem render).
- **Próxima ação:** M2 (autoridade do loop atual: interação, salto, loot, inventário, creeps).
- **Decidido pelo usuário em 15/10, 22:30:** D-002 (GDD v3 aprovado como proposto) e D-007 (serpente em 4 faixas).
  M6–M9 e M11 deixaram de estar bloqueados. A 0.1.2 foi publicada (Release `v0.1.2`, tag no `cbc9739`).
- **Esperando o usuário:** importar o Landscape do `L_Ilha` (bloqueia M17).

## Documentos

| Documento | Assunto |
|---|---|
| [AUDITORIA.md](AUDITORIA.md) | Foto do projeto em 15/10: o que existe, funciona, quebrou e falta |
| [GAME_DESIGN_DOCUMENT.md](GAME_DESIGN_DOCUMENT.md) | Design v3 (**oficial** desde 15/10, 22:30) |
| [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) | Classes alvo, dados, migração |
| [NETWORKING_ARCHITECTURE.md](NETWORKING_ARCHITECTURE.md) | Autoridade, replicação, sessões, listen × dedicado |
| [GAMEPLAY_SYSTEMS.md](GAMEPLAY_SYSTEMS.md) | Máquina de estados, morte, XP, zona, queda, loot, creeps |
| [ABILITY_SYSTEM.md](ABILITY_SYSTEM.md) | GAS, habilidades por dados, tags, draft |
| [ITEM_AND_LOOT_SYSTEM.md](ITEM_AND_LOOT_SYSTEM.md) | Armas, 6 slots, loot, bolsa |
| [AI_AND_BOTS.md](AI_AND_BOTS.md) | Creeps e bots |
| [ART_DIRECTION.md](ART_DIRECTION.md) | Pintado/aquarela, materiais, luz, legibilidade |
| [MAP_DESIGN.md](MAP_DESIGN.md) | Mapas, distâncias, graybox, métricas |
| [UI_UX.md](UI_UX.md) | Telas, HUD, teclas, ESC |
| [BALANCE.md](BALANCE.md) | Fórmulas, simulação do draft, armas, monitor anti-bola-de-neve |
| [PERFORMANCE.md](PERFORMANCE.md) | Máquina de referência, orçamentos, medições |
| [TEST_PLAN.md](TEST_PLAN.md) | Como testar rede neste PC; aceite por marco |
| [DECISIONS.md](DECISIONS.md) | Decisões D-001… |
| [CHANGELOG_AI.md](CHANGELOG_AI.md) | O que cada IA mudou |
| [KNOWN_ISSUES.md](KNOWN_ISSUES.md) | Problemas abertos |

## Ordem de execução

A lista do pedido foi reordenada (D-011): o que já existe em versão solo vira "adaptar e pôr em rede", e a fundação
de rede vem antes do conteúdo.

```
Fase A · Fundação (não depende de D-002)
  M0 Auditoria ✔ → M0.5 Estabilizar 0.1.x → M1 Estados/morte/vitória → M2 Autoridade do loop atual
  → M3 Sessões e menu → M4 Lobby de 20 + staging → M5 GAS (portar as 4 magias)
Fase B · Fatia vertical (D-002 e D-007 aceitas)
  M6 Draft → M7/M8 Combate com armas → M9 Inventário e loot → M10 Creeps → M11 XP e atributos
  → M12 Queda → M13 Zona → M14 Morte/espectador/resultados → M15 Bots (fases 1–3) → M16 UI e configurações
  → ★ FATIA VERTICAL
Fase C · Escala
  M17 Graybox do mapa v2 → M18 Estresse de 20 → M23 Rede → M24 Desempenho → M19 Pipeline pintado
  → M20 Ambiente → M21 Conteúdo (128 habilidades…) → M22 Balanceamento → M25 Teste externo
```

## ★ Fatia vertical (o menor jogo que prova o loop)

**Uma partida de 4 vagas** no `L_Island` (a ilha de 400 m tem o tamanho certo para 4), do menu aos resultados:

| Peça | Mínimo |
|---|---|
| Rede | Host (listen) + 1 cliente + 2 bots |
| Lobby | 4 vagas na configuração de desenvolvimento (o normal é 20) |
| Staging | Ilha de Espera; espera todos carregarem |
| Draft | Formato A, **1 ultimate + 2 básicas** por jogador; pool de 10 básicas + 5 ultimates (fator 1,25) |
| Habilidades | as 15 do pool, sobre 5–6 comportamentos genéricos |
| Armas | 4: Espada, Bacamarte, Arco, Cajado Arcano |
| Itens | ~10: passivos do v2, 3 consumíveis, 1 ativo, Tomo |
| Mundo | baús por tabela de loot, acampamentos pequenos e médios, dirigível, zona |
| Progressão | XP, níveis, pontos de atributo, mutações nos níveis marcados |
| Fim | morte com bolsa de loot, espectador, último vivo vence, resultados |

**Aceite:** uma partida inteira com essas peças, sem erro de Blueprint, em que um cliente não consegue trapacear
(TEST_PLAN.md, M1–M16), e um playtest respondendo às perguntas de diversão (GAME_DESIGN_DOCUMENT.md §19).

---

## Marcos

### M0 · Auditoria do projeto · [DONE]
- **Objetivo:** entender o que existe antes de mudar.
- **Feito:** [AUDITORIA.md](AUDITORIA.md); documentos desta pasta; decisões D-001 a D-014; simulação do draft.
- **Testado:** conferido contra o código, as DSLs e os scripts. **Limite:** o editor não foi aberto.

### M0.5 · Estabilizar a 0.1.x · [DONE]
- **Feito (15/10, 21:05):** `ue_mvp_setup.py` marca o IMC (`modify()`), salva com `only_if_is_dirty=False` e confere o
  arquivo no disco (falha se faltar ação). O `IMC_Default.uasset` passou de 8,3 KB (11:38) para 12,5 KB e tem as 9 ações.
  Versão 0.1.2 gravada no `DefaultGame.ini`.
- **Jogo empacotado 0.1.2 (22:21):** cook com "0 error(s), 0 warning(s)"; o painel `showdebug enhancedinput` lista todas as
  ações do `IMC_Default`; o usuário jogou e o log mostra Muralha de Gelo (E), Chuva de Meteoros (X) e a Bola de Fogo (Q)
  em recarga. A partida passou por Espera → Queda → Partida (modo treino).
- **Publicada** em 15/10, 22:38: Release `v0.1.2` com a tag no commit `cbc9739` (o do build). Abrir baú, consumível e
  mutação no empacotado não foram vistos no log, mas as teclas deles estão no mapeamento cozido.
- **Objetivo:** o jogo publicado volta a ter combate.
- **Depende de:** nada.
- **Tarefas:** corrigir o `ue_mvp_setup.py` (marcar o IMC, salvar sem `only_if_is_dirty`); rodar com o editor aberto;
  **conferir o `.uasset` no disco**; testar no jogo empacotado; medir o desempenho do "depois"; publicar a 0.1.2
  (**com o OK do usuário**), com a tag no commit certo.
- **Arquivos:** `Unreal/ue_mvp_setup.py`, `Content/Input/IMC_Default.uasset`, `DefaultGame.ini` (versão).
- **Multiplayer:** —
- **Aceite:** TEST_PLAN.md, M0.5.
- **Riscos:** o cook leva ~15 min; o PC fica ocupado.

### M1 · Arquitetura central: estados da partida, morte e vitória · [TESTING]
- **Feito (15/10, 20:00–22:05):** `Core/` (`ANRGameMode`, `ANRGameState`, `ANRPlayerState`, `NRTiposPartida.h`,
  `UNRSessaoSubsystem`), `AI/ANRBotController` (bot que ocupa vaga); morte, nível e XP replicados no ASC; aviso nativo de
  morte para o GameMode; invulnerabilidade no Final; HUD com a linha da partida, eliminação, vitória e resultados;
  `GM_NexusRoyale` filho do `ANRGameMode` (o `StartMatch` virou o `IniciarQueda`); GameMode global do projeto trocado.
  Quem entra com a partida em andamento assiste; num recomeço, a Espera aguarda os humanos da partida anterior.
- **Testado** (TEST_PLAN.md §5): fases no log e no HUD; modo treino (morte → Final → Resultados → recomeço); bots de
  teste com abate, XP e vitória; invulnerabilidade no Final; em rede (PIE listen + cliente `-nullrhi`): fases e morte
  chegando ao cliente, vitória do host, recomeço com o cliente junto (`ServerTravel`), Espera aguardando o cliente,
  eliminação por desconexão, cliente atrasado virando espectador.
- **Falta ver:** a câmera indo para quem matou; o HUD do lado do cliente (o cliente de teste não tem render); a câmera
  do espectador atrasado; a contagem de espectadores no recomeço (compilada, não testada); a partida no jogo empacotado.
- **Objetivo:** a partida vira uma máquina de estados explícita no servidor (D-004), com eliminação e último vivo.
- **Depende de:** M0.5 (para não empacotar com o IMC quebrado).
- **Tarefas:**
  - C++: `ANRGameMode`, `ANRGameState`, `ANRPlayerState`, `ANRPlayerController` (`Core/`);
  - fases Espera → Draft (pulada até o M6) → Queda → EmJogo → Final → Resultados;
  - eliminação no servidor (colocação, abate, XP de abate pela fórmula do BALANCE.md §4), modo treino com 1 jogador;
  - morte sem `OpenLevel`; câmera em quem matou; combate congelado no Final;
  - `GM_NexusRoyale` vira filho do `ANRGameMode`; o `StartMatch` vira a entrada na Queda; GameMode global do projeto;
  - HUD: fase, vivos, "VITÓRIA" / "#N de M", tempo até os resultados.
- **Arquivos:** `Source/NexusRoyale/Core/*` (novos), `GAS/NRAbilitySystemComponent.*` (aviso de morte para o
  GameMode), `Combat/NRCombateComponent.*` (sem recomeçar sozinho), `UI/NRHudWidget.*`, `GM_NexusRoyale`
  (reparent + DSL), `DefaultEngine.ini`.
- **Multiplayer:** tudo no servidor; GameState e PlayerState replicam; os vivos vêm dos PlayerStates.
- **Aceite:** TEST_PLAN.md, M1.
- **Riscos:** o reparent do BP; compilar no HD lento; testar 2 jogadores na RX 570 (usar cliente `-nullrhi`).

### M2 · Autoridade do loop atual · [TODO]
- **Objetivo:** tudo o que já existe (menos o combate, D-014) passa pelo servidor e funciona com host + 1 cliente.
- **Depende de:** M1.
- **Tarefas:** `Server_Interagir`, `Server_Saltar`; sorteio de loot no servidor; inventário replicado (dono);
  XP/nível espelhados no PlayerState; vida e morte dos creeps replicadas; HUD lendo dados replicados (interface
  `INRZona`); script `Unreal/rede_testar.py` (host + clientes sem render).
- **Arquivos:** `BP_HeroBase` (DSLs `HandleInteract`, `HandleJumpStarted`), `ANRPlayerController`,
  `UNRInventoryComponent`, `BP_Creep`, `BP_LootChest`, `UNRHudWidget`, `BP_StormController`.
- **Multiplayer:** é o marco.
- **Aceite:** TEST_PLAN.md, M2.
- **Riscos:** descobrir dependências escondidas do input local nos Blueprints.

### M3 · Sessões, menu e ESC · [TODO]
- **Objetivo:** hospedar e entrar (LAN e IP direto); menu principal; ESC sem pausa.
- **Depende de:** M2.
- **Tarefas:** `UNRSessaoSubsystem` (OSS Null), plugin Online Subsystem Null; `L_Menu`; telas Menu, Hospedar, Entrar;
  ESC (voltar, sair com confirmação; aviso do host).
- **Multiplayer:** a UI só chama o subsistema; nenhuma regra na UI.
- **Aceite:** TEST_PLAN.md, M3.
- **Riscos:** firewall do Windows (o alerta já apareceu na 0.1.1; liberar é decisão do usuário).

### M4 · Lobby de 20 vagas, bots de vaga e staging · [TODO]
- **Objetivo:** sala com 20 vagas (humano ou bot), controles do host, travel para a partida, Ilha de Espera.
- **Depende de:** M3.
- **Tarefas:** `L_Lobby`, `ANRLobbyGameMode/State`; vagas no PlayerState; bot de vaga (AIController com PlayerState que
  só anda, até o M15); seamless travel; Ilha de Espera no `L_Island`; fase Espera contando "carreguei".
- **Multiplayer:** vagas e pronto replicados; o host manda pedidos como qualquer cliente (RPC).
- **Aceite:** TEST_PLAN.md, M4.
- **Riscos:** seamless travel não funciona no PIE (testar com `-game`).

### M5 · Fundação de habilidades (GAS) · [TODO]
- **Objetivo:** habilidades viram Gameplay Abilities configuradas por dados (D-008), em rede.
- **Depende de:** M2. Com a D-002 aceita: ultimate no **T** e escala pelo **Arcano** (até o M11, o Poder Mágico atual).
- **Tarefas:** `NRGameplayTags`; `UNRGameplayAbility`; `UNRAbilityDefinition` + Asset Manager; `GE_Custo`/`GE_Recarga`
  genéricos; comportamentos `Projetil`, `AreaComAviso`, `Estrutura`; portar dardo, Bola de Fogo, Muralha de Gelo e
  Chuva de Meteoros; atores das magias com `bReplicates`; Gameplay Cues; HUD lendo recargas pelas tags; remover as
  magias do `UNRCombateComponent`.
- **Multiplayer:** ativação pelo servidor; predição só nas simples.
- **Aceite:** TEST_PLAN.md, M5.
- **Riscos:** curva do GAS; predição mal configurada (começar sem).

### M6 · Draft de habilidades · [TODO]
- **Objetivo:** draft único e sincronizado, em 2–4 min.
- **Depende de:** M4, M5, decisões.
- **Tarefas:** `UNRDraftComponent` + `DA_Draft_Padrao`; tela do draft; lista de preferências; escolha automática;
  bots escolhendo; concessão das habilidades ao nascer; medir a duração real.
- **Multiplayer:** servidor trava cada escolha; Fast Array para todos; corrida resolvida por ordem de chegada.
- **Aceite:** TEST_PLAN.md, M6.
- **Riscos:** UI do pool grande (128) ficar ilegível; corridas.

### M7 + M8 · Combate em terceira pessoa com armas · [TODO]
- **Objetivo:** 2 slots de arma; 4 armas da fatia vertical; mira; recarga; dano validado no servidor.
- **Depende de:** M5.
- **Tarefas:** `UNRWeaponDefinition`, `UNRArmasComponent`, `UNRGA_DispararArma`/`GolpeArma` (Target Data validado),
  animações da UAL (espada, arco), mira com o botão direito, HUD de munição, planilha de TTK com armas.
- **Multiplayer:** "a favor de quem atira" com validação (NETWORKING_ARCHITECTURE.md §5).
- **Riscos:** animações da Quaternius para arco e arma de fogo; sensação do tiro.

### M9 · Inventário de 6 slots, itens e loot · [TODO]
- **Objetivo:** Z X C V B N; passivos, ativos, consumíveis, Tomo; `DT_Loot`; bolsa da morte.
- **Depende de:** M2, M8.
- **Tarefas:** refazer os slots do `UNRInventoryComponent` (Fast Array); colunas novas no `DT_Itens`; `DT_Loot`;
  `ANRBolsaDeLoot`; baús dormentes; UI dos slots e do Tab.
- **Multiplayer:** dono vê o inventário; os outros, as armas.
- **Riscos:** muitos atores de loot (D-009 mitiga).

### M10 · Creeps / PvE · [TODO]
- **Objetivo:** creeps legíveis, em rede, baratos; primeiro creep à distância.
- **Depende de:** M2.
- **Tarefas:** sono do acampamento; aggro visível; `DT_Creeps`; creep à distância; elite; avaliar StateTree.
- **Riscos:** custo do servidor com ~70 creeps (medir no M18).

### M11 · XP, níveis e atributos · [TODO]
- **Objetivo:** ponto de atributo por nível; 4 atributos; mutações nos níveis marcados.
- **Depende de:** M1, M5.
- **Tarefas:** `AS_Hero` com os atributos novos; `CT_Atributos`, `CT_XP`; `Server_GastarPonto`; painel no Tab;
  `UNRMutacoesComponent` com níveis configuráveis e mutações vindas das habilidades.
- **Riscos:** mexer no `AS_Hero` quebra o HUD e os itens (fazer junto).

### M12 · Dirigível e queda · [TODO]
- **Objetivo:** queda em rede, rota em dados.
- **Depende de:** M2.
- **Tarefas:** `DA_Queda`; servidor solta quem ficou; ajuste para a ilha v2.

### M13 · Zona · [TODO]
- **Objetivo:** zona com aviso sonoro e visual claro; raios para a ilha v2.
- **Depende de:** M2.
- **Tarefas:** `INRZona` (já no M2), som de aviso, `CT_Storm` para a v2.

### M14 · Morte, espectador, vitória e resultados · [TODO]
- **Objetivo:** acabamento do que o M1 começou.
- **Depende de:** M1, M9.
- **Tarefas:** espectador completo (trocar de alvo, sem informação extra), tela de morte (quem, com o quê, dano por
  fonte), tela de resultados, `UNRTelemetriaSubsystem` (D-013) e o script de resumo.

### M15 · Bots jogadores · [TODO]
- **Objetivo:** bots das fases 1–3 (AI_AND_BOTS.md).
- **Depende de:** M4, M5, M8, M9.
- **Tarefas:** `ANRBotController`, StateTree, percepção, dificuldades em dados, bot no draft.

### M16 · UI completa e configurações · [TODO]
- **Objetivo:** todas as telas do UI_UX.md; configurações; remapeamento.
- **Tarefas:** `UNRGameUserSettings`; Player Mappable Keys + `UEnhancedInputUserSettings`; telas de vídeo, áudio,
  controles; String Tables.

### M17 · Graybox do mapa · [BLOCKED: Landscape do `L_Ilha` (usuário)]
- **Objetivo:** ilha v2 em blocos, medida com bots (MAP_DESIGN.md §4).
- **Alternativa se o usuário não puder:** graybox sobre plano com o relevo em blocos.

### M18 · Estresse de 20 jogadores · [TODO]
- **Objetivo:** partida inteira com 20 vagas; medir servidor, banda e cliente.
- **Depende de:** fatia vertical.

### M19 · Pipeline de arte pintada · [TODO]
- `M_Pintado_Master`, presets de luz, personagens com cel e contorno, primeiros Niagara (ART_DIRECTION.md).

### M20 · Produção do ambiente · [TODO]
- POIs da ilha v2 com os kits e a arte pintada, depois do graybox aprovado.

### M21 · Conteúdo: habilidades, armas, itens · [TODO]
- De 15 a 128 habilidades (proporção do ABILITY_SYSTEM.md §6); mais famílias de armas; itens ativos.

### M22 · Passe de balanceamento · [TODO]
- Telemetria de lotes de partidas com bots + playtests; BALANCE.md §7 e §8.

### M23 · Otimização de rede · [TODO]
- Relevância, dormência, frequências; avaliar Replication Graph ou Iris pelo perfil do M18.

### M24 · Otimização de desempenho · [TODO]
- Orçamentos do PERFORMANCE.md §3.

### M25 · Empacotamento e teste multiplayer externo · [TODO]
- Release com sessões pela internet (Steam ou EOS); teste com jogadores de fora; avaliar servidor dedicado (exige a
  Unreal compilada do código-fonte).

---

## Itens herdados do PLANO.md

| PLANO.md | Para onde foi |
|---|---|
| 1.9 Teclas no jogo empacotado | M0.5 |
| 1.8 Minimapa do `L_Island` | KNOWN_ISSUES K-11 (opcional) |
| 2.1 Grimórios viram E e R | Substituído pelo draft + Tomo (D-002d) |
| 2.2 Tela de montagem | Substituída pelo draft (D-002a) |
| 2.3 Outros arquétipos e escolas | Arquétipos saem (D-002a); escolas viram conteúdo do pool (M21) |
| 2.4 Feiticeiro completo | Passiva e animação de lançar: M5/M21 |
| 2.5 Legibilidade (barras, dano, tela de morte) | M14, M16 |
| 2.6 Interações Fogo + vegetação, Gelo + água | M21 (com o mapa v2) |
| 2.7 Mutações que faltaram | M11 |
| 3.x Mapa v2 | M17, M20 |
| 4.1 Rede | M1–M4 |
| 4.2 Bots | M4, M15 |
