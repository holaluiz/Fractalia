"""Hook do Claude Code: registra o que acontece no projeto para as outras IAs.

PostToolUse: acrescenta uma linha em Registro/atividade.md para cada mudança (arquivo do projeto
escrito/editado, comando que mexe na Unreal ou no Blender, chamada ao MCP da Unreal) e guarda,
por sessão, o que ainda não foi registrado no AGENTS.md.
Stop: se a sessão mudou o projeto e não atualizou o AGENTS.md depois, pede o registro (uma vez
por parada; nunca entra em loop).
Qualquer erro é engolido: o hook nunca pode atrapalhar a sessão.
"""
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, "Registro", "atividade.md")
STATE_DIR = os.path.join(ROOT, ".claude", "hooks", "state")

HEADER = """# Registro automático de atividade

Uma linha por mudança no projeto, a mais recente no fim. As sessões do Claude Code escrevem aqui
sozinhas (hook em `.claude/hooks/registro.py`). **Outras IAs:** acrescentem as suas linhas à mão,
no mesmo formato. O resumo do que importa (estado atual e diário) fica no [AGENTS.md](../AGENTS.md).

Formato: `- AAAA-MM-DD HH:MM · <IA ou sessão> · <ação> · <o quê>`

"""

UNREAL_OR_BLENDER = re.compile(r"ue_\w+\.py|unreal_mcp\.py|import_nexus_assets\.py|blender|live_send\.py", re.I)
SCRIPT_NAME = re.compile(r"(ue_\w+|unreal_mcp|import_nexus_assets|live_send|\w+)\.py", re.I)
READ_ONLY_SCRIPT = re.compile(r"probe|capture|find_nodes|describe|ping|inspect|check|thumb|bounds|culture", re.I)
READ_ONLY_MCP = re.compile(r"^(list|describe|get|find|search|capture|read|query|inspect)", re.I)
UE_TOOL_CALL = re.compile(r"ue_tool\.py\s+\S+\s+(\w+)", re.I)  # ue_tool.py <Toolset> <ferramenta>
UE_TOOL_ANY = re.compile(r"ue_tool\.py", re.I)
RUNNERS = {"ue_py", "unreal_mcp"}
FILE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SHELL_TOOLS = ("Bash", "PowerShell")


def rel_in_project(path):
    """Caminho relativo ao projeto, ou None se o arquivo estiver fora dele."""
    if not path:
        return None
    full = os.path.normcase(os.path.abspath(path))
    root = os.path.normcase(ROOT)
    if not full.startswith(root + os.sep):
        return None
    return os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")


def one_line(text, limit):
    text = " ".join(str(text).split()).replace("`", "'")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def describe(data):
    """(ação, o quê, conta_como_pendente) ou None quando não é uma mudança do projeto."""
    tool = data.get("tool_name", "")
    inp = data.get("tool_input") or {}

    if tool in FILE_TOOLS:
        rel = rel_in_project(inp.get("file_path") or inp.get("notebook_path"))
        if not rel or rel == "Registro/atividade.md" or rel.startswith(".claude/hooks/state/"):
            return None
        pending = rel not in ("AGENTS.md", "CLAUDE.md")
        return tool, f"`{rel}`", pending

    if tool in SHELL_TOOLS:
        cmd = inp.get("command") or ""
        if not UNREAL_OR_BLENDER.search(cmd):
            return None
        scripts = [s for s in SCRIPT_NAME.findall(cmd)]
        targets = [s for s in scripts if s.lower() not in RUNNERS]
        scripts = targets or scripts  # ue_py.py só executa outro script: decide pelo script executado
        mcp_calls = UE_TOOL_CALL.findall(cmd)
        if mcp_calls and len(mcp_calls) == len(UE_TOOL_ANY.findall(cmd)) \
                and all(READ_ONLY_MCP.search(t) for t in mcp_calls) \
                and all(READ_ONLY_SCRIPT.search(s) or s.lower() == "ue_tool" for s in scripts):
            return None  # só leitura pelo ue_tool.py (read_graph_dsl, list_…)
        if scripts and all(READ_ONLY_SCRIPT.search(s) for s in scripts):
            return None  # só leitura (probe, captura, busca de nós…)
        what = one_line(inp.get("description") or "", 120)
        what = f"{what} — `{one_line(cmd, 160)}`" if what else f"`{one_line(cmd, 200)}`"
        return tool, what, True

    if tool.startswith("mcp__unreal-mcp__"):
        outer = tool[len("mcp__unreal-mcp__"):]
        inner = inp.get("tool_name") or ""
        if READ_ONLY_MCP.search(inner or outer):
            return None
        toolset = (inp.get("toolset_name") or "").split(".")[-1]
        name = f"{toolset}.{inner}" if inner else outer
        return "MCP Unreal", f"`{name}`", True

    return None


def state_path(session):
    safe = re.sub(r"[^\w-]", "_", session or "sem-sessao")
    return os.path.join(STATE_DIR, f"{safe}.json")


def load_state(session):
    try:
        with open(state_path(session), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"pending": []}


def save_state(session, state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(state_path(session), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def append_log(line):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    new = not os.path.exists(LOG)
    with open(LOG, "a", encoding="utf-8") as f:
        if new:
            f.write(HEADER)
        f.write(line + "\n")


def post_tool_use(data):
    found = describe(data)
    if not found:
        return
    action, what, pending = found
    session = data.get("session_id") or ""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_log(f"- {stamp} · Claude Code {session[:8]} · {action} · {what}")

    state = load_state(session)
    if what == "`AGENTS.md`":
        state["pending"] = []
    elif pending and what not in state["pending"]:
        state["pending"].append(what)
    save_state(session, state)


def stop(data):
    if data.get("stop_hook_active"):
        return
    pending = load_state(data.get("session_id") or "").get("pending") or []
    if not pending:
        return
    shown = pending[:15] + ([f"… e mais {len(pending) - 15}"] if len(pending) > 15 else [])
    reason = (
        "Registro para outras IAs: esta sessão mudou o projeto e ainda não atualizou o AGENTS.md. "
        "Atualize a seção 3 (Estado atual) se o estado mudou e acrescente uma entrada no fim da "
        "seção 9 (Diário), dizendo o que ficou sem verificar. Mudança pequena: uma linha basta. "
        "Itens pendentes: " + "; ".join(shown)
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    data = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    event = data.get("hook_event_name")
    if event == "PostToolUse":
        post_tool_use(data)
    elif event == "Stop":
        stop(data)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
