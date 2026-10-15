"""Import the environment kits (Stylized Nature, Medieval Village, Downtown City) into one folder per kit.

Only the pieces the island uses are imported; saving + garbage collection after every few files keeps the editor
inside this PC's memory budget.
"""
import glob
import importlib.util
import os

import unreal

spec = importlib.util.spec_from_file_location("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
eal = unreal.EditorAssetLibrary
ENV = "/Game/Quaternius/Env"

KITS = {
    "Nature": (rf"{q.QROOT}\StylizedNatureMegaKit\glTF", None),  # everything (68 small files)
    "Medieval": (rf"{q.QROOT}\MedievalVillageMegaKit", [
        "Wall_Plaster_Straight", "Wall_Plaster_Door_Round", "Wall_Plaster_Window_Wide_Round",
        "Wall_Plaster_Window_Thin_Round", "Wall_Plaster_WoodGrid", "Wall_UnevenBrick_Straight",
        "Wall_UnevenBrick_Door_Flat", "Wall_UnevenBrick_Window_Wide_Flat", "Corner_Exterior_Wood",
        "Corner_Exterior_Brick", "Floor_WoodDark", "Floor_UnevenBrick", "Floor_RedBrick",
        "Roof_RoundTiles_4x4", "Roof_RoundTiles_4x6", "Roof_RoundTiles_6x6", "Roof_RoundTiles_6x8",
        "Roof_Front_Brick4", "Roof_Front_Brick6", "Door_1_Round", "Door_2_Flat", "WindowShutters_Wide_Round_Open",
        "WindowShutters_Thin_Round_Open", "Prop_Chimney", "Prop_Crate", "Prop_Wagon", "Prop_WoodenFence_Single",
        "Prop_WoodenFence_Extension1", "Prop_Vine1", "Prop_Vine2", "Prop_ExteriorBorder_Straight1",
        "Stairs_Exterior_Straight", "Wall_BottomCover"]),
    "City": (rf"{q.QROOT}\DowntownCityMegaKit", [
        "Building_Large_2", "Building_Medium_2_001", "Building_Small_1", "Street_4WayIntersection",
        "Street_4Lane", "Street_2Lane", "Street_TIntersection", "Street_Asphalt_6x6", "Sidewalk_Straight_3m",
        "Sidewalk_Corner_Round_3m", "Sidewalk_NoCurb_3m", "Sidewalk_Planter", "Prop_Bollard", "Prop_Planter_Single",
        "Prop_ManholeCover", "Prop_ACUnit", "Decal_Crosswalk", "Decal_DoubleYellow_Straight",
        "Entrance_Concrete_2x2", "Stairs_Entrance_Concrete"]),
}

for kit, (src, wanted) in KITS.items():
    files = glob.glob(os.path.join(glob.escape(src), "**", "*.gltf"), recursive=True)
    files = [f for f in files if wanted is None or os.path.splitext(os.path.basename(f))[0] in wanted]
    dest = f"{ENV}/{kit}"
    done = 0
    for i, f in enumerate(sorted(files)):
        name = os.path.splitext(os.path.basename(f))[0]
        if eal.does_asset_exist(f"{dest}/{name}"):
            continue
        q.import_interchange(f, dest)
        done += 1
        if done % 8 == 0:
            unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
            unreal.SystemLibrary.collect_garbage()
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.SystemLibrary.collect_garbage()
    meshes = [p for p in eal.list_assets(dest, recursive=True)
              if str(eal.find_asset_data(p).asset_class_path.asset_name) == "StaticMesh"]
    print(f"KIT {kit}: {len(files)} files, {done} newly imported, {len(meshes)} static meshes in {dest}")

# report sizes (cm) of the pieces the builders rely on
for p in ("Medieval/Wall_Plaster_Straight", "Medieval/Roof_RoundTiles_6x6", "Medieval/Floor_WoodDark",
          "City/Building_Large_2", "City/Street_4WayIntersection", "City/Sidewalk_Straight_3m", "Nature/CommonTree_1"):
    m = eal.load_asset(f"{ENV}/{p}")
    if m:
        bb = m.get_bounding_box()
        print(f"BOUNDS {p:32s} min=({bb.min.x:.0f},{bb.min.y:.0f},{bb.min.z:.0f}) max=({bb.max.x:.0f},{bb.max.y:.0f},{bb.max.z:.0f})")
    else:
        print("missing", p)
