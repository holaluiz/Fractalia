"""Builds every Nexus Royale asset, exports FBX and saves the .blend. Previews: render_all.py.

Headless:  blender --background --factory-startup --python build_all.py
Option (after "--"):  --no-export
"""
import importlib
import os
import sys
import traceback

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.append(HERE)

import nexus_lib  # noqa: E402
import build_heroes  # noqa: E402
import build_personagens  # noqa: E402
import build_props  # noqa: E402
import build_map  # noqa: E402
import export_fbx  # noqa: E402

for mod in (nexus_lib, build_heroes, build_personagens, build_props, build_map, export_fbx):
    importlib.reload(mod)

BLEND = os.path.join(ROOT, "Blender", "NexusRoyale_Assets.blend")
EXPORT = os.path.join(ROOT, "Export")


def main(argv):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "NexusRoyale"
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0

    heroes = build_heroes.build_all()
    chars = build_personagens.build_all()
    build_props.build_all()
    island, items = build_map.build_all(os.path.join(EXPORT, "map_layout.json"))
    print(f"BUILD heroes={len(heroes)} personagens={len(chars)} map_items={len(items)} "
          f"island_verts={len(island.data.vertices)}")

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("SAVED", BLEND)

    if "--no-export" not in argv:
        # export from a centimeter version of the scene; the saved .blend stays in meters
        export_fbx.to_centimeters()
        names = [n for n, *_ in build_heroes.HEROES] + [c["id"] for c in build_personagens.CHARS]
        for p in export_fbx.export_all(os.path.join(EXPORT, "FBX"), names):
            print("EXPORTED", p)


if __name__ == "__main__":
    try:
        main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
        print("BUILD_ALL_OK")
    except Exception:
        traceback.print_exc()
        print("BUILD_ALL_FAIL")
