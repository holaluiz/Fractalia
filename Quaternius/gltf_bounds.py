"""Print the bounding box (meters, glTF Y-up -> reported as X width, Y depth, Z height) of every glTF in a folder.

Usage: python gltf_bounds.py <folder> [name_filter]
"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
folder = sys.argv[1]
flt = sys.argv[2].lower() if len(sys.argv) > 2 else ""
for path in sorted(glob.glob(os.path.join(glob.escape(folder), "**", "*.gltf"), recursive=True)):
    name = os.path.splitext(os.path.basename(path))[0]
    if flt and flt not in name.lower():
        continue
    g = json.load(open(path, encoding="utf-8"))
    mn = [1e9] * 3
    mx = [-1e9] * 3
    for mesh in g.get("meshes", []):
        for prim in mesh["primitives"]:
            acc = g["accessors"][prim["attributes"]["POSITION"]]
            mn = [min(a, b) for a, b in zip(mn, acc["min"])]
            mx = [max(a, b) for a, b in zip(mx, acc["max"])]
    # node transform of the mesh node (translation/scale) if any
    node = next((n for n in g.get("nodes", []) if "mesh" in n), {})
    s = node.get("scale", [1, 1, 1])
    # glTF: +Y up, -Z forward  ->  report X(width) Z(depth) Y(height)
    w, d, h = (mx[0] - mn[0]) * s[0], (mx[2] - mn[2]) * s[2], (mx[1] - mn[1]) * s[1]
    print(f"{name:42s} size(m) w={w:5.2f} d={d:5.2f} h={h:5.2f} | min x={mn[0]:+.2f} y={mn[1]:+.2f} z={mn[2]:+.2f} "
          f"max x={mx[0]:+.2f} y={mx[1]:+.2f} z={mx[2]:+.2f} | node_t={node.get('translation')}")
