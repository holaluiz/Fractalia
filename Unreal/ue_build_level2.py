"""Rebuild L_Island from the new layout: re-imported island (POI plazas + camp clearings) and Quaternius nature."""
import importlib.util
import json

import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
spec = importlib.util.spec_from_file_location("nx", r"D:\meus documentos\Fortnite\Unreal\import_nexus_assets.py")
nx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nx)

ENV = "/Game/Quaternius/Env"
LAYOUT = r"D:\meus documentos\Fortnite\Export\map_layout.json"
NO_COLLISION = {"grass", "flower", "plant", "mushroom", "fern", "bush", "essence_shard", "potion"}
COMPLEX_COLLISION = {"tree", "tree_landmark", "dead_tree", "rock"}
_cache = {}


def env_mesh(name):
    if name not in _cache:
        hits = [p.split(".")[0] for p in eal.list_assets(ENV, recursive=True)
                if p.split(".")[-1] == name and str(eal.find_asset_data(p).asset_class_path.asset_name) == "StaticMesh"]
        _cache[name] = eal.load_asset(hits[0]) if hits else None
    return _cache[name]


if les.get_current_level().get_outermost().get_name() != "/Game/NexusRoyale/Maps/L_Island":
    les.load_level("/Game/NexusRoyale/Maps/L_Island")

# 1) island with the new plazas/clearings (centimeter FBX -> 1:1 import)
nx.use_legacy_fbx_importer()
nx.import_fbx(r"D:\meus documentos\Fortnite\Export\FBX\Map\SM_Island.fbx", "/Game/NexusRoyale/Map", False)
island = eal.load_asset("/Game/NexusRoyale/Map/SM_Island")
island.set_material(0, nx.vertex_color_material())
island.get_editor_property("body_setup").set_editor_property("collision_trace_flag",
                                                             unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
eal.save_loaded_asset(island)
bb = island.get_bounding_box()
print(f"island size cm: {bb.max.x - bb.min.x:.0f} x {bb.max.y - bb.min.y:.0f} x {bb.max.z - bb.min.z:.0f}")

# 2) clear the previous gameplay scatter (lighting, map, showcase and player start stay)
removed = 0
for a in eas.get_all_level_actors():
    if str(a.get_folder_path()).startswith("Gameplay"):
        eas.destroy_actor(a)
        removed += 1
print("removed old gameplay actors:", removed)

# 3) spawn the new layout
with open(LAYOUT, encoding="utf-8") as f:
    layout = json.load(f)
spawned, missing, prepared = 0, set(), set()
for a in layout["actors"]:
    kind = a["type"]
    if kind in ("poi", "creep_camp", "guardian_spawn"):
        continue
    if a.get("ue_mesh"):
        mesh = env_mesh(a["ue_mesh"])
        if mesh is None:
            missing.add(a["ue_mesh"])
            continue
        if kind in COMPLEX_COLLISION and mesh.get_name() not in prepared:
            mesh.get_editor_property("body_setup").set_editor_property(
                "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            eal.save_loaded_asset(mesh)
            prepared.add(mesh.get_name())
        path = mesh.get_path_name().split(".")[0]
    else:
        path = f"/Game/NexusRoyale/Props/{a['mesh']}"
    actor = nx.spawn_mesh(eas, path, a["ue_location_cm"], a["ue_yaw"], a["scale"], label=a.get("name"),
                          folder=f"Gameplay/{kind}")
    if actor is None:
        missing.add(path)
        continue
    if kind in NO_COLLISION:
        actor.set_actor_enable_collision(False)
    spawned += 1
print("spawned:", spawned, "| missing:", sorted(missing)[:10])
les.save_current_level()
unreal.SystemLibrary.collect_garbage()
