# Arquitetura de rede

Estado em 15/10, 22:05: **o estado da partida já é multiplayer** (M1: fase, vivos, vencedor, eliminação, morte, nível e
XP replicados; testado com PIE listen server + cliente sem render). **O resto do jogo ainda roda no input local**
(combate, interação, salto, inventário, mutações): M2 e M5. Este documento é o alvo e as regras; toda decisão de
autoridade nova entra aqui.

---

## 1. Modelo

- **Listen server:** quem cria a sala é o servidor e também joga. Os outros entram como clientes (D-003).
- **Servidor autoritativo:** o cliente pede, o servidor valida e decide. O cliente nunca decide dano, loot, XP, nível,
  morte, vitória, draft nem posse de item ou habilidade.
- **Pronto para dedicado:** nenhuma regra depende de "sou o host". O código testa `HasAuthority()`, nunca
  `IsLocallyControlled()`, para decidir regra. O HUD do host lê os mesmos dados replicados que um cliente.
- **Sem netcode próprio:** usamos replicação de propriedades, RPCs, CharacterMovement e GAS da Unreal.

## 2. Limitações do listen server (documentar para o jogador)

O listen server serve para protótipo, alfa, partidas casuais e privadas e o primeiro lançamento. Ele tem custos:

| Problema | Efeito | Resposta |
|---|---|---|
| **Latência zero do host** | O host reage antes de todos e ganha empates (inclusive no draft, D-007) | Aceito no modo casual; o modo ranqueado futuro usa dedicado |
| **Host vê mais** | O processo do host tem o estado de todos; um host trapaceiro pode ler posições | Aceito no casual; ranqueado em dedicado |
| **Estabilidade depende do host** | Se o host cai ou sai, a partida acaba para todos | MVP: encerra com aviso. Migração de host é marco avançado, depois do núcleo estável |
| **CPU e banda do host** | O PC do host roda o jogo + o servidor de 20 jogadores e ~70 creeps | Orçamento de servidor (§8); bots e creeps leves; testar no PC fraco do projeto |
| **NAT** | Conexão direta pela internet exige porta aberta no roteador do host | Steam Sockets ou EOS P2P (§6) |

**Modo ranqueado (futuro):** mesmas regras, rodando em servidor dedicado. Por isso as regras nunca ficam na UI de
hospedar sala nem no PlayerController do host.

> **Atenção:** compilar o alvo de **servidor dedicado** exige a Unreal compilada a partir do código-fonte (GitHub da
> Epic). A Unreal do launcher (a instalada em `D:\Epic Games\UE_5.8`) não gera o alvo `Server`. Isso entra no M25.

## 3. Quem é dono de quê

| Assunto | Dono (servidor) | Como chega ao cliente | Pedido do cliente |
|---|---|---|---|
| Fase da partida e tempos | `ANRGameMode` | `ANRGameState.Fase`, `FimDaFase` (horário do servidor) | — |
| Vagas, bots, pronto | `ANRLobbyGameMode` | `ANRLobbyGameState`, `ANRPlayerState` | `Server_MarcarPronto`; host: `Server_AdicionarBot`… |
| Draft | `UNRDraftComponent` (no GameState) | Lista replicada de escolhas; faixa e jogador da vez | `Server_Escolher(Habilidade)` |
| Habilidades possuídas | ASC do herói (concede no nascimento) | Specs replicados pelo GAS ao dono | Ativação pelo GAS |
| Custo, recarga, efeitos | GAS | Atributos e tags replicados | — |
| Dano, cura, morte | `AS_Hero` (`PostGameplayEffectExecute`) | Atributo `Vida`; `ANRPlayerState.bVivo` | — |
| Armas e munição | `UNRArmasComponent` | Arma na mão para todos; munição só ao dono | Disparo via GAS (ver §5) |
| Inventário | `UNRInventoryComponent` | Fast Array, **só ao dono** | `Server_UsarItem(Slot)`, `Server_SoltarItem` |
| Loot (sorteio) | `BP_LootChest.Interact` no servidor | Pickups replicados | `Server_Interagir(Alvo)` |
| Pegar item | Servidor (distância e fase) | Inventário do dono | `Server_Interagir(Alvo)` |
| XP, nível, pontos | ASC (servidor) | Espelho no `ANRPlayerState` | `Server_GastarPonto(Atributo)` |
| Mutações | `UNRMutacoesComponent` | Opções e escolhidas, só ao dono | `Server_EscolherMutacao(i)` |
| Abates, colocação | `ANRGameMode` | `ANRPlayerState` | — |
| Creeps e IA | Servidor (`Think`, StateTree) | Character replicado (movimento), vida, estado | — |
| Zona | `BP_StormController` **(já é assim)** | `StartTime`, centros; o resto é calculado igual nos dois lados | — |
| Dirigível e salto | `BP_DropShip` | Rota replicada (já é); passageiros | `Server_Saltar` |
| Vitória e resultados | `ANRGameMode` | `ANRGameState.Vencedor`, PlayerStates | — |

## 4. Replicação: estado ou RPC

- **Estado persistente** (fase, vida, inventário, escolhas) → **propriedade replicada** com `OnRep` para a UI.
  Quem entra atrasado ou reconecta recebe o estado certo.
- **Pedido do jogador** → **RPC `Server_`**, `Reliable`, sempre validado (dono, fase, distância, recarga, recurso).
- **Efeito passageiro sem estado** (som de impacto, faísca) → `Multicast` `Unreliable`, ou um Gameplay Cue do GAS.
- **Nunca:** RPC para algo que precisa existir depois (quem entra depois não recebe), nem propriedade replicada para
  efeito de 1 quadro.

