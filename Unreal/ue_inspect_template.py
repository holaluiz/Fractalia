import unreal

eal = unreal.EditorAssetLibrary
bp = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter")
cdo = unreal.get_default_object(bp.generated_class())
mesh_comp = cdo.get_editor_property("mesh")
print("mesh:", mesh_comp.get_editor_property("skeletal_mesh_asset").get_path_name() if mesh_comp.get_editor_property("skeletal_mesh_asset") else None)
print("anim class:", mesh_comp.get_editor_property("anim_class"))
print("mesh rel loc/rot:", mesh_comp.get_editor_property("relative_location"), mesh_comp.get_editor_property("relative_rotation"))
cap = cdo.get_editor_property("capsule_component")
print("capsule:", cap.get_editor_property("capsule_half_height"), cap.get_editor_property("capsule_radius"))
gm = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
gcdo = unreal.get_default_object(gm.generated_class())
print("game mode pawn:", gcdo.get_editor_property("default_pawn_class"))
print("controller:", gcdo.get_editor_property("player_controller_class"))
for folder in ("/Game/Characters/Mannequins/Rigs", "/Game/Characters/Mannequins/Meshes", "/Game/Characters/Mannequins/Anims/Unarmed"):
    print("==", folder)
    for p in eal.list_assets(folder, recursive=True)[:40]:
        print("  ", p.split(".")[0], "|", eal.find_asset_data(p).asset_class_path.asset_name)
