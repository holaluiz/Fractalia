import unreal

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor = next(a for a in eas.get_all_level_actors() if a.get_actor_label() == "Showcase_Lumi")
for comp in actor.get_components_by_class(unreal.SkeletalMeshComponent):
    m = comp.get_editor_property("skeletal_mesh_asset")
    print(f"COMP {comp.get_name()}: mesh={m.get_name() if m else None} visible={comp.is_visible()} "
          f"anim={comp.get_editor_property('anim_class')} mode={comp.get_editor_property('animation_mode')}")
    print("   overrides:", [x.get_name() if x else None for x in comp.get_editor_property("override_materials")])
    print("   world:", comp.get_world_location(), "scale:", comp.get_world_scale())
    for bone in ("root", "pelvis", "Head", "hand_l", "foot_l"):
        print(f"   {bone}: {comp.get_socket_location(bone)}")
bp = unreal.EditorAssetLibrary.load_asset("/Game/NexusRoyale/Blueprints/BP_Hero_Lumi")
cdo_mesh = unreal.get_default_object(bp.generated_class()).get_editor_property("mesh")
print("CDO mesh:", cdo_mesh.get_editor_property("skeletal_mesh_asset"), cdo_mesh.get_editor_property("relative_location"),
      cdo_mesh.get_editor_property("relative_scale3d"))
