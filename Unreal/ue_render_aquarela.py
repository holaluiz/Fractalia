"""Direção de arte cartoon + aquarela (GDD §10, Design/Mapa.md): pós-processamento leve para a RX 570.
Rodar com: python -I Unreal/ue_py.py -c "ETAPA='materiais'; exec(open(r'D:/meus documentos/Fortnite/Unreal/ue_render_aquarela.py', encoding='utf-8').read())"

ETAPA:
  materiais  cria/recria em /Game/NexusRoyale/Render/ os dois materiais de pós e as instâncias que os volumes usam:
             M_PP_Cel / MI_PP_Cel                         (Scene Color After DOF, linear, resolução de render)
                 iluminação em faixas: luz que chegou = cor da cena / BaseColor do GBuffer, quantizada em 4 faixas
                 relativas à exposição atual (EyeAdaptation), então funciona com qualquer intensidade de sol.
             M_PP_CartoonAquarela / MI_PP_CartoonAquarela (Scene Color After Tonemapping, sRGB, resolução de saída)
                 cenário (stencil 0): Kuwahara 5x5 em 4 quadrantes (manchas chapadas), sangria pelo T_Pigmento,
                 borda escurecida onde a cor muda, pigmento, grão de papel, tinta clara e contorno suave por
                 profundidade/normal que some com a distância. Mesma receita do watercolor() de mapa_gerar.py.
                 personagens (stencil > 0 e visível): sem aquarela, contorno nítido na silhueta e nas quinas.
  stencil    liga Render CustomDepth + stencil nos componentes de malha: 1 herói (BP_HeroBase), 2 creeps (BP_Creep e
             filhos), 3 pickups (BP_Pickup). 4 = magias (ANRProjetilMagico, no C++). SO=["Hero"] limita os BPs.
  volume     no nível ABERTO: PostProcessVolume infinito "PP_CartoonAquarela" com as duas instâncias, sem motion blur
             nem lens flare, e SkyLight com captura estática (real_time_capture desligado). Salva só o nível.
  nanite     conta as StaticMesh com Nanite em /Game (pela tag "NaniteEnabled" do Asset Registry, sem carregar nada).
             Com DESLIGAR=True desliga o Nanite delas em lotes de LOTE (padrão 40), salvando e limpando a memória
             entre um lote e outro. Malha low-poly não ganha nada com Nanite e o fallback dobra a memória.
  dados      só imprime o estado (materiais, volume e stencil) sem mudar nada.
Precisa de r.CustomDepth=3 (stencil). Fica no DefaultEngine.ini; para testar antes, rode o console "r.CustomDepth 3".
"""
import unreal

ETAPA = globals().get("ETAPA", "dados")
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

FOLDER = "/Game/NexusRoyale/Render"
PIGMENTO = "/Game/NexusRoyale/Map/V2/T_Pigmento"
STENCIL = {  # BP: valor do stencil
    "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase": 1,
    "/Game/NexusRoyale/Blueprints/Creeps/BP_Creep": 2,
    "/Game/NexusRoyale/Blueprints/Creeps/BP_Creep_Imp": 2,
    "/Game/NexusRoyale/Blueprints/Creeps/BP_Creep_Puglin": 2,
    "/Game/NexusRoyale/Blueprints/Loot/BP_Pickup": 3,
}
ST = unreal.SceneTextureId

# ---------------------------------------------------------------- passo 1: faixas de luz (antes do tonemapper)
CEL_HLSL = r"""
float3 c = Cena.rgb;
float3 b = Base.rgb;
float bm = max(b.r, max(b.g, b.b));
if (Prof.r > DistanciaCeu || bm < 0.03) return c;
float3 L = c / max(b, 0.03);
float l = dot(L, float3(0.2126, 0.7152, 0.0722));
float e = l * Exposicao;
float f = Sombra;
f += (Meia - Sombra) * smoothstep(Limite1 - Suave, Limite1 + Suave, e);
f += (Luz - Meia) * smoothstep(Limite2 - Suave, Limite2 + Suave, e);
f += (Brilho - Luz) * smoothstep(Limite3 - Suave, Limite3 + Suave, e);
float3 tom = lerp(float3(1.0, 1.0, 1.0), L / max(l, 1e-4), CorDaLuz);
float3 cel = b * tom * (f / max(Exposicao, 1e-6));
return lerp(c, cel, Forca);
"""
CEL_PARAMS = {  # e = luz relativa à exposição (1 = superfície branca bem iluminada)
    "Forca": 1.0, "Sombra": 0.32, "Meia": 0.62, "Luz": 1.0, "Brilho": 1.25,
    "Limite1": 0.30, "Limite2": 0.75, "Limite3": 2.2, "Suave": 0.03, "CorDaLuz": 0.6, "DistanciaCeu": 2.0e6,
}

