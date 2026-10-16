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


SONDA = "import unreal; print('EDITOR' if unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem) else 'JOGO')"


def editor(ex):
    """
    O nó que é o EDITOR. Um jogo aberto do mesmo projeto (por exemplo, um cliente de rede -game do rede_testar.py)
    também responde à descoberta, com os mesmos dados; com mais de um nó, pergunta a cada um se tem os subsistemas do
    editor (15/10: chamadas do ue_py.py caíram no cliente de teste e falharam).
    """
    nos = list(ex.remote_nodes)
    if len(nos) == 1:
        return nos[0]["node_id"]
    for no in nos:
        ex.open_command_connection(no["node_id"])
        try:
            res = ex.run_command(SONDA, unattended=True, exec_mode=rx.MODE_EXEC_STATEMENT)
        finally:
            ex.close_command_connection()
        if any("EDITOR" in linha.get("output", "") for linha in res.get("output", [])):
            return no["node_id"]
    raise RuntimeError("nenhum dos processos da Unreal que responderam é o editor")


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
        time.sleep(1.5)  # dá tempo de os outros processos (clientes de teste) também responderem
        ex.open_command_connection(editor(ex))
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
