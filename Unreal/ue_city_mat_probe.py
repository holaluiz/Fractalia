import unreal

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
for kit_name in ("City/Street_4Lane", "City/Building_Large_2", "Medieval/Wall_Plaster_Straight"):
    folder = f"/Game/Quaternius/Env/{kit_name}/Materials"
    for p in eal.list_assets(folder, recursive=False)[:3]:
        a = eal.load_asset(p.split(".")[0])
        line = f"{kit_name:28s} {a.get_class().get_name():26s} {a.get_name()}"
        if isinstance(a, unreal.MaterialInstance):
            parent = a.get_editor_property("parent")
            line += f" | parent={parent.get_path_name() if parent else None}"
            line += f" | scalars={[str(n) for n in mel.get_scalar_parameter_names(a)][:12]}"
            line += f" | statics={[str(n) for n in mel.get_static_switch_parameter_names(a)][:12]}"
        print(line)