# ---------------------------------------------------------------- passo 2: aquarela + contorno (depois do tonemapper)
# Índices de SceneTexture (MaterialSceneTextureId.h): 1 SceneDepth, 8 WorldNormal, 13 CustomDepth,
# 14 PostProcessInput0, 25 CustomStencil. SceneTextureFetch(i, deslocamento em texels) é do MaterialTemplate.ush.
AQ_HLSL = r"""
float3 base = SceneTextureFetch(14, float2(0, 0)).rgb;
float d0 = SceneTextureFetch(1, float2(0, 0)).r;
float cd0 = SceneTextureFetch(13, float2(0, 0)).r;
float s0 = SceneTextureFetch(25, float2(0, 0)).r;
float vis0 = (s0 > 0.5 && cd0 <= d0 * 1.002 + 2.0) ? 1.0 : 0.0;
float3 n0 = SceneTextureFetch(8, float2(0, 0)).xyz;

float2 dirs[4] = { float2(1, 0), float2(-1, 0), float2(0, 1), float2(0, -1) };
float bProf = 0.0, bNorm = 0.0, silh = 0.0;
[unroll] for (int k = 0; k < 4; k++) {
    float2 off = dirs[k] * Largura;
    float d = SceneTextureFetch(1, off).r;
    float cd = SceneTextureFetch(13, off).r;
    float s = SceneTextureFetch(25, off).r;
    float vis = (s > 0.5 && cd <= d * 1.002 + 2.0) ? 1.0 : 0.0;
    silh = max(silh, abs(vis - vis0));
    bProf = max(bProf, abs(d - d0) / max(min(d, d0), 1.0));
    bNorm = max(bNorm, 1.0 - dot(SceneTextureFetch(8, off).xyz, n0));
}
float linha = max(smoothstep(LimiteProf, LimiteProf * 2.0, bProf), smoothstep(LimiteNormal, LimiteNormal + 0.25, bNorm));

float3 col;
if (vis0 < 0.5) {
    float2 sang = float2(Texture2DSample(Pigmento, PigmentoSampler, Pixel / EscalaSangria).r,
                         Texture2DSample(Pigmento, PigmentoSampler, Pixel / EscalaSangria + 0.37).r) - 0.5;
    sang *= Sangria;
    float3 m[4] = { (float3)0, (float3)0, (float3)0, (float3)0 };
    float3 q[4] = { (float3)0, (float3)0, (float3)0, (float3)0 };
    float3 tot = 0;
    [unroll] for (int j = -2; j <= 2; j++) {
        [unroll] for (int i = -2; i <= 2; i++) {
            float3 c = SceneTextureFetch(14, float2(i, j) * Passo + sang).rgb;
            float3 c2 = c * c;
            tot += c;
            if (i <= 0 && j <= 0) { m[0] += c; q[0] += c2; }
            if (i >= 0 && j <= 0) { m[1] += c; q[1] += c2; }
            if (i <= 0 && j >= 0) { m[2] += c; q[2] += c2; }
            if (i >= 0 && j >= 0) { m[3] += c; q[3] += c2; }
        }
    }
    float melhor = 1e9;
    float3 a = base;
    [unroll] for (int r = 0; r < 4; r++) {
        float3 mu = m[r] / 9.0;
        float3 v = q[r] / 9.0 - mu * mu;
        float vs = v.r + v.g + v.b;
        if (vs < melhor) { melhor = vs; a = mu; }
    }
    float borda = saturate(dot(abs(a - tot / 25.0), float3(1, 1, 1)) * BordaGanho);
    a *= 1.0 - BordaForca * borda;
    float pig = Texture2DSample(Pigmento, PigmentoSampler, Pixel / EscalaPigmento).r;
    float grao = Texture2DSample(Pigmento, PigmentoSampler, Pixel / EscalaPapel).r;
    a *= (1.0 - 0.5 * PigmentoForca + PigmentoForca * pig) * (1.0 - PapelForca + PapelForca * grao);
    float g = dot(a, float3(1, 1, 1) / 3.0);
    a = g + (a - g) * Saturacao;
    a = 1.0 - (1.0 - a) * Clareza;
    a *= CorPapel;
    a *= 1.0 - LinhaCenario * linha * (1.0 - smoothstep(FadeInicio, FadeFim, d0));
    col = lerp(base, a, Forca);
} else {
    col = base * (1.0 - LinhaPersonagem * linha);
}
return lerp(col, CorContorno, silh * ContornoForca);
"""
AQ_PARAMS = {
    "Forca": 1.0, "Passo": 1.5, "Sangria": 3.0, "EscalaSangria": 900.0, "BordaGanho": 3.2, "BordaForca": 0.45,
    "PigmentoForca": 0.2, "EscalaPigmento": 1400.0, "PapelForca": 0.07, "EscalaPapel": 140.0,
    "Saturacao": 0.88, "Clareza": 0.85, "Largura": 1.0, "LimiteProf": 0.04, "LimiteNormal": 0.35,
    "LinhaCenario": 0.35, "FadeInicio": 3000.0, "FadeFim": 12000.0, "LinhaPersonagem": 0.6, "ContornoForca": 1.0,
}
AQ_VECTORS = {"CorPapel": (0.99, 0.96, 0.90), "CorContorno": (0.07, 0.05, 0.04)}


