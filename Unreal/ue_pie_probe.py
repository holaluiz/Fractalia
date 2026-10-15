import unreal

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
print("game world:", world.get_name() if world else None)
if world:
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    print("pawn:", pawn.get_class().get_name() if pawn else None)
    if pawn:
        print("loc:", pawn.get_actor_location())
        mesh = pawn.get_editor_property("mesh")
        print("mesh asset:", mesh.get_editor_property("skeletal_mesh_asset").get_name() if mesh.get_editor_property("skeletal_mesh_asset") else None)
        print("visible:", mesh.is_visible(), "hidden in game:", mesh.get_editor_property("hidden_in_game"))
        print("anim instance:", mesh.get_anim_instance())
        print("comp loc/rot:", mesh.get_world_location(), mesh.get_world_rotation())
        for bone in ("root", "pelvis", "spine_03", "head", "upperarm_l", "hand_l", "thigh_r", "foot_r"):
            print(" ", bone, mesh.get_socket_location(bone))
        cam = unreal.GameplayStatics.get_player_camera_manager(world, 0)
        print("camera:", cam.get_camera_location(), cam.get_camera_rotation())
