"""Drive and inspect the creep camps while PIE runs.

Usage:  python ue_py.py -c "ACT='state'; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_creeps.py').read())"
ACT:    state            creeps (hp, target, dead, moving, distance home), camps, hero DamageTaken
        land             takes the hero off the drop ship and puts it on the ground 12 m from the first camp
        near             hero 4 m from the first camp's centre (inside AggroRadius)
        away             hero 25 m from the first camp (outside the 15 m leash)
        poke             1 damage to one creep from the hero (tests "the whole camp aggroes")
        kill             ApplyDamage 1000 from the hero to every live creep of the first camp
DELAY=<s>        (optional, any ACT) overrides the first camp's RespawnDelay in this PIE run, to test respawn quickly
"""
import math

import unreal

ACT = globals().get("ACT", "state")
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
acts = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor)


def of(*names):
    return [a for a in acts if a.get_class().get_name() in names]


def creeps():
    return [a for a in acts if a.get_class().get_name().startswith("BP_Creep_") and a.get_class().get_name() != "BP_CreepCamp_C"]


hero = (of("BP_HeroBase_C") or [None])[0]
camp = sorted(of("BP_CreepCamp_C"), key=lambda a: a.get_actor_label() if hasattr(a, "get_actor_label") else a.get_name())
camp = camp[0] if camp else None
pc = unreal.GameplayStatics.get_player_controller(w, 0)
gs = unreal.GameplayStatics.get_game_state(w)


def put_hero(dist):
    c = camp.get_actor_location()
    loc = unreal.Vector(c.x + dist, c.y, c.z + 120.0)
    hero.set_actor_location(loc, False, True)
    hero.set_actor_rotation(unreal.Rotator(0.0, 0.0, 180.0), True)
    print("hero placed", round(dist / 100, 1), "m from camp at", loc)


if "DELAY" in globals() and camp:
    camp.set_editor_property("RespawnDelay", float(DELAY))
    print("RespawnDelay ->", DELAY)

if ACT == "land":
    for s in of("BP_DropShip_C"):
        if hero in list(s.get_editor_property("Passengers")):
            s.call_method("Eject", (hero,))
    put_hero(1200.0)
elif ACT == "near":
    put_hero(400.0)
elif ACT == "away":
    put_hero(2500.0)
elif ACT == "poke":
    live = [c for c in creeps() if not c.get_editor_property("IsDead")]
    unreal.GameplayStatics.apply_damage(live[0], 1.0, pc, hero, None)
    print("poked", live[0].get_name())
elif ACT == "kill":
    for c in creeps():
        if not c.get_editor_property("IsDead"):
            unreal.GameplayStatics.apply_damage(c, 1000.0, pc, hero, None)
    print("killed all")

# --- state
print("time", round(gs.get_server_world_time_seconds(), 1))
if hero:
    print("hero", hero.get_actor_location(), "DamageTaken", hero.get_editor_property("DamageTaken"),
          "mode", hero.get_editor_property("character_movement").get_editor_property("movement_mode"))
for cp in of("BP_CreepCamp_C"):
    print("camp", cp.get_name(), cp.get_actor_location(), "pending", cp.get_editor_property("bRespawnPending"),
          "alive", cp.get_editor_property("AliveCount"), "tracked", len(cp.get_editor_property("Creeps")))
for c in creeps():
    loc, home = c.get_actor_location(), c.get_editor_property("HomeLocation")
    t = c.get_editor_property("Target")
    print(f"  {c.get_name():28s} hp {c.get_editor_property('Health'):6.1f} dead {c.get_editor_property('IsDead')!s:5s} "
          f"moving {c.get_editor_property('bMoving')!s:5s} target {t.get_name() if t else '-':16s} "
          f"home {math.dist((loc.x, loc.y), (home.x, home.y)) / 100:5.1f} m  "
          f"hero {(math.dist((loc.x, loc.y, loc.z), (hero.get_actor_location().x, hero.get_actor_location().y, hero.get_actor_location().z)) / 100) if hero else -1:5.1f} m  "
          f"z {loc.z:7.1f}")
