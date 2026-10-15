"""Make every imported hero playable: IK Rigs + Retargeters (Manny -> hero), retargeted ABP_Unarmed,
and a BP_Hero_<Name> child of the template character using the hero mesh + its retargeted AnimBP."""
import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
SRC, TGT = unreal.RetargetSourceOrTarget.SOURCE, unreal.RetargetSourceOrTarget.TARGET

ROOT = "/Game/NexusRoyale"
RIGS = f"{ROOT}/Retarget"
BPS = f"{ROOT}/Blueprints"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
ABP = "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed"
PARENT_BP = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
HEROES = ["Caramelo", "Boto", "PombaGira", "Brakka", "Vela", "Zephyr", "Lumi", "Guardian"]

# our skeletons use UE4-mannequin bone names; chain names follow the auto-generated mannequin rig
MANUAL_CHAINS = [("Spine", "spine_01", "spine_03"), ("Neck", "neck_01", "neck_01"), ("Head", "head", "head"),
                 ("LeftClavicle", "clavicle_l", "clavicle_l"), ("LeftArm", "upperarm_l", "hand_l"),
                 ("RightClavicle", "clavicle_r", "clavicle_r"), ("RightArm", "upperarm_r", "hand_r"),
                 ("LeftLeg", "thigh_l", "ball_l"), ("RightLeg", "thigh_r", "ball_r")]


def fresh(path):
    if eal.does_asset_exist(path):
        eal.delete_asset(path)


def make_ik_rig(name, mesh, manual_ok=True):
    fresh(f"{RIGS}/{name}")
    rig = at.create_asset(name, RIGS, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    c = unreal.IKRigController.get_controller(rig)
    c.set_skeletal_mesh(mesh)
    auto = c.apply_auto_generated_retarget_definition()
    chains = [str(ch.chain_name) for ch in c.get_retarget_chains()]
    if (not auto or len(chains) < 6) and manual_ok:
        for ch in list(c.get_retarget_chains()):
            c.remove_retarget_chain(ch.chain_name)
        c.set_retarget_root("pelvis")
        for chain, a, b in MANUAL_CHAINS:
            c.add_retarget_chain(chain, a, b, "")
        chains = [str(ch.chain_name) for ch in c.get_retarget_chains()]
    eal.save_loaded_asset(rig)
    return rig, auto, chains, str(c.get_retarget_root())


def make_retargeter(hero, ik_src, ik_tgt, src_mesh, tgt_mesh):
    path = f"{RIGS}/RTG_{hero}"
    fresh(path)
    rtg = at.create_asset(f"RTG_{hero}", RIGS, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rtg)
    rc.add_default_ops()
    rc.set_ik_rig(SRC, ik_src)
    rc.set_ik_rig(TGT, ik_tgt)
    rc.assign_ik_rig_to_all_ops(SRC, ik_src)
    rc.assign_ik_rig_to_all_ops(TGT, ik_tgt)
    rc.set_preview_mesh(SRC, src_mesh)
    rc.set_preview_mesh(TGT, tgt_mesh)
    rc.auto_map_chains(unreal.AutoMapChainType.FUZZY, True)
    rc.auto_align_all_bones(TGT)
    eal.save_loaded_asset(rtg)
    mapped = []
    for s in rc.get_all_chain_settings():
        mapped.append(f"{s.get_editor_property('target_chain')}<-{s.get_editor_property('source_chain')}")
    return rtg, mapped


def abp_path(hero):
    return f"{ROOT}/Anims/{hero}/ABP_Unarmed_{hero}"


def retarget_abp(hero, rtg, src_mesh, tgt_mesh):
    out_dir = f"{ROOT}/Anims/{hero}"
    if eal.does_directory_exist(out_dir):
        eal.delete_directory(out_dir)
    res = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
        [eal.find_asset_data(ABP)], src_mesh, tgt_mesh, rtg, "", "", "", f"_{hero}", out_dir, False, True, True)
    return eal.load_asset(abp_path(hero)), len(res)


def chain_map(hero):
    rc = unreal.IKRetargeterController.get_controller(eal.load_asset(f"{RIGS}/RTG_{hero}"))
    return [f"{s.get_editor_property('target_chain')}<-{s.get_editor_property('source_chain')}"
            for s in rc.get_all_chain_settings()]


def make_hero_bp(hero, mesh, abp):
    path = f"{BPS}/BP_Hero_{hero}"
    fresh(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", eal.load_blueprint_class(PARENT_BP))
    bp = at.create_asset(f"BP_Hero_{hero}", BPS, unreal.Blueprint, factory)
    cdo = unreal.get_default_object(bp.generated_class())
    comp = cdo.get_editor_property("mesh")
    comp.set_editor_property("skeletal_mesh_asset", mesh)
    comp.set_editor_property("anim_class", abp.generated_class())
    if hero == "Guardian":  # 3 m tall boss
        cap = cdo.get_editor_property("capsule_component")
        cap.set_editor_property("capsule_half_height", 150.0)
        cap.set_editor_property("capsule_radius", 70.0)
        comp.set_editor_property("relative_location", unreal.Vector(0, 0, -150))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    # verify the override survived the compile
    comp2 = unreal.get_default_object(bp.generated_class()).get_editor_property("mesh")
    m = comp2.get_editor_property("skeletal_mesh_asset")
    return bp, (m.get_name() if m else None), str(comp2.get_editor_property("anim_class"))


def main(heroes=HEROES, rebuild_rigs=True):
    manny = eal.load_asset(MANNY)
    if rebuild_rigs:
        ik_manny, auto, chains, root = make_ik_rig("IK_Mannequin", manny, manual_ok=False)
        print(f"IK_Mannequin auto={auto} root={root} chains={len(chains)}")
    for hero in heroes:
        mesh = eal.load_asset(f"{ROOT}/Heroes/SK_{hero}")
        n = 0
        if rebuild_rigs:
            ik, auto, chains, root = make_ik_rig(f"IK_{hero}", mesh)
            rtg, _ = make_retargeter(hero, ik_manny, ik, manny, mesh)
            abp, n = retarget_abp(hero, rtg, manny, mesh)
        else:
            abp = eal.load_asset(abp_path(hero))
        if abp is None:
            print(f"HERO {hero}: no ABP")
            continue
        bp, mesh_name, anim = make_hero_bp(hero, mesh, abp)
        print(f"HERO {hero}: retargeted={n} bp_mesh={mesh_name} anim={anim.split('.')[-1]} map={chain_map(hero)}")


if __name__ == "__main__":
    main()
