"""Call one Unreal MCP toolset tool from the command line.

Usage:  python ue_tool.py <Toolset> <tool_name> '<json arguments>'
<Toolset> may be a short name (BlueprintTools, ObjectTools, ...) or the full toolset name.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client, text_of  # noqa: E402

SHORT = {
    "BlueprintTools": "editor_toolset.toolsets.blueprint.BlueprintTools",
    "ObjectTools": "editor_toolset.toolsets.object.ObjectTools",
    "AssetTools": "editor_toolset.toolsets.asset.AssetTools",
    "SceneTools": "editor_toolset.toolsets.scene.SceneTools",
    "ActorTools": "editor_toolset.toolsets.actor.ActorTools",
    "CurveTableTools": "editor_toolset.toolsets.curve_table.CurveTableTools",
    "DataTableTools": "editor_toolset.toolsets.data_table.DataTableTools",
    "DataAssetTools": "editor_toolset.toolsets.data_asset.DataAssetTools",
    "UMGToolSet": "UMGToolSet.UMGToolSet",
    "EditorApp": "EditorToolset.EditorAppToolset",
    "Logs": "EditorToolset.LogsToolset",
}


def call(client, toolset, tool, args):
    return client.call("call_tool", {"toolset_name": SHORT.get(toolset, toolset), "tool_name": tool,
                                     "arguments": args})


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    c = Client()
    c.initialize()
    if sys.argv[1] == "--describe":
        print(text_of(c.call("describe_toolset", {"toolset_name": SHORT.get(sys.argv[2], sys.argv[2])})))
        return
    args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    out = text_of(call(c, sys.argv[1], sys.argv[2], args))
    try:  # unwrap {"returnValue": "..."} so DSL / docs print with real newlines
        rv = json.loads(out.replace(" [isError]", "")).get("returnValue")
        if isinstance(rv, str):
            out = rv + (" [isError]" if out.endswith("[isError]") else "")
        elif rv is not None:
            out = json.dumps(rv, indent=1, ensure_ascii=False) + (" [isError]" if out.endswith("[isError]") else "")
    except (ValueError, AttributeError):
        pass
    print(out)


if __name__ == "__main__":
    main()
