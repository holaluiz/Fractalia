import unreal

eal = unreal.EditorAssetLibrary
AP = unreal.AnimPoseExtensions
for mesh_path in ("/Game/NexusRoyale/Heroes/SK_Caramelo", "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"):
    mesh = eal.load_asset(mesh_path)
    skel = mesh.get_editor_property("skeleton")
    pose = AP.get_reference_pose(skel)
    print("==", mesh_path.split("/")[-1])
    for bone in ("root", "pelvis", "spine_01", "spine_03", "head", "upperarm_l", "hand_l", "thigh_r", "foot_r"):
        try:
            loc = AP.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.LOCAL)
            wld = AP.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.WORLD)
            print(f"  {bone:11s} local_t={loc.translation} world_t={wld.translation} local_s={loc.scale3d}")
        except Exception as e:
            print(f"  {bone}: {e}")
