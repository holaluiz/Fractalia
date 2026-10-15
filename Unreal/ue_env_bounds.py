import unreal

eal = unreal.EditorAssetLibrary
for kit, name in (("Medieval", "Wall_Plaster_Straight"), ("Medieval", "Floor_WoodDark"), ("Medieval", "Roof_RoundTiles_6x8"),
                  ("Medieval", "Roof_Front_Brick6"), ("Medieval", "Corner_Exterior_Wood"), ("Medieval", "Door_1_Round"),
                  ("Medieval", "Wall_Plaster_Door_Round"), ("City", "Building_Large_2"), ("City", "Building_Small_1"),
                  ("City", "Building_Medium_2_001"), ("City", "Street_4WayIntersection"), ("City", "Street_4Lane"),
                  ("City", "Sidewalk_Straight_3m"), ("Nature", "CommonTree_1"), ("Nature", "Grass_Common_Tall")):
    m = eal.load_asset(f"/Game/Quaternius/Env/{kit}/{name}/StaticMeshes/{name}")
    if m is None:
        print("missing", kit, name)
        continue
    bb = m.get_bounding_box()
    print(f"{name:26s} X[{bb.min.x:7.0f},{bb.max.x:7.0f}] Y[{bb.min.y:7.0f},{bb.max.y:7.0f}] Z[{bb.min.z:6.0f},{bb.max.z:6.0f}]")
