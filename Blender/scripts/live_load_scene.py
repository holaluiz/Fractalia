# Runs inside the live Blender (via live_send.py): appends the NexusRoyale scene and shows it.
import bpy

PATH = r"D:\meus documentos\Fortnite\Blender\NexusRoyale_Assets.blend"

sc = bpy.data.scenes.get("NexusRoyale")
if sc is None:
    with bpy.data.libraries.load(PATH, link=False) as (src, dst):
        dst.scenes = ["NexusRoyale"]
    sc = dst.scenes[0]

win = bpy.context.window_manager.windows[0]
win.scene = sc
vl = sc.view_layers[0]
heroes = [o for o in sc.objects if o.name.startswith("SK_")]
for o in sc.objects:
    o.select_set(False, view_layer=vl)
for o in heroes:
    o.select_set(True, view_layer=vl)
vl.objects.active = heroes[0] if heroes else None

framed = False
for area in win.screen.areas:
    if area.type != "VIEW_3D":
        continue
    sp = area.spaces.active
    sp.shading.type = "MATERIAL"
    sp.clip_end = 5000
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=win, area=area, region=region, scene=sc, view_layer=vl):
        bpy.ops.view3d.view_selected()
    framed = True

print("scene:", sc.name, "| objects:", len(sc.objects), "| heroes:", [o.name for o in heroes], "| framed:", framed)
print("collections:", [c.name for c in sc.collection.children])
