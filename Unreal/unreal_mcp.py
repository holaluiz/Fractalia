"""Minimal client for the Unreal Editor MCP server (streamable HTTP, JSON-RPC).

Usage:  python unreal_mcp.py calls.json
calls.json: [{"tool": "list_toolsets", "arguments": {}},
             {"tool": "call_tool", "arguments": {"toolset_name": "...", "tool_name": "...", "arguments": {...}}}]
Prints each result's text content.
"""
import json
import sys
import urllib.request

URL = "http://127.0.0.1:8000/mcp"


class Client:
    def __init__(self, url=URL):
        self.url = url
        self.session = None
        self.next_id = 0

    def _post(self, payload, timeout=1800):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            self.session = r.headers.get("Mcp-Session-Id") or self.session
            body = r.read().decode("utf-8")
            ctype = r.headers.get("Content-Type", "")
        if not body.strip():
            return None
        if "text/event-stream" in ctype:
            msgs = [json.loads(line[5:].strip()) for line in body.splitlines() if line.startswith("data:")]
            return next((m for m in reversed(msgs) if "id" in m), msgs[-1] if msgs else None)
        return json.loads(body)

    def request(self, method, params=None):
        self.next_id += 1
        res = self._post({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params or {}})
        if res and "error" in res:
            raise RuntimeError(json.dumps(res["error"]))
        return res.get("result") if res else None

    def initialize(self):
        r = self.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                        "clientInfo": {"name": "nexus-royale-cli", "version": "1.0"}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return r

    def call(self, tool, arguments=None):
        return self.request("tools/call", {"name": tool, "arguments": arguments or {}})


def text_of(result):
    if not result:
        return ""
    out = []
    for c in result.get("content", []):
        out.append(c.get("text", json.dumps(c)))
    if result.get("structuredContent") and not out:
        out.append(json.dumps(result["structuredContent"], indent=1))
    flag = " [isError]" if result.get("isError") else ""
    return "\n".join(out) + flag


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with open(sys.argv[1], encoding="utf-8") as f:
        calls = json.load(f)
    c = Client()
    info = c.initialize()
    print("# server:", (info or {}).get("serverInfo"))
    for call in calls:
        print(f"## {call['tool']} {json.dumps(call.get('arguments', {}))[:200]}")
        try:
            print(text_of(c.call(call["tool"], call.get("arguments"))))
        except Exception as e:  # keep going so one failure doesn't hide the rest
            print("ERROR:", e)


if __name__ == "__main__":
    main()
