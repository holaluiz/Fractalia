"""Compact summary of Unreal MCP toolsets: tool name, first description line, parameter names.

Usage: python ue_describe.py <toolset> [<toolset> ...]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
c = Client()
c.initialize()
for ts in sys.argv[1:]:
    res = c.call("describe_toolset", {"toolset_name": ts})
    text = res["content"][0]["text"]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"== {ts}: {text[:300]}")
        continue
    print(f"== {data.get('name', ts)} ({len(data.get('tools', []))} tools)")
    for t in data.get("tools", []):
        props = t.get("inputSchema", {}).get("properties", {})
        req = set(t.get("inputSchema", {}).get("required", []))
        params = ", ".join(f"{k}{'' if k in req else '?'}" for k in props)
        desc = (t.get("description") or "").strip().splitlines()
        print(f"  - {t['name'].split('.')[-1]}({params}) :: {desc[0][:140] if desc else ''}")
