"""Write a DSL file into a Blueprint graph through MCP.  Usage: ue_write_dsl.py <graph_refPath> <file.dsl> [<bp_refPath>]"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
c = Client()
c.initialize()
code = open(sys.argv[2], encoding="utf-8").read()
res = c.call("call_tool", {"toolset_name": "editor_toolset.toolsets.blueprint.BlueprintTools",
                           "tool_name": "write_graph_dsl", "arguments": {"graph": {"refPath": sys.argv[1]}, "code": code}})
print("write:", res["content"][0]["text"][:1500], "[isError]" if res.get("isError") else "")
if len(sys.argv) > 3:
    res = c.call("call_tool", {"toolset_name": "editor_toolset.toolsets.blueprint.BlueprintTools",
                               "tool_name": "compile_blueprint", "arguments": {"blueprint": {"refPath": sys.argv[3]}}})
    print("compile:", res["content"][0]["text"][:1500], "[isError]" if res.get("isError") else "")
