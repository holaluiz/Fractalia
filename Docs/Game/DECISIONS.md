# Decisões de arquitetura e design

Cada decisão tem: problema, alternativas, escolha, motivo e status.

- **Decidida:** escolha técnica do arquiteto. Pode ser revista, mas vale até alguém mudar aqui.
- **Aguardando o usuário:** muda o design aprovado. Pela regra 1 do [AGENTS.md](../../AGENTS.md), nada disso entra no
  [GAME_DESIGN_DOCUMENT.md](GAME_DESIGN_DOCUMENT.md) nem no código antes da resposta do usuário.
- **Aceita:** o usuário respondeu.

Formato do número: `D-NNN`. Não renumere; marque as substituídas como "Substituída por D-NNN".

---

## D-001 · Documentação viva em `Docs/Game/` · Decidida (15/10)

- **Problema:** o pedido de 15/10 exige um conjunto de documentos (`MASTER_PLAN.md` e outros 16). O projeto já tinha o
  AGENTS.md (contexto para IAs), o PLANO.md (fases da 0.1.x) e o GDD v2.
- **Alternativas:** (a) espalhar o conteúdo nos documentos antigos; (b) criar `Docs/Game/` e deixar os antigos como
  estão; (c) criar `Docs/Game/` e definir o papel de cada um.
- **Escolha:** (c).
  - `Docs/Game/MASTER_PLAN.md` passa a ser **o plano central**. O PLANO.md fica como histórico da 0.1.x; o que estava
    aberto nele foi levado para o MASTER_PLAN.
  - O AGENTS.md continua sendo o contexto e o diário para IAs (estado atual, ambiente, pegadinhas) e aponta para cá.
  - Até 15/10, 22:30, o `Design/GDD.md` (v2) era o oficial. Com a D-002 aceita, o oficial é o
    [GAME_DESIGN_DOCUMENT.md](GAME_DESIGN_DOCUMENT.md) (v3); o v2 virou `Design/GDD_v2.md` e o `Design/GDD.md` só aponta.
  - Texto em português (regra do projeto); nomes de arquivo em inglês (pedido).
- **Motivo:** um só lugar para o plano, sem apagar o histórico nem duplicar o contexto.

## D-002 · A nova direção contra o GDD v2 · Aceita (15/10, 22:30)

O pedido de 15/10 descreve um jogo diferente do GDD v2 em pontos centrais. A tabela lista cada conflito e a
recomendação. **O usuário aprovou todas as recomendações como propostas** (resposta "Aprovar como proposto", 15/10,
por volta de 22:30). O GDD v3 virou o oficial; o item (m) já está no código (`ANRGameMode`, fator 0,4–2,0).

