"""Step 3: ABP_Hero for the Quaternius skeleton = template locomotion graph driven by Quaternius animations.

ABP_Unarmed (Manny) is retargeted onto the UAL skeleton, then every retargeted Manny clip is consolidated into
the matching Universal Animation Library clip, so the graph/blendspace end up playing Quaternius animations.
"""
import importlib.util

import unreal

eal = unreal.EditorAssetLibrary
spec = importlib.util.spec_from_file_location("sh", r"D:\meus documentos\Fortnite\Unreal\ue_setup_heroes.py")
sh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sh)

UAL_MESH = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_Standard"
UAL = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/Animations/UAL1_Standard"  # + clip name
OUT = "/Game/Quaternius/Anims/Hero"
sh.RIGS = "/Game/Quaternius/Retarget"


def ual(clip):
    """Exact UAL clip lookup: assets are named UAL1_Standard<Clip> / UAL2_Standard<Clip>."""
    names = (f"UAL1_Standard{clip}", f"UAL2_Standard{clip}")
    hits = [p.split(".")[0] for p in eal.list_assets("/Game/Quaternius/Animations", recursive=True)
            if p.split(".")[-1] in names]
    return eal.load_asset(hits[0]) if hits else None


manny = eal.load_asset(sh.MANNY)
ual_mesh = eal.load_asset(UAL_MESH)
ik_manny, *_ = sh.make_ik_rig("IK_Mannequin", manny, manual_ok=False)
ik_ual, auto, chains, root = sh.make_ik_rig("IK_UAL", ual_mesh, manual_ok=False)
print(f"IK_UAL auto={auto} root={root} chains={len(chains)}")
rtg, _ = sh.make_retargeter("UAL", ik_manny, ik_ual, manny, ual_mesh)

if eal.does_directory_exist(OUT):
    eal.delete_directory(OUT)
res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
    [eal.find_asset_data(sh.ABP)], manny, ual_mesh, rtg, "", "", "", "_Hero", OUT, False, True, True)
print("retargeted:", len(res))

mapping = {"MM_Idle": "Idle_Loop", "MM_Jump": "Jump_Start", "MM_Fall_Loop": "Jump_Loop", "MM_Land": "Jump_Land"}
for p in eal.list_assets(OUT, recursive=True):
    name = p.split(".")[-1]
    if str(eal.find_asset_data(p).asset_class_path.asset_name) != "AnimSequence":
        continue
    base = name[:-len("_Hero")]
    if base in mapping:
        target = ual(mapping[base])
    elif "_Walk_" in base:
        target = ual("Walk_Loop")
    elif "_Jog_" in base:
        target = ual("Jog_Fwd_Loop")
    else:
        print("  unmapped:", name)
        continue
    ok = eal.consolidate_assets(target, [eal.load_asset(p.split(".")[0])])
    print(f"  {name} -> {target.get_name()} ok={ok}")

abp = eal.load_asset(f"{OUT}/ABP_Unarmed_Hero")
if abp:
    eal.rename_asset(abp.get_path_name().split(".")[0], f"{OUT}/ABP_Hero")
abp = eal.load_asset(f"{OUT}/ABP_Hero")
unreal.BlueprintEditorLibrary.compile_blueprint(abp)
left = [p.split(".")[-1] for p in eal.list_assets(OUT, recursive=True)]
print("ABP_Hero:", abp is not None, "| remaining in folder:", left)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
