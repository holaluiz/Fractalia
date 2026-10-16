"""Testa a máquina de estados da partida (marco M1) durante o PIE: fases, eliminação, abate, XP de abate e vitória.

Uso:  python ue_py.py -c "ACT='estado'; exec(open(r'D:/meus documentos/Fortnite/Unreal/pie_partida.py', encoding='utf-8').read())"
ACT:  estado     fase, tempo na fase e até o fim, vivos, jogadores no início, modo treino, vencedor e cada jogador
                 (nome, bot, vivo, colocação, abates, nível, causa da eliminação)
      bot        ANRGameMode.AdicionarBotDeTeste() (um bot com PlayerState que ocupa uma vaga)
      matar      mata ALVO (nome do jogador; padrão: o primeiro bot vivo). ASSASSINO = nome de quem leva o abate
                 ('eu' = o jogador local; vazio = sem assassino, como a tempestade). Usa AplicarDano no ASC do alvo,
                 com dano de jogador e sem armadura
      saltar     solta todos do dirigível (BP_DropShip.EjectAll), para não esperar a rota
      xp         mostra o XP de abate da fórmula do GameMode para NV (vítima) e NA (assassino)
      esperar    durante a Espera, faz o GameMode aguardar N humanos (padrão 2), para um cliente de rede entrar
As opções (ALVO, ASSASSINO, NV, NA) são apagadas no começo de cada execução: o Python remoto guarda as globais.
"""
import unreal

ACT = globals().pop("ACT", "estado")
OPCOES = {k: globals().pop(k) for k in ("ALVO", "ASSASSINO", "NV", "NA", "N") if k in globals()}
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert w, "sem PIE"
gm = unreal.GameplayStatics.get_game_mode(w)
gs = unreal.GameplayStatics.get_game_state(w)
pc = unreal.GameplayStatics.get_player_controller(w, 0)


def prop(obj, *nomes):
    for n in nomes:
        try:
            return obj.get_editor_property(n)
        except Exception:  # noqa: BLE001
            pass
    return None


def jogadores():
    return [ps for ps in gs.get_editor_property("player_array") if isinstance(ps, unreal.NRPlayerState)]


def nome(ps):
    return ps.get_player_name()


def heroi_de(ps):
    return ps.get_pawn() if ps else None


def achar(alvo):
    if alvo == "eu":
        return pc.player_state
    for ps in jogadores():
        if nome(ps) == alvo:
            return ps
    return None


def estado():
    agora = gs.get_server_world_time_seconds()
    inicio, fim = prop(gs, "InicioDaFase"), prop(gs, "FimDaFase")
    venc = prop(gs, "Vencedor")
    print("PARTIDA fase %s | %.1f s na fase | fim em %s | vivos %d | no início %d | treino %s | vencedor %s | GM %s" % (
        prop(gs, "Fase"), agora - inicio, ("%.1f s" % (fim - agora)) if fim else "-", gs.contar_vivos(),
        prop(gs, "JogadoresNoInicio"), prop(gs, "bModoTreino", "modo_treino"), nome(venc) if venc else "-",
        gm.get_class().get_name() if gm else "?"))
    for ps in jogadores():
        heroi = heroi_de(ps)
        asc = heroi.get_component_by_class(unreal.NRAbilitySystemComponent) if heroi else None
        print("  %-10s bot=%s vivo=%s col=%s abates=%s nivel=%s (asc %s, xp %s) vida=%s causa=%r hidden=%s" % (
            nome(ps), prop(ps, "is_a_bot", "bIsABot"), prop(ps, "bVivo", "vivo"), prop(ps, "Colocacao"), prop(ps, "Abates"),
            prop(ps, "Nivel"), prop(asc, "Nivel") if asc else "-", prop(asc, "XP") if asc else "-",
            ("%.0f/%.0f" % (asc.get_vida(), asc.get_vida_max())) if asc else "-",
            prop(ps, "CausaDaEliminacao"), prop(heroi, "hidden", "bHidden") if heroi else "-"))


if ACT == "estado":
    estado()
elif ACT == "bot":
    pawn = gm.adicionar_bot_de_teste()
    print("bot:", pawn.get_name() if pawn else None)
    estado()
elif ACT == "matar":
    alvo = OPCOES.get("ALVO")
    ps_alvo = achar(alvo) if alvo else next((p for p in jogadores() if prop(p, "is_a_bot", "bIsABot") and prop(p, "bVivo", "vivo")), None)
    assert ps_alvo, f"não achei o alvo {alvo!r}"
    ps_assassino = achar(OPCOES["ASSASSINO"]) if OPCOES.get("ASSASSINO") else None
    vitima = heroi_de(ps_alvo)
    asc = vitima.get_component_by_class(unreal.NRAbilitySystemComponent)
    asc.aplicar_dano(100000.0, heroi_de(ps_assassino), True, True)
    print("matou %s (assassino: %s)" % (nome(ps_alvo), nome(ps_assassino) if ps_assassino else "-"))
    estado()
elif ACT == "saltar":
    naves = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.get_class().get_name() == "BP_DropShip_C"]
    for nave in naves:
        nave.call_method("EjectAll")
    print("dirigíveis:", len(naves))
    estado()
elif ACT == "xp":
    nv, na = int(OPCOES.get("NV", 5)), int(OPCOES.get("NA", 5))
    print("XP de abate (vítima %d, assassino %d): %d" % (nv, na, gm.xp_de_abate(nv, na)))
elif ACT == "esperar":
    gm.esperar_jogadores(int(OPCOES.get("N", 2)))
    estado()
