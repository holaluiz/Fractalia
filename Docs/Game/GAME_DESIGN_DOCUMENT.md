# Nexus Royale: documento de design (v3, PROPOSTA)

> **Status: proposta, aguardando o usuário.** O design oficial continua sendo o [GDD v2](../../Design/GDD.md) até o
> usuário aprovar a decisão [D-002](DECISIONS.md#d-002--a-nova-direção-contra-o-gdd-v2--aguardando-o-usuário). Os
> pontos que dependem dessa resposta estão marcados com **⚑ D-002x**. Os números são **valores iniciais**; as fórmulas
> e as tabelas ficam no [BALANCE.md](BALANCE.md).

Escrito em 2026-10-15 a partir do pedido "Lead Game Architect" do usuário e do GDD v2.

---

## 1. Pitch

Battle royale **solo** em terceira pessoa para **até 20 jogadores**. Antes de saltar, cada jogador faz um **draft** de
3 habilidades básicas e 1 ultimate, **únicas na partida**: se você pegou, ninguém mais tem. Na ilha, encontra **armas**
(uma de perto, uma de longe) e **itens**, mata **creeps** e jogadores para subir de **nível**, e escapa da
**tempestade**. O último vivo vence.

**Fácil de entender:** ache armas e itens, mate creeps, suba de nível, lute, fique na zona, seja o último.
**Difícil de dominar:** combinar habilidades, negar habilidades no draft, escolher armas e atributos, ler o terreno,
arriscar no PvE, rotacionar com a zona.

## 2. Pilares

1. **Toda morte é legível.** Dá para saber o que acertou você, de onde veio e se dava para desviar.
2. **Todo poder tem contrajogo.** Telegrafia, som, tempo de viagem, alcance, recarga, custo ou risco de posição.
3. **Combinações, não habilidades soltas.** O pool é desenhado para criar sinergias (ver §6.4).
4. **Risco gera vantagem, não vitória garantida.** Quem joga bem fica mais forte; o resultado continua em aberto.
5. **O campo é uma arma.** Sem construção: cobertura e altura vêm do terreno e das habilidades de campo (do GDD v2).

## 3. Fluxo da sessão

Cada fase é um estado explícito do servidor (`ENRFaseDaPartida`, [GAMEPLAY_SYSTEMS.md](GAMEPLAY_SYSTEMS.md), §1).

| Fase | Duração alvo | O que acontece |
|---|---|---|
| Menu | — | Jogar → Hospedar ou Entrar |
| Lobby | livre | 20 vagas (humanos e bots); o host configura e começa |
| Staging (Ilha de Espera) | até todos carregarem (máx. 60 s) | Todos nascem numa área segura no mapa da partida; dá para andar e treinar a mira |
| Draft | 2–3 min | 4 rodadas (1 de ultimate + 3 de básicas), ver §6 |
| Queda | ~1 min | O dirigível cruza a ilha; cada um salta quando quer |
| Partida | ~14 min | Loot, PvE, PvP, níveis, tempestade em 6 fases |
| Final | — | Quando sobra 1 vivo: combate congela, vencedor anunciado |
| Resultados | 15 s | Colocação, abates, dano, build; volta ao lobby |

**Sessão completa: ~18 min** (⚑ D-002h). O pedido sugere 18–25 min de partida; o GDD v2 dizia 14. O teste de 20
jogadores decide.

## 4. Sala, lobby e host

- **Host:** quem cria a sala vira o servidor (listen server). Ver [NETWORKING_ARCHITECTURE.md](NETWORKING_ARCHITECTURE.md).
- **20 vagas.** Cada uma: humano ou bot. A partida só começa com as 20 preenchidas (o host completa com bots).
- **O host pode:** adicionar e remover bot, mudar a dificuldade do bot, expulsar, mudar as opções da partida, começar.
- **Cada humano mostra:** nome, conexão, pronto/carregando, ping.
- **Começar** só fica disponível com: 20 vagas preenchidas, todos os humanos "prontos", nenhum carregando.
- **Saídas:** cliente que sai no lobby libera a vaga. Host que sai no lobby fecha a sala. Host que sai na partida
  **encerra a partida para todos** (sem migração de host no MVP).

## 5. Staging (Ilha de Espera)

- Fica **dentro do mapa da partida** (D-006): uma plataforma fora da costa, longe do círculo inicial.
- Serve para: esperar todos carregarem, estabilizar a replicação inicial, compilar shaders e carregar assets antes do
  combate, e dar algo para fazer (andar, pular, atirar em alvos).
- Sem dano entre jogadores, sem loot.
- Termina quando todos os humanos avisam "carreguei" **ou** depois de 60 s. Quem não carregou vira bot naquela vaga
  (ou é removido; opção da sala).

## 6. Draft de habilidades

### 6.1 Regras

- Cada jogador termina com **1 ultimate + 3 básicas**. **Nenhuma habilidade se repete** na partida.
- O servidor é o dono: valida cada escolha, trava na hora e replica o quadro para todos.
- **Pool = escolhas × 1,6.** Com 20 jogadores: 80 escolhas → **128 habilidades** (32 ultimates + 96 básicas). O fator
  fica em dados; no desenvolvimento usamos um pool menor (§6.5).
- **Ultimate primeiro** (rodada 1), básicas nas rodadas 2–4: a ultimate é o maior pico de poder, e escolhê-la antes
  permite montar a build em volta dela.
- A ordem é **serpente**: quem escolheu por último numa rodada escolhe primeiro na próxima.
- **Tempo esgotado:** o servidor escolhe pela lista de preferências que o jogador marcou (ou, sem lista, pela
  sugestão do jogo).

### 6.2 Formato (⚑ D-007)

**Recomendado: serpente em 4 faixas paralelas.** Os 20 jogadores são divididos em 4 faixas de 5. Em cada faixa, um
escolhe por vez (janela de 8 s); as 4 faixas andam juntas sobre o pool global. A composição das faixas e a ordem
mudam a cada rodada. Simulado: **2,4 min** em média; o sequencial levaria 7,3 min. Alternativa já desenhada: reserva
simultânea (1,1 min). Detalhes e números no [BALANCE.md](BALANCE.md), §3.

### 6.3 O que o jogador vê

- O pool inteiro, filtrável por categoria, com as já escolhidas riscadas e o nome de quem pegou.
- A build de cada jogador sendo formada (para negar e responder).
- Antes de começar, 10 s de prévia do pool, e uma **lista de preferências** que o jogador pode marcar (usada se o
  tempo esgotar).

### 6.4 Categorias e combinações

Categorias (Gameplay Tags `Ability.Category.*`): Dano, Mobilidade, Defesa, Controle, Sustento, Utilidade, Visão,
Armadilha, Deslocamento, Invocação, mais **Campo** (cria ou destrói terreno, do GDD v2 §6.2).

Combinações que o pool deve permitir (exemplos do pedido e do GDD v2): mobilidade + dano em área; lentidão + arma de
precisão; empurrão + terreno; visão + arma de longe; escudo + arma de perto; armadilha + deslocamento; fogo +
vegetação; gelo + água.

### 6.5 Pool inicial

As **14 magias e 7 ultimates do GDD v2** (§6.3 e §6.4: Arremetida, Bola de Fogo, Muralha de Gelo, Chuva de Meteoros,
Domo Glacial…) são o primeiro pool. Elas já têm números, contrajogo e interações. As passivas do v2 (Coração Gélido,
Sifão, Graça, Carga Estática) contam como básicas. O pool cresce por dados até 128 (M21).

## 7. Combate

### 7.1 Armas (⚑ D-002b)

- **Dois slots:** 1 de **perto** e 1 de **longe**. Teclas 1 e 2 (e a roda do mouse). Não ocupam os slots de item.
- A arma é a ferramenta principal; as habilidades complementam. A arma **nunca** pode ficar irrelevante no fim: o
  dano de arma escala com o atributo Poder e com a raridade, como as habilidades escalam com o Arcano.
- Tudo é **dado** (`UNRWeaponDefinition`): dano, cadência, alcance, velocidade do projétil, dispersão, pente, recarga,
  raridade, penalidade de movimento, multiplicador de cabeça, animações, VFX, sons.
- **Sem caixa de munição:** cada arma tem pente e recarga (menos loot para administrar).
- **Primeiras famílias (fatia vertical):**

  | Slot | Arma | Ideia |
  |---|---|---|
  | Perto | Espada | Golpe em arco de 2,5 m, combo de 3 |
  | Perto | Bacamarte | Escopeta: 8 projéteis em cone, forte até 8 m |
  | Longe | Arco | Projétil com queda; segurar carrega (do Patrulheiro do v2) |
  | Longe | Cajado Arcano | Dardo rápido levemente teleguiado (o dardo atual do Feiticeiro) |

- **Raridade da arma:** Comum a Lendária, **+5% de dano por nível de raridade** (pouco, para a sorte não decidir a
  luta; ver BALANCE.md).

### 7.2 Habilidades

- **Q, E, R:** as 3 básicas do draft. **T:** a ultimate (⚑ D-002g). Liberada no **nível 6**.
- Custam **mana** e têm recarga. A mana limita o volume numa luta; a recarga, a frequência (do GDD v2 §5).
- **Esquiva** (Shift), comum a todos: 5 m, 0,2 s de invulnerabilidade, recarga de 6 s (⚑ D-002j).
- **Regras de contrajogo** (valem para todo o pool; checklist no [ABILITY_SYSTEM.md](ABILITY_SYSTEM.md), §5):
  - dano ≥ 100 tem projétil visível ou aviso no chão por pelo menos 0,3 s; ultimates, 0,5–1 s;
  - controle dura no máximo 1,5 s; depois dele, 2 s de controles pela metade;
  - nenhuma invisibilidade sem contra (Luz revela; dano revela);
  - nenhuma mobilidade infinita (cargas e recarga);
  - nada mata de vida cheia sem aviso.

### 7.3 Dano e TTK

- **TTK alvo** (do GDD v2 §9): 4–6 s entre dois jogadores do mesmo nível com kit completo; nunca menos de 2 s nem mais
  de 12 s. Com armas, a planilha de TTK precisa ser refeita (BALANCE.md, §5).
- Armadura reduz todo o dano: `0,04·A / (1 + 0,04·A)`.
- Bônus de dano somam entre si; efeitos temporários multiplicam por cima.

## 8. Itens e loot

### 8.1 Inventário (⚑ D-002c)

- **6 slots de item**, teclas **Z X C V B N** (remapeáveis). Armas ficam nos 2 slots próprios.
- Tipos: **ativo** (tem efeito ao usar, com recarga ou cargas), **passivo** (bônus enquanto estiver no slot),
  **consumível** (pilha, some ao acabar).
- Cada slot mostra: ícone, pilha, recarga, cargas, se dá para usar, dica.
- Os **equipamentos do GDD v2** (Couraça, Anel do Foco, Amuleto do Tempo…) viram **passivos**. Os consumíveis do v2
  (Comida, Refeição, Poções) continuam, com pilha.
- **Tomo** (antigo grimório, ⚑ D-002d): consumível; ao usar, escolhe uma das suas habilidades e ela sobe +1 rank
  (máximo 3; ranks do GDD v2 §6.3).

### 8.2 Baús e tabelas

- O loot é **sorteado no servidor**, no momento em que o baú abre, por **tabelas de loot** (dados, não Blueprint).
- **Raridade:** Comum, Incomum, Raro, Épico, Lendário (cores do GDD v2 §8.1).
- **Princípio:** a sorte gera adaptação, não decide o vencedor. Loot melhor fica em lugares perigosos (centro, POIs
  expostos, acampamentos médios e elites, baús dourados).
- Fontes (do GDD v2 §8.4): baú comum, baú dourado, drop aéreo, creeps, morte de jogador.

### 8.3 Morte de jogador

- Solta **tudo** (6 slots + 2 armas) numa **bolsa** no chão (D-009), que qualquer um pode abrir.

## 9. Creeps (PvE)

- Base do GDD v2 §12: acampamentos pequenos (3 Imps), médios (Puglin + 2 Imps), elites (Puglin Ancião); corrente de
  15 m; XP e drop para quem dá o golpe final; ícone de luta no minimapa depois de 2 s.
- **Não são sacos de XP:** cada tipo tem uma ameaça própria e o barulho atrai jogadores.
- **Tipos futuros:** corpo a corpo, à distância, rápido, tanque, suporte, elite. Começa com Imp (corpo a corpo, rápido)
  e Puglin (tanque); o primeiro novo é um **à distância** (M10).
- **Uso tático:** puxar um acampamento para cima de outro jogador funciona (o creep ataca quem o machucou por último).

## 10. Progressão na partida

### 10.1 XP e níveis

- Níveis **1 a 10** (teto testável até 12). Curva do GDD v2 §7.1 como ponto de partida.
- **Fontes:** creeps; abates de jogador; mais tarde, objetivos disputados.
- **Abate de jogador** escala com a diferença de nível (BALANCE.md, §4): matar alguém muito mais fraco rende pouco;
  matar alguém mais forte rende muito.

### 10.2 Atributos (⚑ D-002e/f)

- **1 ponto por nível** (9 pontos até o 10), distribuído na hora (painel ou atalho) e guardado se não for usado.
- **4 atributos:**

  | Atributo | Efeito por ponto efetivo |
  |---|---|
  | **Vigor** | +vida máxima, +tenacidade (reduz controle) |
  | **Poder** | +dano de arma |
  | **Arcano** | +dano e cura de habilidade, +mana máxima |
  | **Agilidade** | +velocidade, −recarga de habilidades, +velocidade de recarga e troca de arma |

- Retorno decrescente: os primeiros pontos valem mais (fórmula do GDD v2 §4.2, adaptada no BALANCE.md).
- **Mutações** nos níveis 3, 6 e 9 (3 opções, Alt+1/2/3): o componente que já existe, com as mutações de habilidade
  vindo dos dados de cada habilidade.

### 10.3 Anti-bola-de-neve

Vantagem para quem joga bem, sem vitória matemática. Mecanismos, nesta ordem (ver BALANCE.md, §6):
1. teto de nível baixo e ganho por nível pequeno;
2. retorno decrescente nos atributos;
3. raridade de arma e item com efeito pequeno;
4. XP de abate ajustado pela diferença de nível;
5. piso de nível no fim de cada fase da tempestade (do GDD v2 §7.3);
6. quem está forte vira alvo: abates de quem tem nível alto rendem mais, e a luta faz barulho no mapa;
7. cura limitada.
Bônus de recuperação para quem está atrás só entra se o teste mostrar que precisa.

## 11. Zona (tempestade)

- Servidor é o dono. Cada fase: espera, fechamento, novo raio, dano fora da zona (% da vida máxima, sobe a cada fase).
- Base: as 6 fases do GDD v2 §13 (`CT_Storm`). Início sem punir exploração; fim rápido.
- A zona aparece no minimapa, no mapa, no relógio do HUD, com aviso sonoro e parede visível.

## 12. Queda

- Depois do draft, todos embarcam no **dirigível**, que cruza a ilha numa rota que muda a cada partida.
- Cada um salta quando quer (servidor valida: só sobre a ilha). Queda livre, planagem controlada, pouso.
- Rota e veículo em dados, para outros veículos e rotas no futuro.

## 13. Morte, espectador e vitória

- Morte é permanente. O servidor: desliga o controle, solta a bolsa, dá o XP a quem matou, atualiza os vivos, registra
  abate e morte, e passa o morto para **espectador** (assiste a quem o matou, depois a qualquer vivo; sem ver a posição
  de ninguém além do que o espectado vê).
- Com **1 vivo**: fim da partida, uma vez só, combate congelado, tela de vitória para o vencedor e de colocação para
  os outros, depois resultados.

## 14. Mapa

- A **ilha v2** (1 km, 9 POIs, rio, lagos, 21 acampamentos) é o alvo ([Design/Mapa.md](../../Design/Mapa.md)).
- O tamanho vem da **frequência de encontros**, não do que a Unreal aguenta.
- **Graybox antes da arte** (M17): medir tempo entre POIs, caminhada, rotação, encontros e linhas de visão. Metas no
  [MAP_DESIGN.md](MAP_DESIGN.md).

## 15. Direção de arte

Mundo 3D **pintado** (aquarela/ilustração), não fotorrealista, com silhuetas legíveis. Iluminação de humor
(pôr do sol, noite) e materiais pintados. Detalhes no [ART_DIRECTION.md](ART_DIRECTION.md). A regra do GDD v2 vale:
personagens, magias e avisos ficam fora do filtro de aquarela e mantêm o contorno nítido.

## 16. Áudio

O som é informação de jogo: tiros perto, habilidades, ultimates (ouvidas a 50 m), baú, passos, aggro de creep, dano,
vida baixa, aviso da zona, nível, eliminação. Áudio espacial; sons críticos têm prioridade sobre o ambiente.

## 17. Controles

Resumo (⚑ D-002g; tabela completa no [UI_UX.md](UI_UX.md)): WASD, Espaço, Ctrl; botão esquerdo ataca com a arma;
direito mira; 1/2 armas; Q/E/R básicas; T ultimate; Shift esquiva; F interage; Z X C V B N itens; Tab inventário e
atributos; M mapa; Esc menu. **Tudo remapeável.**

## 18. O que fica e o que sai do GDD v2

| Fica | Sai (se D-002 for aprovada) |
|---|---|
| Battle royale solo de 20, dirigível, tempestade em 6 fases com piso de nível | Arquétipos e silhueta por arquétipo |
| Vida e mana; esquiva | 20 pontos na montagem e builds salvas |
| As 14 magias + 7 ultimates (viram o pool inicial do draft) | Q e ultimate escolhidas sozinho |
| Magias de campo e terreno reativo | Grimórios como fonte de E/R (viram Tomos) |
| Creeps, acampamentos, drops | 4 slots de equipamento + 3 de consumível |
| Raridades, equipamentos (como passivos), consumíveis | 5 atributos da build (viram 4, por nível) |
| Mutações (em 3 níveis) | Mutação em todo nível |
| Ilha v2 de 1 km; cartoon + aquarela | |

## 19. Perguntas de diversão (todo playtest)

Há interação suficiente? A travessia é chata? O PvE cria decisões? O loot empolga sem ser injusto? O mais fraco consegue
virar? Dá para mostrar habilidade mecânica? As habilidades são legíveis? As mortes são compreensíveis? A partida é
longa demais? O draft é estratégico ou chato? Há várias builds viáveis? Acampar compensa demais? A mobilidade está forte
demais? O longo alcance oprime? Subir de nível cria escolhas? As respostas vão para o [BALANCE.md](BALANCE.md), §8.
