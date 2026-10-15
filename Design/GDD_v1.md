# NEXUS ROYALE — Documento de Design

> Battle royale estilo Fortnite (construção, tempestade, saque, visual cartoon)
> com heróis de kit fixo e progressão de nível dentro da partida, como num MOBA.

## 1. Pitch

Até 40 jogadores saltam de um dirigível sobre uma ilha. Cada um escolhe um **herói**
antes da partida, com passiva, 3 habilidades (Q / E / R) e um ataque básico próprio.
Não existem armas no chão: o poder vem do **nível do herói** (1 a 10), das
**Relíquias** encontradas em baús e da **construção** para se proteger e ganhar altura.
A tempestade fecha o mapa e o último jogador (ou squad) de pé vence.

## 2. Loop principal

1. **Seleção de herói** (30 s) — 4 heróis, papéis distintos.
2. **Queda** — saltar do dirigível, planar até o ponto escolhido.
3. **Coleta** — quebrar árvores/pedras (materiais), abrir baús (Relíquias, poções),
   pegar **Fragmentos de Essência** (XP).
4. **Subir de nível** — XP vem de abates, fragmentos, torres capturadas e do Guardião.
   Cada nível dá +vida/+dano e um ponto para evoluir Q, E ou R (R só a partir do nível 6).
5. **Objetivos** — 4 **Torres de Captura** (N/L/S/O) dão XP contínuo ao dono;
   o **Guardião** no Nexus central (aparece aos 8 min) dá o buff "Bênção do Nexus".
6. **Tempestade** — 6 fases, encolhendo em direção a um ponto aleatório.

## 3. Elementos de MOBA

| Sistema | Regra |
|---|---|
| Níveis | 1–10. XP por nível: 100, 150, 200, 260, 330, 410, 500, 600, 720 |
| Pontos de habilidade | 1 por nível; Q/E até rank 4, R até rank 3 (níveis 6, 8, 10) |
| Recargas | Sem mana; cada habilidade tem cooldown que cai com o rank |
| Relíquias (itens) | Até 3 slots. Ex.: *Botas do Vento* (+12% velocidade), *Coração de Pedra* (+150 vida), *Lâmina Rúnica* (+15% dano), *Ampulheta* (-15% cooldowns) |
| Campos neutros | Golens menores perto das torres; dão XP e um baú |
| Guardião | Chefe neutro no Nexus. Quem der o golpe final ganha "Bênção do Nexus" (+20% dano, regeneração) por 90 s |

## 4. Elementos de Fortnite

- **Construção**: parede, piso, rampa e cone em grade de 5,12 m × 5,12 m (altura 3,84 m).
  Custa 10 de material; peças têm 150 de vida (sobem para 300 em 5 s).
- **Coleta**: ataque de coleta (tecla F) em árvores e pedras gera material.
- **Tempestade**: dano por segundo crescente por fase (1, 2, 5, 8, 10, 10).
- **Dirigível** (equivalente ao ônibus), **plataformas de lançamento** e **baús**.

## 5. Heróis

### Brakka — Tanque (Vanguarda)
Armadura azul e aço, escudo no braço esquerdo, martelo de guerra.
- **Passiva – Muralha Viva**: 15% de redução de dano vindo da frente.
- **Ataque básico**: golpe de martelo em cone curto (45 de dano).
- **Q – Investida de Escudo**: avança 8 m, atordoa 0,75 s o primeiro inimigo. CD 10 s.
- **E – Baluarte**: cria uma parede de energia de 5,12 m (bloqueia projéteis) por 4 s. CD 14 s.
- **R – Tremor**: salta e golpeia o chão, 300 de dano e lentidão de 40% num raio de 7 m. CD 70 s.

