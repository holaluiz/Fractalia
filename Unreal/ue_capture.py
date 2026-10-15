"""Capture the Unreal level viewport (through the MCP server) to a PNG.

Usage: python ue_capture.py out.png [x y z pitch yaw]
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

out = sys.argv[1]
args = {"annotations": {"gridSpacing": 0, "gridExtent": 0, "gridHeight": 0, "maxLabelDistance": 0,
                        "classFilter": {"refPath": "/Script/Engine.Actor"}, "maxLabels": 0}}
if len(sys.argv) >= 7:
    x, y, z, pitch, yaw = map(float, sys.argv[2:7])
    args["captureTransform"] = {"location": {"x": x, "y": y, "z": z},
                                "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0.0},
                                "scale": {"x": 1, "y": 1, "z": 1}}
c = Client()
c.initialize()
if len(sys.argv) >= 3 and sys.argv[2] == "--editor":  # whole editor window, e.g. while PIE is running
    res = c.call("call_tool", {"toolset_name": "EditorToolset.EditorAppToolset", "tool_name": "CaptureEditorImage",
                               "arguments": {}})
else:
    if "captureTransform" not in args:
        cam = c.call("call_tool", {"toolset_name": "EditorToolset.EditorAppToolset", "tool_name": "GetCameraTransform",
                                   "arguments": {}})
        args["captureTransform"] = json.loads(cam["content"][0]["text"])["returnValue"]
    res = c.call("call_tool", {"toolset_name": "EditorToolset.EditorAppToolset", "tool_name": "CaptureViewport",
                               "arguments": args})
data = None
for item in res.get("content", []):
    if item.get("type") == "image":
        data = item["data"]
    elif item.get("type") == "text":
        try:
            rv = json.loads(item["text"]).get("returnValue", {})
            data = data or rv.get("image", {}).get("data") or rv.get("data")
        except (json.JSONDecodeError, AttributeError):
            print(item["text"][:500])
if not data:
    print("no image in result:", json.dumps(res)[:800])
    sys.exit(1)
with open(out, "wb") as f:
    f.write(base64.b64decode(data))
print("saved", out)
