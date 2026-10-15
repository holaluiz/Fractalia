"""MVP, passo 3 (dentro do editor, DEPOIS do ue_gas_setup.py):  python Unreal/ue_py.py Unreal/ue_mvp_setup.py

- cria o material dos projéteis /Game/NexusRoyale/VFX/M_Projetil (unlit, parâmetro de vetor "Cor");
- cria o material das estruturas mágicas /Game/NexusRoyale/VFX/M_Estrutura (iluminado, parâmetro "Cor");
- cria as Input Actions IA_AtaqueBasico, IA_MagiaPrincipal, IA_Magia2, IA_Ultimate e IA_Consumivel1..3 e mapeia
  no IMC_Default: botão esquerdo, Q, E, X e 1/2/3 (GDD §14). Também mapeia o IA_Interact no F, que tinha ficado de fora;
- põe no BP_HeroBase o componente "Combate" (UNRCombateComponent): ataque básico, Bola de Fogo, Muralha de Gelo (E),
  Chuva de Meteoros (X), consumíveis, HUD e morte (animação Death01 da UAL1).
- MVP: a ultimate fica liberada desde o nível 1 (NIVEL_ULTIMATE). O GDD §4.4 pede o nível 6, que é o padrão do C++;
  com um acampamento de Imps só, o nível 6 (1.040 XP) não chega numa partida de teste.
Idempotente.
"""
import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

HERO = "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase"
MAT = "/Game/NexusRoyale/VFX/M_Projetil"
MAT_ESTRUTURA = "/Game/NexusRoyale/VFX/M_Estrutura"
NIVEL_ULTIMATE = 1
ACTIONS = "/Game/Input/Actions"
IMC = "/Game/Input/IMC_Default"
DEATH = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_StandardDeath01"
TECLAS = [  # (Input Action, tecla)
    ("IA_Interact", "F"),
    ("IA_AtaqueBasico", "LeftMouseButton"),
    ("IA_MagiaPrincipal", "Q"),
    ("IA_Magia2", "E"),
    ("IA_Ultimate", "X"),
    ("IA_Consumivel1", "One"),
    ("IA_Consumivel2", "Two"),
    ("IA_Consumivel3", "Three"),
]

# --- material dos projéteis: brilha na cor da magia
if eal.does_asset_exist(MAT):
    mat = eal.load_asset(MAT)
else:
    mat = at.create_asset("M_Projetil", "/Game/NexusRoyale/VFX", unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    cor = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -500, 0)
    cor.set_editor_property("parameter_name", "Cor")
    cor.set_editor_property("default_value", unreal.LinearColor(1.0, 0.4, 0.1, 1.0))
    mult = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, 0)
    mult.set_editor_property("const_b", 6.0)
    mel.connect_material_expressions(cor, "", mult, "A")
    mel.connect_material_property(mult, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
eal.save_loaded_asset(mat)
print("material:", mat.get_path_name())

# --- material das estruturas (Muralha de Gelo): iluminado, na cor da escola e com um pouco de brilho próprio
if eal.does_asset_exist(MAT_ESTRUTURA):
    mat_estrutura = eal.load_asset(MAT_ESTRUTURA)
else:
    mat_estrutura = at.create_asset("M_Estrutura", "/Game/NexusRoyale/VFX", unreal.Material, unreal.MaterialFactoryNew())
    cor = mel.create_material_expression(mat_estrutura, unreal.MaterialExpressionVectorParameter, -600, 0)
    cor.set_editor_property("parameter_name", "Cor")
    cor.set_editor_property("default_value", unreal.LinearColor(0.35, 0.85, 1.0, 1.0))
    mel.connect_material_property(cor, "", unreal.MaterialProperty.MP_BASE_COLOR)
    brilho = mel.create_material_expression(mat_estrutura, unreal.MaterialExpressionMultiply, -300, 200)
    brilho.set_editor_property("const_b", 0.3)
    mel.connect_material_expressions(cor, "", brilho, "A")
    mel.connect_material_property(brilho, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    rugosidade = mel.create_material_expression(mat_estrutura, unreal.MaterialExpressionConstant, -300, 100)
    rugosidade.set_editor_property("r", 0.2)
    mel.connect_material_property(rugosidade, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat_estrutura)
eal.save_loaded_asset(mat_estrutura)
print("material:", mat_estrutura.get_path_name())

# --- teclas
imc = eal.load_asset(IMC)
acoes = {}
for nome, tecla in TECLAS:
    path = f"{ACTIONS}/{nome}"
    ia = eal.load_asset(path) if eal.does_asset_exist(path) else \
        at.create_asset(nome, ACTIONS, unreal.InputAction, unreal.InputAction_Factory())
    eal.save_loaded_asset(ia)
    acoes[nome] = ia
    if not any(m.action == ia for m in imc.get_editor_property("default_key_mappings").mappings):
        key = unreal.Key()
        key.set_editor_property("key_name", tecla)
        imc.map_key(ia, key)
eal.save_loaded_asset(imc)
print("IMC_Default:", sorted((m.action.get_name(), str(m.key.get_editor_property("key_name")))
                             for m in imc.get_editor_property("default_key_mappings").mappings))

# --- componente de combate no herói
bp = eal.load_asset(HERO)


def handles():
    return {str(lib.get_variable_name(lib.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}


def add_component(cls, name):
    hs = handles()
    if name in hs:
        return lib.get_associated_object(lib.get_data(hs[name]))
    actor_handle = sds.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=actor_handle, new_class=cls, blueprint_context=bp)
    h, fail = sds.add_new_subobject(params)
    assert lib.is_handle_valid(h), f"{name}: {fail}"
    sds.rename_subobject(h, unreal.Text(name))
    return lib.get_associated_object(lib.get_data(h))


combate = add_component(unreal.NRCombateComponent, "Combate")
morte = eal.load_asset(DEATH)
assert morte, f"animação de morte não encontrada: {DEATH}"
combate.set_editor_property("AnimMorte", morte)
combate.set_editor_property("MaterialProjetil", mat)
combate.set_editor_property("MaterialEstrutura", mat_estrutura)
combate.set_editor_property("NivelUltimate", NIVEL_ULTIMATE)
combate.set_editor_property("AcaoAtaque", acoes["IA_AtaqueBasico"])
combate.set_editor_property("AcaoMagiaPrincipal", acoes["IA_MagiaPrincipal"])
combate.set_editor_property("AcaoMagia2", acoes["IA_Magia2"])
combate.set_editor_property("AcaoUltimate", acoes["IA_Ultimate"])
combate.set_editor_property("AcaoConsumivel1", acoes["IA_Consumivel1"])
combate.set_editor_property("AcaoConsumivel2", acoes["IA_Consumivel2"])
combate.set_editor_property("AcaoConsumivel3", acoes["IA_Consumivel3"])

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
eal.save_loaded_asset(bp)
print("BP_HeroBase componentes:", sorted(handles()))
