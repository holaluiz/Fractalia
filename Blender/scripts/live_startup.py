# Startup helper for the interactive Blender: starts the "MCP for Blender" server and frames the heroes.
import bpy


def _go():
    try:
        bpy.ops.blendermcp.start_server()
        print("[NexusRoyale] MCP for Blender server started")
    except Exception as e:  # add-on missing or disabled
        print("[NexusRoyale] could not start MCP server:", e)
    win = bpy.context.window_manager.windows[0]
    sc = win.scene
    vl = win.view_layer
    heroes = [o for o in sc.objects if o.name.startswith("SK_")]
    for o in sc.objects:
        o.select_set(False, view_layer=vl)
    for o in heroes:
        o.select_set(True, view_layer=vl)
    if heroes:
        vl.objects.active = heroes[0]
    for area in win.screen.areas:
        if area.type != "VIEW_3D":
            continue
        sp = area.spaces.active
        sp.shading.type = "MATERIAL"
        sp.clip_end = 5000
        region = next(r for r in area.regions if r.type == "WINDOW")
        with bpy.context.temp_override(window=win, area=area, region=region):
            bpy.ops.view3d.view_selected()
    return None


bpy.app.timers.register(_go, first_interval=1.5)
