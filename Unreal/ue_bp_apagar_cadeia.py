"""Apaga a cadeia de nós ligada a um evento de um grafo de Blueprint (o write_graph_dsl não apaga: um evento escrito
com corpo vazio é ignorado e o corpo antigo continua lá).

Uso (editor aberto):
    python Unreal/ue_bp_apagar_cadeia.py <grafo refPath> <título do evento> [--manter-evento] [--sim]
Sem --sim só lista o que apagaria. --manter-evento apaga o corpo e deixa o nó do evento (útil para o BeginPlay).
Exemplo:
    MSYS_NO_PATHCONV=1 python Unreal/ue_bp_apagar_cadeia.py "/Game/.../GM_NexusRoyale.GM_NexusRoyale:EventGraph" "Event BeginPlay" --manter-evento --sim
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unreal_mcp import Client  # noqa: E402

BPT = "editor_toolset.toolsets.blueprint.BlueprintTools"


def chamar(c, ferramenta, args):
    r = c.call("call_tool", {"toolset_name": BPT, "tool_name": ferramenta, "arguments": args})
    texto = r["content"][0]["text"] if r and r.get("content") else ""
    if r.get("isError"):
        raise RuntimeError(f"{ferramenta}: {texto[:400]}")
    try:
        return json.loads(texto).get("returnValue")
    except json.JSONDecodeError:
        return texto


def titulo(info):
    return info.get("title") or info.get("nodeTitle") or info.get("name") or "?"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    grafo, alvo = args[0], args[1]
    manter, sim = "--manter-evento" in sys.argv, "--sim" in sys.argv
    c = Client()
    c.initialize()
    nos = chamar(c, "find_nodes", {"graph": {"refPath": grafo}, "title": alvo, "entry_points_only": True})
    if not nos:
        print(f"nenhum evento com o título {alvo!r}")
        return
    evento = nos[0]
    ref_evento = evento["refPath"] if isinstance(evento, dict) else evento
    cadeia = chamar(c, "get_connected_subgraph", {"node": {"refPath": ref_evento}})
    alvos = []
    for info in cadeia:
        ref = info.get("node", {}).get("refPath") if isinstance(info.get("node"), dict) else info.get("refPath")
        ref = ref or info.get("path") or info.get("node")
        if manter and ref == ref_evento:
            continue
        alvos.append((ref, titulo(info)))
    print(f"evento: {ref_evento}")
    for ref, t in alvos:
        print(f"  {'apagando' if sim else 'apagaria'}: {t}  ({ref})")
        if sim:
            chamar(c, "delete_node", {"node": {"refPath": ref}})
    print(f"{len(alvos)} nós {'apagados' if sim else 'listados'}")


if __name__ == "__main__":
    main()
