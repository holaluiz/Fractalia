"""Step 1: remove the old heroes from the game, import Universal Animation Library 1 + 2 on one skeleton."""
import importlib.util

import unreal

spec = importlib.util.spec_from_file_location("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ROOT = "/Game/NexusRoyale"
QA = "/Game/Quaternius"

# --- 0) old heroes out of the game (source files on disk are untouched)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Showcase_") or isinstance(a, unreal.SkeletalMeshActor):
        eas.destroy_actor(a)
gm = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
unreal.get_default_object(gm.generated_class()).set_editor_property(
    "default_pawn_class", eal.load_blueprint_class("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"))
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
eal.save_loaded_asset(gm)
for folder in (f"{ROOT}/Blueprints", f"{ROOT}/Anims", f"{ROOT}/Retarget"):
    if eal.does_directory_exist(folder):
        eal.delete_directory(folder)
kept = []
for p in eal.list_assets(f"{ROOT}/Heroes", recursive=True):
    path = p.split(".")[0]
    outside = [r for r in (eal.find_package_referencers_for_asset(path, False) or []) if not str(r).startswith(f"{ROOT}/Heroes")]
    if outside:
        kept.append(path)
    else:
        eal.delete_asset(path)
print("old heroes removed; kept (still referenced elsewhere):", kept)

# --- 1) Universal Animation Library 1 (mesh + skeleton + 43 anims), then UAL2 animations on the same skeleton
ual1 = rf"{q.QROOT}\UniversalAnimationLibrary\Universal Animation Library[Standard]\Unreal-Godot\UAL1_Standard.glb"
ual2 = rf"{q.QROOT}\UniversalAnimationLibrary2\Universal Animation Library 2[Standard]\Unreal-Godot\UAL2_Standard.glb"
for d in (f"{QA}/Animations",):
    if eal.does_directory_exist(d):
        eal.delete_directory(d)
r1 = q.import_interchange(ual1, f"{QA}/Animations/UAL1")
skels = q.assets_in(f"{QA}/Animations/UAL1", "Skeleton")
print("UAL1 imported:", len(r1), "objects; skeletons:", skels)
skel = eal.load_asset(skels[0])
r2 = q.import_interchange(ual2, f"{QA}/Animations/UAL2", skeleton=skel)
print("UAL2 imported:", len(r2), "objects")
for folder in (f"{QA}/Animations/UAL1", f"{QA}/Animations/UAL2"):
    anims = q.assets_in(folder, "AnimSequence")
    meshes = q.assets_in(folder, "SkeletalMesh")
    sk2 = q.assets_in(folder, "Skeleton")
    print(folder, "anims:", len(anims), "meshes:", meshes, "skeletons:", sk2)
a = eal.load_asset(q.assets_in(f"{QA}/Animations/UAL2", "AnimSequence")[0])
print("UAL2 anim skeleton:", a.get_editor_property("skeleton").get_path_name())
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
