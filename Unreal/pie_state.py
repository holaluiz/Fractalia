"""Print the match-loop state while PIE runs (hero, drop ship, storm). Usage: ue_py.py pie_state.py"""
import unreal

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
acts = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)


def of(name):
    return [a for a in acts if a.get_class().get_name() == name]


gs = unreal.GameplayStatics.get_game_state(w)
print("server time:", round(gs.get_server_world_time_seconds(), 1))
for h in of("BP_HeroBase_C"):
    cm = h.get_editor_property("character_movement")
    print("hero", h.get_actor_location(), "onShip", h.get_editor_property("bOnShip"), "sky", h.get_editor_property("bSkydiving"),
          "hidden", h.get_editor_property("hidden"), "parent", h.get_attach_parent_actor(), "mode", cm.get_editor_property("movement_mode"),
          "vz", round(h.get_velocity().z), "interact", h.get_editor_property("CurrentInteractable"))
for s in of("BP_DropShip_C"):
    print("ship", s.get_actor_location(), "flying", s.get_editor_property("bFlying"),
          "passengers", len(s.get_editor_property("Passengers")))
for s in of("BP_StormController_C"):
    print("storm started", s.get_editor_property("bStarted"), "phase", s.get_editor_property("CurPhase"),
          "closing", s.get_editor_property("bClosing"), "radius_m", round(s.get_editor_property("CurRadius") / 100, 1),
          "center", s.get_editor_property("CurCenter"), "centers", len(s.get_editor_property("Centers")))
print("pickups:", len(of("BP_Pickup_C")), "opened chests:", sum(c.get_editor_property("bOpened") for c in of("BP_LootChest_C")))
