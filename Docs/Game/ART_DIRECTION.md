# Direção de arte

**Alvo:** uma ilustração 3D jogável. Superfícies pintadas (aquarela/ilustração), formas um pouco simplificadas,
silhuetas fortes, cores saturadas com contraste quente × frio, iluminação de humor (pôr do sol, noite). **Não** é
fotorrealismo. **A legibilidade competitiva vem antes da decoração.**

Base aprovada em 15/10 (GDD v2 §10 e [Design/Mapa.md](../../Design/Mapa.md)): **cartoon + aquarela**; só o cenário
recebe a aquarela; personagens, magias e avisos ficam fora e mantêm contorno nítido.

---

## 1. Hoje

| Peça | Estado |
|---|---|
| Config de render | Sem Lumen, sem sombras virtuais, sem distance fields; `r.CustomDepth=3` (stencil). Mais leve na RX 570 |
| Pós-processamento | `M_PP_CartoonAquarela` (+ instância) e `M_PP_Cel` em `/Game/NexusRoyale/Render/`; volume infinito no `L_Island` |
| Stencil | 1 herói, 2 creeps, 3 pickups, 4 projéteis/estruturas/chuva: ficam fora da aquarela |
| Terreno v2 | `M_Terreno_V2` (8 camadas com variação de pigmento), `T_Pigmento` |
| Malhas | Quaternius (low-poly, cores chapadas); Nanite desligado em 159 malhas (sem commit) |
| VFX | esferas unlit com luz; meteoros saem creme em vez de laranja (estouro no tonemapper) |
| Iluminação | sol, céu e névoa padrão; sem humor definido |
| Medição | antes: 22 FPS / 34,8 ms de GPU com Lumen. **O "depois" não foi medido** |

## 2. Estratégia de materiais (M19)

Não basta pôr uma textura de aquarela ruidosa em tudo. Camadas:

1. **Master material de superfície pintada** (`M_Pintado_Master`) para cenário:
   - albedo chapado da Quaternius × **gradiente de cor** por altura/normal (topo quente, base fria);
   - **máscaras de quebra de aquarela** em coordenadas de mundo (manchas e bordas de pigmento), com escala que cresce
     com a distância (perto: detalhe fino; longe: manchas grandes, para não virar ruído);
   - **AO pintado** (escurece cantos com cor, não com cinza);
   - rugosidade alta e controlada (sem reflexo de PBR); normal de alta frequência quase zero;
   - parâmetros por família: madeira, pedra, metal, vegetação, tecido, arquitetura pintada (instâncias `MI_`).
2. **Pós-processamento** (já existe): unifica o papel e a borda pintada no cenário; fica mais leve quando os materiais
   já fazem parte do trabalho.
3. **Personagens e efeitos:** material próprio com sombra em 2–3 faixas (cel), contorno, e cor de time/escola sem
   aquarela. Rim light leve para separar do fundo quente e do frio.

## 3. Iluminação de humor (M19)

Presets em dados (`DA_Iluminacao_<Nome>`): luz direcional (cor, ângulo), céu, névoa, cor das sombras no
pós-processamento.

| Preset | Luz | Sombra | Atmosfera |
|---|---|---|---|
| Pôr do sol | laranja, baixa, sombras longas | roxo/azul | horizonte quente, silhuetas fortes |
| Noite | ciano como luz principal | azul-marinho | névoa suave, magenta e néon controlados nas janelas e nos POIs |
| Dia (base) | branco quente | azul claro | a de hoje |

**Regra:** o personagem precisa ser legível nos três (testar com captura do mesmo ponto nos três presets).

## 4. Legibilidade competitiva

- **Silhueta:** arma na mão define o que o inimigo faz (espada, arco, bacamarte, cajado). Cosmético nunca esconde.
- **Cores reservadas:** as cores das escolas (GDD v2 §6.1) e das raridades não aparecem decorando o cenário.
- **Avisos no chão:** forma e cor padronizadas (círculo, linha, cone; vermelho = inimigo, azul = seu/aliado).
- **Projéteis:** forma distinta por família e sempre mais brilhantes que o fundo.
- **Mapa:** cenário com contraste baixo nas texturas, para personagens e efeitos (contraste alto) saltarem.

## 5. Pipeline Blender → Unreal (quando houver arte própria)

GRAYBOX → validação de gameplay → kit modular → blockout estilizado → UV → texturas pintadas → LOD → import → material
→ luz → playtest. Escala em centímetros (FBX com unit scale 0,01, AGENTS.md §6), pivô na base, nomes `SM_<Kit>_<Peça>`,
colisão simples (`UCX_`). Todo asset importante entra no CHANGELOG_AI.md.

## 6. Pendências de arte conhecidas

- Meteoros e clarões creme (material unlit estoura no tonemapper): baixar a emissão ou usar cor com tonemapper em conta.
- Chão em chamas sem fogo (disco claro). Primeiro Niagara do projeto: fogo, gelo, impacto.
- Medir o "depois" da troca de render ([PERFORMANCE.md](PERFORMANCE.md)).
