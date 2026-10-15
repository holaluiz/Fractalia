"""Static props for Nexus Royale: build pieces (with UCX collision), loot, nature, objectives."""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nexus_lib import Kit, bm_cone, bm_convex, bm_lathe, bm_tube, collection, make_obj, mat, trs  # noqa: E402

V = Vector
GRID, WALL_H = 5.12, 3.84


# ------------------------------------------------------------------ helpers

def ucx_box(center, size, rot=(0, 0, 0)):
    m = trs(center, rot)
    hx, hy, hz = (s / 2 for s in size)
    pts = [m @ V((x, y, z)) for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
    return bm_convex(pts)


def ucx_cyl(center_bottom, r, h, segs=12):
    c = V(center_bottom)
    pts = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        for z in (0, h):
            pts.append(c + V((r * math.cos(a), r * math.sin(a), z)))
    return bm_convex(pts)


def finish_prop(k, name, coll, offset, ucx=None, hull=False):
    obj = k.finish(name)
    shapes = list(ucx or [])
    if hull:
        shapes.append(bm_convex([v.co.copy() for v in obj.data.vertices]))
    for i, bm in enumerate(shapes):
        u = make_obj(f"UCX_{name}_{i:02d}", bm, None, coll, smooth=False, uv=False)
        u.display_type = "WIRE"
        u.hide_render = True
        u.location = V(offset)
    obj.location = V(offset)
    coll["layout_offset"] = tuple(offset)
    return obj


def M():
    return {
        "wood": mat("M_Build_Wood", "#C08A52", 0.8),
        "wood_dark": mat("M_Build_WoodDark", "#7A5230", 0.8),
        "bark": mat("M_Bark", "#6B4423", 0.9),
        "gold": mat("M_Gold", "#E8B04A", 0.3, 0.9),
        "chest_wood": mat("M_Chest_Wood", "#8A5A2E", 0.7),
        "dark": mat("M_Dark", "#1E1B1A", 0.8),
        "stone": mat("M_Stone", "#A8A398", 0.85),
        "stone_dark": mat("M_StoneDark", "#6F6A62", 0.9),
        "rock": mat("M_Rock", "#8A8F96", 0.9),
        "rock_dark": mat("M_RockDark", "#6F747B", 0.9),
        "pine": mat("M_Leaves_Pine", "#2F7D3B", 0.85),
        "pine2": mat("M_Leaves_Pine2", "#3C9446", 0.85),
        "leaf": mat("M_Leaves_Round", "#5DAA3C", 0.85),
        "leaf2": mat("M_Leaves_Round2", "#4E9A35", 0.85),
        "metal": mat("M_Metal_Dark", "#3A3F4A", 0.4, 0.7),
        "orange": mat("M_Pad_Orange", "#FF8A1F", 0.5),
        "chevron": mat("M_Pad_Glow", "#FFE14D", 0.3, emit="#FFE14D", emit_strength=1.5),
        "glass": mat("M_Glass", "#DDEEFF", 0.05),
        "cork": mat("M_Cork", "#A0703F", 0.9),
        "hp": mat("M_Potion_Health", "#FF3B5C", 0.2, emit="#FF3B5C", emit_strength=2.0),
        "shield": mat("M_Potion_Shield", "#3BA7FF", 0.2, emit="#3BA7FF", emit_strength=2.0),
        "essence": mat("M_Essence_Glow", "#9B5CFF", 0.2, emit="#B98CFF", emit_strength=2.5),
        "tower_glow": mat("M_Tower_Glow", "#BFEFFF", 0.2, emit="#BFEFFF", emit_strength=2.5),
        "banner": mat("M_Banner_Team", "#E6E1D3", 0.8),
        "nexus_glow": mat("M_Nexus_Glow", "#B26BFF", 0.2, emit="#B26BFF", emit_strength=2.5),
        "storm": mat("M_Storm", "#7B3FE4", 0.5, emit="#7B3FE4", emit_strength=2.0),
        "envelope": mat("M_Ship_Envelope", "#E8E2D0", 0.7),
        "ship_blue": mat("M_Ship_Blue", "#2F5DBA", 0.5),
    }


# ------------------------------------------------------------------ build pieces

def build_wall(root, m, off):
    coll = collection("Prop_SM_Build_Wall", root)
    k = Kit("SM_Build_Wall", coll)
    for sx in (1, -1):
        k.box((sx * (GRID / 2 - 0.12), 0, WALL_H / 2), (0.24, 0.3, WALL_H), m["wood_dark"], bevel_w=0.03)
    rnd = random.Random(3)
    for i in range(4):
        z = 0.48 + i * 0.96
        k.box((0, 0, z), (GRID - 0.48, 0.2, 0.9), m["wood"], rot=(0, rnd.uniform(-0.8, 0.8), 0), bevel_w=0.04)
    ang = math.degrees(math.atan2(WALL_H - 0.5, GRID - 0.6))
    k.box((0, -0.13, WALL_H / 2), (math.hypot(GRID - 0.6, WALL_H - 0.5), 0.08, 0.25), m["wood_dark"],
          rot=(0, -ang, 0), bevel_w=0.02)
    return finish_prop(k, "SM_Build_Wall", coll, off, ucx=[ucx_box((0, 0, WALL_H / 2), (GRID, 0.24, WALL_H))])


def build_floor(root, m, off):
    coll = collection("Prop_SM_Build_Floor", root)
    k = Kit("SM_Build_Floor", coll)
    for sx in (1, -1):
        k.box((sx * (GRID / 2 - 0.35), 0, 0.04), (0.25, GRID, 0.08), m["wood_dark"], bevel_w=0.015)
    n = 6
    w = GRID / n
    rnd = random.Random(5)
    for i in range(n):
        y = -GRID / 2 + w * (i + 0.5)
        k.box((0, y, 0.14), (GRID, w - 0.04, 0.12), m["wood"], rot=(rnd.uniform(-0.5, 0.5), 0, 0), bevel_w=0.03)
    return finish_prop(k, "SM_Build_Floor", coll, off, ucx=[ucx_box((0, 0, 0.1), (GRID, GRID, 0.2))])


def build_ramp(root, m, off):
    coll = collection("Prop_SM_Build_Ramp", root)
    k = Kit("SM_Build_Ramp", coll)
    phi = -math.degrees(math.atan2(WALL_H, GRID))
    length = math.hypot(GRID, WALL_H)
    nrm = V((0, 0.6, 0.8))
    for i in range(8):
        t = (i + 0.5) / 8
        p = V((0, GRID / 2 - GRID * t, WALL_H * t)) - nrm * 0.07
        k.box(p, (GRID - 0.5, length / 8 - 0.05, 0.12), m["wood"], rot=(phi, 0, 0), bevel_w=0.03)
    for sx in (1, -1):
        k.box(V((sx * (GRID / 2 - 0.12), 0, WALL_H / 2)) - nrm * 0.12, (0.22, length, 0.3), m["wood_dark"],
              rot=(phi, 0, 0), bevel_w=0.03)
        k.box((sx * (GRID / 2 - 0.15), -GRID / 2 + 0.2, (WALL_H - 0.2) / 2), (0.22, 0.22, WALL_H - 0.2),
              m["wood_dark"], bevel_w=0.02)
        k.box((sx * (GRID / 2 - 0.15), 0.0, (WALL_H / 2 - 0.2) / 2), (0.22, 0.22, WALL_H / 2 - 0.2),
              m["wood_dark"], bevel_w=0.02)
    h = GRID / 2
    wedge = bm_convex([V((x, y, 0)) for x in (-h, h) for y in (-h, h)] + [V((x, -h, WALL_H)) for x in (-h, h)])
    return finish_prop(k, "SM_Build_Ramp", coll, off, ucx=[wedge])


def build_cone(root, m, off):
    coll = collection("Prop_SM_Build_Cone", root)
    k = Kit("SM_Build_Cone", coll)
    h, top = GRID / 2, 1.92
    corners = [V((x, y, 0)) for x, y in ((-h, -h), (h, -h), (h, h), (-h, h))]
    apex = V((0, 0, top))
    k.convex(corners + [apex, V((0, 0, 0.0))], m["wood"])
    for c in corners:
        k.tube([c + V((0, 0, 0.06)), apex + V((0, 0, 0.06))], 0.1, m["wood_dark"], segs=6)
    for a, b in zip(corners, corners[1:] + corners[:1]):
        k.tube([a + V((0, 0, 0.05)), b + V((0, 0, 0.05))], 0.09, m["wood_dark"], segs=6)
    for i in range(1, 4):
        t = i / 4
        ring = [c.lerp(apex, t) + V((0, 0, 0.04)) for c in corners]
        for a, b in zip(ring, ring[1:] + ring[:1]):
            k.tube([a, b], 0.04, m["wood_dark"], segs=5)
    return finish_prop(k, "SM_Build_Cone", coll, off, ucx=[bm_convex(corners + [apex])])


# ------------------------------------------------------------------ loot

def build_chest(root, m, off):
    coll = collection("Prop_SM_Chest", root)
    k = Kit("SM_Chest", coll)
    k.box((0, 0, 0.21), (0.9, 0.56, 0.42), m["chest_wood"], bevel_w=0.03)
    k.cyl((-0.45, 0, 0.42), (0.45, 0, 0.42), 0.28, 0.28, m["chest_wood"], segs=20, ref=(0, 0, 1))
    for x in (-0.3, 0.3):
        k.box((x, 0, 0.215), (0.06, 0.585, 0.43), m["gold"], bevel_w=0.01)
        k.cyl((x - 0.03, 0, 0.42), (x + 0.03, 0, 0.42), 0.295, 0.295, m["gold"], segs=20, ref=(0, 0, 1))
    for x in (-0.45, 0.45):
        for y in (-0.28, 0.28):
            k.box((x, y, 0.21), (0.05, 0.05, 0.43), m["gold"], bevel_w=0.008)
    k.box((0, -0.29, 0.42), (0.12, 0.05, 0.14), m["gold"], bevel_w=0.015)
    k.box((0, -0.318, 0.41), (0.025, 0.01, 0.05), m["dark"])
    return finish_prop(k, "SM_Chest", coll, off, ucx=[ucx_box((0, 0, 0.35), (0.92, 0.58, 0.7))])


def build_crate(root, m, off):
    coll = collection("Prop_SM_Crate", root)
    k = Kit("SM_Crate", coll)
    k.box((0, 0, 0.5), (0.94, 0.94, 0.94), m["wood"], bevel_w=0.02)
    e = 0.47
    for a in (-e, e):
        for b in (-e, e):
            k.box((a, b, 0.5), (0.1, 0.1, 1.0), m["wood_dark"], bevel_w=0.015)
            k.box((a, 0, 0.5 + b), (0.1, 1.0, 0.1), m["wood_dark"], bevel_w=0.015)
            k.box((0, a, 0.5 + b), (1.0, 0.1, 0.1), m["wood_dark"], bevel_w=0.015)
    for y in (-0.49, 0.49):
        k.box((0, y, 0.5), (1.1, 0.06, 0.1), m["wood_dark"], rot=(0, 45, 0))
    for x in (-0.49, 0.49):
        k.box((x, 0, 0.5), (0.06, 1.1, 0.1), m["wood_dark"], rot=(45, 0, 0))
    return finish_prop(k, "SM_Crate", coll, off, ucx=[ucx_box((0, 0, 0.5), (1.04, 1.04, 1.04))])


def build_potions(root, m, offs):
    coll = collection("Prop_SM_Potion_Health", root)
    k = Kit("SM_Potion_Health", coll)
    k.lathe([(0, 0), (0.0, 0.07), (0.03, 0.11), (0.1, 0.12), (0.17, 0.09), (0.21, 0.05), (0.22, 0.0)],
            (0, 0, 0), (0, 0, 1), m["hp"], segs=20)
    k.cyl((0, 0, 0.2), (0, 0, 0.29), 0.04, 0.035, m["glass"], segs=14)
    k.cyl((0, 0, 0.28), (0, 0, 0.34), 0.045, 0.04, m["cork"], segs=12)
    k.box((0, -0.112, 0.11), (0.07, 0.01, 0.02), m["glass"])
    k.box((0, -0.112, 0.11), (0.02, 0.01, 0.07), m["glass"])
    a = finish_prop(k, "SM_Potion_Health", coll, offs[0])
    coll = collection("Prop_SM_Potion_Shield", root)
    k = Kit("SM_Potion_Shield", coll)
    k.lathe([(0, 0), (0.0, 0.08), (0.02, 0.09), (0.22, 0.09), (0.26, 0.07), (0.3, 0.035), (0.31, 0.0)],
            (0, 0, 0), (0, 0, 1), m["shield"], segs=20)
    k.cyl((0, 0, 0.29), (0, 0, 0.36), 0.035, 0.035, m["glass"], segs=14)
    k.cyl((0, 0, 0.35), (0, 0, 0.41), 0.045, 0.04, m["cork"], segs=12)
    k.torus((0, 0, 0.16), 0.093, 0.012, m["gold"], segs=24, rsegs=6)
    b = finish_prop(k, "SM_Potion_Shield", coll, offs[1])
    return a, b


def build_shard(root, m, off):
    coll = collection("Prop_SM_EssenceShard", root)
    k = Kit("SM_EssenceShard", coll)
    k.crystal((0, 0, 0.3), 0.11, 0.5, m["essence"], sides=5)
    k.crystal((0.1, 0.04, 0.18), 0.06, 0.26, m["essence"], sides=5, rot=(15, 25, 0))
    k.crystal((-0.09, -0.03, 0.17), 0.05, 0.22, m["essence"], sides=5, rot=(-10, -30, 0))
    return finish_prop(k, "SM_EssenceShard", coll, off)


# ------------------------------------------------------------------ nature

def build_pine(root, m, off):
    coll = collection("Prop_SM_Tree_Pine", root)
    k = Kit("SM_Tree_Pine", coll)
    k.cyl((0, 0, 0), (0, 0, 2.8), 0.34, 0.22, m["bark"], segs=8, smooth=False)
    for z0, r, d, mm, rz in ((1.6, 2.5, 3.2, "pine", 0), (3.2, 2.0, 2.9, "pine2", 20), (4.8, 1.4, 2.6, "pine", 40)):
        bm = bm_cone(r, 0.0, d, segs=9)
        k.raw(bm, m[mm], trs((0, 0, z0 + d / 2), (0, 0, rz)), smooth=False)
    trunk = ucx_cyl((0, 0, 0), 0.34, 2.8, 8)
    return finish_prop(k, "SM_Tree_Pine", coll, off, ucx=[trunk])


def build_round_tree(root, m, off):
    coll = collection("Prop_SM_Tree_Round", root)
    k = Kit("SM_Tree_Round", coll)
    k.cyl((0, 0, 0), (0, 0, 3.2), 0.38, 0.26, m["bark"], segs=8, smooth=False)
    k.tube([(0, 0, 2.2), (0.5, 0.1, 2.9), (0.9, 0.2, 3.3)], [0.14, 0.11, 0.07], m["bark"], segs=6, smooth=False)
    k.tube([(0, 0, 2.5), (-0.5, -0.2, 3.1), (-0.8, -0.3, 3.6)], [0.13, 0.1, 0.06], m["bark"], segs=6, smooth=False)
    blobs = [((0, 0, 4.4), 1.8, "leaf"), ((1.1, 0.3, 3.8), 1.3, "leaf2"), ((-1.1, -0.4, 4.0), 1.35, "leaf2"),
             ((0.3, -1.0, 4.0), 1.2, "leaf"), ((-0.2, 0.9, 4.1), 1.25, "leaf"), ((0.2, 0.1, 5.4), 1.2, "leaf2")]
    for i, (c, r, mm) in enumerate(blobs):
        k.rock(c, (r, r, r * 0.9), m[mm], seed=40 + i, rough=0.08)
    return finish_prop(k, "SM_Tree_Round", coll, off, ucx=[ucx_cyl((0, 0, 0), 0.38, 3.2, 8)])


def build_rocks(root, m, offs):
    coll = collection("Prop_SM_Rock_01", root)
    k = Kit("SM_Rock_01", coll)
    k.rock((0, 0, 0.75), (1.7, 1.35, 1.15), m["rock"], seed=7, rough=0.2)
    k.rock((1.5, -0.6, 0.35), (0.7, 0.6, 0.5), m["rock_dark"], seed=8, rough=0.2)
    a = finish_prop(k, "SM_Rock_01", coll, offs[0], hull=True)
    coll = collection("Prop_SM_Rock_02", root)
    k = Kit("SM_Rock_02", coll)
    k.rock((0, 0, 1.4), (0.9, 0.8, 1.7), m["rock"], seed=11, rough=0.18, rot=(0, 8, 0))
    k.rock((0.9, 0.3, 0.8), (0.7, 0.6, 1.0), m["rock_dark"], seed=12, rough=0.2, rot=(0, -12, 20))
    k.rock((-0.7, -0.5, 0.45), (0.6, 0.55, 0.55), m["rock"], seed=13, rough=0.2)
    b = finish_prop(k, "SM_Rock_02", coll, offs[1], hull=True)
    return a, b


def build_bush(root, m, off):
    coll = collection("Prop_SM_Bush", root)
    k = Kit("SM_Bush", coll)
    for i, (c, r) in enumerate((((0, 0, 0.55), 0.75), ((0.6, 0.2, 0.4), 0.55), ((-0.55, -0.15, 0.4), 0.6),
                                ((0.1, -0.5, 0.35), 0.5), ((-0.1, 0.55, 0.4), 0.5))):
        k.rock(c, (r, r, r * 0.85), m["leaf2" if i % 2 else "leaf"], seed=60 + i, rough=0.1)
    return finish_prop(k, "SM_Bush", coll, off)


# ------------------------------------------------------------------ objectives & gameplay

def build_tower(root, m, off):
    coll = collection("Prop_SM_CaptureTower", root)
    k = Kit("SM_CaptureTower", coll)
    k.cyl((0, 0, 0), (0, 0, 0.5), 2.1, 1.9, m["stone_dark"], segs=12, smooth=False)
    k.cyl((0, 0, 0.5), (0, 0, 0.9), 1.5, 1.4, m["stone"], segs=12, smooth=False)
    bm = bm_cone(0.75, 0.55, 4.1, segs=4)
    k.raw(bm, m["stone"], trs((0, 0, 0.9 + 2.05), (0, 0, 45)), smooth=False)
    k.torus((0, 0, 2.6), 0.78, 0.07, m["gold"], segs=24, rsegs=6)
    k.cyl((0, 0, 5.0), (0, 0, 5.3), 1.0, 1.1, m["stone_dark"], segs=12, smooth=False)
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        d = V((math.cos(a), math.sin(a), 0))
        k.tube([V((0, 0, 5.3)) + d * 0.7, V((0, 0, 5.8)) + d * 0.9, V((0, 0, 6.6)) + d * 0.6, V((0, 0, 7.1)) + d * 0.2],
               [0.08, 0.07, 0.05, 0.02], m["gold"], segs=6)
    k.crystal((0, 0, 6.3), 0.45, 1.5, m["tower_glow"], sides=6)
    for sx in (1, -1):
        k.box((sx * 0.62, 0, 3.4), (0.04, 0.9, 1.8), m["banner"], rot=(0, 0, 0), bevel_w=0.01)
    return finish_prop(k, "SM_CaptureTower", coll, off,
                       ucx=[ucx_cyl((0, 0, 0), 2.1, 0.9, 12), ucx_box((0, 0, 3.1), (1.1, 1.1, 4.4), (0, 0, 45))])


def build_nexus(root, m, off):
    coll = collection("Prop_SM_Nexus", root)
    k = Kit("SM_Nexus", coll)
    ucx = []
    for i, (r, z) in enumerate(((7.0, 0.0), (6.0, 0.4), (5.0, 0.8))):
        k.cyl((0, 0, z), (0, 0, z + 0.4), r, r, m["stone_dark" if i % 2 == 0 else "stone"], segs=24, smooth=False)
        ucx.append(ucx_cyl((0, 0, z), r, 0.4, 16))
    for i in range(6):
        a = 2 * math.pi * i / 6
        p = V((5.4 * math.cos(a), 5.4 * math.sin(a), 0.4))
        k.cyl(p, p + V((0, 0, 4.2)), 0.45, 0.38, m["stone"], segs=6, smooth=False)
        k.cyl(p + V((0, 0, 4.2)), p + V((0, 0, 4.5)), 0.55, 0.5, m["gold"], segs=6, smooth=False)
        k.crystal(p + V((0, 0, 4.9)), 0.18, 0.6, m["nexus_glow"], sides=5)
    k.cyl((0, 0, 1.2), (0, 0, 2.0), 1.6, 1.3, m["stone_dark"], segs=12, smooth=False)
    ucx.append(ucx_cyl((0, 0, 1.2), 1.6, 0.8, 12))
    k.crystal((0, 0, 5.2), 1.2, 4.2, m["nexus_glow"], sides=6)
    k.torus((0, 0, 3.4), 2.6, 0.09, m["gold"], segs=40, rsegs=6, rot=(10, 0, 0))
    k.torus((0, 0, 3.6), 2.9, 0.06, m["nexus_glow"], segs=40, rsegs=6, rot=(-8, 6, 0))
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.4
        k.crystal((2.9 * math.cos(a), 2.9 * math.sin(a), 4.2 + 0.4 * (i % 2)), 0.25, 0.9, m["nexus_glow"], sides=5,
                  rot=(0, 15, math.degrees(a)))
    return finish_prop(k, "SM_Nexus", coll, off, ucx=ucx)


def build_launch_pad(root, m, off):
    coll = collection("Prop_SM_LaunchPad", root)
    k = Kit("SM_LaunchPad", coll)
    k.cyl((0, 0, 0), (0, 0, 0.15), 1.25, 1.2, m["metal"], segs=24)
    pts = [V((0.6 * math.cos(t * 0.6), 0.6 * math.sin(t * 0.6), 0.15 + t * 0.012)) for t in range(0, 26)]
    k.tube(pts, 0.05, m["gold"], segs=6)
    k.cyl((0, 0, 0.45), (0, 0, 0.57), 1.05, 1.0, m["orange"], segs=24)
    for y in (-0.2, 0.25):
        for sx in (1, -1):
            k.box((sx * 0.22, y, 0.58), (0.5, 0.12, 0.03), m["chevron"], rot=(0, 0, sx * 35))
    return finish_prop(k, "SM_LaunchPad", coll, off, ucx=[ucx_cyl((0, 0, 0), 1.25, 0.57, 12)])


def build_storm_wall(root, m, off):
    coll = collection("Prop_SM_StormWall", root)
    k = Kit("SM_StormWall", coll)
    segs = 64
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    bot = [bm.verts.new((math.cos(2 * math.pi * i / segs), math.sin(2 * math.pi * i / segs), 0.0)) for i in range(segs)]
    top = [bm.verts.new((v.co.x, v.co.y, 1.0)) for v in bot]
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
        u0, u1 = i / segs * 16, (i + 1) / segs * 16
        for loop, (u, v) in zip(f.loops, ((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
            loop[uv].uv = (u, v)
    o = make_obj("SM_StormWall_p001", bm, m["storm"], coll, smooth=True, uv=False)
    k.parts.append(o)
    return finish_prop(k, "SM_StormWall", coll, off)


def build_drop_ship(root, m, off):
    coll = collection("Prop_SM_DropShip", root)
    k = Kit("SM_DropShip", coll)
    prof = [(0, 0), (0.6, 1.6), (2.0, 2.8), (5.0, 3.3), (9.0, 3.2), (12.0, 2.6), (14.5, 1.4), (16.0, 0)]
    axis_z = 6.0
    k.lathe(prof, (0, 8.0, axis_z), (0, -1, 0), m["envelope"], segs=28, ref=(0, 0, 1))

    def radius_at(t):
        for (z0, r0), (z1, r1) in zip(prof, prof[1:]):
            if z0 <= t <= z1:
                return r0 + (r1 - r0) * (t - z0) / (z1 - z0)
        return 0.0

    for t in (3.0, 6.5, 11.5):
        k.torus((0, 8.0 - t, axis_z), radius_at(t) + 0.03, 0.12, m["ship_blue"], rot=(90, 0, 0), segs=40, rsegs=6)
    for i in range(4):
        a = i * 90
        r = Matrix.Rotation(math.radians(a), 4, "Y")
        c = V((0, 6.6, axis_z)) + (r.to_3x3() @ V((0, 0, 2.2)))
        k.box(c, (0.12, 2.6, 2.0), m["ship_blue"], rot=(0, a, 0), bevel_w=0.04)
    k.box((0, 0.5, 1.5), (2.4, 6.0, 1.8), m["chest_wood"], bevel_w=0.08)
    k.box((0, 0.5, 2.5), (2.6, 6.2, 0.2), m["ship_blue"], bevel_w=0.04)
    for y in (-1.5, -0.3, 0.9, 2.1):
        for sx in (1, -1):
            k.box((sx * 1.21, y, 1.7), (0.04, 0.8, 0.6), m["glass"])
    for p in ((-1.0, -1.8), (1.0, -1.8), (-1.0, 2.8), (1.0, 2.8)):
        k.cyl((p[0], p[1], 2.5), (p[0] * 1.5, p[1] * 1.2, axis_z - 2.9), 0.07, 0.07, m["metal"], segs=6)
    for sx in (1, -1):
        hub = V((sx * 1.6, 3.6, 1.6))
        k.cyl(V((sx * 1.2, 3.0, 1.6)), hub, 0.12, 0.12, m["metal"], segs=8)
        for i in range(3):
            k.box(hub + V((0, 0.05, 0)), (0.12, 0.04, 1.4), m["wood_dark"], rot=(0, i * 60, 0))
    return finish_prop(k, "SM_DropShip", coll, off)


PROPS_LAYOUT = {
    "wall": (-9, 9, 0), "floor": (-3, 9, 0), "ramp": (3, 9, 0), "cone": (9, 9, 0),
    "chest": (-10, 17, 0), "crate": (-8, 17, 0), "hp": (-6.5, 17, 0), "shield": (-6, 17, 0), "shard": (-5, 17, 0),
    "pad": (-3, 17, 0), "pine": (1, 18, 0), "round": (6, 18, 0), "rock1": (11, 18, 0), "rock2": (15, 18, 0),
    "bush": (18.5, 17, 0), "tower": (-8, 29, 0), "nexus": (8, 31, 0), "storm": (21, 29, 0), "ship": (0, 48, 6),
}


def build_all():
    m = M()
    build = collection("Build")
    props = collection("Props")
    L = PROPS_LAYOUT
    build_wall(build, m, L["wall"])
    build_floor(build, m, L["floor"])
    build_ramp(build, m, L["ramp"])
    build_cone(build, m, L["cone"])
    build_chest(props, m, L["chest"])
    build_crate(props, m, L["crate"])
    build_potions(props, m, (L["hp"], L["shield"]))
    build_shard(props, m, L["shard"])
    build_launch_pad(props, m, L["pad"])
    build_pine(props, m, L["pine"])
    build_round_tree(props, m, L["round"])
    build_rocks(props, m, (L["rock1"], L["rock2"]))
    build_bush(props, m, L["bush"])
    build_tower(props, m, L["tower"])
    build_nexus(props, m, L["nexus"])
    build_storm_wall(props, m, L["storm"])
    build_drop_ship(props, m, L["ship"])


if __name__ == "__main__":
    build_all()
