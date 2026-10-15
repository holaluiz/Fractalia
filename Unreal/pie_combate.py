"""Testa o combate do herói (GAS, dardo, Bola de Fogo, XP) durante o PIE.

Uso:  python ue_py.py -c "ACT='heroi'; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_combate.py', encoding='utf-8').read())"
ACT:  heroi        vida, mana, nível, XP, morto, recargas
      mirar        vira a câmera para o creep vivo mais próximo
      dardo        mira e aperta o botão esquerdo (injeta IA_AtaqueBasico pelo Enhanced Input)
      fogo         mira e aperta Q (IA_MagiaPrincipal)
      muralha      vira para o creep vivo mais próximo, olha para o chão (PITCH, padrão -25) e aperta E (IA_Magia2)
      meteoros     mira no centro do acampamento e aperta X (IA_Ultimate)
      mirar_chao, mirar_acampamento   só a mira do "muralha" e do "meteoros"
      SO_TECLA=1   (com muralha/meteoros) aperta sem mirar. Use depois de um mirar_* numa chamada anterior: o input
                   é processado antes da câmera se atualizar no frame, então girar e apertar na mesma chamada usa a
                   direção antiga da câmera
      estruturas   estruturas mágicas vivas: vida, tempo restante, distância do herói e do creep mais próximo
      muralha_dano ApplyDamage DANO (padrão 150) na estrutura mais próxima, sem instigador (como um inimigo)
      chuvas       Chuvas de Meteoros ativas e quantos alvos já acertaram
      xp           GanharXP(N) (padrão 100), para testar a liberação da ultimate
      tecla1..3    aperta 1, 2 ou 3 (consumíveis)
      dardo_direto, fogo_direto, muralha_direto, meteoros_direto
                   o mesmo sem passar pelo input (chama UsarAtaqueBasico/UsarMagiaPrincipal/UsarMagia2/UsarUltimate)
      bau          teleporta para o baú fechado mais perto e aperta F (IA_Interact)
      pegar        teleporta para o pickup mais perto e aperta F
      inventario   consumíveis, equipados, grimórios e a última mensagem do inventário
      mutacoes     fila de níveis, opções da vez (com a descrição), trocas restantes e as escolhidas
      escolher     Escolher(N) (padrão 0) direto no componente Mutacoes, sem o Alt
      trocar       TrocarOpcoes() direto no componente
      piso         AplicarPisoDeNivel(N) (padrão 4), como o fim de fase da tempestade faz
      atributos    pontos efetivos (For, Agi, Vit, Int, Esp), velocidade máxima, bônus fora de combate e o que
                   mudou nas magias (largura da muralha, chamas da Bola de Fogo, recarga/raio da ultimate)
Junto com pie_creeps.py (land/near/state) para pôr o herói no acampamento.
O Python remoto do editor guarda as variáveis entre chamadas: as opções (SO_TECLA, PITCH, DANO, N) são apagadas
no começo de cada execução, para não valerem na próxima sem ninguém pedir.
"""
import math

import unreal

ACT = globals().get("ACT", "heroi")
# Lidas e apagadas já no início (mesmo que o script falhe depois): o Python remoto guarda as globais entre chamadas.
OPCOES = {k: globals().pop(k) for k in ("SO_TECLA", "PITCH", "DANO", "N") if k in globals()}
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(w, 0)
hero = pc.get_controlled_pawn()
asc = hero.get_component_by_class(unreal.NRAbilitySystemComponent)
cb = hero.get_component_by_class(unreal.NRCombateComponent)


def heroi():
    print("HEROI vida %.0f/%.0f mana %.0f/%.0f nivel %d xp %d morto %s | recarga dardo %.1f s, Q %.1f s, E %.1f s, X %.1f s"
          " (ultimate liberada: %s)" % (
              asc.get_vida(), asc.get_vida_max(), asc.get_mana(), asc.get_mana_max(), asc.get_editor_property("Nivel"),
              asc.get_editor_property("XP"), asc.is_morto(), cb.recarga_restante(0), cb.recarga_restante(1),
              cb.recarga_restante(2), cb.recarga_restante(3), cb.ultimate_liberada()))


