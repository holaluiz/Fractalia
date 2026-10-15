"""Print pin names/types of Blueprint node type ids via MCP.  Usage: ue_node_pins.py <graph_refPath> <type_id> ..."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
c = Client()
c.initialize()
graph = sys.argv[1]
for tid in sys.argv[2:]:
    res = c.call("call_tool", {"toolset_name": "editor_toolset.toolsets.blueprint.BlueprintTools",
                               "tool_name": "get_node_type_pins", "arguments": {"graph": {"refPath": graph}, "type_id": tid}})
    txt = res["content"][0]["text"]
    try:
        rv = json.loads(txt)["returnValue"]
    except (json.JSONDecodeError, KeyError):
        print(f"[{tid}] {txt[:300]}")
        continue

    def fmt(pins):
        return ", ".join(f"{p.get('name')}:{p.get('type_id', p.get('type', ''))}" for p in pins)

    if isinstance(rv, dict):
        print(f"[{tid}]\n   IN : {fmt(rv.get('input_pins', []))}\n   OUT: {fmt(rv.get('output_pins', []))}")
    else:
        print(f"[{tid}] {json.dumps(rv)[:400]}")
