"""Mapa v2, interface: WBP_Mapa (minimapa / tela cheia / queda) e HUD_NexusRoyale (cria os mapas, tecla M, abre o
mapa da queda sozinho no dirigível). Usa o Builder do ue_br_build.py (variáveis, funções, DSL) e o UMGToolSet.

Uso:  python -I Unreal/ue_mapa_ui_build.py [assets|members|graphs|input|gm|all]
  assets   IA_Mapa na tecla M (IMC_Default), HUD_NexusRoyale e WBP_Mapa com uma Image "Imagem" como raiz
  members  variáveis e funções (Builder)
  graphs   DSL de Unreal/Blueprints/WBP_Mapa__*.dsl e HUD_NexusRoyale__*.dsl
  input    evento IA_Mapa (Started) -> AlternarMapa no HUD (a DSL não cria evento de input)
  gm       GM_NexusRoyale passa a usar o HUD_NexusRoyale
Idempotente. O desenho em si fica no material M_UI_Mapa (Unreal/ue_mapa_ui_material.py).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ue_br_build as bb  # noqa: E402

UI = "/Game/NexusRoyale/UI/Mapa"
UMG = "UMGToolSet.UMGToolSet"
bb.PATHS.update({"WBP_Mapa": f"{UI}/WBP_Mapa", "HUD_NexusRoyale": f"{UI}/HUD_NexusRoyale"})
bb.SPEC.update({
    "WBP_Mapa": {
        # MaterialMapa = MI_UI_Minimapa (redondo, 150 m em volta do jogador) ou MI_UI_MapaCompleto (ilha inteira);
        # os valores globais (jogador, tempestade, rota) vão para a MPC_Mapa no Atualizar.
        "vars": [("MaterialMapa", ("obj", "/Script/Engine.MaterialInterface"))],
        # a DSL não continua depois de um IsValid com ramos: cada parte é uma função que termina no próprio ramo
        "fns": {"Atualizar": [], "AtualizarJogador": [], "AtualizarTempestade": [], "AtualizarRota": [],
                "DefinirMaterial": [("NovoMaterial", ("obj", "/Script/Engine.MaterialInterface"))]},
    },
    "HUD_NexusRoyale": {
        "vars": [("Mini", ("obj", "WBP_Mapa")), ("Completo", ("obj", "WBP_Mapa")), ("bAberto", "bool"), ("bQueda", "bool")],
        "fns": {"AlternarMapa": [], "AtualizarQueda": [], "MostrarCompleto": [("Mostrar", "bool")]},
    },
})

PY_ASSETS = r'''
import unreal
eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
ia_path = "/Game/Input/Actions/IA_Mapa"
ia = eal.load_asset(ia_path) if eal.does_asset_exist(ia_path) else \
    at.create_asset("IA_Mapa", "/Game/Input/Actions", unreal.InputAction, unreal.InputAction_Factory())
eal.save_loaded_asset(ia)
imc = eal.load_asset("/Game/Input/IMC_Default")
if not any(m.action == ia for m in imc.get_editor_property("default_key_mappings").mappings):
    key = unreal.Key()
    key.set_editor_property("key_name", "M")
    imc.map_key(ia, key)
    eal.save_loaded_asset(imc)
print("IMC_Default:", sorted({m.action.get_name() for m in imc.get_editor_property("default_key_mappings").mappings}))
hud = "%s/HUD_NexusRoyale" % "UI_PATH"
if not eal.does_asset_exist(hud):
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.HUD)
    at.create_asset("HUD_NexusRoyale", "UI_PATH", unreal.Blueprint, f)
eal.save_asset(hud)
print("HUD:", eal.does_asset_exist(hud))
'''.replace("UI_PATH", UI)

PY_GM = r'''
import unreal
eal = unreal.EditorAssetLibrary
gm = eal.load_asset("/Game/NexusRoyale/Blueprints/Core/GM_NexusRoyale")
hud = eal.load_blueprint_class("UI_PATH/HUD_NexusRoyale")
unreal.get_default_object(gm.generated_class()).set_editor_property("hud_class", hud)
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
eal.save_asset("/Game/NexusRoyale/Blueprints/Core/GM_NexusRoyale")
print("GM HUD:", unreal.get_default_object(gm.generated_class()).get_editor_property("hud_class").get_name())
'''.replace("UI_PATH", UI)


def run_py(code):
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "ue_py.py"), "-c", code], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=240)
    print((p.stdout + p.stderr).strip()[-1500:])


def umg(b, tool, args):
    res = b.c.call("call_tool", {"toolset_name": UMG, "tool_name": tool, "arguments": args})
    txt = res["content"][0]["text"] if res and res.get("content") else ""
    if res.get("isError"):
        print(f"  ! {tool}: {txt[:500]}")
        return None
    try:
        return json.loads(txt).get("returnValue")
    except (ValueError, AttributeError):
        return txt


def assets(b):
    run_py(PY_ASSETS)
    wbp = bb.ref("WBP_Mapa")
    have = umg(b, "ListWidgetBlueprints", {"folderPath": UI}) or []
    if "WBP_Mapa" not in json.dumps(have):
        umg(b, "CreateWidgetBlueprint", {"folderPath": UI, "assetName": "WBP_Mapa",
                                         "parentClass": {"refPath": "/Script/UMG.UserWidget"}})
        print("  + WBP_Mapa")
    widgets = umg(b, "GetWidgets", {"widgetBlueprint": wbp}) or {}
    if "Imagem" not in json.dumps(widgets):
        img = umg(b, "AddWidget", {"widgetBlueprint": wbp, "widgetClass": {"refPath": "/Script/UMG.Image"},
                                   "widgetDisplayName": "Imagem", "parentWidget": None, "childIndex": 0})
        print("  + Imagem:", json.dumps(img)[:300])
        widgets = umg(b, "GetWidgets", {"widgetBlueprint": wbp}) or {}
    image_ref = None
    for w in (widgets.get("Widgets") or widgets.get("widgets") or []):
        if "Imagem" in json.dumps(w):
            image_ref = w.get("Widget") or w.get("widget") or w
            break
    if image_ref:
        umg(b, "ToggleWidgetAsVariable", {"widgetBlueprint": wbp, "widget": image_ref, "bIsVariable": True})
    print("  tree:", json.dumps(widgets)[:400])
    print("  compile WBP:", umg(b, "CompileWidgetBlueprint", {"widgetBlueprint": wbp}))


PY_CLEAN = r'''
import unreal
bel = unreal.BlueprintEditorLibrary
eal = unreal.EditorAssetLibrary
bp = eal.load_asset("UI_PATH/WBP_Mapa")
for fn in ("Configurar",):  # versão antiga (com MID), substituída pela MPC + instâncias
    try:
        bel.remove_function_graph(bp, fn)
        print("removida função", fn)
    except Exception as e:
        print("função", fn, "não removida:", e)
bel.remove_unused_variables(bp)
bel.compile_blueprint(bp)
eal.save_asset("UI_PATH/WBP_Mapa")
print("variáveis restantes:", [v for v in ("Modo", "MeiaVista", "Pixels", "MID", "MaterialMapa") if bp.generated_class() and unreal.get_default_object(bp.generated_class()).get_editor_property(v) is not None] if False else "ok")
'''.replace("UI_PATH", UI)


def wire_input(b):
    graph = {"refPath": bb.ref("HUD_NexusRoyale")["refPath"] + ":EventGraph"}
    for title in ("IA_Mapa", "AlternarMapa"):
        for n in b.tool("find_nodes", {"graph": graph, "title": title})[0] or []:
            b.tool("delete_node", {"node": n})
    ev, _ = b.tool("create_node", {"graph": graph, "type_id": "Input|EnhancedActionEvents|IA_Mapa", "pos": {"x": -400, "y": 900}})
    call, _ = b.tool("create_node", {"graph": graph, "type_id": "CallFunction|AlternarMapa", "pos": {"x": 0, "y": 900}})
    ev_info = b.tool("get_node_infos", {"nodes": [ev]})[0][0]
    call_info = b.tool("get_node_infos", {"nodes": [call]})[0][0]
    out = next(p["pin_id"] for p in ev_info["output_pins"] if p.get("name") == "Started")
    inp = next(p["pin_id"] for p in call_info["input_pins"] if p.get("name") == "execute")
    b.tool("connect_pins", {"output_pin": out, "input_pin": inp})
    print("  IA_Mapa Started -> AlternarMapa")
    b.compile("HUD_NexusRoyale")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    b = bb.Builder()
    if what in ("assets", "all"):
        print("[assets]")
        assets(b)
    if what in ("members", "all"):
        for bp in ("WBP_Mapa", "HUD_NexusRoyale"):
            print(f"[members] {bp}")
            b.members(bp)
    if what in ("graphs", "all"):
        for bp in ("WBP_Mapa", "HUD_NexusRoyale"):
            print(f"[graphs] {bp}")
            b.write_graphs(bp)
    if what in ("clean", "all"):
        print("[clean]")
        run_py(PY_CLEAN)
    if what in ("input", "all"):
        print("[input]")
        wire_input(b)
    if what in ("gm", "all"):
        print("[gm]")
        run_py(PY_GM)


if __name__ == "__main__":
    main()
