import unreal

eal = unreal.EditorAssetLibrary
for p in eal.list_assets("/Game/NexusRoyale/Anims/Caramelo", recursive=True):
    d = eal.find_asset_data(p)
    print(" ", str(d.asset_class_path.asset_name), p.split(".")[0].replace("/Game/NexusRoyale/Anims/Caramelo", ""))
print("ABP copies anywhere:", [p for p in eal.list_assets("/Game", recursive=True) if "ABP_Unarmed" in p])
rig = eal.load_asset("/Game/NexusRoyale/Retarget/IK_Caramelo")
c = unreal.IKRigController.get_controller(rig)
print("IK_Caramelo root:", c.get_retarget_root(), "chains:", [(str(x.chain_name), str(x.start_bone.bone_name), str(x.end_bone.bone_name)) for x in c.get_retarget_chains()])
rc = unreal.IKRetargeterController.get_controller(eal.load_asset("/Game/NexusRoyale/Retarget/RTG_Caramelo"))
print("mapping:", [(str(s.get_editor_property("target_chain")), str(s.get_editor_property("source_chain"))) for s in rc.get_all_chain_settings()])
print("RunBatchRetarget:", (unreal.IKRetargetBatchOperation.run_batch_retarget.__doc__ or "").strip().splitlines()[:2] if hasattr(unreal.IKRetargetBatchOperation, "run_batch_retarget") else "missing")
print([n for n in dir(unreal) if "BatchRetarget" in n or "RetargetBatch" in n])
