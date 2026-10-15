"""Run Python inside the open Unreal Editor (Python plugin "remote execution").

Usage:  python ue_py.py <script.py>        runs the file (as __main__) inside the editor
        python ue_py.py -c "<statement>"
Uses the engine's own remote_execution.py client.
"""
import os
import sys
import time

ENGINE_PY = r"D:\Epic Games\UE_5.8\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python"
sys.path.append(ENGINE_PY)
import remote_execution as rx  # noqa: E402


def run(command, mode=rx.MODE_EXEC_FILE, wait=20.0):
    cfg = rx.RemoteExecutionConfig()
    cfg.multicast_bind_address = "127.0.0.1"
    ex = rx.RemoteExecution(cfg)
    ex.start()
    try:
        deadline = time.time() + wait
        while not ex.remote_nodes and time.time() < deadline:
            time.sleep(0.25)
        if not ex.remote_nodes:
            raise RuntimeError("no Unreal Editor answered the remote-execution discovery")
        ex.open_command_connection(ex.remote_nodes[0]["node_id"])
        return ex.run_command(command, unattended=True, exec_mode=mode)
    finally:
        ex.stop()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "-c":
        res = run(sys.argv[2])
    else:
        path = os.path.abspath(sys.argv[1]).replace("\\", "/")
        stmt = (f"exec(compile(open(r'{path}', encoding='utf-8').read(), r'{path}', 'exec'), "
                f"{{'__name__': '__main__', '__file__': r'{path}'}})")
        res = run(stmt)
    for line in res.get("output", []):
        print(f"[{line.get('type')}] {line.get('output', '').rstrip()}")
    if res.get("result") not in (None, "None", ""):
        print("result:", res.get("result"))
    print("SUCCESS" if res.get("success") else "FAILED")
    sys.exit(0 if res.get("success") else 1)


if __name__ == "__main__":
    main()
