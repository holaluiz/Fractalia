# Interface e experiência

---

## 1. Hoje

| Tela | Estado |
|---|---|
| HUD | `UNRHudWidget` (C++ monta o layout): vida, mana, nível e XP, magias com recarga, consumíveis, equipados, mira, relógio da tempestade, "FORA DA ZONA", prompt do F, painel de mutações, avisos grandes |
| Mapas | Minimapa (canto, 260 px), M em tela cheia, mapa da queda (`WBP_Mapa` + `HUD_NexusRoyale`) |
| Menus, lobby, ESC, configurações, morte, vitória, resultados | **Não existem.** O jogo abre direto no `L_Island` |

## 2. Telas alvo

| Tela | Conteúdo mínimo | Marco |
|---|---|---|
| Menu principal | Jogar, Configurações, Sair | M3 |
| Hospedar | Nome da sala, LAN/internet, (opções da partida no lobby) | M3 |
| Entrar | Lista de salas (LAN), campo de IP direto | M3 |
| Lobby | 20 vagas (nome, humano/bot, pronto, ping), controles do host (bot, dificuldade, expulsar, opções, começar) | M4 |
| Carregando / Ilha de Espera | Quem já carregou; dicas | M4 |
| Draft | Pool filtrável, escolhidas riscadas com dono, builds de todos, faixa e vez, tempo, lista de preferências | M6 |
| HUD | Ver §3 | M5–M16 |
| Inventário (Tab) | 6 slots, 2 armas, atributos e pontos para gastar, mutações escolhidas | M9, M11 |
| Mapa (M) | Já existe | — |
| ESC | Voltar, Configurações, Sair da partida (com confirmação) | M3 (básico), M16 |
| Configurações | Vídeo, áudio, controles e teclas, câmera, mira, idioma, acessibilidade | M16 |
| Morte / espectador | Quem matou, com o quê, dano recebido por fonte; espectando X | M14 |
| Vitória / colocação | "VITÓRIA" ou "#N de 20" | M1 (texto), M14 |
| Resultados | Tabela da partida | M14 |

## 3. HUD da partida

Mostra, sem lotar a tela: vida, mana, habilidades com recarga, ultimate (pronta/bloqueada), 6 itens, 2 armas e
munição, XP e nível, **pontos de atributo disponíveis**, jogadores vivos, zona (relógio e distância), minimapa,
efeitos de estado importantes (lento, atordoado, queimando, molhado, escudo).

Disposição proposta: vida/mana/nível embaixo à esquerda; habilidades embaixo no centro; armas e munição embaixo à
direita; itens (Z…N) numa linha acima das habilidades; minimapa, vivos e relógio da zona em cima à direita;
estados acima da barra de vida.

**Visual:** herda o mundo pintado (bordas de pincel, papel), mas com contraste alto e leitura instantânea. Números
grandes só para o que importa na luta (vida, munição, recarga).

## 4. Controles padrão (D-002g)

| Ação | Tecla | Hoje |
|---|---|---|
| Mover / pular / agachar | WASD / Espaço / Ctrl | igual (agachar não existe) |
| Atacar com a arma | Botão esquerdo | era o dardo do Feiticeiro |
| Mirar | Botão direito | — |
| Arma de perto / de longe | 1 / 2 (roda do mouse alterna) | 1-3 eram consumíveis |
| Habilidades básicas | Q / E / R | Q e E existiam |
| Ultimate | **T** | era X |
| Esquiva | Shift | — |
| Interagir | F | igual |
| Itens | **Z X C V B N** | — |
| Escolher mutação | Alt + 1/2/3 (ou clique no painel) | igual |
| Trocar opções de mutação | Alt + 4 | igual |
| Inventário e atributos | Tab | — |
| Mapa | M | igual |
| Menu | Esc | — |
| Saltar do dirigível / planar | Espaço | igual |

**Remapeamento:** todas as ações ficam como **Player Mappable Keys** no Enhanced Input, com as configurações do jogador
salvas pelo `UEnhancedInputUserSettings`. Conflitos de tecla aparecem na tela de controles.

**Correção pendente antes de tudo:** o `IMC_Default` no disco não tem as teclas de combate (bug 1.9; M0.5).

## 5. ESC sem pausa

- ESC abre uma camada **local**. A partida **não pausa** (multiplayer). O personagem para de receber input de jogo
  enquanto o menu está aberto, mas continua no mundo e pode tomar dano.
- **Sair da partida:** pede confirmação. Cliente: sai e volta ao menu. **Host:** aviso "Sair vai encerrar a partida
  para todos os jogadores conectados."

## 6. Idioma

Interface em português (pt-BR) primeiro. Textos em `FText` com namespace, para dar para traduzir depois (String
Tables a partir do M16).