### Vela — Atiradora (Caçadora)
Capuz verde, capa, arco longo.
- **Passiva – Olho de Falcão**: tiros a mais de 30 m causam +20% de dano.
- **Ataque básico**: flecha com carga (segurar = mais dano, até 90).
- **Q – Flecha Perfurante**: atravessa inimigos e construções, 120 de dano. CD 8 s.
- **E – Rolamento**: esquiva rápida de 6 m, recarrega o próximo tiro. CD 7 s.
- **R – Chuva de Flechas**: área de 8 m que causa 60 de dano/s por 4 s. CD 60 s.

### Zephyr — Mago (Arcano)
Manto roxo, chapéu pontudo, olhos brilhantes, cajado de cristal.
- **Passiva – Sobrecarga**: a cada 3 habilidades, a próxima causa +50% de dano.
- **Ataque básico**: orbe arcano teleguiado (40 de dano).
- **Q – Esfera Instável**: projétil que explode em área (150 de dano, raio 3 m). CD 7 s.
- **E – Piscar**: teleporte de 10 m na direção da mira. CD 12 s.
- **R – Tornado Arcano**: tornado que puxa inimigos e destrói construções, 5 s. CD 80 s.

### Lumi — Suporte (Curandeira)
Branca e dourada, auréola, asinhas, lanterna de luz.
- **Passiva – Luz Gentil**: aliados próximos regeneram 4 de vida/s fora de combate.
- **Ataque básico**: raio de luz (30 de dano; cura aliados em 20).
- **Q – Pulso Restaurador**: cura 120 em área de 6 m. CD 12 s.
- **E – Égide**: escudo de 150 num aliado (ou em si mesma) por 4 s. CD 14 s.
- **R – Santuário**: zona de 8 m por 6 s; aliados dentro não podem cair abaixo de 1 de vida. CD 90 s.

### Boto Encantado Corsário — Assassino (Encantador)
Corsário de rosa e branco com chapéu de plumas (modelo em `Personagens/`).
- **Passiva – Encanto das Águas**: ao sair da água ganha +25% de velocidade e fica invisível por 2 s.
- **Ataque básico**: estocada de sabre (50 de dano).
- **Q – Estocada da Maré**: avança 7 m atravessando inimigos, 90 de dano. CD 8 s.
- **E – Olhar Encantado**: encanta o alvo, que caminha até o Boto por 1,25 s. CD 14 s.
- **R – Forma de Boto**: vira boto-cor-de-rosa e mergulha no chão/água por 4 s (inalvejável); ao emergir arremessa inimigos para cima (220 de dano). CD 75 s.

### Cara Caramelo — Lutador (Duelista urbano)
Jaqueta preta, calça cargo e tênis (modelo em `Personagens/`).
- **Passiva – Vira-lata**: abaixo de 30% de vida ganha 25% de roubo de vida e regenera 5/s.
- **Ataque básico**: combo de socos (3 golpes, 35 cada).
- **Q – Rolê**: dash de 6 m; o próximo soco atordoa 0,5 s. CD 9 s.
- **E – Faro**: invoca um cachorro caramelo que persegue o inimigo mais próximo por 5 s, revelando e mordendo (60/s). CD 16 s.
- **R – Matilha**: cinco caramelos avançam em linha, 250 de dano e empurrão. CD 70 s.

### Pomba Gira Carmesim — Maga (Controle)
Vestido vermelho e dourado com fitas e cabelo volumoso (modelo em `Personagens/`).
- **Passiva – Gira**: cada habilidade dá 1 acúmulo; com 3 ela gira e ganha +30% de velocidade por 2 s.
- **Ataque básico**: pétalas de rosa teleguiadas (45 de dano).
- **Q – Rosa Carmesim**: rosa com espinhos que enraíza 1 s, 130 de dano. CD 9 s.
- **E – Leque de Fogo**: cone de fogo, 110 de dano + queimadura. CD 11 s.
- **R – Roda de Fogo**: dança que cria um anel de fogo de 9 m por 5 s; quem atravessa sofre 200 de dano e 50% de lentidão. CD 85 s.

