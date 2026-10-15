"""Print skeleton joints, meshes and animation names of glTF/GLB files (reads JSON only)."""
import json
import struct
import sys


def load_json(path):
    if path.lower().endswith(".glb"):
        with open(path, "rb") as f:
            magic, version, length = struct.unpack("<4sII", f.read(12))
            chunk_len, chunk_type = struct.unpack("<I4s", f.read(8))
            return json.loads(f.read(chunk_len).decode("utf-8"))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


sys.stdout.reconfigure(encoding="utf-8")
for path in sys.argv[1:]:
    g = load_json(path)
    nodes = g.get("nodes", [])
    print("=" * 8, path.split("\\")[-1])
    print("meshes:", [m.get("name") for m in g.get("meshes", [])])
    for s in g.get("skins", []):
        joints = [nodes[j].get("name") for j in s["joints"]]
        print(f"skin '{s.get('name')}': {len(joints)} joints -> {joints[:60]}")
    anims = [a.get("name") for a in g.get("animations", [])]
    print(f"animations ({len(anims)}):", anims)
