"""Testa o combate do herói (GAS, dardo, Bola de Fogo, XP) durante o PIE.

Uso:  python ue_py.py -c "ACT='heroi'; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_combate.py', encoding='utf-8').read())"
ACT:  heroi        vida, mana, nível, XP, morto, recargas
      mirar        vira a câmera para o creep vivo mais próximo
      dardo        mira e aperta o botão esquerdo (injeta IA_AtaqueBasico pelo Enhanced Input)
      fogo         mira e aperta Q (IA_MagiaPrincipal)
      tecla1..3    aperta 1, 2 ou 3 (consumíveis)
      dardo_direto, fogo_direto   o mesmo sem passar pelo input (chama UsarAtaqueBasico/UsarMagiaPrincipal)
      bau          teleporta para o baú fechado mais perto e aperta F (IA_Interact)
      pegar        teleporta para o pickup mais perto e aperta F
      inventario   consumíveis, equipados, grimórios e a última mensagem do inventário
Junto com pie_creeps.py (land/near/state) para pôr o herói no acampamento.
"""
import math

import unreal

ACT = globals().get("ACT", "heroi")
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(w, 0)
hero = pc.get_controlled_pawn()
asc = hero.get_component_by_class(unreal.NRAbilitySystemComponent)
cb = hero.get_component_by_class(unreal.NRCombateComponent)


def heroi():
    print("HEROI vida %.0f/%.0f mana %.0f/%.0f nivel %d xp %d morto %s | recarga dardo %.1f s, Q %.1f s" % (
        asc.get_vida(), asc.get_vida_max(), asc.get_mana(), asc.get_mana_max(), asc.get_editor_property("Nivel"),
        asc.get_editor_property("XP"), asc.is_morto(), cb.recarga_restante(0), cb.recarga_restante(1)))


def mirar():
    vivos = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
             if a.get_class().get_name().startswith("BP_Creep_") and not a.get_editor_property("IsDead")]
    if not vivos:
        print("nenhum creep vivo")
        return
    alvo = min(vivos, key=lambda a: (a.get_actor_location() - hero.get_actor_location()).length())
    d = alvo.get_actor_location() - hero.get_actor_location()
    yaw = math.degrees(math.atan2(d.y, d.x))
    pitch = math.degrees(math.atan2(d.z - 60.0, math.hypot(d.x, d.y)))
    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))
    print("mirando", alvo.get_name(), "a %.1f m" % (d.length() / 100.0))


def apertar(acao):
    sub = [o for o in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem) if "LocalPlayer" in o.get_path_name()][-1]
    ia = unreal.load_object(None, f"/Game/Input/Actions/{acao}.{acao}")
    sub.inject_input_vector_for_action(ia, unreal.Vector(1.0, 0.0, 0.0), [], [])
    print("apertou", acao)


if ACT == "heroi":
    heroi()
elif ACT == "mirar":
    mirar()
elif ACT == "dardo":
    mirar()
    apertar("IA_AtaqueBasico")
elif ACT == "fogo":
    mirar()
    apertar("IA_MagiaPrincipal")
elif ACT == "dardo_direto":  # sem input: chama a fun