def expr(mat, cls, x, y, **props):
    e = mel.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def link(a, a_out, b, b_in):
    if not mel.connect_material_expressions(a, a_out, b, b_in):
        raise RuntimeError(f"não ligou {a.get_name()}.{a_out or 'out'} -> {b.get_name()}.{b_in}")


def custom_node(mat, code, inputs, desc):
    c = expr(mat, unreal.MaterialExpressionCustom, -300, 0, code=code, description=desc,
             output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    cis = []
    for n in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        cis.append(ci)
    c.set_editor_property("inputs", cis)
    return c


def scene_tex(mat, tid, y):
    return expr(mat, unreal.MaterialExpressionSceneTexture, -900, y, scene_texture_id=tid)


def new_pp_material(name, location):
    path = f"{FOLDER}/{name}"
    mi_path = f"{FOLDER}/MI_{name[2:]}"
    if eal.does_asset_exist(path):
        if eal.does_asset_exist(mi_path):  # solta a instância para poder apagar o pai (ver ue_mapa_ui_material.py)
            mel.set_material_instance_parent(eal.load_asset(mi_path), None)
        if not eal.delete_asset(path):
            raise RuntimeError(f"não consegui apagar {path}")
    mat = at.create_asset(name, FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    mat.set_editor_property("blendable_location", location)
    return mat, path, mi_path


def add_params(mat, custom, scalars, vectors, y0):
    y = y0
    for n, v in scalars.items():
        link(expr(mat, unreal.MaterialExpressionScalarParameter, -900, y, parameter_name=n, default_value=v), "", custom, n)
        y += 90
    for n, v in vectors.items():
        p = expr(mat, unreal.MaterialExpressionVectorParameter, -900, y, parameter_name=n,
                 default_value=unreal.LinearColor(*v, 1.0))
        link(p, "", custom, n)
        y += 160


def finish(mat, custom, path, mi_path):
    mel.connect_material_property(custom, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    eal.save_asset(path)
    mi = eal.load_asset(mi_path) if eal.does_asset_exist(mi_path) else \
        at.create_asset(mi_path.rsplit("/", 1)[1], FOLDER, unreal.MaterialInstanceConstant,
                        unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, mat)
    mel.update_material_instance(mi)
    eal.save_asset(mi_path)
    print("material:", path, "| expressões:", mel.get_num_material_expressions(mat), "| instância:", mi_path)


def build_cel():
    mat, path, mi_path = new_pp_material("M_PP_Cel", unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_DOF)
    custom = custom_node(mat, CEL_HLSL, ["Cena", "Base", "Prof", "Exposicao"] + list(CEL_PARAMS), "Faixas de luz")
    link(scene_tex(mat, ST.PPI_POST_PROCESS_INPUT0, -400), "Color", custom, "Cena")
    link(scene_tex(mat, ST.PPI_BASE_COLOR, -280), "Color", custom, "Base")
    link(scene_tex(mat, ST.PPI_SCENE_DEPTH, -160), "Color", custom, "Prof")
    link(expr(mat, unreal.MaterialExpressionEyeAdaptation, -900, -40), "", custom, "Exposicao")
    add_params(mat, custom, CEL_PARAMS, {}, 60)
    finish(mat, custom, path, mi_path)


def build_aquarela():
    pig = eal.load_asset(PIGMENTO)
    if pig is None:
        raise RuntimeError(f"{PIGMENTO} não existe (rode Unreal/ue_mapa_assets.py)")
    mat, path, mi_path = new_pp_material("M_PP_CartoonAquarela", unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
    # as entradas _X só existem para o compilador ligar essas scene textures (o HLSL lê com SceneTextureFetch)
    marks = {"_Cena": ST.PPI_POST_PROCESS_INPUT0, "_Prof": ST.PPI_SCENE_DEPTH, "_ProfCustom": ST.PPI_CUSTOM_DEPTH,
             "_Estencil": ST.PPI_CUSTOM_STENCIL, "_Normal": ST.PPI_WORLD_NORMAL}
    custom = custom_node(mat, AQ_HLSL, list(marks) + ["Pixel", "Pigmento"] + list(AQ_PARAMS) + list(AQ_VECTORS),
                         "Aquarela e contorno")
    y = -700
    for n, tid in marks.items():
        link(scene_tex(mat, tid, y), "Color", custom, n)
        y += 120
    link(expr(mat, unreal.MaterialExpressionScreenPosition, -900, y), "PixelPosition", custom, "Pixel")
    link(expr(mat, unreal.MaterialExpressionTextureObjectParameter, -900, y + 100, parameter_name="TexturaPigmento",
              texture=pig), "", custom, "Pigmento")
    add_params(mat, custom, AQ_PARAMS, AQ_VECTORS, y + 260)
    finish(mat, custom, path, mi_path)


# ---------------------------------------------------------------- stencil nos personagens, creeps e pickups
def mesh_components(bp):
    """Componentes de malha do BP: os herdados do C++ (pelo CDO) e os do Construction Script (pelo subobject)."""
    out = {}
    cdo = unreal.get_default_object(bp.generated_class())
    for c in cdo.get_components_by_class(unreal.MeshComponent):
        out[c.get_name()] = c
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o = lib.get_object(lib.get_data(h))
        if isinstance(o, unreal.MeshComponent):
            out[str(lib.get_variable_name(lib.get_data(h)))] = o
    return out


def set_stencil():
    so = globals().get("SO")  # opcional: só os BPs cujo nome contém um destes textos, ex. SO=["Hero", "Creep"]
    for path, value in STENCIL.items():
        if so and not any(s in path.rsplit("/", 1)[1] for s in so):
            continue
        bp = eal.load_asset(path)
        if bp is None:
            print("!! não existe:", path)
            continue
        comps = mesh_components(bp)
        for c in comps.values():
            c.set_editor_property("render_custom_depth", True)
            c.set_editor_property("custom_depth_stencil_value", value)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        eal.save_asset(path)
        print(f"stencil {value}: {path.rsplit('/', 1)[1]} -> {sorted(comps)}")


# ---------------------------------------------------------------- volume e céu no nível aberto
def setup_level():
    if les.is_in_play_in_editor():
        raise RuntimeError("PIE rodando: rode de novo quando o PIE acabar")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
    vol = next((a for a in actors if isinstance(a, unreal.PostProcessVolume) and a.get_actor_label() == "PP_CartoonAquarela"), None)
    if vol is None:
        vol = eas.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 0))
        vol.set_actor_label("PP_CartoonAquarela")
        vol.set_folder_path("Luz e Céu")
    vol.set_editor_property("unbound", True)
    vol.set_editor_property("priority", 10.0)
    s = vol.get_editor_property("settings")
    blends = []
    for mi in ("MI_PP_Cel", "MI_PP_CartoonAquarela"):
        wb = unreal.WeightedBlendable()
        wb.set_editor_property("weight", 1.0)
        wb.set_editor_property("object", eal.load_asset(f"{FOLDER}/{mi}"))
        blends.append(wb)
    wbs = unreal.WeightedBlendables()
    wbs.set_editor_property("array", blends)
    s.set_editor_property("weighted_blendables", wbs)
    for flag, prop, val in (("override_motion_blur_amount", "motion_blur_amount", 0.0),
                            ("override_lens_flare_intensity", "lens_flare_intensity", 0.0),
                            ("override_vignette_intensity", "vignette_intensity", 0.0)):
        s.set_editor_property(flag, True)
        s.set_editor_property(prop, val)
    vol.set_editor_property("settings", s)
    for sky in [a for a in actors if isinstance(a, unreal.SkyLight)]:
        comp = sky.get_component_by_class(unreal.SkyLightComponent)
        was = comp.get_editor_property("real_time_capture")
        comp.set_editor_property("real_time_capture", False)
        comp.recapture_sky()
        print("SkyLight", sky.get_actor_label(), "real_time_capture", was, "-> False")
    les.save_current_level()
    print("volume pronto no nível", unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name())


def nanite():
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine", "StaticMesh")],
                          package_paths=["/Game"], recursive_paths=True)
    meshes = reg.get_assets(flt)
    on = [a for a in meshes if str(a.get_tag_value("NaniteEnabled")) == "True"]
    by_root = {}
    for a in on:
        root = "/".join(str(a.package_path).split("/")[:3])
        by_root[root] = by_root.get(root, 0) + 1
    print(f"StaticMesh em /Game: {len(meshes)} | com Nanite: {len(on)} | por pasta: {by_root}")
    if not globals().get("DESLIGAR"):
        return
    if les.is_in_play_in_editor():
        raise RuntimeError("PIE rodando: rode de novo quando o PIE acabar")
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    lote = int(globals().get("LOTE", 40))
    feitos = 0
    for i in range(0, len(on), lote):
        for a in on[i:i + lote]:
            path = str(a.package_name)
            mesh = eal.load_asset(path)
            ns = mesh.get_editor_property("nanite_settings")
            ns.set_editor_property("enabled", False)
            sms.set_nanite_settings(mesh, ns, True)
            eal.save_asset(path, only_if_is_dirty=False)
            feitos += 1
        unreal.SystemLibrary.collect_garbage()
        print(f"  Nanite desligado: {feitos}/{len(on)}")


def report():
    for n in ("M_PP_Cel", "MI_PP_Cel", "M_PP_CartoonAquarela", "MI_PP_CartoonAquarela"):
        print(n, eal.does_asset_exist(f"{FOLDER}/{n}"))
    for path in STENCIL:
        bp = eal.load_asset(path)
        if bp:
            print(path.rsplit("/", 1)[1], {k: (c.get_editor_property("render_custom_depth"),
                                              c.get_editor_property("custom_depth_stencil_value"))
                                          for k, c in mesh_components(bp).items()})
    if not les.is_in_play_in_editor():
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        for a in eas.get_all_level_actors():
            if isinstance(a, (unreal.PostProcessVolume, unreal.SkyLight)):
                print("ator:", a.get_actor_label(), a.get_class().get_name())


if ETAPA == "materiais":
    eal.make_directory(FOLDER)
    build_cel()
    build_aquarela()
elif ETAPA == "stencil":
    set_stencil()
elif ETAPA == "volume":
    setup_level()
elif ETAPA == "nanite":
    nanite()
else:
    report()
