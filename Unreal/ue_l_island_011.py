"""L_Island para a 0.1.1 (PLANO.md, itens 1.5 e 1.6). Roda no editor aberto, fora do PIE:

    python Unreal/ue_py.py -c "ACT='v1'; exec(open(r'D:/meus documentos/Fortnite/Unreal/ue_l_island_011.py', encoding='utf-8').read())"

ACT:
  'v1'          lista os atores da v1 (Nexus, torres, fragmentos SM_EssenceShard, poções de escudo e de vida decorativas,
                plataformas de salto, os heróis antigos na praça) pelo rótulo, pela classe e pela malha. Não apaga nada.
                Os caixotes (SM_Crate) ficam: servem de cobertura.
  'apagar_v1'   apaga os mesmos atores e salva o nível.
  'clareiras'   procura pontos de chão plano sem nada em volta (o creep anda em linha reta, sem NavMesh) e imprime
                um JSON pronto para Unreal/Data/Camps_L_Island.json. Opções: RAIO (cm livres em volta, 800),
                N (quantos, 8), DIST (distância mínima entre eles, 6000) e MANTER (lista de [x, y] que ficam).
"""
import json
import math
import re

import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
LEVEL = "/Game/NexusRoyale/Maps/L_Island"

_g = globals()
ACT = _g.pop("ACT", "v1")
RAIO = float(_g.pop("RAIO", 800.0))
N = int(_g.pop("N", 8))
DIST = float(_g.pop("DIST", 6000.0))
MANTER = _g.pop("MANTER", [])

# O que é da v1 (GDD §16.1, "Remover"). Casa com rótulo, classe ou malha.
V1 = re.compile(r"Nexus(?!Royale)|Tower|Torre|Fragment|Fragmento|EssenceShard|Potion_Health|Shield|Escudo|JumpPad|Jump_Pad|LaunchPad|Plataforma"
                r"|Statue|Estatua|Guardian|Brakka|Lumi|Vela|Zephyr|Boto|Caramelo|PombaGira|Pomba_Gira|BP_Hero_", re.I)
# Nunca apagar: o jogo atual.
MANTEM = re.compile(r"BP_HeroBase|GM_Nexus|HUD_Nexus|NexusRoyale/Blueprints/(Core|Match|Loot|Creeps)|PlayerStart", re.I)


def carregar():
    if les.get_current_level().get_outermost().get_name() != LEVEL:
        les.load_level(LEVEL)
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def descrever(a):
    partes = [a.get_actor_label(), a.get_class().get_path_name()]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if m:
            partes.append(m.get_path_name())
    return partes


def atores_v1():
    achados = []
    for a in eas.get_all_level_actors():
        partes = descrever(a)
        texto = " ".join(partes)
        if MANTEM.search(texto):
            continue
        if V1.search(texto):
            achados.append((a, partes))
    return achados


def clareiras(world):
    # Caixas (no plano) do que bloqueia o creep: malhas com colisão que não são chão. Grama, flores e arbustos não
    # têm colisão (o creep passa); pisos, ruas e decalques são rasos (o teste de plano cuida do desnível).
    caixas = []
    for a in eas.get_all_level_actors():
        comps = a.get_components_by_class(unreal.StaticMeshComponent)
        if not comps:
            continue
        if all(c.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION for c in comps):
            continue
        origem, ext = a.get_actor_bounds(False)
        if ext.x > 15000 or ext.y > 15000:  # a ilha (o chão)
            continue
        if ext.z < 60:  # pisos, ruas, decalques
            continue
        caixas.append((origem.x, origem.y, ext.x, ext.y, a.get_actor_label()))
    print("obstáculos considerados:", len(caixas))

    def livre(x, y):
        for (ox, oy, ex, ey, _) in caixas:
            dx = max(abs(x - ox) - ex, 0.0)
            dy = max(abs(y - oy) - ey, 0.0)
            if dx * dx + dy * dy < RAIO * RAIO:
                return False
        return True

    def plano(x, y):
        zs = []
        for (dx, dy) in ((0, 0), (RAIO * 0.6, 0), (-RAIO * 0.6, 0), (0, RAIO * 0.6), (0, -RAIO * 0.6)):
            hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x + dx, y + dy, 30000.0),
                                                         unreal.Vector(x + dx, y + dy, -5000.0),
                                                         unreal.TraceTypeQuery.ECC_VISIBILITY, False, [],
                                                         unreal.DrawDebugTrace.NONE, True)
            t = hit.to_tuple()
            if not t[0]:
                return None
            zs.append(t[4].z)
        if max(zs) - min(zs) > 120:  # mais de 1,2 m de desnível em ~5 m: encosta
            return None
        return zs[0]

    candidatos = []
    passo = 1000.0
    lim = 19000.0
    y = -lim
    while y <= lim:
        x = -lim
        while x <= lim:
            if livre(x, y):
                z = plano(x, y)
                if z is not None and z > 50.0:  # acima do nível do mar
                    candidatos.append((x, y, z))
            x += passo
        y += passo
    print("pontos livres e planos:", len(candidatos))

    escolhidos = [(float(p[0]), float(p[1]), None) for p in MANTER]
    # Espalha: sempre o candidato mais longe de todos os já escolhidos (e longe do centro da praça no começo).
    while len(escolhidos) < N and candidatos:
        melhor, md = None, -1.0
        for c in candidatos:
            d = min((math.hypot(c[0] - e[0], c[1] - e[1]) for e in escolhidos), default=math.hypot(c[0], c[1]))
            if d > md:
                melhor, md = c, d
        if md < DIST and escolhidos:
            break
        escolhidos.append(melhor)
        candidatos.remove(melhor)
    saida = [{"x": round(e[0]), "y": round(e[1]), "z": round(e[2]) if e[2] is not None else 700} for e in escolhidos]
    print(json.dumps(saida))
    return saida


world = carregar()
if ACT == "v1":
    for a, partes in atores_v1():
        print("v1:", " | ".join(partes))
elif ACT == "apagar_v1":
    lista = atores_v1()
    for a, partes in lista:
        print("apagando:", partes[0])
        eas.destroy_actor(a)
    les.save_current_level()
    print("apagados:", len(lista))
elif ACT == "clareiras":
    clareiras(world)
else:
    print("ACT desconhecido:", ACT)
