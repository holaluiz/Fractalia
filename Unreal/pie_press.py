"""Inject an Enhanced Input action into the PIE player (tests the real input bindings).

Usage: ue_py.py pie_press.py   with env-free default IA_Jump; edit ACTION below or pass via -c wrapper.
"""
import unreal

ACTION = globals().get("ACTION", "/Game/Input/Actions/IA_Jump.IA_Jump")
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(w, 0)
subs = [o for o in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem)
        if "PIE" in o.get_path_name() or "LocalPlayer" in o.get_path_name()]
print("subsystems:", [o.get_path_name() for o in subs])
sub = subs[-1]
ia = unreal.load_object(None, ACTION)
sub.inject_input_vector_for_action(ia, unreal.Vector(1.0, 0.0, 0.0), [], [])
print("injected", ia.get_name(), "into", pc.get_name())