**Condições de replicação:** inventário e mutações `COND_OwnerOnly`; munição `COND_OwnerOnly`; arma na mão para todos;
escolhas do draft para todos.

**Por ator (alvos iniciais, ajustar com o Network Insights):**

| Ator | Frequência de rede | Relevância | Dormência |
|---|---|---|---|
| Herói | 30–60 Hz (padrão do Character) | distância (`NetCullDistance` ~250 m) | — |
| Creep | 10 Hz | ~150 m | dorme quando o acampamento dorme |
| Baú | baixa | ~150 m | `DORM_Initial` até abrir |
| Pickup e bolsa | baixa | ~150 m | dormente depois de nascer; acorda ao mudar |
| Projétil | 30 Hz | ~250 m | — |
| Estrutura de habilidade | 10 Hz | ~250 m | — |
| `BP_StormController`, `BP_DropShip`, GameState | — | sempre relevante | — |

## 5. Predição

| O quê | Como |
|---|---|
| Movimento | CharacterMovement (predição e correção da engine) |
| Habilidades | GAS. Começar com `ServerInitiated`/`ServerOnly` nas complexas; `LocalPredicted` nas simples (custo, recarga, montagem). Efeitos visuais por Gameplay Cue |
| Armas | **"A favor de quem atira", com validação:** o cliente calcula o acerto e manda os dados de alvo (Target Data do GAS); o servidor confere cadência, munição, distância, linha de visão e ângulo, e só então aplica o dano. É o modelo do Lyra |
| Projéteis | O servidor cria o projétil de verdade; o cliente que atirou mostra um projétil falso na hora e esconde quando o real chega |
| Interação | Sem predição: a resposta do servidor chega em ~1 RTT, aceitável para baú e pickup |

## 6. Sessões e conexão

- `UNRSessaoSubsystem` (D-010) esconde a plataforma. A UI chama `Hospedar(opções)`, `Procurar()`, `Entrar(resultado)`,
  `EntrarPorIP(endereço)`, `Sair()`.
- **Desenvolvimento:** Online Subsystem **Null** (descoberta na LAN) e IP direto (`open 192.168.x.x:7777`).
- **Internet:**
  - Null/IP direto: o host abre a porta UDP 7777 no roteador (passo a passo para o usuário quando chegar a hora);
  - **Steam** (app de teste 480 no começo): sessões + Steam Sockets fazem a travessia de NAT;
  - **EOS:** sessões + P2P da Epic, sem depender da Steam.
- **Viagem:** menu → `L_Lobby?listen` → (começar) **seamless travel** para o mapa da partida → (fim) seamless travel de
  volta ao lobby. O seamless travel mantém as conexões e os PlayerStates (`CopyProperties`).

## 7. Desconexão

| Quando | Cliente sai | Host sai |
|---|---|---|
| Lobby | Vaga liberada | Sala fecha; clientes voltam ao menu com aviso |
| Staging | Vaga vira bot (opção da sala) | Fim para todos |
| Draft | Escolhas já feitas ficam; as que faltam viram automáticas (bot assume) | Fim para todos |
| Partida | **Proposta:** o herói é eliminado na hora, solta a bolsa e fica com a colocação do momento (alternativa: vira bot por 30 s) | Fim para todos, com aviso "o host saiu" |
| Reconexão | Fora do MVP. A arquitetura permite (estado em PlayerState e replicação), mas o modo solo sem respawn não exige | — |

**Contagem de vivos** sempre recalculada a partir dos PlayerStates (não de um contador solto), para uma desconexão não
deixar o número errado. Vitória dispara **uma vez** (a fase Final é um estado; o GameMode ignora eliminações depois).

## 8. Orçamento e escala

- **Alvo:** 20 jogadores, ~70 creeps, ~100 pickups ativos, ~30 projéteis e ~10 estruturas ao mesmo tempo.
- **Servidor:** `NetServerMaxTickRate` 30 no começo; medir antes de subir.
- **Replication Graph / Iris:** só se o perfil do teste de 20 (M18) mostrar o servidor gastando demais em replicação.
  Até lá, relevância por distância e dormência bastam.
- **Ferramentas:** Network Insights (`-NetTrace=1`), `stat net`, `net.ListActorChannels`, simulação de rede
  (`NetEmulation.PktLag`, `PktLoss`) nos testes.

## 9. Contra trapaça (o básico)

- Toda RPC confere: o pedido é do dono? A fase permite? Está perto o bastante? A recarga passou? Tem recurso?
- Taxa de disparo e munição contadas no servidor.
- O cliente nunca manda "acertei X com Y de dano"; manda "atirei daqui para lá" (e o servidor recalcula o dano).
- Espectador recebe só o que o espectado vê.
- XP, nível, itens e habilidades nunca vêm do cliente.

## 10. Como testar rede neste PC

O PC do projeto (RX 570 de 4 GB, 16 GB de RAM) não aguenta dois PIEs com render. Ver [TEST_PLAN.md](TEST_PLAN.md), §2:
- **PIE listen server + 1 cliente** só com o editor recém-aberto e nada mais pesado aberto;
- **clientes sem render:** `UnrealEditor.exe NexusRoyale.uproject 127.0.0.1 -game -nullrhi -nosound -log` (conecta ao
  PIE ou a um host `-game`); servem para replicação e para o teste de 20;
- **bots** preenchem as vagas nos testes de partida inteira.
