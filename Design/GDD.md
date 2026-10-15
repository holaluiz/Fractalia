# NEXUS ROYALE — Documento de Design (v2)

> Battle royale **solo** de magias com progressão de MOBA. Você monta seu campeão antes
> da partida (arquétipo, atributos, magia principal e ultimate) e, dentro dela, sobe de
> nível, encontra grimórios e itens e enfrenta creeps e outros jogadores até sobrar um.

A versão anterior (heróis de kit fixo, construção, torres e Guardião) está arquivada em
[GDD_v1.md](GDD_v1.md). Nada dela foi mantido.

Os números deste documento são **valores iniciais de balanceamento**. Eles devem ir para
tabelas de dados na Unreal (seção 16) e ser ajustados em teste. A primeira rodada de ajuste
(15/10) veio da simulação de TTK em [Simulacao_TTK.xlsx](Simulacao_TTK.xlsx).

---

## 1. Pitch

- **20 jogadores**, cada um por si, saltam de um dirigível sobre uma ilha.
- **Antes da partida**, cada um escolhe um **arquétipo**, distribui **20 pontos** em
  5 atributos e escolhe **1 magia principal** e **1 ultimate**.
- **Na partida**, abre baús (itens, grimórios de magia e consumíveis) e mata creeps e
  jogadores para subir do **nível 1 ao 10**.
  - A ultimate é liberada no **nível 6**.
  - A cada nível, o jogador escolhe uma **mutação** entre três.
- **Duas barras:** vida e mana. As magias gastam mana e têm recarga.
- **Sem construção.** O campo de batalha muda com **magias de campo**: muralhas, pilares,
  zonas de fogo, névoa e vento. Os elementos também **interagem entre si e com o
  terreno**.
- A tempestade fecha o mapa e o último vivo vence. A partida dura cerca de **14 minutos**.

## 2. Pilares de design

1. **Sua build, sua identidade.** As escolhas feitas antes da partida definem *como* você
   joga, e não apenas números maiores.
2. **Todo combate é legível.** Dá para saber o que o inimigo é e o que ele vai fazer antes
   de morrer para isso.
3. **O campo é uma arma.** Sem construção, cobertura e altura vêm das magias e do terreno.
4. **Risco gera recompensa.** Farmar e lutar dão poder, mas expõem você.
5. **Habilidade antes de números.** Nível e itens abrem opções, e a diferença de poder entre
   jogadores tem limite.

## 3. Loop da partida

| Momento | Tempo | O que acontece |
|---|---|---|
| Pré-partida | lobby | Escolher uma das builds salvas (seção 4.5) |
| Queda | 0:00–1:00 | Dirigível cruza a ilha; saltar e planar até o ponto escolhido |
| Início | 1:00–4:00 | Baús, primeiros acampamentos de creeps; níveis 1→3 |
| Meio | 4:00–9:00 | Acampamentos médios, primeiras lutas, elites acordam (4:00), 1º drop aéreo (6:30); ultimate por volta de 7–8 min |
| Final | 9:00–14:00 | Tempestade aperta, 2º drop aéreo (10:30), níveis 7–10, briga final |

---

## 4. Pré-partida: montagem do campeão

A montagem tem quatro escolhas em sequência: **Arquétipo → Atributos → Magia principal →
Ultimate**.

### 4.1 Arquétipos

O arquétipo é a base fixa. Ele define a **silhueta**, o **ataque básico**, uma **passiva**
e os valores base. Atributos e magias personalizam por cima. Qualquer arquétipo pode usar
qualquer magia, desde que cumpra os requisitos (4.3).

**Por que arquétipo + personalização:** liberdade total deixa todo inimigo irreconhecível e
facilita surgir uma build dominante. O arquétipo garante leitura à distância (silhueta e
arma na mão) e um piso de identidade. Os 20 pontos, a magia principal e a ultimate ainda dão
centenas de combinações.

| Arquétipo | Visual (Quaternius) | Vida | Mana | Veloc. | Ataque básico | Passiva |
|---|---|---|---|---|---|---|
| **Guerreiro** | Outfit Peasant + arma pesada (`Hammer_Double`, `Sword_big`) | 550 | 150 | 6,0 m/s | Golpe em arco de 3 m, 65 físico, 1 golpe a cada 0,9 s | **Ímpeto:** cada golpe básico que acerta dá +4% de velocidade por 3 s (acumula 5×) |
| **Patrulheiro** | Outfit Ranger + arco (`Bow_Wooden`) | 450 | 170 | 6,3 m/s | Flecha carregável: 30–90 físico (segurar até 1 s), alcance 60 m | **Rastreador:** inimigos que você acerta deixam pegadas visíveis só para você por 6 s |
| **Feiticeiro** | Outfit Peasant + grimório na mão (`Book2_Open`) | 400 | 260 | 6,0 m/s | Dardo arcano levemente teleguiado, 60 mágico, 35 m, 1 a cada 1,0 s | **Canalizador:** a cada 3 magias lançadas, a próxima custa metade da mana |
| **Místico** | Outfit Ranger com capuz + amuleto/cristal (`Necklace2`, `Crystal3`) | 480 | 220 | 6,0 m/s | Feixe contínuo de 15 m, 100 mágico/s; cura 10% do dano causado | **Elo Vital:** ao matar creep ou jogador, recupera 15% da vida e da mana máximas |

**Habilidades comuns a todos:**

- **Esquiva** (Shift): 5 m, 0,2 s de invulnerabilidade, recarga de 6 s, sem custo de mana.

### 4.2 Atributos

- **Pontos:** 20 para distribuir, com **no máximo 10 por atributo**.
- **Retorno decrescente:** os pontos 1–5 valem 1,0 cada, os pontos 6–8 valem 0,6 e os
  pontos 9–10 valem 0,3. Um atributo com 10 pontos rende **7,4 pontos efetivos**. Isso
  torna "tudo num atributo" ruim, sem proibir.

| Atributo | Por ponto efetivo | Combina com |
|---|---|---|
| **Força** | +4% dano físico (armadura vem só de itens) | Guerreiro e Patrulheiro de dano |
| **Agilidade** | +3% velocidade de ataque, +1,5% velocidade de movimento, −4% recarga da esquiva | Patrulheiro, perseguição, fuga |
| **Vitalidade** | +30 vida máxima, +0,4 vida/s | Tanque, magias de Terra |
| **Intelecto** | +25 mana máxima, +4% poder mágico (dano mágico) | Feiticeiro, Fogo, Gelo |
| **Espírito** | +0,5 mana/s, −2,5% recarga de magias, +4% cura recebida | Místico, Luz, Sombra |

**Exemplos de build:**

| Build | For | Agi | Vit | Int | Esp | Resultado |
|---|---|---|---|---|---|---|
| Guerreiro brigador | 7 | 4 | 7 | 0 | 2 | +25% dano físico, +186 vida, +6% veloc. |
| Patrulheiro caçador | 6 | 8 | 3 | 0 | 3 | +22% dano físico, +20% veloc. de ataque, +10% veloc. |
| Feiticeiro de Fogo | 0 | 2 | 4 | 8 | 6 | +27% poder mágico, +170 mana, −14% recarga |
| Místico resistente | 0 | 2 | 6 | 4 | 8 | +168 vida, +3,4 mana/s, −17% recarga, +27% cura |

### 4.3 Requisitos de magia

- **Requisito:** cada magia pode exigir um mínimo de **pontos investidos** (não efetivos)
  num atributo. Exemplo: Bola de Fogo exige Intelecto 3.
- **Na montagem**, a magia principal e a ultimate **precisam** cumprir o requisito.
- **Na partida**, um grimório sem o requisito pode ser equipado mesmo assim, com
  **60% do efeito e +30% de custo de mana**. Nenhum loot é inútil, mas a build certa rende
  mais.

### 4.4 Magias: modelo híbrido

| Slot | Tecla | Origem | Pode trocar na partida? |
|---|---|---|---|
| Magia principal | Q | Escolhida na montagem | Não (só melhora de rank) |
| Magia 2 | E | Grimório achado na partida | Sim |
| Magia 3 | R | Grimório achado na partida | Sim |
| Ultimate | X | Escolhida na montagem, liberada no nível 6 | Não |

Qualquer slot de magia comum (Q, E, R) pode conter uma magia **ativa** ou **passiva**.
As passivas têm orçamento de poder menor (seção 6).

**Por que o híbrido:**

- **Identidade garantida, metade fixa.** A magia principal e a ultimate são planejadas com
  os atributos e os requisitos. O jogador entra sabendo seu combo central e pode treiná-lo.
  A ultimate é o maior pico de poder, então ela precisa ser previsível para quem a escolheu.
- **Variedade e adaptação, metade variável.** Os slots E e R vêm do loot. Nenhuma partida
  é igual, o jogador se adapta ao que encontra e o prazer de "achar coisa boa" (o coração do
  battle royale) continua existindo.
- **Combate ao meta resolvido.** Como metade do kit não é conhecida antes da partida,
  nenhuma build completa pode ser "a melhor". A metade fixa ainda recompensa quem planejou.
- **Sorte sob controle:**
  - **Grimório garantido:** acampamentos médios sempre soltam um. Farmar é uma rota
    previsível para conseguir magias.
  - **Afinidade:** 40% dos grimórios rolados para você são de escolas que você já tem
    equipadas (principal ou ultimate).
  - **Sem requisito, ainda funciona:** a magia rende 60% do efeito (4.3).
  - **Grimório repetido melhora a magia:** um grimório da mesma magia sobe o rank, inclusive
    o da principal.
- **Equilíbrio entre os slots fixos e os variáveis:** a principal não troca, mas sobe de
  rank. A ultimate não troca, mas melhora por mutações. Os grimórios trocam
  livremente: ao trocar, o antigo cai no chão e outro jogador pode pegar.

### 4.5 Builds salvas e justiça

- **Builds salvas:** até **5**, editáveis livremente entre partidas.
- **Igualdade:** todos os jogadores têm os mesmos 20 pontos e acesso a todos os
  arquétipos e magias.
- **Progressão de conta só dá cosmético.** Cosméticos **nunca** mudam a silhueta do
  arquétipo nem a cor das escolas de magia (seção 10).

---

## 5. Vida e mana

| | Vida | Mana |
|---|---|---|
| Base | Do arquétipo | Do arquétipo |
| Por nível | +80 | +20 |
| Regeneração | Só Vitalidade (+0,4/s por ponto), passiva Graça e consumíveis; sem regeneração natural | 2/s em combate, 8/s fora de combate, mais Espírito |
| Recupera com | Comida, Sifão, Farol, Aurora, Coração Gélido, Elo Vital, feixe do Místico | Poção de mana, Elo Vital |

- **Em combate** significa que você causou ou recebeu dano de jogador nos últimos 5 s.
- **Papéis separados:** a recarga limita a **frequência** de cada magia, e a mana limita o
  **volume total** de magias numa luta. Quem esvazia a mana fica vulnerável. Isso cria o
  ritmo lutar → recuar → recarregar.
- **Sem custo de mana:** o ataque básico e a esquiva.
- **Mana visível:** a mana do inimigo aparece na barra acima dele (seção 10). "Ele está sem
  mana" é uma decisão de jogo.

---

## 6. Magias

### 6.1 Escolas

Cada escola tem **cor, som e forma de efeito próprios**. Essa é a principal ferramenta de
leitura do combate.

| Escola | Cor | Dano | Papel |
|---|---|---|---|
| Marcial | Prata | Físico | Investidas, tiros especiais, quebrar estruturas |
| Fogo | Laranja | Mágico | Dano em área, negar terreno, queimar vegetação |
| Gelo | Ciano | Mágico | Cobertura, plataformas sobre a água, sobrevivência |
| Terra | Âmbar | Mágico | Altura, muralhas, deslocar inimigos |
| Tempestade | Azul elétrico | Mágico | Mobilidade, empurrões, raios |
| Sombra | Violeta | Mágico | Visão, emboscada, roubo de vida |
| Luz | Dourado | Mágico | Revelar, curar, anular Sombra |

### 6.2 Magias de campo

Sem construção, o campo de batalha muda pelas **magias de campo** (marcadas com ◆ nas
tabelas). Elas criam ou destroem cobertura, dão altura, negam áreas ou alteram a visão.
Toda escola elemental tem pelo menos uma. A Marcial não tem: ela é a resposta a essas
magias, porque destrói estruturas (6.5). Estruturas criadas por magia têm vida, aparecem para todos
e podem ser destruídas por dano ou por magias Marciais.

### 6.3 Magias comuns (14)

| Magia | Escola | Tipo | Efeito | Mana | Recarga | Requisito |
|---|---|---|---|---|---|---|
| **Arremetida** | Marcial | Ativa | Avança 8 m; o primeiro inimigo sofre 90 e é empurrado 3 m; destrói estruturas mágicas no caminho | 40 | 9 s | Força 3 |
| **Tiro Rasante** | Marcial | Ativa | O próximo ataque básico vira projétil que atravessa inimigos e estruturas mágicas: 120 de dano e revela os atingidos por 3 s | 45 | 8 s | Agilidade 3 |
| **Bola de Fogo** | Fogo | Ativa | Projétil que explode num raio de 3 m: 130 de dano; incendeia vegetação | 55 | 7 s | Intelecto 3 |
| **Muro de Chamas** ◆ | Fogo | Ativa | Linha de fogo de 10 × 2 m por 5 s; quem atravessa sofre 60 + queimadura de 20/s por 3 s; queima vegetação | 60 | 14 s | — |
| **Muralha de Gelo** ◆ | Gelo | Ativa | Parede de 6 × 3,5 m a até 15 m, com 400 de vida, por 6 s; bloqueia projéteis e passagem | 50 | 12 s | Intelecto 2 |
| **Coração Gélido** | Gelo | Passiva | Ao cair abaixo de 30% de vida, fica preso em gelo por 1,5 s (invulnerável, imóvel) e cura 15% da vida. Recarga de 60 s | — | — | Vitalidade 4 |
| **Pilar de Pedra** ◆ | Terra | Ativa | Ergue um pilar de 2 × 2 × 4 m a até 15 m, por 8 s. Dá altura e cobertura; se surgir sob um inimigo, ele é lançado e atordoado por 0,5 s | 50 | 10 s | Vitalidade 2 |
| **Fissura** ◆ | Terra | Ativa | Rachadura em linha de 12 m: 100 de dano, lentidão de 40% por 2 s; derruba estruturas mágicas; deixa terreno irregular (−20% de velocidade) por 4 s | 55 | 11 s | Vitalidade 3 |
| **Rajada** ◆ | Tempestade | Ativa | Cone de vento de 8 m: empurra inimigos 6 m, desvia projéteis e empurra zonas (fogo, névoa). Mirando o chão, impulsiona você 8 m para cima com planagem curta | 45 | 9 s | Agilidade 2 |
| **Carga Estática** | Tempestade | Passiva | A cada 4º ataque básico, um raio salta para até 2 inimigos a 8 m (60 de dano, conta como raio para interações) | — | — | Agilidade 3 |
| **Névoa Sombria** ◆ | Sombra | Ativa | Nuvem de 7 m por 6 s: bloqueia a linha de visão; projéteis teleguiados perdem o alvo; quem está dentro some do radar de pegadas | 55 | 15 s | Espírito 2 |
| **Sifão** | Sombra | Passiva | 6% do dano mágico causado vira vida | — | — | Espírito 3 |
| **Farol** ◆ | Luz | Ativa | Planta um farol (150 de vida) por 8 s: revela inimigos invisíveis ou em névoa num raio de 15 m e cura você em 20/s a até 6 m dele; dissipa Névoa Sombria | 60 | 16 s | Espírito 3 |
| **Graça** | Luz | Passiva | Fora de combate, regenera 2% da vida máxima/s; consumíveis curam 25% a mais | — | — | Espírito 2 |

**Ranks (via grimório repetido ou mutação):**

| Rank | Efeito |
|---|---|
| 1 | Valores da tabela |
| 2 | +20% de efeito |
| 3 | +40% de efeito e −15% de recarga |

### 6.4 Ultimates (7)

As ultimates são liberadas no **nível 6** e melhoram só por mutações (7.4). Todas têm
aviso visual e sonoro de 0,5–1 s antes do impacto e são ouvidas a 50 m.

| Ultimate | Escola | Efeito | Mana | Recarga | Requisito |
|---|---|---|---|---|---|
| **Fúria do Campeão** | Marcial | Por 6 s: +30% de dano físico, +20% de velocidade, imune a lentidão; ataques básicos atravessam estruturas | 100 | 75 s | Força 5 |
| **Chuva de Meteoros** | Fogo | Área de 8 m: 3 meteoros de 120 após 1 s de aviso (cada alvo é atingido por no máximo 1); chão em chamas por 4 s; queima vegetação | 120 | 80 s | Intelecto 5 |
| **Domo Glacial** ◆ | Gelo | Domo de gelo de 8 m (paredes com 600 de vida) por 6 s. Isola uma luta ou protege você de terceiros | 110 | 85 s | Intelecto 4 |
| **Fortaleza de Pedra** ◆ | Terra | Ergue um anel de 4 muralhas e um pilar central com você em cima (raio de 6 m) por 10 s; quem estiver na borda sofre 150 e é lançado | 110 | 85 s | Vitalidade 5 |
| **Olho do Furacão** ◆ | Tempestade | Você levita 6 m por 5 s e dispara raios em até 3 inimigos a 20 m (70/s cada); o vento empurra quem chega a menos de 4 m | 120 | 80 s | Agilidade 5 |
| **Eclipse** ◆ | Sombra | Escuridão de 25 m por 6 s: inimigos dentro perdem o minimapa e a mira assistida e enxergam só 8 m; você ganha +20% de velocidade | 110 | 85 s | Agilidade 4 |
| **Aurora** | Luz | Por 8 s, cura 40/s. Se você fosse morrer, é curado em 40% e o efeito acaba (1 vez) | 100 | 90 s | Espírito 5 |

**Combinações naturais (arquétipo → principal + ultimate):**

- **Guerreiro:** Arremetida + Fúria do Campeão, ou Fissura + Fortaleza de Pedra.
- **Patrulheiro:** Tiro Rasante + Olho do Furacão, ou Rajada + Eclipse.
- **Feiticeiro:** Bola de Fogo + Chuva de Meteoros, ou Muralha de Gelo + Domo Glacial.
- **Místico:** Sifão + Aurora, ou Névoa Sombria + Eclipse.

### 6.5 Terreno reativo: interações elementais

As magias reagem ao terreno e umas às outras. É aqui que o campo de batalha muda a cada
luta.

| Combinação | Resultado |
|---|---|
| **Fogo + vegetação** (arbustos, grama alta) | Queima por 4 s (20/s em quem está dentro); a vegetação some por 60 s e remove esconderijos |
| **Fogo + gelo** (muralha, domo, plataforma) | Derrete: a estrutura perde 50% da vida por segundo e deixa uma poça |
| **Gelo + água** (rio, lago, poça) | Congela um raio de 4 m por 8 s, criando uma plataforma andável |
| **Raio + Molhado** | +50% de dano e atordoamento de 0,5 s; o raio salta para outro alvo Molhado a até 5 m |
| **Vento + zona** (fogo, Névoa Sombria) | A zona é empurrada 6 m na direção da Rajada |
| **Luz + Sombra** | Farol e Aurora dissipam Névoa Sombria e Eclipse no seu raio |
| **Marcial + estrutura mágica** | Arremetida, Tiro Rasante e Fúria do Campeão destroem estruturas mágicas |

**Estado "Molhado":** vale enquanto você está na água ou numa poça e por 4 s depois de
sair. Você recebe 30% menos dano de fogo e 50% mais de raio.

---

## 7. Níveis, XP e mutações

### 7.1 Curva de nível

| Nível | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| XP para chegar (a partir do anterior) | 100 | 150 | 200 | 260 | 330 | 410 | 500 | 600 | 720 |
| XP acumulado | 100 | 250 | 450 | 710 | 1.040 | 1.450 | 1.950 | 2.550 | 3.270 |

- **Cada nível:** +80 de vida, +20 de mana, +6% de dano (aditivo) e **1 mutação**.
- **Nível 6:** libera a ultimate.

### 7.2 Fontes de XP

| Fonte | XP |
|---|---|
| Creep pequeno (Imp) | 30 |
| Creep médio (Puglin) | 120 |
| Elite (Puglin Ancião) | 400 |
| Abate de jogador | 80 × nível da vítima (mínimo 100) e +20% por nível que a vítima tiver acima de você |

XP vem **apenas** de creeps e jogadores. O XP fica com quem dá o golpe final.

### 7.3 Anti-bola-de-neve

- **Recompensa por abate:** matar alguém forte rende muito XP (abate de jogador, em 7.2).
- **Recuperação:** quem está abaixo do nível médio dos vivos ganha +30% de XP de creeps.
  Quem está 2 ou mais níveis acima da média ganha −20%.
- **Piso de nível:** ao fim de cada fase da tempestade, quem estiver abaixo do piso sobe
  até ele. O piso garante que todos têm a ultimate nos 8–10 finais.

| Fim da fase | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Piso de nível | 2 | 3 | 4 | 6 | 7 |

- **Teto baixo:** o nível máximo é 10, e o ganho por nível é pequeno.

### 7.4 Mutações

A cada nível (do 2 ao 10, 9 escolhas no total) aparecem **3 mutações**. O jogador escolhe 1
com Alt+1/2/3 ou deixa para depois, sem limite de tempo. Há **1 troca de opções** por
partida.

| Categoria | Exemplos |
|---|---|
| **Atributo** | +2 pontos efetivos em Força / Agilidade / Vitalidade / Intelecto / Espírito |
| **Magia** (só para magias equipadas) | *Arremetida:* 2 cargas · *Bola de Fogo:* deixa chão em chamas por 3 s · *Muralha de Gelo:* +50% de largura · *Pilar de Pedra:* 2 pilares · *Rajada:* também cura 60 · *Névoa Sombria:* você fica invisível dentro dela · *Farol:* dura 14 s |
| **Ultimate** (oferecida nos níveis 8 e 10) | −20% de recarga da ultimate · +30% de área da ultimate · a ultimate devolve 50% da mana gasta |
| **Geral** | +8% de velocidade fora de combate · esquiva com 2 cargas · +15% de cura de consumíveis · +1 slot de consumível · abates revelam o inimigo mais próximo por 5 s |

As mutações oferecidas têm peso para combinar com a sua build (escolas e atributos que
você usa), sem excluir as outras.

---

## 8. Itens

### 8.1 Equipamento

| Item | Detalhe |
|---|---|
| **Slots** | 4: **Armadura, Cabeça, Anel, Amuleto**. Um item por slot; pegar outro troca, e o antigo cai no chão |
| **Comparação** | Ao mirar um item, setas verdes e vermelhas mostram o ganho em relação ao equipado |
| **Raridade** | Os números da tabela são do nível **Comum**; as outras raridades multiplicam |

| Raridade | Cor | Multiplicador |
|---|---|---|
| Comum | Cinza | 1,0× |
| Incomum | Verde | 1,25× |
| Raro | Azul | 1,5× |
| Épico | Roxo | 1,8× |
| Lendário | Dourado | 2,0× + efeito único |

| Slot | Item | Atributos (Comum) | Malha (Ultimate RPG) |
|---|---|---|---|
| Armadura | Couraça de Couro | +60 vida, +4% velocidade | `Armor_Leather` |
| Armadura | Cota de Placas | +100 vida, +4 armadura | `Armor_Metal` |
| Armadura | Manto Rúnico | +60 vida, +50 mana | `Armor_Black` |
| Cabeça | Elmo de Ferro | +50 vida, +3 armadura | `Crown2` (provisório) |
| Cabeça | Diadema Arcano | +40 mana, +5% poder mágico | `Crown` |
| Cabeça | Capuz do Rastreador | +5% velocidade de ataque, +3% velocidade | `Glove` (provisório) |
| Anel | Anel da Força | +6% dano físico | `Ring1` |
| Anel | Anel do Foco | +6% poder mágico | `Ring2` |
| Anel | Anel do Vento | +5% velocidade | `Ring3` |
| Anel | Anel da Fonte | +0,6 mana/s | `Ring4` |
| Amuleto | Amuleto do Tempo | −6% recarga de magias | `Necklace1` |
| Amuleto | Amuleto Vital | +100 vida | `Heart` |
| Amuleto | Amuleto do Duelista | +1% dano físico **por ponto de Força** | `Necklace2` |
| Amuleto | Amuleto do Erudito | +1% poder mágico **por ponto de Intelecto** | `Necklace3` |
| Amuleto | Amuleto do Eremita | −0,6% recarga **por ponto de Espírito** | `Necklace1` (cor) |

Os amuletos "por ponto" fazem a build da pré-partida conversar com o loot.

**Lendários.** Só aparecem em elites, baús dourados e drops aéreos:

| Lendário | Slot | Efeito único |
|---|---|---|
| Couraça da Fênix | Armadura | 1× por partida: ao morrer, revive com 30% de vida e explode (150 de dano, 5 m) |
| Coroa do Arquimago | Cabeça | Abates zeram a recarga das magias comuns |
| Anel do Andarilho Celeste | Anel | A esquiva ganha 2 cargas e pode ser usada no ar |
| Amuleto Elemental | Amuleto | Suas magias de campo ◆ duram 50% mais |

### 8.2 Grimórios

| Item | Detalhe |
|---|---|
| **Malha** | `Book1_Closed`–`Book4_Closed` do Ultimate RPG, com brilho na cor da escola |
| **Raridade** | Comum = rank 1, Raro = rank 2, Épico = rank 3 |
| **Mesma magia** | Pegar um grimório de uma magia que você já tem sobe o rank dela, inclusive da principal |

### 8.3 Consumíveis

| Item | Detalhe |
|---|---|
| **Slots** | 3, nas teclas 1–3 |
| **Uso** | Dá para andar a 50% da velocidade; levar dano não interrompe |

| Consumível | Efeito | Pilha | Malha |
|---|---|---|---|
| Comida leve | +60 de vida em 2 s | 6 | Ultimate Food: `Apple`, `Bread`, `Banana` |
| Refeição | +200 de vida em 5 s | 3 | `Burger`, `Pizza`, `CookingPot_Soup` |
| Poção de Mana | +120 de mana em 1 s | 3 | Ultimate RPG: `Potion5_Filled` (líquido ciano) |
| Poção de Pressa | +25% de velocidade por 6 s | 2 | `Potion9_Filled` (líquido verde) |

### 8.4 Baús e drops

| Fonte | Quantidade | Conteúdo |
|---|---|---|
| Baú comum | ~50, nos POIs | 1 item (Comum–Raro), 1 consumível, 40% de chance de grimório (Comum–Raro) |
| Baú dourado | ~6, em locais expostos | 1 item (Raro–Épico, 5% Lendário), 1 grimório (Raro–Épico) |
| Drop aéreo | 1 no início das fases 3 e 5, anunciado no mapa | 1 Lendário garantido + 1 grimório Épico |
| Morte de jogador | — | Solta todos os itens, grimórios (E/R) e consumíveis |

O conteúdo é rolado **no momento em que o baú é aberto**, aplicando a afinidade de quem
abriu.

---

## 9. Combate

- **TTK alvo:** 4–6 s entre dois jogadores do **mesmo nível** usando o kit completo. Nunca
  menos de 2 s nem mais de 12 s. Conferido em [Simulacao_TTK.xlsx](Simulacao_TTK.xlsx)
  (15/10): com os números atuais, 45 dos 48 confrontos de teste ficam entre 2 e 12 s. Os 3 de
  fora são Místico resistente contra tanque, com 12,1–12,6 s.
- **Armadura** reduz todo o dano: `redução = 0,04·A / (1 + 0,04·A)`. Com 10 de armadura,
  a redução é de 28,6%. A armadura vem só de itens.
- **Bônus de dano somam**, mesmo de categorias diferentes (nível, item, atributo): +24% do
  nível 5, +25% de Força e +6% do Anel da Força dão +55%. Efeitos temporários, como a Fúria
  do Campeão, multiplicam por cima.
- **Controle** (atordoar, enraizar, lançar) dura no máximo 1,5 s. Depois de sofrer controle,
  os próximos controles por 2 s duram metade.
- **Telegrafia:** toda magia com 100 de dano ou mais tem projétil visível ou indicador no
  chão por pelo menos 0,3 s. As ultimates têm 0,5–1 s.

---

## 10. Legibilidade

| Ferramenta | Como funciona |
|---|---|
| **Silhueta do arquétipo** | Arma na mão + outfit. Cosméticos não podem esconder isso |
| **Cor da escola** | Todo efeito de magia usa a cor da escola (6.1). Cosméticos não mudam essas cores |
| **Barras acima do inimigo** | Vida, mana e nível visíveis a até 40 m |
| **Inspeção** | Mirar no inimigo por 0,5 s mostra arquétipo, nível, ícones das magias e se a ultimate está pronta |
| **Tela de morte** | Build completa de quem matou você (arquétipo, atributos, magias, itens) e o dano recebido por fonte |
| **Áudio** | Cada escola tem um som de conjuração próprio; ultimates são ouvidas a 50 m |
| **Direção de arte** | Cartoon + aquarela (decisão de 15/10). Só o cenário recebe o filtro de aquarela. Personagens, magias e telegrafias ficam de fora (Custom Depth/Stencil) e mantêm o contorno nítido. Detalhes em [Mapa.md](Mapa.md) |

---

## 11. Mapa

- **Ilha v2** (aprovada em 15/10; os detalhes estão em [Mapa.md](Mapa.md)):
  - cerca de 1 km de ponta a ponta, 0,80 km² de terra, num Landscape de 1,26 km;
  - feita no estilo do Fortnite, com cerca de 25% do tamanho dele, porque são 20 jogadores;
  - 9 POIs: Distrito Arcano (cidade), Vila Carvalho, Porto Sereno, Fazenda Girassol, Forte Corvo,
    Pico do Trovão (91 m), Lago Espelho, Selva Rubra e Ruínas Rúnicas;
  - o Rio Prata, a Lagoa Verde e os 21 acampamentos da seção 12;
  - **interface:** minimapa no HUD, mapa em tela cheia (M) e mapa da queda.
  - O layout fica em `Unreal/Data/Mapa/mapa_v2.json` e é gerado por `Unreal/mapa_gerar.py`.
- **Cobertura:** sem construção, ela vem dos prédios dos POIs, do relevo, da vegetação
  (destrutível com fogo) e das magias de campo.
- **Requisitos de terreno para as interações (6.5):**
  - pelo menos um **rio** e dois **lagos**, para Gelo e raio;
  - áreas de **grama alta e arbustos**, para Fogo e esconderijos;
  - **elevações naturais** espaçadas, para a briga por altura.
- **Densidade:** 20 jogadores em 0,80 km² dá cerca de 200 × 200 m por jogador no início. No
  Fortnite são cerca de 230 × 230 m.

---

## 12. Creeps da jungle

Monstros do pacote Bestiary.

| Acampamento | Quantidade | Composição | Vida | XP | Drop | Reaparece |
|---|---|---|---|---|---|---|
| Pequeno | 12 | 3 Imps | 150 cada | 30 cada | 50%: comida ou poção | 90 s |
| Médio | 6 | 1 Puglin + 2 Imps | 700 / 150 | 120 + 30 × 2 | Grimório garantido (Comum–Raro) | 150 s |
| Elite | 3 | Puglin Ancião (Puglin em escala 1,6×, material próprio, ataques em área) | 2.500 | 400 | 50% Lendário, senão Épico | Não reaparece; acorda no fim da fase 1 |

**Regras:**

- **Golpe final:** XP e drop ficam com quem der o último golpe. Isso permite roubar o creep
  do outro e incentiva emboscadas.
- **Corrente:** o creep volta ao acampamento e regenera se o alvo se afastar 15 m.
- **Barulho:** após 2 s de luta contra creep, um ícone de espadas aparece no minimapa de
  todos.
- **Custo real:** um acampamento pequeno no nível 1 deve custar cerca de 25% da vida. Farmar
  nunca é de graça.

---

## 13. Tempestade

| Fase | Espera | Fechamento | Dano/s (da vida máxima) | Ao fim |
|---|---|---|---|---|
| 1 | 0:00–3:00 | 3:00–4:00 | 1% | Piso nível 2; elites acordam |
| 2 | 4:00–5:30 | 5:30–6:30 | 2% | Piso nível 3 |
| 3 | 6:30–7:30 | 7:30–8:30 | 3% | Piso nível 4; drop aéreo no início |
| 4 | 8:30–9:30 | 9:30–10:30 | 5% | Piso nível 6 |
| 5 | 10:30–11:15 | 11:15–12:15 | 8% | Piso nível 7; drop aéreo no início |
| 6 | 12:15–12:45 | 12:45–14:00 | 10% | Fecha totalmente |

O dano é **percentual** porque a vida varia de ~400 a ~1.800 entre builds e níveis.

---

## 14. Controles (PC)

| Ação | Tecla |
|---|---|
| Mover / pular / agachar | WASD / Espaço / Ctrl |
| Esquiva | Shift |
| Ataque básico | Botão esquerdo (segurar carrega, no Patrulheiro) |
| Magia principal / Magia 2 / Magia 3 | Q / E / R (sem efeito se o slot for passivo) |
| Ultimate | X |
| Interagir (baú, item, grimório) | F |
| Consumíveis | 1 / 2 / 3 |
| Escolher mutação | Alt + 1 / 2 / 3, ou clique com o painel aberto |
| Painel de build / mapa | Tab / M |
| Saltar do dirigível / planar | Espaço |

---

## 15. Escopo e roadmap

| Etapa | Entrega |
|---|---|
| **1. Núcleo** | GAS com atributos, vida e mana; Feiticeiro; Bola de Fogo, Muralha de Gelo e Chuva de Meteoros; acampamento de Imps; baú comum; tempestade; XP e nível |
| **2. Montagem** | 4 arquétipos; editor de build e builds salvas; escolas Marcial, Fogo, Gelo e Terra (8 magias + 4 ultimates); grimórios; mutações; itens Comum–Épico; interações Fogo + vegetação e Gelo + água |
| **3. Partida completa** | 7 escolas (14 magias + 7 ultimates); lendários; drops aéreos; elites; todas as interações; legibilidade (inspeção, tela de morte); 20 jogadores em servidor dedicado |
| **4. Depois** | Bots para completar lobbies; progressão de conta (cosméticos); outros modos |

---

## 16. Arquitetura na Unreal

O sistema inteiro (atributos, custo de mana, recargas, itens que modificam atributos,
efeitos temporários e replicação) é o caso de uso do **Gameplay Ability System (GAS)**.

> O projeto hoje é só Blueprint. O `AttributeSet` do GAS é escrito em C++, então é preciso
> adicionar uma classe C++ ao projeto (Visual Studio com o workload de C++ para jogos). O
> resto pode ficar em Blueprint.

| Peça | Função |
|---|---|
| `AS_Hero` (C++) | Atributos: Vida, VidaMax, Mana, ManaMax, RegenMana, Força, Agilidade, Vitalidade, Intelecto, Espírito, DanoFisico, PoderMagico, Armadura, VelocMov, VelocAtaque, ReducaoRecarga |
| `PS_Hero` | PlayerState com o AbilitySystemComponent, nível, XP, mutações e build |
| `BP_HeroBase` | Character: corpo Quaternius + outfit + cabelo (esqueleto UAL, `ABP_Hero`), esquiva, slots de magia |
| `GA_*` | Uma Gameplay Ability por magia, ataque básico e esquiva; custo = `GE_Cost_*`, recarga = `GE_Cooldown_*` |
| `GE_*` | Itens (duração infinita), consumíveis, mutações, tempestade, atributos da build |
| Gameplay Tags | `Magic.School.Fire`, `Magic.Field`, `State.Wet`, `State.InCombat`, `State.Stunned`… |
| `DA_Archetype`, `DA_Spell`, `DA_Item`, `DA_Mutation` | Data Assets com o conteúdo |
| `DT_XP`, `DT_Storm`, `DT_Loot`, `DT_Creeps` | Tabelas de balanceamento (números deste documento) |
| `BPC_ElementalReactor` | Componente que resolve as interações da seção 6.5 em vegetação, água e estruturas |
| `BP_SpellStructure_*` | Muralha, pilar, domo e farol: vida, duração e tags |
| `GM_NexusRoyale` / `GS_NexusRoyale` | Fases da partida, piso de nível, vitória |
| `BP_StormController` | Fases, encolhimento e dano percentual |
| `BP_LootChest`, `BP_Pickup_Item`, `BP_Pickup_Grimoire`, `BP_Pickup_Consumable`, `BP_AirDrop` | Loot |
| `BP_CreepCamp`, `BP_Creep_Imp`, `BP_Creep_Puglin`, `BP_Creep_PuglinElder` | PvE com IA simples (StateTree) |
| `BP_DropShip` | Entrada na ilha |
| `WBP_HUD`, `WBP_BuildEditor`, `WBP_MutationPick`, `WBP_Inspect`, `WBP_DeathRecap` | Interface |
| `SG_Builds` | SaveGame com as 5 builds salvas |

### 16.1 Migração do que existe no projeto

**Reaproveitar:**

| Asset | Uso |
|---|---|
| `BP_Creep`, `BP_Creep_Imp`, `BP_Creep_Puglin` | Creeps |
| `SM_Island`, POIs, árvores, pedras, arbustos | Mapa |
| `SM_Chest` | Baú |
| `SM_DropShip` | Dirigível |
| `SM_StormWall` / `M_Storm` | Tempestade |
| `SM_Potion_Health` | Consumível |
| Montagem Quaternius dos heróis (`ABP_Hero`, `M_HeroHead`, outfits) | Vira a base do `BP_HeroBase` |

**Remover (vieram da v1):**

| Categoria | Assets |
|---|---|
| Heróis | `BP_Hero_Brakka/Lumi/Vela/Zephyr`, `MI_Suit_*`, `SK_Guardian` |
| Construção | `SM_Build_*`, `M_Build_*` |
| Torres e Nexus | `SM_CaptureTower`, `M_Tower_Glow`, `SM_Nexus`, `M_Nexus_Glow` |
| Pickups e mobilidade | `SM_EssenceShard`, `M_Essence_Glow`, `SM_Potion_Shield`, `M_Potion_Shield`, `SM_LaunchPad`, `M_Pad_*`, `M_Banner_Team` |

**Atualizar:**

- `Export/map_layout.json` e `Unreal/import_nexus_assets.py` ainda posicionam torres, Nexus
  e fragmentos.
- `Blender/scripts/build_all.py` ainda gera os heróis e peças de construção antigos.

---

## 17. Riscos e pontos em aberto

| Risco | Ação |
|---|---|
| TTK fora do alvo com nível, itens e atributos combinados | Planilha de simulação feita ([Simulacao_TTK.xlsx](Simulacao_TTK.xlsx)); refazer a conta a cada mudança de números; tabelas de dados para ajustar sem mexer em Blueprint |
| Poucos modelos: a versão Standard do Bestiary tem só Imp e Puglin, e a de outfits só Peasant e Ranger | Arma na mão e cor definem o arquétipo; Puglin Ancião como elite provisório; avaliar mais pacotes |
| Rede: 20 jogadores + ~50 creeps + estruturas e zonas replicadas | IA simples, creeps dormindo longe de jogadores, poucas estruturas simultâneas por jogador |
| Lobbies vazios num jogo pequeno | Bots (etapa 4) |
| Complexidade para iniciantes | Builds prontas sugeridas para cada arquétipo; tutorial contra creeps |

**Referências para estudar:**

| Jogo | O que estudar |
|---|---|
| Spellbreak | BR de magias com interações elementais |
| Supervive | BR com creeps e níveis |
| Battlerite Royale | Kits de MOBA em BR |
| Realm Royale | Classes e forja de habilidades |
| Dota 2 | Atributos e itens |
| Hades | Escolhas a cada nível |
