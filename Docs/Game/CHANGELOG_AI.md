# Registro de mudanças feitas por IA

Uma entrada por tarefa significativa, **a mais nova embaixo**. Formato: data e hora (Brasília), IA, o que mudou,
arquivos/assets, como foi testado, o que fica sem verificar, próxima ação.

O diário detalhado das sessões anteriores a esta pasta está no [AGENTS.md](../../AGENTS.md), seção 9; o registro
automático de cada edição, em [Registro/atividade.md](../../Registro/atividade.md).

---

### 2026-10-15 19:40 → 20:30 · Claude (Claude Code) · Marco 0: auditoria e documentação
- **Pedido:** prompt "Lead Game Architect" do usuário: auditar o projeto, criar `Docs/Game/`, escrever o GDD, a
  arquitetura e o plano mestre, definir a fatia vertical e só então começar o primeiro marco.
- **Feito:**
  - auditoria completa ([AUDITORIA.md](AUDITORIA.md)): inventário, o que funciona/quebrou/falta, riscos de escala,
    mapa de dependências, dívida técnica;
  - os 17 documentos pedidos em `Docs/Game/`, em português;
  - **GDD v3 como proposta** ([GAME_DESIGN_DOCUMENT.md](GAME_DESIGN_DOCUMENT.md)): o `Design/GDD.md` (v2) não foi
    tocado, pela regra 1 do AGENTS.md; os conflitos estão em [DECISIONS.md](DECISIONS.md), D-002, esperando o usuário;
  - protótipo numérico do draft: [ferramentas/simular_draft.py](ferramentas/simular_draft.py) (resultado em
    BALANCE.md §3);
  - [MASTER_PLAN.md](MASTER_PLAN.md) com os marcos reordenados (D-011) e a fatia vertical.
- **Arquivos:** só `Docs/Game/*` (novos). Nenhum código, Blueprint ou asset mudou.
- **Testado:** o simulador rodou (400 drafts por formato). A auditoria foi conferida contra o código e as DSLs; **nada
  foi aberto no editor** (Unreal fechada, MCP sem conexão).
- **Próxima ação:** respostas do usuário à D-002 e à D-007; M0.5 (teclas no IMC) e M1 (máquina de estados).

### 2026-10-15 20:10 → 21:05 · Claude (Claude Code) · M0.5: teclas de combate salvas no IMC
- **Problema:** K-01. O `map_key` muda o `IMC_Default` na memória sem marcar o pacote, e o `save_loaded_asset` pulava o
  salvamento; o jogo empacotado (0.1.0 e 0.1.1) saiu sem botão esquerdo, Q, E, X, F, 1-4.
- **Feito:** `Unreal/ue_mvp_setup.py` chama `imc.modify()`, salva com `only_if_is_dirty=False` e confere os nomes das
  ações dentro do `.uasset` (falha se faltar). Rodado com o editor aberto.
- **Arquivos:** `Unreal/ue_mvp_setup.py`; `Content/Input/IMC_Default.uasset` (8,3 KB → 12,5 KB);
  `Content/NexusRoyale/Blueprints/Core/BP_HeroBase.uasset` (re-salvo pelo script, mesmos valores);
  `Config/DefaultGame.ini` (versão 0.1.2).
- **Testado:** as 9 ações aparecem no arquivo salvo. **Sem verificar:** o jogo empacotado (empacotando às 22:05).
- **Próxima ação:** abrir a 0.1.2 empacotada, testar as teclas, publicar com o OK do usuário.

### 2026-10-15 20:00 → 22:05 · Claude (Claude Code) · M1: máquina de estados, morte e vitória em rede
- **Feito:**
  - C++ novo em `Source/NexusRoyale/Core/`: `NRTiposPartida.h` (fases), `ANRGameMode` (fases, eliminação, abate, XP de
    abate, vitória uma vez só, invulnerabilidade no Final, espectador para quem chega atrasado, recomeço por
    `ServerTravel` ou `OpenLevel`, bot de teste, `EsperarJogadores`), `ANRGameState` (fase e prazos no relógio do
    servidor, vivos, vencedor, modo treino), `ANRPlayerState` (vivo, abates, colocação, nível, quem eliminou),
    `UNRSessaoSubsystem` (humanos esperados no recomeço); `AI/ANRBotController`;
  - `UNRAbilitySystemComponent`: `bMorto`, `UltimoAssassino`, `Nivel` e `XP` replicados (morte vista no cliente pelo
    `OnRep`), `OnMorreuNativo`, `DefinirInvulneravel`, espelho do nível no PlayerState;
  - `UNRCombateComponent`: não recomeça o mapa sozinho quando há `ANRGameState`;
  - `UNRHudWidget`: linha da partida ("N vivos", "Treino", "Esperando jogadores") e avisos de eliminação, vitória,
    "FIM DO TREINO" e resultados (placar e contagem);
  - `GM_NexusRoyale`: pai trocado para o `ANRGameMode` (`Unreal/ue_m1_setup.py`), `StartMatch` virou o evento
    `IniciarQueda` (DSL), o timer antigo do `BeginPlay` foi apagado (`Unreal/ue_bp_apagar_cadeia.py`);
  - `DefaultEngine.ini`: `GlobalDefaultGameMode` = `GM_NexusRoyale`; `Build.cs`: `AIModule`;
  - ferramentas: `Unreal/pie_partida.py` (estado, bot, matar, saltar, esperar), `Unreal/rede_testar.py` (clientes sem
    render), `ue_py.py` escolhe o editor entre vários processos, `ue_gas_compilar.py --pouca-memoria`,
    `ue_release.py empacotar --pouca-memoria`.
- **Testado:** TEST_PLAN.md §5 (três rodadas, 21:08–21:57): PIE solo com bots, modo treino, rede com cliente `-nullrhi`
  (fases e morte replicadas, vitória, recomeço com o cliente, desconexão, espectador). Capturas em
  `Export/Previews/teste_m1_*.png`.
- **Problemas achados e corrigidos no caminho:** compilação sem memória (`C1060`); causa "HeroBase"; Espera sem aguardar
  o cliente no recomeço; cliente atrasado com herói; `ue_py.py` caindo no cliente de teste.
- **Sem verificar:** câmera em quem matou; HUD do lado do cliente; câmera do espectador; contagem de espectadores no
  recomeço (última correção, compilada e não testada); a partida no jogo empacotado.
- **Decisões:** D-015 (atrasado assiste), D-016 (Espera aguarda humanos), D-017 (bot de teste e modo treino).
- **Próxima ação:** M2 (autoridade do loop atual).