| # | Tema | GDD v2 (aprovado, parte implementada) | Pedido de 15/10 | Recomendação |
|---|---|---|---|---|
| a | Montagem antes da partida | Arquétipo (4) + 20 pontos em 5 atributos + Q e ultimate escolhidas; 5 builds salvas | **Draft:** 3 habilidades básicas + 1 ultimate, únicas na partida (ninguém repete) | **Draft substitui a montagem.** Sem arquétipos e sem builds salvas. A identidade vem do draft + armas + itens + pontos |
| b | Ataque principal | Ataque básico do arquétipo (dardo, golpe, flecha, feixe) | **Armas:** 1 slot de perto + 1 de longe, a ferramenta principal | **Armas.** O dardo arcano vira uma arma de longe ("Cajado") |
| c | Itens | 4 slots de equipamento (Armadura, Cabeça, Anel, Amuleto) + 3 de consumível (1-3) | **6 slots** genéricos (Z X C V B N), ativos, passivos ou consumíveis | **6 slots.** Os equipamentos do v2 viram itens passivos; os consumíveis entram nos mesmos slots, com pilha |
| d | Habilidades achadas na partida | E e R vêm de grimórios | As 4 vêm do draft | **Grimório vira "Tomo":** consumível que sobe +1 rank numa habilidade do draft, à escolha (ranks do GDD v2 §6.3) |
| e | Ganho por nível | 1 mutação (3 opções) por nível, do 2 ao 10 | **1 ponto de atributo** por nível | **Ponto a cada nível + mutação nos níveis 3, 6 e 9** (o componente já existe e é a parte "divertida" de subir). Ultimate só a partir do 6 |
| f | Atributos | Força, Agilidade, Vitalidade, Intelecto, Espírito (pontos na montagem) | Sugestão: Vitalidade, Poder, Arcano, Agilidade, Resiliência ("os nomes não são obrigatórios") | **4 atributos:** Vigor (vida, tenacidade), Poder (dano de arma), Arcano (dano e cura de habilidade, mana), Agilidade (velocidade, recarga de arma e de habilidade). Fórmulas em [BALANCE.md](BALANCE.md) |
| g | Teclas | Q, E, R magias; **X ultimate**; 1-3 consumíveis; Alt+1/2/3 mutação | Itens em **Z X C V B N**; armas em slots próprios | Q/E/R básicas, **T ultimate**, 1/2 armas, F interagir, Z X C V B N itens, Shift esquiva, Tab inventário. Detalhes em [UI_UX.md](UI_UX.md) |
| h | Duração | ~14 min de partida | 18–25 min (hipótese) | **~14 min de partida + ~4 min de staging, draft e queda ≈ 18 min de sessão.** O teste decide |
| i | Mana | Magias gastam mana | Habilidades têm "custo de recurso" | **Mana fica**, só para habilidades. Armas usam munição do pente (recarga), sem caixa de munição |
| j | Esquiva | Shift, comum a todos | Não fala | **Fica** como habilidade comum (contrajogo de projéteis) |
| k | Rede | Servidor dedicado na etapa 3 | Listen server (host) agora, dedicado depois | **Listen server agora** (D-003) |
| l | Pilares do v2 | Campo como arma (magias de campo), terreno reativo, legibilidade | Contrajogo, combinações, legibilidade | **Ficam.** As 14 magias + 7 ultimates do v2 viram o primeiro pool do draft |
| m | XP de abate | 80 × nível da vítima (mín. 100), +20% por nível que a vítima tiver acima | "Quem tem nível alto não deve ganhar demais matando os fracos" | **Fator entre 0,4 e 2,0** (também reduz quando a vítima é mais fraca). Fórmula no BALANCE.md §4. No código desde 15/10, 22:40 (a 0.1.2 publicada ainda usa a do v2) |

**Por que essas recomendações:**
- (a)/(b) O pedido diz que o herói "não é preso a uma classe" e que a build sai de arma + draft + itens + pontos. Manter
  arquétipos por cima disso criaria duas camadas de identidade e mais tempo antes da partida.
- (d) Sem os grimórios, a parte "achei coisa boa" do battle royale fica só nas armas e itens. O Tomo mantém o loot
  ligado às habilidades sem quebrar a unicidade do draft.
- (e) O pedido quer 1 ponto por nível; as mutações já existem e testam bem. Nos 3 níveis marcados elas viram picos de
  decisão, sem encher todo nível de escolhas.
- (f) Quatro atributos com dois eixos (arma × habilidade, sobreviver × ritmo) são o menor conjunto em que nenhum é
  ótimo para todos. Resiliência entra no Vigor; o Espírito se divide entre Arcano (mana) e Agilidade (recarga).
- (g) Z X C V B N ocupa o X da ultimate. T fica perto do Q/E/R e não briga com nada que já existe.

**Aplicado em 15/10:** o GDD v2 virou `Design/GDD_v2.md` (arquivado) e o [GAME_DESIGN_DOCUMENT.md](GAME_DESIGN_DOCUMENT.md)
é o oficial. Falta no código: o `AS_Hero` trocar os 5 atributos da build pelos 4 novos (M11), armas (M7/M8), 6 slots e
Tomo (M9), draft (M6), teclas novas (M5/M16).

## D-003 · Listen server agora, servidor dedicado depois · Decidida (15/10)

- **Problema:** o pedido quer um jogador hospedando a sala (como Warcraft III e Garena). O GDD v2 previa servidor dedicado.
- **Alternativas:** (a) dedicado desde já; (b) listen server, sem pensar em dedicado; (c) listen server com as regras
  escritas para rodar igual num dedicado.
- **Escolha:** (c).
- **Motivo:** (a) exige hospedagem e custo agora. (b) prende o jogo ao host. Em (c), toda regra vive no GameMode e nos
  componentes do servidor, nunca na UI nem no PlayerController local. O host é só "mais um cliente que por acaso é o
  servidor". As limitações do listen server estão em [NETWORKING_ARCHITECTURE.md](NETWORKING_ARCHITECTURE.md), §2.
- **Consequência:** o código nunca testa `IsLocallyControlled()` para decidir regra; testa `HasAuthority()`. O HUD do
  host lê os mesmos dados replicados que um cliente lê.

## D-004 · Máquina de estados própria da partida · Decidida (15/10)

