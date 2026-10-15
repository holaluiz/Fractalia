"""Builds the user's characters in a fresh scene, renders a skeleton overlay and a deformation test pose."""
import math
import os
import sys
import traceback

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.append(HERE)
OUT = os.path.join(ROOT, "Export", "Previews", "Personagens")


def bone_sticks(arm, coll, mat):
    from nexus_lib import bm_cone, frame, make_obj
    objs = []
    for b in arm.data.bones:
        h = arm.matrix_world @ b.head_local
        t = arm.matrix_world @ b.tail_local
        d = t - h
        bm = bm_cone(0.018, 0.006, d.length, segs=6)
        objs.append(make_obj(f"STICK_{arm.name}_{b.name}", bm, mat, coll, frame((h + t) / 2, d), smooth=False))
        bm2 = bm_cone(0.022, 0.022, 0.03, segs=8)
        objs.append(make_obj(f"JOINT_{arm.name}_{b.name}", bm2, mat, coll, frame(h, d), smooth=False))
    return objs


def pose_test(arm):
    """Arms down, elbow/knee bends, a step: deforms the mesh like a gameplay animation would."""
    pb = arm.pose.bones

    def rot(name, axis, deg):
        b = pb[name]
        bpy.context.view_layer.update()
        m = b.matrix.copy()
        pivot = m.translation.copy()
        r = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-pivot)
        b.matrix = r @ m
        bpy.context.view_layer.update()

    rot("upperarm_l", "Y", 55)
    rot("upperarm_r", "Y", -55)
    rot("lowerarm_l", "Z", 35)
    rot("lowerarm_r", "Z", -35)
    rot("thigh_l", "X", -35)
    rot("calf_l", "X", 55)
    rot("thigh_r", "X", 18)
    rot("spine_02", "Z", 12)
    rot("head", "X", -10)


MODE = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "rig"

try:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import nexus_lib
    import build_personagens
    import render_previews as rp
    chars = build_personagens.build_all()
    for cid, (arm, mesh) in chars.items():
        arm.location.x = 0.0
    bpy.context.view_layer.update()
    sc = bpy.context.scene
    for cid, (arm, mesh) in chars.items():
        # hide the other characters
        for oid, (a2, m2) in chars.items():
            for o in (a2, m2):
                o.hide_render = oid != cid
        h = mesh.dimensions.z
        if MODE == "pose":
            # Workbench: EEVEE crashes this machine's AMD driver while the GPU is shared with the live Blender
            sc.render.engine = "BLENDER_WORKBENCH"
            sc.display.shading.light = "STUDIO"
            sc.display.shading.color_type = "TEXTURE"
            sc.display.shading.show_xray = False
            sc.display.shading.show_shadows = True
            sc.render.resolution_x = sc.render.resolution_y = 900
            pose_test(arm)
            for tag, loc in (("a", (1.6, -3.6, 1.5)), ("b", (-2.6, -2.4, 1.2))):
                rp.add_camera(loc, (0, 0, h * 0.5), lens=45)
                rp.render(os.path.join(OUT, f"pose_{cid}_{tag}.png"))
            for b in arm.pose.bones:
                b.matrix_basis = Matrix.Identity(4)
            continue
        # 1) skeleton overlay (workbench x-ray)
        coll = nexus_lib.collection("_Sticks")
        red = nexus_lib.mat("M_Stick", "#FF2020", 0.5, emit="#FF2020", emit_strength=1.0)
        sticks = bone_sticks(arm, coll, red)
        sc.render.engine = "BLENDER_WORKBENCH"
        sc.display.shading.light = "STUDIO"
        sc.display.shading.color_type = "MATERIAL"
        sc.display.shading.show_xray = True
        sc.display.shading.xray_alpha = 0.45
        sc.render.resolution_x = sc.render.resolution_y = 900
        h = mesh.dimensions.z
        for tag, d in (("front", Vector((0, -1, 0.05))), ("side", Vector((1, 0, 0.05)))):
            rp.add_camera(tuple(Vector((0, 0, h / 2)) + d.normalized() * h * 1.9), (0, 0, h / 2), lens=50)
            rp.render(os.path.join(OUT, f"rig_{cid}_{tag}.png"))
        for o in sticks:
            bpy.data.objects.remove(o, do_unlink=True)
    print("TEST_OK")
except Exception:
    traceback.print_exc()
    print("TEST_FAIL")
