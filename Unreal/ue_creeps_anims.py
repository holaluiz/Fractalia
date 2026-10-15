"""Creeps step 1: import the Bestiary monsters and give them Universal Animation Library motion.

Each monster keeps its own (55-bone) skeleton; UAL clips are retargeted with IK Rigs. The hero AnimBP is retargeted
too and its idle/walk are consolidated into the zombie clips, so ABP_Creep_<Name> shambles like a jungle creep.
"""
import importlib.util

import unreal

eal = unreal.EditorAssetLibrary


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


q = load("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
sh = load("sh", r"D:\meus documentos\Fortnite\Unreal\ue_setup_heroes.py")
sh.RIGS = "/Game/Quaternius/Retarget"
GLB = rf"{q.QROOT}\BestiaryDungeonMonsters\Bestiary - Dungeon Monsters Kit[Standard]\Exports\GLB (Godot-Unreal)"
DEST = "/Game/Quaternius/Creeps"
UAL_MESH = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_Standard"
ABP_HERO = "/Game/Quaternius/Anims/Hero/ABP_Hero"
EXTRA = ["Zombie_Idle_Loop", "Zombie_Walk_Fwd_Loop", "Zombie_Scratch", "Hit_Chest", "Death01", "Punch_Cross"]


def ual(clip):
    names = (f"UAL1_Standard{clip}", f"UAL2_Standard{clip}")
    hits = [p.split(".")[0] for p in eal.list_assets("/Game/Quaternius/Animations", recursive=True)
            if p.split(".")[-1] in names]
    return hits[0] if hits else None


def first(folder, cls):
    hits = [p.split(".")[0] for p in eal.list_assets(folder, recursive=True)
            if str(eal.find_asset_data(p).asset_class_path.asset_name) == cls]
    return hits[0] if hits else None


def named(folder, suffix):
    hits = [p.split(".")[0] for p in eal.list_assets(folder, recursive=True) if p.split(".")[-1].endswith(suffix)]
    return eal.load_asset(hits[0]) if hits else None


ual_mesh = eal.load_asset(UAL_MESH)
ik_ual = eal.load_asset(f"{sh.RIGS}/IK_UAL")
for name in ("Imp", "Puglin"):
    folder = f"{DEST}/{name}"
    if first(folder, "SkeletalMesh") is None:
        q.import_interchange(rf"{GLB}\{name}.glb", folder)
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        unreal.SystemLibrary.collect_garbage()
    mesh = eal.load_asset(first(folder, "SkeletalMesh"))
    ik, auto, chains, root = sh.make_ik_rig(f"IK_{name}", mesh, manual_ok=False)
    rtg, _ = sh.make_retargeter(f"UAL_{name}", ik_ual, ik, ual_mesh, mesh)
    out = f"{folder}/Anims"
    if eal.does_directory_exist(out):
        eal.delete_directory(out)
    assets = [eal.find_asset_data(ABP_HERO)] + [eal.find_asset_data(ual(c)) for c in EXTRA]
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        assets, ual_mesh, mesh, rtg, "", "", "", f"_{name}", out, False, True, True)
    # shamble: hero idle/walk -> zombie idle/walk (jog stays for chasing)
    for src_clip, dst_clip in (("Idle_Loop", "Zombie_Idle_Loop"), ("Walk_Loop", "Zombie_Walk_Fwd_Loop")):
        src = named(out, f"Standard{src_clip}_{name}")
        dst = named(out, f"Standard{dst_clip}_{name}")
        if src and dst:
            eal.consolidate_assets(dst, [src])
    abp = named(out, f"ABP_Hero_{name}")
    if abp:
        eal.rename_asset(abp.get_path_name().split(".")[0], f"{out}/ABP_Creep_{name}")
    abp = eal.load_asset(f"{out}/ABP_Creep_{name}")
    unreal.BlueprintEditorLibrary.compile_blueprint(abp)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    clips = sorted(p.split(".")[-1] for p in eal.list_assets(out) if
                   str(eal.find_asset_data(p).asset_class_path.asset_name) == "AnimSequence")
    bb = mesh.get_bounds()
    print(f"CREEP {name}: ik_auto={auto} chains={len(chains)} retargeted={len(res)} abp={abp is not None} "
          f"height={2 * bb.box_extent.z:.0f}cm clips={clips}")
unreal.SystemLibrary.collect_garbage()
