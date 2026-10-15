"""BR stage 1, step 2: variables, functions, dispatchers and DSL graphs of the match-loop and creep Blueprints (via MCP).

Usage:  python ue_br_build.py [members|graphs|all] [BP_Name ...]
DSL sources live in Unreal/Blueprints/<BP>__<Graph>.dsl (EventGraph or a function name). Idempotent.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

BPT = "editor_toolset.toolsets.blueprint.BlueprintTools"
HERE = os.path.dirname(os.path.abspath(__file__))
DSL_DIR = os.path.join(HERE, "Blueprints")

B = "/Game/NexusRoyale/Blueprints"
PATHS = {
    "BP_HeroBase": f"{B}/Core/BP_HeroBase",
    "GM_NexusRoyale": f"{B}/Core/GM_NexusRoyale",
    "BP_StormController": f"{B}/Match/BP_StormController",
    "BP_DropShip": f"{B}/Match/BP_DropShip",
    "BP_Interactable": f"{B}/Loot/BP_Interactable",
    "BP_LootChest": f"{B}/Loot/BP_LootChest",
    "BP_Pickup": f"{B}/Loot/BP_Pickup",
    "BP_Creep": f"{B}/Creeps/BP_Creep",
    "BP_CreepCamp": f"{B}/Creeps/BP_CreepCamp",
}


def ref(name):
    p = PATHS[name]
    return {"refPath": f"{p}.{p.rsplit('/', 1)[1]}"}


def cls(name):
    p = PATHS.get(name)
    if p:
        return {"refPath": f"{p}.{p.rsplit('/', 1)[1]}_C"}
    return {"refPath": name}  # engine class path, e.g. /Script/Engine.StaticMesh


# variable spec: (name, type) where type is a basic type, ("obj", class), ("struct", path); suffix [] = array
# flags: "rep" replicated, "edit" instance editable
SPEC = {
    "BP_HeroBase": {
        "vars": [("bOnShip", "bool"), ("bSkydiving", "bool"), ("CurrentShip", ("obj", "BP_DropShip")),
                 ("CurrentInteractable", ("obj", "BP_Interactable")), ("GlideHeight", "float"),
                 ("DiveFallSpeed", "float"), ("GlideFallSpeed", "float"), ("ShipCameraDistance", "float"),
                 ("DefaultCameraDistance", "float"),
                 ("DefaultGravityScale", "float"), ("DefaultAirControl", "float"), ("DamageTaken", "float")],
        "fns": {"StormTick": [("DamagePercent", "float")], "EnterShip": [("Ship", ("obj", "BP_DropShip"))],
                "ExitShip": [("DropLocation", "Vector")], "SetInteractable": [("Target", ("obj", "BP_Interactable"))],
                "ClearInteractable": [("Target", ("obj", "BP_Interactable"))], "HandleJumpStarted": [],
                "HandleJumpCompleted": [], "HandleInteract": [], "UpdateSkydive": [], "EndSkydive": []},
    },
    "BP_DropShip": {
        "vars": [("StartPoint", "Vector", "rep"), ("EndPoint", "Vector", "rep"), ("Speed", "float", "edit"),
                 ("LaunchTime", "float", "rep"), ("bFlying", "bool", "rep"), ("Passengers[]", ("obj", "BP_HeroBase")),
                 ("DropOffset", "float"), ("DropRadius", "float", "edit")],
        "fns": {"Launch": [("Start", "Vector"), ("End", "Vector")], "Board": [("Hero", ("obj", "BP_HeroBase"))],
                "Eject": [("Hero", ("obj", "BP_HeroBase"))], "EjectAll": [], "FlyTick": []},
    },
    "BP_StormController": {
        "vars": [("StormTable", ("obj", "/Script/Engine.CurveTable")), ("StartTime", "float", "rep"),
                 ("bStarted", "bool", "rep"), ("Centers[]", "Vector", "rep"), ("CurCenter", "Vector"),
                 ("CurRadius", "float"), ("CurPhase", "int"), ("bClosing", "bool"), ("LastPhase", "int"),
                 ("WallBaseZ", "float", "edit"), ("WallHeightScale", "float", "edit"), ("NumPhases", "int")],
        "dispatchers": {"OnPhaseStarted": [("Phase", "int")], "OnPhaseEnded": [("Phase", "int"), ("LevelFloor", "int")]},
        "fns": {"StormValue": [("Row", "name"), ("Phase", "int"), ("Value", "float", "out")], "StartStorm": [],
                "UpdateCircle": [], "UpdateWall": [], "CheckPhaseEvents": [], "DamageTick": [],
                "ServerTime": [("Time", "float", "out")],
                "DebugSkipTo": [("Seconds", "float")]},
    },
    "BP_Interactable": {
        "vars": [("Prompt", "text", "edit")],
        "fns": {"Interact": [("Hero", ("obj", "BP_HeroBase"))]},
    },
    "BP_LootChest": {
        "vars": [("bOpened", "bool", "rep"), ("OpenMesh", ("obj", "/Script/Engine.StaticMesh")),
                 ("ItemMeshes[]", ("obj", "/Script/Engine.StaticMesh")), ("ItemNames[]", "string"),
                 ("ConsumableMeshes[]", ("obj", "/Script/Engine.StaticMesh")), ("ConsumableNames[]", "string"),
                 ("GrimoireMeshes[]", ("obj", "/Script/Engine.StaticMesh")), ("GrimoireNames[]", "string"),
                 ("GrimoireChance", "float", "edit"), ("bGolden", "bool", "edit")],
        "fns": {"Interact": None, "SpawnPickup": [("Mesh", ("obj", "/Script/Engine.StaticMesh")), ("Label", "string"),
                                                  ("Kind", "int"), ("Rarity", "int"), ("Slot", "int")],
                "RollRarity": [("Rarity", "int", "out")],
                "SpawnItem": [("ItemId", "name"), ("Kind", "int"), ("Rarity", "int"), ("Slot", "int")]},
    },
    "BP_Pickup": {
        "vars": [("ItemName", "string", "rep"), ("Kind", "int", "rep"), ("Rarity", "int", "rep"),
                 ("RarityColors[]", "LinearColor"), ("RarityNames[]", "string"), ("KindNames[]", "string"),
                 ("DisplaySize", "float"), ("ItemId", "name", "rep")],
        "fns": {"Interact": None, "Setup": [("Mesh", ("obj", "/Script/Engine.StaticMesh")), ("Label", "string"),
                                            ("InKind", "int"), ("InRarity", "int")],
                "SetupItem": [("InItemId", "name"), ("InKind", "int"), ("InRarity", "int")]},
    },
    "BP_Creep": {  # jungle creep (GDD 12); per-monster numbers live in the children's defaults (ue_creeps_camp.py)
        "vars": [("Health", "float"), ("MaxHealth", "float", "edit"), ("HomeLocation", "Vector"),
                 ("AggroRadius", "float", "edit"), ("LeashRadius", "float", "edit"), ("AttackRange", "float", "edit"),
                 ("AttackDamage", "float", "edit"), ("AttackCooldown", "float", "edit"), ("LastAttackTime", "float"),
                 ("XPReward", "int", "edit"), ("HitAnim", ("obj", "/Script/Engine.AnimSequenceBase")),
                 ("AttackAnim", ("obj", "/Script/Engine.AnimSequenceBase")),
                 ("DeathAnim", ("obj", "/Script/Engine.AnimSequenceBase")), ("IsDead", "bool"),
                 ("Target", ("obj", "/Script/Engine.Pawn")), ("MoveGoal", "Vector"), ("StopDistance", "float"),
                 ("bMoving", "bool"), ("BlockingStructure", ("obj", "/Script/Engine.Actor"))],
        "dispatchers": {"OnCreepKilled": [("Killer", ("obj", "/Script/Engine.Controller")), ("XP", "int")]},
        "fns": {"Think": [], "Die": [("Killer", ("obj", "/Script/Engine.Controller"))],
                "Alert": [("Attacker", ("obj", "/Script/Engine.Pawn"))], "ResetLeash": [],
                "FindBlocker": [("TargetLocation", "Vector")],
                "AttackActor": [("Victim", ("obj", "/Script/Engine.Actor")), ("LookAt", "Vector")]},
    },
    "BP_CreepCamp": {  # CreepClasses is a class<BP_Creep> array: ue_creeps_camp.py fixes its type after "members"
        "vars": [("CreepClasses[]", ("obj", "BP_Creep"), "edit"), ("Creeps[]", ("obj", "BP_Creep")),
                 ("SpawnRadius", "float", "edit"), ("RespawnDelay", "float", "edit"), ("bRespawnPending", "bool"),
                 ("AliveCount", "int")],
        "fns": {"SpawnCamp": [], "CheckCamp": [], "Respawn": []},
    },
    "GM_NexusRoyale": {
        "vars": [("ShipAltitude", "float"), ("ShipPathHalfLength", "float"), ("ShipLateralSpread", "float")],
        "fns": {},
    },
}


class Builder:
    def __init__(self):
        self.c = Client()
        self.c.initialize()

    def tool(self, name, args, quiet=False):
        res = self.c.call("call_tool", {"toolset_name": BPT, "tool_name": name, "arguments": args})
        txt = res["content"][0]["text"] if res and res.get("content") else ""
        err = bool(res and res.get("isError"))
        if err and not quiet:
            print(f"  ! {name}: {txt[:400]}")
        try:
            return json.loads(txt).get("returnValue"), err
        except (ValueError, AttributeError):
            return txt, err

    def existing_vars(self, bp):
        rv, _ = self.tool("list_variables", {"blueprint": ref(bp)})
        out = set()
        for v in rv or []:
            out.add(v.get("name") if isinstance(v, dict) else str(v))
        return out

    def graphs(self, bp):
        rv, _ = self.tool("list_graphs", {"blueprint": ref(bp)})
        return {g["refPath"].rsplit(":", 1)[-1]: g for g in rv or []}

    def add_var(self, bp, spec, have):
        name, typ = spec[0], spec[1]
        flags = spec[2:] if len(spec) > 2 else ()
        array = name.endswith("[]")
        name = name.rstrip("[]")
        if name not in have:
            args = {"blueprint": ref(bp), "name": name}
            if array:
                args["container_type"] = "ARRAY"
            if isinstance(typ, tuple) and typ[0] == "obj":
                args["object_class"] = cls(typ[1])
                self.tool("add_object_variable", args)
            elif isinstance(typ, tuple) and typ[0] == "struct":
                args["struct_type"] = {"refPath": typ[1]}
                self.tool("add_struct_variable", args)
            else:
                args["type_name"] = typ
                self.tool("add_variable", args)
            print(f"  + var {bp}.{name}")
        if "rep" in flags:
            self.tool("set_variable_replication", {"blueprint": ref(bp), "variable_name": name, "replication": "REPLICATED"})
        if "edit" in flags:
            self.tool("set_variable_instance_editable", {"blueprint": ref(bp), "variable_name": name, "instance_editable": True},
                      quiet=True)

    def add_params(self, graph, params, dispatcher=False):
        for p in params:
            pname, ptyp = p[0], p[1]
            is_in = not (len(p) > 2 and p[2] == "out")
            if isinstance(ptyp, tuple):
                self.tool("add_object_function_param", {"graph": graph, "param_name": pname, "object_class": cls(ptyp[1]),
                                                        "input_param": is_in})
            else:
                self.tool("add_function_param", {"graph": graph, "param_name": pname, "param_type": ptyp,
                                                 "input_param": is_in})

    def members(self, bp):
        spec = SPEC[bp]
        have = self.existing_vars(bp)
        for v in spec.get("vars", []):
            self.add_var(bp, v, have)
        graphs = self.graphs(bp)
        for dname, params in spec.get("dispatchers", {}).items():
            if dname not in graphs:
                g, err = self.tool("add_event_dispatcher", {"blueprint": ref(bp), "name": dname})
                if not err:
                    self.add_params(g, params, dispatcher=True)
                    print(f"  + dispatcher {bp}.{dname}")
        for fname, params in spec.get("fns", {}).items():
            if fname in graphs:
                continue
            g, err = self.tool("add_function_graph", {"blueprint": ref(bp), "graph_name": fname})
            if not err and params:  # params None = override of an inherited function (signature comes from parent)
                self.add_params(g, params)
            print(f"  + fn {bp}.{fname}")
        self.compile(bp)

    def compile(self, bp):
        rv, err = self.tool("compile_blueprint", {"blueprint": ref(bp)})
        print(f"  compile {bp}: {'ERROR ' + str(rv)[:600] if err else 'ok'}")
        return not err

    def write_graphs(self, bp):
        graphs = self.graphs(bp)
        ok = True
        for f in sorted(glob.glob(os.path.join(DSL_DIR, f"{bp}__*.dsl"))):
            gname = os.path.basename(f)[len(bp) + 2:-4]
            if gname not in graphs:
                print(f"  ! {bp}: no graph {gname}")
                ok = False
                continue
            code = open(f, encoding="utf-8").read()
            rv, err = self.tool("write_graph_dsl", {"graph": graphs[gname], "code": code}, quiet=True)
            print(f"  dsl {bp}.{gname}: {'ERROR ' + str(rv)[:900] if err else 'ok'}")
            ok = ok and not err
        return self.compile(bp) and ok


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    names = sys.argv[2:] or list(SPEC)
    b = Builder()
    if what in ("members", "all"):
        for bp in names:
            print(f"[members] {bp}")
            b.members(bp)
    if what in ("graphs", "all"):
        for bp in names:
            print(f"[graphs] {bp}")
            b.write_graphs(bp)


if __name__ == "__main__":
    main()
