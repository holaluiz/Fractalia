import bpy

ob = bpy.data.objects["SM_Island"]
zs = [v.co.z for v in ob.data.vertices]
lc = None


def walk(l):
    global lc
    if l.collection.name == "Prop_SM_Island":
        lc = l
    for c in l.children:
        walk(c)


walk(bpy.context.view_layer.layer_collection)
print("ISLAND", tuple(ob.location), tuple(round(d, 1) for d in ob.dimensions), "zmin", round(min(zs), 2), "zmax",
      round(max(zs), 2), "above0", sum(1 for z in zs if z > 0), "/", len(zs))
print("VIS hide_render", ob.hide_render, "hide_viewport", ob.hide_viewport, "excluded", lc.exclude if lc else None,
      "coll_hide_render", bpy.data.collections["Prop_SM_Island"].hide_render)
print("MATS", [m.name for m in ob.data.materials], "colattrs", [a.name for a in ob.data.color_attributes])
scat = [o for o in bpy.data.objects if o.name.startswith("MAP_")]
print("SCATTER", len(scat), scat[0].matrix_world.translation if scat else None)
