import inspect

import unreal


def doc(obj, names):
    for n in names:
        f = getattr(obj, n, None)
        if f is None:
            print(f"  {obj.__name__}.{n}: MISSING")
            continue
        d = (f.__doc__ or "").strip().splitlines()
        print(f"  {obj.__name__}.{n}: {d[0] if d else ''}")


doc(unreal.IKRigController, ["get_controller", "set_skeletal_mesh", "apply_auto_generated_retarget_definition",
                             "apply_auto_fbik", "add_retarget_chain", "set_retarget_root", "get_retarget_chains",
                             "get_retarget_root"])
doc(unreal.IKRetargeterController, ["get_controller", "set_ik_rig", "set_preview_mesh", "auto_map_chains",
                                    "auto_align_all_bones", "add_default_ops", "assign_ik_rig_to_all_ops",
                                    "get_all_chain_settings", "set_current_retarget_pose", "create_retarget_pose",
                                    "reset_retarget_pose"])
doc(unreal.IKRetargetBatchOperation, ["duplicate_and_retarget"])
print("RetargetSourceOrTarget:", [m for m in dir(unreal.RetargetSourceOrTarget) if m.isupper()])
print("AutoMapChainType:", [m for m in dir(unreal.AutoMapChainType) if m.isupper()] if hasattr(unreal, "AutoMapChainType") else None)
print("factories:", [n for n in dir(unreal) if n.startswith("IKR") and "Factory" in n])
