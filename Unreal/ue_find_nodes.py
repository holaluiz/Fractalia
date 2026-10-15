"""Find Blueprint node type ids through MCP.  Usage: ue_find_nodes.py <graph_refPath> <filter> [<filter> ...]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
c = Client()
c.initialize()
graph = sys.argv[1]
for flt in sys.argv[2:]:
    res = c.call("call_tool", {"toolset_name": "editor_toolset.toolsets.blueprint.BlueprintTools",
                               "tool_name": "find_node_types",
                               "arguments": {"graph": {"refPath": graph}, "type_id_filter": flt, "context_pins": []}})
    txt = res["content"][0]["text"]
    try:
        ids = json.loads(txt)["returnValue"]
    except (json.JSONDecodeError, KeyError):
        print(f"[{flt}] {txt[:300]}")
        continue
    ids = [i if isinstance(i, str) else json.dumps(i) for i in ids]
    print(f"[{flt}] ({len(ids)}) " + " | ".join(ids[:8]))
