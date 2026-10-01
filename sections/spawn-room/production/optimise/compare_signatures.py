"""python compare_signatures.py before.json after.json  -> exit 1 on any difference beyond tolerance"""
import json
import sys

a, b = (json.load(open(x)) for x in sys.argv[1:3])
bad = []
if a["triangles"] != b["triangles"]:
    bad.append("triangles %d -> %d" % (a["triangles"], b["triangles"]))
for i in (0, 1):
    for k in range(3):
        if abs(a["bbox"][i][k] - b["bbox"][i][k]) > 1e-4:
            bad.append("scene bbox %s" % (a["bbox"], ))
            break
import numpy as np

va = np.load(sys.argv[1].replace(".json", ".verts.npy"))
vb = np.load(sys.argv[2].replace(".json", ".verts.npy"))


def cells(v):
    return np.floor(v.astype(np.float64) / 0.001).astype(np.int64)


def covered(src, dst):
    """Every vertex of src has a vertex of dst in its own or a neighbouring 1 mm cell (so within about 2 mm)."""
    have = set(map(tuple, cells(dst)))
    missing = 0
    for c in cells(src):
        t = tuple(c)
        if t in have:
            continue
        if any((t[0] + i, t[1] + j, t[2] + k) in have for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)):
            continue
        missing += 1
    return missing


m1, m2 = covered(va, vb), covered(vb, va)
if m1 or m2:
    bad.append("world vertex sets differ: %d original vertices without a match, %d new vertices without a match" % (m1, m2))
keys = set(a["area_by_material"]) | set(b["area_by_material"])
worst = 0.0
for k in sorted(keys):
    x, y = a["area_by_material"].get(k, 0.0), b["area_by_material"].get(k, 0.0)
    rel = abs(x - y) / max(x, 1e-9)
    worst = max(worst, rel)
    if rel > 1e-4 and abs(x - y) > 1e-4:
        bad.append("material %s area %.5f -> %.5f" % (k, x, y))
for k, (lo, hi) in a["asset_bbox"].items():
    if k not in b["asset_bbox"]:
        bad.append("asset missing " + k)
        continue
    lo2, hi2 = b["asset_bbox"][k]
    if any(abs(p - q) > 1e-4 for p, q in zip(lo + hi, lo2 + hi2)):
        bad.append("asset bbox moved: " + k)
for k, v in a["identity"].items():
    w = b["identity"].get(k)
    if w is None:
        if v["type"] != "EMPTY" and not v["props"]:
            continue
        bad.append("identity object missing: " + k)
        continue
    if v["props"] != w["props"]:
        bad.append("properties changed: " + k)
    if any(abs(p - q) > 1e-4 for p, q in zip(v["matrix"], w["matrix"])):
        bad.append("transform moved: " + k)
    if v["parent"] != w["parent"]:
        bad.append("parent changed: %s %s -> %s" % (k, v["parent"], w["parent"]))
if a.get("animation") != b.get("animation"):
    for x in a.get("animation", []):
        if x not in b.get("animation", []):
            bad.append("animation lost or changed: %s" % (x,))
    for x in b.get("animation", []):
        if x not in a.get("animation", []):
            bad.append("animation added by the derivative: %s" % (x,))
if a["lights"].keys() != b["lights"].keys():
    bad.append("lights differ")
print("compare: materials %d, worst relative area difference %.2e" % (len(keys), worst))
for x in bad[:40]:
    print("DIFF", x)
print("RESULT", "FAIL (%d differences)" % len(bad) if bad else "PASS")
sys.exit(1 if bad else 0)
