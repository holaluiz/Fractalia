"""Grava, quadro a quadro, o que acontece no PIE: vida dos creeps e do herói, posição dos creeps em relação à muralha,
estruturas mágicas, Chuvas de Meteoros e projéteis (onde nasceram e onde sumiram). Serve para ver coisas mais rápidas que uma chamada do Python remoto (os pulsos de 0,5 s
do chão em chamas, um creep encostando na muralha).

Uso:  python ue_py.py -c "ACT='iniciar'; SEG=8; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_gravar.py', encoding='utf-8').read())"
ACT:  iniciar   começa a gravar por SEG segundos de jogo (padrão 8). A posição sai a cada PASSO s (padrão 0,25);
                a vida, a cada mudança
      mostrar   imprime o que foi gravado até agora (e se ainda está gravando)
      parar     para antes do fim
Os tempos são do relógio do jogo (respeitam a dilatação de tempo), contados a partir do "iniciar".
Roda num callback de pós-tick do Slate: o Python remoto roda na thread do jogo, então não pode esperar lá dentro
sem travar o frame. O estado fica no módulo "_pie_gravar" (sobrevive entre chamadas e à troca de globais).
"""
import math
import sys
import types

import unreal

ACT = globals().get("ACT", "mostrar")
# Lidas e apagadas no início: o Python remoto guarda as globais entre chamadas.
OPCOES = {k: globals().pop(k) for k in ("SEG", "PASSO") if k in globals()}

G = sys.modules.get("_pie_gravar")
if G is None:
    G = types.ModuleType("_pie_gravar")
    G.handle = None
    G.linhas = []
    sys.modules["_pie_gravar"] = G


def _parar(motivo):
    if G.handle is not None:
        unreal.unregister_slate_post_tick_callback(G.handle)
        G.handle = None
        G.linhas.append("-- fim da gravação: %s" % motivo)


def _relativo_muralha(loc, estruturas):
    """Distância à frente/atrás do plano da estrutura mais perto (sinal = lado) e deslocamento ao longo dela, em m."""
    if not estruturas:
        return ""
    e = min(estruturas, key=lambda a: (a.get_actor_location() - loc).length())
    d = loc - e.get_actor_location()
    f, r = e.get_actor_forward_vector(), e.get_actor_right_vector()
    return " | muralha: frente %+.2f m, lado %+.2f m" % ((d.x * f.x + d.y * f.y) / 100.0, (d.x * r.x + d.y * r.y) / 100.0)


def _tick(_dt):
    try:
        w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        if w is None:
            _parar("o PIE acabou")
            return
        t = unreal.GameplayStatics.get_time_seconds(w) - G.t0
        G.quadros += 1
        estruturas = list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.NREstruturaMagica))
        chuvas = list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.NRChuvaMeteoros))
        creeps = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
                  if a.get_class().get_name().startswith("BP_Creep_")]

        for c in creeps:
            nome, hp = c.get_name(), c.get_editor_property("Health")
            antes = G.vida.get(nome)
            if antes is not None and abs(hp - antes) > 0.01:
                G.linhas.append("%6.2f  %s vida %.1f -> %.1f (%+.1f)%s" % (
                    t, nome, antes, hp, hp - antes, "  MORREU" if c.get_editor_property("IsDead") else ""))
            G.vida[nome] = hp
        asc = G.heroi.get_component_by_class(unreal.NRAbilitySystemComponent)
        vida_heroi = asc.get_vida() if asc else -1.0
        if G.vida_heroi is not None and abs(vida_heroi - G.vida_heroi) > 0.01:
            G.linhas.append("%6.2f  HERÓI vida %.1f -> %.1f (%+.1f)" % (t, G.vida_heroi, vida_heroi, vida_heroi - G.vida_heroi))
        G.vida_heroi = vida_heroi
        for e in estruturas:
            nome, vida = e.get_name(), e.get_editor_property("Vida")
            if nome not in G.estr:
                G.linhas.append("%6.2f  %s apareceu, vida %.0f, a %.1f m do herói" % (
                    t, nome, vida, (e.get_actor_location() - G.heroi.get_actor_location()).length() / 100.0))
            elif abs(vida - G.estr[nome]) > 0.01:
                G.linhas.append("%6.2f  %s vida %.0f -> %.0f" % (t, nome, G.estr[nome], vida))
            G.estr[nome] = vida
        for nome in [n for n in G.estr if n not in {e.get_name() for e in estruturas}]:
            G.linhas.append("%6.2f  %s sumiu" % (t, nome))
            del G.estr[nome]
        for ch in chuvas:
            nome, alvos = ch.get_name(), ch.alvos_atingidos()
            if nome not in G.chuvas:
                G.linhas.append("%6.2f  %s apareceu em %s" % (t, nome, ch.get_actor_location()))
            elif alvos != G.chuvas[nome]:
                G.linhas.append("%6.2f  %s alvos atingidos %d -> %d" % (t, nome, G.chuvas[nome], alvos))
            G.chuvas[nome] = alvos
        for nome in [n for n in G.chuvas if n not in {c.get_name() for c in chuvas}]:
            G.linhas.append("%6.2f  %s sumiu" % (t, nome))
            del G.chuvas[nome]
        # Projéteis: onde nasceram e o último ponto visto (depois de explodir, o projétil fica 0,15 s parado no ponto da explosão).
        projeteis = list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.NRProjetilMagico))
        for p in projeteis:
            loc = p.get_actor_location()
            if p.get_name() not in G.proj:
                G.linhas.append("%6.2f  %s nasceu em (%.0f, %.0f, %.0f)%s" % (t, p.get_name(), loc.x, loc.y, loc.z, _relativo_muralha(loc, estruturas)))
            G.proj[p.get_name()] = (loc, _relativo_muralha(loc, estruturas))
        for nome in [n for n in G.proj if n not in {p.get_name() for p in projeteis}]:
            loc, rel = G.proj.pop(nome)
            G.linhas.append("%6.2f  %s sumiu; último ponto (%.0f, %.0f, %.0f)%s" % (t, nome, loc.x, loc.y, loc.z, rel))

        if t >= G.proxima_pos:
            G.proxima_pos += G.passo
            h = G.heroi.get_actor_location()
            for c in creeps:
                if c.get_editor_property("IsDead"):
                    continue
                loc = c.get_actor_location()
                alvo = c.get_editor_property("Target")
                G.linhas.append("%6.2f  .. %s em (%.0f, %.0f) andando %s alvo %s, herói a %.1f m, casa a %.1f m%s" % (
                    t, c.get_name(), loc.x, loc.y, c.get_editor_property("bMoving"), alvo.get_name() if alvo else "-",
                    math.dist((loc.x, loc.y), (h.x, h.y)) / 100.0,
                    math.dist((loc.x, loc.y), (c.get_editor_property("HomeLocation").x, c.get_editor_property("HomeLocation").y)) / 100.0,
                    _relativo_muralha(loc, estruturas)))
        if t >= G.seg:
            _parar("%.1f s de jogo, %d quadros (%.1f por segundo de jogo)" % (G.seg, G.quadros, G.quadros / max(t, 1e-3)))
    except Exception as erro:  # noqa: BLE001 - um erro no callback repetiria a cada frame
        G.linhas.append("ERRO no gravador: %r" % (erro,))
        _parar("erro")


if ACT == "iniciar":
    _parar("reiniciada")
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    G.heroi = unreal.GameplayStatics.get_player_controller(w, 0).get_controlled_pawn()
    G.t0 = unreal.GameplayStatics.get_time_seconds(w)
    G.seg = float(OPCOES.get("SEG", 8.0))
    G.passo = float(OPCOES.get("PASSO", 0.25))
    G.proxima_pos = 0.0
    G.quadros = 0
    G.vida_heroi = None
    G.linhas, G.vida, G.estr, G.chuvas, G.proj = ["-- gravando %.1f s (relógio do jogo em %.2f)" % (G.seg, G.t0)], {}, {}, {}, {}
    G.handle = unreal.register_slate_post_tick_callback(_tick)
    print("gravando por %.1f s de jogo" % G.seg)
elif ACT == "parar":
    _parar("pedido")
if ACT in ("mostrar", "parar"):
    print("\n".join(G.linhas) if G.linhas else "nada gravado")
    print("ainda gravando" if G.handle is not None else "parado")
