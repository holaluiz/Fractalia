"""Hero characters for Nexus Royale: rigged with UE-mannequin bone names (rigid skinning)."""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nexus_lib import (Kit, bm_ico, bm_lathe, bm_tube, collection, frame, mat,  # noqa: E402
                       roughen, trs)

V = Vector

# ------------------------------------------------------------------ skeleton

def joints(s=1.0, arm_drop=50.0):
    J = {}
    J["root"] = V((0, 0, 0))
    for k, z in (("pelvis", 0.98), ("spine_01", 1.06), ("spine_02", 1.2), ("spine_03", 1.34),
                 ("neck_01", 1.5), ("head", 1.6), ("head_end", 1.92)):
        J[k] = V((0, 0, z)) * s
    a = math.radians(arm_drop)
    d = V((math.cos(a), 0, -math.sin(a)))
    S = V((0.19, 0.01, 1.45))
    E = S + 0.27 * d + V((0, 0.02, 0))
    W = E + 0.25 * d + V((0, -0.015, 0))
    H = W + 0.13 * d + V((0, -0.01, 0))
    base = {
        "clavicle": V((0.035, 0.0, 1.445)), "upperarm": S, "lowerarm": E, "hand": W, "hand_end": H,
        "thigh": V((0.1, 0, 0.95)), "calf": V((0.11, -0.015, 0.52)), "foot": V((0.115, 0.03, 0.095)),
        "ball": V((0.115, -0.1, 0.03)), "ball_end": V((0.115, -0.18, 0.03)),
    }
    for side, sx in (("l", 1), ("r", -1)):
        for k, p in base.items():
            J[f"{k}_{side}"] = V((p.x * sx, p.y, p.z)) * s
    return J


def bone_list():
    bl = [("root", None, "root", None),
          ("pelvis", "root", "pelvis", "spine_01"),
          ("spine_01", "pelvis", "spine_01", "spine_02"),
          ("spine_02", "spine_01", "spine_02", "spine_03"),
          ("spine_03", "spine_02", "spine_03", "neck_01"),
          ("neck_01", "spine_03", "neck_01", "head"),
          ("head", "neck_01", "head", "head_end")]
    for s in "lr":
        bl += [(f"clavicle_{s}", "spine_03", f"clavicle_{s}", f"upperarm_{s}"),
               (f"upperarm_{s}", f"clavicle_{s}", f"upperarm_{s}", f"lowerarm_{s}"),
               (f"lowerarm_{s}", f"upperarm_{s}", f"lowerarm_{s}", f"hand_{s}"),
               (f"hand_{s}", f"lowerarm_{s}", f"hand_{s}", f"hand_end_{s}"),
               (f"thigh_{s}", "pelvis", f"thigh_{s}", f"calf_{s}"),
               (f"calf_{s}", f"thigh_{s}", f"calf_{s}", f"foot_{s}"),
               (f"foot_{s}", f"calf_{s}", f"foot_{s}", f"ball_{s}"),
               (f"ball_{s}", f"foot_{s}", f"ball_{s}", f"ball_end_{s}")]
    return bl


def build_armature(name, J, coll):
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    coll.objects.link(obj)
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    vl.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    for bname, parent, h, t in bone_list():
        b = eb.new(bname)
        b.head = J[h]
        b.tail = J[t] if t else J[h] + V((0, 0, 0.25))
        b.roll = 0.0
        if parent:
            b.parent = eb[parent]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.show_in_front = True
    arm.display_type = "STICK"
    return obj


def bind(mesh_obj, arm_obj):
    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_obj


# ------------------------------------------------------------------ shared body

def head_center(s, hs):
    return V((0, 0, 1.74)) * s, (0.155 * hs * s, 0.145 * hs * s, 0.165 * hs * s)


TORSO_DEPTH = 0.66  # front/back flattening of the torso lathes


def chest_front(z, s, b):
    """Approximate y of the chest surface (front) at height z (unscaled)."""
    return -0.19 * b * TORSO_DEPTH * s


def surf(hc, hr, x, dz, inset=0.0):
    rx, ry, rz = hr
    t = 1 - (x / rx) ** 2 - (dz / rz) ** 2
    return V((hc.x + x, hc.y - ry * math.sqrt(max(t, 0.0)) + inset, hc.z + dz))


