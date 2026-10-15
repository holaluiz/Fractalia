"""BR stage 1, step 3: wire Enhanced Input events of BP_HeroBase to its handler functions (via MCP).

The DSL cannot declare input events, so the event and call nodes are created and connected here.
IA_Jump overrides the template's jump binding (Started -> HandleJumpStarted, Completed -> HandleJumpCompleted);
IA_Interact Started -> HandleInteract. Idempotent: existing input nodes are deleted and recreated.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

BPT = "editor_toolset.toolsets.blueprint.BlueprintTools"
BP = {"refPath": "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase.BP_HeroBase"}
GRAPH = {"refPath": "/Game/NexusRoyale/Blueprints/Core/BP_HeroBase.BP_HeroBase:EventGraph"}
WIRING = [  # (input event type id, [(exec output pin, handler function)])
    ("Input|EnhancedActionEvents|IA_Jump", [("Started", "HandleJumpStarted"), ("Completed", "HandleJumpCompleted")]),
    ("Input|EnhancedActionEvents|IA_Interact", [("Started", "HandleInteract")]),
]

c = Client()
c.initialize()


def tool(name, args):
    res = c.call("call_tool", {"toolset_name": BPT, "tool_name": name, "arguments": args})
    txt = res["content"][0]["text"]
    if res.get("isError"):
        raise RuntimeError(f"{name}: {txt[:600]}")
    return json.loads(txt).get("returnValue")


def info(node):
    return tool("get_node_infos", {"nodes": [node]})[0]


def pin_id(node, nfo, pin_name, direction):
    pins = nfo["output_pins" if direction == "EGPD_Output" else "input_pins"]
    for p in pins:
        if p.get("name") == pin_name:
            return p["pin_id"]
    raise KeyError(f"pin {pin_name} ({direction}) not in {[p.get('name') for p in pins]}")


# remove previous input nodes and handler calls so reruns stay clean
for type_id, outs in WIRING:
    action = type_id.rsplit("|", 1)[1]
    for n in tool("find_nodes", {"graph": GRAPH, "title": action}) or []:
        tool("delete_node", {"node": n})
    for _, fn in outs:
        for n in tool("find_nodes", {"graph": GRAPH, "title": fn}) or []:
            tool("delete_node", {"node": n})

y = 900
for type_id, outs in WIRING:
    ev = tool("create_node", {"graph": GRAPH, "type_id": type_id, "pos": {"x": -400, "y": y}})
    ev_info = info(ev)
    print(type_id, "outputs:", [p.get("name") for p in ev_info["output_pins"]])
    for k, (out_pin, fn) in enumerate(outs):
        call = tool("create_node", {"graph": GRAPH, "type_id": f"CallFunction|{fn}", "pos": {"x": 0, "y": y + k * 160}})
        call_info = info(call)
        tool("connect_pins", {"output_pin": pin_id(ev, ev_info, out_pin, "EGPD_Output"),
                              "input_pin": pin_id(call, call_info, "execute", "EGPD_Input")})
        print(f"  {out_pin} -> {fn}")
    y += 400

print("compile:", tool("compile_blueprint", {"blueprint": BP}))
