# PLANO.md: plano de melhorias do Nexus Royale

> **Histórico.** Desde 15/10, 20:30, o plano central é o [Docs/Game/MASTER_PLAN.md](Docs/Game/MASTER_PLAN.md). Os itens
> abertos daqui foram levados para lá (tabela "Itens herdados do PLANO.md"). Não marque mais nada aqui.

Criado em 2026-10-15, por volta de 18:10 (Brasília), por Claude (Claude Code), a pedido do usuário: "analise
tudo, crie um plano, guarde o plano na pasta e comece a seguir esse plano".

**Como usar:** marque `[x]` no que ficar pronto e escreva ao lado o que foi testado. O contexto completo do
projeto continua no [AGENTS.md](AGENTS.md); o design, no [Design/GDD.md](Design/GDD.md). Este plano não muda
números do GDD (regra 1 do AGENTS.md); onde o GDD não diz, a escolha está em "Decisões para o usuário revisar".

---

## 1. Diagnóstico

O que a análise do código, dos Blueprints (DSL), dos logs e do GDD encontrou.

1. **Partida real no jogo instalado (0.1.0).** O log do jogo em `D:\Jogos\NexusRoyale` mostra uma partida de
   8,5 min (17:31–17:40): 4 baús abertos, **nenhum creep morto (0 de XP)** e o fim tomando 3% de dano por segundo
   da tempestade da fase 3. Ou seja: o jogador não achou os creeps, não subiu de nível e não viu a tempestade
   chegando.
2. **O minimapa não aparece no jogo empacotado (nem no editor).** Duas causas:
   - o jogo empacotado roda em **SM6** (DirectX 12, compilador DXC) e o editor em SM5. O `M_UI_Mapa` não compila
     em SM6 (`vector swizzle 'w' is out of bounds`: o HLSL usa `Vista.w`, mas o parâmetro chega como float3). A
     Unreal troca pelo material padrão e o mapa some. O aviso está no log do editor de 14:05
     (`NexusRoyale-backup-2026.10.15-14.51.21.log`);
   - achada no teste em PIE: o `HUD_NexusRoyale` chamava `SetDesiredSizeInViewport` depois das âncoras, e na 5.8
     essa função zera as âncoras. O minimapa ia para fora da tela (à esquerda) e o mapa completo (M e queda)
     aparecia com só um quarto à vista, no canto.
3. **Sem informação da tempestade no HUD.** Não há relógio, fase nem aviso de "fora da zona". Sem o minimapa, o
   jogador fica sem nada.
4. **Mensagens de debug na tela:** "Tempestade: -X% da vida" a cada segundo (`BP_HeroBase.StormTick`), "Dano: -X"
   (`BP_HeroBase.EventAnyDamage`) e o prompt "[F] Abrir baú" como `PrintString`.
5. **Pouco conteúdo no `L_Island`:** um acampamento só, a 18 m da praça. Quem salta do dirigível longe dali nunca
   acha creeps. Os creeps também não soltam nada (GDD §12).
6. **Subir de nível não muda o jogo:** só números. As **mutações** (GDD §7.4) e o **piso de nível** no fim de cada
   fase (§7.3) não existem. O `BP_StormController` já dispara `OnPhaseEnded` com o piso, mas ninguém escuta.
7. **Restos da v1 no `L_Island`:** Nexus, torres, fragmentos, poções de escudo, plataformas de salto e as estátuas
   dos heróis antigos na praça.
8. **Lacunas maiores (etapa 2 em diante):** grimórios ainda não viram magias E/R, não há tela de montagem, só o
   Feiticeiro de Fogo existe, não há rede, e o mapa v2 (`L_Ilha`) espera o usuário importar o Landscape.

## 2. Fase 1: versão 0.1.1, "uma partida inteira faz sentido"

Objetivo: quem instalar a 0.1.1 cai na ilha, acha creeps, sobe de nível escolhendo mutações, vê a tempestade no
minimapa e no relógio, e não lê mensagens de debug. A publicação também testa a atualização automática do launcher
(0.1.0 → 0.1.1), que ainda não foi testada.

- [x] **1.1 Minimapa no jogo empacotado.** Feito: o `.w` saiu do HLSL do `M_UI_Mapa` (o modo virou o escalar
      `Modo`, `Unreal/ue_mapa_ui_material.py`), e o `HUD_NexusRoyale` passou a chamar posição → tamanho → âncoras →
      alinhamento. **Conferido no jogo empacotado 0.1.1 (SM6):** o minimapa aparece no canto, com a seta e o círculo
      da tempestade, e o cook compilou o `M_UI_Mapa` para SM6 sem aviso.
      - **Achado novo:** o fundo do minimapa é o desenho da ilha v2 (Distrito Arcano, Lago Espelho…), não o do
        `L_Island`. A seta e o círculo estão certos (coordenadas do mundo), mas os nomes não batem com a ilha de
        teste. Some quando o `L_Ilha` virar o mapa padrão (fase 3); antes disso, dá para gerar uma textura do
        `L_Island` vista de cima (item 1.8).
