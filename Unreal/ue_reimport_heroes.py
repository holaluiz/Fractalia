"""Re-import the hero skeletal meshes (centimeter FBX, unscaled bones) and rebuild their retarget chain."""
import importlib.util
import json
import os

import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
AP = unreal.AnimPoseExtensions
ROOT = "/Game/NexusRoyale"
FBX = r"D:\meus documentos\Fortnite\Export\FBX\Heroes"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nx = load("nx", r"D:\meus documentos\Fortnite\Unreal\import_nexus_assets.py")
sh = load("sh", r"D:\meus documentos\Fortnite\Unreal\ue_setup_heroes.py")

# 1) drop references to the old hero assets
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.SkeletalMeshActor):
        eas.destroy_actor(a)
gm = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
gcdo = unreal.get_default_object(gm.generated_class())
gcdo.set_editor_property("default_pawn_class", eal.load_blueprint_class("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"))
for folder in (f"{ROOT}/Blueprints", f"{ROOT}/Anims", f"{ROOT}/Retarget"):
    if eal.does_directory_exist(folder):
        eal.delete_directory(folder)
for p in eal.list_assets(f"{ROOT}/Heroes", recursive=False):
    cls = str(eal.find_asset_data(p).asset_class_path.asset_name)
    if cls in ("SkeletalMesh", "Skeleton", "PhysicsAsset"):
        eal.delete_asset(p.split(".")[0])

# 2) re-import 1:1 and check the reference pose (root must be unscaled, pelvis ~95 cm high)
nx.use_legacy_fbx_importer()
for fn in sorted(os.listdir(FBX)):
    nx.import_fbx(os.path.join(FBX, fn), f"{ROOT}/Heroes", True)
for hero in sh.HEROES:
    mesh = eal.load_asset(f"{ROOT}/Heroes/SK_{hero}")
    pose = AP.get_reference_pose(mesh.get_editor_property("skeleton"))
    r = AP.get_bone_pose(pose, "root", unreal.AnimPoseSpaces.LOCAL)
    pel = AP.get_bone_pose(pose, "pelvis", unreal.AnimPoseSpaces.WORLD)
    head = AP.get_bone_pose(pose, "head", unreal.AnimPoseSpaces.LOCAL)
    print(f"REF {hero}: root_scale={r.scale3d.x:.2f} pelvis_z={pel.translation.z:.1f} head_local={head.translation.length():.1f}cm")

# 3) rigs, retargeters, retargeted AnimBPs and hero Blueprints
sh.main(rebuild_rigs=True)

# 4) default pawn + guardian back on the Nexus
gcdo.set_editor_property("default_pawn_class", eal.load_blueprint_class(f"{ROOT}/Blueprints/BP_Hero_Caramelo"))
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
with open(r"D:\meus documentos\Fortnite\Export\map_layout.json", encoding="utf-8") as f:
    for a in json.load(f)["actors"]:
        if a["type"] == "guardian_spawn":
            nx.spawn_mesh(eas, f"{ROOT}/Heroes/SK_Guardian", a["ue_location_cm"], a["ue_yaw"], 1.0,
                          label="Guardian", folder="Gameplay/guardian_spawn")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
print("DONE")
