# Balanceamento

Todas as fórmulas e constantes do jogo. **Quando um número mudar, mude aqui e no dado (tabela ou Data Asset), e
anote em §9.** Números marcados **(v2, em uso)** estão implementados hoje; **(aprovado, ainda não implementado)** vêm do GDD v3
(D-002, aceita em 15/10) e entram no código nos marcos indicados.

---

## 1. Onde moram os números

| Assunto | Hoje | Alvo |
|---|---|---|
| Atributos, vida, mana, XP por nível | `UNRAbilitySystemComponent` (defaults C++ editáveis no Details) | `CT_Atributos`, `CT_XP` (CSV) |
| Magias | structs no `UNRCombateComponent` (defaults do `BP_HeroBase`) | `DA_Hab_*` |
| Itens | `DT_Itens` (CSV, gerado por `gerar_dt_itens.py`) | igual, com colunas novas |
| Loot | defaults do `BP_LootChest` e do `BP_CreepCamp` | `DT_Loot` (CSV) |
| Creeps | defaults dos `BP_Creep_*` (`ue_creeps_camp.py`) | `DT_Creeps` (CSV) |
| Zona | `CT_Storm` (CSV) | igual |
| Mutações | defaults do `UNRMutacoesComponent` | igual + dados das habilidades |
| Draft | — | `DA_Draft_Padrao` |
| Armas | — | `DA_Arma_*` |
| TTK | `Design/Simulacao_TTK.xlsx` (sem armas) | refazer com armas (M8) |

## 2. Fórmulas em uso (v2)

- **Armadura:** `redução = 0,04·A / (1 + 0,04·A)`. 10 de armadura = 28,6%.
- **Pontos efetivos** (retorno decrescente): pontos 1–5 valem 1,0; 6–8 valem 0,6; 9–10 valem 0,3 (10 pontos = 7,4).
- **Por ponto efetivo:** Força +4% dano físico; Agilidade +3% vel. de ataque, +1,5% vel. de movimento; Vitalidade
  +30 vida, +0,4 vida/s; Intelecto +25 mana, +4% poder mágico; Espírito +0,5 mana/s, −2,5% recarga, +4% cura.
- **Por nível:** +80 vida, +20 mana, +6% de dano (aditivo).
- **XP acumulado para os níveis 2–10:** 100, 250, 450, 710, 1.040, 1.450, 1.950, 2.550, 3.270.
- **XP de creep:** Imp 30, Puglin 120, elite 400.
- **Mana:** 2/s em combate, 8/s fora; "em combate" = dano de/para jogador nos últimos 5 s.
- **Bônus de dano** somam entre categorias; temporários multiplicam por cima.
- **Raridade de item:** 1,0 / 1,25 / 1,5 / 1,8 / 2,0×.
- **Zona** (`CT_Storm`, ilha de 400 m): fecha em 240, 390, 510, 630, 735 e 840 s; dano 1, 2, 3, 5, 8, 10% da vida
  máxima por segundo; piso de nível 2, 3, 4, 6, 7 no fim das fases 1–5.

## 3. Draft (simulação, 15/10)

Ferramenta: [ferramentas/simular_draft.py](ferramentas/simular_draft.py) (`python -I simular_draft.py 400`).
Resultado guardado em [ferramentas/resultado_simular_draft.txt](ferramentas/resultado_simular_draft.txt).

**Modelo:** 20 jogadores, 1 ultimate + 3 básicas, pool 32 + 96 (1,6×); preferência = popularidade (lei de potência) +
gosto do jogador + ruído; tempo de decisão log-normal (mediana 4,5 s; quem passaria da janela decide no último segundo
em 80% das vezes); 10 s de prévia; 0,5 s entre escolhas; 3 s entre rodadas; latência de 120 ms para corridas.

| Formato | Média | p90 | Pegou a favorita | Posição média | Corridas | Tempo esgotado |
|---|---|---|---|---|---|---|
| A · serpente, 4 faixas de 5, janela 8 s | **2,41 min** | 2,52 | 41,2% | 3,01 | 0,53 | 2,4 |
| A' · serpente, 4 faixas, janela 6 s | 2,15 min | 2,23 | 40,4% | 3,45 | 0,74 | 4,6 |
| A5 · serpente, 5 faixas de 4, janela 8 s | 2,07 min | 2,18 | 41,4% | 3,04 | 0,78 | 2,4 |
| B · reserva simultânea, top 3, janela 12 s | **1,14 min** | 1,16 | 41,8% | 2,83 | 0 | 1,7 |
| C · serpente sequencial (1 por vez) | 7,32 min | 7,66 | 41,0% | 3,00 | 0 | 2,3 |
| Fatia vertical, A com 4 jogadores (pool 7 + 14) | 1,77 min | 1,94 | 49,1% | 1,75 | 0 | 0,5 |
| Fatia vertical, B com 4 jogadores | 1,01 min | 1,10 | 49,3% | 1,75 | 0 | 0,4 |

**Leitura:**
- O formato quase não muda a satisfação (quem escolhe antes leva a favorita em ~41% das vezes em todos); muda o tempo.
- A cabe no alvo de 2–4 min e mostra cada escolha na hora (negação e resposta ao vivo). A janela de 6 s economiza
  15 s, mas dobra os tempos esgotados.
- B é o mais rápido e sem corrida, mas só revela ao fim da rodada.
- **Corrida** (A): ~0,5 por draft; o host ganha esses empates (latência zero).
- **Falta medir com gente:** o tempo de decisão real e se o draft parece estratégico ou chato (§8).

## 4. XP e níveis (aprovado; XP de abate no código desde 15/10)

- **Teto:** nível 10 (testar 12 só se as partidas terminarem com quase todos no 10).
- **Curva:** a do v2 (§2) até o teste.
- **XP de abate de jogador** (substitui a fórmula do v2, que só subia):

  `XP = max(100, 80 × NívelVítima) × clamp(1 + 0,2 × (NívelVítima − NívelAssassino), 0,4, 2,0)`

  | Assassino → vítima | Base | Fator | XP |
  |---|---|---|---|
  | 5 → 5 | 400 | 1,0 | 400 |
  | 5 → 8 | 640 | 1,6 | 1.024 |
  | 8 → 3 | 240 | 0,4 | 96 |
  | 2 → 9 | 720 | 2,0 | 1.440 |

  Quem está na frente ganha pouco caçando os fracos; quem está atrás ganha muito derrubando o forte.
- **Bônus de recuperação do v2** (+30% de XP de creep abaixo da média): **desligado** até o teste mostrar que precisa
  (pedido: nada de bônus de recuperação arbitrário).
- **Piso de nível** do v2: fica (garante a ultimate no fim).

## 5. Atributos (aprovado, ainda não implementado: M11)

1 ponto por nível (9 até o nível 10). Retorno decrescente: pontos 1–4 valem 1,0; 5–7 valem 0,6; 8–9 valem 0,3 (9 num
atributo só = 6,4 efetivos; 3/3/3 = 9 efetivos).

| Atributo | Por ponto efetivo (inicial) |
|---|---|
| Vigor | +35 vida máxima, −3% de duração de controle sofrido (até −30%) |
| Poder | +4% dano de arma |
| Arcano | +4% dano e cura de habilidade, +20 mana máxima |
| Agilidade | +1,5% velocidade de movimento, −2,5% recarga de habilidade, +5% velocidade de recarga/troca de arma |

**Base sem arquétipo (aprovado, M11):** 500 de vida, 200 de mana, 6,0 m/s. Por nível: +80 vida, +20 mana, +4% de dano
(arma e habilidade). **Precisa da planilha de TTK nova** antes de travar (M8/M22).

## 6. Armas e loot (aprovado, ainda não implementado: M8, M9)

**Raridade de arma:** +5% de dano por nível de raridade (Comum 1,00 … Lendária 1,20).

| Arma | Dano | Cadência | Alcance | Pente / recarga | DPS teórico | Observação |
|---|---|---|---|---|---|---|
| Espada | 55 por golpe (combo de 3) | 0,5 s | 2,5 m (arco) | — | 110 | Exige estar colado; −10% de velocidade ao golpear |
| Bacamarte | 8 × 11 = 88 por tiro | 0,9 s | ótimo até 8 m | 4 / 2,2 s | 98 (rajada), 72 (sustentado) | Cone; cai rápido com a distância |
| Arco | 40–110 (carga 0–1 s) | ~1,25 s carregado | 60 m, com queda | — | 88 | Cabeça ×1,5 |
| Cajado Arcano | 30 por dardo | 0,45 s | 35 m | 18 / 1,8 s | 66 | Teleguiado leve (cone 12°): mais fácil, menos dano |

Contra 500 de vida (nível 1, sem armadura), só com arma e 100% de acerto: 4,5–7,6 s. Com habilidades, o alvo é 4–6 s
(GDD v2 §9).

**Baú comum:** 1 arma (60%) ou 1 passivo/ativo (40%) + 1 consumível + 15% de Tomo; raridade 60/30/10.

## 7. Anti-bola-de-neve: o que monitorar

Da telemetria (M14), a cada lote de partidas com bots e com gente:

| Pergunta | Sinal de problema |
|---|---|
| O maior nível aos 10 min vence quantas vezes? | > 60% |
| Diferença de nível entre o 1º e o 5º no fim | > 3 níveis |
| De onde vem o XP (creep × jogador) | > 70% de jogador (caçar compensa demais) ou < 20% (lutar não compensa) |
| Vencedor com arma Comum/Incomum | < 10% (a raridade decide demais) |
| Duração das lutas (primeiro dano → morte) | < 2 s ou > 12 s |
| Mortes pela zona | > 25% (zona punitiva ou rotação longa) |
| Duração da partida | fora de 12–20 min |

## 8. Diário de diversão (playtests)

| Data | Teste | Achado | Ação |
|---|---|---|---|
| — | — | Nenhum playtest com a nova direção ainda | — |

## 9. Mudanças de números

| Data | O quê | De → para | Por quê |
|---|---|---|---|
| 15/10 | Pacote B da planilha de TTK (GDD v2) | ver AGENTS.md, seção 3 | 45 de 48 duelos no alvo |
