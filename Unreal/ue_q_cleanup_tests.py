import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Test_"):
        eas.destroy_actor(a)
shown = [a.get_actor_label() for a in eas.get_all_level_actors() if a.get_actor_label().startswith("Showcase_")]
print("showcase:", shown)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
