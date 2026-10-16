# -*- coding: utf-8 -*-
"""
Simulador do draft de habilidades (Docs/Game/BALANCE.md, seção "Draft").

Compara formatos de draft para 20 jogadores × 4 escolhas (1 ultimate + 3 básicas), com o pool de 1,6× as escolhas
(32 ultimates + 96 básicas). Mede:
  - duração total (média e p90), do início da prévia até a última escolha;
  - satisfação: posição da habilidade obtida na lista de preferência do jogador, calculada sobre o pool que existia
    no começo da rodada (1 = pegou a favorita; maior = alguém tirou a dele antes);
  - corridas: escolhas recusadas porque outra faixa pegou a mesma habilidade enquanto o pedido viajava (só no A);
  - tempos esgotados: o servidor escolhe pelo jogador.

Formatos:
  A  serpente em faixas paralelas: 4 faixas de 5 jogadores; dentro da faixa, um de cada vez (janela de 8 s);
     as faixas andam ao mesmo tempo sobre o pool global; a ordem inverte a cada rodada (serpente).
  B  reserva simultânea: na rodada, todos mandam as 3 preferidas ao mesmo tempo (janela de 12 s); o servidor
     resolve por prioridade (serpente sobre os 20) e revela; quem perdeu as 3 recebe a melhor que sobrou.
  C  serpente sequencial clássica (um jogador por vez, 80 vezes): a referência do que NÃO fazer.

É um modelo simples (preferência = popularidade + gosto do arquétipo + ruído; tempo de decisão log-normal). Serve para
comparar formatos, não para prever o tempo exato. Uso:  python -I simular_draft.py [execucoes]
"""
import math
import random
import statistics
import sys

ARQUETIPOS = 4  # gostos de jogador ("brigão", "atirador", "controle", "suporte"); cada habilidade tem um


def criar_pool(n, rng):
    """Popularidade em lei de potência (algumas habilidades são muito disputadas) e um arquétipo por habilidade."""
    return [{"id": i, "pop": 1.0 / (i + 1) ** 0.7, "arq": rng.randrange(ARQUETIPOS)} for i in range(n)]


def preferencias(jogador, pool, rng):
    """Lista de ids da mais para a menos desejada por este jogador."""
    def util(h):
        return h["pop"] * 3.0 + (0.6 if h["arq"] == jogador["arq"] else 0.0) + rng.gauss(0.0, 0.35)
    return [h["id"] for h in sorted(pool, key=util, reverse=True)]


def tempo_decisao(rng, mediana=4.5, sigma=0.55, janela=None):
    """
    Segundos até decidir. Quem passaria da janela corre no fim (decide no último segundo) em 80% das vezes; nos outros
    20% o tempo esgota (devolve um valor acima da janela).
    """
    d = rng.lognormvariate(math.log(mediana), sigma)
    if janela is not None and d > janela and rng.random() < 0.8:
        d = janela - rng.uniform(0.2, 1.0)
    return d


def posicao(prefs, escolhida, disponiveis):
    """Posição (1 = favorita) da escolhida entre as que estavam disponíveis no começo da rodada."""
    k = 0
    for h in prefs:
        if h in disponiveis:
            k += 1
            if h == escolhida:
                return k
    return k


def rodadas(n_ult, n_bas):
    return [("ult", n_ult)] + [("bas", n_bas)] * 3


def simular_A(rng, jogadores=20, faixas=4, janela=8.0, entre_escolhas=0.5, entre_rodadas=3.0, previa=10.0,
              latencia=0.12, pool_ult=32, pool_bas=96):
    pools = {"ult": criar_pool(pool_ult, rng), "bas": criar_pool(pool_bas, rng)}
    js = [{"arq": rng.randrange(ARQUETIPOS)} for _ in range(jogadores)]
    prefs = {t: [preferencias(j, pools[t], rng) for j in js] for t in pools}
    livres = {t: set(h["id"] for h in pools[t]) for t in pools}
    por_faixa = [list(range(f, jogadores, faixas)) for f in range(faixas)]
    t = previa
    pos, corridas, esgotados = [], 0, 0
    for r, (tipo, _) in enumerate(rodadas(pool_ult, pool_bas)):
        inicio_rodada = set(livres[tipo])
        # eventos: cada faixa anda sozinha; processamos em ordem de tempo para o pool global ficar coerente
        ordem = [(lst if r % 2 == 0 else list(reversed(lst))) for lst in por_faixa]
        relogio = [t] * faixas
        indice = [0] * faixas
        escolhas_recentes = []  # (tempo, id) para detectar corrida

        def proximo(f):
            """Sorteia UMA vez quando o jogador da vez nesta faixa vai decidir."""
            if indice[f] >= len(ordem[f]):
                return None
            d = tempo_decisao(rng, janela=janela)
            return (relogio[f] + min(d, janela), f, ordem[f][indice[f]], d > janela)

        pendente = [proximo(f) for f in range(faixas)]
        while any(p is not None for p in pendente):
            # a faixa cujo jogador decide primeiro
            quando, f, jog, esgotou = min(p for p in pendente if p is not None)
            if esgotou:
                esgotados += 1
                escolhida = max(livres[tipo], key=lambda h: pools[tipo][h]["pop"])
            else:
                # o jogador viu o pool como estava "latencia" segundos antes
                visto = set(livres[tipo]) | {h for (tq, h) in escolhas_recentes if tq > quando - latencia}
                escolhida = next(h for h in prefs[tipo][jog] if h in visto)
                if escolhida not in livres[tipo]:
                    corridas += 1
                    quando += 1.5  # recusada: escolhe de novo
                    escolhida = next(h for h in prefs[tipo][jog] if h in livres[tipo])
            livres[tipo].discard(escolhida)
            escolhas_recentes.append((quando, escolhida))
            pos.append(posicao(prefs[tipo][jog], escolhida, inicio_rodada))
            relogio[f] = quando + entre_escolhas
            indice[f] += 1
            pendente[f] = proximo(f)
        t = max(relogio) + entre_rodadas
    return t, pos, corridas, esgotados


