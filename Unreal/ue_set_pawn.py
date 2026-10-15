"""Set the default pawn of the template GameMode and make L_Island the startup/default map."""
import unreal

HERO = "Caramelo"
eal = unreal.EditorAssetLibrary
gm = eal.load_asset("/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode")
cdo = unreal.get_default_object(gm.generated_class())
cdo.set_editor_property("default_pawn_class", eal.load_blueprint_class(f"/Game/NexusRoyale/Blueprints/BP_Hero_{HERO}"))
unreal.BlueprintEditorLibrary.compile_blueprint(gm)
eal.save_loaded_asset(gm)
print("pawn:", unreal.get_default_object(gm.generated_class()).get_editor_property("default_pawn_class"))

maps = unreal.get_default_object(unreal.GameMapsSettings)
level = unreal.SoftObjectPath("/Game/NexusRoyale/Maps/L_Island.L_Island")
maps.set_editor_property("editor_startup_map", level)
maps.set_editor_property("game_default_map", level)
maps.save_config()
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
cur = les.get_current_level().get_outermost().get_name()
if cur != "/Game/NexusRoyale/Maps/L_Island":
    les.load_level("/Game/NexusRoyale/Maps/L_Island")
print("level:", les.get_current_level().get_outermost().get_name())
