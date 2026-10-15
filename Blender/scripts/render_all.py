"""Preview renders of the saved NexusRoyale_Assets.blend (separate process: a GPU driver crash can't lose work).

blender --background "<...>/NexusRoyale_Assets.blend" --python render_all.py -- [eevee|workbench]
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.append(HERE)
import nexus_lib  # noqa: E402
import render_previews as rp  # noqa: E402

PREV = os.path.join(ROOT, "Export", "Previews")
ENGINE = (sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "eevee").lower()


def water(size=1400.0, center=(0, 420, -0.15)):
    me = bpy.data.meshes.get("PRV_Water") or bpy.data.meshes.new("PRV_Water")
    if not me.vertices:
        h = size / 2
        me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
        me.materials.append(nexus_lib.mat("PRV_WaterMat", "#2E8FD8", 0.15))
    ob = bpy.data.objects.get("PRV_Water") or bpy.data.objects.new("PRV_Water", me)
    c = rp.preview_collection()
    if ob.name not in c.objects:
        c.objects.link(ob)
    ob.location = center


def engine():
    rp.setup_render((1600, 900))
    if ENGINE == "workbench":
        sc = bpy.context.scene
        sc.render.engine = "BLENDER_WORKBENCH"
        sc.display.shading.light = "STUDIO"
        sc.display.shading.color_type = "TEXTURE"
        sc.display.shading.show_shadows = True


engine()
rp.ground(80)
water()
rp.standard_lights((4.0, 0, 1), 1.4)
rp.only_visible(["Heroes"])
rp.add_camera((4.0, -16.5, 2.3), (4.0, 0, 1.2), lens=35)
rp.render(os.path.join(PREV, "heroes_lineup.png"))
rp.add_camera((9.2, -6.2, 1.8), (9.2, 0, 1.05), lens=40)
rp.render(os.path.join(PREV, "personagens_lineup.png"))
rp.only_visible(["Build", "Props"])
rp.standard_lights((4, 20, 0), 3.0)
rp.add_camera((4, -14, 14), (4, 18, 1.5), lens=30)
rp.render(os.path.join(PREV, "props_overview.png"))
rp.only_visible(["Map"])
rp.add_light("PRV_Sun", "SUN", (0, 420, 100), (48, 8, 40), 4.0)
rp.add_camera((-230, 420 - 290, 210), (10, 430, 0), lens=32)
rp.render(os.path.join(PREV, "map_overview.png"))
print("RENDER_ALL_OK")
