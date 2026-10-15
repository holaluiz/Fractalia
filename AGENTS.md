# AGENTS.md: contexto do projeto para IAs

> **Leia este arquivo antes de mexer no projeto.** Ele vale para qualquer IA (Claude, ChatGPT,
> Gemini, Copilot, Cursor…) e é a memória compartilhada do que já foi feito.
>
> **Ao terminar uma sessão de trabalho:** atualize a seção 3 (Estado atual) e acrescente uma
> entrada no fim da seção 9 (Diário). Seja curto e diga o que ficou **sem verificar**.

Última atualização: 2026-10-15, por volta de 11:35 (horário de Brasília), por Claude (Claude Code).

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
    "Dano: -X" (`TODO(GAS)`).
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
  - ninguém escuta o `OnCreepKilled` ainda (XP e nível são o item 4 dos próximos passos). A chamada
    roda, mas o Python não consegue se ligar a um dispatcher de BP para conferir os argumentos;
  - **não tem drop** (GDD §12: 50% de comida ou poção no pequeno, grimório no médio);
  - o dano no herói só soma em `DamageTaken`. Com o GAS, trocar por `AplicarDano`;
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
- **Lacunas do loop da partida** (marcadas com `TODO` nas DSLs):
  - a tempestade e os pickups só mostram uma mensagem (`PrintString`). Ainda não tiram vida nem
    entram no inventário, porque isso depende do GAS;
  - **não tem rede:** o salto e o F não são RPC. Funciona só no PIE solo;
  - não tem HUD: nem prompt do F, nem relógio da tempestade;
  - **os raios da tempestade, a rota do dirigível e o `DropRadius` (190 m) são da ilha de 400 m.**
    Ajustar no `CT_Storm.csv` e nos valores padrão quando o mapa v2 entrar;
  - **o `L_Island` ainda tem os restos da v1:** Nexus, torres, fragmentos, poções de escudo e
    plataformas de salto;
  - o PIE avisa que a memória de vídeo estourou em cerca de 500 MB na RX 570.

### Próximos passos

Etapa 1 ("Núcleo") do roadmap, no GDD seção 15. Já estão feitos o baú comum e a tempestade, que
ainda esperam o GAS para causar efeito. Falta:

1. **GAS. O código C++ está escrito, mas não foi compilado,** porque falta o Visual Studio. Está em
   `Unreal/NexusRoyale/Source/NexusRoyale/`:
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
   - **Atenção:** o `.uproject` ainda **não** lista o módulo, de propósito. Com o módulo listado e
     sem compilador, o editor não abre.
2. Arquétipo Feiticeiro e as magias Bola de Fogo, Muralha de Gelo e Chuva de Meteoros.
3. ~~Acampamento de Imps~~ (feito, sem GAS). Falta: drop dos creeps, levar os 21 acampamentos para o
   `L_Ilha` com `place_camps()` e o `mapa_ue.json`, e o elite (Puglin Ancião).
4. XP e nível: ligar o `OnCreepKilled` e o `OnPhaseEnded` (piso de nível).

A arquitetura alvo está no GDD, seção 16: `AS_Hero` em C++, `PS_Hero`, `BP_HeroBase`, `GA_*`/`GE_*`,
`DT_*`/`DA_*`, `BP_StormController` e outros.

### Pendências do usuário

- **Instalar o Visual Studio.** O usuário escolheu essa opção em 15/10. O `AttributeSet` do GAS só
  pode ser escrito em C++, e hoje a máquina tem só o Visual Studio Installer.
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
| Git | O projeto **não** é um repositório git. Não dá para desfazer alterações por histórico |

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
| `Unreal/NexusRoyale/Source/NexusRoyale/` | Módulo C++ (GAS, itens e base do HUD). Ainda não compilado nem listado no `.uproject` |
| `Unreal/ue_gas_compilar.py`, `Unreal/ue_gas_setup.py` | Compilar o módulo (com o editor fechado) e depois configurar o DT_Itens e os componentes do herói (com o editor aberto) |
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
