# Mapa v2: a ilha de 1 km

> Proposta de 15/10, gerada a partir de dados. O layout ainda **aguarda a aprovação do usuário**.
> Quando for aprovado, a seção 11 do GDD passa a apontar para este documento.

## Resumo

| Item | Valor |
|---|---|
| Tamanho | Cerca de 1.006 m (leste–oeste) × 1.051 m (norte–sul). São 0,80 km² de terra, num Landscape de 1,26 km com mar em volta |
| Por que esse tamanho | Pedido do usuário: "25% do Fortnite, porque são menos jogadores" e "1 km com montanhas, água, cidade, vila, selva". O Fortnite tem cerca de 5,5 km² |
| Ponto mais alto | Pico do Trovão, cerca de 91 m |
| Fonte da verdade | [`Unreal/Data/Mapa/mapa_v2.json`](../Unreal/Data/Mapa/mapa_v2.json): POIs, morros, rio, lagos, estradas, regiões e acampamentos, em metros |
| Gerador | [`Unreal/mapa_gerar.py`](../Unreal/mapa_gerar.py). Rode `python -I Unreal/mapa_gerar.py` depois de mudar o JSON. Leva uns 35 s e o resultado é sempre o mesmo |
| Prévias | [`Previa_Mapa.png`](../Unreal/Data/Mapa/gerado/Previa_Mapa.png) (cartoon) e [`Previa_Mapa_Aquarela.png`](../Unreal/Data/Mapa/gerado/Previa_Mapa_Aquarela.png) |

## Pontos de interesse

| POI | Grade | Tipo | Kit | Papel |
|---|---|---|---|---|
| **Distrito Arcano** | D5 | Cidade | Downtown City | O ponto de queda mais disputado, com prédios e cobertura vertical |
| **Vila Carvalho** | C8 | Vila | Medieval Village | Casas em anel em volta de uma praça |
| **Porto Sereno** | F10 | Porto | Medieval + Fantasy Props | Foz do rio, píeres e loot de pesca |
| **Fazenda Girassol** | B6 | Fazenda | Medieval + Props | Plantações de grama alta, combustível para Fogo |
| **Forte Corvo** | C3 | Forte | Muralhas medievais | Topo de colina, briga por altura |
| **Pico do Trovão** | G2 | Montanha | Rochas Stylized Nature | Creep elite no topo, vista da ilha toda |
| **Lago Espelho** | F6 | Lago | Nature + Props | Centro do mapa, Gelo e raio |
| **Selva Rubra** | H8 | Selva | Nature + Bestiary | Mata fechada, Lagoa Verde e mais acampamentos |
| **Ruínas Rúnicas** | I5 | Ruínas | Props + Medieval | Planalto com mais grimórios |

**Terreno exigido pelo GDD (6.5):** está tudo lá.

- O rio (Rio Prata, 927 m) desce do pico, passa pelo Lago Espelho e sai no mar em Porto Sereno.
- Há dois lagos, campos de grama alta e elevações espalhadas.
- Duas pontes cruzam o rio. Elas são calculadas automaticamente onde as estradas cruzam a água.

**Creeps:** os acampamentos seguem o GDD, seção 12.

- 12 pequenos;
- 6 médios;
- 3 elite: Pico do Trovão, Selva Rubra e Ruínas Rúnicas.

O gerador confere se algum acampamento caiu na água ou numa encosta íngreme.

## O que o gerador produz (`Unreal/Data/Mapa/gerado/`)

| Arquivo | Uso na Unreal |
|---|---|
| `heightmap_1009.r16` / `.png` | Relevo do Landscape. 1009 × 1009, escala X/Y de 125 cm e Z de 100. 32768 corresponde ao nível do mar |
| `camada_<Grama, Campo, Floresta, Selva, Areia, Rocha, Pedra, Terra>.png` | Camadas de pintura do Landscape. A soma das camadas é 255 |
| `T_Mapa_Base.png`, `T_Mapa_Aquarela.png` | Imagem da ilha para os mapas da interface: 2048 px, norte para cima |
| `mapa_ue.json` | POIs, acampamentos, rio (com o nível da água), lagos, pontes e estradas, em cm da Unreal (X = norte, Y = leste) |

