"""Screenshot of the PIE game view (ue_capture.py's CaptureViewport only sees the editor world, and --editor grabs the
whole window, which other floating windows can cover).

Usage:  python ue_py.py -c "AIM=(pitch, yaw); OUT=r'C:/tmp/shot.png'; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_capture.py').read())"
AIM (optional) turns the player's control rotation first, so the third-person camera looks that way.
DELAY (optional, s) waits that long in game before grabbing the frame (e.g. to catch the middle of an animation).
Python cannot spawn actors into the PIE world (no SceneCapture), so this renders the player view off-screen at 1280x720.
"""
import os

import unreal

OUT = globals().get("OUT", os.path.join(os.environ.get("TEMP", "C:/Temp"), "pie_capture.png"))
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
if "AIM" in globals():
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=AIM[0], yaw=AIM[1]))
unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, OUT, None, False, False, unreal.ComparisonTolerance.LOW, "",
                                                  float(globals().get("DELAY", 0.0)))
print("screenshot queued:", OUT)
