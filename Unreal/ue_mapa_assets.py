"""Mapa v2, passo 1 (só assets, não mexe no nível aberto): texturas do mapa, textura de pigmento,
material do Landscape com as 8 camadas e os LayerInfo. Rodar com: python -I Unreal/ue_py.py Unreal/ue_mapa_assets.py
Cores: as mesmas do mapa gerado (Unreal/mapa_gerar.py), em sRGB convertidas para linear. Visual cartoon/aquarela:
cor chapada por camada, variação de pigmento em duas escalas (40 m e 6 m), fosco (roughness 1, specular 0).
"""
import os

import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

FOLDER = "/Game/NexusRoyale/Map/V2"
GEN = r"D:\meus documentos\Fortnite\Unreal\Data\Mapa\gerado"
LAYERS = [("Grama", (132, 196, 76)), ("Campo", (190, 210, 92)), ("Floresta", (70, 140, 58)), ("Selva", (40, 112, 70)),
          ("Areia", (236, 214, 150)), ("Rocha", (150, 142, 132)), ("Pedra", (186, 180, 170)), ("Terra", (196, 160, 104))]


def lin(rgb):
    return [((c / 255.0) ** 2.2) for c in rgb]


def import_texture(file_name, dest, kind):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(GEN, file_name)
    task.destination_path = FOLDER
    task.destination_name = dest
    task.replace_existing = True
    task.automated = True
    task.save = False
    at.import_asset_tasks([task])
    tex = eal.load_asset(f"{FOLDER}/{dest}")
    if kind == "ui":
        tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
        tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    else:  # máscara em tons de cinza, linear, que ladrilha
        tex.set_editor_property("srgb", False)
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    eal.save_asset(f"{FOLDER}/{dest}")
    print("textura:", dest, tex.blueprint_get_size_x(), "x", tex.blueprint_get_size_y())
    return tex


def expr(mat, cls, x, y, **props):
    e = mel.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def link(a, a_out, b, b_in):
    if not mel.connect_material_expressions(a, a_out, b, b_in):
        print(f"  !! não ligou {a.get_name()}.{a_out or 'out'} -> {b.get_name()}.{b_in}")


def build_material(pigment):
    path = f"{FOLDER}/M_Terreno_V2"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    mat = at.create_asset("M_Terreno_V2", FOLDER, unreal.Material, unreal.MaterialFactoryNew())

    blend = expr(mat, unreal.MaterialExpressionLandscapeLayerBlend, -700, 0)
    inputs = []
    for i, (name, _) in enumerate(LAYERS):
        li = unreal.LayerBlendInput()
        li.set_editor_property("layer_name", name)
        li.set_editor_property("blend_type", unreal.LandscapeLayerBlendType.LB_WEIGHT_BLEND)
        li.set_editor_property("preview_weight", 1.0 if i == 0 else 0.0)
        inputs.append(li)
    blend.set_editor_property("layers", inputs)
    for i, (name, rgb) in enumerate(LAYERS):
        v = expr(mat, unreal.MaterialExpressionVectorParameter, -1100, i * 130 - 400,
                 parameter_name=f"Cor_{name}", default_value=unreal.LinearColor(*lin(rgb), 1.0))
        link(v, "", blend, f"Layer {name}")

    # variação de pigmento: lerp(0.82, 1.18, macro 40 m) * lerp(0.92, 1.08, micro 6 m)
    wp = expr(mat, unreal.MaterialExpressionWorldPosition, -1700, 800)
    xy = expr(mat, unreal.MaterialExpressionComponentMask, -1500, 800, r=True, g=True, b=False, a=False)
    link(wp, "", xy, "")
    factors = []
    for k, (scale, lo, hi) in enumerate(((4000.0, 0.82, 1.18), (600.0, 0.92, 1.08))):
        div = expr(mat, unreal.MaterialExpressionDivide, -1300, 760 + k * 200, const_b=scale)
        link(xy, "", div, "A")
        ts = expr(mat, unreal.MaterialExpressionTextureSample, -1100, 760 + k * 200,
                  texture=pigment, sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
        link(div, "", ts, "UVs")
        lerp = expr(mat, unreal.MaterialExpressionLinearInterpolate, -800, 760 + k * 200, const_a=lo, const_b=hi)
        link(ts, "R", lerp, "Alpha")
        factors.append(lerp)
    var = expr(mat, unreal.MaterialExpressionMultiply, -550, 800)
    link(factors[0], "", var, "A")
    link(factors[1], "", var, "B")
    color = expr(mat, unreal.MaterialExpressionMultiply, -350, 200)
    link(blend, "", color, "A")
    link(var, "", color, "B")
    mel.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = expr(mat, unreal.MaterialExpressionConstant, -350, 400, r=1.0)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    spec = expr(mat, unreal.MaterialExpressionConstant, -350, 500, r=0.0)
    mel.connect_material_property(spec, "", unreal.MaterialProperty.MP_SPECULAR)

    mel.recompile_material(mat)
    eal.save_asset(path)
    print("material:", path, "| expressões:", mel.get_num_material_expressions(mat))
    return mat


# Os LayerInfo NÃO são criados aqui: na 5.8 o LayerName do LandscapeLayerInfoObject é somente leitura pelo Python.
# Eles são criados no painel do Landscape, no botão "+" de cada camada (passo a passo em Design/Mapa.md).
eal.make_directory(FOLDER)
import_texture("T_Mapa_Base.png", "T_Mapa_Base", "ui")
import_texture("T_Mapa_Aquarela.png", "T_Mapa_Aquarela", "ui")
pig = import_texture("T_Pigmento.png", "T_Pigmento", "mask")
build_material(pig)
