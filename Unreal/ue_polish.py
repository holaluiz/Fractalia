"""VRAM relief + hero showcase on the Nexus plaza."""
import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ROOT = "/Game/NexusRoyale"

# 1) 4K Tripo basecolor maps -> 2K in game
for p in eal.list_assets(f"{ROOT}/Heroes", recursive=False):
    a = eal.load_asset(p)
    if isinstance(a, unreal.Texture2D):
        a.set_editor_property("max_texture_size", 2048)
        eal.save_loaded_asset(a)
        print("texture capped:", a.get_name())

# 2) medium scalability for the editor viewport / PIE on a 4 GB GPU
unreal.SystemLibrary.execute_console_command(None, "Scalability 1")
unreal.SystemLibrary.execute_console_command(None, "r.Streaming.PoolSize 1200")

# 3) hero line-up facing the player start (player spawns at y=-1800 looking +Y)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Showcase_"):
        eas.destroy_actor(a)
heroes = ["Brakka", "Vela", "Zephyr", "Lumi", "Boto", "Caramelo", "PombaGira"]
for i, hero in enumerate(heroes):
    x = (i - (len(heroes) - 1) / 2) * 180.0
    cls = eal.load_blueprint_class(f"{ROOT}/Blueprints/BP_Hero_{hero}")
    actor = eas.spawn_actor_from_class(cls, unreal.Vector(x, -1250.0, 800.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=-90.0))
    actor.set_actor_label(f"Showcase_{hero}")
    actor.set_folder_path("Showcase")
    actor.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.DISABLED)
print("showcase placed")
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
