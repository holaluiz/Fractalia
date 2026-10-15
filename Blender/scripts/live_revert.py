# Live Blender: reload the asset file from disk (after a headless rebuild), then re-apply the hero view.
import bpy


def _after():
    import runpy
    runpy.run_path(r"D:\meus documentos\Fortnite\Blender\scripts\live_view_heroes.py")
    return None


bpy.app.timers.register(_after, first_interval=1.0, persistent=True)
bpy.ops.wm.revert_mainfile()
print("reverted:", bpy.data.filepath)
