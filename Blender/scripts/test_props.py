import os
import sys
import traceback

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import build_props
    import render_previews as rp
    build_props.build_all()
    for c in bpy.data.collections:
        if c.name.startswith("Prop_"):
            objs = list(c.objects)
            main = [o for o in objs if not o.name.startswith("UCX_")]
            ucx = [o for o in objs if o.name.startswith("UCX_")]
            mo = main[0]
            print(f"PROP {mo.name}: verts={len(mo.data.vertices)} mats={len(mo.data.materials)} "
                  f"ucx={len(ucx)} dims={tuple(round(d, 2) for d in mo.dimensions)}")
    rp.setup_render((1600, 900))
    g = rp.ground(200)
    rp.standard_lights((4, 20, 0), 3.0)
    rp.add_camera((4, -14, 14), (4, 18, 1.5), lens=30)
    rp.render(os.path.join(ROOT, "Export", "Previews", "props_overview.png"))
    rp.add_camera((-6.5, 8, 3.2), (-6.5, 17, 0.5), lens=40)
    rp.render(os.path.join(ROOT, "Export", "Previews", "props_loot.png"))
    rp.add_camera((0, -6, 7), (0, 9, 1.5), lens=28)
    rp.render(os.path.join(ROOT, "Export", "Previews", "props_build.png"))
    rp.add_camera((0, 12, 9), (0, 34, 4), lens=26)
    rp.render(os.path.join(ROOT, "Export", "Previews", "props_objectives.png"))
    print("TEST_OK")
except Exception:
    traceback.print_exc()
    print("TEST_FAIL")
