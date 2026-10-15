import os
import sys
import traceback

import bpy

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import build_heroes
    import render_previews as rp
    heroes = build_heroes.build_all()
    for name, (arm, mesh) in heroes.items():
        print(f"HERO {name}: verts={len(mesh.data.vertices)} mats={len(mesh.data.materials)} "
              f"groups={len(mesh.vertex_groups)} bones={len(arm.data.bones)} dims={tuple(round(d, 2) for d in mesh.dimensions)}")
    rp.setup_render((1600, 800))
    rp.ground()
    rp.standard_lights((0.6, 0, 1), 1.0)
    rp.add_camera((0.6, -10.5, 2.0), (0.6, 0, 1.25), lens=36)
    rp.render(os.path.join(ROOT, "Export", "Previews", "heroes_lineup.png"))
    rp.add_camera((-2.4, -4.2, 1.7), (-2.4, 0, 1.15), lens=50)
    rp.render(os.path.join(ROOT, "Export", "Previews", "heroes_close_a.png"))
    rp.add_camera((0.8, -4.2, 1.7), (0.8, 0, 1.15), lens=50)
    rp.render(os.path.join(ROOT, "Export", "Previews", "heroes_close_b.png"))
    print("TEST_OK")
except Exception:
    traceback.print_exc()
    print("TEST_FAIL")
