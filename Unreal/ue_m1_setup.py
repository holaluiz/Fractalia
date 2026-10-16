"""Marco M1 (Docs/Game/MASTER_PLAN.md): liga a máquina de estados da partida ao GM_NexusRoyale.

Rodar com o editor aberto, fora do PIE, DEPOIS de compilar o módulo com o ANRGameMode:
    python Unreal/ue_py.py Unreal/ue_m1_setup.py

- troca o pai do GM_NexusRoyale (era o BP_ThirdPersonGameMode do template) pelo ANRGameMode (C++);
- guarda e devolve os valores que importam (herói, HUD, PlayerController, variáveis do dirigível), porque o reparent
  pode trocar o que vinha herdado do pai antigo;
- GameState e PlayerState passam a ser os do C++ (ANRGameState, ANRPlayerState);
- salva só o GM_NexusRoyale (sem depender da marca de "alterado": ver K-01 no KNOWN_ISSUES).
O EventGraph (IniciarQueda no lugar do timer do BeginPlay) é gravado depois, pela DSL:
    python Unreal/ue_dsl_grafos.py GM_NexusRoyale EventGraph --ler
Idempotente.
"""
import unreal

eal = unreal.EditorAssetLibrary
bel = unreal.BlueprintEditorLibrary

GM = "/Game/NexusRoyale/Blueprints/Core/GM_NexusRoyale"
CLASSES = ["default_pawn_class", "hud_class", "player_controller_class", "spectator_class"]
VARIAVEIS = ["ShipAltitude", "ShipPathHalfLength", "ShipLateralSpread"]

bp = eal.load_asset(GM)
assert bp, f"não achei {GM}"
cdo = unreal.get_default_object(bp.generated_class())


def ler():
    c = unreal.get_default_object(bp.generated_class())
    classes = {k: c.get_editor_property(k) for k in CLASSES + ["game_state_class", "player_state_class"]}
    variaveis = {}
    for v in VARIAVEIS:
        try:
            variaveis[v] = c.get_editor_property(v)
        except Exception as e:  # noqa: BLE001
            variaveis[v] = f"(erro: {e})"
    return classes, variaveis


antes_classes, antes_vars = ler()
print("pai antes:", bel.get_blueprint_parent_class(bp).get_name())
print("antes:", {k: (v.get_name() if v else None) for k, v in antes_classes.items()}, antes_vars)

alvo = unreal.NRGameMode.static_class()
if bel.get_blueprint_parent_class(bp) != alvo:
    assert bel.reparent_blueprint(bp, alvo) is not False, "reparent falhou"
    bel.compile_blueprint(bp)

cdo = unreal.get_default_object(bp.generated_class())
for k in CLASSES:
    if antes_classes[k] is not None and cdo.get_editor_property(k) != antes_classes[k]:
        cdo.set_editor_property(k, antes_classes[k])
cdo.set_editor_property("game_state_class", unreal.NRGameState.static_class())
cdo.set_editor_property("player_state_class", unreal.NRPlayerState.static_class())
for v, valor in antes_vars.items():
    if not isinstance(valor, str):
        cdo.set_editor_property(v, valor)

bel.compile_blueprint(bp)
assert eal.save_loaded_asset(bp, False), "GM_NexusRoyale não foi salvo"

depois_classes, depois_vars = ler()
print("pai depois:", bel.get_blueprint_parent_class(bp).get_name())
print("depois:", {k: (v.get_name() if v else None) for k, v in depois_classes.items()}, depois_vars)