- [ ] **1.9 URGENTE: teclas de combate no jogo empacotado (versão 0.1.2).** Achado depois de publicar a 0.1.1: o
      `IMC_Default` no disco só tem pulo, câmera, movimento e mapa; botão esquerdo, Q, E, X, F, 1-3 e 4 nunca foram
      salvos (só existiam na memória do editor). No jogo empacotado não dá para atacar, abrir baú nem escolher
      mutação. Corrigir o `ue_mvp_setup.py` (marcar o IMC antes de salvar), rodar, conferir o arquivo, empacotar
      e publicar a 0.1.2 com o OK do usuário.
- [ ] **1.8 (opcional) Minimapa do `L_Island`:** capturar a ilha de cima e usar como `T_Mapa_UI` enquanto o mapa
      padrão for o `L_Island`, com a `Extensao` dos materiais ajustada para 400 m.
- [x] **1.2 HUD da partida** (`UNRHudWidget`, C++). Testado em PIE: relógio ("Fase 2 · a tempestade fecha em
      1:16" / "está fechando"), "FORA DA ZONA: 16 m até o círculo · −2% da vida por segundo", prompt
      "[F] Pegar: Grimório: Coração Gélido (Comum)" e nenhum `PrintString` de debug.
  - relógio da tempestade no topo: "Fase N · a tempestade fecha em M:SS" / "fechando: M:SS" / "fechada";
  - aviso grande "FORA DA ZONA" quando o herói está fora do círculo;
  - prompt do F ("[F] Abrir baú", "[F] Pegar …") perto da mira, lido do interativo atual do herói;
  - tirar os `PrintString` de debug (tempestade, dano e prompt).
- [x] **1.3 Mutações** (GDD §7.4), num componente C++ novo (`UNRMutacoesComponent`). Testado em PIE pelas
      funções do componente (o Alt de verdade não dá para injetar pelo Python; falta testar no teclado):
  - a cada nível (2 a 10) entram 3 opções; **Alt+1/2/3** escolhe, sem limite de tempo, e as escolhas acumulam;
  - **1 troca de opções por partida** (Alt+4);
  - as do kit atual: +2 pontos efetivos num atributo (com peso pela build), Bola de Fogo deixa chão em chamas por
    3 s, Muralha de Gelo +50% de largura, as três de ultimate (só nos níveis 8 e 10), +8% de velocidade fora de
    combate e +15% de cura de consumíveis;
  - ficam para depois as que dependem do que não existe: esquiva com 2 cargas, +1 slot de consumível, abates
    revelam inimigo, e as de magias que o Feiticeiro de Fogo não tem;
  - painel no HUD com as opções e a lista das escolhidas.
  - **Testado:** fila de níveis (2, 3, 4 e 5 juntos depois de limpar a ilha), a troca uma vez só, ultimate só
    no 8 e no 10 (sempre uma das opções), e cada efeito: muralha 6 → 9 m, chamas da Bola de Fogo (nascem no
    chão e não ferem quem lança), velocidade 618 → 666 fora de combate, Vitalidade +60 de vida, raio da ultimate
    4 → 4,56 m, recarga 80 → 64 s, mana devolvida (−60 em vez de −120).
  - **Sem testar:** Alt+1/2/3 e Alt+4 no teclado; as chamas da Bola de Fogo ferindo creeps (a queima é a mesma
    da Chuva de Meteoros, já testada).
- [x] **1.4 Piso de nível** (GDD §7.3): no fim das fases 1 a 5, quem estiver abaixo do piso (2, 3, 4, 6, 7, já no
      `CT_Storm`) sobe até ele, e cada nível ganho dá a sua mutação. Testado em PIE pelo relógio da tempestade:
      fim da fase 1 → nível 2; fim da fase 2 → nível 3.
- [x] **1.5 Creeps:** 6 acampamentos no `L_Island` (4 pequenos e 2 médios), em clareiras achadas por script, e
      o drop do GDD §12. Testado em PIE: os 2 médios soltaram grimório; 3 dos 4 pequenos soltaram consumível. O
      Puglin ataca (quase matou o herói no nível 10).
- [x] **1.6 Limpar o `L_Island`:** 107 atores da v1 apagados (Nexus, 4 torres, 8 plataformas de salto, 21 poções
      de escudo, 9 de vida, 60 fragmentos e os 4 heróis antigos da praça). Os caixotes ficaram, como cobertura.
- [x] **1.7 Testar e publicar:** compilado, testado num PIE, empacotado e conferido no jogo (18:58). **Publicada**
      com o OK do usuário às 19:09: Release `v0.1.1` em `holaluiz/MOBA-BR` (zip de 976 MB). **A atualização pelo
      launcher funcionou:** o atalho instalado baixou, trocou a pasta `game` (0.1.0 → 0.1.1) e abriu o jogo em
      123 s; o mapa da queda apareceu inteiro e centralizado. A tag aponta para o `2ff3965`, porque o código da
      0.1.1 ainda não foi commitado.

## 3. Fase 2: montagem e grimórios (etapa 2 do GDD §15)

- [ ] **2.1 Grimórios viram as magias E e R**, com rank por raridade e "mesma magia sobe o rank" (§8.2). É aqui
      que o combate migra para Gameplay Abilities (`GA_*`), como diz o cabeçalho do `UNRCombateComponent`.
- [ ] **2.2 Tela de montagem** antes da partida: arquétipo, 20 pontos em 5 atributos, Q e ultimate (§4).
- [ ] **2.3 Os outros arquétipos** (Guerreiro, Patrulheiro, Místico) e as escolas Marcial, Gelo e Terra
      (8 magias + 4 ultimates).
- [ ] **2.4 Feiticeiro completo:** passiva Canalizador, animação de lançar, ultimate de volta ao nível 6
      (`NIVEL_ULTIMATE` no `ue_mvp_setup.py`) quando o mapa tiver XP suficiente.
- [ ] **2.5 Legibilidade** (§10): barras e nível acima dos inimigos, número de dano, tela de morte.
- [ ] **2.6 Interações** Fogo + vegetação e Gelo + água (§6.5), quando houver vegetação e água no mapa v2.
- [ ] **2.7 Mutações que faltaram** na 1.3, quando existirem esquiva, slot extra e inimigos jogadores.

## 4. Fase 3: mapa v2 (depende do usuário)

- [ ] **3.0 (usuário)** importar o Landscape no `L_Ilha` (passo a passo em Design/Mapa.md, "Como montar").
- [ ] 3.1 Conferir a orientação; água (mar, lagos, rio); POIs; vegetação.
- [ ] 3.2 Levar dirigível, tempestade (raios novos no `CT_Storm.csv`), baús e os 21 acampamentos
      (`place_camps()` com o `mapa_ue.json`) para o `L_Ilha` e torná-lo o mapa padrão.
- [ ] 3.3 Elites (Puglin Ancião), baús dourados e drops aéreos (§8.4 e §12).

## 5. Fase 4: partida completa

- [ ] 4.1 Rede: replicar creeps, magias, F e salto (RPCs); listen server com Steam (app 480) ou EOS, depois
      servidor dedicado (§15, etapa 3).
- [ ] 4.2 Bots para completar a partida enquanto não há 20 jogadores.

## 6. Dívidas técnicas (encaixar quando passar perto)

- `Content/NexusRoyale/Map/_tmp/` (cópia da ilha com redirector pendurado).
- Assets e scripts da v1 (GDD §16.1, "Remover"; `Export/map_layout.json`, `import_nexus_assets.py`,
  `Blender/scripts/build_all.py`) e o `BP_ThirdPersonGameMode` com o `BP_Hero_Brakka`.
- Visual: meteoros e clarões saem creme em vez de laranja; o chão em chamas não parece fogo.
- Creeps: malhas de equipamento do Imp e do Puglin, golpe no meio da animação, batem no corpo depois da morte.
- Memória de vídeo: o editor cai no segundo ou terceiro PIE (seção 5 do AGENTS.md).

## 7. Decisões para o usuário revisar

Escolhas feitas onde o GDD não diz nada. Nenhuma muda número do GDD; todas são fáceis de trocar.

| Assunto | Escolha | Onde mudar |
|---|---|---|
| Tecla da troca de mutações | Alt+4 (o GDD só diz "1 troca por partida") | `IA_TrocarMutacoes` no `IMC_Default` |
| Alt+1/2/3 sem mutação pendente | Usa o consumível normalmente | `UNRCombateComponent` |
| Mutações de atributo | Podem repetir; as outras, uma vez cada | `UNRMutacoesComponent` |
| Níveis 8 e 10 | Uma das 3 opções é sempre de ultimate (se ainda houver) | `UNRMutacoesComponent` |
| "+30% de área da ultimate" | Área: raio × 1,14 (e o raio dos meteoros junto) | `UNRMutacoesComponent` |
| Chão em chamas da Bola de Fogo | 20/s no raio da explosão (3 m), como a Chuva de Meteoros | `FNRMagiaProjetil` |
| Drop dos creeps | Cai onde o último creep do acampamento morreu | `BP_CreepCamp.CheckCamp` |
| Acampamentos no `L_Island` | Mais alguns pequenos e 2 médios (a ilha de teste tem 400 m) | `Unreal/Data/Camps_L_Island.json` |