def simular_B(rng, jogadores=20, janela=12.0, revelar=3.0, previa=10.0, k=3, pool_ult=32, pool_bas=96):
    pools = {"ult": criar_pool(pool_ult, rng), "bas": criar_pool(pool_bas, rng)}
    js = [{"arq": rng.randrange(ARQUETIPOS)} for _ in range(jogadores)]
    prefs = {t: [preferencias(j, pools[t], rng) for j in js] for t in pools}
    livres = {t: set(h["id"] for h in pools[t]) for t in pools}
    t = previa
    pos, esgotados = [], 0
    prioridade = list(range(jogadores))
    rng.shuffle(prioridade)
    for r, (tipo, _) in enumerate(rodadas(pool_ult, pool_bas)):
        inicio_rodada = set(livres[tipo])
        tempos = [tempo_decisao(rng, mediana=6.0, janela=janela) for _ in range(jogadores)]  # montar uma lista de 3 leva mais
        t += min(max(tempos), janela) + revelar
        ordem = prioridade if r % 2 == 0 else list(reversed(prioridade))
        for jog in ordem:
            if tempos[jog] > janela:
                esgotados += 1
                lista = []
            else:
                lista = [h for h in prefs[tipo][jog] if h in inicio_rodada][:k]
            escolhida = next((h for h in lista if h in livres[tipo]), None)
            if escolhida is None and lista:
                # perdeu as k: a UI mostra o que sobrou e o jogador escolhe de novo (já está no tempo de revelar)
                escolhida = next(h for h in prefs[tipo][jog] if h in livres[tipo])
            elif escolhida is None:  # tempo esgotado: o servidor escolhe a mais popular que sobrou
                escolhida = max(livres[tipo], key=lambda h: pools[tipo][h]["pop"])
            livres[tipo].discard(escolhida)
            pos.append(posicao(prefs[tipo][jog], escolhida, inicio_rodada))
    return t, pos, 0, esgotados


def simular_C(rng, jogadores=20, janela=8.0, entre_escolhas=0.5, previa=10.0, pool_ult=32, pool_bas=96):
    return simular_A(rng, jogadores=jogadores, faixas=1, janela=janela, entre_escolhas=entre_escolhas, previa=previa,
                     pool_ult=pool_ult, pool_bas=pool_bas)


def resumo(nome, resultados):
    dur = sorted(r[0] for r in resultados)
    pos = [p for r in resultados for p in r[1]]
    primeira = sum(1 for p in pos if p == 1) / len(pos)
    p90 = dur[int(0.9 * (len(dur) - 1))]
    corr = statistics.mean(r[2] for r in resultados)
    esg = statistics.mean(r[3] for r in resultados)
    print(f"{nome:<44} {statistics.mean(dur) / 60:5.2f} min  p90 {p90 / 60:5.2f} min  "
          f"favorita {primeira * 100:5.1f}%  posição média {statistics.mean(pos):5.2f}  "
          f"corridas {corr:4.2f}  esgotados {esg:4.2f}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rng = random.Random(20261015)
    print(f"{n} drafts por formato, 20 jogadores, pool 32 ultimates + 96 básicas (1,6×)\n")
    resumo("A  serpente em 4 faixas (janela 8 s)", [simular_A(rng) for _ in range(n)])
    resumo("A' serpente em 4 faixas (janela 6 s)", [simular_A(rng, janela=6.0) for _ in range(n)])
    resumo("A5 serpente em 5 faixas de 4 (janela 8 s)", [simular_A(rng, faixas=5) for _ in range(n)])
    resumo("B  reserva simultânea, top 3 (janela 12 s)", [simular_B(rng) for _ in range(n)])
    resumo("C  serpente sequencial, 1 por vez (8 s)", [simular_C(rng) for _ in range(n)])
    print("\nFatia vertical: 4 jogadores, pool de desenvolvimento 7 ultimates + 14 básicas (GDD v2)\n")
    resumo("A  1 faixa de 4 (janela 8 s)",
           [simular_A(rng, jogadores=4, faixas=1, pool_ult=7, pool_bas=14) for _ in range(n)])
    resumo("B  reserva simultânea (janela 12 s)",
           [simular_B(rng, jogadores=4, pool_ult=7, pool_bas=14) for _ in range(n)])


if __name__ == "__main__":
    main()
