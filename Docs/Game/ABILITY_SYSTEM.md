# Sistema de habilidades e draft

---

## 1. Hoje

- **GAS presente, mas sem habilidades.** Existem o `UAS_Hero` (atributos), o `UNRAbilitySystemComponent` (dano, cura,
  regeneração, XP, nível, bônus) e efeitos C++ com SetByCaller (`NRGameplayEffects`). Nenhuma `GameplayAbility`,
  nenhuma Gameplay Tag.
- **As magias estão no `UNRCombateComponent`:** dardo (botão esquerdo), Bola de Fogo (Q), Muralha de Gelo (E), Chuva
  de Meteoros (X), configuradas por structs (`FNRMagiaProjetil`, `FNRMagiaEstrutura`, `FNRMagiaChuva`). Custo,
  recarga e mira são do componente. Tudo roda no input local (sem rede).
- **Atores reaproveitáveis:** `ANRProjetilMagico` (projétil com área e teleguiado), `ANREstruturaMagica` (parede com
  vida e duração), `ANRChuvaMeteoros` (aviso no chão + impactos + chão em chamas).

## 2. Alvo: GAS com comportamentos genéricos (D-008)

```
UNRAbilityDefinition (Data Asset, uma por habilidade)
   ├─ Id (tag)            Ability.Id.BolaDeFogo
   ├─ Tipo                Básica | Ultimate
   ├─ Categorias (tags)   Ability.Category.Damage, Ability.Category.Field …
   ├─ Escola (tag)        Ability.School.Fire  (cor, som, interação)
   ├─ Ícone, Nome, Descrição, Dica de contrajogo
   ├─ Custo de mana, Recarga, Cargas
   ├─ Telegrafia          tempo de aviso, forma (círculo, linha, cone), cor
   ├─ Comportamento       classe: UNRGA_Projetil | UNRGA_AreaComAviso | UNRGA_Estrutura | UNRGA_Avanco | …
   ├─ Parâmetros          struct instanciada do comportamento (dano, raio, velocidade, duração…)
   ├─ Ranks               multiplicadores por rank (1–3)
   └─ Mutações próprias   lista de mutações que só aparecem para quem tem esta habilidade
```

- **Concessão:** quando o herói nasce, o servidor lê as escolhas do draft no `ANRPlayerState` e dá um
  `FGameplayAbilitySpec` por habilidade, com o Data Asset como `SourceObject`, e a tecla (Q/E/R/T) como `InputID`.
- **Custo e recarga:** um `GE_Custo` e um `GE_Recarga` genéricos, com o valor por SetByCaller e a tag de recarga
  `Cooldown.<Id>`, para não criar 2 assets por habilidade.
- **Escala:** dano e cura × (1 + Arcano); recarga × (1 − redução da Agilidade). Ranks multiplicam por cima.
- **Liberação da ultimate:** a GA confere o nível do dono (≥ 6) em `CanActivateAbility`; o HUD mostra "nível 6".
- **Efeitos visuais e sons:** Gameplay Cues (`GameplayCue.Ability.<Id>.*`), para replicar sem RPC próprio.

### Comportamentos (primeira leva)

| Classe | Cobre (exemplos do GDD v2) | Já existe a base |
|---|---|---|
| `UNRGA_Projetil` | Bola de Fogo, Tiro Rasante | `ANRProjetilMagico` |
| `UNRGA_AreaComAviso` | Chuva de Meteoros, Fissura, Muro de Chamas | `ANRChuvaMeteoros` |
| `UNRGA_Estrutura` | Muralha de Gelo, Pilar de Pedra, Domo Glacial, Farol | `ANREstruturaMagica` |
| `UNRGA_Avanco` | Arremetida, Rajada (impulso) | — |
| `UNRGA_Buff` | Fúria do Campeão, Aurora | efeitos do ASC |
| `UNRGA_Passiva` | Sifão, Graça, Coração Gélido, Carga Estática | — |
| `UNRGA_Zona` | Névoa Sombria, Eclipse | — |

Uma habilidade única demais ganha classe própria (filha de `UNRGameplayAbility`). Revisar a lista a cada 10 novas.

## 3. Gameplay Tags (nativas, em `NRGameplayTags`)

```
Ability.Id.*                 identidade de cada habilidade
Ability.Type.Basic / Ability.Type.Ultimate
Ability.Category.Damage | Mobility | Defense | Control | Sustain | Utility | Vision | Trap | Displacement | Summon | Field
Ability.School.Martial | Fire | Ice | Earth | Storm | Shadow | Light
Cooldown.*                   recarga por habilidade
Effect.Stun | Slow | Root | Silence | Shield | Knockback | Burn | Wet | Reveal | Invisible
Damage.Physical | Damage.Ability | Damage.Weapon | Damage.Storm | Damage.True
State.Dead | State.Casting | State.Invulnerable | State.InCombat | State.OnShip | State.Skydiving | State.Downed(futuro)
```

