# Problemas conhecidos

Gravidade: **Alta** (quebra o jogo ou bloqueia um marco) · **Média** · **Baixa**. Quando resolver, mova para "Resolvidos"
com a data e o commit.

---

## Abertos

| # | Gravidade | Problema | Onde | Contorno / próximo passo |
|---|---|---|---|---|
| K-01 | **Alta** | No jogo empacotado (0.1.0 e 0.1.1) as teclas de combate não funcionam: o `IMC_Default` no disco só tinha pulo, câmera, movimento e mapa | `Unreal/ue_mvp_setup.py` | **Corrigido no projeto em 15/10, 21:05** (arquivo conferido). Falta o teste no jogo empacotado e publicar a 0.1.2 (OK do usuário) |
| K-02 | **Alta** | Não há multiplayer: combate, inventário, interação, salto e mutações rodam no input local | C++ e Blueprints (AUDITORIA.md §2) | M1 feito (estado da partida, morte, nível e XP em rede); faltam M2 e M5 |
| K-04 | Alta | O editor cai no 2º ou 3º PIE por falta de memória de vídeo (RX 570) | Máquina | Um PIE por abertura; clientes `-nullrhi` (TEST_PLAN.md §2). Em 15/10 à noite, recomeços dentro do mesmo PIE (2º mundo) não derrubaram o editor em três PIEs seguidos (um por abertura) |
| K-06 | Média | Atores das magias não replicam (`bReplicates` falso) | `ANRProjetilMagico`, `ANREstruturaMagica`, `ANRChuvaMeteoros` | M5 |
| K-07 | Média | O sorteio do baú roda onde o `Interact` é chamado (num cliente, seria o cliente) | `BP_LootChest` | M2: `Server_Interagir` |
| K-08 | Média | O HUD lê variáveis de Blueprint pelo nome (renomear apaga o texto sem erro) | `UNRHudWidget` | Interface C++ `INRZona`; ler do GameState |
| K-10 | Média | O `L_Ilha` (mapa v2) não tem Landscape | Editor | Usuário importa à mão (Design/Mapa.md, "Como montar") |
| K-11 | Média | Fundo do minimapa é a ilha v2, não o `L_Island` | `T_Mapa_UI` | Some quando o `L_Ilha` for o mapa; ou captura de cima do `L_Island` (PLANO.md 1.8) |
| K-12 | Média | Creeps sem NavMesh andam em linha reta e enroscam | `BP_Creep` | Acampamentos em clareiras; NavMesh no mapa v2 |
| K-13 | Média | 159 malhas com Nanite desligado estão **sem commit** | `Content/Quaternius`, `Content/LevelPrototyping` | Decidir com o usuário e commitar junto com a medição de desempenho |
| K-14 | Baixa | Tag `v0.1.1` aponta para o `2ff3965`, não para o código da 0.1.1 (`b63f296`) | GitHub | Na 0.1.2, a tag vai no commit certo |
| K-15 | Baixa | Meteoros e clarões saem creme; chão em chamas não parece fogo | `M_Projetil` | ART_DIRECTION.md §6 |
| K-16 | Baixa | Câmera às vezes nasce colada no herói (braço em 0 m); não se repetiu | `BP_HeroBase` | Investigar se voltar |
| K-17 | Baixa | Creeps batem no corpo do herói depois da morte (o dano é ignorado) | `BP_Creep.Think` | Checar `IsMorto` no alvo (M10) |
| K-18 | Baixa | Restos da v1 no projeto e nos scripts | AUDITORIA.md §6 | Limpeza junto com um marco que passe perto |
| K-19 | Baixa | Cópia da ilha com redirector pendurado | `Content/NexusRoyale/Map/_tmp/` | Consolidar e *Fix Up Redirectors* |
| K-20 | Baixa | O C: tem pouco espaço e o arquivo de paginação está nele | Máquina | Usuário: paginação no D: (AGENTS.md, Pendências) |
| K-21 | Média | Compilar C++ trava no HD lento e falha por falta de memória: em 15/10, 20:38, "C1060: espaço de heap do compilador insuficiente" no arquivo unity do módulo, com 2 GB de RAM livres e 25,7 de 28,9 GB de memória virtual em uso | Máquina | PCH no cache (AGENTS.md §5) e `ue_gas_compilar.py --pouca-memoria` (1 `cl.exe` por vez, sem unity). Fechar outros apps e o arquivo de paginação no D: (usuário) resolvem de vez |
| K-23 | Média | Antes do lobby (M4), a primeira partida não sabe quantos jogadores vêm: a Espera fecha em 3 s e um cliente que demora (de 6 a 60 s neste PC) entra como espectador | `ANRGameMode` | No teste, `pie_partida.py esperar` (`EsperarJogadores`). Nos recomeços já funciona (`UNRSessaoSubsystem`). O lobby (M4) resolve |
| K-24 | Baixa | Gravar um evento com corpo vazio pela DSL não apaga o corpo antigo (o `write_graph_dsl` ignora) | DSL | `Unreal/ue_bp_apagar_cadeia.py` apaga a cadeia de um evento pelo MCP (`delete_node`) |
| K-25 | Baixa | Mudar o CDO de um Blueprint pelo Python (sem salvar) antes do PIE não valeu no PIE (a Espera de 150 s usou 3 s) | Editor | Para números só de teste, use uma função `BlueprintCallable` no PIE (como `EsperarJogadores`) |
| K-22 | Baixa | Sem verificar: Alt+1/2/3 e Alt+4 no teclado; chamas da Bola de Fogo ferindo creeps; a morte pela tempestade | 0.1.1 | Testar no M0.5 |

## Resolvidos

| # | Problema | Quando | Como |
|---|---|---|---|
| — | Minimapa invisível no jogo empacotado (HLSL `.w` no SM6; ordem das chamadas de viewport) | 15/10 | Versão 0.1.1 (commit `b63f296`) |
| K-03 | Morte recarregava o mapa no próprio cliente (`OpenLevel`) | 15/10, M1 | O `ANRGameMode` decide fim e recomeço (`ServerTravel` com clientes; `OpenLevel` só sozinho) |
| K-05 | `Nivel` e `XP` não replicavam | 15/10, M1 | Replicados no ASC (XP só ao dono) e espelhados no `ANRPlayerState` |
| K-09 | GameMode global do projeto era o do template (herói da v1) | 15/10, M1 | `GlobalDefaultGameMode` = `GM_NexusRoyale` |
| — | O `ue_py.py` mandava o Python para um cliente de teste em vez do editor | 15/10, M1 | Pergunta a cada processo se é o editor; o `rede_testar.py` abre clientes sem Python remoto |
| — | Morte pela tempestade aparecia como "por HeroBase" | 15/10, M1 | Vítima como instigador = sem assassino |
