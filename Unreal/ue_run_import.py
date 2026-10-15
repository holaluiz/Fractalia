"""Clean the test folder, import every FBX and build L_Island; print a short report."""
import importlib.util

import unreal

eal = unreal.EditorAssetLibrary
if eal.does_directory_exist("/Game/NexusRoyale/_ImportTest"):
    eal.delete_directory("/Game/NexusRoyale/_ImportTest")

spec = importlib.util.spec_from_file_location("nx", r"D:\meus documentos\Fortnite\Unreal\import_nexus_assets.py")
nx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nx)

nx.import_all()
nx.build_level()

for sub in ("Heroes", "Props", "Map"):
    assets = eal.list_assets(f"/Game/NexusRoyale/{sub}", recursive=False)
    meshes = [a for a in assets if a.split("/")[-1].startswith(("SK_", "SM_")) and "Skeleton" not in a
              and "PhysicsAsset" not in a]
    print(f"{sub}: {len(assets)} assets, {len(meshes)} meshes")
for p in ("/Game/NexusRoyale/Heroes/SK_Caramelo", "/Game/NexusRoyale/Props/SM_Build_Wall", "/Game/NexusRoyale/Map/SM_Island"):
    a = eal.load_asset(p)
    b = a.get_bounds() if isinstance(a, unreal.SkeletalMesh) else None
    if b:
        print(p, "extent(cm)=", b.box_extent)
    else:
        bb = a.get_bounding_box()
        print(p, "size(cm)=", bb.max - bb.min)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print("level actors:", len(eas.get_all_level_actors()))
