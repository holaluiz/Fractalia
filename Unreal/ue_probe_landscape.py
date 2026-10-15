"""Probe (só leitura): o que a API Python da Unreal oferece para criar/importar Landscape, e o estado do L_Island."""
import unreal

names = sorted(n for n in dir(unreal) if "andscape" in n)
print("classes com 'Landscape':", len(names))
print(", ".join(names))

for cls_name in ("LandscapeEditorSubsystem", "LandscapeProxy", "Landscape", "LandscapeSubsystem"):
    cls = getattr(unreal, cls_name, None)
    if cls is None:
        print(f"-- {cls_name}: não existe")
        continue
    meths = [m for m in dir(cls) if not m.startswith("_") and any(k in m.lower() for k in ("import", "create", "height", "layer", "weight", "render_target", "spawn"))]
    print(f"-- {cls_name}: {meths}")

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print("nível aberto:", world.get_path_name() if world else None)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
by_class = {}
for a in actors:
    by_class[a.get_class().get_name()] = by_class.get(a.get_class().get_name(), 0) + 1
print("atores no nível:", len(actors))
print(sorted(by_class.items(), key=lambda kv: -kv[1])[:25])
print("World Partition:", bool(world and world.get_world_partition()) if hasattr(world, "get_world_partition") else "?")
