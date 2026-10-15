"""MVP, passo 3 (dentro do editor, DEPOIS do ue_gas_setup.py):  python Unreal/ue_py.py Unreal/ue_mvp_setup.py

- cria o material dos projéteis /Game/NexusRoyale/VFX/M_Projetil (unlit, parâmetro de vetor "Cor");
- cria as Input Actions IA_AtaqueBasico, IA_MagiaPrincipal e IA_Consumivel1..3 e mapeia no IMC_Default:
  botão esquerdo, Q e 1/2/3 (GDD §14). Também mapeia o IA_Interact no F, que tinha ficado de fora;
- põe no BP_HeroBase o componente "Combate" (UNRCombateComponent): ataque básico, Bola de Fogo,
  consumíveis, HUD e morte (animação Death01 da UAL1).
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
ACTIONS = "/Game/Input/Actions"
IMC = "/Game/Input/IMC_Default"
DEATH = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_StandardDeath01"
TECLAS = [  # (Input Action, tecla)
    ("IA_Interact", "F"),
    ("IA_AtaqueBasico", "LeftMouseButton"),
    ("IA_MagiaPrincipal", "Q"),
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
combate.set_editor_property("AcaoAtaque", acoes["IA_AtaqueBasico"])
combate.set_editor_property("AcaoMagiaPrincipal", acoes["IA_MagiaPrincipal"])
combate.set_editor_property("AcaoConsumivel1", acoes["IA_Consumivel1"])
combate.set_editor_property("AcaoConsumivel2", acoes["IA_Consumivel2"])
combate.set_editor_property("AcaoConsumivel3", acoes["IA_Consumivel3"])

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
eal.save_loaded_asset(bp)
print("BP_HeroBase componentes:", sorted(handles()))
