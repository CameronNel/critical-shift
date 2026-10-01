"""python compare_signatures.py before.json after.json  -> exit 1 on any difference beyond tolerance"""
import collections
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
fmap = b.get("family_map") or {}
if fmap:                                    # the derivative merged materials into families: compare area per family
    relabel = collections.Counter()
    for k, v in a["area_by_material"].items():
        relabel[fmap.get(k, k)] += v
    a["area_by_material"] = dict(relabel)
    mrel = collections.defaultdict(lambda: [0.0] * 5)
    for k, v in a.get("moment_by_material", {}).items():
        for i in range(5):
            mrel[fmap.get(k, k)][i] += v[i]
    a["moment_by_material"] = dict(mrel)
# area-weighted position moments per material: swapping constants between equal-area polygons in different places still shows
for k in sorted(set(a.get("moment_by_material", {})) | set(b.get("moment_by_material", {}))):
    ma, mb = a.get("moment_by_material", {}).get(k, [0.0] * 5), b.get("moment_by_material", {}).get(k, [0.0] * 5)
    if any(abs(x - y) > 1e-3 + 1e-6 * abs(x) for x, y in zip(ma, mb)):
        bad.append("geometry moments differ for material %s: %s -> %s" % (k, [round(x, 3) for x in ma], [round(x, 3) for x in mb]))
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
import collections

ca = collections.Counter(json.dumps(x, sort_keys=True) for x in a.get("animation", []))
cb = collections.Counter(json.dumps(x, sort_keys=True) for x in b.get("animation", []))
for x, n in (ca - cb).items():
    bad.append("animation lost or changed (x%d): %s" % (n, x))
for x, n in (cb - ca).items():
    bad.append("animation added or changed by the derivative (x%d): %s" % (n, x))
if a["lights"].keys() != b["lights"].keys():
    bad.append("lights differ")
print("compare: materials %d, worst relative area difference %.2e" % (len(keys), worst))
for x in bad[:40]:
    print("DIFF", x)
print("RESULT", "FAIL (%d differences)" % len(bad) if bad else "PASS")
sys.exit(1 if bad else 0)