def face(k, hc, hr, M, eyes=True, glint=True, brows=True, nose=True, mouth=True):
    sc = hr[0] / 0.155
    for sx in (1, -1):
        p = surf(hc, hr, 0.058 * sc * sx, 0.005 * sc, 0.012 * sc)
        if eyes:
            k.ellipsoid(p, (0.026 * sc, 0.014 * sc, 0.038 * sc), M["eye"], "head", segs=12, rings=8)
            if glint:
                k.ellipsoid(p + V((0.009 * sc, -0.012 * sc, 0.013 * sc)), (0.008 * sc,) * 3, M["white"],
                            "head", segs=8, rings=6)
        if brows:
            k.capsule(surf(hc, hr, 0.028 * sc * sx, 0.062 * sc, -0.002),
                      surf(hc, hr, 0.088 * sc * sx, 0.052 * sc, -0.002),
                      0.011 * sc, 0.008 * sc, M["brow"], "head", segs=8)
    if nose:
        k.ellipsoid(surf(hc, hr, 0.0, -0.032 * sc, 0.008 * sc), (0.022 * sc, 0.02 * sc, 0.024 * sc),
                    M["skin"], "head", segs=10, rings=8)
    if mouth:
        k.capsule(surf(hc, hr, -0.032 * sc, -0.078 * sc, 0.006 * sc),
                  surf(hc, hr, 0.032 * sc, -0.078 * sc, 0.006 * sc), 0.008 * sc, 0.008 * sc,
                  M["mouth"], "head", segs=8)


def body(k, J, M, s=1.0, b=1.0, hs=1.0, face_opts=None):
    k.ellipsoid(V((0, 0, 0.965)) * s, (0.16 * b * s, 0.12 * b * s, 0.12 * s), M["pants"], "pelvis")
    belly = [(0.95, 0.0), (0.97, 0.12), (1.03, 0.145), (1.12, 0.15), (1.2, 0.15), (1.28, 0.12), (1.31, 0.0)]
    k.lathe([((z - 0.95) * s, r * b * s) for z, r in belly], V((0, 0, 0.95)) * s, V((0, 0, 1)), M["top"],
            "spine_01", segs=20, sy=0.75)
    chest = [(1.1, 0.0), (1.12, 0.13), (1.2, 0.165), (1.3, 0.185), (1.4, 0.195), (1.46, 0.185), (1.51, 0.15),
             (1.545, 0.08), (1.555, 0.0)]
    k.lathe([((z - 1.1) * s, r * b * s) for z, r in chest], V((0, 0, 1.1)) * s, V((0, 0, 1)), M["top"],
            "spine_03", segs=24, sy=TORSO_DEPTH)
    k.capsule(V((0, 0, 1.47)) * s, V((0, 0, 1.64)) * s, 0.052 * s * max(1.0, b * 0.9), 0.046 * s,
              M["skin"], "neck_01")
    hc, hr = head_center(s, hs)
    k.ellipsoid(hc, hr, M["skin"], "head", segs=24, rings=16)
    for sx in (1, -1):  # ears
        k.ellipsoid(hc + V((hr[0] * 0.97 * sx, 0.01 * s, -0.01 * s)), (0.022 * s, 0.035 * s, 0.045 * s),
                    M["skin"], "head", segs=10, rings=8)
    face(k, hc, hr, M, **(face_opts or {}))
    for side in "lr":
        S, E, W, H = (J[f"{n}_{side}"] for n in ("upperarm", "lowerarm", "hand", "hand_end"))
        k.capsule(S, E, 0.068 * b * s, 0.056 * b * s, M["sleeve"], f"upperarm_{side}", ext=0.035 * s)
        k.capsule(E, W, 0.056 * b * s, 0.046 * b * s, M["forearm"], f"lowerarm_{side}", ext=0.02 * s)
        d = (H - W).normalized()
        rot = frame((0, 0, 0), d)
        g = b ** 0.5
        k.ellipsoid(W + d * 0.065 * s, (0.037 * s * g, 0.06 * s * g, 0.076 * s), M["gloves"], f"hand_{side}", rot=rot)
        k.capsule(W + d * 0.03 * s + V((0, -0.035, 0)) * s, W + d * 0.075 * s + V((0, -0.07, 0)) * s,
                  0.019 * s * g, 0.017 * s * g, M["gloves"], f"hand_{side}", segs=8)
        T, K, A, B, BE = (J[f"{n}_{side}"] for n in ("thigh", "calf", "foot", "ball", "ball_end"))
        k.capsule(T, K, 0.096 * b * s, 0.072 * b * s, M["pants"], f"thigh_{side}", ext=0.03 * s)
        k.capsule(K, A, 0.07 * b * s, 0.05 * b * s, M["pants"], f"calf_{side}", ext=0.02 * s)
        k.capsule(A + V((0, 0, -0.02)) * s, A + V((0, 0, 0.17)) * s, 0.064 * b * s, 0.068 * b * s,
                  M["boots"], f"calf_{side}")
        k.box(V(((A.x + B.x) / 2, (A.y + B.y) / 2, 0.058 * s)), (0.115 * b * s, 0.2 * s, 0.11 * s),
              M["boots"], f"foot_{side}", bevel_w=0.035 * s, smooth=True)
        k.ellipsoid(V((B.x, B.y - 0.02 * s, 0.045 * s)), (0.06 * b * s, 0.07 * s, 0.045 * s), M["boots"], f"ball_{side}")
        k.box(V(((A.x + B.x) / 2, (A.y + BE.y) / 2 + 0.015 * s, 0.012 * s)), (0.125 * b * s, 0.28 * s, 0.024 * s),
              M["sole"], f"foot_{side}", bevel_w=0.008 * s)
    return hc, hr


