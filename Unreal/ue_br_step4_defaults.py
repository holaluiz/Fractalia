"""BR stage 1, step 4: default values of the match-loop Blueprints and L_Island setup.

- tuning defaults (ship route/speed, skydive, storm wall, loot tables with GDD 8 names, rarity colours);
- L_Island: BP_StormController at the centre, a PlayerStart on the plaza, GM_NexusRoyale as the level's game mode,
  and the 32 placeholder SM_Chest meshes swapped for BP_LootChest at the same transforms. Idempotent.
"""
import unreal

eal = unreal.EditorAssetLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
B = "/Game/NexusRoyale/Blueprints"
ITEMS = "/Game/Quaternius/Items"


def cdo(path):
    return unreal.get_default_object(eal.load_blueprint_class(path))


def mesh(name):
    return eal.load_asset(f"{ITEMS}/{name}/{name}")


def save(path):
    bp = eal.load_asset(path)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    eal.save_loaded_asset(bp)


# --- tuning
h = cdo(f"{B}/Core/BP_HeroBase")
for k, v in {"GlideHeight": 3000.0, "DiveFallSpeed": -2600.0, "GlideFallSpeed": -450.0,
             "ShipCameraDistance": 2400.0}.items():
    h.set_editor_property(k, v)
save(f"{B}/Core/BP_HeroBase")

s = cdo(f"{B}/Match/BP_DropShip")
s.set_editor_property("Speed", 1300.0)
s.set_editor_property("DropOffset", 600.0)
save(f"{B}/Match/BP_DropShip")

st = cdo(f"{B}/Match/BP_StormController")
st.set_editor_property("WallBaseZ", -3000.0)
st.set_editor_property("WallHeightScale", 150.0)
st.set_editor_property("NumPhases", 6)
save(f"{B}/Match/BP_StormController")

gm = cdo(f"{B}/Core/GM_NexusRoyale")
gm.set_editor_property("ShipAltitude", 14000.0)
gm.set_editor_property("ShipPathHalfLength", 32000.0)
gm.set_editor_property("ShipLateralSpread", 8000.0)
save(f"{B}/Core/GM_NexusRoyale")

# --- loot tables (GDD 8.1-8.3); grimoires cycle the 4 book meshes until school tints exist
ITEM_TABLE = [("Armor_Leather", "Couraça de Couro"), ("Armor_Metal", "Cota de Placas"), ("Armor_Black", "Manto Rúnico"),
              ("Crown2", "Elmo de Ferro"), ("Crown", "Diadema Arcano"), ("Glove", "Capuz do Rastreador"),
              ("Ring1", "Anel da Força"), ("Ring2", "Anel do Foco"), ("Ring3", "Anel do Vento"),
              ("Ring4", "Anel da Fonte"), ("Necklace1", "Amuleto do Tempo"), ("Heart", "Amuleto Vital"),
              ("Necklace2", "Amuleto do Duelista"), ("Necklace3", "Amuleto do Erudito")]
CONSUMABLES = [("Apple", "Comida leve (maçã)"), ("Bread", "Comida leve (pão)"), ("Banana", "Comida leve (banana)"),
               ("Burger", "Refeição (hambúrguer)"), ("Pizza", "Refeição (pizza)"), ("CookingPot_Soup", "Refeição (sopa)"),
               ("Potion5_Filled", "Poção de Mana"), ("Potion9_Filled", "Poção de Pressa")]
SPELLS = ["Arremetida", "Tiro Rasante", "Bola de Fogo", "Muro de Chamas", "Muralha de Gelo", "Coração Gélido",
          "Pilar de Pedra", "Fissura", "Rajada", "Carga Estática", "Névoa Sombria", "Sifão", "Farol", "Graça"]

ib = f"{B}/Loot/BP_Interactable"
cdo(ib).set_editor_property("Prompt", "Interagir")
save(ib)

ch = cdo(f"{B}/Loot/BP_LootChest")
ch.set_editor_property("Prompt", "Abrir baú")
ch.set_editor_property("OpenMesh", mesh("Chest_Open"))
ch.set_editor_property("ItemMeshes", [mesh(m) for m, _ in ITEM_TABLE])
ch.set_editor_property("ItemNames", [n for _, n in ITEM_TABLE])
ch.set_editor_property("ConsumableMeshes", [mesh(m) for m, _ in CONSUMABLES])
ch.set_editor_property("ConsumableNames", [n for _, n in CONSUMABLES])
ch.set_editor_property("GrimoireMeshes", [mesh(f"Book{i % 4 + 1}_Closed") for i in range(len(SPELLS))])
ch.set_editor_property("GrimoireNames", SPELLS)
ch.set_editor_property("GrimoireChance", 0.4)
save(f"{B}/Loot/BP_LootChest")

pk = cdo(f"{B}/Loot/BP_Pickup")
pk.set_editor_property("Prompt", "Pegar")
pk.set_editor_property("DisplaySize", 45.0)
pk.set_editor_property("RarityNames", ["Comum", "Incomum", "Raro", "Épico", "Lendário"])
pk.set_editor_property("KindNames", ["item", "grimório", "consumível"])
pk.set_editor_property("RarityColors", [unreal.LinearColor(0.6, 0.6, 0.6, 1.0), unreal.LinearColor(0.2, 0.9, 0.2, 1.0),
                                        unreal.LinearColor(0.2, 0.5, 1.0, 1.0), unreal.LinearColor(0.7, 0.3, 1.0, 1.0),
                                        unreal.LinearColor(1.0, 0.75, 0.1, 1.0)])
save(f"{B}/Loot/BP_Pickup")
print("defaults ok; chest items:", len(ch.get_editor_property("ItemMeshes")))

# --- level
level = "/Game/NexusRoyale/Maps/L_Island"
if les.get_current_level().get_outermost().get_name() != level:
    les.load_level(level)
actors = eas.get_all_level_actors()

storm_cls = eal.load_blueprint_class(f"{B}/Match/BP_StormController")
if not any(a.get_class() == storm_cls for a in actors):
    a = eas.spawn_actor_from_class(storm_cls, unreal.Vector(0, 0, 0))
    a.set_actor_label("StormController")
    a.set_folder_path("Gameplay/match")

if not any(isinstance(a, unreal.PlayerStart) for a in actors):
    ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0.0, -1600.0, 1000.0))
    ps.set_folder_path("Gameplay/match")

chest_cls = eal.load_blueprint_class(f"{B}/Loot/BP_LootChest")
swapped = 0
for a in actors:
    if isinstance(a, unreal.StaticMeshActor):
        sm = a.static_mesh_component.static_mesh
        if sm and sm.get_name() == "SM_Chest":
            new = eas.spawn_actor_from_class(chest_cls, a.get_actor_location(), a.get_actor_rotation())
            new.set_actor_scale3d(a.get_actor_scale3d())
            new.set_actor_label(a.get_actor_label().replace("SM_Chest", "LootChest"))
            new.set_folder_path("Gameplay/chest")
            eas.destroy_actor(a)
            swapped += 1
print("chests swapped:", swapped)

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property("default_game_mode", eal.load_blueprint_class(f"{B}/Core/GM_NexusRoyale"))
les.save_current_level()
print("level saved; game mode:", world.get_world_settings().get_editor_property("default_game_mode"))
