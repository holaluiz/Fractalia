# Nexus Royale

Battle royale solo de magias com progressão de MOBA, na Unreal Engine 5.8 com assets da Quaternius.
O design completo está em [Design/GDD.md](Design/GDD.md) (v2).

**IAs e quem for continuar o trabalho:** o estado atual, as regras, o ambiente e o diário de sessões
estão em [AGENTS.md](AGENTS.md).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `Design/` | Documento de design (heróis, habilidades, sistemas, arquitetura na Unreal) |
| `Blender/NexusRoyale_Assets.blend` | Todos os assets (cena `NexusRoyale`) |
| `Blender/scripts/` | Geração procedural: `build_all.py` gera heróis, props e mapa, exporta FBX e renderiza previews |
| `Export/FBX/{Heroes,Props,Map}` | 25 FBX prontos para a Unreal (5 Skeletal Mesh, 20 Static Mesh com colisão UCX) |
| `Export/map_layout.json` | 631 posições de gameplay (Nexus, torres, baús, árvores…) já em cm da Unreal |
| `Export/Previews/` | Renders de conferência |
| `Unreal/import_nexus_assets.py` | Script Python do editor: importa os FBX e monta o nível `L_Island` |

## Regenerar os assets

```bash
"D:/blender/blender.exe" --background --factory-startup --python "D:/meus documentos/Fortnite/Blender/scripts/build_all.py"
```

Tudo é determinístico; mudar um script e rodar de novo atualiza `.blend`, FBX, layout e previews.

## Blender ao vivo

O add-on **MCP for Blender** (Siddharth Ahuja) precisa estar conectado (barra lateral N → MCP for Blender →
Connect to Claude). `Blender/scripts/live_send.py` envia um script para o Blender aberto:

```bash
"D:/blender/5.2/python/bin/python.exe" -I "D:/meus documentos/Fortnite/Blender/scripts/live_send.py" "D:/meus documentos/Fortnite/Blender/scripts/live_view_heroes.py"
```

## Unreal

O projeto está em `Unreal/NexusRoyale` (UE 5.8.3, em `D:\Epic Games\UE_5.8`). O servidor MCP sobe com o editor
em `http://127.0.0.1:8000/mcp`, configurado no `.mcp.json` da raiz. Os scripts de controle e o estado do trabalho
estão em [AGENTS.md](AGENTS.md).

> As seções acima sobre Blender e `Export/` descrevem os assets da v1 (heróis fixos, construção, torres). No GDD v2
> eles foram substituídos pela Quaternius; veja a seção 16.1 do GDD.
