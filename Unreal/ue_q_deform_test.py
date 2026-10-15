"""Deformation A/B test: raw Idle_Loop on the body and on the UAL mannequin (no AnimBP), next to the heroes."""
import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
IDLE = [p.split(".")[0] for p in eal.list_assets("/Game/Quaternius/Animations/UAL1", recursive=True)
        if p.split(".")[-1] == "UAL1_StandardIdle_Loop"][0]
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Test_"):
        eas.destroy_actor(a)
tests = {"Test_RawFemale": "/Game/Quaternius/Characters/Superhero_Female_FullBody",
         "Test_RawMale": "/Game/Quaternius/Characters/Superhero_Male_FullBody",
         "Test_UALMannequin": "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_Standard"}
for i, (label, folder) in enumerate(tests.items()):
    mesh_path = folder if eal.does_asset_exist(folder) else [p.split(".")[0] for p in eal.list_assets(folder, recursive=True)
                                                             if str(eal.find_asset_data(p).asset_class_path.asset_name) == "SkeletalMesh"][0]
    actor = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(-900.0 + i * 200.0, -900.0, 712.0),
                                       unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    actor.set_actor_label(label)
    comp = actor.skeletal_mesh_component
    comp.set_skeletal_mesh_asset(eal.load_asset(mesh_path))
    comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    comp.set_editor_property("animation_data", unreal.SingleAnimationPlayData(anim_to_play=eal.load_asset(IDLE), saved_looping=True, saved_playing=True))
    comp.play_animation(eal.load_asset(IDLE), True)
    print("spawned", label, mesh_path.split("/")[-1])

# what does ABP_Hero contain? (node classes in its graphs)
abp = eal.load_asset("/Game/Quaternius/Anims/Hero/ABP_Hero")
names = set()
for g in unreal.BlueprintEditorLibrary.find_graphs(abp) if hasattr(unreal.BlueprintEditorLibrary, "find_graphs") else []:
    names.add(g.get_name())
print("ABP graphs:", sorted(names))
