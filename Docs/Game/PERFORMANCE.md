# Desempenho

**Regra:** medir antes de otimizar. Toda otimização entra aqui com o número de antes e de depois.

---

## 1. Máquina de referência

O PC de desenvolvimento é o "mínimo" realista: Windows 10, **Radeon RX 570 (4 GB)**, 16 GB de RAM, SSD de 128 GB quase
cheio (C:) e **HD mecânico** (D:, onde ficam a Unreal e o projeto). Se roda bem aqui, roda na maioria dos PCs.

## 2. Medições existentes

| Data | Situação | Resultado |
|---|---|---|
| 15/10 12:47 | PIE no `L_Island`, viewport 1142×730, **com Lumen e sombras virtuais** | 22 FPS; 34,8 ms de GPU (Lumen ~35 ms no compute assíncrono, sombras virtuais 7,6 ms, Nanite 4,3 ms); render targets 3,1 GB; o editor transborda 680 MB da memória de vídeo para a RAM |
| 15/10 12:52 | Config trocada: sem Lumen, sem sombras virtuais, sem distance fields; Nanite desligado nas malhas low-poly | **"Depois" não medido** |

Ferramenta: `Unreal/pie_medir.py` (FPSChart, ProfileGPU e memória no log).

## 3. Orçamentos (proposta)

| Item | Cliente (RX 570, 1080p, qualidade média) | Servidor (host) |
|---|---|---|
| Quadro | 60 FPS (16,6 ms) no jogo empacotado | tick de 30 Hz com 20 jogadores + ~70 creeps |
| Game thread | ≤ 8 ms | ≤ 10 ms com o servidor junto (host) |
| GPU | ≤ 14 ms | — |
| Memória de vídeo | ≤ 3 GB | — |
| Draw calls | ≤ 2.000 | — |
| Banda por cliente | — | ≤ 30 KB/s média, picos ≤ 80 KB/s |
| Atores replicados | — | ≤ 400 ativos |

## 4. O que já se sabe que pesa

- Lumen e sombras virtuais (desligados).
- **Memória de vídeo do editor:** o 2º ou 3º PIE derruba o editor (AGENTS.md §5).
- **Compilação no HD lento:** o `cl.exe` lendo o PCH por falta de página (truque do cache no AGENTS.md §5).
- Materiais com nó Custom precisam compilar no SM6 (jogo empacotado).

## 5. Plano de medição

| Quando | O quê |
|---|---|
| M0.5 | Medir o "depois" no jogo empacotado (FPS, GPU, memória) |
| M5 | Custo de um combate com 4 jogadores (habilidades, projéteis) |
| M18 | **Teste de 20**: host + clientes sem render + bots; servidor (game thread, rede com Network Insights), um cliente com render (FPS) |
| M19 | Materiais pintados: complexidade de shader, custo do pós-processamento |
| M24 | Passe geral: LODs, HLOD (se World Partition), culling, instancing, Niagara |

Ferramentas: `stat unit`, `stat game`, `stat net`, `ProfileGPU`, Unreal Insights (`-trace=cpu,gpu,frame,net`),
`memreport`, Network Insights.

## 6. Diretrizes

- Malhas do cenário repetidas → instâncias (HISM/ISM); vegetação pelo PCG ou foliage.
- Nanite só onde ajuda (malhas densas); as Quaternius são low-poly e ficaram sem.
- Niagara: sistemas pequenos, com escalabilidade e limite de partículas; desligar efeitos longe.
- IA: acampamentos dormem sem herói por perto; `Think` em intervalo, não por tick.
- Rede: frequência por tipo de ator e dormência (NETWORKING_ARCHITECTURE.md §4).
- Pool de objetos só quando o perfil mostrar custo de criar/destruir (projéteis num combate de 20).
