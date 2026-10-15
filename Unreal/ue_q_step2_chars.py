"""Step 2: Universal Base Characters (bodies + rigged hair/eyebrows) on the shared UAL skeleton."""
import glob
import importlib.util
import os

import unreal

spec = importlib.util.spec_from_file_location("q", r"D:\meus documentos\Fortnite\Unreal\ue_q_lib.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
eal = unreal.EditorAssetLibrary
DEST = "/Game/Quaternius/Characters"
SKEL = "/Game/Quaternius/Animations/UAL1/UAL1_Standard/SkeletalMeshes/UAL1_Standard_Skeleton"
UBC = rf"{q.QROOT}\UniversalBaseCharacters\Universal Base Characters[Standard]"

skel = eal.load_asset(SKEL)
files = glob.glob(glob.escape(rf"{UBC}\Base Characters\Godot - UE") + r"\*.gltf") + \
    glob.glob(glob.escape(rf"{UBC}\Hairstyles\Rigged to Head Bone\glTF (Godot -Unreal)") + r"\*.gltf")
print("files:", len(files))
if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)
for f in files:
    name = os.path.splitext(os.path.basename(f))[0]
    res = q.import_interchange(f, f"{DEST}/{name}", skeleton=skel)
    print("imported", name, len(res))

for p in q.assets_in(DEST, "SkeletalMesh"):
    m = eal.load_asset(p)
    s = m.get_editor_property("skeleton")
    b = m.get_bounds()
    mats = [str(x.get_editor_property("material_slot_name")) for x in m.get_editor_property("materials")]
    print(f"MESH {p.split('/')[-1]:28s} skel_shared={s.get_path_name().split('.')[0] == SKEL} "
          f"height={2 * b.box_extent.z:.0f}cm slots={mats}")
print("extra skeletons created:", q.assets_in(DEST, "Skeleton"))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
