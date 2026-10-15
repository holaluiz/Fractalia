"""Unreal Editor Python: imports the Nexus Royale FBX files and builds the island level.

Run inside the Unreal Editor (Python Editor Script Plugin enabled), e.g. through the
unreal-mcp server or `py "D:/meus documentos/Fortnite/Unreal/import_nexus_assets.py"` in the
editor console. Safe to re-run: assets are replaced, the level is rebuilt.

NOT YET TESTED against a live editor (Unreal was not installed when this was written).
"""
import json
import os

import unreal

EXPORT = r"D:\meus documentos\Fortnite\Export"
DEST = "/Game/NexusRoyale"
LEVEL = f"{DEST}/Maps/L_Island"

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary


def log(msg):
    unreal.log(f"[NexusRoyale] {msg}")


def use_legacy_fbx_importer():
    # Recent engine versions route FBX through Interchange, which ignores FbxImportUI options.
    unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")


def import_fbx(path, dest, skeletal, static_scale=1.0):
    """Centimeter FBX from Blender imports 1:1. NOTE: replacing an existing asset reuses that asset's stored import
    settings (e.g. an old x100), so re-import into a fresh path and consolidate instead (see ue_fix_island.py)."""
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = dest
    task.automated = True
    task.replace_existing = True
    task.save = True
    ui = unreal.FbxImportUI()
    ui.import_materials = True
    ui.import_textures = skeletal  # Personagens heroes carry an embedded 4K basecolor map
    ui.import_animations = False
    ui.create_physics_asset = skeletal
    # Blender exports centimeters with unscaled bones (export_fbx.to_centimeters): import 1:1
    if skeletal:
        ui.import_as_skeletal = True
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
        ui.skeletal_mesh_import_data.set_editor_property("import_morph_targets", False)
        ui.skeletal_mesh_import_data.set_editor_property("import_uniform_scale", 1.0)
    else:
        ui.import_as_skeletal = False
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
        sm = ui.static_mesh_import_data
        sm.set_editor_property("import_uniform_scale", static_scale)
        sm.set_editor_property("combine_meshes", True)
        sm.set_editor_property("auto_generate_collision", False)  # UCX_ shapes come from Blender
        sm.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
        sm.set_editor_property("generate_lightmap_u_vs", True)
    task.options = ui
    asset_tools.import_asset_tasks([task])
    return list(task.imported_object_paths)


def vertex_color_material():
    path = f"{DEST}/Materials/M_VertexColor"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    m = asset_tools.create_asset("M_VertexColor", f"{DEST}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    vc = mel.create_material_expression(m, unreal.MaterialExpressionVertexColor, -400, 0)
    rough = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", 0.9)
    mel.connect_material_property(vc, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def water_material():
    path = f"{DEST}/Materials/M_Water"
    if eal.does_asset_exist(path):
        return eal.load_asset(path)
    m = asset_tools.create_asset("M_Water", f"{DEST}/Materials", unreal.Material, unreal.MaterialFactoryNew())
    col = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 0)
    col.set_editor_property("constant", unreal.LinearColor(0.03, 0.28, 0.67, 1.0))
    rough = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", 0.05)
    mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m)
    return m


def import_all():
    use_legacy_fbx_importer()
    imported = {}
    for sub, skeletal in (("Heroes", True), ("Props", False), ("Map", False)):
        folder = os.path.join(EXPORT, "FBX", sub)
        for fn in sorted(os.listdir(folder)):
            if fn.lower().endswith(".fbx"):
                paths = import_fbx(os.path.join(folder, fn), f"{DEST}/{sub}", skeletal)
                imported[fn[:-4]] = paths
                log(f"imported {fn}: {paths}")
    island = eal.load_asset(f"{DEST}/Map/SM_Island")
    if island:
        island.set_material(0, vertex_color_material())
        # walkable terrain: use the render triangles as the collision
        bs = island.get_editor_property("body_setup")
        bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        eal.save_loaded_asset(island)
    return imported


def spawn_mesh(eas, asset_path, loc_cm, yaw=0.0, scale=1.0, label=None, folder=None):
    asset = eal.load_asset(asset_path)
    if asset is None:
        log(f"missing asset {asset_path}")
        return None
    actor = eas.spawn_actor_from_object(asset, unreal.Vector(*loc_cm), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    if actor:
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        if label:
            actor.set_actor_label(label)
        if folder:
            actor.set_folder_path(folder)
    return actor


def build_level():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if eal.does_asset_exist(LEVEL):
        les.load_level(LEVEL)
        for a in eas.get_all_level_actors():
            eas.destroy_actor(a)
    else:
        les.new_level(LEVEL)
    with open(os.path.join(EXPORT, "map_layout.json"), encoding="utf-8") as f:
        layout = json.load(f)

    spawn_mesh(eas, f"{DEST}/Map/SM_Island", (0, 0, 0), label="Island", folder="Map")
    water = spawn_mesh(eas, "/Engine/BasicShapes/Plane", (0, 0, -15), scale=1400.0, label="Water", folder="Map")
    if water:
        water.static_mesh_component.set_material(0, water_material())
    for a in layout["actors"]:
        kind, mesh = a["type"], a["mesh"]
        sub = "Heroes" if mesh.startswith("SK_") else "Props"
        actor = spawn_mesh(eas, f"{DEST}/{sub}/{mesh}", a["ue_location_cm"], a["ue_yaw"], a["scale"],
                           label=a.get("name"), folder=f"Gameplay/{kind}")
        if actor and kind == "bush":
            actor.set_actor_enable_collision(False)

    for cls, loc, rot, label in (
            (unreal.DirectionalLight, (0, 0, 20000), (0.0, -48.0, 35.0), "Sun"),
            (unreal.SkyLight, (0, 0, 15000), (0, 0, 0), "SkyLight"),
            (unreal.SkyAtmosphere, (0, 0, 0), (0, 0, 0), "SkyAtmosphere"),
            (unreal.ExponentialHeightFog, (0, 0, 0), (0, 0, 0), "Fog"),
            (unreal.PlayerStart, (0, -1800, 1000), (0, 0, 90), "PlayerStart")):
        act = eas.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2]))
        act.set_actor_label(label)
        act.set_folder_path("Lighting" if cls is not unreal.PlayerStart else "Gameplay")
    sun = next((x for x in eas.get_all_level_actors() if x.get_actor_label() == "Sun"), None)
    if sun:
        sun.light_component.set_editor_property("atmosphere_sun_light", True)
    sky = next((x for x in eas.get_all_level_actors() if x.get_actor_label() == "SkyLight"), None)
    if sky:
        sky.light_component.set_editor_property("real_time_capture", True)
    les.save_current_level()
    log(f"level built with {len(layout['actors'])} gameplay actors")


if __name__ == "__main__":
    import_all()
    build_level()
