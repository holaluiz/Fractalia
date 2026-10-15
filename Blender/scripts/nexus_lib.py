"""Procedural modeling helpers for Nexus Royale assets (Blender 5.x, runs headless)."""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector


# ---------------------------------------------------------------- materials

def srgb(hexstr):
    """'#RRGGBB' -> linear RGB tuple."""
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def mat(name, hexcolor, rough=0.6, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        nt.nodes.clear()
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    col = srgb(hexcolor)
    bsdf.inputs["Base Color"].default_value = (*col, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*srgb(emit), 1.0)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    m.diffuse_color = (*col, 1.0)
    return m


# ---------------------------------------------------------------- collections

def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


# ---------------------------------------------------------------- matrices

def frame(origin, direction, ref=Vector((0, -1, 0))):
    """4x4 matrix whose local +Z points along `direction`, placed at `origin`."""
    z = Vector(direction).normalized()
    x = Vector(ref).cross(z)
    if x.length < 1e-6:
        x = Vector((1, 0, 0)).cross(z)
        if x.length < 1e-6:
            x = Vector((0, 1, 0)).cross(z)
    x.normalize()
    y = z.cross(x)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(origin)
    return m


def trs(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    """Location / Euler degrees / scale -> matrix."""
    from mathutils import Euler
    r = Euler([math.radians(a) for a in rot], "XYZ").to_matrix().to_4x4()
    s = Matrix.Diagonal((*scale, 1.0))
    t = Matrix.Translation(loc)
    return t @ r @ s


# ---------------------------------------------------------------- primitive bmeshes (local space)

def bm_sphere(segs=16, rings=10):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=1.0)
    return bm


def bm_ico(subdiv=2):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    return bm


def bm_cube(bevel=0.0, bevel_segs=2):
    """Unit cube centered at origin (size 1). Bevel is applied later, after scaling."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    return bm


def bm_cone(r1, r2, depth, segs=16, cap=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs,
                          radius1=r1, radius2=r2, depth=depth)
    return bm


def bm_lathe(profile, segs=16, sx=1.0, sy=1.0, cap=True):
    """Revolve a (z, r) profile around local Z. r<=0 makes a pole."""
    bm = bmesh.new()
    rings = []
    for z, r in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * sx * math.cos(2 * math.pi * i / segs),
                                        r * sy * math.sin(2 * math.pi * i / segs), z))
                          for i in range(segs)])
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        for i in range(segs):
            j = (i + 1) % segs
            if len(a) == 1:
                bm.faces.new((a[0], b[i], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap:
        if len(rings[0]) > 1:
            bm.faces.new(list(reversed(rings[0])))
        if len(rings[-1]) > 1:
            bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def capsule_profile(length, r1, r2, ncap=4, nmid=3):
    prof = []
    for i in range(ncap + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / ncap
        prof.append((r1 + r1 * math.sin(a), r1 * math.cos(a)))
    for i in range(1, nmid):
        t = i / nmid
        prof.append((r1 + t * (length - r1 - r2), r1 + t * (r2 - r1)))
    for i in range(ncap + 1):
        a = (math.pi / 2) * i / ncap
        prof.append((length - r2 + r2 * math.sin(a), r2 * math.cos(a)))
    # remove duplicate poles / zero-length steps
    clean = []
    for z, r in prof:
        if clean and abs(clean[-1][0] - z) < 1e-6 and abs(clean[-1][1] - r) < 1e-6:
            continue
        clean.append((z, max(r, 0.0) if abs(r) > 1e-6 else 0.0))
    return clean


def bm_tube(points, radius, segs=10, closed=False, cap=True):
    """Sweep a circle along a polyline (parallel transport frames)."""
    pts = [Vector(p) for p in points]
    n = len(pts)
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * n
    tangents = []
    for i in range(n):
        if closed:
            t = pts[(i + 1) % n] - pts[i - 1]
        else:
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        tangents.append(t.normalized())
    ref = Vector((0, 0, 1)) if abs(tangents[0].z) < 0.9 else Vector((1, 0, 0))
    normal = (ref - tangents[0] * ref.dot(tangents[0])).normalized()
    bm = bmesh.new()
    rings = []
    for i in range(n):
        t = tangents[i]
        normal = (normal - t * normal.dot(t)).normalized()
        binorm = t.cross(normal)
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            ring.append(bm.verts.new(pts[i] + radii[i] * (math.cos(a) * normal + math.sin(a) * binorm)))
        rings.append(ring)
    pairs = list(zip(rings[:-1], rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    for a, b in pairs:
        for k in range(segs):
            j = (k + 1) % segs
            bm.faces.new((a[k], a[j], b[j], b[k]))
    if cap and not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_torus(R, r, segs=32, rsegs=10):
    pts = [(R * math.cos(2 * math.pi * i / segs), R * math.sin(2 * math.pi * i / segs), 0.0) for i in range(segs)]
    return bm_tube(pts, r, segs=rsegs, closed=True)


def bm_grid(nx, ny, sx, sy):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=0.5)
    for v in bm.verts:
        v.co.x *= sx
        v.co.y *= sy
    return bm


def bm_convex(points):
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    # convex_hull may leave interior verts; remove loose ones
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def roughen(bm, amount, seed=0, scale=1.0):
    rnd = random.Random(seed)
    for v in bm.verts:
        d = v.co.normalized() if v.co.length > 1e-6 else Vector((0, 0, 1))
        v.co += d * (rnd.uniform(-1, 1) * amount * scale)


def bevel(bm, offset, segs=2):
    bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=offset, offset_type="OFFSET",
                    segments=segs, profile=0.5, affect="EDGES", clamp_overlap=True)


# ---------------------------------------------------------------- objects

def _box_uv(bm, scale=1.0):
    uv = bm.loops.layers.uv.verify()
    bm.normal_update()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            c = loop.vert.co
            if ax == 0:
                loop[uv].uv = (c.y * scale, c.z * scale)
            elif ax == 1:
                loop[uv].uv = (c.x * scale, c.z * scale)
            else:
                loop[uv].uv = (c.x * scale, c.y * scale)


def make_obj(name, bm, material, coll, matrix=None, smooth=True, bone=None, uv=True):
    if matrix is not None:
        bm.transform(matrix)
    if uv:
        _box_uv(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    obj = bpy.data.objects.new(name, me)
    coll.objects.link(obj)
    if material is not None:
        me.materials.append(material)
    if bone:
        vg = obj.vertex_groups.new(name=bone)
        vg.add(list(range(len(me.vertices))), 1.0, "REPLACE")
    return obj


def join(objs, name):
    objs = [o for o in objs if o is not None]
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0]
    with bpy.context.temp_override(active_object=objs[0], object=objs[0],
                                   selected_objects=objs, selected_editable_objects=objs):
        bpy.ops.object.join()
    res = objs[0]
    res.name = name
    res.data.name = name
    return res


class Kit:
    """Collects parts for one asset, then joins them."""

    def __init__(self, name, coll):
        self.name = name
        self.coll = coll
        self.parts = []
        self.i = 0

    def _add(self, bm, material, matrix=None, smooth=True, bone=None):
        self.i += 1
        o = make_obj(f"{self.name}_p{self.i:03d}", bm, material, self.coll, matrix, smooth, bone)
        self.parts.append(o)
        return o

    # -- convenience shapes, all in world space
    def ellipsoid(self, center, radii, material, bone=None, rot=None, segs=16, rings=10, smooth=True):
        m = Matrix.Translation(center) @ (rot or Matrix.Identity(4)) @ Matrix.Diagonal((*radii, 1.0))
        return self._add(bm_sphere(segs, rings), material, m, smooth, bone)

    def capsule(self, p1, p2, r1, r2, material, bone=None, ext=0.0, segs=14, sx=1.0, sy=1.0, ref=(0, -1, 0)):
        p1, p2 = Vector(p1), Vector(p2)
        d = (p2 - p1)
        L = d.length + 2 * ext
        d.normalize()
        bm = bm_lathe(capsule_profile(L, r1, r2), segs, sx, sy)
        return self._add(bm, material, frame(p1 - d * ext, d, Vector(ref)), True, bone)

    def lathe(self, profile, origin, direction, material, bone=None, segs=16, sx=1.0, sy=1.0,
              smooth=True, cap=True, ref=(0, -1, 0)):
        bm = bm_lathe(profile, segs, sx, sy, cap)
        return self._add(bm, material, frame(origin, direction, Vector(ref)), smooth, bone)

    def box(self, center, size, material, bone=None, rot=(0, 0, 0), bevel_w=0.0, bevel_segs=2, smooth=False):
        bm = bm_cube()
        for v in bm.verts:
            v.co.x *= size[0]
            v.co.y *= size[1]
            v.co.z *= size[2]
        if bevel_w > 0:
            bevel(bm, bevel_w, bevel_segs)
        return self._add(bm, material, trs(center, rot), smooth, bone)

    def cyl(self, p1, p2, r1, r2, material, bone=None, segs=16, smooth=True, ref=(0, -1, 0)):
        p1, p2 = Vector(p1), Vector(p2)
        d = p2 - p1
        bm = bm_cone(r1, r2, d.length, segs)
        m = frame((p1 + p2) / 2, d, Vector(ref))
        return self._add(bm, material, m, smooth, bone)

    def tube(self, points, radius, material, bone=None, segs=10, closed=False, smooth=True):
        return self._add(bm_tube(points, radius, segs, closed), material, None, smooth, bone)

    def torus(self, center, R, r, material, bone=None, rot=(0, 0, 0), segs=32, rsegs=10, scale=(1, 1, 1)):
        return self._add(bm_torus(R, r, segs, rsegs), material, trs(center, rot, scale), True, bone)

    def rock(self, center, radii, material, bone=None, seed=0, rough=0.18, subdiv=2, rot=(0, 0, 0)):
        bm = bm_ico(subdiv)
        roughen(bm, rough, seed)
        m = trs(center, rot) @ Matrix.Diagonal((*radii, 1.0))
        return self._add(bm, material, m, False, bone)

    def crystal(self, center, radius, height, material, bone=None, sides=6, rot=(0, 0, 0), base=0.3):
        prof = [(-height * base, 0.0), (0.0, radius), (height * (1 - base) * 0.35, radius * 0.9),
                (height * (1 - base), 0.0)]
        bm = bm_lathe(prof, sides)
        return self._add(bm, material, trs(center, rot), False, bone)

    def convex(self, points, material, bone=None, smooth=False):
        return self._add(bm_convex(points), material, None, smooth, bone)

    def raw(self, bm, material, matrix=None, smooth=True, bone=None):
        return self._add(bm, material, matrix, smooth, bone)

    def finish(self, name=None):
        return join(self.parts, name or self.name)


def set_origin_world(obj, point=(0, 0, 0)):
    """Keep the geometry where it is but put the object origin at `point` (world)."""
    p = Vector(point)
    obj.data.transform(Matrix.Translation(obj.location - p))
    obj.location = p