def creeps_vivos():
    return [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character)
            if a.get_class().get_name().startswith("BP_Creep_") and not a.get_editor_property("IsDead")]


def mirar_em(loc, pitch=None):
    """Yaw a partir do herói (a câmera gira atrás dele); pitch a partir da câmera atual, salvo se PITCH for dado."""
    h = hero.get_actor_location()
    yaw = math.degrees(math.atan2(loc.y - h.y, loc.x - h.x))
    if pitch is None:
        cam = pc.player_camera_manager.get_camera_location()
        d = loc - cam
        pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
    pc.set_control_rotation(unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))
    print("mira yaw %.1f pitch %.1f" % (yaw, pitch))


def acampamento():
    camps = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_CreepCamp_C"]
    return min(camps, key=lambda a: (a.get_actor_location() - hero.get_actor_location()).length()) if camps else None


def estruturas():
    lista = list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.NREstruturaMagica))
    vivos = creeps_vivos()
    for e in lista:
        loc = e.get_actor_location()
        perto = min(((c.get_actor_location() - loc).length() / 100.0 for c in vivos), default=-1)
        print("ESTRUTURA %s vida %.0f/%.0f resta %.1f s desfazendo %s | herói a %.1f m, creep mais perto a %.1f m, z %.0f" % (
            e.get_name(), e.get_editor_property("Vida"), e.get_editor_property("VidaMax"), e.tempo_restante(),
            e.esta_desfazendo(), (hero.get_actor_location() - loc).length() / 100.0, perto, loc.z))
    if not lista:
        print("nenhuma estrutura")
    return lista


def mirar():
    vivos = creeps_vivos()
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
    # Sem o objeto padrão da classe (Default__…): o nome dele também contém "LocalPlayer", e a ordem da lista varia.
    sub = [o for o in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem)
           if "LocalPlayer_" in o.get_path_name() and "Default__" not in o.get_path_name()][-1]
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
elif ACT == "dardo_direto":  # sem input: chama a função do componente
    mirar()
    print("lançou", cb.usar_ataque_basico())
elif ACT == "fogo_direto":
    mirar()
    print("lançou", cb.usar_magia_principal())
elif ACT in ("muralha", "muralha_direto", "mirar_chao"):
    vivos = creeps_vivos()
    if vivos and not OPCOES.get("SO_TECLA"):
        alvo = min(vivos, key=lambda a: (a.get_actor_location() - hero.get_actor_location()).length())
        mirar_em(alvo.get_actor_location(), float(OPCOES.get("PITCH", -25.0)))
    if ACT == "muralha":
        apertar("IA_Magia2")
    elif ACT == "muralha_direto":
        print("lançou", cb.usar_magia2())
elif ACT in ("meteoros", "meteoros_direto", "mirar_acampamento"):
    cp = acampamento()
    if cp and not OPCOES.get("SO_TECLA"):
        mirar_em(cp.get_actor_location())
    if ACT == "meteoros":
        apertar("IA_Ultimate")
    elif ACT == "meteoros_direto":
        print("lançou", cb.usar_ultimate())
elif ACT == "estruturas":
    estruturas()
elif ACT == "muralha_dano":
    lista = estruturas()
    if lista:
        e = min(lista, key=lambda a: (a.get_actor_location() - hero.get_actor_location()).length())
        print("dano aplicado", unreal.GameplayStatics.apply_damage(e, float(OPCOES.get("DANO", 150.0)), None, None, None))
        print("vida agora %.0f, desfazendo %s" % (e.get_editor_property("Vida"), e.esta_desfazendo()))
