"""Mapa v2, passo 2: cria (ou abre) o nível /Game/NexusRoyale/Maps/L_Ilha com luz e céu, sem mexer no L_Island.
Antes de trocar de nível: para o PIE se estiver rodando e salva o que estiver sujo (para não perder trabalho de
outra sessão). O Landscape em si é importado à mão no painel (Design/Mapa.md, passo 1).
Rodar com: python -I Unreal/ue_py.py Unreal/ue_mapa_nivel.py
"""
import unreal

LEVEL = "/Game/NexusRoyale/Maps/L_Ilha"
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
eal = unreal.EditorAssetLibrary

if les.is_in_play_in_editor():
    les.editor_request_end_play()
    print("PIE estava rodando: parado")

saved = unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
print("pacotes sujos salvos:", saved)

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print("nível antes:", world.get_path_name())
if eal.does_asset_exist(LEVEL):
    print("abrindo", LEVEL, les.load_level(LEVEL))
else:
    print("criando", LEVEL, les.new_level(LEVEL, False))

have = {a.get_class().get_name() for a in eas.get_all_level_actors()}


def spawn(cls, label, loc=(0, 0, 0), rot=(0, 0, 0)):
    if cls.static_class().get_name() in have:
        return None
    a = eas.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(roll=rot[2], pitch=rot[0], yaw=rot[1]))
    a.set_actor_label(label)
    a.set_folder_path("Luz e Céu")
    return a


# sol vindo do noroeste (como o sombreado do mapa): luz viaja para sudeste (-X, +Y), 40° abaixo do horizonte
sun = spawn(unreal.DirectionalLight, "Sol", (0, 0, 20000), (-40, 135, 0))
if sun:
    comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
    comp.set_editor_property("intensity", 8.0)
    comp.set_editor_property("atmosphere_sun_light", True)
spawn(unreal.SkyAtmosphere, "Atmosfera", (0, 0, 0))
sky = spawn(unreal.SkyLight, "Luz do Céu", (0, 0, 15000))
if sky:
    sky.get_component_by_class(unreal.SkyLightComponent).set_editor_property("real_time_capture", True)
spawn(unreal.ExponentialHeightFog, "Névoa", (0, 0, 0))
spawn(unreal.PlayerStart, "Início (provisório)", (0, 0, 15000))

les.save_current_level()
print("nível agora:", unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name())
print("atores:", sorted(a.get_actor_label() for a in eas.get_all_level_actors()))
