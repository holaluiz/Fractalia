"""Step 5: hero suit + hair materials (height-masked over the Quaternius base skin) and per-hero instances."""
import unreal

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
MAT = "/Game/NexusRoyale/Materials"
CH = "/Game/Quaternius/Characters"
BPS = "/Game/NexusRoyale/Blueprints"
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary


def hexcol(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return unreal.LinearColor(c[0], c[1], c[2], 1.0)


def new_material(name):
    path = f"{MAT}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    m = at.create_asset(name, MAT, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("used_with_skeletal_mesh", True)
    return m


def expr(m, cls, x, y, **props):
    e = mel.create_material_expression(m, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def link(a, a_out, b, b_in):
    if not mel.connect_material_expressions(a, a_out, b, b_in):
        raise RuntimeError(f"connect failed: {a.get_name()}.{a_out} -> {b.get_name()}.{b_in}")


def tex_param(m, name, tex, x, y, sampler=None):
    e = expr(m, unreal.MaterialExpressionTextureSampleParameter2D, x, y, parameter_name=name, texture=tex)
    if sampler is not None:
        e.set_editor_property("sampler_type", sampler)
    return e


def vec_param(m, name, color, x, y):
    return expr(m, unreal.MaterialExpressionVectorParameter, x, y, parameter_name=name, default_value=color)


def scalar_param(m, name, value, x, y):
    return expr(m, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=name, default_value=value)


def band(m, z, lo, hi, x, y, invert=False):
    """smoothstep(lo, hi, z) (or 1 - it)."""
    s = expr(m, unreal.MaterialExpressionSmoothStep, x, y)
    link(lo, "", s, "Min")
    link(hi, "", s, "Max")
    link(z, "", s, "Value")
    if not invert:
        return s
    o = expr(m, unreal.MaterialExpressionOneMinus, x + 150, y)
    link(s, "", o, "")
    return o


def add(m, a, b, x, y):
    e = expr(m, unreal.MaterialExpressionAdd, x, y)
    link(a, "", e, "A")
    link(b, "", e, "B")
    return e


def const(m, v, x, y):
    return expr(m, unreal.MaterialExpressionConstant, x, y, r=v)


def lerp(m, a, b, alpha, x, y):
    e = expr(m, unreal.MaterialExpressionLinearInterpolate, x, y)
    link(a, "", e, "A")
    link(b, "", e, "B")
    link(alpha, "", e, "Alpha")
    return e


def build_suit():
    skin = eal.load_asset(f"{CH}/Superhero_Male_FullBody/T_Superhero_Male_Dark")
    nrm = eal.load_asset(f"{CH}/Superhero_Male_FullBody/T_Superhero_Male_Normal")
    rgh = eal.load_asset(f"{CH}/Superhero_Male_FullBody/T_Superhero_Male_Roughness")
    m = new_material("M_HeroSuit")
    t_skin = tex_param(m, "SkinTex", skin, -1400, -300)
    t_nrm = tex_param(m, "NormalTex", nrm, -400, 500, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    t_rgh = tex_param(m, "RoughTex", rgh, -400, 300)
    suit = vec_param(m, "SuitColor", hexcol("#2F5DBA"), -1400, 0)
    boots = vec_param(m, "BootColor", hexcol("#2B2F3A"), -1400, 150)
    accent = vec_param(m, "AccentColor", hexcol("#E8B04A"), -1400, 300)
    neck = scalar_param(m, "NeckZ", 150.0, -1700, -150)
    boot_z = scalar_param(m, "BootZ", 16.0, -1700, 0)
    belt_z = scalar_param(m, "BeltZ", 100.0, -1700, 150)
    wrist = scalar_param(m, "GloveX", 62.0, -1700, 300)
    # pre-skinned position only exists in the vertex shader: hand it to the pixel shader via an interpolator
    pre = expr(m, unreal.MaterialExpressionPreSkinnedPosition, -1900, -350)
    pos = expr(m, unreal.MaterialExpressionVertexInterpolator, -1750, -350)
    link(pre, "", pos, "VS")
    z = expr(m, unreal.MaterialExpressionComponentMask, -1550, -350, r=False, g=False, b=True, a=False)
    link(pos, "PS", z, "")
    ax = expr(m, unreal.MaterialExpressionComponentMask, -1550, -450, r=True, g=False, b=False, a=False)
    link(pos, "PS", ax, "")
    absx = expr(m, unreal.MaterialExpressionAbs, -1450, -450)
    link(ax, "", absx, "")
    one = const(m, 1.5, -1700, 450)
    neg = const(m, -1.5, -1700, 520)
    # skin above the neck line
    skin_mask = band(m, z, add(m, neck, neg, -1300, -200), add(m, neck, one, -1300, -150), -1100, -200)
    # boots below BootZ, gloves beyond |x| > GloveX (arms are spread in the reference pose)
    boot_mask = band(m, z, add(m, boot_z, neg, -1300, 50), add(m, boot_z, one, -1300, 100), -1100, 50, invert=True)
    glove_mask = band(m, absx, add(m, wrist, neg, -1300, 350), add(m, wrist, one, -1300, 400), -1100, 350)
    # belt: |z - BeltZ| < 3
    dz = expr(m, unreal.MaterialExpressionSubtract, -1300, 200)
    link(z, "", dz, "A")
    link(belt_z, "", dz, "B")
    adz = expr(m, unreal.MaterialExpressionAbs, -1200, 200)
    link(dz, "", adz, "")
    belt_mask = band(m, adz, const(m, 2.5, -1200, 250), const(m, 3.5, -1200, 280), -1050, 200, invert=True)
    c = lerp(m, suit, accent, belt_mask, -800, 100)
    c = lerp(m, c, boots, boot_mask, -650, 100)
    c = lerp(m, c, boots, glove_mask, -500, 100)
    c = lerp(m, c, t_skin, skin_mask, -350, 0)
    mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(t_nrm, "RGB", unreal.MaterialProperty.MP_NORMAL)
    rough = lerp(m, const(m, 0.45, -400, 150), t_rgh, skin_mask, -200, 200)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.layout_material_expressions(m)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def build_hair():
    tex = eal.load_asset(f"{CH}/Hair_Long/T_Hair_2_BaseColor")
    nrm = eal.load_asset(f"{CH}/Hair_Long/T_Hair_2_Normal")
    m = new_material("M_HeroHair")
    t = tex_param(m, "HairTex", tex, -900, 0)
    n = tex_param(m, "NormalTex", nrm, -400, 300, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    col = vec_param(m, "HairColor", hexcol("#3B2416"), -900, -200)
    desat = expr(m, unreal.MaterialExpressionDesaturation, -650, 0)
    link(t, "RGB", desat, "")
    mul = expr(m, unreal.MaterialExpressionMultiply, -450, -100)
    link(col, "", mul, "A")
    link(desat, "", mul, "B")
    boost = expr(m, unreal.MaterialExpressionMultiply, -300, -100, const_b=2.0)
    link(mul, "", boost, "A")
    mel.connect_material_property(boost, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(const(m, 0.55, -300, 100), "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.layout_material_expressions(m)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def instance(parent, name, vectors=None, scalars=None, textures=None):
    path = f"{MAT}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    mi = at.create_asset(name, MAT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, parent)
    for k, v in (vectors or {}).items():
        mel.set_material_instance_vector_parameter_value(mi, k, hexcol(v))
    for k, v in (scalars or {}).items():
        mel.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (textures or {}).items():
        mel.set_material_instance_texture_parameter_value(mi, k, eal.load_asset(v))
    mel.update_material_instance(mi)
    eal.save_loaded_asset(mi)
    return mi


suit = build_suit()
hair = build_hair()
FEM = {"SkinTex": f"{CH}/Superhero_Female_FullBody/T_Superhero_Female_Dark_BaseColor",
       "NormalTex": f"{CH}/Superhero_Female_FullBody/T_Superhero_Female_Normal",
       "RoughTex": f"{CH}/Superhero_Female_FullBody/T_Superhero_Female_Roughness"}
LOOKS = {  # suit, boots/gloves, accent, hair, female?
    "Brakka": ("#2F5DBA", "#2B2F3A", "#E8B04A", "#2A1A10", False),
    "Vela": ("#3E7D3A", "#5C3A21", "#E9DFC4", "#B5452B", True),
    "Zephyr": ("#5B2A86", "#241A33", "#4FF2FF", "#D9D9E6", False),
    "Lumi": ("#F4F1EA", "#D9A441", "#FF7AB6", "#FF8FC4", True),
}
for hero, (s, b, a, h, fem) in LOOKS.items():
    mi_suit = instance(suit, f"MI_Suit_{hero}", {"SuitColor": s, "BootColor": b, "AccentColor": a},
                       {"NeckZ": 146.0 if fem else 150.0, "BeltZ": 97.0 if fem else 100.0},
                       FEM if fem else None)
    mi_hair = instance(hair, f"MI_Hair_{hero}", {"HairColor": h})
    bp = eal.load_asset(f"{BPS}/BP_Hero_{hero}")
    mesh_comp = unreal.get_default_object(bp.generated_class()).get_editor_property("mesh")
    mesh_comp.set_editor_property("override_materials", [mi_hair, None, mi_suit])  # slots: brows, eyes, body
    for h_ in sds.k2_gather_subobject_data_for_blueprint(bp):
        name = str(lib.get_variable_name(lib.get_data(h_)))
        if name.startswith("Hair_"):
            comp = lib.get_object(lib.get_data(h_))
            comp.set_editor_property("override_materials", [mi_hair])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    print("styled", hero)
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
