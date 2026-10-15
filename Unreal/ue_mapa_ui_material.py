"""Mapa v2, interface: material M_UI_Mapa, usado pelo minimapa, pelo mapa em tela cheia (M) e pelo mapa da queda.
Rodar com: python -I Unreal/ue_py.py Unreal/ue_mapa_ui_material.py

Um nó Custom (HLSL) desenha tudo a partir da textura T_Mapa_UI (gerada por Unreal/mapa_gerar.py, norte para cima):
ilha, tempestade (fora do círculo atual fica roxo; borda roxa; próximo círculo em branco), rota do dirigível
(tracejado), marcador e a seta do jogador.
Os valores globais vêm da Material Parameter Collection MPC_Mapa (o WBP_Mapa atualiza todo tick): Jogador, Tempestade,
Proxima, Rota, Marcador, RotaLigada. O que muda entre os mapas fica em duas instâncias: MI_UI_Minimapa (Vista com
modo 0 e 150 m, 260 px) e MI_UI_MapaCompleto (modo 1, ilha inteira, 900 px). Parâmetros:
  Jogador     (X cm, Y cm, yaw graus, -)       X = norte, Y = leste (coordenadas da Unreal)
  Vista       (centro X, centro Y, meia largura em cm, modo)   modo 0 = minimapa redondo centrado no jogador,
                                                               modo 1 = mapa quadrado (tela cheia e queda)
  Tempestade  (X, Y, raio cm) + TempestadeLigada     Proxima (X, Y, raio) + ProximaLigada
  RotaInicio, RotaFim (X, Y) + RotaLigada           Marcador (X, Y, ligado)
  Extensao    metade do lado coberto pela textura (63000 cm)
  Girar       1 = minimapa gira com a câmera; 0 = norte sempre para cima (padrão, como no Fortnite)
  PixelsWidget  tamanho do widget em pixels (só para a espessura das linhas)
"""
import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

FOLDER = "/Game/NexusRoyale/UI/Mapa"
MAP_TEX = f"{FOLDER}/T_Mapa_UI"
GEN = r"D:\meus documentos\Fortnite\Unreal\Data\Mapa\gerado"

HLSL = r"""
float modo = Vista.w;
float2 d = UV - 0.5;
float2 s = d * 2.0 * Vista.z;
float px = 2.0 * Vista.z / max(PixelsWidget, 64.0);
float a = radians(Jogador.z) * Girar * (1.0 - modo);
float2 f = float2(cos(a), sin(a));
float2 rt = float2(-sin(a), cos(a));
float2 centro = lerp(Jogador.xy, Vista.xy, modo);
float2 w = centro + (-s.y) * f + s.x * rt;
float2 muv = float2((w.y + Extensao) / (2.0 * Extensao), (Extensao - w.x) / (2.0 * Extensao));
float3 col = Texture2DSample(Mapa, MapaSampler, saturate(muv)).rgb;

if (TempestadeLigada > 0.5) {
    float ds = distance(w, Tempestade.xy);
    col = lerp(col, col * 0.45 + float3(0.32, 0.08, 0.42), 0.65 * step(Tempestade.z, ds));
    col = lerp(col, float3(0.85, 0.35, 1.0), saturate(1.75 - abs(ds - Tempestade.z) / px));
}
if (ProximaLigada > 0.5) {
    float dn = distance(w, Proxima.xy);
    col = lerp(col, float3(1.0, 1.0, 1.0), saturate(1.5 - abs(dn - Proxima.z) / px));
}
if (RotaLigada > 0.5) {
    float2 ab = RotaFim.xy - RotaInicio.xy;
    float t = saturate(dot(w - RotaInicio.xy, ab) / max(dot(ab, ab), 1.0));
    float dl = distance(w, RotaInicio.xy + t * ab);
    float dash = step(0.45, frac(t * length(ab) / (px * 22.0)));
    col = lerp(col, float3(1.0, 0.82, 0.25), saturate(2.5 - dl / px) * dash);
}
if (Marcador.z > 0.5) {
    float dm = distance(w, Marcador.xy);
    col = lerp(col, float3(1.0, 0.75, 0.1), saturate(2.0 - abs(dm - 7.0 * px) / px));
    col = lerp(col, float3(1.0, 0.75, 0.1), saturate(2.0 - dm / px));
}

float ay = radians(Jogador.z);
float2 rel = w - Jogador.xy;
float2 fl = float2(cos(ay), sin(ay));
float2 rl = float2(-sin(ay), cos(ay));
float2 q = float2(dot(rel, rl), dot(rel, fl)) / (px * 9.0);
float tri = step(q.y, 1.0) * step(-0.7, q.y) * step(abs(q.x), (1.0 - q.y) * 0.55);
float borda = step(q.y, 1.3) * step(-0.95, q.y) * step(abs(q.x), (1.3 - q.y) * 0.62);
col = lerp(col, float3(0.10, 0.07, 0.05), borda);
col = lerp(col, float3(1.0, 1.0, 1.0), tri);

float r = length(d) * 2.0;
float alpha = lerp(1.0 - smoothstep(0.985, 1.0, r), 1.0, modo);
col = lerp(col, float3(0.24, 0.17, 0.11), smoothstep(0.93, 0.96, r) * (1.0 - modo));
return float4(col, alpha);
"""

MPC_PATH = f"{FOLDER}/MPC_Mapa"
MPC_VECTORS = {  # globais, atualizados pelo WBP_Mapa (nome: padrão). Na 5.8 o vetor de MPC chega ao HLSL como RGB:
    "Jogador": (0.0, 0.0, 0.0, 0.0),        # X, Y, yaw
    "Tempestade": (0.0, 0.0, 56000.0, 0.0),  # X, Y, raio
    "Proxima": (0.0, 0.0, 31000.0, 0.0),     # X, Y, raio
    "RotaInicio": (-50000.0, -40000.0, 0.0, 0.0),
    "RotaFim": (50000.0, 40000.0, 0.0, 0.0),
    "Marcador": (0.0, 0.0, 0.0, 0.0),        # X, Y, ligado
}
MPC_SCALARS = {"RotaLigada": 0.0, "TempestadeLigada": 0.0, "ProximaLigada": 0.0}
VEC_PARAMS = {"Vista": (0.0, 0.0, 15000.0, 0.0)}  # por instância
SCALAR_PARAMS = {"Extensao": 63000.0, "Girar": 0.0, "PixelsWidget": 280.0}
INSTANCES = {  # nome: (Vista, PixelsWidget)
    "MI_UI_Minimapa": ((0.0, 0.0, 15000.0, 0.0), 260.0),
    "MI_UI_MapaCompleto": ((0.0, 0.0, 56000.0, 1.0), 900.0),
}


def import_ui_texture():
    task = unreal.AssetImportTask()
    task.filename = GEN + r"\T_Mapa_UI.png"
    task.destination_path = FOLDER
    task.destination_name = "T_Mapa_UI"
    task.replace_existing = True
    task.automated = True
    if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
        raise RuntimeError("PIE rodando: o editor recusa operações de asset. Rode de novo quando o PIE acabar.")
    at.import_asset_tasks([task])
    tex = eal.load_asset(MAP_TEX)
    if tex is None:
        raise RuntimeError("T_Mapa_UI não carregou depois da importação")
    tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("address_x", unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property("address_y", unreal.TextureAddress.TA_CLAMP)
    eal.save_asset(MAP_TEX)
    return tex


def build_mpc():
    if not eal.does_asset_exist(MPC_PATH):
        at.create_asset("MPC_Mapa", FOLDER, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    mpc = eal.load_asset(MPC_PATH)
    vecs = []
    for n, v in MPC_VECTORS.items():
        p = unreal.CollectionVectorParameter()
        p.set_editor_property("parameter_name", n)
        p.set_editor_property("default_value", unreal.LinearColor(*v))
        vecs.append(p)
    scs = []
    for n, v in MPC_SCALARS.items():
        p = unreal.CollectionScalarParameter()
        p.set_editor_property("parameter_name", n)
        p.set_editor_property("default_value", v)
        scs.append(p)
    mpc.set_editor_property("vector_parameters", vecs)
    mpc.set_editor_property("scalar_parameters", scs)
    eal.save_asset(MPC_PATH)
    print("MPC:", MPC_PATH, [p.get_editor_property("parameter_name") for p in mpc.get_editor_property("vector_parameters")])
    return mpc


def build_instances(mat):
    for name, (vista, pixels) in INSTANCES.items():
        path = f"{FOLDER}/{name}"
        mi = eal.load_asset(path) if eal.does_asset_exist(path) else             at.create_asset(name, FOLDER, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, mat)
        mel.set_material_instance_vector_parameter_value(mi, "Vista", unreal.LinearColor(*vista))
        mel.set_material_instance_scalar_parameter_value(mi, "PixelsWidget", pixels)
        mel.update_material_instance(mi)
        eal.save_asset(path)
        print("instância:", path, vista, pixels)


def build_material(tex, mpc):
    path = f"{FOLDER}/M_UI_Mapa"
    if eal.does_asset_exist(path):
        # delete_all_material_expressions deixou nós soltos (um AppendVector antigo quebrava a compilação):
        # solta as instâncias, apaga o material e cria de novo; build_instances liga as instâncias outra vez
        for name in INSTANCES:
            mi_path = f"{FOLDER}/{name}"
            if eal.does_asset_exist(mi_path):
                mel.set_material_instance_parent(eal.load_asset(mi_path), None)
                eal.save_asset(mi_path)
        if not eal.delete_asset(path):
            raise RuntimeError("não consegui apagar o M_UI_Mapa antigo")
    mat = at.create_asset("M_UI_Mapa", FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)

    custom = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -400, 0)
    custom.set_editor_property("code", HLSL)
    custom.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    custom.set_editor_property("description", "Mapa")
    names = ["UV", "Mapa"] + list(MPC_VECTORS) + list(MPC_SCALARS) + list(VEC_PARAMS) + list(SCALAR_PARAMS)
    inputs = []
    for n in names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        inputs.append(ci)
    custom.set_editor_property("inputs", inputs)

    def link(src, pin):
        if not mel.connect_material_expressions(src, "", custom, pin):
            print("  !! não ligou", pin)

    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -900, -300)
    link(uv, "UV")
    tobj = mel.create_material_expression(mat, unreal.MaterialExpressionTextureObjectParameter, -900, -200)
    tobj.set_editor_property("parameter_name", "TexturaMapa")
    tobj.set_editor_property("texture", tex)
    link(tobj, "Mapa")
    y = -50
    for n in list(MPC_VECTORS) + list(MPC_SCALARS):
        e = mel.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter, -1100, y)
        e.set_editor_property("collection", mpc)
        e.set_editor_property("parameter_name", n)
        link(e, n)  # o HLSL só usa .xyz dos vetores da MPC (chegam como RGB)
        y += 120
    for n, v in VEC_PARAMS.items():
        e = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -1100, y)
        e.set_editor_property("parameter_name", n)
        e.set_editor_property("default_value", unreal.LinearColor(*v))
        # a saída padrão do VectorParameter é RGB (float3); o HLSL usa os 4 componentes
        if not mel.connect_material_expressions(e, "RGBA", custom, n):
            app = mel.create_material_expression(mat, unreal.MaterialExpressionAppendVector, -800, y)
            mel.connect_material_expressions(e, "", app, "A")
            mel.connect_material_expressions(e, "A", app, "B")
            link(app, n)
        y += 150
    for n, v in SCALAR_PARAMS.items():
        e = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -900, y)
        e.set_editor_property("parameter_name", n)
        e.set_editor_property("default_value", v)
        link(e, n)
        y += 100

    rgb = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -150, -40)
    for k, on in (("r", True), ("g", True), ("b", True), ("a", False)):
        rgb.set_editor_property(k, on)
    mel.connect_material_expressions(custom, "", rgb, "")
    alpha = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -150, 80)
    for k, on in (("r", False), ("g", False), ("b", False), ("a", True)):
        alpha.set_editor_property(k, on)
    mel.connect_material_expressions(custom, "", alpha, "")
    mel.connect_material_property(rgb, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(alpha, "", unreal.MaterialProperty.MP_OPACITY)

    mel.recompile_material(mat)
    eal.save_asset(path)
    print("material:", path, "| expressões:", mel.get_num_material_expressions(mat))
    return mat


eal.make_directory(FOLDER)
build_instances(build_material(import_ui_texture(), build_mpc()))
