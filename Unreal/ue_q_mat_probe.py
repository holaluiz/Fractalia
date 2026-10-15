import unreal

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
seen = set()
for folder in ("/Game/Quaternius/Characters/Superhero_Male_FullBody", "/Game/Quaternius/Characters/Hair_Long"):
    for p in eal.list_assets(folder, recursive=True):
        d = eal.find_asset_data(p)
        cls = str(d.asset_class_path.asset_name)
        if cls in ("Texture2D", "SkeletalMesh", "PhysicsAsset"):
            continue
        a = eal.load_asset(p.split(".")[0])
        line = f"{cls:28s} {p.split('.')[0]}"
        if isinstance(a, unreal.MaterialInterface):
            base = a.get_base_material()
            line += f" | base={base.get_path_name()} blend={base.get_editor_property('blend_mode')}"
            if isinstance(a, unreal.MaterialInstance):
                line += f" | vec={[str(x) for x in mel.get_vector_parameter_names(a)]} tex={[str(x) for x in mel.get_texture_parameter_names(a)]} sc={[str(x) for x in mel.get_scalar_parameter_names(a)]}"
        print(line)
