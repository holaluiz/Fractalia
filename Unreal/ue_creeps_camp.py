"""Creeps step 3: BP_CreepCamp, creep tuning (GDD 12) and camp placement. Runs inside the editor; idempotent.

Order:  ue_py.py ue_creeps_camp.py          -> creates BP_CreepCamp (and stops: its members do not exist yet)
        ue_br_build.py members BP_Creep BP_CreepCamp BP_HeroBase
        ue_py.py ue_creeps_camp.py          -> CreepClasses becomes class<BP_Creep>[], defaults, camps placed in the level
        ue_br_build.py graphs BP_Creep BP_CreepCamp   (+ ue_write_dsl.py for BP_HeroBase EventGraph)

Placement is data-driven: CAMPS_FILE has the same shape as mapa_ue.json "acampamentos" ({"pequeno": [{x, y, z}], ...}),
so the ~1 km map can reuse place_camps() with its own data. z is only a hint: the camp is dropped onto the ground.
"""
import json
import os

import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
at = unreal.AssetToolsHelpers.get_asset_tools()
bel = unreal.BlueprintEditorLibrary

FOLDER = "/Game/NexusRoyale/Blueprints/Creeps"
CREEPS = "/Game/Quaternius/Creeps"
HERE = os.path.dirname(os.path.abspath(globals().get("__file__", r"D:\meus documentos\Fortnite\Unreal\x.py")))
LEVEL = "/Game/NexusRoyale/Maps/L_Island"
CAMPS_FILE = os.path.join(HERE, "Data", "Camps_L_Island.json")

# GDD 12 + 7.2. Damage/cooldown are first guesses: 3 Imps at 12 dmg / 1.5 s cost a level-1 Feiticeiro (400 HP, 60 dmg/s)
# about 25-30% of their health over the ~7.5 s fight ("custo real" rule). Ranges in cm.
BASE = dict(MaxHealth=150.0, XPReward=30, AggroRadius=700.0, LeashRadius=1500.0, AttackRange=170.0,
            AttackDamage=12.0, AttackCooldown=1.5)
MONSTERS = {
    "Imp": dict(),
    "Puglin": dict(MaxHealth=700.0, XPReward=120, AttackRange=150.0, AttackDamage=30.0, AttackCooldown=1.8),
}
ANIMS = dict(HitAnim="UAL1_StandardHit_Chest", AttackAnim="UAL2_StandardZombie_Scratch", DeathAnim="UAL1_StandardDeath01")
CAMP_KINDS = {  # GDD 12: small = 3 Imps / 90 s, medium = Puglin + 2 Imps / 150 s (elite needs the Puglin Ancião)
    "pequeno": (["Imp", "Imp", "Imp"], 90.0),
    "medio": (["Puglin", "Imp", "Imp"], 150.0),
}
CAMP_DROPS = {  # GDD 12: (DropChance, bDropGrimoire). Small: 50% food or potion; medium: a grimoire (Comum-Raro), always
    "pequeno": (0.5, False),
    "medio": (1.0, True),
}


def cdo(path):
    return unreal.get_default_object(eal.load_blueprint_class(path))


def has_var(path, name):
    try:
        cdo(path).get_editor_property(name)
        return True
    except Exception:
        return False


def save(path):
    bp = eal.load_asset(path)
    bel.compile_blueprint(bp)
    eal.save_loaded_asset(bp)


def creep_class(name):
    return eal.load_blueprint_class(f"{FOLDER}/BP_Creep_{name}")


def make_camp_bp():
    path = f"{FOLDER}/BP_CreepCamp"
    if eal.does_asset_exist(path):
        return
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.Actor)
    bp = at.create_asset("BP_CreepCamp", FOLDER, unreal.Blueprint, f)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    root = sds.k2_gather_subobject_data_for_blueprint(bp)[0]
    params = unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.BillboardComponent, blueprint_context=bp)
    h, fail = sds.add_new_subobject(params)
    if lib.is_handle_valid(h):
        sds.rename_subobject(h, unreal.Text("Icon"))
    bel.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    print("created", path)


def fix_class_array():
    """add_object_variable makes object refs; the camp needs a class<BP_Creep> array."""
    bp = eal.load_asset(f"{FOLDER}/BP_CreepCamp")
    pin = unreal.EdGraphPinType()
    pin.import_text(f'(PinCategory="class",PinSubCategoryObject="{FOLDER}/BP_Creep.BP_Creep_C",ContainerType=Array)')
    bel.change_member_variable_type(bp, "CreepClasses", pin)
    bel.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    print("CreepClasses type:", pin.export_text())


def creep_defaults():
    base = f"{FOLDER}/BP_Creep"
    c = cdo(base)
    for k, v in BASE.items():
        c.set_editor_property(k, v)
    save(base)
    for name, over in MONSTERS.items():
        path = f"{FOLDER}/BP_Creep_{name}"
        c = cdo(path)
        for k, v in {**BASE, **over}.items():
            c.set_editor_property(k, v)
        for var, clip in ANIMS.items():
            c.set_editor_property(var, eal.load_asset(f"{CREEPS}/{name}/Anims/{clip}_{name}"))
        save(path)
        print(name, {k: c.get_editor_property(k) for k in ("MaxHealth", "XPReward", "AttackDamage")},
              {k: c.get_editor_property(k).get_name() for k in ANIMS})


def camp_defaults():
    path = f"{FOLDER}/BP_CreepCamp"
    c = cdo(path)
    classes, delay = CAMP_KINDS["pequeno"]
    c.set_editor_property("CreepClasses", [creep_class(n) for n in classes])
    c.set_editor_property("SpawnRadius", 250.0)
    c.set_editor_property("RespawnDelay", delay)
    chance, grimoire = CAMP_DROPS["pequeno"]
    c.set_editor_property("DropChance", chance)
    c.set_editor_property("bDropGrimoire", grimoire)
    save(path)
    print("camp:", [x.get_name() for x in c.get_editor_property("CreepClasses")], c.get_editor_property("RespawnDelay"))


def ground_z(world, x, y, z_hint):
    hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, z_hint + 20000.0), unreal.Vector(x, y, z_hint - 20000.0),
                                                 unreal.TraceTypeQuery.ECC_VISIBILITY, False, [], unreal.DrawDebugTrace.NONE, True)
    t = hit.to_tuple()  # (blocking_hit, initial_overlap, time, distance, location, ...)
    return t[4].z if t[0] else z_hint


def place_camps(level, camps):
    if les.get_current_level().get_outermost().get_name() != level:
        les.load_level(level)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    camp_cls = eal.load_blueprint_class(f"{FOLDER}/BP_CreepCamp")
    for a in eas.get_all_level_actors():  # idempotent: replace the camps this script placed before
        if a.get_class() == camp_cls:
            eas.destroy_actor(a)
    n = 0
    for kind, spots in camps.items():
        if kind.startswith("_"):
            continue
        if kind not in CAMP_KINDS:
            print("skip camp kind", kind, len(spots))
            continue
        classes, delay = CAMP_KINDS[kind]
        for i, p in enumerate(spots):
            z = ground_z(world, p["x"], p["y"], p.get("z", 0.0))
            a = eas.spawn_actor_from_class(camp_cls, unreal.Vector(p["x"], p["y"], z))
            a.set_actor_label(f"CreepCamp_{kind}_{i + 1}")
            a.set_folder_path("Gameplay/creeps")
            a.set_editor_property("CreepClasses", [creep_class(c) for c in classes])
            a.set_editor_property("RespawnDelay", delay)
            chance, grimoire = CAMP_DROPS[kind]
            a.set_editor_property("DropChance", chance)
            a.set_editor_property("bDropGrimoire", grimoire)
            n += 1
            print("camp", a.get_actor_label(), a.get_actor_location())
    les.save_current_level()
    print("camps placed:", n, "in", level)


make_camp_bp()
if has_var(f"{FOLDER}/BP_CreepCamp", "CreepClasses"):
    fix_class_array()
    creep_defaults()
    camp_defaults()
    place_camps(LEVEL, json.load(open(CAMPS_FILE, encoding="utf-8")))
else:
    print("BP_CreepCamp has no members yet: run ue_br_build.py members BP_Creep BP_CreepCamp BP_HeroBase, then this again")
