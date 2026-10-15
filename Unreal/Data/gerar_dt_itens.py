"""Gera Unreal/Data/DT_Itens.csv (linhas do FNRItemRow em C++) a partir do GDD §8.

Números da raridade Comum; frações para porcentagens (0,04 = +4%). Rodar de novo depois de mudar a lista:
    python -I Unreal/Data/gerar_dt_itens.py
Depois reimportar o CSV no DT_Itens (o script ue_gas_setup.py faz isso).
"""
import csv
import os

ITEMS = "/Game/Quaternius/Items"
COLS = ["Name", "Nome", "Tipo", "Slot", "Malha", "bLendario", "VidaMax", "ManaMax", "Armadura", "DanoFisico",
        "PoderMagico", "VelocMov", "VelocAtaque", "ReducaoRecarga", "RegenMana", "EscalaComAtributo", "Cura",
        "CuraDuracao", "Mana", "ManaDuracao", "Pressa", "PressaDuracao", "Pilha", "Magia"]


def malha(nome):
    return f"{ITEMS}/{nome}/{nome}.{nome}"


def equip(id_, nome, slot, mesh, escala="Nenhum", **stats):
    return dict(Name=id_, Nome=nome, Tipo="Equipamento", Slot=slot, Malha=malha(mesh), EscalaComAtributo=escala, **stats)


def consumivel(id_, nome, mesh, pilha, **efeito):
    return dict(Name=id_, Nome=nome, Tipo="Consumivel", Slot="Nenhum", Malha=malha(mesh), Pilha=pilha, **efeito)


def grimorio(id_, magia, mesh):
    return dict(Name=f"Grimorio_{id_}", Nome=f"Grimório: {magia}", Tipo="Grimorio", Slot="Nenhum", Malha=malha(mesh),
                Magia=id_)


ROWS = [
    # GDD §8.1
    equip("CouracaCouro", "Couraça de Couro", "Armadura", "Armor_Leather", VidaMax=60, VelocMov=0.04),
    equip("CotaPlacas", "Cota de Placas", "Armadura", "Armor_Metal", VidaMax=100, Armadura=4),
    equip("MantoRunico", "Manto Rúnico", "Armadura", "Armor_Black", VidaMax=60, ManaMax=50),
    equip("ElmoFerro", "Elmo de Ferro", "Cabeca", "Crown2", VidaMax=50, Armadura=3),
    equip("DiademaArcano", "Diadema Arcano", "Cabeca", "Crown", ManaMax=40, PoderMagico=0.05),
    equip("CapuzRastreador", "Capuz do Rastreador", "Cabeca", "Glove", VelocAtaque=0.05, VelocMov=0.03),
    equip("AnelForca", "Anel da Força", "Anel", "Ring1", DanoFisico=0.06),
    equip("AnelFoco", "Anel do Foco", "Anel", "Ring2", PoderMagico=0.06),
    equip("AnelVento", "Anel do Vento", "Anel", "Ring3", VelocMov=0.05),
    equip("AnelFonte", "Anel da Fonte", "Anel", "Ring4", RegenMana=0.6),
    equip("AmuletoTempo", "Amuleto do Tempo", "Amuleto", "Necklace1", ReducaoRecarga=0.06),
    equip("AmuletoVital", "Amuleto Vital", "Amuleto", "Heart", VidaMax=100),
    equip("AmuletoDuelista", "Amuleto do Duelista", "Amuleto", "Necklace2", escala="Forca", DanoFisico=0.01),
    equip("AmuletoErudito", "Amuleto do Erudito", "Amuleto", "Necklace3", escala="Intelecto", PoderMagico=0.01),
    equip("AmuletoEremita", "Amuleto do Eremita", "Amuleto", "Necklace1", escala="Espirito", ReducaoRecarga=0.006),
    # GDD §8.3 (cada categoria é um item só, para empilhar no mesmo slot)
    consumivel("ComidaLeve", "Comida leve", "Apple", 6, Cura=60, CuraDuracao=2),
    consumivel("Refeicao", "Refeição", "Burger", 3, Cura=200, CuraDuracao=5),
    consumivel("PocaoMana", "Poção de Mana", "Potion5_Filled", 3, Mana=120, ManaDuracao=1),
    consumivel("PocaoPressa", "Poção de Pressa", "Potion9_Filled", 2, Pressa=0.25, PressaDuracao=6),
]
# GDD §6.3 (as 14 magias comuns); as malhas alternam entre os 4 livros até existir a cor por escola
SPELLS = [("Arremetida", "Arremetida"), ("TiroRasante", "Tiro Rasante"), ("BolaDeFogo", "Bola de Fogo"),
          ("MuroDeChamas", "Muro de Chamas"), ("MuralhaDeGelo", "Muralha de Gelo"), ("CoracaoGelido", "Coração Gélido"),
          ("PilarDePedra", "Pilar de Pedra"), ("Fissura", "Fissura"), ("Rajada", "Rajada"),
          ("CargaEstatica", "Carga Estática"), ("NevoaSombria", "Névoa Sombria"), ("Sifao", "Sifão"),
          ("Farol", "Farol"), ("Graca", "Graça")]
ROWS += [grimorio(sid, nome, f"Book{i % 4 + 1}_Closed") for i, (sid, nome) in enumerate(SPELLS)]

DEFAULTS = dict(bLendario="False", EscalaComAtributo="Nenhum", Pilha=1, Magia="None")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DT_Itens.csv")
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for row in ROWS:
        full = {c: DEFAULTS.get(c, 0) for c in COLS}
        full.update(row)
        w.writerow(full)
print(f"{len(ROWS)} linhas -> {out}")
