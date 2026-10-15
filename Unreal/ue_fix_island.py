"""Fresh-import the centimeter island FBX at 1.0 into a temp path, then consolidate it over SM_Island."""
import importlib.util

import unreal

eal = unreal.EditorAssetLibrary
spec = importlib.util.spec_from_file_location("nx", r"D:\meus documentos\Fortnite\Unreal\import_nexus_assets.py")
nx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nx)
nx.use_legacy_fbx_importer()
TMP = "/Game/NexusRoyale/Map/_tmp"
if eal.does_directory_exist(TMP):
    eal.delete_directory(TMP)
nx.import_fbx(r"D:\meus documentos\Fortnite\Export\FBX\Map\SM_Island.fbx", TMP, False, static_scale=1.0)
new = eal.load_asset(f"{TMP}/SM_Island")
bb = new.get_bounding_box()
size = bb.max.x - bb.min.x
print(f"fresh import size cm: {size:.0f} x {bb.max.y - bb.min.y:.0f} x {bb.max.z - bb.min.z:.0f}")
if 30000 < size < 50000:
    new.set_material(0, nx.vertex_color_material())
    new.get_editor_property("body_setup").set_editor_property("collision_trace_flag",
                                                              unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    old = eal.load_asset("/Game/NexusRoyale/Map/SM_Island")
    ok = eal.consolidate_assets(new, [old])  # every reference to the old island now points to the new one
    print("consolidated:", ok)
    eal.rename_asset(f"{TMP}/SM_Island", "/Game/NexusRoyale/Map/SM_Island")
    isl = eal.load_asset("/Game/NexusRoyale/Map/SM_Island")
    bb = isl.get_bounding_box()
    print(f"SM_Island now: {bb.max.x - bb.min.x:.0f} cm wide, zmax {bb.max.z:.0f}")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
