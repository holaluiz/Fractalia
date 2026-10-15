"""Build the two points of interest on the island from the Quaternius modular kits.

Vila (Medieval Village MegaKit): 6 one-storey houses on a ring around a cobbled plaza.
Cidade (Downtown City MegaKit): 4-way intersection with street arms and the 3 pre-made buildings on the corners.
Kit orientation in Unreal (measured): walls span X, thickness in Y (outer face +Y), height Z; roofs X=width,
Y=depth (ridge along Y); city buildings have their facade on +Y with the body towards -Y.
"""
import json
import math

import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LAYOUT = r"D:\meus documentos\Fortnite\Export\map_layout.json"
_meshes = {}
_collision_done = set()


def mesh(kit, name):
    key = (kit, name)
    if key not in _meshes:
        nested = f"/Game/Quaternius/Env/{kit}/{name}/StaticMeshes/{name}"  # default Interchange layout
        flat = f"/Game/Quaternius/Env/{kit}/{name}"  # custom pipeline layout (e.g. city without vertex colors)
        _meshes[key] = eal.load_asset(nested if eal.does_asset_exist(nested) else flat)
        m = _meshes[key]
        if m is not None and name not in _collision_done:  # walkable/collidable: use the render triangles
            m.get_editor_property("body_setup").set_editor_property(
                "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            eal.save_loaded_asset(m)
            _collision_done.add(name)
    return _meshes[key]


def rot2(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def place(kit, name, loc, yaw, folder, scale=1.0):
    m = mesh(kit, name)
    if m is None:
        print("  missing", kit, name)
        return None
    a = eas.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    a.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    a.set_folder_path(folder)
    return a


def clear(folder):
    for a in eas.get_all_level_actors():
        if str(a.get_folder_path()).startswith(folder):
            eas.destroy_actor(a)


# ------------------------------------------------------------------ village
STYLES = {
    "plaster": dict(straight="Wall_Plaster_Straight", door="Wall_Plaster_Door_Round",
                    window="Wall_Plaster_Window_Wide_Round", window2="Wall_Plaster_Window_Thin_Round",
                    deco="Wall_Plaster_WoodGrid", corner="Corner_Exterior_Wood",
                    shutter="WindowShutters_Wide_Round_Open", shutter2="WindowShutters_Thin_Round_Open"),
    "brick": dict(straight="Wall_UnevenBrick_Straight", door="Wall_UnevenBrick_Door_Flat",
                  window="Wall_UnevenBrick_Window_Wide_Flat", window2="Wall_UnevenBrick_Window_Wide_Flat",
                  deco="Wall_UnevenBrick_Straight", corner="Corner_Exterior_Brick", shutter=None, shutter2=None),
}


def house(cx, cy, cz, yaw, W, D, style, folder):
    """W x D meters (multiples of 2), front (door) on local -Y."""
    s = STYLES[style]
    hw, hd = W * 50.0, D * 50.0

    def put(name, lx, ly, lz, lyaw):
        wx, wy = rot2(lx, ly, yaw)
        return place("Medieval", name, (cx + wx, cy + wy, cz + lz), yaw + lyaw, folder)

    sides = [  # (start, step, fixed, axis, local yaw, kind)
        ("front", -hw, hd, "x", 180.0), ("back", -hw, hd, "x", 0.0),
        ("right", -hd, hw, "y", -90.0), ("left", -hd, hw, "y", 90.0)]
    for side, start, half_other, axis, lyaw in sides:
        n = int((W if axis == "x" else D) / 2)
        for i in range(n):
            along = start + 100.0 + 200.0 * i
            if side == "front":
                pos = (along, -hd)
                kind = "door" if i == n // 2 else "window"
            elif side == "back":
                pos = (along, hd)
                kind = "window2" if i % 2 == 0 else "straight"
            elif side == "right":
                pos = (hw, along)
                kind = "deco" if i % 2 == 0 else "window2"
            else:
                pos = (-hw, along)
                kind = "window" if i % 2 == 1 else "deco"
            put(s[kind], pos[0], pos[1], 0.0, lyaw)
            if kind == "window" and s["shutter"]:
                put(s["shutter"], pos[0], pos[1], 0.0, lyaw)
            if kind == "window2" and s["shutter2"]:
                put(s["shutter2"], pos[0], pos[1], 0.0, lyaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            put(s["corner"], sx * hw, sy * hd, 0.0, 0.0)
    for i in range(int(W / 2)):
        for j in range(int(D / 2)):
            put("Floor_WoodDark", -hw + 100 + 200 * i, -hd + 100 + 200 * j, 2.0, 0.0)
    put(f"Roof_RoundTiles_{W}x{D}", 0.0, 0.0, 312.0, 0.0)
    put(f"Roof_Front_Brick{W}", 0.0, -hd, 312.0, 180.0)
    put(f"Roof_Front_Brick{W}", 0.0, hd, 312.0, 0.0)


def build_village(c):
    folder = "POI/Vila"
    clear(folder)
    cx, cy, cz = c
    for i in range(-2, 3):  # 10 x 10 m cobbled plaza
        for j in range(-2, 3):
            place("Medieval", "Floor_UnevenBrick", (cx + i * 200, cy + j * 200, cz + 3), 0.0, folder)
    houses = [(4, 4, 30, "plaster"), (6, 6, 90, "brick"), (4, 6, 150, "plaster"),
              (6, 8, 210, "brick"), (4, 4, 270, "plaster"), (6, 6, 330, "plaster")]
    for k, (W, D, theta, style) in enumerate(houses):
        r = 1150.0 + D * 50.0
        hx, hy = cx + r * math.cos(math.radians(theta)), cy + r * math.sin(math.radians(theta))
        house(hx, hy, cz, theta - 90.0, W, D, style, f"{folder}/Casa_{k + 1}")
    place("Medieval", "Prop_Wagon", (cx + 250, cy - 120, cz + 3), 35.0, folder)
    for k, (dx, dy) in enumerate(((-300, 250), (-340, 300), (320, 300), (-150, -380))):
        place("Medieval", "Prop_Crate", (cx + dx, cy + dy, cz + 3), 20.0 * k, folder)
    for k in range(4):  # fence pieces closing two gaps of the ring
        a = math.radians(0 + 180 * (k // 2)) + (k % 2) * 0.12
        place("Medieval", "Prop_WoodenFence_Single", (cx + 1700 * math.cos(a), cy + 1700 * math.sin(a), cz),
              math.degrees(a) + 90, folder)
    print("village built at", c)


# ------------------------------------------------------------------ downtown
def build_city(c):
    folder = "POI/Cidade"
    clear(folder)
    cx, cy, cz = c
    z = cz + 3.0
    place("City", "Street_4WayIntersection", (cx, cy, z), 0.0, folder)
    for k in range(3):  # street arms, 6 m pieces
        d = 1233.0 + 300.0 + 600.0 * k
        place("City", "Street_4Lane", (cx + d, cy, z), 0.0, folder)
        place("City", "Street_4Lane", (cx - d, cy, z), 0.0, folder)
        place("City", "Street_4Lane", (cx, cy + d, z), 90.0, folder)
        place("City", "Street_4Lane", (cx, cy - d, z), 90.0, folder)
    lots = [(1, 1, "Building_Large_2"), (-1, 1, "Building_Medium_2_001"),
            (-1, -1, "Building_Small_1"), (1, -1, "Building_Medium_2_001")]
    for sx, sy, name in lots:
        m = mesh("City", name)
        yaw = 180.0 if sy > 0 else 0.0  # facade (+Y) towards the east-west street
        bb = m.get_bounding_box()
        xs, ys = [], []
        for px in (bb.min.x, bb.max.x):
            for py in (bb.min.y, bb.max.y):
                rx, ry = rot2(px, py, yaw)
                xs.append(rx)
                ys.append(ry)
        ox = (950.0 - min(xs)) if sx > 0 else (-950.0 - max(xs))
        oy = (950.0 - min(ys)) if sy > 0 else (-950.0 - max(ys))
        place("City", name, (cx + ox, cy + oy, cz), yaw, folder)
    for sx in (-1, 1):  # bollards and planters on the corners, manholes on the crossing
        for sy in (-1, 1):
            for t in (0, 1, 2):
                place("City", "Prop_Bollard", (cx + sx * (1300 + 150 * t), cy + sy * 1000, z), 0.0, folder)
            place("City", "Prop_Planter_Single", (cx + sx * 1000, cy + sy * 1700, z), 0.0, folder)
    for dx, dy in ((300, 300), (-400, -200)):
        place("City", "Prop_ManholeCover", (cx + dx, cy + dy, z + 1), 0.0, folder)
    print("city built at", c)


def poi_centers():
    with open(LAYOUT, encoding="utf-8") as f:
        return {a["name"]: a["ue_location_cm"] for a in json.load(f)["actors"] if a["type"] == "poi"}


def main(which=("Vila", "Cidade")):
    pois = poi_centers()
    if "Vila" in which:
        build_village(pois["Vila"])
    if "Cidade" in which:
        build_city(pois["Cidade"])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.collect_garbage()
    print("POI actors:", sum(1 for a in eas.get_all_level_actors() if str(a.get_folder_path()).startswith("POI")))


if __name__ == "__main__":
    main()