### Guardião do Nexus — chefe neutro
Golem de pedra com núcleo de lava. 5.000 de vida, ataques em área, fica no Nexus.

## 6. Controles (PC)

| Ação | Tecla |
|---|---|
| Mover / pular / agachar | WASD / Espaço / Ctrl |
| Ataque básico | Botão esquerdo |
| Habilidades | Q / E / R |
| Evoluir habilidade | Ctrl + Q/E/R |
| Modo construção | G; peças em F1–F4 (parede, piso, rampa, cone) |
| Coletar | F |
| Usar item | 1–3 |

## 7. Arquitetura na Unreal (Blueprints, via MCP)

| Asset | Função |
|---|---|
| `GM_NexusRoyale` / `GS_NexusRoyale` | Fases da partida, tempestade, condição de vitória |
| `PS_Hero` | Nível, XP, pontos de habilidade, relíquias |
| `BP_HeroBase` (Character) | Movimento, vida/escudo, ataque básico, slots Q/E/R |
| `BP_Hero_Brakka/Vela/Zephyr/Lumi` | Filhos de `BP_HeroBase` com malha, stats e habilidades |
| `BPC_AbilitySystem` | Cooldowns, ranks, execução das habilidades |
| `BPC_BuildSystem` | Grade de 512 × 512 × 384 uu, pré-visualização, custo e vida das peças |
| `BP_BuildPiece` | Peça construída (vida, animação de construção) |
| `BP_StormController` | Fases, encolhimento e dano da tempestade |
| `BP_CapturePoint` / `BP_Guardian` / `BP_NeutralCamp` | Objetivos de MOBA |
| `BP_LootChest`, `BP_Pickup_*` | Relíquias, poções, fragmentos de XP |
| `BP_DropShip`, `BP_LaunchPad` | Entrada no mapa e mobilidade |
| `WBP_HUD`, `WBP_HeroSelect` | Interface (vida, escudo, nível, CDs, materiais, tempestade) |

Animações: os esqueletos dos heróis usam os mesmos nomes de ossos do manequim da
Unreal (`pelvis`, `spine_01`, `upperarm_l`…), então as animações do template Third
Person podem ser reaproveitadas com o IK Retargeter.

## 8. Assets gerados no Blender

Arquivo-fonte: `Blender/NexusRoyale_Assets.blend` · Exportados em `Export/FBX/`.
Escala: 1 unidade do Blender = 1 m = 100 uu. Frente dos personagens = -Y no Blender.

| Asset | Tipo | Pivô |
|---|---|---|
| `SK_Brakka`, `SK_Vela`, `SK_Zephyr`, `SK_Lumi`, `SK_Guardian` | Skeletal Mesh | Entre os pés |
| `SM_Build_Wall` (5,12 × 0,24 × 3,84 m) | Static + UCX | Base, centro |
| `SM_Build_Floor` (5,12 × 5,12 × 0,2 m) | Static + UCX | Centro, base |
| `SM_Build_Ramp` (sobe para -Y) | Static + UCX | Centro da base |
| `SM_Build_Cone` | Static + UCX | Centro da base |
| `SM_Chest`, `SM_Crate`, `SM_Potion_Health`, `SM_Potion_Shield`, `SM_EssenceShard` | Static | Base |
| `SM_Tree_Pine`, `SM_Tree_Round`, `SM_Rock_01/02`, `SM_Bush` | Static | Base |
| `SM_CaptureTower`, `SM_Nexus`, `SM_LaunchPad`, `SM_DropShip`, `SM_StormWall` | Static | Base |
| `SM_Island` (400 × 400 m, cores por vértice) | Static | Centro, nível do mar = 0 |

`Export/map_layout.json` traz as posições (já em coordenadas da Unreal, cm) de
torres, Nexus, baús, árvores e pedras para montar o nível automaticamente.