- **Problema:** a partida hoje é um timer de 0,5 s no `GM_NexusRoyale` e um `OpenLevel` na morte. O pedido exige uma
  máquina de estados explícita (lobby → staging → draft → queda → partida → fim → resultados).
- **Alternativas:** (a) `AGameMode` com o `MatchState` da engine (WaitingToStart, InProgress, WaitingPostMatch) e
  estados extras; (b) `AGameModeBase` + `AGameStateBase` com um enum próprio replicado.
- **Escolha:** (b). `ANRGameMode` (C++, só servidor) decide as transições; `ANRGameState` replica a fase, o horário do
  servidor em que ela termina e os vivos. Clientes e HUD só leem.
- **Motivo:** o `MatchState` do `AGameMode` foi feito para partidas por rodada e traz comportamento que atrapalha
  (spawn atrasado, `ReadyToStartMatch`, reinício). Um enum próprio com tempos no relógio do servidor é mais simples de
  testar e de mostrar na UI, e é o mesmo padrão que já funciona na tempestade.
- **Consequência:** o `GM_NexusRoyale` passa a ser filho do `ANRGameMode` (reparent), e o `StartMatch` do Blueprint vira
  a entrada na fase de queda.

## D-005 · AbilitySystemComponent no herói, identidade no PlayerState · Decidida (15/10)

- **Problema:** o GDD v2 §16 pedia o ASC no PlayerState; ele foi feito no Character. Com draft, abates e colocação, há
  dados que precisam existir antes do pawn e depois da morte.
- **Alternativas:** (a) mover o ASC para o PlayerState (padrão do Lyra); (b) manter no Character e pôr no PlayerState só
  o que é "da partida".
- **Escolha:** (b). No `ANRPlayerState` (replicado): nome, bot ou humano, pronto, habilidades do draft, vivo, abates,
  nível e XP (espelho), colocação. O ASC continua no herói.
- **Motivo:** sem respawn no modo solo, o ASC no pawn não perde nada na partida, e mover agora custaria refazer o
  `AS_Hero`, o inventário e o HUD juntos. O draft acontece antes do pawn existir; por isso as escolhas moram no
  PlayerState, e o servidor concede as habilidades ao ASC quando o herói nasce.
- **Revisar se:** surgir um modo com respawn ou reconexão (aí o ASC no PlayerState sobrevive à troca de pawn).

## D-006 · Lobby em mapa próprio, staging dentro do mapa da partida · Decidida (15/10)

- **Problema:** o pedido quer uma área de espera que esconda o carregamento, e avisa que um mapa pequeno separado não
  carrega o mapa grande sozinho.
- **Alternativas:** (a) mapa de transição que carrega o mapa da partida por Asset Bundles; (b) área de espera dentro do
  mapa da partida, depois de um travel do lobby; (c) World Partition com a área de espera num canto do mundo.
- **Escolha:** (b). O lobby fica num mapa leve (`L_Lobby`). Ao começar, o host faz **seamless travel** para o mapa da
  partida. Lá, todos nascem na **Ilha de Espera** (uma plataforma fora da ilha, ou o hangar do dirigível), fazem o
  draft e só então embarcam. A fase de staging espera todos os clientes avisarem "carreguei" (ou 60 s).
- **Motivo:** o mapa da partida já está carregado quando a espera começa, então o que a espera esconde é o que realmente
  pesa: compilar shaders no primeiro uso, a replicação inicial e jogadores lentos. Os mapas atuais não são World
  Partition (1 km cabe inteiro na memória), então (c) não ganha nada agora. (a) exige uma estrutura de Asset Bundles
  que o projeto não tem.
- **Revisar se:** o mapa v2 virar World Partition (então a Ilha de Espera pode virar uma célula sempre carregada).

## D-007 · Formato do draft · Aceita (15/10, 22:30): serpente em 4 faixas

- **Problema:** 20 jogadores × 4 escolhas = 80 escolhas. Um de cada vez leva de 7 a 13 min.
- **Alternativas, simuladas** com [ferramentas/simular_draft.py](ferramentas/simular_draft.py) (400 drafts cada;
  resultado em [BALANCE.md](BALANCE.md), §3):

  | Formato | Duração média | Pegou a favorita | Corridas por draft |
  |---|---|---|---|
  | A · serpente em 4 faixas de 5, janela de 8 s | 2,4 min | 41% | 0,5 |
  | A5 · serpente em 5 faixas de 4, janela de 8 s | 2,1 min | 41% | 0,8 |
  | B · reserva simultânea (top 3), janela de 12 s | 1,1 min | 42% | 0 |
  | C · serpente sequencial, 1 por vez | 7,3 min | 41% | 0 |

