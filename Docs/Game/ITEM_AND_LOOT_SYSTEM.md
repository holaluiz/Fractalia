# Itens, armas e loot

---

## 1. Hoje

- `UNRInventoryComponent` (C++): 4 slots de equipamento (Armadura, Cabeça, Anel, Amuleto), 3 de consumível (teclas
  1-3), 2 grimórios. Equipar aplica o bônus no ASC; trocar devolve o antigo para o chão (o pickup passa a mostrar o
  item que saiu). **Nada replica.**
- `DT_Itens` (33 linhas, gerado de `Unreal/Data/DT_Itens.csv` por `gerar_dt_itens.py`): números do GDD v2 §8, raridade
  multiplica (1,0 / 1,25 / 1,5 / 1,8 / 2,0).
- `BP_LootChest.Interact`: 1 equipamento + 1 consumível + 40% de grimório, raridades do GDD v2 §8.4 (60/30/10).
- `BP_CreepCamp.DropLoot`: pequeno 50% de consumível; médio, grimório Comum–Raro.
- `BP_Pickup`: malha da tabela, luz na cor da raridade.
- **Não há armas.**

## 2. Alvo

### 2.1 Slots

| Slot | Quantos | Teclas | Replica para |
|---|---|---|---|
| Arma de perto | 1 | 1 (e roda do mouse) | todos (a arma aparece na mão) |
| Arma de longe | 1 | 2 (e roda do mouse) | todos |
| Itens | 6 | Z X C V B N (remapeáveis) | só o dono |

Armas não ocupam os 6 slots (D-002c).

### 2.2 Tipos de item

| Tipo | Usa tecla? | Exemplo (vindo do GDD v2) |
|---|---|---|
| **Passivo** | não (a tecla mostra a dica) | Couraça de Couro (+60 vida, +4% velocidade), Anel do Foco, Amuleto do Tempo |
| **Ativo** | sim; recarga ou cargas | Pergaminho de Salto (avança 6 m, 2 cargas), Lanterna de Luz (revela 15 m) — **novos, a desenhar** |
| **Consumível** | sim; pilha | Comida leve (6), Refeição (3), Poção de Mana (3), Poção de Pressa (2) |
| **Tomo** | sim; some | +1 rank numa habilidade à escolha (D-002d) |

**Regra anti-acúmulo:** passivos do mesmo item não somam (o segundo igual não faz nada e a UI avisa), para 6 slots
cheios de "Anel do Foco" não virarem a build ótima.

### 2.3 Dados

- **Itens:** continuam no `DT_Itens` (CSV), com colunas novas: `Tipo` (Passivo/Ativo/Consumivel/Tomo), `Icone`,
  `Recarga`, `Cargas`, `ClasseAtiva` (GA do efeito ativo), `Pilha`.
- **Armas:** `UNRWeaponDefinition` (Data Asset `DA_Arma_<Nome>`): slot (perto/longe), dano, cadência, alcance,
  velocidade do projétil, dispersão (parado/andando/no ar), pente, tempo de recarga, multiplicador de cabeça,
  penalidade de movimento, malha, animações, VFX, sons, ícone.
- **Raridade:** item = multiplicador do GDD v2 (1,0–2,0×); **arma = +5% de dano por nível** (menos, porque a arma é o
  dano principal; BALANCE.md §6).

### 2.4 Replicação (M2 e M9)

- Os 6 slots e as 2 armas num **Fast Array** (`FFastArraySerializer`) para replicar só o que mudou.
- Itens: `COND_OwnerOnly`. Armas: para todos (arma na mão), munição só ao dono.
- Usar, soltar, trocar: `Server_UsarItem(Slot)`, `Server_SoltarItem(Slot)`, `Server_TrocarArma(Slot)`.
- O efeito do item (bônus, cura) é aplicado pelo ASC no servidor; o cliente vê pelos atributos replicados.

## 3. Loot

### 3.1 Tabelas (`DT_Loot`, M9)

Uma linha por **fonte** × **entrada**:

| Coluna | Exemplo |
|---|---|
| Fonte | `BauComum`, `BauDourado`, `DropAereo`, `CreepPequeno`, `CreepMedio`, `Elite` |
| Grupo | `Arma`, `Passivo`, `Ativo`, `Consumivel`, `Tomo` |
| Peso | 40 |
| RaridadeMin / RaridadeMax | Comum / Raro |
| Quantidade | 1 |
| Chance | 1,0 (sempre) ou 0,4 (40%) |

O baú lê as linhas da fonte dele e sorteia **no servidor** quando abre. Nada de loot escrito dentro do Blueprint.

### 3.2 Baú comum (proposta inicial)

1 arma (60%) **ou** 1 passivo/ativo (40%), mais 1 consumível, mais 15% de Tomo. Raridade 60/30/10 (Comum/Incomum/Raro).
Números em BALANCE.md §6.

### 3.3 Onde está o loot bom

Centro do mapa, POIs expostos, acampamentos médios e elites, baús dourados (~6), drops aéreos (fases 3 e 5).
A sorte gera adaptação; quem quer loot melhor aceita mais risco.

## 4. No chão (D-009)

| Situação | Representação |
|---|---|
| Baú fechado | ator dormente (não gasta rede) |
| Baú aberto | até 3 `BP_Pickup` (um por item), como hoje |
| Morte de jogador | **1 `ANRBolsaDeLoot`** com a lista replicada (6 itens + 2 armas); abrir mostra a lista, F pega um, Shift+F pega tudo que couber |
| Tempestade fechou em cima | pickups e bolsas somem |
| Item trocado | o antigo vira pickup no chão (como hoje) |

## 5. Morte

O servidor tira tudo do inventário e das armas do morto, cria a bolsa no lugar e grava na telemetria. Os outros veem a
bolsa; só quem chega perto vê o conteúdo.
