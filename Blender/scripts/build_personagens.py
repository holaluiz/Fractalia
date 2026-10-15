"""User-supplied characters (Personagens/*.fbx, Tripo AI static meshes) -> rigged game heroes.

Each mesh is scaled to game size, its joints are estimated from the geometry, an armature with the
same UE-mannequin bone names as the procedural heroes is built, and automatic (heat) weights are applied.
"""
import math
import os
import statistics as st
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.append(HERE)
import build_heroes  # noqa: E402
from nexus_lib import collection  # noqa: E402

V = Vector
SRC = os.path.join(ROOT, "Personagens")

# height: total height in meters (incl. hat/hair); skull: fraction of the total that is the top of the skull
CHARS = [
    dict(id="Boto", folder="Boto Encantado Corsário", height=2.0, skull=0.9, x=7.4),
    dict(id="Caramelo", folder="Cara Caramelo", height=1.85, skull=0.965, x=9.2),
    dict(id="PombaGira", folder="Pomba Gira Carmesim", height=1.85, skull=0.955, x=11.0),
]


def import_mesh(cfg, coll):
    folder = os.path.join(SRC, cfg["folder"])
    fbx = next(os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".fbx"))
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx)
    new = [o for o in bpy.data.objects if o not in before]
    mesh = next(o for o in new if o.type == "MESH")
    for o in new:
        if o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    for c in list(mesh.users_collection):
        c.objects.unlink(mesh)
    coll.objects.link(mesh)
    bpy.context.view_layer.update()
    # bake the importer's rotation/scale, then scale to game height with feet on the ground
    mesh.data.transform(mesh.matrix_world)
    mesh.matrix_world = Matrix.Identity(4)
    vs = mesh.data.vertices
    zmin = min(v.co.z for v in vs)
    zmax = max(v.co.z for v in vs)
    s = cfg["height"] / (zmax - zmin)
    xs = [v.co.x for v in vs]
    cx = (min(xs) + max(xs)) / 2
    low = [v.co for v in vs if v.co.z < zmin + 0.04 * (zmax - zmin)]
    cy = st.fmean(c.y for c in low)
    mesh.data.transform(Matrix.Diagonal((s, s, s, 1.0)) @ Matrix.Translation((-cx, -cy, -zmin)))
    mesh.name = mesh.data.name = f"SK_{cfg['id']}"
    if mesh.data.uv_layers:
        mesh.data.uv_layers[0].name = "UVMap"
    for i, m in enumerate(mesh.data.materials):
        if m:
            m.name = f"M_{cfg['id']}" if i == 0 else f"M_{cfg['id']}_{i}"
    for p in mesh.data.polygons:
        p.use_smooth = True
    return mesh


def estimate_joints(mesh, cfg):
    co = [v.co.copy() for v in mesh.data.vertices]
    Hb = cfg["height"] * cfg["skull"]

    def torso_y(z, half=0.08):
        ys = [c.y for c in co if abs(c.x) < half * Hb and abs(c.z - z) < 0.025 * Hb]
        return st.fmean(ys) if ys else 0.0

    J = {"root": V((0, 0, 0))}
    for k, f in (("pelvis", 0.53), ("spine_01", 0.585), ("spine_02", 0.65), ("spine_03", 0.72),
                 ("neck_01", 0.825), ("head", 0.865)):
        z = f * Hb
        J[k] = V((0, torso_y(z) + 0.012 * Hb, z))
    J["head_end"] = V((0, J["head"].y, Hb))

    for side, sx in (("l", 1.0), ("r", -1.0)):
        # ---- arm: fingertip + upper-envelope line through the arm (ignores cloth hanging below it)
        arm = [c for c in co if c.x * sx > 0.2 * Hb]
        tip_x = max(c.x * sx for c in arm)
        bins = []
        x = 0.2 * Hb
        while x < 0.8 * tip_x:
            sl = [c for c in arm if x <= c.x * sx < x + 0.02 * Hb]
            if len(sl) > 3:
                ztop = max(c.z for c in sl)
                band = [c for c in sl if c.z > ztop - 0.05 * Hb]
                bins.append((x + 0.01 * Hb, ztop - 0.03 * Hb, st.fmean(c.y for c in band)))
            x += 0.02 * Hb
        n = len(bins)
        mx = sum(b[0] for b in bins) / n
        mz = sum(b[1] for b in bins) / n
        slope = sum((b[0] - mx) * (b[1] - mz) for b in bins) / max(1e-9, sum((b[0] - mx) ** 2 for b in bins))
        y_arm = st.median(b[2] for b in bins)
        line_z = lambda xx: mz + slope * (xx - mx)  # noqa: E731
        xs = 0.1 * Hb
        S = V((xs * sx, y_arm, line_z(xs)))
        T = V((tip_x * sx, y_arm, line_z(tip_x)))
        d = T - S
        J[f"clavicle_{side}"] = V((0.02 * Hb * sx, J["spine_03"].y, S.z - 0.01 * Hb))
        J[f"upperarm_{side}"] = S
        J[f"lowerarm_{side}"] = S + d * 0.43 + V((0, 0.008 * Hb, 0))
        J[f"hand_{side}"] = S + d * 0.76
        J[f"hand_end_{side}"] = S + d * 0.95

        # ---- leg: feet from the lowest vertices, hip from proportions
        foot = [c for c in co if c.z < 0.06 * Hb and c.x * sx > 0.0]
        fx = st.fmean(c.x for c in foot)
        ymin = min(c.y for c in foot)   # toes (front = -Y)
        ymax = max(c.y for c in foot)   # heel
        flen = ymax - ymin
        A = V((fx, ymax - 0.28 * flen, 0.048 * Hb))
        hip = V((0.055 * Hb * sx, J["pelvis"].y, 0.515 * Hb))
        t = (0.515 - 0.285) / (0.515 - 0.048)
        K = hip.lerp(A, t) + V((0, -0.012 * Hb, 0))
        J[f"thigh_{side}"] = hip
        J[f"calf_{side}"] = K
        J[f"foot_{side}"] = A
        J[f"ball_{side}"] = V((fx, ymin + 0.3 * flen, 0.016 * Hb))
        J[f"ball_end_{side}"] = V((fx, ymin, 0.016 * Hb))
    return J


# approximate limb thickness per bone, as a fraction of the body height (Hb)
BONE_RADIUS = {
    "pelvis": 0.075, "spine_01": 0.075, "spine_02": 0.08, "spine_03": 0.085, "neck_01": 0.035, "head": 0.06,
    "clavicle": 0.035, "upperarm": 0.03, "lowerarm": 0.026, "hand": 0.022,
    "thigh": 0.05, "calf": 0.036, "foot": 0.03, "ball": 0.022,
}


def skin_weights(mesh, arm, Hb, k=3, power=4.0, smooth_iters=4):
    """Rigid-free skinning that tolerates the non-manifold AI meshes where Blender's heat weighting fails.

    Each vertex is weighted by its distance to every bone segment divided by that limb's thickness,
    restricted to its own side of the body, limited to the k strongest bones and smoothed along mesh edges.
    """
    import numpy as np

    deform = [b for b in arm.data.bones if b.name != "root"]
    P = np.array([v.co[:] for v in mesh.data.vertices])
    A = np.array([b.head_local[:] for b in deform])
    B = np.array([b.tail_local[:] for b in deform])
    AB = B - A
    t = np.clip(((P[:, None, :] - A[None]) * AB[None]).sum(2) / (AB ** 2).sum(1)[None], 0.0, 1.0)
    d = np.linalg.norm(P[:, None, :] - (A[None] + t[..., None] * AB[None]), axis=2)
    base = [b.name[:-2] if b.name.endswith(("_l", "_r")) else b.name for b in deform]
    r = np.array([BONE_RADIUS[n] * Hb for n in base])
    side = np.array([1 if b.name.endswith("_l") else (-1 if b.name.endswith("_r") else 0) for b in deform])
    x = P[:, 0:1]
    mask = np.ones(d.shape, bool)
    mask[:, side == 1] &= x > -0.01 * Hb
    mask[:, side == -1] &= x < 0.01 * Hb
    w = np.where(mask, 1.0 / ((d / r[None]) ** power + 1e-6), 0.0)
    drop = np.argsort(-w, axis=1)[:, k:]
    np.put_along_axis(w, drop, 0.0, axis=1)
    w /= w.sum(1, keepdims=True)
    E = np.array([e.vertices[:] for e in mesh.data.edges])
    deg = np.zeros(len(P))
    np.add.at(deg, E[:, 0], 1)
    np.add.at(deg, E[:, 1], 1)
    for _ in range(smooth_iters):
        acc = np.zeros_like(w)
        np.add.at(acc, E[:, 0], w[E[:, 1]])
        np.add.at(acc, E[:, 1], w[E[:, 0]])
        w = np.where(mask, 0.5 * w + 0.5 * acc / np.maximum(deg, 1)[:, None], 0.0)
        w /= w.sum(1, keepdims=True)
    w[w < 0.02] = 0.0
    w /= w.sum(1, keepdims=True)

    mesh.vertex_groups.clear()
    for j, b in enumerate(deform):
        vg = mesh.vertex_groups.new(name=b.name)
        for i in np.nonzero(w[:, j])[0]:
            vg.add([int(i)], float(w[i, j]), "REPLACE")
    mesh.parent = arm
    mod = mesh.modifiers.new("Armature", "ARMATURE")
    mod.object = arm
    unweighted = int((w.sum(1) < 0.99).sum())
    return unweighted, len(deform)


def build_all():
    root = collection("Heroes")
    out = {}
    for cfg in CHARS:
        coll = collection(f"Hero_{cfg['id']}", root)
        mesh = import_mesh(cfg, coll)
        J = estimate_joints(mesh, cfg)
        arm = build_heroes.build_armature(f"SKEL_{cfg['id']}", J, coll)
        unweighted, groups = skin_weights(mesh, arm, cfg["height"] * cfg["skull"])
        arm.location.x = cfg["x"]
        coll["joints"] = {k: tuple(round(c, 4) for c in v) for k, v in J.items()}
        out[cfg["id"]] = (arm, mesh)
        print(f"PERSONAGEM {cfg['id']}: verts={len(mesh.data.vertices)} groups={groups} unweighted={unweighted} "
              f"dims={tuple(round(d, 2) for d in mesh.dimensions)}")
    return out