- **Escolha recomendada:** **A** (o pedido prefere; dá para ver cada escolha na hora e responder a ela). O formato
  fica num Data Asset; **B** é implementado depois sobre o mesmo estado, como alternativa rápida.
- **Motivo:** A e B dão a mesma satisfação; B é mais rápido e não tem corrida, mas o jogador só vê as escolhas dos
  outros ao fim de cada rodada, o que tira a negação ao vivo. A cabe no alvo de 2–4 min.
- **Corrida no A:** quando duas faixas pedem a mesma habilidade quase juntas, o servidor aceita a primeira que chegar.
  O host tem latência zero e ganha esses empates (cerca de 0,5 por draft). Aceitável no modo casual; no modo
  ranqueado (dedicado) não há host.

## D-008 · Habilidades como Gameplay Abilities genéricas configuradas por dados · Decidida (15/10)

- **Problema:** o alvo é um pool de 128 habilidades. Hoje cada magia é um ramo de código no `UNRCombateComponent` e
  cada mutação é um `case` de `switch`.
- **Alternativas:** (a) uma classe `GA_*` (Blueprint) por habilidade; (b) poucas classes C++ de comportamento
  (projétil, área com aviso, estrutura, avanço, buff, passiva, invocação) configuradas por um Data Asset por
  habilidade; (c) um sistema próprio, sem GAS.
- **Escolha:** (b), com saída para (a) quando uma habilidade for única demais.
  - `UNRAbilityDefinition` (Primary Data Asset): tag de identidade (`Ability.Id.BolaDeFogo`), básica ou ultimate,
    categorias (`Ability.Category.Damage`…), ícone, textos, custo, recarga, telegrafia, a classe de comportamento e
    os parâmetros dela.
  - O draft, a UI e os bots leem só o Data Asset. Adicionar habilidade = criar um Data Asset (e, raramente, uma classe).
- **Motivo:** o GAS já dá ativação pelo servidor com predição, custo, recarga por tag, efeitos e replicação. Uma
  classe por habilidade não escala para 128; um sistema próprio jogaria fora o que o projeto já compilou.

## D-009 · Loot no chão · Decidida (15/10)

- **Problema:** cada item no chão é um ator replicado. Numa partida de 20, as mortes soltariam centenas.
- **Escolha:**
  - baús ficam **dormentes** na rede até abrir; ao abrir, criam um pickup por item (no máximo 3), como hoje;
  - a morte solta **uma bolsa** (`ANRBolsaDeLoot`) com a lista replicada dos itens e armas, em vez de um ator por item;
  - pickups e bolsas somem quando a tempestade fecha sobre eles.
- **Motivo:** o custo de rede é por ator; uma lista dentro de um ator custa uma fração disso. A bolsa também é mais
  legível ("aqui morreu alguém").

## D-010 · Sessões atrás de um subsistema do jogo · Decidida (15/10)

- **Problema:** hospedar e entrar em salas sem prender o jogo a Steam ou EOS.
- **Escolha:** `UNRSessaoSubsystem` (GameInstance Subsystem) com `Hospedar`, `Procurar`, `Entrar`, `Sair`. Por dentro,
  usa a interface de sessões do Online Subsystem configurado: **Null** (LAN) e **IP direto** no desenvolvimento; Steam
  ou EOS depois. A UI e o gameplay só falam com o subsistema.
- **Internet:** listen server pela internet precisa de NAT traversal. Com Null/IP direto, o host abre a porta 7777 no
  roteador. Com Steam (Steam Sockets) ou EOS (P2P), a plataforma resolve. Ver NETWORKING_ARCHITECTURE.md, §6.

## D-011 · Ordem dos marcos diferente da lista do pedido · Decidida (15/10)

- **Mudanças** (detalhe em [MASTER_PLAN.md](MASTER_PLAN.md)):
  1. **M0.5 "Estabilizar a 0.1.x"** entra antes de tudo: o jogo publicado está sem as teclas de combate (correção de
     gameplay é a prioridade 1 do pedido).
  2. **Morte, espectador e vitória (núcleo)** sobem para o M1: uma máquina de estados sem fim de partida não se testa.
  3. **M2 vira "Autoridade do loop atual"**: dirigível, interação, loot, inventário, creeps e XP passam pelo servidor e
     são testados com host + 1 cliente **antes** das sessões. Sessão sem gameplay replicado não prova nada.
  4. **Combate legado não ganha RPC** (D-014): o combate entra em rede junto com o GAS (M5).
  5. Dirigível, tempestade e creeps já existem: os marcos deles viram "adaptar e pôr em rede", menores.
  6. **Graybox do mapa (M17) depende do usuário** importar o Landscape do `L_Ilha` (ou de decidir fazer o graybox sem
     Landscape).

## D-012 · Bots com StateTree, mesmo pawn e mesmas regras · Decidida (15/10)

- **Escolha:** bot = `AAIController` com PlayerState próprio, possuindo o mesmo `BP_HeroBase`. O cérebro é um StateTree
  (o plugin GameplayStateTree já está ativo). O bot ativa habilidades pelo mesmo `TryActivateAbility` e usa armas pela
  mesma ação do jogador. Percepção pelo `AIPerception` (visão e audição), sem ler a posição de quem ele não vê.
- **Motivo:** o pedido exige as mesmas regras para bots e humanos; o StateTree já está no projeto e é a ferramenta atual
  da engine para IA. Os creeps continuam no `Think` em Blueprint até precisarem de mais (M10).

## D-013 · Telemetria de desenvolvimento local · Decidida (15/10)

- **Escolha:** o servidor grava um arquivo JSON Lines por partida em `Saved/Telemetria/` (eventos: fase, draft, dano
  resumido, abate, morte, nível, XP por fonte, loot, uso de habilidade e de arma, tempestade). Sem IP, sem ID de
  plataforma; o nome do jogador vira um índice da partida. Um script Python resume (ver BALANCE.md).
- **Motivo:** responde às perguntas de balanceamento do pedido sem backend e sem dado pessoal.

## D-014 · O combate legado não ganha RPCs · Decidida (15/10)

- **Problema:** o `UNRCombateComponent` roda no input local. Pôr RPC nele já permitiria testar combate em rede no M2.
- **Escolha:** não. O combate entra em rede quando virar Gameplay Abilities (M5). Até lá, o teste de rede do M2 cobre
  movimento, queda, loot, inventário, creeps e XP; combate em rede só no M5.
- **Motivo:** o GAS já traz a ativação pelo servidor com predição. RPCs no componente legado seriam código para jogar
  fora em poucas semanas.

## D-015 · Quem entra com a partida em andamento só assiste · Decidida (15/10)

- **Problema:** no teste de rede do M1, um cliente que conectou durante a Queda ganhou herói e contou como vivo, numa
  partida que já tinha decidido o modo treino e o número de jogadores.
- **Escolha:** da Queda em diante, `ANRGameMode::HandleStartingNewPlayer` não cria herói: o jogador vira espectador
  (`StartSpectatingOnly`), com `bVivo = false`, e fica fora da contagem de jogadores. Na partida seguinte ele joga.
- **Motivo:** é a regra do battle royale (GAMEPLAY_SYSTEMS.md §2) e evita que alguém entre no meio com vantagem de
  posição ou desfaça a contagem de vivos.

## D-016 · A Espera aguarda os humanos que a sala espera · Decidida (15/10)

- **Problema:** um cliente leva de 6 a 60 s para carregar o mapa neste PC. No recomeço (`ServerTravel`), a Espera fechava
  em 3 s, antes de o cliente voltar.
- **Escolha:** `ANRGameMode.JogadoresEsperados`: a Espera termina quando há pelo menos esse número de humanos conectados e
  com herói (ou no tempo máximo de 60 s). No recomeço, o GameMode deixa o número (jogadores + espectadores de agora) no
  `UNRSessaoSubsystem`, que vive no GameInstance e sobrevive à troca de mapa. No M4, o lobby passa a informar o número.
  Para testar a primeira partida antes do lobby: `EsperarJogadores(N)` (função de desenvolvimento).
- **Por que não pela URL (`?Restart?Esperar=N`):** o `ServerTravel` relativo acumula opções na URL a cada recomeço, e a
  leitura pega a primeira ocorrência (valor velho).

## D-017 · Bots de teste e modo treino no M1 · Decidida (15/10)

- **Problema:** testar vitória e abate sem lobby nem segundo jogador, e sem quebrar o loop solo de antes.
- **Escolha:** `ANRGameMode::AdicionarBotDeTeste()` cria um `ANRBotController` com PlayerState e o mesmo herói (ainda sem
  cérebro); e a partida que começa com 1 jogador vira **modo treino** (acaba quando ele morre e recomeça o mapa).
- **Motivo:** o bot exercita o mesmo caminho de eliminação dos humanos (PlayerState, colocação, abate, XP); o modo
  treino mantém o que o jogo publicado fazia (morrer e recomeçar), agora pela máquina de estados.