elif ACT == "chuvas":
    lista = list(unreal.GameplayStatics.get_all_actors_of_class(w, unreal.NRChuvaMeteoros))
    for c in lista:
        print("CHUVA", c.get_name(), c.get_actor_location(), "alvos atingidos", c.alvos_atingidos())
    if not lista:
        print("nenhuma chuva ativa")
elif ACT == "xp":
    asc.ganhar_xp(int(OPCOES.get("N", 100)))
elif ACT.startswith("tecla"):
    apertar("IA_Consumivel" + ACT[-1])
elif ACT in ("mutacoes", "escolher", "trocar", "piso", "atributos"):
    mut = hero.get_component_by_class(unreal.NRMutacoesComponent)
    if ACT == "escolher":
        print("escolheu:", mut.escolher(int(OPCOES.get("N", 0))))
    elif ACT == "trocar":
        print("trocou:", mut.trocar_opcoes())
    elif ACT == "piso":
        unreal.NRAbilitySystemComponent.aplicar_piso_de_nivel(w, int(OPCOES.get("N", 4)))
    print("MUTACOES fila", list(mut.get_editor_property("NiveisPendentes")), "trocas", mut.get_editor_property("TrocasRestantes"))
    for i, m in enumerate(mut.get_editor_property("Opcoes")):
        print("  opcao %d: %s: %s" % (i, unreal.NRMutacoesComponent.nome(m), mut.descrever(m)))
    print("  escolhidas:", [str(unreal.NRMutacoesComponent.nome(m)) for m in mut.get_editor_property("Escolhidas")])
    print("ATRIBUTOS", [round(asc.get_pontos_efetivos(i), 2) for i in range(5)],
          "veloc max %.0f" % hero.get_component_by_class(unreal.CharacterMovementComponent).get_editor_property("max_walk_speed"),
          "fora de combate +%.2f" % asc.get_editor_property("BonusVelocForaDeCombate"),
          "| muralha %.0f cm, chamas Q %.1f s, ult recarga %.1f s raio %.0f, mana devolvida %.2f" % (
              cb.get_editor_property("Magia2").get_editor_property("Tamanho").y,
              cb.get_editor_property("MagiaPrincipal").get_editor_property("DuracaoChamas"),
              cb.get_editor_property("Ultimate").get_editor_property("Recarga"),
              cb.get_editor_property("Ultimate").get_editor_property("RaioArea"),
              cb.get_editor_property("ManaDevolvidaUltimate")))
elif ACT in ("bau", "pegar"):  # vai até o baú fechado (ou o pickup) mais perto e aperta F
    cls_name = "BP_LootChest_C" if ACT == "bau" else "BP_Pickup_C"
    alvos = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == cls_name]
    if ACT == "bau":
        alvos = [a for a in alvos if not a.get_editor_property("bOpened")]
    if not alvos:
        print("nada para", ACT)
    else:
        alvo = min(alvos, key=lambda a: (a.get_actor_location() - hero.get_actor_location()).length())
        loc = alvo.get_actor_location()
        hero.set_actor_location(unreal.Vector(loc.x - 60.0, loc.y, loc.z + 100.0), False, True)
        print(ACT, alvo.get_name(), "item", alvo.get_editor_property("ItemName") if ACT == "pegar" else "")
        apertar("IA_Interact")
if ACT in ("inventario", "bau", "pegar") or ACT.startswith("tecla"):
    inv = hero.get_component_by_class(unreal.NRInventoryComponent)
    print("CONSUMIVEIS", [(str(s.get_editor_property("ItemId")), s.get_editor_property("Quantidade")) for s in inv.get_editor_property("Consumiveis")])
    print("EQUIPADOS", [str(e.get_editor_property("ItemId")) for e in inv.get_editor_property("Equipados")])
    print("GRIMORIOS", [str(g.get_editor_property("ItemId")) for g in inv.get_editor_property("Grimorios")])
    print("MENSAGEM", inv.mensagem_recente())
heroi()
