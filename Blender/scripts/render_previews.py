"""Preview renders (EEVEE) of the generated assets."""
import math

import bpy
from mathutils import Vector


def setup_render(res=(1600, 900), samples=32):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    try:
        sc.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    world = bpy.data.worlds.get("W_Preview") or bpy.data.worlds.new("W_Preview")
    sc.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg is None:
        bg = world.node_tree.nodes.new("ShaderNodeBackground")
        out = next((n for n in world.node_tree.nodes if n.type == "OUTPUT_WORLD"), None) or \
            world.node_tree.nodes.new("ShaderNodeOutputWorld")
        world.node_tree.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs[0].default_value = (0.38, 0.62, 0.95, 1.0)
    bg.inputs[1].default_value = 0.9


def preview_collection():
    c = bpy.data.collections.get("_Preview")
    if c is None:
        c = bpy.data.collections.new("_Preview")
        bpy.context.scene.collection.children.link(c)
    return c


def add_light(name, kind, loc, rot, energy, size=1.0, color=(1, 1, 1)):
    c = preview_collection()
    ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "SUN":
        ld.angle = math.radians(3)
    elif kind == "AREA":
        ld.size = size
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, ld)
    if ob.name not in c.objects:
        c.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob


def add_camera(loc, target, lens=35.0, ortho=None):
    c = preview_collection()
    cd = bpy.data.cameras.get("CAM_Preview") or bpy.data.cameras.new("CAM_Preview")
    cd.lens = lens
    cd.clip_end = 5000
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
    else:
        cd.type = "PERSP"
    ob = bpy.data.objects.get("CAM_Preview") or bpy.data.objects.new("CAM_Preview", cd)
    if ob.name not in c.objects:
        c.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    return ob


def ground(size=60, color=(0.25, 0.5, 0.18)):
    c = preview_collection()
    me = bpy.data.meshes.get("PRV_Ground")
    if me is None:
        me = bpy.data.meshes.new("PRV_Ground")
        h = size / 2
        me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
        m = bpy.data.materials.new("PRV_GroundMat")
        m.diffuse_color = (*color, 1)
        try:
            m.use_nodes = True
        except Exception:
            pass
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1)
            bsdf.inputs["Roughness"].default_value = 0.9
        me.materials.append(m)
    ob = bpy.data.objects.get("PRV_Ground") or bpy.data.objects.new("PRV_Ground", me)
    if ob.name not in c.objects:
        c.objects.link(ob)
    return ob


def only_visible(collection_names):
    """Hide every top-level collection except the listed ones (+ _Preview)."""
    keep = set(collection_names) | {"_Preview"}

    def include_all(lc):
        lc.exclude = False
        for ch in lc.children:
            include_all(ch)

    for lc in bpy.context.view_layer.layer_collection.children:
        if lc.name in keep:
            include_all(lc)
        elif not lc.exclude:
            lc.exclude = True


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def standard_lights(center=(0, 0, 0), scale=1.0):
    cx, cy, cz = center
    add_light("PRV_Sun", "SUN", (cx, cy, cz + 10), (50, 10, 35), 3.5)
    add_light("PRV_Fill", "AREA", (cx - 6 * scale, cy - 8 * scale, cz + 4 * scale), (65, 0, -35), 600 * scale * scale,
              size=8 * scale, color=(0.85, 0.9, 1.0))
    add_light("PRV_Rim", "AREA", (cx + 4 * scale, cy + 7 * scale, cz + 5 * scale), (-60, 0, 150), 500 * scale * scale,
              size=6 * scale, color=(1.0, 0.92, 0.8))
