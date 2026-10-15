# AGENTS.md: contexto do projeto para IAs

> **Leia este arquivo antes de mexer no projeto.** Ele vale para qualquer IA (Claude, ChatGPT,
> Gemini, Copilot, Cursor…) e é a memória compartilhada do que já foi feito.
>
> **Ao terminar uma sessão de trabalho:** atualize a seção 3 (Estado atual) e acrescente uma
> entrada no fim da seção 9 (Diário). Seja curto e diga o que ficou **sem verificar**.

Última atualização: 2026-10-15, por volta de 17:35 (horário de Brasília), por Claude (Claude Code), sessão "Instalador com atualização automática".

---

## 1. O projeto em 30 segundos

- **Nexus Royale** é um battle royale **solo** de magias com progressão de MOBA, feito na
  **Unreal Engine 5.8**. Até agora o projeto é só Blueprint e usa assets gratuitos da **Quaternius**.
- **Antes da partida**, o jogador monta o campeão:
  - escolhe um arquétipo (Guerreiro, Patrulheiro, Feiticeiro ou Místico);
  - distribui 20 pontos em 5 atributos;
  - escolhe uma magia principal e uma ultimate.
- **Na partida**, abre baús e encontra grimórios, mata creeps e sobe do nível 1 ao 10. A cada
  nível escolhe uma mutação. Tem barra de vida e de mana, e a tempestade fecha o mapa.
- **Não tem construção.** O campo de batalha muda com as **magias de campo**.
- **O design oficial está em [Design/GDD.md](Design/GDD.md) (v2).** A v1 (heróis fixos, construção,
  torres, Guardião) está em `Design/GDD_v1.md` e **foi abandonada**. Nada dela vale.
- **O usuário fala português (pt-BR).** Responda e escreva os documentos em português.

## 2. Regras para quem continuar

1. Os números do GDD são valores iniciais de balanceamento. **Não altere o GDD sem perguntar ao
   usuário.** Proponha a mudança e espere a resposta.
2. **Não apague a pasta `Personagens/`.** São modelos do próprio usuário (feitos no Tripo). Eles
   saíram do jogo, mas os arquivos ficam no disco.
3. Personagem novo usa o **esqueleto compartilhado da Quaternius** (seção 6).
4. Antes de escrever um script novo, procure um parecido em `Unreal/` e `Blender/scripts/`.
5. O PC tem pouca RAM e pouca memória de vídeo:
   - importe em lotes pequenos;
   - não deixe Blender e Unreal fazendo trabalho pesado ao mesmo tempo.
6. Mudanças no sistema (memória virtual, instalar programas) são do usuário. Passe o passo a passo
   e deixe que ele faça.
7. **Registre tudo o que acontecer, na hora, para as outras IAs** (pedido do usuário em 15/10). Toda
   mudança no projeto vai para dois lugares:
   - **[Registro/atividade.md](Registro/atividade.md)**, uma linha por mudança. Nas sessões do Claude
     Code, isso é automático. Outras IAs devem escrever à mão, no mesmo formato.
   - **Este arquivo:** seção 3 se o estado mudou, e uma entrada na seção 9.

## 2.1 Registro automático (Claude Code)

- `.claude/settings.json` liga dois hooks que rodam `.claude/hooks/registro.py`:
  - **PostToolUse:** grava em `Registro/atividade.md` cada arquivo do projeto escrito ou editado,
    cada comando que altera a Unreal ou o Blender e cada chamada de escrita ao MCP da Unreal.
    Leituras (probes, capturas, `read_graph_dsl`, `list_…`) não entram.
  - **Stop:** se a sessão mudou o projeto e não atualizou o AGENTS.md depois, o Claude é parado uma
    vez e recebe o pedido de registrar o que mudou.
- O que está pendente fica em `.claude/hooks/state/<sessão>.json` e é limpo quando a sessão edita
  o AGENTS.md.
- **Outras ferramentas** (Cursor, ChatGPT, Copilot…) não rodam esses hooks. Elas precisam seguir a
  regra 7 à mão.

## 3. Estado atual (2026-10-15)

### Pronto

- **Instalador e atualização automática** (sessão "Instalador com atualização automática", 15/10).
  - **Versão 0.1.0 empacotada** (Development, 1,33 GB; zip de 1,07 GB) em `D:\NexusRoyale_Builds\0.1.0`.
    Aberta direto da pasta do build às 17:22: carrega o `L_Island` sem erro de Blueprint, com o herói, o
    HUD, os Imps e o visual aquarela.
  - **Publicação:** Release `v0.1.0` no repositório privado `holaluiz/MOBA-BR`, com o
    `NexusRoyale-Instalador.exe`, o zip e o `manifest.json` (veja a seção 9 para o que foi testado).
  - **Instalador/launcher** (`Launcher/NexusRoyaleLauncher.cs`, um `.exe` só):
    - instala em `<disco com mais espaço>:\Jogos\NexusRoyale`, cria os atalhos "Nexus Royale" e a
      entrada em Aplicativos;
    - a cada abertura, confere a última Release, baixa a versão nova, confere o SHA-256, troca a pasta
      `game` e só então abre o jogo. Sem internet, abre o que já está instalado. Ele também troca a si
      mesmo quando o manifest traz um launcher mais novo;
    - pede o token do GitHub quando não acha um. **Neste PC está instalado em `D:\Jogos\NexusRoyale`.**
  - **Publicar versão nova:** com a Unreal fechada, `Publicar-versao.bat` ou
    `python -I Unreal/ue_release.py tudo` (seção 5, "Release").
