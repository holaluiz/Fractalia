"""BR stage 1, step 1: assets for the match loop (no GAS yet).

Creates IA_Interact (F), BP_HeroBase (copy of the Quaternius hero), GM_NexusRoyale, BP_StormController,
BP_DropShip, BP_Interactable, BP_LootChest and BP_Pickup with their components. Idempotent.
"""
import unreal

eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary

ROOT = "/Game/NexusRoyale/Blueprints"
CORE, MATCH, LOOT = f"{ROOT}/Core", f"{ROOT}/Match", f"{ROOT}/Loot"
PROPS = "/Game/NexusRoyale/Props"


def new_bp(folder, name, parent):
    path = f"{folder}/{name}"
    if eal.does_asset_exist(path):
        return eal.load_asset(path), False
    f = unreal.BlueprintFactory()
    f.set_editor_property("parent_class", parent)
    return at.create_asset(name, folder, unreal.Blueprint, f), True


def handles(bp):
    return {str(lib.get_variable_name(lib.get_data(h))): h for h in sds.k2_gather_subobject_data_for_blueprint(bp)}


def add_comp(bp, cls, name, parent=None):
    hs = handles(bp)
    if name in hs:
        return lib.get_associated_object(lib.get_data(hs[name]))
    if parent is None:  # attach to the root scene component
        parent = next(h for n, h in hs.items() if n in ("DefaultSceneRoot", "Root") or
                      (lib.is_root_component(lib.get_data(h)) if hasattr(lib, "is_root_component") else False))
    params = unreal.AddNewSubobjectParams(parent_handle=parent, new_class=cls, blueprint_context=bp)
    h, fail = sds.add_new_subobject(params)
    assert lib.is_handle_valid(h), f"{bp.get_name()}.{name}: {fail}"
    sds.rename_subobject(h, unreal.Text(name))
    return lib.get_associated_object(lib.get_data(h))


def finish(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)


for folder in (CORE, MATCH, LOOT):
    if not eal.does_directory_exist(folder):
        eal.make_directory(folder)

# --- input: IA_Interact on F
ia_path = "/Game/Input/Actions/IA_Interact"
ia = eal.load_asset(ia_path) if eal.does_asset_exist(ia_path) else \
    at.create_asset("IA_Interact", "/Game/Input/Actions", unreal.InputAction, unreal.InputAction_Factory())
eal.save_loaded_asset(ia)
imc = eal.load_asset("/Game/Input/IMC_Default")
if not any(m.action == ia for m in imc.get_editor_property("default_key_mappings").mappings):
    key = unreal.Key()
    key.set_editor_property("key_name", "F")
    imc.map_key(ia, key)
    eal.save_loaded_asset(imc)
print("IMC_Default actions:", sorted({m.action.get_name() for m in imc.get_editor_property("default_key_mappings").mappings}))

# --- hero base: the assembled Quaternius hero (body + hair + outfit, ABP_Hero) becomes the shared base
hero_path = f"{CORE}/BP_HeroBase"
if not eal.does_asset_exist(hero_path):
    eal.duplicate_asset("/Game/NexusRoyale/Blueprints/BP_Hero_Brakka", hero_path)
hero = eal.load_asset(hero_path)
finish(hero)

# --- game mode: keeps the template's controller (it adds the input mapping contexts), pawn = BP_HeroBase
gm, _ = new_bp(CORE, "GM_NexusRoyale", eal.load_blueprint_class("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode"))
unreal.get_default_object(gm.generated_class()).set_editor_property("default_pawn_class", hero.generated_class())
finish(gm)

# --- storm
storm, _ = new_bp(MATCH, "BP_StormController", unreal.Actor)
wall = add_comp(storm, unreal.StaticMeshComponent, "Wall")
wall.set_editor_property("static_mesh", eal.load_asset(f"{PROPS}/SM_StormWall"))
wall.set_collision_profile_name("NoCollision")
wall.set_editor_property("cast_shadow", False)
cdo = unreal.get_default_object(storm.generated_class())
cdo.set_editor_property("replicates", True)
cdo.set_editor_property("always_relevant", True)
finish(storm)

# --- drop ship
ship, _ = new_bp(MATCH, "BP_DropShip", unreal.Actor)
hull = add_comp(ship, unreal.StaticMeshComponent, "Hull")
hull.set_editor_property("static_mesh", eal.load_asset(f"{PROPS}/SM_DropShip"))
hull.set_collision_profile_name("NoCollision")
hull.set_editor_property("relative_scale3d", unreal.Vector(2.0, 2.0, 2.0))
cdo = unreal.get_default_object(ship.generated_class())
cdo.set_editor_property("replicates", True)
cdo.set_editor_property("always_relevant", True)
finish(ship)

# --- interactables: base (trigger sphere), chest, pickup
inter, _ = new_bp(LOOT, "BP_Interactable", unreal.Actor)
sphere = add_comp(inter, unreal.SphereComponent, "InteractSphere")
sphere.set_editor_property("sphere_radius", 220.0)
sphere.set_collision_profile_name("Trigger")
unreal.get_default_object(inter.generated_class()).set_editor_property("replicates", True)
finish(inter)

chest, _ = new_bp(LOOT, "BP_LootChest", inter.generated_class())
cm = add_comp(chest, unreal.StaticMeshComponent, "ChestMesh")
cm.set_editor_property("static_mesh", eal.load_asset(f"{PROPS}/SM_Chest"))
cm.set_collision_profile_name("BlockAllDynamic")
finish(chest)

pick, _ = new_bp(LOOT, "BP_Pickup", inter.generated_class())
pm = add_comp(pick, unreal.StaticMeshComponent, "PickupMesh")
pm.set_collision_profile_name("NoCollision")
pm.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 60.0))
glow = add_comp(pick, unreal.PointLightComponent, "Glow")
glow.set_editor_property("intensity", 2500.0)
glow.set_editor_property("attenuation_radius", 250.0)
glow.set_editor_property("cast_shadows", False)
glow.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 60.0))
spin = add_comp(pick, unreal.RotatingMovementComponent, "Spin")
spin.set_editor_property("rotation_rate", unreal.Rotator(0.0, 0.0, 90.0))  # (roll, pitch, yaw) -> yaw 90 deg/s
finish(pick)

for bp in (hero, gm, storm, ship, inter, chest, pick):
    print(bp.get_path_name(), sorted(handles(bp)))
