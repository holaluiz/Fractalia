import json, struct, sys
for path in sys.argv[1:]:
    f = open(path, "rb"); f.read(12); n, t = struct.unpack("<I4s", f.read(8)); g = json.loads(f.read(n))
    mn = [1e9]*3; mx = [-1e9]*3
    for m in g["meshes"]:
        for p in m["primitives"]:
            a = g["accessors"][p["attributes"]["POSITION"]]
            mn = [min(x, y) for x, y in zip(mn, a["min"])]; mx = [max(x, y) for x, y in zip(mx, a["max"])]
    print(path.split("\\")[-1], "height(m)=%.2f width=%.2f depth=%.2f" % (mx[1]-mn[1], mx[0]-mn[0], mx[2]-mn[2]), "| meshes:", [m["name"] for m in g["meshes"]], "| images:", [i.get("name") or i.get("uri") for i in g.get("images", [])][:6])
