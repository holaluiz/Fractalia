import unreal


def doc(cls, names):
    for n in names:
        f = getattr(cls, n, None)
        d = ((f.__doc__ or "").strip().splitlines() or [""])[0] if f else "MISSING"
        print(f"  {cls.__name__}.{n}: {d[:160]}")


doc(unreal.InterchangeManager, ["get_interchange_manager_scripted", "create_source_data", "import_asset", "import_scene"])
p = unreal.ImportAssetParameters()
print("ImportAssetParameters props:", [x for x in dir(p) if not x.startswith("_") and x.islower()][:40])
pipe = unreal.InterchangeGenericAssetsPipeline()
print("pipeline props:", [x for x in dir(pipe) if not x.startswith("_") and x.islower() and "propert" in x])
sk = pipe.get_editor_property("common_skeletal_meshes_and_animations_properties")
print("common skel props:", [x for x in dir(sk) if not x.startswith("_") and x.islower()][:40])
doc(unreal.Skeleton, ["add_compatible_skeleton", "get_compatible_skeletons"])
print("skeleton editor props:", [x for x in dir(unreal.Skeleton) if "compat" in x.lower()])
