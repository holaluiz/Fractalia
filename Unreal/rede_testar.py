"""Abre clientes de rede SEM RENDER (-nullrhi) que entram num servidor, para testar replicação neste PC fraco.

A RX 570 não aguenta dois PIEs com render (Docs/Game/TEST_PLAN.md §2). Um cliente -nullrhi não usa a placa de vídeo:
roda o jogo, conecta, replica e grava o próprio log, que é onde se confere o que chegou ao cliente
("Partida (cliente): fase ...", "morreu (visto no cliente ...)").

Uso:
    python -I Unreal/rede_testar.py abrir [N] [endereço]     abre N clientes (padrão 1) em 127.0.0.1:17777 (PIE listen)
    python -I Unreal/rede_testar.py logs [filtro]            imprime as linhas do log de cada cliente (padrão: LogNexus)
    python -I Unreal/rede_testar.py fechar                   fecha os clientes abertos por este script
Os logs ficam em Unreal/NexusRoyale/Saved/Logs/ClienteRede<N>.log; os PIDs em Saved/rede_testar_pids.txt.
O servidor pode ser o PIE em "Play As Listen Server" (porta 17777) ou um jogo aberto com ?listen (porta 7777).
"""
import os
import subprocess
import sys

UE = r"D:\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
RAIZ = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(RAIZ, "NexusRoyale", "NexusRoyale.uproject")
LOGS = os.path.join(RAIZ, "NexusRoyale", "Saved", "Logs")
PIDS = os.path.join(RAIZ, "NexusRoyale", "Saved", "rede_testar_pids.txt")


def abrir(n, endereco):
    os.makedirs(LOGS, exist_ok=True)
    pids = []
    for i in range(1, n + 1):
        log = os.path.join(LOGS, f"ClienteRede{i}.log")
        if os.path.exists(log):
            os.remove(log)
        # Sem Python remoto no cliente: senão ele responde à descoberta do ue_py.py igual ao editor (15/10).
        args = [UE, PROJETO, endereco, "-game", "-nullrhi", "-nosound", "-unattended", "-nosplash", "-log",
                f"-abslog={log}", "-culture=pt-BR",
                "-ini:Engine:[/Script/PythonScriptPlugin.PythonScriptPluginSettings]:bRemoteExecution=False"]
        p = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
        pids.append(p.pid)
        print(f"cliente {i}: pid {p.pid}, log {log}")
    with open(PIDS, "a", encoding="utf-8") as f:
        f.writelines(f"{pid}\n" for pid in pids)


def logs(filtro):
    for nome in sorted(os.listdir(LOGS)):
        if nome.startswith("ClienteRede") and nome.endswith(".log"):
            print(f"===== {nome}")
            with open(os.path.join(LOGS, nome), encoding="utf-8", errors="replace") as f:
                for linha in f:
                    if filtro in linha:
                        print(linha.rstrip()[:240])


def fechar():
    if not os.path.exists(PIDS):
        print("nenhum cliente registrado")
        return
    for pid in open(PIDS, encoding="utf-8").read().split():
        r = subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True, text=True)
        print(pid, (r.stdout or r.stderr).strip()[:120])
    os.remove(PIDS)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    acao = sys.argv[1] if len(sys.argv) > 1 else "abrir"
    if acao == "abrir":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        abrir(n, sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1:17777")
    elif acao == "logs":
        logs(sys.argv[2] if len(sys.argv) > 2 else "LogNexus")
    elif acao == "fechar":
        fechar()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
