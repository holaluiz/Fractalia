import unreal

eal = unreal.EditorAssetLibrary
AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
for path in ("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple", "/Game/NexusRoyale/Heroes/SK_Caramelo",
             "/Game/NexusRoyale/Heroes/SK_Brakka"):
    mesh = eal.load_asset(path)
    pose = AP.get_reference_pose(mesh.get_editor_property("skeleton"))
    foot = AP.get_bone_pose(pose, "foot_l", W).translation
    ball = AP.get_bone_pose(pose, "ball_l", W).translation
    hand = AP.get_bone_pose(pose, "hand_l", W).translation
    print(f"{path.split('/')[-1]:18s} toe_dir=({ball.x - foot.x:+.1f}, {ball.y - foot.y:+.1f})  hand_l.x={hand.x:+.1f}")
print("shaders remaining:", unreal.ShaderCompilingManager.get_num_remaining_jobs() if hasattr(unreal, "ShaderCompilingManager") else "n/a")
