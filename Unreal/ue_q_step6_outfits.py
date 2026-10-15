"""Step 6: Quaternius fantasy outfits on the heroes (body becomes head-only through an opacity-masked material)."""
import glob
import importlib.util
import os

import unreal

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


q = load("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
m5 = None  # material helpers live in step 5 (imported lazily below)
SKEL = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_Standard_Skeleton"
OUT = "/Game/Quaternius/Outfits"
CH = "/Game/Quaternius/Characters"
MAT = "/Game/NexusRoyale/Materials"
BPS = "/Game/NexusRoyale/Blueprints"
ABP = "/Game/Quaternius/Anims/Hero/ABP_Hero"
SRC = rf"{q.QROOT}\ModularOutfitsFantasy\Modular Character Outfits - Fantasy[Standard]\Exports\glTF (Godot-Unreal)"

# --- 1) import outfits + modular parts on the shared skeleton
def skm(folder):
    hits = [p.split(".")[0] for p in eal.list_assets(folder, recursive=True)
            if str(eal.find_asset_data(p).asset_class_path.asset_name) == "SkeletalMesh"]
    return eal.load_asset(hits[0]) if hits else None


# import only what is missing, saving + collecting garbage after each file (the editor ran out of memory once)
skel = eal.load_asset(SKEL)
for sub in ("Outfits", "Modular Parts"):
    for f in glob.glob(glob.escape(rf"{SRC}\{sub}") + r"\*.gltf"):
        name = os.path.splitext(os.path.basename(f))[0]
        dest = f"{OUT}/{'Parts' if sub == 'Modular Parts' else 'Full'}/{name}"
        if eal.does_directory_exist(dest) and skm(dest) is not None:
            continue
        if eal.does_directory_exist(dest):
            eal.delete_directory(dest)
        q.import_interchange(f, dest, skeleton=skel)
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        unreal.SystemLibrary.collect_garbage()
        print("imported", name)

print("outfit meshes:", len([p for p in eal.list_assets(OUT, recursive=True)
                             if str(eal.find_asset_data(p).asset_class_path.asset_name) == "SkeletalMesh"]))

# --- 2) head-only material: masked, opacity from the pre-skinned height (vertex interpolator)
m5 = load("m5", r"D:\meus documentos\Fortnite\Unreal\ue_q_step5_materials.py") if False else None


def build_head():
    path = f"{MAT}/M_HeroHead"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    m = at.create_asset("M_HeroHead", MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("used_with_skeletal_mesh", True)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)

    def e(cls, x, y, **kw):
        n = mel.create_material_expression(m, cls, x, y)
        for k, v in kw.items():
            n.set_editor_property(k, v)
        return n

    def ln(a, ao, b, bi):
        assert mel.connect_material_expressions(a, ao, b, bi), f"{a.get_name()}.{ao}->{b.get_name()}.{bi}"

    skin = e(unreal.MaterialExpressionTextureSampleParameter2D, -600, -200, parameter_name="SkinTex",
             texture=eal.load_asset(f"{CH}/Superhero_Male_FullBody/T_Superhero_Male_Dark"))
    nrm = e(unreal.MaterialExpressionTextureSampleParameter2D, -600, 100, parameter_name="NormalTex",
            texture=eal.load_asset(f"{CH}/Superhero_Male_FullBody/T_Superhero_Male_Normal"),
            sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    rgh = e(unreal.MaterialExpressionTextureSampleParameter2D, -600, 350, parameter_name="RoughTex",
            texture=eal.load_asset(f"{CH}/Superhero_Male_FullBody/T_Superhero_Male_Roughness"))
    pre = e(unreal.MaterialExpressionPreSkinnedPosition, -1100, 600)
    vi = e(unreal.MaterialExpressionVertexInterpolator, -950, 600)
    ln(pre, "", vi, "VS")
    z = e(unreal.MaterialExpressionComponentMask, -800, 600, r=False, g=False, b=True, a=False)
    ln(vi, "PS", z, "")
    cut = e(unreal.MaterialExpressionScalarParameter, -800, 750, parameter_name="CutZ", default_value=143.0)
    sub = e(unreal.MaterialExpressionSubtract, -600, 650)
    ln(z, "", sub, "A")
    ln(cut, "", sub, "B")
    mel.connect_material_property(skin, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(nrm, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(rgh, "R", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(sub, "", unreal.MaterialProperty.MP_OPACITY_MASK)  # visible where z > CutZ
    m.set_editor_property("opacity_mask_clip_value", 0.0)
    mel.layout_material_expressions(m)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def head_instance(parent, name, fem):
    path = f"{MAT}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    mi = at.create_asset(name, MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    if fem:
        base = f"{CH}/Superhero_Female_FullBody"
        mel.set_material_instance_texture_parameter_value(mi, "SkinTex", eal.load_asset(f"{base}/T_Superhero_Female_Dark_BaseColor"))
        mel.set_material_instance_texture_parameter_value(mi, "NormalTex", eal.load_asset(f"{base}/T_Superhero_Female_Normal"))
        mel.set_material_instance_texture_parameter_value(mi, "RoughTex", eal.load_asset(f"{base}/T_Superhero_Female_Roughness"))
    mel.set_material_instance_scalar_parameter_value(mi, "CutZ", 139.0 if fem else 143.0)
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    return mi


head = build_head()
mi_head = {False: head_instance(head, "MI_Head_Male", False), True: head_instance(head, "MI_Head_Female", True)}

# --- 3) dress the heroes
LOOK = {  # outfit components (folders under OUT), extra hair, female?
    "Brakka": (["Parts/Male_Ranger_Body", "Parts/Male_Ranger_Arms", "Parts/Male_Ranger_Legs",
                "Parts/Male_Ranger_Feet_Boots", "Parts/Male_Ranger_Acc_Pauldron"], ["Hair_Buzzed", "Hair_Beard"], False),
    "Vela": (["Full/Female_Ranger"], [], True),
    "Zephyr": (["Full/Male_Peasant"], ["Hair_SimpleParted"], False),
    "Lumi": (["Full/Female_Peasant"], ["Hair_Buns"], True),
}
abp_class = eal.load_asset(ABP).generated_class()
for hero, (outfit, hair, fem) in LOOK.items():
    bp = eal.load_asset(f"{BPS}/BP_Hero_{hero}")
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    mesh_h = next(h for h in handles if str(lib.get_variable_name(lib.get_data(h))) in ("Mesh", "CharacterMesh0"))
    # drop previously added skeletal components (hair/outfits) and rebuild
    old = [h for h in handles if str(lib.get_variable_name(lib.get_data(h))).startswith(("Hair_", "Outfit_"))]
    if old:
        sds.delete_subobjects(handles[0], old, bp)
    mi_hair = eal.load_asset(f"{MAT}/MI_Hair_{hero}")
    cdo_mesh = unreal.get_default_object(bp.generated_class()).get_editor_property("mesh")
    cdo_mesh.set_editor_property("override_materials", [mi_hair, None, mi_head[fem]])
    for part in outfit + hair:
        folder = f"{OUT}/{part}" if "/" in part else f"{CH}/{part}"
        mesh = skm(folder)
        if mesh is None:
            print(f"  {hero}: missing {part}")
            continue
        handle, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(
            parent_handle=mesh_h, new_class=unreal.SkeletalMeshComponent, blueprint_context=bp))
        label = ("Outfit_" if "/" in part else "") + part.split("/")[-1]
        sds.rename_subobject(handle, unreal.Text(label))
        comp = lib.get_object(lib.get_data(handle))
        comp.set_editor_property("skeletal_mesh_asset", mesh)
        comp.set_editor_property("anim_class", abp_class)
        if "/" not in part:
            comp.set_editor_property("override_materials", [mi_hair])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    names = [str(lib.get_variable_name(lib.get_data(h))) for h in sds.k2_gather_subobject_data_for_blueprint(bp)]
    print(f"HERO {hero}: {[n for n in names if n.startswith(('Outfit_', 'Hair_'))]}")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
