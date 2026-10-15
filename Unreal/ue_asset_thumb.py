"""Render an asset thumbnail through the MCP server to a PNG.  Usage: ue_asset_thumb.py <asset_path> <out.png>"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

c = Client()
c.initialize()
res = c.call("call_tool", {"toolset_name": "EditorToolset.EditorAppToolset", "tool_name": "CaptureAssetImage",
                           "arguments": {"assetPath": sys.argv[1]}})
txt = res["content"][0].get("text", "")
rv = json.loads(txt).get("returnValue", {}) if txt.startswith("{") else {}
data = rv.get("data") or (res["content"][0].get("data") if res["content"][0].get("type") == "image" else None)
if not data:
    print("no image:", txt[:300])
    sys.exit(1)
open(sys.argv[2], "wb").write(base64.b64decode(data))
print("saved", sys.argv[2])
