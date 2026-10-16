# IA: creeps e bots

---

## 1. Creeps (hoje)

- `BP_Creep` (Character + AIController), filhos `BP_Creep_Imp` e `BP_Creep_Puglin`; `BP_CreepCamp` cria e reaparece.
- `Think` em Blueprint, a cada 0,3 s, **só no servidor**:
  - sem alvo: volta para casa e pega o primeiro herói a menos de 7 m;
  - com alvo: persegue e bate a 1,7 m (`ApplyDamage`);
  - Muralha de Gelo no caminho: bate nela até quebrar;
  - alvo a mais de 15 m da origem: solta, volta com vida cheia (corrente);
  - ao levar dano: o acampamento inteiro ataca o agressor.
- Anda por `AddMovementInput` em linha reta (**sem NavMesh**); pode enroscar.
- Morte: pose, sem colisão, XP para quem deu o golpe final, some em 3 s; o acampamento solta o drop.
- **Rede:** criado no servidor; o Character replica movimento. Vida, golpe e morte não replicam (sem verificar).

## 2. Creeps (alvo)

| Item | O quê | Marco |
|---|---|---|
| Rede | Vida replicada (barra acima), estado (morto, atacando) por `OnRep`; animação de golpe por Gameplay Cue ou multicast | M2 |
| Sono | O acampamento dorme (sem `Think`, sem tick, dormente na rede) quando não há herói a menos de ~60 m | M10 |
| Aggro legível | Ícone "!" e som ao pegar alvo; linha de ataque visível; corrente com aviso | M10 |
| Tipos | Imp (corpo a corpo, rápido), Puglin (tanque); novo **à distância** (projétil lento); elite (Puglin Ancião, área) | M10 |
| Dados | `DT_Creeps`: vida, dano, recarga, alcances, XP, drop, velocidade | M10 |
| Navegação | NavMesh no mapa v2 (ilha de 1 km); no `L_Island` continua em linha reta, em clareiras | M17 |
| Uso tático | O creep ataca quem o machucou por último: dá para puxar um acampamento para cima de outro jogador | M10 |
| Ferramenta | StateTree, quando o `Think` em Blueprint ficar pequeno demais (decisão no M10) | M10 |

**Custo de servidor:** ~70 creeps × `Think` a 0,3 s é barato; o caro é o movimento e a replicação. Por isso o sono e a
frequência de rede de 10 Hz.

## 3. Bots (D-012)

Bot = `ANRBotController` (AIController com PlayerState próprio) possuindo o **mesmo** `BP_HeroBase`. Usa as mesmas
habilidades (GAS), as mesmas armas e o mesmo inventário. Cérebro em **StateTree** (plugin já ativo).

**Informação honesta:** o bot só sabe o que percebe (`AIPerception`: visão com cone e distância, audição de tiros e
habilidades). Ele sabe a zona (todo jogador vê a zona no mapa). Nada de ler a posição de quem ele não viu.

### Fases

| Fase | O bot faz | Marco |
|---|---|---|
| 1 | Anda, salta do dirigível num ponto sorteado, atira em quem vê, foge da zona | M15 (parte no M4 como "preenche vaga") |
| 2 | Abre baús, pega e troca armas, mata creeps, luta (aproxima/recua pela vida) | M15 |
| 3 | Usa habilidades e itens, participa do draft (§4) | M15 (draft no M6) |
| 4 | Estratégia: rotação com a zona, avaliar ameaça, terceiro na briga, evitar briga perdida | M22+ |

### Dificuldade (`DA_Bot_<Dificuldade>`)

Tempo de reação, erro de mira (graus), chance de usar habilidade na hora certa, agressividade, quanto loot procura.
O bot não tem mira perfeita nem reação instantânea em nenhuma dificuldade.

## 4. Bots no draft

- No começo do draft, cada bot sorteia um **plano**: brigão (perto + defesa), atirador (longe + mobilidade), controle
  (controle + dano em área), suporte (sustento + utilidade).
- Para cada habilidade livre: `pontuação = afinidade com o plano + cobertura de papel + sinergia com as que já tem −
  categoria repetida + ruído(dificuldade)`. As sinergias ficam numa tabela de pares (dados).
- Escolhe em 1–3 s (para o draft não esperar), e a mesma função é a "sugestão" que o servidor usa quando o tempo de um
  humano esgota.