- **MVP jogável no `L_Island`** (testado em PIE em 15/10, de 12:12 a 13:33). Basta abrir o editor e
  dar Play. O ciclo completo funciona: dirigível → salto e planagem → baú → itens → creeps → XP e
  nível → tempestade → morte → a partida recomeça sozinha em 6 s.
  - **Módulo C++ `NexusRoyale` compilado** (VS 2026, MSVC 14.50.35717) e listado no `.uproject`,
    com o plugin GameplayAbilities. Para recompilar: feche o editor e rode
    `python -I Unreal/ue_gas_compilar.py`. A primeira compilação levou 7 min; as seguintes, de 1,5 a 3 min.
  - **Herói (`BP_HeroBase`)** com três componentes C++:
    - **`Habilidades`** (`UNRAbilitySystemComponent`): Feiticeiro de Fogo do GDD §4.2, com vida 520,
      mana 430 e Poder Mágico +27%. Todo `ApplyDamage` da Unreal no herói (creeps, projéteis) vira
      `AplicarDano` (`bReceberDanoDaUnreal`). Ganhou `GastarMana`, `XP`, `GanharXP`, `DarXP` (estático,
      chamado no `Die` do creep), `ProgressoXP` e `OnSubiuNivel`. O XP acumulado por nível é o do GDD §7.1.
    - **`Inventario`** (`UNRInventoryComponent`): ganhou `PegarDoChao` (sem pinos de saída, para a
      DSL), `ItemQueFicaNoChao`, `RaridadeQueFicaNoChao` e `MensagemRecente` ("Pegou: …", "Usou: …").
    - **`Combate`** (`UNRCombateComponent`, novo, em `Source/NexusRoyale/Combat/`):
      - botão esquerdo: dardo arcano (60 mágico, 35 m, 1/s, levemente teleguiado num cone de 12°);
      - **Q:** Bola de Fogo (130 em área de 3 m, 55 de mana, recarga de 7 s);
      - **E:** Muralha de Gelo (GDD §6.3): parede de 6 × 3,5 m no chão sob a mira, a até 15 m (no
        mínimo 2,5 m), com 400 de vida, por 6 s, 50 de mana e recarga de 12 s. Vira um `ANREstruturaMagica`;
      - **X:** Chuva de Meteoros (GDD §6.4): área de 8 m de diâmetro sob a mira, a até 30 m (o alcance
        é chute: o GDD não diz). Tem 1 s de aviso, 3 meteoros de 120 (cada alvo leva no máximo um) e
        chão em chamas por 4 s, com 20/s (chute, como a vegetação queimando do §6.5). Custa 120 de
        mana, com recarga de 80 s. Vira um `ANRChuvaMeteoros`. A ultimate é liberada no `NivelUltimate`:
        6 no C++, como no GDD, mas **1 no `BP_HeroBase`** (MVP), porque um acampamento só não leva ao nível 6;
      - **1, 2 e 3:** consumíveis.
      - A configuração das magias fica em structs editáveis no Details (`Combat/NRMagiaTypes.h`):
        `FNRMagiaProjetil`, `FNRMagiaEstrutura` e `FNRMagiaChuva`.
      - **Ainda não é Gameplay Ability (`GA_*`).** Decisão desta etapa: com o kit fixo e a partida solo,
        o GAS não muda o comportamento e custaria refazer custo, recarga e mira com tags e efeitos. A
        migração fica para a etapa 2 (grimórios trocando E e R, mutações e rede). O motivo está no
        header do `UNRCombateComponent`.
      - As teclas vêm de Input Actions novas no `IMC_Default` e são ligadas em C++ no InputComponent
        do herói.
      - Também cria o HUD do jogador e, na morte, toca o `Death01` em todas as malhas, tira movimento
        e input e recomeça o nível depois de `TempoParaRecomecar` (6 s).
    - O dano das magias é multiplicado por (1 + Poder Mágico), e a recarga diminui com a Redução de Recarga.
  - **`ANRProjetilMagico`** (C++): esfera unlit (`/Game/NexusRoyale/VFX/M_Projetil`, parâmetro "Cor")
    com luz. Bloqueia o cenário e sobrepõe pawns, ignora quem lançou e explode na hora se nasceu
    encostado num inimigo. Aplica `ApplyDamage` (em pawns e estruturas mágicas) ou `ApplyRadialDamage`.
    Usa custom depth com stencil 4 (pedido da sessão do visual).
  - **`ANREstruturaMagica`** (C++, o `BP_SpellStructure_*` do GDD §16): uma caixa `BlockAllDynamic`
    (bloqueia pawns, projéteis e a linha de visão do dano em área; a câmera atravessa) com o cubo da
    engine e o material `/Game/NexusRoyale/VFX/M_Estrutura` (iluminado, parâmetro "Cor").
    - Tem vida e duração. Sobe do chão em 0,15 s, afunda em 0,3 s e escurece conforme perde vida.
    - Toma dano pelo `ApplyDamage` da Unreal, mas **o dano do próprio dono não conta**: ela segura os
      tiros dele sem se desfazer.
    - Stencil 4.
  - **`ANRChuvaMeteoros`** (C++): disco de aviso piscando na cor da escola. Depois vêm os meteoros
    (esferas que caem na diagonal, a meio raio do centro, com clarão do tamanho da explosão) e o
    disco vira chão em chamas, com luz. O dano vai por `ApplyDamage`, em pawns e estruturas; quem
    lançou fica de fora. Stencil 4.
  - **HUD (`UNRHudWidget`), sem Widget Blueprint:** o C++ monta o layout sozinho. No pé da tela ficam
    a mensagem do inventário, "Nível N · a/b XP" com a barra dourada, a vida, a mana, a linha das
    magias (botão esquerdo, Q, E e X, com a recarga em segundos, "sem mana" e "nível N" para a
    ultimate presa) e os consumíveis. Também mostra a mira "+" no centro (some no
    dirigível e na morte), os equipados no canto e avisos grandes ("Nível 3!", "VOCÊ FOI ELIMINADO —
    recomeçando em N"). Para trocar o visual, crie um WBP filho com widgets de mesmo nome (lista no header).
  - **Tempestade:** o `StormTick` chama `AplicarDanoTempestade` (% da vida máxima, sem armadura).
  - **Loot com a tabela:** o baú sorteia IDs do `DT_Itens` (`SortearItem`) e cria os pickups com
    `SpawnItem` → `BP_Pickup.SetupItem`, que tira malha e nome da tabela. O F chama `PegarDoChao`; se
    o slot estava ocupado, o pickup passa a mostrar o item que saiu. O F agora pega um item
    sobreposto quando o atual some (`InteractNearby`).
  - **Scripts:** `Unreal/ue_gas_setup.py` (DT_Itens e os componentes Habilidades e Inventario) e
    `Unreal/ue_mvp_setup.py` (M_Projetil, M_Estrutura, as teclas, inclusive E e X, e o componente
    Combate), mais o `Unreal/pie_combate.py` para testar.
  - **Teclas:** WASD, Espaço (salta do dirigível e plana), botão esquerdo, Q, E, X, F, 1-3 e M.
- **Projeto Unreal** em `Unreal/NexusRoyale`:
  - criado a partir do template Third Person (Blueprint), UE 5.8.3;
  - plugins ativos: Model Context Protocol, All Toolsets, Python Editor Script e GameplayStateTree.
- **Nível `L_Island`** (`/Game/NexusRoyale/Maps/L_Island`):
  - ilha de 400 × 400 m (40.000 cm) com a natureza da Quaternius;
  - dois POIs montados por script: **Vila** (Medieval Village) e **Cidade** (Downtown City).
- **Packs Quaternius importados** em `/Game/Quaternius/`: Env (cerca de 590 assets), Outfits,
  Characters, Animations (UAL1 e UAL2) e Creeps.
- **Visual do herói Quaternius funcionando:** corpo, roupa e cabelo, `ABP_Hero` e `M_HeroHead`.
- **Creeps e acampamento de Imps, ainda sem GAS** (testado em PIE em 15/10, às 11:30). Ficam em
  `/Game/NexusRoyale/Blueprints/Creeps/`, e os grafos estão em `Unreal/Blueprints/BP_Creep__*.dsl` e
  `BP_CreepCamp__*.dsl`.
  - **`BP_Creep`** (Character com AIController), com os filhos `BP_Creep_Imp` e `BP_Creep_Puglin`.
    - **`Think`** roda a cada 0,3 s no servidor:
      - sem alvo, volta para casa e pega o primeiro herói a menos de `AggroRadius` (7 m);
      - com alvo, persegue e bate dentro de `AttackRange` (1,7 m), com `ApplyDamage` da Unreal;
      - **se uma estrutura mágica (Muralha de Gelo) bloqueia o caminho até o alvo, bate nela** com o
        mesmo dano e a mesma recarga, até ela quebrar. Isso tem prioridade sobre bater no alvo, então
        o creep não acerta o herói através da muralha. O `FindBlocker` confere no espaço local da
        estrutura (encostado numa face, dentro da largura, do lado oposto ao alvo), e o `AttackActor`
        é o golpe, no alvo ou na estrutura (escolha do usuário em 15/10, às 16:15);
      - se o alvo se afasta mais de `LeashRadius` (15 m) do ponto de origem, solta o alvo, volta com
        a vida cheia e anda para casa (corrente do GDD §12).
    - **Andar:** o `EventTick` dirige com `AddMovementInput` até o `MoveGoal`. Não precisa de NavMesh,
      que nenhum nível tem.
    - **Ao levar dano:** toca a animação de golpe, e os creeps a menos de 10 m da origem dele que
      estão sem alvo atacam o agressor (o acampamento inteiro reage).
    - **`Die`:** pose de morte (animação direta, que segura o último quadro), sem colisão nem
      movimento. Chama `OnCreepKilled(Killer = controller de quem deu o golpe final, XP)` e some em 3 s.
    - **Números** (em `Unreal/ue_creeps_camp.py`; os de dano são chute para o GDD §12 "custa ~25% da
      vida no nível 1"):

      | | Vida | XP | Dano / recarga | Alcance |
      |---|---|---|---|---|
      | Imp | 150 | 30 | 12 / 1,5 s | 1,7 m |
      | Puglin | 700 | 120 | 30 / 1,8 s | 1,5 m |

      Os dois usam aggro de 7 m e corrente de 15 m, e as animações retargetadas `Hit_Chest`,
      `Zombie_Scratch` e `Death01`.
  - **`BP_CreepCamp`** (Actor): cria um creep por entrada de `CreepClasses` num círculo de 2,5 m. A
    cada 1 s confere se todos morreram; se sim, reaparece depois de `RespawnDelay`.
    - Pequeno = 3 Imps / 90 s. Médio = Puglin + 2 Imps / 150 s (o script já sabe montar, mas nenhum
      foi posto).
  - **Posição por dados:** `Unreal/Data/Camps_L_Island.json` tem o mesmo formato de
    `mapa_ue.json` → `acampamentos`. O `place_camps()` do script solta cada acampamento no chão.
    - No `L_Island` há **um acampamento pequeno** a 18 m da praça do PlayerStart, em (-1560, -700).
  - **`BP_HeroBase`** ganhou `DamageTaken` e um `EventAnyDamage` que soma o dano e mostra
    "Dano: -X". O dano de verdade agora vai para o GAS pelo componente `Habilidades`.
  - **Corrigido em 15/10, às 13:00:** um golpe que tirasse metade ou mais da vida restante matava o
    creep e não alertava o acampamento (nó puro recalculado depois do `SetHealth`, veja a seção 5).
- **GDD v2** escrito e revisado: os nomes de assets conferem com os pacotes.
- **Loop da partida, ainda sem GAS** (testado em PIE em 15/10, às 03:20). Os Blueprints ficam em
  `/Game/NexusRoyale/Blueprints/{Core,Match,Loot}`, e os grafos estão em DSL em `Unreal/Blueprints/<BP>__<Grafo>.dsl`.
  - **`GM_NexusRoyale`:** é o GameMode do `L_Island` (override no World Settings). Filho do GM do
    template, com o pawn `BP_HeroBase`. Meio segundo depois do início:
    - cria um `BP_DropShip` numa reta aleatória sobre a ilha, a 140 m de altura;
    - embarca todos os heróis;
    - liga a tempestade.
  - **`BP_HeroBase`:** cópia do herói Quaternius montado (corpo, roupa e cabelo).
    - Espaço: salta do dirigível, mas só quando ele está a menos de 190 m do centro. Fora dele, é o
      pulo normal.
    - Na queda, mergulha até -26 m/s. A 30 m do chão, plana a -4,5 m/s. Ao pousar, volta ao normal.
    - F: interage com o objeto mais próximo (`IA_Interact`, mapeado no `IMC_Default`).
    - Os eventos de input foram ligados por `Unreal/ue_br_wire_input.py`, porque a DSL não declara
      evento de input.
  - **`BP_StormController`:** posicionado no centro do nível.
    - Lê `/Game/NexusRoyale/Data/CT_Storm`, importado de `Unreal/Data/CT_Storm.csv`, com 6 fases. Os
      tempos são os do GDD §13; os raios são provisórios.
    - Os centros são sorteados de modo que cada círculo caiba no anterior. A parede é o `SM_StormWall`
      escalado.
    - Tem os dispatchers `OnPhaseStarted` e `OnPhaseEnded`, este último com o piso de nível.
    - A cada 1 s, chama `StormTick(%)` em quem está fora do círculo.
    - `DebugSkipTo(segundos)` adianta o relógio para testes.
  - **Baús:** os 32 `SM_Chest` do nível viraram `BP_LootChest`, nas mesmas posições.
    - Ao abrir, sorteiam as raridades do GDD §8.4: 1 item da tabela do GDD §8.1, 1 consumível e 40% de
      chance de um grimório.
    - Cada sorteio vira um `BP_Pickup` com malha da Quaternius e luz na cor da raridade.
    - As malhas do Ultimate RPG e do Ultimate Food foram importadas em `/Game/Quaternius/Items/` (27).
- **Planilha de TTK** (tempo para matar): [Design/Simulacao_TTK.xlsx](Design/Simulacao_TTK.xlsx).
  - Simula duelos passo a passo (0,1 s) entre as 4 builds do GDD 4.2 nos níveis 1, 5 e 10, com
    entradas editáveis, Resumo com cores e um Duelo livre.
  - **O pacote B de ajustes foi aplicado ao GDD em 15/10, com o aval do usuário:**
    - Força sem armadura e k = 0,04;
    - Vitalidade com +30 de vida por ponto e +80 de vida por nível;
    - Guerreiro com golpe de 65 e Feiticeiro com dardo de 60;
    - Místico com feixe de 100/s e roubo de vida de 10%, e Sifão com 6%;
    - ultimate sem bônus no nível 10 e Chuva de Meteoros com 1 meteoro por alvo;
    - bônus de dano de categorias diferentes agora somam (GDD §9).
  - **Resultado:** 45 de 48 confrontos ficam entre 2 e 12 s. Antes eram 27. Os 3 de fora são
    Místico resistente contra tanque, com 12,1–12,6 s.
  - **Ao mudar números do GDD,** atualize as entradas da planilha. O gerador em Python fica fora do
    projeto, em `C:\Users\vulgo\AppData\Roaming\Claude\side-session-notes\local_7e223023-05ea-4a10-89bd-d0257a575c6c\ttk_scripts\`.
- **Mapa v2, a ilha de cerca de 1 km** (design em [Design/Mapa.md](Design/Mapa.md)).
  - **Layout aprovado** pelo usuário, com a direção de arte cartoon + aquarela.
    - Os dados ficam em `Unreal/Data/Mapa/mapa_v2.json`, e o gerador é `Unreal/mapa_gerar.py`.
    - A saída fica em `gerado/`: relevo, 8 camadas, imagens do mapa e `mapa_ue.json`.
  - **Na Unreal** (scripts `Unreal/ue_mapa_assets.py` e `Unreal/ue_mapa_nivel.py`):
    - em `/Game/NexusRoyale/Map/V2/` estão o `M_Terreno_V2` (8 camadas com variação de pigmento),
      o `T_Pigmento`, o `T_Mapa_Base` e o `T_Mapa_Aquarela`;
    - o nível novo `/Game/NexusRoyale/Maps/L_Ilha` tem sol, céu, névoa e PlayerStart provisório.
  - **Nível:** o editor foi reaberto às 10:58 no `L_Island`, pela sessão dos creeps. O `L_Ilha`
    continua salvo, com luz e céu.
  - **Esperando o usuário:** importar o Landscape à mão no `L_Ilha`. A API Python da 5.8 não cria
    Landscape nem LayerInfo. O passo a passo está em Design/Mapa.md, "Como montar", passo 1. Em
    15/10, às 11:00, o usuário disse que não conseguia agora e pediu para seguir com os widgets.
  - **Interface dos mapas, em andamento desde 11:00.** Fica em `/Game/NexusRoyale/UI/Mapa/`, e os
    scripts são `Unreal/ue_mapa_ui_material.py` e `Unreal/ue_mapa_ui_build.py`.
    - **`T_Mapa_UI`:** aquarela com os nomes e a grade A–J × 1–10 sobre ±560 m.
    - **`MPC_Mapa`:** guarda os valores globais (jogador, tempestade atual e próxima, rota do
      dirigível, marcador).
    - **`M_UI_Mapa`:** um nó Custom em HLSL. Duas instâncias usam esse material:
      - `MI_UI_Minimapa`: redondo, 150 m em volta do jogador, com o norte para cima;
      - `MI_UI_MapaCompleto`: a ilha inteira.
    - **`WBP_Mapa`:** uma `Image` com o material. A cada tick, escreve na MPC o jogador, o
      `BP_StormController` e o `BP_DropShip`.
    - **`HUD_NexusRoyale`:**
      - mostra o minimapa no canto superior direito (260 px);
      - mostra o mapa em tela cheia (900 px) na tecla **M** (`IA_Mapa`, adicionado ao
        `IMC_Default`);
      - abre o mapa sozinho enquanto o herói está no dirigível (o mapa da queda) e fecha no salto.
    - **`GM_NexusRoyale`:** o `HUD Class` agora é `HUD_NexusRoyale`. Foi a única mudança num asset
      da sessão de gameplay.
  - **Depois do Landscape, pela ordem:**
    1. conferir a orientação;
    2. água (mar, lagos e rio);
    3. POIs;
    4. vegetação (PCG ou HISM);
    5. levar o dirigível, a tempestade e os baús para o `L_Ilha` e torná-lo o mapa padrão.
  - **Tempestade:** os raios precisam acompanhar o mapa. A proposta está em Design/Mapa.md.

### Sem verificação ou com problema conhecido

- **Creeps** (o que foi testado está na seção 9, entrada das 10:55):
  - o XP já chega ao herói pelo `DarXP` no `Die` (testado: +30 por Imp). O dispatcher
    `OnCreepKilled` continua sem ninguém escutando;
  - **não tem drop** (GDD §12: 50% de comida ou poção no pequeno, grimório no médio);
  - não tem rede: o `Think` só roda com autoridade e os creeps não estão marcados para replicar;
  - o Imp usa só `Imp_Body`. As malhas `Imp_Chains`, `Imp_Mace`, `Imp_Shorts` e `Imp_SpikedCollar`
    (e as do Puglin) não estão no BP;
  - **sem NavMesh,** o creep anda em linha reta e pode enroscar em árvore ou pedra. Os acampamentos
    precisam ficar em clareiras;
  - o Puglin e o acampamento médio não foram testados em PIE;
  - o ataque acerta no início da animação, sem esperar o golpe.
- **Cópia da ilha.** `Content/NexusRoyale/Map/_tmp/` tem uma cópia de `SM_Island` e `M_Island`. O
  último passo, renomear a ilha nova, falhou porque sobrou um redirector. É preciso:
  1. conferir qual dos dois assets o nível usa;
  2. consolidar num só e rodar *Fix Up Redirectors*.
- **Restos da v1 no projeto.** A lista completa está no GDD, seção 16.1, em "Remover". Inclui
  `BP_Hero_*`, `SK_Guardian`, `SM_Build_*`, as torres e o Nexus, além das pastas vazias
  `NexusRoyale/Heroes/SK_Boto`, `SK_Caramelo` e `SK_PombaGira`.
- **Scripts que ainda geram coisas da v1:**
  - `Export/map_layout.json` e `Unreal/import_nexus_assets.py` ainda posicionam torres, Nexus e
    fragmentos;
  - `Blender/scripts/build_all.py` ainda gera os heróis e as peças de construção antigos.
- O GameMode do template (`BP_ThirdPersonGameMode`) ainda usa o `BP_Hero_Brakka` da v1, mas o
  `L_Island` já usa o `GM_NexusRoyale`.
- **MVP (sessão "MVP rollout"), sem verificar:**
  - a morte pela **tempestade** (o dano está ligado, mas o teste foi pelos creeps);
  - o **nível 2 em diante**, na prática: o `GanharXP` foi conferido no código, e o teste chegou a 90 XP;
  - equipamento **trocando** com o do slot (`Trocou`) e consumíveis cheios (`Cheio`);
  - o Puglin contra as magias;
  - **no jogo empacotado (0.1.0), o minimapa do canto superior direito não aparece.** O log não cita
    `WBP_Mapa` nem `HUD_NexusRoyale`. Confira se o `HUD Class` chega ao jogo cozido. A praça também mostra
    as estátuas dos heróis da v1;
  - o jogo empacotado só foi aberto por 40 s: não foi jogado de ponta a ponta.
- **Muralha de Gelo e Chuva de Meteoros.** Testadas em PIE nas sessões "Kit do Feiticeiro" (seção 9,
  entrada das 13:52) e "Testar muralha contra creeps e chão em chamas" (entrada das 15:37). Já
  conferidos: Bola de Fogo contra a muralha, chão em chamas e o visual dos meteoros e do disco.
  - **Creeps contra a muralha: corrigido às 16:35.** Antes, eles paravam encostados nela e ficavam
    empurrando enquanto ela durasse. Agora batem nela (veja "Creeps" acima). Testado em PIE, com a
    muralha durando 30 s só no PIE:
    - os 3 Imps tiram 12 por golpe, 36 a cada ~1,7 s, e a muralha quebra em ~18 s;
    - com o herói colado na muralha, a 0,8–1,6 m dos Imps (dentro do alcance), ele não levou dano;
    - quando a muralha quebrou, eles foram para o herói na hora.

    Com os 6 s do GDD, 3 Imps tiram ~130 e a muralha aguenta;
  - **visual:** os meteoros e o clarão da explosão saem creme/amarelo-claros, não laranja (material
    unlit `M_Projetil` estourando no tonemapper). O chão em chamas é o mesmo disco do aviso, só mais
    claro, sem efeito de fogo, e de longe vira uma linha fina. Capturas em
    `Export/Previews/teste_chuva_*.png` (a pasta `Export/` fica fora do git);
  - **sem verificar:**
    - "sem mana" no E e no X, e a ultimate presa até o nível 6 ("nível 6" no HUD): no MVP o
      `BP_HeroBase` libera a ultimate no nível 1;
    - quem lança dentro do próprio chão em chamas (o código ignora o instigador, mas não foi testado);
    - meteoros e chamas contra uma muralha (os meteoros ferem estruturas; as chamas, só pawns);
    - a animação de golpe dos creeps contra a muralha (só o dano foi conferido), o Puglin batendo
      nela e a muralha com os 6 s de verdade (a conta está acima);
  - **mistério da câmera:** no primeiro PIE da sessão "Kit do Feiticeiro" (15:04), o braço da câmera
    do herói estava em 0 m (`DefaultCameraDistance` 0), e a muralha ia parar a 15 m, longe da mira.
    Depois que a partida recomeçou (15:19), o braço voltou a 4 m e a mira acertou. **Não se repetiu**
    nos três inícios de partida das 15:38–16:03 (braço em 4 m). A causa não foi achada; se a câmera
    aparecer colada no herói, comece por aí;
  - "queima vegetação" (GDD §6.4) não existe, porque ainda não há vegetação que queime. Também não
    há rede.
- **MVP, limites conhecidos:**
  - a magia sai do peito do herói, sem animação de lançar;
  - os grimórios vão para o inventário, mas ainda não viram magias E e R;
  - o arquétipo e a build estão fixos no `Habilidades` (Feiticeiro de Fogo); não há tela de montagem;
  - mira de terceira pessoa: a magia vai até o ponto sob a mira e sai do herói, então perto de
    paredes pode bater nelas;
  - creeps continuam batendo no corpo depois da morte (o dano é ignorado);
  - a mensagem `PrintString` do `StormTick` e o "Dano: -X" do herói continuam na tela (debug).
- **Lacunas do loop da partida** (marcadas com `TODO` nas DSLs):
  - **não tem rede:** o salto, o F e as magias não são RPC. Funciona só no PIE solo;
  - o HUD ainda não tem prompt do F nem relógio da tempestade;
  - **os raios da tempestade, a rota do dirigível e o `DropRadius` (190 m) são da ilha de 400 m.**
    Ajustar no `CT_Storm.csv` e nos valores padrão quando o mapa v2 entrar;
  - **o `L_Island` ainda tem os restos da v1:** Nexus, torres, fragmentos, poções de escudo e
    plataformas de salto;
  - o PIE avisa que a memória de vídeo estourou em cerca de 500 MB na RX 570. **Às 15:44 o editor
    caiu** ao recomeçar o PIE ("Out of video memory", D3D12), **e de novo às 16:17**. Veja a
    pegadinha na seção 5.

### Próximos passos

Etapa 1 ("Núcleo") do roadmap, no GDD seção 15. Já estão feitos: GAS com vida e mana, Feiticeiro
fixo, Bola de Fogo, Muralha de Gelo, Chuva de Meteoros, acampamento de Imps, baú comum, tempestade,
XP e nível (o MVP em "Pronto"). Falta:

1. ~~**GAS**~~ **compilado e ligado em 15/10, às 12:00** (veja "MVP jogável" em "Pronto"). O que
   segue é a descrição original do módulo, em `Unreal/NexusRoyale/Source/NexusRoyale/`:
   - **`GAS/AS_Hero`:** os atributos do GDD §16, com os nomes do GDD. Também tem os meta-atributos
     `Dano` (passa pela armadura, 0,04·A/(1+0,04·A)), `DanoVerdadeiro` e `Cura`.
   - **`GAS/NRAbilitySystemComponent`:** fica no próprio herói, e não no PlayerState como diz o GDD
     §16. Num BR sem respawn não faz diferença, e assim não é preciso C++ no Character.
     - Calcula vida, mana e bônus a partir de arquétipo + build + nível. Os coeficientes do GDD §4.2,
       §5 e §7.1 são editáveis no Details.
     - Faz a regeneração e marca "em combate" por 5 s.
     - Expõe ao Blueprint `AplicarDano`, `AplicarDanoTempestade`, `Curar`, `RestaurarMana` e
       `AplicarBonus`, e os eventos `OnVidaMudou`, `OnManaMudou`, `OnDanoRecebido` e `OnMorreu`.
   - **`GAS/NRGameplayEffects`:** efeitos com SetByCaller por nome, sem tags.
   - **`Items/`:** a linha da tabela `FNRItemRow`; o `UNRInventoryComponent`, com 4 slots de
     equipamento, 3 de consumível, os grimórios, a troca que solta o item antigo e o consumo com
     lentidão; e o `UNRItemLibrary`, com `SortearItem`, `CarregarMalha` e as raridades.
   - **`UI/NRHudWidget`:** base do WBP_HUD (barras de vida e mana, consumíveis e equipados).
   - **Tabela de itens:** `Unreal/Data/DT_Itens.csv`, com 33 linhas, gerada por
     `Unreal/Data/gerar_dt_itens.py` com os números do GDD §8.
   - **Para retomar depois do Visual Studio:**
     1. fechar a Unreal;
     2. `python -I Unreal/ue_gas_compilar.py --abrir`, que acrescenta o módulo e o plugin
        GameplayAbilities ao `.uproject`, compila e abre o editor em inglês;
     3. `python Unreal/ue_py.py Unreal/ue_gas_setup.py`, que cria o DT_Itens e põe os componentes
        Habilidades e Inventario no BP_HeroBase, com o Feiticeiro de Fogo;
     4. pela DSL: `StormTick` chamando `AplicarDanoTempestade`; o pickup com ItemId e raridade
        chamando `Inventario.Pegar`; o baú usando `SortearItem`; as teclas 1-3; `OnMorreu`; e o
        WBP_HUD na tela.
   - **Os passos 1 a 4 acima foram feitos.** O `.uproject` agora lista o módulo e o plugin
     GameplayAbilities. O editor carrega a DLL já compilada; se alguém mudar o C++, precisa
     recompilar com o editor fechado antes de abrir.
2. Feiticeiro: ~~Muralha de Gelo e Chuva de Meteoros~~ **feitas em 15/10, às 15:30**, no
   `UNRCombateComponent` (veja "MVP jogável" em "Pronto"). Faltam a passiva Canalizador, a animação de
   lançar e devolver a ultimate ao nível 6 quando houver mais acampamentos (`NIVEL_ULTIMATE` no
   `ue_mvp_setup.py`). A migração para Gameplay Abilities (`GA_*`, GDD §16) fica para a etapa 2, junto
   com os grimórios trocando E e R. Os creeps já batem na muralha que os bloqueia (feito às 16:35).
3. ~~Acampamento de Imps~~ (feito, com GAS). Falta: drop dos creeps, levar os 21 acampamentos para o
   `L_Ilha` com `place_camps()` e o `mapa_ue.json`, e o elite (Puglin Ancião).
4. XP e nível: falta o `OnPhaseEnded` (piso de nível) e a escolha de mutação a cada nível (GDD §7).
5. Grimórios virando as magias E e R; tela de montagem (arquétipo + 20 pontos); prompt do F e relógio
   da tempestade no HUD.
6. Corrigir o minimapa no jogo empacotado e publicar a 0.1.1 com `Publicar-versao.bat`. Isso também
   testa a atualização de uma versão para outra pelo launcher.
7. Multiplayer (o usuário perguntou em 15/10 se já dava para jogar online; não dá). Há um cartão de
   sessão proposto: listen server com a Steam (app 480) ou EOS.

A arquitetura alvo está no GDD, seção 16: `AS_Hero` em C++, `PS_Hero`, `BP_HeroBase`, `GA_*`/`GE_*`,
`DT_*`/`DA_*`, `BP_StormController` e outros.

### Pendências do usuário

- ~~**Instalar o Visual Studio.**~~ **Instalado às 11:33:** VS Community 2026 18.11 em
  `D:\VisualStudio\Community`, com o MSVC 14.50.35717 e o 14.51.36231. O UBT escolhe o 14.50.35717,
  que o `Windows_SDK.json` marca como banido por erros internos de compilação, mas o módulo compilou
  sem erro. Se aparecer "internal compiler error", force o 14.51 no `BuildConfiguration.xml`. O
  histórico abaixo fica só como registro.
  - O `AttributeSet` do GAS só pode ser escrito em C++.
  - A UE 5.8 aceita o VS 2026 (MSVC 14.50.35723 ou mais novo) ou o VS 2022 17.14 (MSVC 14.44.35211
    ou mais novo). Veja `Engine/Config/Windows/Windows_SDK.json`.
  - Comando sugerido, que instala tudo no D::
    `winget install --id Microsoft.VisualStudio.Community --source winget --override "--passive --wait --norestart --installPath D:\VisualStudio\Community --path cache=D:\VisualStudio\Cache --path shared=D:\VisualStudio\Shared --add Microsoft.VisualStudio.Workload.NativeGame --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.VC.14.50.18.0.x86.x64 --add Microsoft.Net.Component.4.6.2.TargetingPack --add Component.Unreal.Ide --add Component.Unreal.Debugger"`
  - **Às 11:00 continuava sem instalar.** O usuário respondeu que tinha terminado, mas não existia
    instalação nenhuma: o `vswhere` vinha vazio, não havia `D:\VisualStudio` e não havia log do
    instalador nem do winget. Talvez o comando tenha falhado ou o UAC tenha sido recusado. Confira
    com `vswhere` antes de compilar.
  - **Às 11:35 a instalação começou, rodada pelo Claude a pedido do usuário.** O usuário confirmou
    o download (cerca de 8–10 GB), a licença do VS Community e o UAC.
    - Foi o VS 2026 Community 18.11 pelo winget, com o comando acima, em `D:\VisualStudio`.
    - Às 11:45 estava em cerca de 3 GB.
    - **O C: tem só 5,9 GB livres:** confira se sobrou espaço depois.
- **Criar um arquivo de paginação no D:** (inicial 16384 MB, máximo 32768 MB). A Unreal já travou
  por falta de memória, e o C: está quase cheio.

## 4. Ambiente

| Item | Onde / valor |
|---|---|
| Unreal Engine 5.8.3 | `D:\Epic Games\UE_5.8` |
| Projeto Unreal | `Unreal\NexusRoyale\NexusRoyale.uproject`, com o editor em pt-BR |
| Blender 5.2 | `D:\blender\blender.exe`. Python embutido: `D:\blender\5.2\python\bin\python.exe` |
| Python do sistema | 3.14 (`python`) |
| Máquina | Windows 10, 16 GB de RAM, Radeon RX 570 com 4 GB. O C: está quase cheio, então tudo vai no D: |
| Git | Repositório git criado em 15/10, por volta das 13:30, pela sessão "Git e versão jogável" (branch `main`, com LFS). Antes disso não havia histórico |

## 5. Como controlar a Unreal e o Blender

### Unreal

O servidor MCP sobe junto com o editor em `http://127.0.0.1:8000/mcp`, configurado no `.mcp.json` da
raiz. O editor também aceita Python remoto, ativado em Project Settings > Python.

O conector MCP nativo da IA falha se o editor não estava aberto quando a sessão começou. Nesse caso,
use os scripts de `Unreal/`:

| Script | Uso |
|---|---|
| `python Unreal/ue_py.py arquivo.py` ou `-c "..."` | Roda Python dentro do editor aberto |
| `python Unreal/unreal_mcp.py calls.json` | Cliente MCP direto por HTTP |
| `python Unreal/ue_tool.py <Toolset> <ferramenta> '<json>'` | Chama uma ferramenta do MCP (BlueprintTools, AssetTools, DataTableTools…) |
| `python Unreal/ue_write_dsl.py <grafo> <arquivo.dsl> [<bp>]` | Grava um grafo de Blueprint a partir de uma DSL e compila |
| `python Unreal/ue_find_nodes.py <grafo> <termos…>` | Procura os IDs de nó para a DSL |
| `python Unreal/ue_capture.py saida.png [x y z pitch yaw]` | Captura o viewport **do mundo do editor**. Com `--editor`, captura a janela inteira (outra janela flutuante pode cobrir o PIE) |
| `Unreal/pie_capture.py` (via `ue_py.py -c`) | Screenshot do **jogo** durante o PIE, opcionalmente virando a câmera (`AIM`) e com atraso (`DELAY`) |
| `Unreal/pie_creeps.py` (via `ue_py.py -c "ACT='...'"`) | Testa os acampamentos no PIE: `land`, `near`, `away`, `poke`, `kill` e `state` |
| `Unreal/pie_combate.py` (via `ue_py.py -c "ACT='...'"`) | Testa o MVP no PIE: `heroi` (vida, mana, XP, recargas), `dardo`, `fogo`, `muralha`, `meteoros`, `tecla1..3` (input de verdade), `mirar_chao` e `mirar_acampamento` (só a mira), `*_direto` (sem input), `estruturas`, `muralha_dano`, `chuvas`, `xp`, `bau`, `pegar` e `inventario`. A lista completa está no docstring |
| `Unreal/pie_gravar.py` (via `ue_py.py -c "ACT='iniciar'; SEG=8; ..."`) | Grava quadro a quadro, pelo callback de pós-tick do Slate: a vida dos creeps e do herói a cada mudança, a posição dos creeps em relação à muralha, as estruturas, as chuvas e os projéteis (onde nasceram e onde sumiram). `ACT='mostrar'` imprime. Os tempos são do relógio do jogo |

**Pegadinhas:**

- **Os IDs de nó da DSL seguem o idioma em que o editor abriu.** Em pt-BR eles vêm como "Ator|…", e
  todas as DSLs usam os IDs em inglês.
  - Trocar o idioma com o editor aberto (`ue_culture.py`) **não** troca os IDs, porque o catálogo
    foi montado na abertura.
  - **O que funciona:** fechar o editor e abrir com `UnrealEditor.exe <uproject> -culture=en`. Isso
    vale só para essa execução.
  - Depois, para voltar a interface ao português sem perder os IDs em inglês:
    `python Unreal/ue_py.py -c "import unreal; unreal.InternationalizationLibrary.set_current_culture('pt-BR', False)"`.
- **DSL (`write_graph_dsl`), coisas que só se descobre testando:**
  - **Variável bool perde o "b" no nó:** `bStarted` vira `Variables|Default|GetStarted` e `SetStarted`.
  - **`(return)` dentro de `for` é descartado em silêncio.** Use uma variável de controle (veja
    `BP_StormController__UpdateCircle.dsl`).
  - **A DSL não cria eventos de input** (`EnhancedActionEvents`). Use `create_node` + `connect_pins`,
    como em `Unreal/ue_br_wire_input.py`.
  - **Override de função de um BP pai sem retorno vira evento:** `(event EventInteract (Hero) …)`.
  - **Chamar função de outro BP:** `Class|BPHeroBase|StormTick :self alvo`. Para ler uma variável
    de outro BP: `Class|BPInteractable|GetPrompt :self alvo`.
  - **Gravar de novo substitui** aquele evento ou função. Os outros eventos do grafo ficam.
  - **Não existe `IsValid` puro na DSL.** `Utilities|IsValid` é a macro com exec. Dentro de uma
    expressão, como `(if (not (Utilities|IsValid x)) …)`, o `if` **some em silêncio** e a gravação
    diz que deu certo. Use `(Utilities|IsValid x (:"Is Valid" …) (:"Is Not Valid" …))` e **leia o
    grafo de volta** (`read_graph_dsl`) depois de gravar.
  - **Eventos de dano levam prefixo:** `(event Game|Damage|EventAnyDamage (Damage DamageType InstigatedBy DamageCauser) …)`.
  - **Limpar uma variável de objeto:** `(Variables|Default|SetTarget)`, sem argumento. Não existe `None`.
  - **Chamar função do próprio BP em outra instância:** `(CallFunction|Alert :self outro …)`. O
    `Class|BPCreep|…` só aparece em grafos de outros BPs.
  - **`bind` de expressão pura NÃO guarda o valor.** O Blueprint recalcula nós puros a cada uso.
    `(bind hp (- (GetHealth) Damage)) (SetHealth hp) (if (<= hp 0) …)` testa "vida nova − dano" e
    matava o creep. Depois de um `Set`, leia a variável de novo (`(<= (GetHealth) 0)`), ou guarde
    em variável de verdade.
  - **`Pawn|GetControlRotation` é a versão do Controller.** Com um pawn no `:self`, a DSL inventa uma
    conversão por `LastHitBy` (nulo, e dá "Accessed None"). Passe o controller:
    `(Pawn|GetControlRotation :self (Game|GetPlayerController :PlayerIndex 0))`.
  - **Funções C++ com vários pinos de saída são ruins na DSL.** Prefira funções com só o retorno, mais
    getters (`PegarDoChao` + `ItemQueFicaNoChao`).
  - **Na leitura de volta, argumentos iguais ao padrão somem** (enum 0, int 0), e isso é normal.
- **Injetar input no PIE:** filtre `EnhancedInputLocalPlayerSubsystem` sem o `Default__…`, porque o
  nome do objeto padrão também contém "LocalPlayer" e a ordem do `ObjectIterator` varia. O
  `pie_press.py` e o `pie_combate.py` já fazem isso. A injeção só vale no próximo frame; para ler o
  efeito, faça outra chamada.
  - **Girar a câmera e apertar a tecla na mesma chamada usa a direção antiga,** porque o input é
    processado antes de a câmera se atualizar. Gire numa chamada (`mirar_chao`, `mirar_acampamento`) e
    aperte na seguinte, com `SO_TECLA=1`.
- **O Python remoto (`ue_py.py -c`) guarda as variáveis globais entre chamadas,** inclusive as de
  outras sessões. Um `SO_TECLA=1` esquecido fazia o `pie_combate.py` pular a mira em silêncio. Agora
  o script lê e apaga as opções (`SO_TECLA`, `PITCH`, `DANO`, `N`) no começo. Faça o mesmo em
  scripts novos.
- **`set_editor_property` num componente de ator durante o PIE reconstrói o ator** (roda o construction
  script de novo). Os componentes C++ recomeçam: o `Habilidades` recalcula a vida e a mana e o
  `Combate` religa as teclas. O Blueprint fica marcado como sujo no editor, mesmo sem o asset mudar.
  Para mudar um número só no PIE (como a duração da muralha), tudo bem, mas confira os pacotes sujos
  depois.
  - **Melhor:** `set_editor_property(nome, valor, unreal.PropertyAccessChangeNotifyMode.NEVER)` não
    dispara o PostEditChange, então não reconstrói o ator nem suja o Blueprint. Para um struct, leia,
    mude o campo e grave o struct inteiro (assim a muralha durou 30 s só no PIE).
- **Variável de Blueprint que não é "Instance Editable"** (como a `Health` do creep) dá "cannot be
  edited on instances" no `set_editor_property`. Num teste, um `ApplyDamage` **negativo sem
  instigador** sobe a vida pela lógica do próprio BP, sem alertar o acampamento. Para prender um creep
  no lugar, use `CharacterMovementComponent.disable_movement()` (e `set_movement_mode(MOVE_WALKING)`
  para soltar).
- **Com o editor em segundo plano, o PIE roda a cerca de 3 quadros por segundo** (o log diz
  `max tick rate 3`). Cada chamada do `ue_py.py` leva ~2 s de jogo, e o tempo entre uma chamada e
  outra também passa no jogo. A muralha de 6 s some antes da próxima chamada, e os creeps matam o
  herói se ninguém olhar. Por isso:
  - faça a sequência inteira num comando só;
  - veja o que aconteceu entre as chamadas com o `Unreal/pie_gravar.py`;
  - para capturar coisa rápida (meteoros caindo), deixe o jogo lento com
    `unreal.GameplayStatics.set_global_time_dilation(w, 0.1)` e volte a 1.0 no fim.
- **O segundo ou terceiro mundo de PIE na mesma abertura do editor derruba o editor por falta de
  memória de vídeo.** O erro é "Out of video memory trying to allocate a rendering resource" (D3D12,
  na RX 570):
  - às 15:44, no segundo PIE;
  - às 16:17, no terceiro mundo de PIE. O recomeço da partida depois da morte do herói também cria
    um mundo novo.

  Por isso:
  - **um PIE por abertura do editor.** Para outro PIE, confira os pacotes sujos, feche com
    `unreal.SystemLibrary.quit_editor()` e reabra com `-culture=en` (de 3 a 6 min);
  - **não deixe o herói morrer** no meio de um teste;
  - **num editor recém-aberto, o PIE demora a começar.** Espere o relógio do jogo passar de 3 s antes
    do `pie_creeps.py land`. Senão, o GameMode embarca o herói no dirigível depois do pouso.
- **A mira do `mirar_acampamento` pode cair curta** quando a câmera ainda não se ajustou: o pitch sai
  da posição antiga da câmera, e a chuva caiu a 6 m do herói em vez de 12 m. Confira onde a chuva
  apareceu (`ACT='chuvas'` ou o `pie_gravar.py`). Com o braço em 4 m e o chão plano, o pitch para
  acertar o centro do acampamento a 12 m é cerca de -4,9°.
- **Captura com HUD:** `ue_capture.py <png> --editor` mostra o UMG. O `pie_capture.py` (screenshot de
  alta resolução) renderiza só a cena, sem interface.
- **Iniciar e parar o PIE pelo Python:** `LevelEditorSubsystem.editor_request_begin_play()` e
  `editor_request_end_play()` (o `EditorApp StartPIE` do MCP exige um JSON de opções).
- **`add_object_variable` do MCP cria `int` para algumas classes**, como `CurveTable`. Corrija com
  Python: `BlueprintEditorLibrary.change_member_variable_type` usando um `EdGraphPinType` montado por
  `import_text`.
- **Durante o PIE, o `EditorAssetLibrary` recusa chamadas.** Para ver o estado, filtre os atores pelo
  nome da classe (`Unreal/pie_state.py`).
  - Para testar input de verdade: `Unreal/pie_press.py` injeta a ação pelo Enhanced Input.
  - Para chamar funções de BP: `actor.call_method("Nome", (args,))`.
- **`unreal.Rotator(a, b, c)` no Python é (roll, pitch, yaw),** não (pitch, yaw, roll). Use nomes:
  `unreal.Rotator(roll=0, pitch=0, yaw=-90)`. Era por isso que os creeps estavam deitados.
- **Durante o PIE, o `CaptureViewport` mostra o mundo do editor,** sem nada do que nasceu no jogo.
  Use `Unreal/pie_capture.py` (`AutomationLibrary.take_high_res_screenshot`). O Python também não
  consegue criar ator no mundo do PIE nem se ligar a dispatchers de BP.
- **Várias sessões no mesmo editor:** o Python remoto aceita uma conexão por vez. Se der "Remote party
  failed to attempt the command socket connection", tente de novo. Um PIE aberto trava os
  `EditorAssetLibrary` das outras sessões, então feche o PIE logo. E não use
  `save_dirty_packages` às cegas, porque ele salva o trabalho das outras sessões também.
- **No Git Bash, caminhos `/Game/...` viram caminhos do Windows.** Use `MSYS_NO_PATHCONV=1` antes do
  comando.
- **Importações grandes:** importe em lotes pequenos, salve e rode `unreal.SystemLibrary.collect_garbage()`
  entre um lote e outro.
- **Se o MCP parar de responder,** veja se o editor fechou. Ele fecha sozinho quando o usuário
  instala alguma coisa ou quando falta memória. O log fica em `Unreal/NexusRoyale/Saved/Logs/`.

### Release (versão instalável)

- **Fluxo:** `Unreal/ue_release.py`. Rode com a Unreal **fechada**, porque o cook precisa da RAM.
  - `tudo` faz tudo de uma vez: sobe a versão (`ProjectVersion` do `DefaultGame.ini`) se a atual já foi
    publicada, empacota (BuildCookRun), zipa em partes de até 1,9 GB, compila o instalador e cria a
    Release `v<versão>` em `holaluiz/MOBA-BR` pelo `gh`. O `Publicar-versao.bat` da raiz faz o mesmo.
  - Também existem as ações separadas `versao`, `compilar`, `empacotar [--sem-cook]`, `launcher`, `zipar`
    e `publicar`. O `--sem-cook` refaz só o stage, o pak e a cópia, reaproveitando o último cook.
  - **Tempo nesta máquina:** compilar 7 min, o primeiro cook 15 min e os seguintes 5 min (cache de
    shaders), o stage menos de 1 min e o zip 1 min.
  - A saída fica em `D:\NexusRoyale_Builds\<versão>\`: `Windows/` (o jogo), o zip, o
    `NexusRoyale-Instalador.exe`, o `manifest.json` e os logs.
- **Launcher:** `Launcher/NexusRoyaleLauncher.cs` (C# 5, compilado pelo `csc` do .NET 4.8 que vem no
  Windows). Detalhes no LEIA-ME e no cabeçalho do `.cs`. Se mudar o launcher, suba a constante `Versao`:
  os launchers instalados se trocam pelo da próxima Release.
- **O launcher só vê versões publicadas como Release.** Um `git push` sozinho não chega aos jogadores,
  porque o GitHub não compila Unreal. Quem publica é o `tudo`.
- **Pegadinhas do empacotamento:**
  - **Erro 1455 no UBA** ("VirtualAlloc failed") logo no começo da compilação: falta memória virtual
    (o arquivo de paginação fica no C:, que está cheio). O script já passa `-NoUBA`.
  - **"Failure - 2 error(s)" no fim do cook (ExitCode 25),** com tudo cozido: era a regra
    `GameFeatureData` do Asset Manager, que algum plugin exige. Foi posta no `DefaultGame.ini`.
  - **O stage barra pastas com nome de plataforma** (`Apple`, `Android`, `Linux`, `Mac`, `IOS`…). A maçã
    do Ultimate Food fica em `Quaternius/Items/Apple`, então ela foi liberada com
    `[Staging] +AllowedDirectories`. Asset novo numa pasta com esses nomes precisa de outra linha.

### Blender

- O add-on do usuário é o **"MCP for Blender"** (Siddharth Ahuja, porta 9876), e ele **não é
  compatível** com o conector Blender do Claude. Use `Blender/scripts/live_send.py` para mandar um
  script ao Blender aberto, ou rode sem interface com `blender --background --factory-startup --python …`.
- **Para renders, use o Workbench.** O EEVEE sem interface derruba o driver da AMD
  (`atio6axx.dll`) quando a Unreal também está usando a placa de vídeo.

## 6. Pipeline de assets (decisões não óbvias)

- **Packs da Quaternius escolhidos pelo usuário.** A licença permite uso em jogos. Os zips estão em
  `Quaternius/_zips`, e cada pack foi extraído na sua pasta.

  | Pack | Uso no jogo |
  |---|---|
  | Universal Base Characters | Corpos |
  | Universal Animation Library 1 e 2 | Animações |
  | Modular Outfits Fantasy | Roupas |
  | Bestiary | Creeps (Imp e Puglin) |
  | Stylized Nature, Medieval Village e Downtown City MegaKits | Cenário |
  | Fantasy Props | Props |
  | Ultimate Food | Consumíveis de cura |
  | Ultimate RPG | Mutações e melhorias |

- **Esqueleto compartilhado.** Corpos, roupas, cabelos e as duas bibliotecas de animação usam o mesmo
  esqueleto: `/Game/Quaternius/Animations/UAL1/.../UAL1_Standard_Skeleton`.
  - Ele é forçado na importação por uma cópia do pipeline Interchange (`make_pipeline` em
    `Unreal/ue_q_lib.py`).
  - Os scripts rodam nesta ordem: `ue_q_step1_anims.py`, `ue_q_step1b_ual2.py`, `ue_q_step2_chars.py`,
    `ue_q_step3_abp.py`, `ue_q_step4_heroes.py`, `ue_q_step5_materials.py` e `ue_q_step6_outfits.py`.
- **`ABP_Hero`** (em `/Game/Quaternius/Anims/Hero/`) é o ABP_Unarmed do template, retargetado e com
  os clipes trocados pelos da UAL. **O nó de Control Rig de IK de pé foi removido** porque torcia as
  pernas no esqueleto da Quaternius.
- **Visual do herói:**
  - O material `M_HeroHead` esconde todo o corpo base menos a cabeça, para o corpo não atravessar
    a roupa.
  - Ele faz isso com uma máscara de opacidade pela altura antes do skinning, passada por um
    VertexInterpolator, porque `PreSkinnedPosition` só funciona no vertex shader.
  - Roupa e cabelo são SkeletalMeshComponents que rodam o mesmo ABP.
- **Creeps do Bestiary** têm esqueleto próprio, de 55 ossos.
  - Os clipes da UAL são retargetados com IK Rig (`Unreal/ue_creeps_anims.py`).
  - O Imp tem 1,68 m e o Puglin 0,93 m, e cada um tem 3 variações de cor.
- **Do Blender para a Unreal:** FBX com esqueleto deve ser exportado em centímetros (unit scale 0.01,
  ×100, `FBX_SCALE_NONE`) e importado em 1:1. Senão o osso raiz fica com escala 100 e as animações
  colapsam.
- **Kits de cenário:**
  - O montador `Unreal/ue_build_pois.py` aceita os dois formatos de pasta: o padrão do Interchange
    (`Env/<Kit>/<Nome>/StaticMeshes/<Nome>`) e o do pipeline customizado (`Env/<Kit>/<Nome>`).
  - As orientações medidas dos kits estão no docstring do script.

## 7. Mapa de pastas

| Caminho | Conteúdo |
|---|---|
| `AGENTS.md` | Este arquivo: o contexto para IAs |
| `CLAUDE.md` | Lido automaticamente pelo Claude Code. Só aponta para este arquivo |
| `README.md` | Visão geral para humanos |
| `Design/GDD.md` | Design oficial (v2). `GDD_v1.md` é o antigo, abandonado |
| `Design/Mapa.md` | Mapa v2 (ilha de cerca de 1 km): POIs, os três mapas da interface, direção de arte cartoon/aquarela e plano de montagem |
| `Registro/atividade.md` | Uma linha por mudança no projeto. Automático no Claude Code, à mão nas outras IAs |
| `Unreal/Data/Mapa/` | `mapa_v2.json` (layout da ilha, a fonte da verdade) e `gerado/` (saída do `Unreal/mapa_gerar.py`) |
| `Unreal/NexusRoyale/` | Projeto da Unreal. O conteúdo próprio fica em `Content/NexusRoyale/`, e o da Quaternius em `Content/Quaternius/` |
| `Unreal/*.py` | Scripts que rodam no editor ou falam com ele (seção 5). `ue_q_*` é o pipeline da Quaternius, `ue_creeps_*` os creeps, `ue_build_*` o nível e os POIs |
| `Unreal/ue_br_*.py` | Loop da partida: `step1_assets` (BPs e componentes), `build.py` (variáveis, funções e DSL), `wire_input`, `step4_defaults` (valores padrão e nível) e `items_import` |
| `Unreal/pie_state.py`, `Unreal/pie_press.py` | Estado do PIE (herói, dirigível e tempestade) e injeção de input |
| `Unreal/ue_creeps_bp.py`, `Unreal/ue_creeps_anims.py`, `Unreal/ue_creeps_camp.py` | Creeps: BPs e cápsulas, animações retargetadas, e o acampamento (tipos, números e posição no nível) |
| `Unreal/pie_creeps.py`, `Unreal/pie_capture.py` | Teste dos acampamentos no PIE e screenshot do jogo |
| `Unreal/Data/Camps_L_Island.json` | Acampamentos do `L_Island`, no formato de `mapa_ue.json` → `acampamentos` |
| `Unreal/Blueprints/*.dsl` | Grafos de Blueprint em DSL, para o `write_graph_dsl` |
| `Unreal/Data/` | Tabelas de balanceamento em CSV para importar como CurveTable ou DataTable (`CT_Storm.csv`, `DT_Itens.csv` + `gerar_dt_itens.py`) |
| `Unreal/NexusRoyale/Source/NexusRoyale/` | Módulo C++ compilado e listado no `.uproject`: `GAS/` (AS_Hero, ASC, efeitos), `Items/` (inventário, tabela, biblioteca), `Combat/` (UNRCombateComponent, ANRProjetilMagico, ANREstruturaMagica, ANRChuvaMeteoros e as structs das magias em NRMagiaTypes.h) e `UI/` (NRHudWidget) |
| `Unreal/ue_mvp_setup.py`, `Unreal/pie_combate.py`, `Unreal/pie_gravar.py` | Setup do combate (material, teclas e componente), teste do MVP no PIE e o gravador quadro a quadro do PIE |
| `Unreal/ue_gas_compilar.py`, `Unreal/ue_gas_setup.py` | Compilar o módulo (com o editor fechado) e depois configurar o DT_Itens e os componentes do herói (com o editor aberto) |
| `Launcher/` | Instalador/launcher (`NexusRoyaleLauncher.cs`), o `LEIA-ME.txt` e `bin/` (o `.exe` compilado, fora do git) |
| `Unreal/ue_release.py`, `Publicar-versao.bat` | Empacotar e publicar uma versão (seção 5, "Release"). Os builds ficam em `D:\NexusRoyale_Builds\<versão>` |
| `Blender/` | `NexusRoyale_Assets.blend` e os scripts de geração procedural (da v1) |
| `Export/` | FBX da v1, `map_layout.json` e as capturas de conferência em `Previews/` |
| `Quaternius/` | Packs baixados (`_zips/`) e extraídos, mais os scripts de download e de medição |
| `Personagens/` | Modelos do usuário (Boto, Caramelo, Pomba Gira). **Fora do jogo, mas não apagar** |

## 8. Decisões do usuário

| Data | Decisão |
|---|---|
| 14/10 | Criar um jogo inspirado no Fortnite, com heróis de MOBA, usando os MCPs da Unreal e do Blender |
| 15/10 (madrugada) | Os personagens próprios (Tripo) foram testados e depois trocados pela Quaternius. Os arquivos ficam no disco |
| 15/10 | Cenários: Stylized Nature, Medieval Village e Downtown City. Creeps: Bestiary |
| 15/10, por volta de 02:20 | **Mudança de design para o GDD v2:** arquétipo com 20 pontos; mana; magias híbridas (Q e ultimate escolhidas antes, E e R vindas de grimórios); sem construção, mas com magias de campo; foco no solo; nada da v1 continua. O usuário disse: "eu ajusto depois" |
| 15/10, por volta de 02:36 | "Continue construindo o game": seguir a etapa 1 do roadmap |
| 15/10, por volta de 03:00 | "Sempre que algo acontecer deve ser registrado para outras IAs": registro na hora (regra 7 e seção 2.1) |
| 15/10, por volta de 03:25 | **Layout da ilha v2 aprovado:** cerca de 1 km, 9 POIs (ver Design/Mapa.md). Os três mapas são necessários no lançamento: minimapa no HUD, tela cheia (M) e mapa da queda |
| 15/10, por volta de 03:25 | **Direção de arte: cartoon + aquarela.** Só o cenário recebe o filtro de aquarela; personagens e magias ficam com contorno nítido (GDD §10) |
| 15/10, por volta de 11:00 | **Balanceamento: pacote B da planilha de TTK aplicado ao GDD** (ver seção 3, "Planilha de TTK"). Os bônus de dano passam a somar entre categorias |
| 15/10, por volta de 03:00 | **Mapa no estilo do Fortnite, com 25% do tamanho** (porque são menos jogadores), mais um **minimapa** para o lançamento. Substitui a ilha de 400 m. O Fortnite tem cerca de 5,5 km². **Atenção, sessão de gameplay:** os raios de `Unreal/Data/CT_Storm.csv` vão mudar com o mapa |

## 9. Diário de sessões

Acrescente as entradas **no fim**, no formato `### AAAA-MM-DD HH:MM (Brasília) · IA/ferramenta · tema`.

### 2026-10-14 21:19 → 2026-10-15 02:26 · Claude (Claude Code) · Construção inicial
- **Blender:** gerou os assets procedurais da v1 (heróis, props e ilha), o `map_layout.json` e 25 FBX.
- **Unreal:** o usuário instalou a 5.8.3, e o projeto foi criado por `Unreal/create_project.ps1`.
- **Personagens do usuário:** os personagens Tripo foram rigados com pesos próprios e depois
  substituídos pela Quaternius.
- **Quaternius:** 9 packs baixados e importados; heróis montados; deformação corrigida com a remoção
  do Control Rig.
- **Mapa e creeps:** ilha nova de 40.000 cm, natureza, Vila e Cidade (237 peças), e os creeps Imp e
  Puglin.
- **Onde parou:** a sessão bateu no limite de uso enquanto gravava a IA dos creeps pela DSL.

### 2026-10-15 02:03 → 02:28 · Claude (Claude Code) · Conceito novo e GDD v2
- Revisou o conceito do usuário com ele e reescreveu `Design/GDD.md` como v2.
- A versão antiga foi arquivada em `GDD_v1.md`.

### 2026-10-15 02:30 → 03:25 · Claude (Claude Code) · Revisão do GDD v2 e gameplay
- **Revisão do GDD:** corrigiu os nomes de assets (poções e grimórios) e as inconsistências (build
  Místico, horário dos drops, magias de campo e recuperação de vida).
- **Planilha de TTK:** propôs fazê-la numa sessão separada.
- **Gameplay:** depois do pedido "continue construindo o game", começou o GAS e os Blueprints.
  - **Visual Studio:** não está instalado. O usuário escolheu instalar (opção recomendada) e recebeu o
    comando do winget (seção 3, Pendências).
  - Enquanto isso, montou a parte que não depende do GAS: dirigível, salto e planagem, tempestade,
    baús e pickups (seção 3, Pronto).
  - **Testado em PIE:** embarque; salto com Espaço de verdade, injetado pelo Enhanced Input; mergulho
    a -26 m/s e planagem a -4,5 m/s; pouso; as fases da tempestade em 100, 200, 300, 600, 760 e
    900 s, que batem com o GDD; abrir um baú, sortear e pegar o item; distribuição de raridade 60/30/10.
  - **Sem verificar:**
    - a tecla F de verdade (só a função `HandleInteract` foi chamada);
    - o bloqueio do salto fora da ilha, que não foi exercitado depois da correção;
    - o grimório saindo do baú (é 40%, e não saiu no teste);
    - a parede da tempestade de perto.
  - **Correções no caminho:**
    - `return` dentro de loop na DSL era descartado, e a tempestade fechava na hora;
    - a variável `StormTable` saía como int;
    - o casco do dirigível estava de lado (o Y da malha é invertido em relação ao Blender).
  - O editor foi reaberto com `-culture=en` e a interface voltou para pt-BR no fim. O Blueprint de
    teste `_Scratch/BP_DslTest` foi apagado.

### 2026-10-15 02:34 → 11:05 · Claude (Claude Code) · Planilha de TTK e ajuste do GDD
- Criou `Design/Simulacao_TTK.xlsx`, com cerca de 191 mil fórmulas e os valores já calculados.
- **Diagnóstico com os números originais:** só 27 de 48 confrontos ficavam entre 2 e 12 s.
  - Feiticeiro de Fogo → Guerreiro no nível 5 levava 12,3 s (a estimativa era de 15 s).
  - O Místico não matava tanques.
  - No nível 10, o Feiticeiro matava em 1,0 s.
- O usuário aprovou o pacote B, aplicado ao GDD em §4.1, §4.2, §4.4, §5, §6.3, §6.4, §7.1, §9, §13
  e §17. Com ele, 45 de 48 ficam no limite.
- **Conferência:** um modelo independente em Python bate nos 48 TTKs, antes e depois. Numa cópia
  com 9.190 fórmulas, o avaliador externo `formulas` também bateu.
- **Sem verificar:**
  - a planilha nunca foi aberta num app de planilha, porque a máquina não tem Excel nem LibreOffice;
  - o TTK é teórico, com 100% de acerto;
  - o kit de cada nível é suposição (aba Builds).

### 2026-10-15 02:50 → 02:55 · Claude (Claude Code) · Registro de contexto
- Criou este `AGENTS.md` e o `CLAUDE.md`, que aponta para ele.
- Atualizou a parte desatualizada do `README.md`.

### 2026-10-15 02:58 → 03:30 · Claude (Claude Code) · Registro automático e mapa novo (até o nível L_Ilha)
- **Registro automático:** criou o hook `.claude/hooks/registro.py`, ligado em
  `.claude/settings.json`, e o arquivo `Registro/atividade.md` (seção 2.1).
  - Testes simulados passaram: edição, PowerShell, MCP, Stop bloqueando uma vez e liberando depois
    do AGENTS.md.
  - As sessões que já estavam abertas também passaram a usar o hook.
- **Mapa novo:** o usuário pediu um mapa no estilo do Fortnite, com 25% do tamanho, mais um
  minimapa. Depois o usuário fixou: **"1 km com montanhas, água, cidade, vila, selva"** e os três
  mapas (minimapa, tela cheia e queda).
  - **Gerado:** o layout (`Unreal/Data/Mapa/mapa_v2.json`) e o gerador `Unreal/mapa_gerar.py`.
    - Resultado: 1.006 × 1.051 m, 0,80 km² de terra, pico de 91 m.
    - Tem 9 POIs, o Rio Prata, 2 lagos, 2 pontes e os 21 acampamentos do GDD, sem nenhum caído na
      água ou em encosta.
  - **Prévias:** `gerado/Previa_Mapa.png` (cartoon) e `gerado/Previa_Mapa_Aquarela.png`.
  - **Documento:** `Design/Mapa.md`, com o plano de montagem e a tempestade proposta.
  - **Direção de arte:** o usuário perguntou se o jogo pode ser todo cartoon/aquarela e se ficaria
    mais leve. A resposta está em Design/Mapa.md: sim, e fica mais leve no total.
  - **Sem verificar:**
    - o Landscape não foi importado na Unreal;
    - a orientação dos arquivos (linha = Y/leste) foi deduzida, não testada no editor.
- **03:25 a 03:30.** O usuário aprovou o layout e escolheu a direção de arte cartoon + aquarela.
  Isso foi registrado no GDD (§10 e §11), na seção 8 e na memória.
  - **Na Unreal:**
    - o material `M_Terreno_V2` (8 camadas, sem erro de ligação) e 3 texturas em
      `/Game/NexusRoyale/Map/V2/`;
    - o nível `L_Ilha` com luz e céu. Antes da troca, os pacotes sujos foram salvos e o PIE foi
      checado.
  - **LayerInfo pelo Python não funciona:** o `LayerName` é somente leitura. Os assets criados
    foram apagados.
  - **Hook:** o `ue_py.py` deixou de contar como mudança quando o script executado é só de
    leitura.

### 2026-10-15 10:55 → 11:12 · Claude (Claude Code) · GAS em C++ (escrito, sem compilar)
- O usuário pediu para seguir com o GAS dizendo que o Visual Studio tinha terminado de instalar.
  **Ele não estava instalado** (seção 3, Pendências). O usuário recebeu o comando de novo.
- **Para não perder tempo,** escreveu todo o módulo C++ (seção 3, Próximos passos, item 1): o
  `DT_Itens.csv` e os scripts `ue_gas_compilar.py` e `ue_gas_setup.py`.
  - Usou os números novos do GDD: Vitalidade +30, +80 de vida por nível e armadura 0,04, que vieram
    da planilha de TTK.
- **Sem verificar:**
  - **nada foi compilado.** As APIs foram conferidas nos headers da 5.8, mas erros de compilação são
    esperados na primeira vez;
  - o `ue_gas_setup.py` não rodou.
- **Não mexeu na Unreal:** o editor estava aberto com a sessão dos creeps trabalhando. O `.uproject`
  não foi alterado.
- O único teste foi o `ue_gas_compilar.py` sem o Visual Studio. Ele parou no primeiro passo, como
  devia, sem tocar no `.uproject`.
- **11:35 a 11:50:** a pedido do usuário, iniciou a instalação do Visual Studio no D: (seção 3,
  Pendências).
  - **Combinado com as outras sessões:** a dos creeps liberou o editor às 11:40. A do mapa salva o
    `WBP_Mapa` e o `HUD_NexusRoyale` e depois avisa "pode fechar". Só então o editor fecha para
    compilar.
  - **O WBP_HUD vai entrar no `HUD_NexusRoyale`** por uma função `CriarHUD`, escrita na DSL da
    sessão do mapa (`ue_mapa_ui_build.py`). Isso só pode ser feito depois de compilar, porque antes
    o `WBP_HUD` não existe.
  - **Dano dos creeps:** depois de compilar, o `EventAnyDamage` do `BP_HeroBase` passa a chamar
    `Habilidades.AplicarDano`.

### 2026-10-15 11:00 → em andamento · Claude (Claude Code) · Interface dos mapas (minimapa, M e queda)
- **Contexto:** o usuário não conseguia importar o Landscape agora e pediu para seguir com os
  widgets. Os assets estão na seção 3, em "Interface dos mapas".
- **Feito:**
  - `T_Mapa_UI` (o `mapa_gerar.py` agora também gera essa textura e a célula da grade de cada POI);
  - `MPC_Mapa`, `M_UI_Mapa` e as instâncias `MI_UI_*`;
  - `WBP_Mapa` (criado pelo UMGToolSet), `HUD_NexusRoyale`, o `IA_Mapa` na tecla M e o HUD no
    `GM_NexusRoyale`.
  - Os grafos foram escritos em DSL (`Unreal/Blueprints/WBP_Mapa__*.dsl` e `HUD_NexusRoyale__*.dsl`)
    e compilam.
- **Pegadinhas descobertas** (valem para quem mexer em DSL e material):
  - **IDs repetidos no catálogo:** a DSL pega a primeira variante.
    - `Appearance|GetDynamicMaterial` cai na versão da Border.
    - `Rendering|Material|SetVectorParameterValue` cai na versão da Material Parameter Collection.
    - `Rendering|Material|CreateDynamicMaterialInstance` cai na versão de componente.
    - Por isso os mapas usam MPC, instâncias de material e `Class|Image|SetBrush` +
      `Utilities|Struct|MakeSlateBrush`.
  - **`(Utilities|IsValid x (:"Is Valid" …) (:"Is Not Valid" …))` encerra o fluxo:** o que vem
    depois dá "Unreachable code". Separe em funções.
  - **Num nó Custom (HLSL), VectorParameter e CollectionParameter entregam RGB.** Para ter os 4
    componentes, ligue pela saída "RGBA".
  - **O `SetVisibility` de um widget por referência** é `Class|Widget|SetVisibility`, e o pino se
    chama `:Visibility`.
  - **Os eventos de widget levam prefixo:** `(event UserInterface|EventConstruct)` e
    `(event UserInterface|EventTick (MyGeometry InDeltaTime))`.
- **Observação para a sessão de gameplay:** às 11:05, o `IMC_Default` tinha só `IA_Jump`, `IA_Look`,
  `IA_Move` e o `IA_Mapa` (adicionado agora). **O `IA_Interact` (F) não está mapeado nele.** Não
  mexi.
- **Sem verificar:** a textura e o material da UI foram refeitos durante um PIE da sessão dos creeps
  (o editor recusa asset no PIE). Isso será refeito e testado em PIE quando o editor estiver livre.

### 2026-10-15 10:55 → 11:35 · Claude (Claude Code) · IA dos creeps e acampamento de Imps
- **Pedido** (sessão lateral da etapa 1): fazer os creeps funcionarem e montar o acampamento pequeno.
- **Editor:** estava fechado (o log parou às 09:53 sem encerramento). Foi aberto às 10:57 com
  `-culture=en` no `L_Island`. As sessões do mapa (UI) e do GAS passaram a usar o mesmo editor.
- **Como estava:** o `Think` antigo estava gravado (com `SimpleMoveTo`, que precisa de NavMesh, e só
  com o jogador 0). O EventGraph estava vazio, os valores padrão eram todos 0, e o `IsDead` e o
  dispatcher `OnCreepKilled(Killer: Actor, XP: int)` já existiam.
- **Feito:** está na seção 3, "Creeps e acampamento". O builder (`ue_br_build.py`) ganhou
  `BP_Creep`, `BP_CreepCamp` e o `DamageTaken` do herói. As DSLs antigas viraram
  `BP_Creep__EventGraph.dsl` e `BP_Creep__Think.dsl`, reescritas.
- **Bug corrigido:** a malha dos creeps estava com **pitch** -90 (deitada), porque
  `ue_creeps_bp.py` usava `Rotator(0, -90, 0)`, que é (roll, pitch, yaw). Agora é yaw -90 nos dois
  filhos e no script.
- **Testado em PIE** (herói tirado do dirigível por `pie_creeps.py land`):
  - a 9,5 m, nada acontece. A 4 m, os 3 Imps pegam o herói, dois andam 5 m até ele e todos batem.
    O `DamageTaken` sobe cerca de 24/s (3 × 12 / 1,5 s);
  - o herói a 22 m da origem: os Imps soltam o alvo, voltam à vida cheia e andam até 0,3 m de casa;
  - 1 de dano num Imp, com o herói a 12 m (fora do aggro): os 3 atacam e perseguem 12 m;
  - morte: pose de morte, movimento NONE, sem colisão, 3 s de vida e "pending" no acampamento;
  - reaparecimento com 6 s e 20 s (valor trocado só no PIE) e com os **90 s de verdade** (morte em
    t=222,6, ainda pendente em 297,3, de volta em 316,4);
  - screenshots conferidos: Imps em pé, atacando em volta do herói, e caindo para trás ao morrer;
  - nenhum erro de Blueprint dos creeps no log. Os BPs compilam com warnings como erro.
- **Sem verificar:** os argumentos do `OnCreepKilled`; o Puglin e o acampamento médio; a animação
  de golpe vista de perto; a rede (veja a seção 3).
- **Interferência com outras sessões:**
  - os PIEs (11:15–11:24 e 11:25–11:31) recusaram assets da sessão da UI dos mapas;
  - às 11:14, um `save_dirty_packages(False, True)` meu salvou **todos** os pacotes sujos. Se algum
    asset da UI estava pela metade, ele foi salvo assim;
  - depois disso, só salvei os meus. No fim, `HUD_NexusRoyale` e `WBP_Mapa` (da UI) ficaram sujos
    e não foram tocados;
  - o `WBP_Mapa.AtualizarJogador` gerou cerca de 355 erros "Accessed None … LastHitBy" no PIE (é da
    sessão da UI).
- O editor continua aberto, em inglês e no `L_Island`. A interface não foi devolvida ao pt-BR,
  porque outras sessões estavam usando o editor.
- **Nota de passagem** para as sessões irmãs: `creeps_acampamento.md`, na pasta de notas
  compartilhada (`side-session-notes\local_7e223023-…`). Foi proposta uma sessão para os drops e as
  malhas de equipamento dos creeps.
- **11:40:** a sessão de gameplay pediu para fechar o editor e compilar o módulo do GAS. Respondi
  "ok, pode fechar": nada dos creeps estava sujo e não havia PIE. Avisei que `HUD_NexusRoyale` e
  `WBP_Mapa`, da sessão da UI, continuavam sem salvar.

### 2026-10-15 12:20 → em andamento · Claude (Claude Code) · Visual cartoon/aquarela mais leve (render)
- **Pedido** (sessão lateral): trocar Lumen, VSM e distance fields por config leve, desligar o Nanite
  das malhas low-poly, criar o pós-processamento cartoon + aquarela com stencil nos personagens e
  medir antes e depois no PIE.
- **Até agora só scripts, nada rodou na Unreal:** `Unreal/ue_render_aquarela.py` (materiais
  `M_PP_Cel` e `M_PP_CartoonAquarela` em `/Game/NexusRoyale/Render/`, stencil, volume, SkyLight e
  Nanite) e `Unreal/pie_medir.py` (FPSChart, ProfileGPU e memória no log).
- **Combinado com a sessão "MVP rollout":** medir o "antes" com a config atual quando ela liberar o
  PIE; o `DefaultEngine.ini` só muda numa próxima janela com o editor fechado. Ela vai pôr stencil 4
  na `Malha` do `ANRProjetilMagico` (C++).
- **12:40, leitura:** 159 das 181 StaticMesh de `/Game` têm Nanite (148 da Quaternius e 11 da
  LevelPrototyping). Os cvars atuais confirmam Lumen (GI e reflexos), VSM, distance fields e
  `r.CustomDepth=1`, sem stencil. Ainda nada mudou na Unreal.
- **12:47, medição do "antes" no PIE** (L_Island, viewport de 1142×730):
  - 22 FPS, com 34,8 ms de GPU;
  - o Lumen gasta cerca de 35 ms no compute assíncrono, as sombras virtuais 7,6 ms e o Nanite 4,3 ms;
  - **o pool de render targets tem 3,1 GB:** Lumen 1,42 GB, sombras virtuais 1,27 GB e distance
    fields 0,19 GB;
  - o editor usa 3,5 GB de memória de vídeo e transborda 680 MB para a RAM. As texturas somam só
    89 MB.
  - O detalhe está em `render_medicoes.md`, na pasta de notas da sessão.
- **12:52, `DefaultEngine.ini` trocado com o editor fechado** (janela de compilação da sessão
  "MVP rollout"): `r.DynamicGlobalIlluminationMethod=0`, `r.ReflectionMethod=0`,
  `r.Shadow.Virtual.Enable=0`, `r.GenerateMeshDistanceFields=False` e `r.CustomDepth=3`. O original
  ficou em `Config/DefaultEngine.ini.antes_aquarela`.
- **Combinado:** o `BP_Pickup` e o `BP_LootChest` estão com a sessão "MVP rollout". O stencil do
  pickup só entra depois do aviso dela. O `ue_render_aquarela.py` ganhou `SO=[...]` para limitar os BPs.
- **13:18 a 13:24, na Unreal** (editor reaberto pela "MVP rollout" com a config nova):
  - os materiais `M_PP_Cel` / `MI_PP_Cel` e `M_PP_CartoonAquarela` / `MI_PP_CartoonAquarela`
    compilam, com 91 e 111 instruções;
  - stencil 1 no `BP_HeroBase` (corpo, roupa e cabelo), 2 no `BP_Creep`, `_Imp` e `_Puglin` e 3 no
    `BP_Pickup`;
  - no `L_Island`: o `PostProcessVolume` "PP_CartoonAquarela" infinito e o SkyLight com captura
    estática. Só o mapa foi salvo, e ele estava limpo antes.
  - Visto no viewport do editor, o cenário fica pintado, com contorno.
  - **Ainda sem verificar:** os personagens fora da aquarela no PIE; o `L_Ilha`; o Nanite; a medição
    do "depois".
- **13:33, em andamento:** desligando o Nanite das 159 malhas, em lotes de 40 com save e coleta de
  lixo. A sessão "Git e versão jogável" espera o meu "pode fechar" para fechar o editor e fazer o
  cook.

### 2026-10-15 11:48 → 13:40 · Claude (Claude Code) · MVP rollout: GAS compilado e MVP jogável
- **Pedido do usuário:** "rode o MVP assim que possível".
- **11:48:** o Visual Studio tinha terminado de instalar às 11:33. As sessões do GAS e do mapa
  tinham batido no limite de uso às 11:39 (voltam às 15:50). Nada estava sujo e não havia PIE.
  Então fechei o editor e compilei o módulo, que **passou na primeira vez** (7 min).
- **Feito** (detalhes em "MVP jogável", seção 3):
  - `ue_gas_setup.py` rodou;
  - combate em C++ (`Combat/`), HUD montado em C++, XP e nível, morte e recomeço;
  - `ue_mvp_setup.py` com as teclas (o **F não estava mapeado** no `IMC_Default`; agora está);
  - DSLs: `StormTick` → `AplicarDanoTempestade`, `Die` do creep → `DarXP`, loot por ItemId e
    `InteractNearby`.
- **Bugs de outras sessões corrigidos no caminho:**
  - **creep morria com qualquer golpe de metade da vida restante ou mais, sem alertar o acampamento**
    (nó puro recalculado; `BP_Creep__EventGraph.dsl`);
  - os ~355 erros "Accessed None … LastHitBy" do `WBP_Mapa.AtualizarJogador`, que também
    derrubavam a captura pelo MCP (`WBP_Mapa__AtualizarJogador.dsl`);
  - o injetor de teclas do `pie_press.py` às vezes mirava o objeto padrão da classe.
- **Testado em PIE** (com `pie_combate.py` e `pie_creeps.py`):
  - o herói nasce com vida 520, mana 430 e Poder Mágico +27%;
  - os Imps tiram vida pelo GAS, e com 3 Imps o herói morre em ~20 s. Na morte: pose, sem
    movimento, "VOCÊ FOI ELIMINADO" e o nível recomeça em 6 s;
  - dardo pela tecla (com a recarga conferida) e direto: 76 de dano. Mirando 6° ao lado, curva e
    acerta. O acampamento inteiro reage;
  - Bola de Fogo pela tecla e direto: −55 de mana, recarga de 6 s, matou 2 Imps juntos (+60 XP);
  - XP: +30 por Imp, e a barra no HUD mostra 90/100;
  - baú aberto pelo F, com os itens da tabela. Pelo F: grimório, Amuleto do Erudito (equipado) e
    Refeição (slot 1). A Couraça de Couro deu +60 de vida máxima. A tecla 1 usou a Poção de Pressa;
  - o HUD na captura da janela: barras, nível/XP, linha das magias, consumíveis, equipados e a mira.
- **Sem verificar:** está na seção 3, "MVP (sessão "MVP rollout"), sem verificar".
- **Convivência com outras sessões:**
  - a do **visual** trocou o `DefaultEngine.ini` (sem Lumen nem VSM, `r.CustomDepth=3`) na janela em
    que o editor estava fechado para compilar, e pôs stencil nos BPs (1 herói, 2 creep, 3 pickup);
  - pus o stencil 4 no projétil, a pedido dela;
  - a sessão **Git e versão jogável** recebeu o "pode empacotar" às 13:34, para fazer o cook com o
    editor fechado depois da medição da sessão do visual.
- O editor continua aberto, em inglês e no `L_Island`. Ninguém devolveu a interface ao pt-BR.
- **Próximo passo proposto ao usuário** (cartão de sessão, ainda não iniciado): Muralha de Gelo e
  Chuva de Meteoros do Feiticeiro (item 2 dos próximos passos).

### 2026-10-15 13:52 → 15:35 · Claude (Claude Code) · Kit do Feiticeiro: Muralha de Gelo e Chuva de Meteoros
- **Pedido** (cartão da sessão "MVP rollout"): completar o kit do Feiticeiro da etapa 1, com a
  Muralha de Gelo no E e a Chuva de Meteoros no X, os números do GDD §6 e as recargas no HUD.
- **Decisão:** estender o `UNRCombateComponent` em vez de migrar para `GA_*`. O motivo está na seção
  3, "MVP jogável".
- **Feito:**
  - `Combat/NRMagiaTypes.h`, `NREstruturaMagica` e `NRChuvaMeteoros`, com E e X no componente;
  - o projétil agora também fere estruturas;
  - a linha de magias do HUD;
  - o `ue_mvp_setup.py` (IA_Magia2 no E, IA_Ultimate no X, M_Estrutura e `NivelUltimate` = 1 no MVP);
  - o `pie_combate.py` com as ações novas.
- **Compilação** com o editor fechado às 14:09, combinada com as sessões abertas. A primeira
  falhou: o parâmetro `Slot` da lambda do HUD escondia o `UWidget::Slot`. Depois de corrigir,
  compilou em 45 s.
- **A sessão caiu às 15:11 e foi retomada às 15:17** numa conversa nova, com a transcrição colada
  pelo usuário. Entre 15:06 e 15:09, o usuário jogou no PIE e usou as duas magias pelo teclado
  (o log mostra muralhas a 2,5–4 m e uma chuva que matou 2 Imps).
- **Testado em PIE no `L_Island`**, de 15:20 a 15:30, com o acampamento de Imps a 12 m:
  - **E pelo teclado:** muralha a 5,7 m, entre o herói e os Imps, com 400 de vida. Recarga de
    10,3 s (12 s com a Redução de Recarga). Some em 6 s. Um segundo E na recarga não faz nada;
  - **custo exato** (chamada direta, mana antes e depois): 50 da muralha e 120 da chuva. A recarga
    da chuva fica em 68,8 s (80 s com a redução). O segundo uso é recusado sem gastar mana;
  - **muralha segurando o dardo:** o dardo mirado num Imp atrás dela não chegou (os 3 Imps ficaram
    com 150 e sem alvo), e a muralha continuou com 400, porque o tiro do dono não estraga;
  - **muralha quebrando com dano de inimigo:** 400 → 250 → 0, e ela se desfaz;
  - **X pelo teclado:** a chuva caiu a 12,8 m, no centro do acampamento. Os meteoros acertaram 2, 1 e 0
    alvos (cada Imp levou um só) e mataram os 3 Imps (120 × 1,27 = 152 ≥ 150), com +90 de XP;
  - **HUD na captura:** "[E] Muralha de Gelo (50 de mana): 8,3 s" e "[X] Chuva de Meteoros (120 de
    mana): 47,4 s". A muralha aparece ciano, com contorno.
- **Sem verificar:** está na seção 3, "Muralha de Gelo e Chuva de Meteoros … sem verificar".
- **No caminho:**
  - o `pie_combate.py` passou a apagar as próprias opções;
  - entraram três pegadinhas novas na seção 5 (globais do Python remoto, `set_editor_property` no
    PIE e girar e apertar na mesma chamada).
- **Ao sair:** PIE parado. Salvei só o `BP_HeroBase`, que ficou sujo por causa da reconstrução no PIE
  e manteve os mesmos valores. Não sobrou nada sem salvar. O editor continua aberto, em inglês e no
  `L_Island`. Avisei a sessão "Design system MCP motor", a única aberta, de que o editor está livre.
- **Commit `74f7ed1` na `main`, sem push** (15:40, a pedido do usuário). Entraram só `Combat/`,
  `NRHudWidget.cpp`, `ue_mvp_setup.py`, `pie_combate.py` e o `AGENTS.md`, que foi inteiro, com as
  notas das outras sessões desde o primeiro commit.
  - **Ficaram fora** os assets desta sessão: `IA_Magia2`, `IA_Ultimate`, `M_Estrutura` e o
    `BP_HeroBase.uasset`. O `ue_mvp_setup.py` recria todos eles.
  - O commit foi na `main` e não numa branch porque o checkout é compartilhado com outras sessões.

### 2026-10-15 15:37 → 16:10 · Claude (Claude Code) · Teste da muralha contra creeps e do chão em chamas
- **Pedido** (sessão lateral da "Kit do Feiticeiro etapa 1"): testar em PIE o que tinha ficado sem
  verificar na Muralha de Gelo e na Chuva de Meteoros. Não mexi em C++, Blueprint nem números do GDD.
  Os números trocados (duração da muralha, vida e movimento dos Imps) valeram só dentro do PIE.
- **Ferramenta nova:** `Unreal/pie_gravar.py`, um gravador quadro a quadro (seção 5).
- **Creeps contra a muralha** (muralha a 3,8 m do herói, durando 30 s só no PIE, e Imps provocados a
  12 m): eles param a 0,7 m do plano da muralha e ficam empurrando por todo o tempo dela, com
  `bMoving` True. Os dois dos lados escorregaram de ±1,1 m para ±0,8 m, rumo ao meio. Nenhum
  contornou e nenhum bateu na muralha. No primeiro PIE, com os 6 s de verdade, foi igual. Quando a
  muralha sumiu, os três alcançaram o herói em ~0,7 s e bateram juntos (−36 a cada ~1,7 s). Há
  uma proposta de correção esperando o usuário (seção 3).
- **Bola de Fogo contra a muralha:** com os Imps encostados do outro lado, o Q pelo teclado explodiu
  a 0,50 m do plano da muralha, do lado do herói (0,20 m da face, como no código). Os Imps estavam a
  ~1,2 m da explosão, dentro dos 3 m de raio, e **nenhum perdeu vida**. A muralha **ficou com
  400/400**. Deu o mesmo duas vezes, antes e depois do recomeço da partida (o herói morreu no meio). Contraprova: no primeiro PIE, o mesmo Q sem a muralha
  tirou 165,4 de cada Imp em volta do herói e matou os três.
- **Chão em chamas** (Imps presos no lugar com `disable_movement()` e com a vida subida a 1000 por
  `ApplyDamage` negativo, para sobreviverem aos meteoros; jogo a 0,1× durante as capturas):
  - a chuva caiu a 0,26 m do centro do acampamento. No primeiro impacto (t = 1,0 s), um Imp levou
    meteoro + chamas (−165,4) e o outro só chamas (−12,7). O segundo meteoro acertou o outro Imp
    (−152,6), e o terceiro não acertou ninguém (cada alvo leva um meteoro só);
  - **as chamas tiram 12,7 a cada 0,5 s** (= 20/s × 0,5 s × 1,27), **8 pulsos** do primeiro impacto
    até 5,0 s (101,8 no total por Imp). A chuva some em 5,1 s. O Imp fora da área não levou nada.
  - Antes disso, uma chuva mirada errado caiu a 6 m do herói, longe dos Imps: 0 alvos e nenhuma
    chama, como devia (seção 5, pegadinha da mira).
- **Visual** (capturas com `ue_capture.py --editor`, copiadas para `Export/Previews/teste_chuva_*.png`):
  - o disco de aviso aparece laranja, sólido;
  - o meteoro cai como esfera com contorno preto (stencil 4);
  - a explosão é um domo de 7 m;
  - o chão em chamas é o disco mais claro;
  - meteoros e clarões saem creme, não laranja (seção 3).
- **O editor caiu às 15:44,** ao recomeçar o PIE: "Out of video memory" (D3D12). Não havia pacote
  sujo antes do PIE. O processo fechou sozinho, e o editor foi reaberto às 15:47 com `-culture=en`.
  A sessão "Design system MCP motor" foi avisada. Depois disso, todos os testes foram num PIE só (seção 5).
- **Sem verificar:** está na seção 3, "Muralha de Gelo e Chuva de Meteoros".
- **Ao sair:** PIE parado às 16:03, sem pacotes sujos. Nada foi salvo. O editor continua aberto, em
  inglês e no `L_Island`. As gravações e uma nota de passagem ficaram na pasta de notas
  compartilhada (`side-session-notes\local_5af47a64-…\teste_muralha_chuva.md`). Sem commit.

### 2026-10-15 16:15 → 16:45 · Claude (Claude Code) · Creeps batem na muralha que os bloqueia
- **Pedido do usuário:** "quando a muralha bloquear, os creeps devem bater nela (mesmo dano e recarga
  do ataque). Implemente no Think do BP_Creep e teste no PIE." A alternativa era contornar.
- **Feito no `BP_Creep`** (DSLs em `Unreal/Blueprints/`; variável e funções novas no `ue_br_build.py`):
  - a variável `BlockingStructure` (Actor);
  - a função `FindBlocker(TargetLocation)`: uma `NREstruturaMagica` que não esteja se desfazendo, com
    o creep encostado numa face (raio da cápsula + 40 cm), dentro da largura e do lado oposto ao alvo,
    tudo no espaço local da estrutura;
  - a função `AttackActor(Victim, LookAt)`: o golpe que antes ficava no `Think`;
  - o `Think`, que testa o bloqueio antes do alcance do alvo.
  - Cada grafo foi gravado sozinho, com o `ue_write_dsl.py`, e lido de volta. O `ue_br_build.py graphs`
    regrava todos os grafos do BP. Os filhos `_Imp` e `_Puglin` compilaram, e salvei só o `BP_Creep`.
- **Testado em PIE no `L_Island`** (muralha de 30 s só no PIE, com `PropertyAccessChangeNotifyMode.NEVER`;
  gravação em `gravacao_creeps_batem.txt`, na pasta de notas):
  - a muralha perdeu 12 por golpe (36 a cada ~1,7 s com 3 Imps) e quebrou ~18 s depois do primeiro golpe;
  - com o herói colado na muralha, a 0,8–1,6 m dos Imps, ele não levou dano enquanto ela estava de pé;
  - quando ela sumiu, os Imps foram para o herói na hora (−24/−12, o ataque normal);
  - o leash continuou funcionando (vida cheia ao afastar o herói);
  - nenhum erro de Blueprint no log.
- **Sem verificar:** a animação de golpe contra a muralha (sem captura), o Puglin e os 6 s de verdade.
- **O editor caiu de novo às 16:17** (falta de memória de vídeo, no terceiro mundo de PIE da
  abertura). O `BP_Creep` já estava salvo. Reabri às 16:22.
  - O primeiro PIE depois disso não serviu: o GameMode embarcou o herói no dirigível depois do pouso.
  - Fechei o editor limpo às 16:31 (sem pacotes sujos), reabri, e o teste rodou no primeiro PIE.
  - A pegadinha da seção 5 foi reescrita.
- **Ao sair:** PIE parado, sem pacotes sujos. O editor continua aberto, em inglês e no `L_Island`.
- **Commit `82b22bc` na `main`, sem push** (16:50, a pedido do usuário). Entraram:
  - o `BP_Creep.uasset`;
  - as DSLs `BP_Creep__Think`, `FindBlocker` e `AttackActor`;
  - o `pie_gravar.py`;
  - só o trecho do `BP_Creep` no `ue_br_build.py`. O trecho do `InteractNearby`, de outra sessão,
    ficou fora;
  - o `AGENTS.md`, com as duas entradas desta sessão. Esta linha ficou fora do commit.

### 2026-10-15 16:44 → 17:35 · Claude (Claude Code) · Instalador com atualização automática
- **Pedido do usuário:** "um MVP jogável que possa ser instalado e que, quando subirem atualizações
  no git, baixe sozinho antes de iniciar". O usuário escolheu deixar as versões no repositório
  **privado** `holaluiz/MOBA-BR` (cada PC precisa do login do `gh` ou de um token) e liberou fechar
  a Unreal.
- **Herdado da sessão "Git e versão jogável"** (não publicada): `Unreal/ue_release.py` e um launcher
  em PowerShell. A compilação de 13:24 tinha morrido com o erro 1455 do UBA (memória virtual cheia).
- **Feito** (detalhes na seção 3, "Instalador e atualização automática", e na seção 5, "Release"):
  - `Launcher/NexusRoyaleLauncher.cs`: instalador + launcher num `.exe` só. Ele substitui o
    `Jogar.bat`/`launcher.ps1`, que foram apagados;
  - `ue_release.py`: ações `launcher`, `empacotar --sem-cook` e `tudo --versao` (sobe a versão
    sozinho), o instalador no manifest e na Release, e `-NoUBA`. `Publicar-versao.bat` na raiz;
  - `DefaultGame.ini`: a regra `GameFeatureData` e o `[Staging] +AllowedDirectories` da pasta `Apple`
    (as pegadinhas estão na seção 5);
  - **Release `v0.1.0` publicada às 17:29** (1,07 GB em cerca de 1 min de upload). A tag ficou na
    `main` do GitHub (`e26d174`), porque os commits locais não foram enviados; o commit do build
    (`82b22bc` + as mudanças sem commit) está no `manifest.json`.
- **Testado:**
  - o instalador (pelo UI Automation): a tela, a pasta sugerida `D:\Jogos\NexusRoyale`, os atalhos
    do menu Iniciar e da área de trabalho, o registro em Aplicativos e o token do `gh` achado sozinho;
  - o launcher sem Release mostra "Ainda não há nenhuma versão publicada";
  - **com a Release:** o launcher baixou 1.073 MB a ~16 MB/s, conferiu, instalou e abriu o jogo em
    97 s. Ficaram `game\versao.txt` = 0.1.0 e o `DisplayVersion` 0.1.0. O jogo abriu de
    `D:\Jogos\NexusRoyale\game` com o HUD (captura).
- **Sem verificar:**
  - **a atualização de uma versão para outra** (com a pasta `game` antiga já instalada). O jogo ficou
    aberto (o usuário estava jogando). Para testar: com o jogo fechado, ponha `0.0.9` no
    `game\versao.txt` e abra o atalho;
  - a troca do próprio launcher (só acontece quando `Versao` no `.cs` passar de 1.0.0);
  - o pedido de token num PC sem `gh`, o `/desinstalar` e o Visual C++ num PC que não o tenha;
  - o minimapa, que não aparece no jogo empacotado (seção 3).
- **Ao sair:** a Unreal continua **fechada** desde 16:52, sem nada sujo, e está livre para abrir.
  Nada foi commitado.
