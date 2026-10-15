"""Send Python code to a live Blender running the "MCP for Blender" add-on (port 9876).

Usage:  python live_send.py <file.py>      (runs the file inside the live Blender)
        python live_send.py -c "<code>"
"""
import json
import socket
import sys


def send(command, host="localhost", port=9876, timeout=600.0):
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.sendall(json.dumps(command).encode("utf-8"))
        buf = b""
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf += chunk
            try:
                return json.loads(buf.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    return {"status": "error", "message": "connection closed without a response"}


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "-c":
        code = sys.argv[2]
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            code = f.read()
    res = send({"type": "execute_code", "params": {"code": code}})
    if res.get("status") == "success":
        print(res.get("result", {}).get("result", ""))
    else:
        print(json.dumps(res, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