Nada de `enum` gigante para identidade: o draft, a UI e os bots filtram por tag.

## 4. Draft (M6)

### 4.1 Estado (servidor → todos)

`UNRDraftComponent`, no `ANRGameState`:
- `Pool`: lista de `FPrimaryAssetId` sorteada no começo (respeitando a proporção por categoria, §6).
- `Escolhas`: Fast Array de `{Habilidade, Jogador, Rodada}`.
- `Rodada`, `Faixas` (quem está em qual), `JogadorDaVez` por faixa, `FimDaJanela` por faixa (horário do servidor).

### 4.2 Regras (servidor)

1. `Server_Escolher(Habilidade)` só é aceito se: é a vez desse jogador na faixa dele, a janela não acabou, a
   habilidade está no pool, **ninguém escolheu antes** e o tipo bate com a rodada (ultimate na 1, básica nas outras).
2. Aceito → entra em `Escolhas` (replica para todos na hora) e a faixa passa para o próximo.
3. Recusado → o cliente recebe o motivo ("já foi escolhida") e continua na vez dele até a janela acabar.
4. Janela acabou → o servidor escolhe pela lista de preferências do jogador; sem lista, pela sugestão (mesma lógica
   dos bots).
5. Fim da rodada 4 → as escolhas vão para o `ANRPlayerState` de cada um; o GameMode passa para a Queda.

Formato (faixas, janelas, rodadas, fator do pool) em `DA_Draft_Padrao` (D-007).

### 4.3 Bots no draft

Cada bot recebe um "plano" (brigão, atirador, controle, suporte) e pontua cada habilidade livre: afinidade com o
plano + cobertura (quer pelo menos 1 de mobilidade ou defesa) + sinergia com o que já tem (tabela de pares em dados)
− repetição de categoria. Escolhe a melhor com um pouco de ruído pela dificuldade. Detalhes no
[AI_AND_BOTS.md](AI_AND_BOTS.md).

## 5. Checklist de contrajogo (toda habilidade nova passa por aqui)

- [ ] Tem pelo menos uma fraqueza clara: aviso, som, animação, tempo de viagem, alcance, recarga, custo ou risco de
      posição.
- [ ] Dano ≥ 100: projétil visível ou aviso no chão ≥ 0,3 s (ultimate: 0,5–1 s).
- [ ] Controle ≤ 1,5 s e respeita a redução por repetição.
- [ ] Invisibilidade tem contra (Luz, dano, som de passos).
- [ ] Mobilidade tem limite (cargas, recarga, distância).
- [ ] Não tira a relevância da arma.
- [ ] Combina com pelo menos 2 outras habilidades do pool (anotar quais).
- [ ] Cor e som da escola; silhueta do efeito distinta das outras.
- [ ] Números no Data Asset, e entrada no BALANCE.md.

## 6. Composição do pool final (128)

| Categoria principal | Básicas (96) | Ultimates (32) |
|---|---|---|
| Dano | 22 | 8 |
| Controle / Deslocamento | 16 | 6 |
| Mobilidade | 14 | 4 |
| Defesa / Campo | 16 | 5 |
| Sustento | 10 | 4 |
| Visão / Utilidade / Armadilha / Invocação | 18 | 5 |

Proporção inicial, para todo draft oferecer opções de cada papel. Cada partida sorteia o pool mantendo essa proporção
(com 20 jogadores, o pool inteiro entra).

## 7. Pool de desenvolvimento (fatia vertical)

As 14 magias + 7 ultimates do GDD v2, nesta ordem de implementação (mais base pronta primeiro):

| Ordem | Habilidade | Tipo | Comportamento |
|---|---|---|---|
| 1 | Bola de Fogo | Básica | Projetil (porta do código atual) |
| 2 | Muralha de Gelo | Básica | Estrutura (porta) |
| 3 | Chuva de Meteoros | Ultimate | AreaComAviso (porta) |
| 4 | Arremetida | Básica | Avanco |
| 5 | Pilar de Pedra | Básica | Estrutura |
| 6 | Rajada | Básica | Avanco + empurrão em cone |
| 7 | Sifão | Básica (passiva) | Passiva |
| 8 | Névoa Sombria | Básica | Zona |
| 9 | Fúria do Campeão | Ultimate | Buff |
| 10 | Domo Glacial | Ultimate | Estrutura |
| … | o resto do GDD v2 §6.3 e §6.4 | | |

Com 4 jogadores na fatia vertical: 12 básicas + 4 ultimates escolhidas; o pool de 14 + 7 dá fator ~1,2 nas básicas e
~1,75 nas ultimates. O fator 1,6 vale para 20 jogadores.
