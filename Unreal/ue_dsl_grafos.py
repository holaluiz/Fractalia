"""Grava só alguns grafos de um Blueprint a partir das DSLs de Unreal/Blueprints, compila e lê de volta.
O `ue_br_build.py graphs <BP>` regrava todos os grafos do BP; este grava só os pedidos.

Uso (editor aberto, fora do PIE):
    python Unreal/ue_dsl_grafos.py BP_HeroBase StormTick SetInteractable
    python Unreal/ue_dsl_grafos.py BP_HeroBase EventGraph=caminho/so_um_evento.dsl
Sem "=arquivo", usa Unreal/Blueprints/<BP>__<grafo>.dsl. Gravar um grafo substitui só os eventos e funções que a
DSL traz (os outros eventos do EventGraph ficam). Com --ler, imprime a DSL lida de volta (confira os ifs: a gravação
diz "ok" mesmo quando some um nó; seção 5 do AGENTS.md).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ue_br_build import DSL_DIR, Builder  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ler = "--ler" in sys.argv
    bp, pedidos = args[0], args[1:]
    b = Builder()
    graphs = b.graphs(bp)
    ok = True
    for pedido in pedidos:
        nome, _, arquivo = pedido.partition("=")
        arquivo = arquivo or os.path.join(DSL_DIR, f"{bp}__{nome}.dsl")
        if nome not in graphs:
            print(f"  ! {bp}: não existe o grafo {nome} (crie com ue_br_build.py members {bp})")
            ok = False
            continue
        code = open(arquivo, encoding="utf-8").read()
        rv, err = b.tool("write_graph_dsl", {"graph": graphs[nome], "code": code}, quiet=True)
        print(f"  dsl {bp}.{nome}: {'ERRO ' + str(rv)[:900] if err else 'ok'}")
        ok = ok and not err
        if ler:
            rv, err = b.tool("read_graph_dsl", {"graph": graphs[nome]}, quiet=True)
            print(rv if not err else f"  (não li: {rv})")
    ok = b.compile(bp) and ok
    print("tudo ok" if ok else "COM ERROS")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
