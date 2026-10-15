"""Import 3 sample FBX files into /Game/NexusRoyale/_ImportTest and report what came in."""
import os

import unreal

EXPORT = r"D:\meus documentos\Fortnite\Export\FBX"
DEST = "/Game/NexusRoyale/_ImportTest"
eal = unreal.EditorAssetLibrary

for cvar in ("Interchange.FeatureFlags.Import.FBX",):
    try:
        print(cvar, "=", unreal.SystemLibrary.get_console_variable_bool_value(cvar))
    except Exception as e:
        print(cvar, "lookup failed:", e)

import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("nx", r"D:\meus documentos\Fortnite\Unreal\import_nexus_assets.py")
nx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nx)
nx.use_legacy_fbx_importer()
try:
    print("after:", unreal.SystemLibrary.get_console_variable_bool_value("Interchange.FeatureFlags.Import.FBX"))
except Exception as e:
    print("after lookup failed:", e)

for rel, skel in ((r"Heroes\SK_Caramelo.fbx", True), (r"Props\SM_Build_Ramp.fbx", False), (r"Map\SM_Island.fbx", False)):
    paths = nx.import_fbx(os.path.join(EXPORT, rel), DEST, skel)
    print("IMPORTED", rel, "->", paths)

for p in eal.list_assets(DEST, recursive=True):
    a = eal.load_asset(p)
    line = f"  {a.get_class().get_name():20s} {p}"
    if isinstance(a, unreal.SkeletalMesh):
        skel = a.get_editor_property("skeleton")
        bones = skel.get_editor_property("bone_tree") if False else None
        ref = a.get_editor_property("materials")
        line += f" | skeleton={skel.get_path_name() if skel else None} mats={len(ref)}"
        bb = a.get_bounds()
        line += f" | bounds_extent={bb.box_extent}"
    if isinstance(a, unreal.StaticMesh):
        bs = a.get_editor_property("body_setup")
        agg = bs.get_editor_property("agg_geom") if bs else None
        convex = len(agg.get_editor_property("convex_elems")) if agg else -1
        line += f" | convex={convex} slots={len(a.get_editor_property('static_materials'))}"
        line += f" | bounds={a.get_bounding_box().max - a.get_bounding_box().min}"
    print(line)
