"""GAS, passo 2 (dentro do editor, DEPOIS de compilar com ue_gas_compilar.py):  python Unreal/ue_py.py Unreal/ue_gas_setup.py

- cria/atualiza /Game/NexusRoyale/Data/DT_Itens a partir de Unreal/Data/DT_Itens.csv (linha = FNRItemRow em C++);
- põe no BP_HeroBase os componentes "Habilidades" (UNRAbilitySystemComponent) e "Inventario" (UNRInventoryComponent),
  com o arquétipo Feiticeiro e a build "Feiticeiro de Fogo" do GDD §4.2 (For 0, Agi 2, Vit 4, Int 8, Esp 6).
Idempotente. Os grafos (tempestade, pickups, consumíveis 1-3, HUD) vêm depois, pela DSL.
"""
import os

import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data", "DT_Itens.csv")
DT = "/Game/NexusRoyale/Data/DT_Itens"
HERO = "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase"

row_struct = unreal.load_object(None, "/Script/NexusRoyale.NRItemRow")
assert row_struct, "FNRItemRow não carregou: o módulo C++ NexusRoyale está compilado e o editor foi reaberto?"

# --- DT_Itens
if eal.does_asset_exist(DT):
    table = eal.load_asset(DT)
else:
    factory = unreal.DataTableFactory()
    factory.set_editor_property("struct", row_struct)
    table = at.create_asset("DT_Itens", "/Game/NexusRoyale/Data", unreal.DataTable, factory)
ok = unreal.DataTableFunctionLibrary.fill_data_table_from_csv_file(table, CSV)
eal.save_loaded_asset(table)
names = unreal.DataTableFunctionLibrary.get_data_table_row_names(table)
print(f"DT_Itens: preenchido={ok}, {len(names)} linhas")

# --- componentes do herói
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


asc = add_component(unreal.NRAbilitySystemComponent, "Habilidades")
inv = add_component(unreal.NRInventoryComponent, "Inventario")

arq = unreal.NRArquetipoBase()
arq.set_editor_property("Nome", unreal.Text("Feiticeiro"))
arq.set_editor_property("Vida", 400.0)
arq.set_editor_property("Mana", 260.0)
arq.set_editor_property("Velocidade", 6.0)
build = unreal.NRPontosBuild()
for k, v in {"Forca": 0, "Agilidade": 2, "Vitalidade": 4, "Intelecto": 8, "Espirito": 6}.items():
    build.set_editor_property(k, v)
asc.set_editor_property("Arquetipo", arq)
asc.set_editor_property("Build", build)
asc.set_editor_property("bInicializarNoBeginPlay", True)
inv.set_editor_property("TabelaItens", table)

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
eal.save_loaded_asset(bp)
print("BP_HeroBase componentes:", sorted(handles()))
