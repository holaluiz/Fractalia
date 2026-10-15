# Live Blender: front view on the hero lineup, armatures drawn behind the meshes.
import math

import bpy
from mathutils import Euler, Vector

win = bpy.context.window_manager.windows[0]
for o in win.scene.objects:
    if o.type == "ARMATURE":
        o.show_in_front = False
for area in win.screen.areas:
    if area.type == "VIEW_3D":
        sp = area.spaces.active
        r3d = sp.region_3d
        r3d.view_perspective = "PERSP"
        r3d.view_location = Vector((0.6, 0.0, 1.15))
        r3d.view_rotation = Euler((math.radians(82), 0, 0)).to_quaternion()
        r3d.view_distance = 10.5
        sp.overlay.show_extras = False
        area.tag_redraw()
print("view set")