## Os três mapas da interface (para o lançamento)

Os três usam a mesma textura da ilha e a mesma conversão de coordenadas, que está em
`mapa_ue.json` (`mapa_imagem`).

1. **Minimapa no HUD**
   - Fica no canto superior direito, circular, e mostra cerca de 150 m em volta do jogador.
   - **O norte fica sempre para cima, como no Fortnite, e a seta do jogador gira.** O parâmetro
     `Girar` = 1 do material faz o mapa girar com a câmera. Ele não é o padrão porque os nomes, que
     estão desenhados na textura, girariam junto.
   - Mostra o jogador, o círculo atual e o próximo da tempestade, o ícone de luta contra creeps
     (GDD §12, "Barulho"), drops aéreos e o marcador.
2. **Mapa em tela cheia (M)**
   - Mostra a ilha inteira, com a grade A–J e 1–10, os nomes dos POIs e a tempestade atual e a
     próxima.
   - Mostra a posição do jogador e um marcador colocado com clique.
3. **Mapa da queda**
   - É o mesmo widget do mapa em tela cheia, aberto no dirigível.
   - Mostra a rota do dirigível (sorteada a cada partida), a contagem para saltar e onde o jogador
     marcou para cair.

**Como é feito:**

- **Um único material, `M_UI_Mapa`** (`/Game/NexusRoyale/UI/Mapa`), criado por
  `Unreal/ue_mapa_ui_material.py`. Um nó Custom em HLSL desenha:
  - a textura `T_Mapa_UI` (aquarela com nomes e grade 10 × 10 sobre ±560 m);
  - a tempestade: roxo fora do círculo atual, e o próximo círculo em branco;
  - a rota do dirigível tracejada;
  - o marcador e a seta do jogador.
- O widget só atualiza os parâmetros a cada tick. Os parâmetros estão documentados no topo do
  script.
- **Grade da tela cheia:** colunas A–J de oeste para leste e linhas 1–10 de norte para sul, sobre
  ±560 m. As células da tabela de POIs usam essa grade.

**De onde vem a imagem:**

- Por enquanto, de `T_Mapa_*` (gerada dos mesmos dados do terreno).
- Quando os POIs estiverem montados na Unreal, ela passa a vir de uma captura ortográfica de cima
  da ilha (SceneCapture2D com 1.260 m de largura), passada pelo mesmo filtro de estilo. Assim os
  prédios aparecem no mapa.

## Tempestade com o mapa novo (proposta para a sessão de gameplay)

Os raios de `Unreal/Data/CT_Storm.csv` foram feitos para a ilha de 400 m. Para a ilha de cerca de
1 km, o círculo inicial precisa cobrir tudo (cerca de 560 m).

| Fase | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Raio atual (m) | 290 | 160 | 110 | 70 | 40 | 18 | 0 |
| Raio proposto (m) | 560 | 310 | 210 | 135 | 75 | 35 | 0 |

Os tempos do GDD (seção 13) não mudam. Com raios maiores, o fechamento fica mais rápido (até
cerca de 4 m/s na fase 1). Isso precisa ser testado junto com a velocidade dos arquétipos (6,0 a
6,3 m/s).

## Como montar na Unreal (próximos passos)

1. **Landscape.** Este passo é manual: a API Python da 5.8 não cria Landscape nem LayerInfo.
   - **Já está pronto** (`Unreal/ue_mapa_assets.py`): em `/Game/NexusRoyale/Map/V2/` estão o
     `M_Terreno_V2`, o `T_Pigmento`, o `T_Mapa_Base` e o `T_Mapa_Aquarela`.
   - **Nível:** a ilha nova vai num nível próprio, `/Game/NexusRoyale/Maps/L_Ilha`. O `L_Island`
     (ilha de 400 m) fica intacto até a nova estar pronta, porque a sessão de gameplay está usando
     esse nível.
   - **Passo a passo no editor**, com o `L_Ilha` aberto (nomes em português, com o inglês entre
     parênteses):
     1. Selecionar modo → **Paisagem** (*Landscape*, Shift+2). Aba **Gerenciar** (*Manage*) →
        **Nova** (*New*) → **Importar do arquivo** (*Import from File*).
     2. **Material:** `M_Terreno_V2`.
     3. **Arquivo do mapa de altura:**
        `D:\meus documentos\Fortnite\Unreal\Data\Mapa\gerado\heightmap_1009.png`. O painel deve
        mostrar **1009 × 1009**, com 63 quads por seção, 2 × 2 seções e 8 × 8 componentes.
     4. **Localização:** X 0, Y 0, Z 0. Esse campo é o **centro** do Landscape; o canto fica
        sozinho em (-63000, -63000).
     5. **Escala:** X 125, Y 125, Z 100.
     6. **Camadas.** Para cada uma das 8 (Grama, Campo, Floresta, Selva, Areia, Rocha, Pedra,
        Terra):
        - no campo do LayerInfo, clicar em **+** → *Weight-Blended Layer (normal)* e salvar em
          `/Game/NexusRoyale/Map/V2`;
        - no campo de arquivo, escolher `gerado\camada_<Nome>.png`.
     7. **Importar**, e depois salvar (Ctrl+S).
   - **Depois disso, a IA confere** a orientação com uma captura de cima, comparando com o
     `T_Mapa_Base`: o norte (+X) deve ficar no topo.
2. **Material do Landscape** com as 8 camadas, no estilo escolhido (ver Direção de arte).
3. **Água:**
   - um plano de mar no nível 0;
   - um plano em cada lago, no nível de `mapa_ue.json`;
   - o rio como spline mesh seguindo os pontos e níveis de `mapa_ue.json`.
4. **POIs:** montar com os kits, adaptando o `Unreal/ue_build_pois.py` (que hoje monta a Vila e a
   Cidade na ilha de 400 m) para as posições novas.
5. **Vegetação:** Stylized Nature espalhada pelas camadas Floresta, Selva e Campo, com instâncias
   (HISM) e distância de corte curta, pensando na RX 570.
6. **Jogo:** acampamentos, baús, pontes e o centro da tempestade a partir do `mapa_ue.json`.
7. **Interface:** `T_Mapa`, `WBP_Minimapa`, `WBP_MapaCompleto` e o modo queda.

## Direção de arte: cartoon e aquarela (pergunta do usuário em 15/10)

**É possível?** Sim, e combina com os assets. A Quaternius já é low-poly, com cores chapadas e
texturas pequenas.

- **Cartoon:** iluminação em faixas (cel shading) e contorno, feitos por um material de
  pós-processamento.
- **Aquarela:**
  - manchas de cor chapadas (filtro tipo Kuwahara);
  - borda escurecida onde a cor muda;
  - leve "sangria" da tinta;
  - textura de papel por cima.
- **Leitura do combate (pilar 2 do GDD):** personagens, magias e telegrafias de ataque ficam fora do
  filtro de aquarela (Custom Depth/Stencil) e mantêm o contorno nítido. Só o cenário fica
  "pintado".

**Fica mais leve ou mais pesado?** Mais leve no total.

- **Economiza:**
  - Lumen;
  - sombras virtuais;
  - Nanite;
  - texturas PBR grandes (difusa, normal e rugosidade em 2K ou 4K).

  Nada disso é necessário num visual estilizado, e são justamente os recursos que mais pesam numa
  RX 570 de 4 GB. As texturas chapadas ocupam bem menos memória de vídeo.
- **Custa:** o pós-processamento de contorno e aquarela tem custo fixo por pixel. Pela minha
  estimativa, que ainda não foi medida, fica em 1 a 3 ms em 1080p numa RX 570. Pode ser feito em
  meia resolução se precisar.
- **Na prática:** o jogo deve rodar melhor estilizado do que com o visual padrão da Unreal 5.
