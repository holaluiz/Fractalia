"""Creeps step 2: BP_Creep (AI-controlled Character) and the per-monster children (mesh, AnimBP, capsule)."""
import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
FOLDER = "/Game/NexusRoyale/Blueprints/Creeps"


def new_bp(name, parent_class):
    path = f"{FOLDER}/{name}"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent_class)
    return at.create_asset(name, FOLDER, unreal.Blueprint, f)


base = new_bp("BP_Creep", unreal.Character)
cdo = unreal.get_default_object(base.generated_class())
cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
cdo.set_editor_property("use_controller_rotation_yaw", False)
move = cdo.get_editor_property("character_movement")
move.set_editor_property("max_walk_speed", 420.0)
move.set_editor_property("orient_rotation_to_movement", True)
move.set_editor_property("rotation_rate", unreal.Rotator(0.0, 540.0, 0.0))
unreal.BlueprintEditorLibrary.compile_blueprint(base)
eal.save_loaded_asset(base)
print("BP_Creep ready:", base.get_path_name())

SPECS = {  # mesh height ~168 / 93 cm -> capsule half-heights
    "Imp": dict(half=86.0, radius=40.0),
    "Puglin": dict(half=48.0, radius=34.0),
}
for name, s in SPECS.items():
    bp = new_bp(f"BP_Creep_{name}", base.generated_class())
    c = unreal.get_default_object(bp.generated_class())
    mesh_path = [p.split(".")[0] for p in eal.list_assets(f"/Game/Quaternius/Creeps/{name}", recursive=True)
                 if str(eal.find_asset_data(p).asset_class_path.asset_name) == "SkeletalMesh"][0]
    comp = c.get_editor_property("mesh")
    comp.set_editor_property("skeletal_mesh_asset", eal.load_asset(mesh_path))
    comp.set_editor_property("anim_class", eal.load_asset(f"/Game/Quaternius/Creeps/{name}/Anims/ABP_Creep_{name}").generated_class())
    comp.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, -s["half"]))
    comp.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))  # Rotator() is (roll, pitch, yaw)
    cap = c.get_editor_property("capsule_component")
    cap.set_editor_property("capsule_half_height", s["half"])
    cap.set_editor_property("capsule_radius", s["radius"])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    print("child ready:", bp.get_path_name())
