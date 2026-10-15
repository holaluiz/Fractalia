"""Step 4: hero Blueprints from the Quaternius base characters (+ hair components) and the hero line-up."""
import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()

CH = "/Game/Quaternius/Characters"
BPS = "/Game/NexusRoyale/Blueprints"
ABP = "/Game/Quaternius/Anims/Hero/ABP_Hero"
PARENT = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
HEROES = {  # name: (body, [extra skeletal meshes rigged to the head])
    "Brakka": ("Superhero_Male_FullBody", ["Hair_Buzzed", "Hair_Beard"]),
    "Vela": ("Superhero_Female_FullBody", ["Hair_Long"]),
    "Zephyr": ("Superhero_Male_FullBody", ["Hair_SimpleParted"]),
    "Lumi": ("Superhero_Female_FullBody", ["Hair_Buns"]),
}


def mesh(name):
    hits = [p.split(".")[0] for p in eal.list_assets(f"{CH}/{name}", recursive=True)
            if str(eal.find_asset_data(p).asset_class_path.asset_name) == "SkeletalMesh"]
    return eal.load_asset(hits[0])


def mesh_handle(bp):
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        if str(lib.get_variable_name(lib.get_data(h))) in ("Mesh", "CharacterMesh0"):
            return h
    raise RuntimeError("Mesh component not found")


abp_class = eal.load_asset(ABP).generated_class()
if not eal.does_directory_exist(BPS):
    eal.make_directory(BPS)
for hero, (body, extras) in HEROES.items():
    path = f"{BPS}/BP_Hero_{hero}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", eal.load_blueprint_class(PARENT))
    bp = at.create_asset(f"BP_Hero_{hero}", BPS, unreal.Blueprint, factory)
    cdo = unreal.get_default_object(bp.generated_class())
    comp = cdo.get_editor_property("mesh")
    comp.set_editor_property("skeletal_mesh_asset", mesh(body))
    comp.set_editor_property("anim_class", abp_class)
    parent = mesh_handle(bp)
    for extra in extras:
        params = unreal.AddNewSubobjectParams(parent_handle=parent, new_class=unreal.SkeletalMeshComponent,
                                              blueprint_context=bp)
        handle, fail = sds.add_new_subobject(params)
        if not lib.is_handle_valid(handle):
            print(f"  {hero}: could not add {extra}: {fail}")
            continue
        sds.rename_subobject(handle, unreal.Text(extra))
        c = lib.get_object(lib.get_data(handle))
        c.set_editor_property("skeletal_mesh_asset", mesh(extra))
        c.set_editor_property("anim_class", abp_class)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)
    comps = [str(lib.get_variable_name(lib.get_data(h))) for h in sds.k2_gather_subobject_data_for_blueprint(bp)]
    m = unreal.get_default_object(bp.generated_class()).get_editor_property("mesh").get_editor_property("skeletal_mesh_asset")
    print(f"HERO {hero}: body={m.get_name() if m else None} components={comps}")

# default pawn + line-up on the Nexus plaza
gm = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
unreal.get_default_object(gm.generated_class()).set_editor_property(
    "default_pawn_class", eal.load_blueprint_class(f"{BPS}/BP_Hero_Brakka"))
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
eal.save_loaded_asset(gm)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Showcase_"):
        eas.destroy_actor(a)
for i, hero in enumerate(HEROES):
    x = (i - (len(HEROES) - 1) / 2) * 200.0
    actor = eas.spawn_actor_from_class(eal.load_blueprint_class(f"{BPS}/BP_Hero_{hero}"),
                                       unreal.Vector(x, -1250.0, 800.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    actor.set_actor_label(f"Showcase_{hero}")
    actor.set_folder_path("Showcase")
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
print("DONE")
