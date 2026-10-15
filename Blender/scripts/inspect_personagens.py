"""Inspect + preview-render the user's character FBX files (Personagens/)."""
import glob
import math
import os
import sys
import traceback

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.append(HERE)
import render_previews as rp  # noqa: E402

SRC = os.path.join(ROOT, "Personagens")
OUT = os.path.join(ROOT, "Export", "Previews", "Personagens")
os.makedirs(OUT, exist_ok=True)


def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


for fbx in sorted(glob.glob(os.path.join(SRC, "*", "*.fbx"))):
    name = os.path.basename(os.path.dirname(fbx))
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=fbx)
        bpy.context.view_layer.update()
        objs = list(bpy.context.scene.objects)
        print(f"=== {name} ===")
        for o in objs:
            line = (f"  {o.type:9s} {o.name!r} parent={o.parent.name if o.parent else None} "
                    f"loc={tuple(round(v, 3) for v in o.location)} rot={tuple(round(math.degrees(v), 1) for v in o.rotation_euler)} "
                    f"scale={tuple(round(v, 4) for v in o.scale)} dims={tuple(round(v, 3) for v in o.dimensions)}")
            if o.type == "MESH":
                me = o.data
                line += (f"\n            verts={len(me.vertices)} tris~={sum(len(p.vertices) - 2 for p in me.polygons)} "
                         f"uv={[u.name for u in me.uv_layers]} mats={[m.name if m else None for m in me.materials]} "
                         f"vgroups={len(o.vertex_groups)} mods={[m.type for m in o.modifiers]} "
                         f"shapekeys={len(me.shape_keys.key_blocks) if me.shape_keys else 0}")
            if o.type == "ARMATURE":
                bones = o.data.bones
                line += f"\n            bones={len(bones)} roots={[b.name for b in bones if b.parent is None]}"
                line += f"\n            names={[b.name for b in bones][:80]}"
            print(line)
        for img in bpy.data.images:
            print(f"  IMAGE {img.name!r} size={tuple(img.size)} path={img.filepath}")
        for a in bpy.data.actions:
            print(f"  ACTION {a.name!r} frames={tuple(a.frame_range)}")
        mn, mx = world_bbox(objs)
        print(f"  BBOX min={tuple(round(v, 3) for v in mn)} max={tuple(round(v, 3) for v in mx)}")

        # preview render: front + side, camera fitted to the bbox
        c = (mn + mx) / 2
        size = max((mx - mn).length, 0.01)
        rp.setup_render((900, 900), samples=24)
        rp.ground(size * 20)
        bpy.data.objects["PRV_Ground"].location.z = mn.z
        rp.standard_lights(tuple(c), size / 2.0)
        for tag, d in (("front", Vector((0, -1, 0.15))), ("side", Vector((1, -0.25, 0.1))), ("back", Vector((0, 1, 0.1)))):
            d.normalize()
            rp.add_camera(tuple(c + d * size * 1.9), tuple(c), lens=50)
            rp.render(os.path.join(OUT, f"{name}_{tag}.png"))
    except Exception:
        traceback.print_exc()
        print(f"FAILED {name}")
print("INSPECT_DONE")
