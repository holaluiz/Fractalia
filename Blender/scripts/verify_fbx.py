import os

import bpy

FBX = r"D:\meus documentos\Fortnite\Export\FBX"
for rel in (r"Heroes\SK_Brakka.fbx", r"Props\SM_Build_Ramp.fbx", r"Map\SM_Island.fbx"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(FBX, rel))
    bpy.context.view_layer.update()
    for o in bpy.context.scene.objects:
        line = f"VERIFY {rel} | {o.type} {o.name} scale={tuple(round(s, 3) for s in o.scale)} " \
               f"dims={tuple(round(d, 2) for d in o.dimensions)}"
        if o.type == "ARMATURE":
            roots = [b.name for b in o.data.bones if b.parent is None]
            line += f" bones={len(o.data.bones)} roots={roots}"
        if o.type == "MESH":
            line += f" verts={len(o.data.vertices)} colattrs={[a.name for a in o.data.color_attributes]}"
        print(line)
    print(f"VERIFY {rel} | size={os.path.getsize(os.path.join(FBX, rel)) // 1024} KB")
