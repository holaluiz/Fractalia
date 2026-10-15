"""Island terrain + gameplay layout for Nexus Royale."""
import json
import math
import os
import random
import sys

import bpy
from mathutils import Vector, noise

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nexus_lib import collection, mat, srgb  # noqa: E402

SIZE = 400.0          # meters
STEP = 2.5            # grid spacing
MAP_OFFSET = (0.0, 420.0, 0.0)   # where the island sits in the .blend (export moves it back to 0)
NEXUS = (0.0, 0.0)
TOWERS = {"Torre_Norte": (0.0, 95.0), "Torre_Leste": (95.0, 0.0), "Torre_Sul": (0.0, -95.0),
          "Torre_Oeste": (-95.0, 0.0)}
NEXUS_H = 7.0
# points of interest (flattened plazas) and jungle creep camps, island-local meters (Blender axes)
POIS = {"Vila": (-60.0, 55.0, 30.0), "Cidade": (60.0, -55.0, 36.0)}
CAMPS = [(30.0, 48.0), (62.0, 22.0), (-30.0, -48.0), (-62.0, -22.0), (-50.0, 15.0), (50.0, -15.0)]
# Unreal meshes (Quaternius Stylized Nature MegaKit) used for each scatter type
NATURE = {
    "tree": ["CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5",
             "Pine_1", "Pine_2", "Pine_3", "Pine_4", "Pine_5", "CommonTree_2", "Pine_3"],
    "tree_landmark": ["TwistedTree_1", "TwistedTree_2", "TwistedTree_3"],
    "dead_tree": ["DeadTree_1", "DeadTree_2", "DeadTree_3"],
    "rock": ["Rock_Medium_1", "Rock_Medium_2", "Rock_Medium_3"],
    "bush": ["Bush_Common", "Bush_Common_Flowers"],
    "grass": ["Grass_Common_Short", "Grass_Common_Tall", "Grass_Wispy_Short", "Grass_Wispy_Tall"],
    "flower": ["Flower_3_Group", "Flower_4_Group", "Flower_3_Single", "Flower_4_Single"],
    "fern": ["Fern_1"],
    "plant": ["Plant_1_Big", "Plant_7_Big", "Plant_1"],
    "mushroom": ["Mushroom_Common", "Mushroom_Laetiporus"],
}


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def fbm(x, y, z=0.0, octaves=4):
    v, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        v += amp * noise.noise(Vector((x * freq, y * freq, z)))
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return v / norm


def raw_height(x, y):
    d = math.hypot(x, y) / 175.0 + fbm(x / 70.0, y / 70.0, 3.7, 3) * 0.22
    island = 1.0 - smoothstep(0.6, 1.0, d)
    hills = fbm(x / 85.0 + 11.3, y / 85.0 - 4.2, 0.5, 4) * 0.5 + 0.5
    mountain = max(0.0, 1.0 - math.hypot(x - 85.0, y - 70.0) / 65.0) ** 2 * 24.0
    ridge = max(0.0, 1.0 - math.hypot(x + 90.0, y + 80.0) / 45.0) ** 2 * 10.0
    return island * (2.5 + hills * 9.0 + mountain + ridge) - (1.0 - island) * 8.0


PADS = [(NEXUS[0], NEXUS[1], NEXUS_H, 24.0)] + \
       [(x, y, max(3.0, raw_height(x, y)), 10.0) for x, y in TOWERS.values()] + \
       [(x, y, max(3.0, raw_height(x, y)), r) for x, y, r in POIS.values()] + \
       [(x, y, max(3.0, raw_height(x, y)), 7.0) for x, y in CAMPS]


def height(x, y):
    h = raw_height(x, y)
    for px, py, ph, r in PADS:
        t = smoothstep(r, r * 1.8, math.hypot(x - px, y - py))
        h = ph + (h - ph) * t
    return h


def pad_dist(x, y):
    return min(math.hypot(x - px, y - py) - r for px, py, _, r in PADS)


def build_island(coll):
    n = int(SIZE / STEP) + 1
    half = SIZE / 2
    verts, faces = [], []
    for j in range(n):
        for i in range(n):
            x, y = -half + i * STEP, -half + j * STEP
            verts.append((x, y, height(x, y)))
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            faces.append((a, a + 1, a + n + 1, a + n))
    me = bpy.data.meshes.new("SM_Island")
    me.from_pydata(verts, [], faces)
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (co.x / 8.0, co.y / 8.0)
    # vertex colors: sand / grass / rock / stone pads
    col = me.color_attributes.new("Col", "BYTE_COLOR", "POINT")
    pal = {k: srgb(v) for k, v in {"wet": "#C2A86E", "sand": "#E6D29A", "grass": "#6DBE45", "grass2": "#4E9A35",
                                     "rock": "#8C8A85", "pad": "#B8B2A6"}.items()}
    from mathutils import Color  # noqa: F401
    for v in me.vertices:
        x, y, h = v.co
        nz = v.normal.z
        if h < -0.5:
            c = pal["wet"]
        elif h < 1.6:
            c = pal["sand"]
        elif nz < 0.8 or h > 21.0:
            c = pal["rock"]
        elif pad_dist(x, y) < -2.0:
            c = pal["pad"]
        else:
            t = fbm(x / 25.0, y / 25.0, 9.1, 2) * 0.5 + 0.5
            c = tuple(a + (b - a) * t for a, b in zip(pal["grass"], pal["grass2"]))
        col.data[v.index].color = (*c, 1.0)
    me.color_attributes.active_color = col
    try:
        me.color_attributes.render_color_index = me.color_attributes.active_color_index
    except Exception:
        pass
    m = mat("M_Island", "#6DBE45", 0.9)
    nt = m.node_tree
    bsdf = next(nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED")
    if not any(nd.type == "VERTEX_COLOR" for nd in nt.nodes):
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Col"
        nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("SM_Island", me)
    coll.objects.link(ob)
    return ob


def scatter():
    """Deterministic gameplay layout in island-local meters."""
    rnd = random.Random(2026)
    placed = []  # (x, y, clearance radius, kind)

    def ok(x, y, kind, min_d, clear):
        for (px, py, pc, pk) in placed:
            need = clear + pc
            if pk == kind:
                need = max(need, min_d)
            if math.hypot(x - px, y - py) < need:
                return False
        return True

    def slope(x, y):
        e = 1.0
        dx = height(x + e, y) - height(x - e, y)
        dy = height(x, y + e) - height(x, y - e)
        return math.hypot(dx, dy) / (2 * e)

    items = []

    def place(kind, mesh, count, min_d, clear=1.5, hmin=2.2, hmax=20.0, smax=0.45, pad_clear=6.0,
              scale=(1.0, 1.0), yaw=True, z_off=0.0, tries=40000, ue=None):
        got = 0
        for _ in range(tries):
            if got >= count:
                break
            x, y = rnd.uniform(-170, 170), rnd.uniform(-170, 170)
            h = height(x, y)
            if not (hmin <= h <= hmax) or slope(x, y) > smax or pad_dist(x, y) < pad_clear:
                continue
            if not ok(x, y, kind, min_d, clear):
                continue
            s = rnd.uniform(*scale)
            r = rnd.uniform(0, 360) if yaw else 0.0
            placed.append((x, y, clear, kind))
            m = mesh if isinstance(mesh, str) or mesh is None else rnd.choice(mesh)
            item = dict(type=kind, mesh=m, loc=(round(x, 2), round(y, 2), round(h + z_off, 2)),
                        yaw=round(r, 1), scale=round(s, 2))
            if ue:
                item["ue_mesh"] = rnd.choice(ue)
            items.append(item)
            got += 1

    items.append(dict(type="nexus", mesh="SM_Nexus", loc=(NEXUS[0], NEXUS[1], NEXUS_H), yaw=0.0, scale=1.0))
    placed.append((NEXUS[0], NEXUS[1], 24.0, "nexus"))
    items.append(dict(type="guardian_spawn", mesh="SK_Guardian", loc=(0.0, -9.0, NEXUS_H + 2.0), yaw=0.0, scale=1.0))
    for name, (x, y) in TOWERS.items():
        h = height(x, y)
        items.append(dict(type="capture_tower", name=name, mesh="SM_CaptureTower", loc=(x, y, round(h, 2)),
                          yaw=0.0, scale=1.0))
        placed.append((x, y, 12.0, "tower"))
    for name, (x, y, r) in POIS.items():
        items.append(dict(type="poi", name=name, mesh=None, loc=(x, y, round(height(x, y), 2)), yaw=0.0, scale=1.0,
                          radius=r))
        placed.append((x, y, r, "poi"))
    for i, (x, y) in enumerate(CAMPS):
        h = round(height(x, y), 2)
        items.append(dict(type="creep_camp", name=f"Acampamento_{i + 1}", mesh=None, loc=(x, y, h), yaw=0.0, scale=1.0,
                          radius=7.0))
        placed.append((x, y, 7.0, "camp"))
        for k in range(2):  # spooky dead trees framing each camp
            a = math.radians(rnd.uniform(0, 360))
            d = rnd.uniform(9.0, 12.0)
            tx, ty = x + d * math.cos(a), y + d * math.sin(a)
            items.append(dict(type="dead_tree", mesh="SM_Tree_Round", ue_mesh=rnd.choice(NATURE["dead_tree"]),
                              loc=(round(tx, 2), round(ty, 2), round(height(tx, ty), 2)), yaw=round(rnd.uniform(0, 360), 1),
                              scale=round(rnd.uniform(0.7, 0.9), 2)))
            placed.append((tx, ty, 3.0, "dead_tree"))
    place("launch_pad", "SM_LaunchPad", 8, 45.0, clear=3.0, pad_clear=4.0, smax=0.2, yaw=False)
    place("chest", "SM_Chest", 32, 22.0, clear=2.0, pad_clear=2.0, smax=0.3)
    place("essence_shard", "SM_EssenceShard", 60, 12.0, clear=1.0, pad_clear=1.0, smax=0.5, z_off=0.6, yaw=False)
    place("potion", ["SM_Potion_Health", "SM_Potion_Shield"], 30, 15.0, clear=1.0, pad_clear=1.0, smax=0.5,
          z_off=0.4)
    place("rock", ["SM_Rock_01", "SM_Rock_02"], 70, 9.0, clear=3.5, hmin=1.0, hmax=30.0, smax=1.2, scale=(0.7, 1.4),
          ue=NATURE["rock"])
    place("tree_landmark", "SM_Tree_Round", 6, 60.0, clear=7.0, pad_clear=10.0, scale=(0.9, 1.1),
          ue=NATURE["tree_landmark"])
    place("tree", ["SM_Tree_Pine", "SM_Tree_Pine", "SM_Tree_Round"], 280, 6.0, clear=2.5, scale=(0.8, 1.25),
          ue=NATURE["tree"])
    place("bush", "SM_Bush", 120, 4.0, clear=1.5, scale=(0.8, 1.3), ue=NATURE["bush"])
    place("fern", None, 30, 14.0, clear=3.5, pad_clear=3.0, scale=(0.5, 0.8), ue=NATURE["fern"])
    place("plant", None, 80, 5.0, clear=1.0, pad_clear=2.0, scale=(0.8, 1.2), ue=NATURE["plant"])
    place("flower", None, 160, 3.0, clear=0.6, pad_clear=1.0, scale=(0.8, 1.2), ue=NATURE["flower"])
    place("grass", None, 420, 2.2, clear=0.5, pad_clear=1.0, scale=(0.8, 1.3), ue=NATURE["grass"])
    place("mushroom", None, 50, 4.0, clear=0.5, pad_clear=2.0, scale=(0.8, 1.4), ue=NATURE["mushroom"])
    place("crate", "SM_Crate", 25, 12.0, clear=1.5, smax=0.3, scale=(1.0, 1.0))
    return items


def to_ue(item):
    x, y, z = item["loc"]
    out = dict(item)
    out["ue_location_cm"] = (round(x * 100, 1), round(-y * 100, 1), round(z * 100, 1))
    out["ue_yaw"] = round(-item["yaw"], 1)
    return out


def write_layout(items, path):
    data = {
        "map": "SM_Island",
        "units": "loc in meters (Blender, island-local); ue_location_cm in Unreal units",
        "storm": {"center_cm": [0, 0, 0], "start_radius_cm": 18000, "phases": [
            {"wait_s": 60, "shrink_s": 60, "end_radius_cm": 12000, "dps": 1},
            {"wait_s": 50, "shrink_s": 50, "end_radius_cm": 7500, "dps": 2},
            {"wait_s": 45, "shrink_s": 45, "end_radius_cm": 4500, "dps": 5},
            {"wait_s": 40, "shrink_s": 40, "end_radius_cm": 2500, "dps": 8},
            {"wait_s": 30, "shrink_s": 30, "end_radius_cm": 1000, "dps": 10},
            {"wait_s": 20, "shrink_s": 60, "end_radius_cm": 0, "dps": 10}]},
        "drop_ship_path_cm": [[-22000, 14000, 9000], [22000, -14000, 9000]],
        "actors": [to_ue(i) for i in items],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def preview_scatter(island, items, coll):
    """Linked-duplicate instances of the props on the island (preview only, not exported)."""
    for i, it in enumerate(items):
        if not it.get("mesh"):
            continue
        src = bpy.data.objects.get(it["mesh"])
        if src is None or src.type != "MESH" or it["type"] == "guardian_spawn":
            continue
        ob = bpy.data.objects.new(f"MAP_{it['type']}_{i:03d}", src.data)
        coll.objects.link(ob)
        ob.location = it["loc"]
        ob.rotation_euler = (0, 0, math.radians(it["yaw"]))
        ob.scale = (it["scale"],) * 3
        ob.parent = island
    for k, (name, y) in enumerate((("SM_DropShip", 0.0),)):
        src = bpy.data.objects.get(name)
        if src:
            ob = bpy.data.objects.new("MAP_DropShip", src.data)
            coll.objects.link(ob)
            ob.location = (-60.0, 40.0, 70.0)
            ob.rotation_euler = (0, 0, math.radians(-120))
            ob.scale = (2.0, 2.0, 2.0)
            ob.parent = island


def build_all(layout_path):
    root = collection("Map")
    coll = collection("Prop_SM_Island", root)
    island = build_island(coll)
    island.location = MAP_OFFSET
    coll["layout_offset"] = MAP_OFFSET
    items = scatter()
    write_layout(items, layout_path)
    scat = collection("Map_PreviewScatter", root)
    preview_scatter(island, items, scat)
    return island, items