def hand_center(J, side, s):
    W, H = J[f"hand_{side}"], J[f"hand_end_{side}"]
    return W + (H - W).normalized() * 0.06 * s


def shell(k, profile, origin, axis, material, bone, thickness, segs=24, sx=1.0, sy=1.0):
    bm = bm_lathe(profile, segs, sx, sy, cap=False)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=thickness)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return k.raw(bm, material, frame(origin, axis), True, bone)


def dome_profile(R, z0=0.0, n=8):
    """Hemisphere (z from z0*R up to the pole) for lathe shells."""
    a0 = math.asin(max(-1.0, min(1.0, z0)))
    out = []
    for i in range(n + 1):
        a = a0 + (math.pi / 2 - a0) * i / n
        out.append((R * math.sin(a), R * math.cos(a) if i < n else 0.0))
    return out


def common_mats(prefix, skin, eye="#1B1B24"):
    return {
        "skin": mat(f"M_{prefix}_Skin", skin, 0.55),
        "eye": mat("M_Eye_Dark", eye, 0.2),
        "white": mat("M_Eye_Glint", "#FFFFFF", 0.2, emit="#FFFFFF", emit_strength=1.0),
        "mouth": mat("M_Mouth", "#5A2430", 0.5),
        "sole": mat("M_Sole_Dark", "#2A2522", 0.8),
    }


# ------------------------------------------------------------------ heroes

def hero_brakka(coll):
    s, b, hs = 1.04, 1.3, 1.0
    J = joints(s)
    M = common_mats("Brakka", "#C98B5E")
    armor = mat("M_Brakka_Armor", "#2F5DBA", 0.35, 0.3)
    steel = mat("M_Brakka_Steel", "#9AA5B1", 0.3, 0.8)
    gold = mat("M_Gold", "#E8B04A", 0.3, 0.9)
    leather = mat("M_Brakka_Leather", "#4A3426", 0.7)
    beard = mat("M_Brakka_Beard", "#3B2416", 0.9)
    ivory = mat("M_Ivory", "#EDE3C8", 0.5)
    M.update(top=armor, pants=mat("M_Brakka_Pants", "#3A3F4A", 0.8), boots=leather, gloves=leather,
             sleeve=M["skin"], forearm=steel, brow=beard)
    k = Kit("SK_Brakka", coll)
    hc, hr = body(k, J, M, s, b, hs, face_opts=dict(mouth=False))
    # beard + helmet with horns
    k.ellipsoid(hc + V((0, -0.085, -0.105)) * s, (0.115 * s, 0.075 * s, 0.085 * s), beard, "head")
    shell(k, dome_profile(0.178 * s, -0.05), hc + V((0, 0.01, 0.05)) * s, V((0, 0.12, 1)), steel, "head", 0.012 * s)
    k.torus(hc + V((0, 0.005, 0.045)) * s, 0.172 * s, 0.016 * s, gold, "head", rot=(4, 0, 0), segs=28)
    k.box(hc + V((0, -0.165, 0.075)) * s, (0.035 * s, 0.03 * s, 0.09 * s), steel, "head", bevel_w=0.008 * s)
    for sx in (1, -1):
        base = hc + V((0.16 * sx, 0.0, 0.07)) * s
        pts = [base, base + V((0.09 * sx, -0.02, 0.03)) * s, base + V((0.16 * sx, -0.05, 0.11)) * s,
               base + V((0.18 * sx, -0.08, 0.2)) * s]
        k.tube(pts, [0.038 * s, 0.03 * s, 0.018 * s, 0.004 * s], ivory, "head", segs=10)
    # chest emblem, belt
    k.ellipsoid(V((0, chest_front(1.31, 1, b) - 0.004, 1.32)) * s, (0.055 * s, 0.02 * s, 0.06 * s), gold,
                "spine_03", segs=12, rings=8)
    k.torus(V((0, 0, 1.03)) * s, 0.15 * b * s, 0.03 * s, leather, "pelvis", segs=28, scale=(1, 0.78, 1))
    k.box(V((0, -0.15 * b * 0.78 - 0.02, 1.03)) * s, (0.08 * s, 0.03 * s, 0.07 * s), gold, "pelvis",
          bevel_w=0.01 * s)
    # shoulder pads
    for side, sx in (("l", 1), ("r", -1)):
        S = J[f"upperarm_{side}"]
        k.ellipsoid(S + V((0.03 * sx, 0, 0.05)) * s, (0.13 * s, 0.14 * s, 0.095 * s), steel, f"upperarm_{side}",
                    rot=trs(rot=(0, -20 * sx, 0)))
        k.ellipsoid(S + V((0.05 * sx, 0, 0.0)) * s, (0.12 * s, 0.13 * s, 0.07 * s), armor, f"upperarm_{side}",
                    rot=trs(rot=(0, -35 * sx, 0)))
    # round shield strapped to the left forearm
    E, W = J["lowerarm_l"], J["hand_l"]
    out = frame((0, 0, 0), W - E).to_3x3() @ V((1, 0, 0))
    c = (E + W) / 2 + out * 0.075 * s
    R = 0.31 * s
    k.lathe([(0.0, 0.0), (0.0, R), (0.03 * s, R * 0.97), (0.06 * s, R * 0.62), (0.072 * s, 0.0)], c, out, armor,
            "lowerarm_l", segs=32)
    rim_rot = tuple(math.degrees(a) for a in frame((0, 0, 0), out).to_3x3().to_euler())
    k.torus(c + out * 0.012 * s, R, 0.024 * s, steel, "lowerarm_l", rot=rim_rot, segs=32, rsegs=8)
    k.torus(c + out * 0.045 * s, R * 0.55, 0.014 * s, gold, "lowerarm_l", rot=rim_rot, segs=28, rsegs=6)
    k.ellipsoid(c + out * 0.075 * s, (0.07 * s, 0.07 * s, 0.07 * s), gold, "lowerarm_l", segs=14, rings=10)
    # hammer in right hand
    hcr = hand_center(J, "r", s)
    wood = mat("M_Wood_Dark", "#6B4423", 0.7)
    k.cyl(hcr + V((0, 0.2, 0)) * s, hcr + V((0, -0.62, 0)) * s, 0.024 * s, 0.024 * s, wood, "hand_r", segs=10)
    k.ellipsoid(hcr + V((0, 0.22, 0)) * s, (0.035 * s,) * 3, gold, "hand_r", segs=10, rings=8)
    k.box(hcr + V((0, -0.66, 0)) * s, (0.17 * s, 0.17 * s, 0.32 * s), steel, "hand_r", bevel_w=0.025 * s)
    for dz in (-0.1, 0.1):
        k.box(hcr + V((0, -0.66, dz)) * s, (0.18 * s, 0.18 * s, 0.035 * s), gold, "hand_r", bevel_w=0.006 * s)
    return J, k.finish()


def hero_vela(coll):
    s, b, hs = 0.97, 0.9, 1.02
    J = joints(s)
    M = common_mats("Vela", "#F1C6A0", eye="#2B4A2A")
    green = mat("M_Vela_Tunic", "#3E7D3A", 0.75)
    hood = mat("M_Vela_Hood", "#2E5E2B", 0.85)
    leather = mat("M_Vela_Leather", "#7A4E2D", 0.7)
    cream = mat("M_Vela_Cream", "#E9DFC4", 0.8)
    hair = mat("M_Vela_Hair", "#B5452B", 0.7)
    wood = mat("M_Vela_BowWood", "#8B5A2B", 0.6)
    M.update(top=green, pants=mat("M_Vela_Pants", "#5C4632", 0.8), boots=mat("M_Vela_Boots", "#6B4428", 0.7),
             gloves=leather, sleeve=green, forearm=leather, brow=hair)
    k = Kit("SK_Vela", coll)
    hc, hr = body(k, J, M, s, b, hs, face_opts=dict(nose=False, mouth=False))
    # scarf mask over lower face
    scarf = mat("M_Vela_Scarf", "#2B5130", 0.85)
    k.ellipsoid(hc + V((0, -0.006, -0.078)) * s, (0.162 * s, 0.152 * s, 0.1 * s), scarf, "head")
    # hood (tilted dome open to the front) + drape
    shell(k, dome_profile(0.198 * s, -0.25), hc + V((0, 0.02, 0.012)) * s, V((0, 0.62, 0.78)), hood, "head", 0.014 * s)
    k.ellipsoid(V((0, 0.1, 1.53)) * s, (0.16 * s, 0.08 * s, 0.1 * s), hood, "neck_01")
    # braid
    for i in range(4):
        k.ellipsoid(V((0.13 - 0.005 * i, -0.06, 1.62 - 0.07 * i)) * s, (0.035 * s,) * 3, hair, "head", segs=10, rings=8)
    # cape
    bm = bmesh.new()
    rows, cols = 8, 10
    grid = []
    for r in range(rows + 1):
        v = r / rows
        z = 1.47 - v * 0.82
        w = 0.21 + 0.13 * v
        row = []
        for c in range(cols + 1):
            u = c / cols * 2 - 1
            y = 0.135 + 0.09 * v - 0.075 * u * u + 0.012 * math.sin(u * 6 + v * 3)
            row.append(bm.verts.new(V((u * w, y, z)) * s))
        grid.append(row)
    for r in range(rows):
        for c in range(cols):
            bm.faces.new((grid[r][c], grid[r][c + 1], grid[r + 1][c + 1], grid[r + 1][c]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.016 * s)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    k.raw(bm, hood, None, True, "spine_03")
    # quiver with arrows
    q0, q1 = V((0.11, 0.25, 1.02)) * s, V((-0.08, 0.27, 1.46)) * s
    k.cyl(q0, q1, 0.06 * s, 0.065 * s, leather, "spine_02", segs=12)
    qd = (q1 - q0).normalized()
    for i, off in enumerate((V((0.02, 0, 0)), V((-0.02, 0.015, 0)), V((0, -0.02, 0)))):
        a0 = q1 + off * s
        a1 = a0 + qd * 0.16 * s
        k.cyl(a0, a1, 0.008 * s, 0.008 * s, wood, "spine_02", segs=6)
        k.box(a1, (0.04 * s, 0.006 * s, 0.07 * s), cream if i % 2 else hair, "spine_02", rot=(0, -25, 0))
    # belt + pouch, shoulder guard
    k.torus(V((0, 0, 1.03)) * s, 0.15 * b * s, 0.022 * s, leather, "pelvis", segs=28, scale=(1, 0.78, 1))
    k.box(V((0.15 * b, -0.04, 0.98)) * s, (0.06 * s, 0.08 * s, 0.09 * s), leather, "pelvis", bevel_w=0.015 * s)
    k.ellipsoid(J["upperarm_r"] + V((-0.02, 0, 0.04)) * s, (0.09 * s, 0.1 * s, 0.065 * s), leather, "upperarm_r",
                rot=trs(rot=(0, 25, 0)))
    # bow in left hand
    hcl = hand_center(J, "l", s)
    pts, rad = [], []
    for i in range(13):
        t = i / 12 * 2 - 1
        y = 0.13 * (1 - t * t) - 0.03 * (abs(t) ** 6)
        pts.append(hcl + V((0, 0.13 - y - 0.0, t * 0.66)) * s)
        rad.append((0.024 - 0.013 * abs(t)) * s)
    k.tube(pts, rad, wood, "hand_l", segs=8)
    k.cyl(pts[0], pts[-1], 0.004 * s, 0.004 * s, cream, "hand_l", segs=5)
    k.cyl(hcl + V((0, 0, -0.07)) * s, hcl + V((0, 0, 0.07)) * s, 0.03 * s, 0.03 * s, leather, "hand_l", segs=10)
    return J, k.finish()


def hero_zephyr(coll):
    s, b, hs = 1.0, 0.95, 1.0
    J = joints(s)
    M = common_mats("Zephyr", "#2A2340")
    robe = mat("M_Zephyr_Robe", "#5B2A86", 0.7)
    hat = mat("M_Zephyr_Hat", "#4A2270", 0.75)
    gold = mat("M_Gold", "#E8B04A", 0.3, 0.9)
    glow = mat("M_Arcane_Glow", "#4FF2FF", 0.2, emit="#4FF2FF", emit_strength=3.0)
    wood = mat("M_Wood_Dark", "#6B4423", 0.7)
    dark = mat("M_Zephyr_Pants", "#2C1F3D", 0.8)
    M.update(eye=glow, top=robe, pants=dark, boots=mat("M_Zephyr_Boots", "#3B2A1E", 0.7), gloves=dark,
             sleeve=robe, forearm=robe, brow=dark)
    k = Kit("SK_Zephyr", coll)
    hc, hr = body(k, J, M, s, b, hs, face_opts=dict(glint=False, brows=False, nose=False, mouth=False))
    # robe skirt with gold trim
    prof = [(0.0, 0.3), (0.12, 0.26), (0.26, 0.21), (0.42, 0.17)]
    shell(k, prof, V((0, 0, 0.66)) * s, V((0, 0, 1)), robe, "pelvis", 0.014 * s, segs=24, sy=0.85)
    k.torus(V((0, 0, 0.665)) * s, 0.3 * s, 0.018 * s, gold, "pelvis", segs=32)
    k.torus(V((0, 0, 1.06)) * s, 0.152 * b * s, 0.03 * s, gold, "pelvis", segs=28, scale=(1, 0.8, 1))
    k.box(V((0.17, 0.0, 0.96)) * s, (0.05 * s, 0.13 * s, 0.17 * s), mat("M_Book", "#7B2C2C", 0.6), "pelvis",
          bevel_w=0.012 * s, rot=(0, 0, 10))
    # high collar
    shell(k, [(0.0, 0.1), (0.05, 0.115), (0.11, 0.16)], V((0, 0.01, 1.5)) * s, V((0, 0.2, 1)), robe, "neck_01",
          0.012 * s, segs=20)
    # sleeve cuffs
    for side in "lr":
        E, W = J[f"lowerarm_{side}"], J[f"hand_{side}"]
        d = (W - E).normalized()
        shell(k, [(0.0, 0.05), (0.07, 0.075), (0.1, 0.085)], W - d * 0.09 * s, d, robe, f"lowerarm_{side}",
              0.01 * s, segs=16)
        k.torus(W + d * 0.012 * s, 0.085 * s, 0.01 * s, gold, f"lowerarm_{side}",
                rot=tuple(math.degrees(a) for a in frame((0, 0, 0), d).to_3x3().to_euler()), segs=20, rsegs=6)
        k.ellipsoid(J[f"upperarm_{side}"] + V((0.02 if side == "l" else -0.02, 0, 0.04)) * s,
                    (0.085 * s, 0.09 * s, 0.06 * s), gold, f"upperarm_{side}")
    # wizard hat: brim + bent cone + band + gem
    brim_c = hc + V((0, 0.01, 0.085)) * s
    k.lathe([(-0.012 * s, 0.0), (-0.012 * s, 0.31 * s), (0.0, 0.33 * s), (0.012 * s, 0.31 * s), (0.012 * s, 0.0)],
            brim_c, V((0, 0.08, 1)), hat, "head", segs=32)
    cone = [brim_c, brim_c + V((0, 0.02, 0.2)) * s, brim_c + V((0, 0.07, 0.38)) * s,
            brim_c + V((0, 0.17, 0.5)) * s, brim_c + V((0, 0.27, 0.52)) * s]
    k.tube(cone, [0.175 * s, 0.13 * s, 0.075 * s, 0.035 * s, 0.006 * s], hat, "head", segs=20)
    k.torus(brim_c + V((0, 0.0, 0.035)) * s, 0.168 * s, 0.018 * s, gold, "head", rot=(4, 0, 0), segs=28)
    k.crystal(brim_c + V((0, -0.17, 0.04)) * s, 0.03 * s, 0.08 * s, glow, "head", rot=(90, 0, 0))
    # staff
    hcr = hand_center(J, "r", s)
    k.cyl(hcr + V((0, 0, -0.85)) * s, hcr + V((0, 0, 0.78)) * s, 0.022 * s, 0.026 * s, wood, "hand_r", segs=10)
    k.ellipsoid(hcr + V((0, 0, -0.86)) * s, (0.03 * s,) * 3, gold, "hand_r", segs=10, rings=8)
    top = hcr + V((0, 0, 0.78)) * s
    for i in range(3):
        a = 2 * math.pi * i / 3
        dx, dy = math.cos(a), math.sin(a)
        claw = [top, top + V((dx * 0.05, dy * 0.05, 0.06)) * s, top + V((dx * 0.07, dy * 0.07, 0.15)) * s,
                top + V((dx * 0.035, dy * 0.035, 0.24)) * s]
        k.tube(claw, [0.016 * s, 0.014 * s, 0.01 * s, 0.004 * s], gold, "hand_r", segs=6)
    k.crystal(top + V((0, 0, 0.13)) * s, 0.065 * s, 0.26 * s, glow, "hand_r")
    return J, k.finish()


def hero_lumi(coll):
    s, b, hs = 0.93, 0.85, 1.1
    J = joints(s)
    M = common_mats("Lumi", "#FFD9C2", eye="#3A2A5A")
    white = mat("M_Lumi_White", "#F4F1EA", 0.6)
    pink = mat("M_Lumi_Pink", "#FF7AB6", 0.6)
    gold = mat("M_Gold", "#E8B04A", 0.3, 0.9)
    hair = mat("M_Lumi_Hair", "#FF8FC4", 0.7)
    halo = mat("M_Halo_Glow", "#FFD86B", 0.2, emit="#FFD86B", emit_strength=2.5)
    orb = mat("M_Lumi_Orb", "#FFE38A", 0.2, emit="#FFE38A", emit_strength=3.0)
    M.update(top=white, pants=mat("M_Lumi_Leggings", "#EDE6DA", 0.7), boots=white, gloves=white,
             sleeve=white, forearm=M["skin"], brow=hair)
    k = Kit("SK_Lumi", coll)
    hc, hr = body(k, J, M, s, b, hs)
    # hair: tilted dome shell + bangs + twin buns
    shell(k, dome_profile(0.19 * s * hs, -0.45), hc + V((0, 0.025, 0.0)) * s, V((0, 0.5, 0.86)), hair,
          "head", 0.03 * s)
    for x, rz in ((-0.075, 25), (0.0, 0), (0.075, -25)):
        k.ellipsoid(hc + V((x, -0.14, 0.13)) * s, (0.07 * s, 0.04 * s, 0.045 * s), hair, "head",
                    rot=trs(rot=(0, rz, 0)), segs=12, rings=8)
    for sx in (1, -1):
        k.ellipsoid(hc + V((0.155 * sx, -0.045, -0.04)) * s, (0.05 * s, 0.075 * s, 0.11 * s), hair, "head",
                    rot=trs(rot=(0, 10 * sx, 0)), segs=12, rings=10)
        bun = hc + V((0.11 * sx, 0.075, 0.165)) * s
        k.ellipsoid(bun, (0.055 * s,) * 3, hair, "head", segs=14, rings=10)
        k.torus(bun + V((-0.022 * sx, -0.01, -0.03)) * s, 0.045 * s, 0.01 * s, gold, "head", rot=(0, -40 * sx, 0),
                segs=20, rsegs=6)
    # halo
    k.torus(hc + V((0, 0.03, 0.3)) * s, 0.13 * s, 0.013 * s, halo, "head", rot=(12, 0, 0), segs=36, rsegs=8)
    # skirt layers, collar, brooch, puffy sleeves, boot trims
    shell(k, [(0.0, 0.25), (0.1, 0.2), (0.2, 0.155)], V((0, 0, 0.84)) * s, V((0, 0, 1)), pink, "pelvis", 0.012 * s,
          sy=0.85)
    shell(k, [(0.0, 0.215), (0.08, 0.18), (0.16, 0.15)], V((0, 0, 0.9)) * s, V((0, 0, 1)), white, "pelvis", 0.012 * s,
          sy=0.85)
    k.torus(V((0, 0, 1.53)) * s, 0.065 * s, 0.016 * s, gold, "neck_01", segs=24)
    k.ellipsoid(V((0, chest_front(1.33, 1, b) - 0.004, 1.34)) * s, (0.035 * s, 0.015 * s, 0.035 * s), pink,
                "spine_03", segs=12, rings=8)
    for side, sx in (("l", 1), ("r", -1)):
        k.ellipsoid(J[f"upperarm_{side}"] + V((0.04 * sx, 0, 0.0)) * s, (0.09 * s, 0.085 * s, 0.075 * s), pink,
                    f"upperarm_{side}")
        k.torus(J[f"foot_{side}"] + V((0, 0, 0.17)) * s, 0.068 * b * s, 0.014 * s, gold, f"calf_{side}", segs=20,
                rsegs=6)
    # wings
    feather_w = mat("M_Lumi_Feather", "#FFFFFF", 0.5)
    for sx in (1, -1):
        base = V((0.05 * sx, 0.14, 1.38)) * s
        for i, (ang, ln) in enumerate(((20, 0.3), (42, 0.26), (64, 0.2))):
            r = Matrix.Rotation(math.radians(-sx * ang), 4, "Y") @ Matrix.Rotation(math.radians(-sx * 15), 4, "Z")
            c = base + (r.to_3x3() @ V((sx * ln / 2, 0, 0))) * s
            k.ellipsoid(c, (ln / 2 * s, 0.022 * s, 0.05 * s), feather_w if i else gold, "spine_03", rot=r, segs=12, rings=8)
    # lantern staff
    hcr = hand_center(J, "r", s)
    k.cyl(hcr + V((0, 0, -0.5)) * s, hcr + V((0, 0, 0.56)) * s, 0.02 * s, 0.02 * s, white, "hand_r", segs=10)
    k.ellipsoid(hcr + V((0, 0, -0.51)) * s, (0.028 * s,) * 3, gold, "hand_r", segs=10, rings=8)
    ring_c = hcr + V((0, 0, 0.7)) * s
    k.torus(ring_c, 0.11 * s, 0.014 * s, gold, "hand_r", rot=(90, 0, 0), segs=28, rsegs=6)
    k.ellipsoid(ring_c, (0.065 * s,) * 3, orb, "hand_r", segs=16, rings=10)
    for sx in (1, -1):
        k.ellipsoid(ring_c + V((0.13 * sx, 0, 0.02)) * s, (0.05 * s, 0.012 * s, 0.03 * s), gold, "hand_r",
                    rot=trs(rot=(0, -30 * sx, 0)), segs=10, rings=6)
    return J, k.finish()


def hero_guardian(coll):
    s, b = 1.65, 1.0
    J = joints(s, arm_drop=60)
    stone = mat("M_Guardian_Stone", "#6E6A64", 0.9)
    dark = mat("M_Guardian_StoneDark", "#4D4944", 0.9)
    moss = mat("M_Guardian_Moss", "#4F7A2E", 0.95)
    lava = mat("M_Guardian_Lava", "#FF7A1A", 0.3, emit="#FF7A1A", emit_strength=3.0)
    k = Kit("SK_Guardian", coll)
    seed = [100]

    def rock_along(p1, p2, r, material, bone, rough=0.12, extra=0.0):
        p1, p2 = V(p1), V(p2)
        d = p2 - p1
        bm = bm_ico(2)
        seed[0] += 1
        roughen(bm, rough, seed[0])
        m = frame((p1 + p2) / 2, d) @ Matrix.Diagonal((r, r * 0.9, d.length / 2 + extra, 1.0))
        k.raw(bm, material, m, False, bone)

    def rock_at(c, radii, material, bone, rough=0.15, rot=(0, 0, 0)):
        seed[0] += 1
        k.rock(V(c), radii, material, bone, seed=seed[0], rough=rough, rot=rot)

    rock_at(J["pelvis"], (0.26 * s, 0.19 * s, 0.16 * s), dark, "pelvis")
    rock_at(V((0, 0, 1.14)) * s, (0.24 * s, 0.18 * s, 0.13 * s), stone, "spine_01")
    rock_at(V((0, 0.02, 1.3)) * s, (0.34 * s, 0.24 * s, 0.22 * s), stone, "spine_02")
    rock_at(V((0, 0.05, 1.45)) * s, (0.42 * s, 0.22 * s, 0.15 * s), stone, "spine_03")
    k.ellipsoid(V((0, -0.205, 1.3)) * s, (0.085 * s, 0.05 * s, 0.1 * s), lava, "spine_02", segs=12, rings=8)
    for a, c in ((25, V((0.07, -0.21, 1.2))), (-30, V((-0.08, -0.21, 1.38))), (70, V((0.12, -0.2, 1.4)))):
        k.box(c * s, (0.12 * s, 0.03 * s, 0.018 * s), lava, "spine_02", rot=(0, a, 0))
    # small head sunk between shoulders
    hcg = V((0, -0.06, 1.62)) * s
    rock_at(hcg, (0.15 * s, 0.14 * s, 0.13 * s), dark, "head")
    for sx in (1, -1):
        k.ellipsoid(hcg + V((0.06 * sx, -0.125, 0.02)) * s, (0.03 * s, 0.015 * s, 0.018 * s), lava, "head", segs=10,
                    rings=6)
    rock_at(V((0, 0.06, 1.58)) * s, (0.2 * s, 0.12 * s, 0.08 * s), moss, "spine_03", rough=0.2)
    for side, sx in (("l", 1), ("r", -1)):
        S, E, W, H = (J[f"{n}_{side}"] for n in ("upperarm", "lowerarm", "hand", "hand_end"))
        rock_at(S + V((0.04 * sx, 0, 0.06)) * s, (0.2 * s, 0.2 * s, 0.16 * s), stone, f"upperarm_{side}")
        rock_at(S + V((0.05 * sx, 0.02, 0.15)) * s, (0.14 * s, 0.13 * s, 0.05 * s), moss, f"upperarm_{side}", rough=0.25)
        k.crystal(S + V((0.02 * sx, 0.08, 0.17)) * s, 0.045 * s, 0.22 * s, lava, f"upperarm_{side}",
                  rot=(-25, 20 * sx, 0))
        rock_along(S, E, 0.12 * s, dark, f"upperarm_{side}")
        rock_along(E, W, 0.13 * s, stone, f"lowerarm_{side}", extra=0.03 * s)
        rock_at(W + (H - W) * 0.6, (0.17 * s, 0.17 * s, 0.17 * s), dark, f"hand_{side}")
        T, K, A, B = (J[f"{n}_{side}"] for n in ("thigh", "calf", "foot", "ball"))
        rock_along(T, K, 0.13 * s, dark, f"thigh_{side}", extra=0.02 * s)
        rock_along(K, A, 0.12 * s, stone, f"calf_{side}", extra=0.04 * s)
        rock_at(V(((A.x + B.x) / 2, (A.y + B.y) / 2 - 0.02 * s, 0.06 * s)), (0.1 * s, 0.17 * s, 0.07 * s), dark,
                f"foot_{side}")
        rock_at(V((B.x, B.y - 0.05 * s, 0.045 * s)), (0.08 * s, 0.07 * s, 0.045 * s), stone, f"ball_{side}")
    return J, k.finish()


HEROES = [("Brakka", hero_brakka, -3.2), ("Vela", hero_vela, -1.6), ("Zephyr", hero_zephyr, 0.0),
          ("Lumi", hero_lumi, 1.6), ("Guardian", hero_guardian, 4.4)]


def build_all():
    root = collection("Heroes")
    out = {}
    for name, fn, x in HEROES:
        coll = collection(f"Hero_{name}", root)
        J, mesh = fn(coll)
        arm = build_armature(f"SKEL_{name}", J, coll)
        bind(mesh, arm)
        arm.location.x = x
        out[name] = (arm, mesh)
    return out


if __name__ == "__main__":
    build_all()
