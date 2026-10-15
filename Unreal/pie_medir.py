"""Medição de desempenho durante o PIE (antes/depois da troca de renderização).

Usage:  python ue_py.py -c "ACT='inicio'; AIM=(-8, 200); exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_medir.py').read())"
        (espere uns 15 s no jogo)
        python ue_py.py -c "ACT='fim'; TAG='antes'; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_medir.py').read())"
ACT:    inicio   vira a câmera (AIM opcional), desliga a janela do ProfileGPU e começa o FPSChart
        fim      para o FPSChart e joga no log: médias de FPS/GPU/render/game, ProfileGPU de um quadro,
                 rhi.DumpMemory, pool de render targets e o total do ListTextures
        cvar     só imprime os cvars de renderização que importam aqui (GI, reflexos, VSM, distance fields, CustomDepth)
O resumo sai no log entre as linhas "=== MEDIR <TAG> ===" e "=== MEDIR <TAG> fim ===". A memória de vídeo por
processo vem do Windows (contador "GPU Process Memory"), fora do editor.
"""
import unreal

ACT = globals().get("ACT", "cvar")
TAG = globals().get("TAG", "medida")
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
CVARS = ("r.DynamicGlobalIlluminationMethod", "r.ReflectionMethod", "r.Shadow.Virtual.Enable",
         "r.GenerateMeshDistanceFields", "r.CustomDepth", "r.Lumen.TraceMeshSDFs", "r.ScreenPercentage",
         "r.Streaming.PoolSize", "r.AmbientOcclusionLevels", "r.Nanite")


def cmd(c):
    unreal.SystemLibrary.execute_console_command(w, c)


if ACT == "cvar":
    for c in CVARS:
        print(c, "=", unreal.SystemLibrary.get_console_variable_int_value(c),
              "/", unreal.SystemLibrary.get_console_variable_float_value(c))
elif w is None:
    raise RuntimeError("PIE não está rodando")
elif ACT == "inicio":
    if "AIM" in globals():
        pc = unreal.GameplayStatics.get_player_controller(w, 0)
        pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=AIM[0], yaw=AIM[1]))
    cmd("r.ProfileGPU.ShowUI 0")
    cmd("StartFPSChart")
    print("FPSChart iniciado")
elif ACT == "fim":
    unreal.log(f"=== MEDIR {TAG} ===")
    for c in CVARS:
        unreal.log(f"cvar {c} = {unreal.SystemLibrary.get_console_variable_float_value(c)}")
    cmd("StopFPSChart")
    cmd("rhi.DumpMemory")
    cmd("r.DumpRenderTargetPoolMemory")
    cmd("ListTextures")
    cmd("ProfileGPU")
    unreal.log(f"=== MEDIR {TAG} fim ===")
    print("medição jogada no log:", TAG)
