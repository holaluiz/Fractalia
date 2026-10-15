"""Step 1b: Universal Animation Library 2 animations onto the UAL1 skeleton."""
import importlib.util

import unreal

spec = importlib.util.spec_from_file_location("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
eal = unreal.EditorAssetLibrary
QA = "/Game/Quaternius"
SKEL = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_Standard_Skeleton"

skel = eal.load_asset(SKEL)
ual2 = rf"{q.QROOT}\UniversalAnimationLibrary2\Universal Animation Library 2[Standard]\Unreal-Godot\UAL2_Standard.glb"
if eal.does_directory_exist(f"{QA}/Animations/UAL2"):
    eal.delete_directory(f"{QA}/Animations/UAL2")
r2 = q.import_interchange(ual2, f"{QA}/Animations/UAL2", skeleton=skel)
print("UAL2 imported:", len(r2), "objects")
for folder in (f"{QA}/Animations/UAL1", f"{QA}/Animations/UAL2"):
    print(folder, "anims:", len(q.assets_in(folder, "AnimSequence")), "meshes:", q.assets_in(folder, "SkeletalMesh"),
          "skeletons:", q.assets_in(folder, "Skeleton"))
anims2 = q.assets_in(f"{QA}/Animations/UAL2", "AnimSequence")
if anims2:
    print("UAL2 anim skeleton:", eal.load_asset(anims2[0]).get_editor_property("skeleton").get_path_name())
print("UAL1 anim names:", sorted(p.split("/")[-1] for p in q.assets_in(f"{QA}/Animations/UAL1", "AnimSequence"))[:50])
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
