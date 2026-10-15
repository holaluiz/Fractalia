"""Re-import the Downtown City pieces without vertex colors (removes the red wear-mask tint) and rebuild the city."""
import glob
import importlib.util
import os

import unreal


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


q = load("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
pois = load("pois", r"D:\meus documentos\Fortnite\Unreal\ue_build_pois.py")
env = load("env", r"D:\meus documentos\Fortnite\Unreal\ue_env_import.py") if False else None
eal = unreal.EditorAssetLibrary

pois.clear("POI/Cidade")
if eal.does_directory_exist("/Game/Quaternius/Env/City"):
    eal.delete_directory("/Game/Quaternius/Env/City")
WANTED = ["Building_Large_2", "Building_Medium_2_001", "Building_Small_1", "Street_4WayIntersection",
          "Street_4Lane", "Street_2Lane", "Street_TIntersection", "Street_Asphalt_6x6", "Sidewalk_Straight_3m",
          "Sidewalk_Corner_Round_3m", "Sidewalk_NoCurb_3m", "Sidewalk_Planter", "Prop_Bollard", "Prop_Planter_Single",
          "Prop_ManholeCover", "Prop_ACUnit", "Decal_Crosswalk", "Decal_DoubleYellow_Straight",
          "Entrance_Concrete_2x2", "Stairs_Entrance_Concrete"]
src = rf"{q.QROOT}\DowntownCityMegaKit"
files = [f for f in glob.glob(os.path.join(glob.escape(src), "**", "*.gltf"), recursive=True)
         if os.path.splitext(os.path.basename(f))[0] in WANTED]
for i, f in enumerate(sorted(files)):
    q.import_interchange(f, "/Game/Quaternius/Env/City", ignore_vertex_colors=True)
    if i % 6 == 5:
        unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
        unreal.SystemLibrary.collect_garbage()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
m = eal.load_asset("/Game/Quaternius/Env/City/Street_4Lane/StaticMeshes/Street_4Lane")
print("re-imported", len(files), "city pieces; vertex colors on street:",
      unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).has_vertex_colors(m) if m else "missing")
pois._meshes.clear()
pois._collision_done.clear()
pois.main(which=("Cidade",))
