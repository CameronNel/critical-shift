# Cycle 12 — bounded independent print-repair preflight

**PASS for the bounded repair. No formal /10 score or room acceptance assigned.**

Current source SHA-256: `e90d540600a9ec180f3a3bf71a89da4bf0f29a156b0ac3c8bcff2f59d0a63199`. Fresh Blender 5.2.2 LTS factory processes, `--disable-autoexec`, one thread and `--python-exit-code 1`. No source save, edit, rebuild or render. Protected files and the frozen cycle-11 technical JSON/Markdown hashes remained unchanged.

All 12 `MED_R2 | Clinical cabinet stock 0` through `11` groups were tested against their actual `Sealed supply case` through `.011` evaluated surfaces. All **96 barcode islands** were independently identified. Ink and oxide selection covered every identification and expiry print face; all 24 stock print metadata entries select their complete materials without z ranges and name the correct cases and `SUPPLY_CABINET` parent.

Contact checks covered **8,622 unique print vertices, 16,464 unique edge midpoints and 8,166 face centroids: 33,252 samples**, using both nearest-surface signed separation and front-face directional raycasts. **Zero failed samples.** Signed gaps range from **0.250101 to 1.250029 mm**; the largest directional ray gap is **1.250020 mm**. Supporting normals are exactly aligned in the measurement (0° deviation); no penetration was found. The same 0.250101–1.250029 mm interval covers all barcode vertices, resolving the former approximately 8.5 mm barcode gap.

The ink set includes 768 barcode vertices and 3,654 identification-text vertices. The expiry text contributes 4,200 vertices. Detailed per-group vertex/edge/centroid counts, contact extrema, actual surface witnesses and all barcode island bounds are in the JSON and `/workspace/scratch/medical-cycle12-print-preflight/independent-print-contact.json`.

All **32 room mesh material users** that request the linked `MED_Physical_1m` channel have it, with finite nondegenerate coordinates. The three consumable cartons now have that layer and zero degenerate faces. The active main-floor and decon-floor surface graphs each use their own measured mesh-bound multiplier, feeding the active 0.6 m Brick Width / Row Height with Scale=1. Main slab: 8.36×9.36×0.24 m; decon slab: 2.06×2.12×0.24 m. An initial broad node listing encountered a retained brick node outside the measured tile-vector path; the separate active-surface traversal confirms the actual shader path and supplies the reported scale evidence.

This checks the current saved native repair only. It does not rescore the room, render new evidence, certify global geometry/runtime behavior or establish final acceptance. Complete fresh cycles 12/13 and formal independent critics remain separate work. Midpoint/centroid sampling is bounded evidence, not an arbitrary continuous-surface intersection proof. Battery-label components were outside this focused recheck.

Commands (both exited 0):

```sh
/workspace/tools/blender-5.2.2-linux-x64/blender -b --factory-startup --disable-autoexec -t 1 --python-exit-code 1 --python /workspace/scratch/medical-cycle12-print-preflight/print-probe.py > /workspace/scratch/medical-cycle12-print-preflight/print-probe.log 2>&1
/workspace/tools/blender-5.2.2-linux-x64/blender -b --factory-startup --disable-autoexec -t 1 --python-exit-code 1 --python /workspace/scratch/medical-cycle12-print-preflight/floor-active-probe.py > /workspace/scratch/medical-cycle12-print-preflight/floor-active-probe.log 2>&1
```
