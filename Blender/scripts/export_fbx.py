"""Export every asset collection to its own FBX, ready for Unreal.

Unreal wants centimeters with unscaled bones, so export runs on a centimeter copy of the scene
(to_centimeters: unit scale 0.01, every mesh/armature/location x100). Import in Unreal at scale 1.0.
"""
import os

import bpy
from mathutils import Matrix, Vector

CM = 100.0  # applied by to_centimeters(); layout offsets stored on collections are in meters

FBX_COMMON = dict(
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_NONE",
    axis_forward="-Z",
    axis_up="Y",
    use_mesh_modifiers=True,
    mesh_smooth_type="FACE",
    use_tspace=False,
    add_leaf_bones=False,
    primary_bone_axis="Y",
    secondary_bone_axis="X",
    armature_nodetype="NULL",
    bake_anim=False,
    path_mode="AUTO",
)


def to_centimeters():
    """Rescale the whole scene so 1 BU = 1 cm (do NOT save afterwards: the .blend stays in meters)."""
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    S = Matrix.Diagonal((CM, CM, CM, 1.0))
    for me in bpy.data.meshes:
        me.transform(S)
    for arm in bpy.data.armatures:
        arm.transform(S)
    for ob in bpy.data.objects:
        ob.location = ob.location * CM
    bpy.context.scene.unit_settings.scale_length = 1.0 / CM
    bpy.context.view_layer.update()


def _select_only(objs):
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.hide_set(False)
        o.select_set(True)
    vl.objects.active = objs[0]


def _ensure_included(coll):
    def walk(lc):
        if lc.collection == coll:
            return lc
        for ch in lc.children:
            r = walk(ch)
            if r:
                return r
        return None
    lc = walk(bpy.context.view_layer.layer_collection)
    if lc:
        lc.exclude = False
        lc.hide_viewport = False
        # parents too
        for parent in bpy.data.collections:
            if coll.name in parent.children:
                _ensure_included(parent)


def export_hero(name, out_dir):
    arm = bpy.data.objects[f"SKEL_{name}"]
    mesh = bpy.data.objects[f"SK_{name}"]
    _ensure_included(arm.users_collection[0])
    old_loc, old_name = arm.location.copy(), arm.name
    arm.location = (0, 0, 0)
    arm.name = "Armature"  # UE skips an armature node named "Armature" -> 'root' stays the root bone
    try:
        _select_only([arm, mesh])
        path = os.path.join(out_dir, f"SK_{name}.fbx")
        # embed image textures (the Personagens heroes use a 4K basecolor map)
        opts = dict(FBX_COMMON, path_mode="COPY", embed_textures=True)
        bpy.ops.export_scene.fbx(filepath=path, object_types={"ARMATURE", "MESH"}, **opts)
    finally:
        arm.name = old_name
        arm.location = old_loc
    return path


def export_static(coll, out_dir):
    _ensure_included(coll)
    off = Vector(coll.get("layout_offset", (0, 0, 0))) * CM
    objs = [o for o in coll.objects if o.type == "MESH" and o.parent is None]
    main = next(o for o in objs if not o.name.startswith("UCX_"))
    saved = [(o, o.location.copy()) for o in objs]
    for o in objs:
        o.location = o.location - off
    try:
        _select_only([main] + [o for o in objs if o is not main])
        path = os.path.join(out_dir, f"{main.name}.fbx")
        bpy.ops.export_scene.fbx(filepath=path, object_types={"MESH"}, colors_type="SRGB", **FBX_COMMON)
    finally:
        for o, loc in saved:
            o.location = loc
    return path


def export_all(root_dir, heroes):
    hero_dir = os.path.join(root_dir, "Heroes")
    prop_dir = os.path.join(root_dir, "Props")
    map_dir = os.path.join(root_dir, "Map")
    for d in (hero_dir, prop_dir, map_dir):
        os.makedirs(d, exist_ok=True)
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    out = []
    for name in heroes:
        out.append(export_hero(name, hero_dir))
    for coll in bpy.data.collections:
        if not coll.name.startswith("Prop_"):
            continue
        target = map_dir if coll.name == "Prop_SM_Island" else prop_dir
        out.append(export_static(coll, target))
    return out
