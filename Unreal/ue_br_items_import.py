"""Import the Ultimate RPG / Ultimate Food meshes the GDD uses for items, grimoires and consumables (static meshes)."""
import importlib.util
import os

import unreal

eal = unreal.EditorAssetLibrary
spec = importlib.util.spec_from_file_location("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

QROOT = r"D:\meus documentos\Fortnite\Quaternius"
DEST = "/Game/Quaternius/Items"
WANTED = {
    "UltimateRPG": ["Armor_Leather", "Armor_Metal", "Armor_Black", "Crown", "Crown2", "Glove", "Ring1", "Ring2", "Ring3",
                    "Ring4", "Necklace1", "Necklace2", "Necklace3", "Heart", "Book1_Closed", "Book2_Closed",
                    "Book3_Closed", "Book4_Closed", "Potion5_Filled", "Potion9_Filled", "Chest_Open"],
    "UltimateFood": ["Apple", "Bread", "Banana", "Burger", "Pizza", "CookingPot_Soup"],
}


def static_mesh_in(folder):
    for p in eal.list_assets(folder, recursive=True):
        if str(eal.find_asset_data(p).asset_class_path.asset_name) == "StaticMesh":
            return eal.load_asset(p.split(".")[0])
    return None


done = 0
for pack, names in WANTED.items():
    for name in names:
        dest = f"{DEST}/{name}"
        if eal.does_directory_exist(dest) and static_mesh_in(dest):
            continue
        q.import_interchange(os.path.join(QROOT, pack, "FBX", f"{name}.fbx"), dest)
        done += 1
        if done % 6 == 0:
            unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
            unreal.SystemLibrary.collect_garbage()
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.SystemLibrary.collect_garbage()

for names in WANTED.values():
    for name in names:
        sm = static_mesh_in(f"{DEST}/{name}")
        if sm is None:
            print(f"{name}: MISSING")
            continue
        b = sm.get_bounds()
        print(f"{name}: {sm.get_path_name()} extent={b.box_extent}")
print("imported now:", done)
