# Design do mapa

---

## 1. Mapas que existem

| Mapa | O que é | Estado |
|---|---|---|
| `L_Island` | Ilha de teste de 400 × 400 m: natureza Quaternius, Vila e Cidade, 32 baús, 6 acampamentos | **Mapa padrão** do jogo e do editor; limpo da v1 em 15/10 |
| `L_Ilha` | Ilha v2 de ~1 km ([Design/Mapa.md](../../Design/Mapa.md)): sol, céu, névoa, PlayerStart | **Sem Landscape:** espera o usuário importar o relevo à mão (a API Python da 5.8 não cria Landscape) |
| `Lvl_ThirdPerson` | Mapa do template | Sem uso |

Nenhum é World Partition. 1 km cabe inteiro na memória; World Partition só se o mapa crescer (D-006).

## 2. Ilha v2 (alvo)

Fonte da verdade: `Unreal/Data/Mapa/mapa_v2.json` (gerador `Unreal/mapa_gerar.py`). 1.006 × 1.051 m, 0,80 km² de
terra, pico de 91 m, 9 POIs, rio, 2 lagos, 21 acampamentos (12 pequenos, 6 médios, 3 elites).

**Distâncias medidas no layout** (em linha reta; corrida a 6 m/s):

| POI | Vizinho mais perto | Distância | Corrida |
|---|---|---|---|
| Distrito Arcano | Fazenda Girassol | 226 m | 38 s |
| Vila Carvalho | Fazenda Girassol | 220 m | 37 s |
| Porto Sereno | Selva Rubra | 380 m | 63 s |
| Fazenda Girassol | Vila Carvalho | 220 m | 37 s |
| Forte Corvo | Distrito Arcano | 271 m | 45 s |
| Pico do Trovão | Lago Espelho | 380 m | 63 s |
| Lago Espelho | Distrito Arcano | 271 m | 45 s |
| Selva Rubra | Ruínas Rúnicas | 313 m | 52 s |
| Ruínas Rúnicas | Lago Espelho | 310 m | 52 s |

Média entre todos os POIs: 517 m; a maior: 833 m (139 s de corrida). **Leitura:** entre um POI e o próximo há 40–60 s
de travessia, que precisa de pontos de decisão no meio (acampamento, baú solto, cobertura, altura). O lado leste (Porto,
Selva, Ruínas, Pico) é mais espalhado que o oeste.

## 3. Graybox antes da arte (M17)

1. Importar o Landscape do `L_Ilha` (usuário) **ou** decidir fazer o graybox sobre um plano com o relevo em blocos.
2. Pôr blocos cinza nos POIs (prédios com altura e portas), cobertura, rotas e acampamentos.
3. Jogar com bots e medir (abaixo). Ajustar o layout no `mapa_v2.json` e regerar.
4. Só depois trocar os blocos pelos kits Quaternius e pela arte pintada.

## 4. O que medir (metas iniciais, hipóteses)

| Métrica | Como medir | Meta |
|---|---|---|
| Tempo até o primeiro encontro | telemetria: primeira vez que dois jogadores se veem/causam dano | 60–120 s depois de pousar |
| Encontros por minuto (partida) | telemetria | 1–3 no início; crescendo |
| Travessia entre POIs vizinhos | distância / 6 m/s | 30–60 s, com pelo menos 1 decisão no meio |
| Rotação com a zona | tempo de corrida da borda ao novo círculo | ≤ 70% do tempo de espera da fase |
| Linhas de visão longas | traços a partir de pontos altos | poucas > 150 m (o longo alcance não pode dominar) |
| Cobertura | % de pontos com cobertura a menos de 15 m | > 80% nas rotas principais |
| Densidade | área de terra / jogadores | ~200 × 200 m por jogador no início (já é a do layout) |

Um script de medição a partir da telemetria e do `mapa_v2.json` entra no M17.

## 5. Elementos que todo POI precisa

Combate de perto (interiores, portas), combate de longe (praça, campo aberto), vertical (telhados, morros), rotas de
fuga, cobertura, baús, um ponto de risco alto com loot melhor, e pelo menos 2 saídas.

## 6. Zona e mapa

Os raios do `CT_Storm` são da ilha de 400 m. Para a v2, o círculo inicial precisa de ~560 m (proposta em Design/Mapa.md,
"Tempestade com o mapa novo").
