# Cycle 9 repair contact preflight — PASS within bounded scope

Candidate SHA: `42af739f1aacd6bf51deba5ad9234be23faa7bae5babccc97be0188e13211bd8`. This is a read-only repair preflight, not a new formal cycle grade or final room acceptance.

I inspected the current repairs in `skill_redo.py` and the added all-vertex seam check in `verify_overhaul.py`, then independently cold-opened the actual candidate in Blender 5.2.2 LTS. The actual scene has 1,312 objects. No source was saved or edited.

The previous seam-contact blocker is repaired. The new welt follows the final cover BVH with a 0.4 mm offset and a 1.2 mm radius; the independent audit tested every final mesh vertex rather than a group's nearest vertex. All eight tailored groups pass both the 5 mm gap and 2 mm penetration limits.

| Group | Vertices checked | Maximum nearest-surface distance | Maximum penetration |
|---|---:|---:|---:|
| Segmented adult berth cushion | 1254 | 1.6003 mm | 0.4532 mm |
| Segmented adult berth cushion.001 | 1254 | 1.6003 mm | 0.4532 mm |
| Segmented adult berth cushion.002 | 1254 | 1.6003 mm | 0.4532 mm |
| Contoured head pad | 1254 | 1.6004 mm | 0.7732 mm |
| Recovery pillow | 1254 | 1.6003 mm | 0.7663 mm |
| Cart segmented mattress | 1254 | 1.6002 mm | 0.6218 mm |
| Cart segmented mattress.001 | 1254 | 1.6002 mm | 0.6222 mm |
| Cart segmented mattress.002 | 1254 | 1.6002 mm | 0.6199 mm |

Total: 10,032 vertices; zero vertices beyond 5 mm. Worst nearest-surface distance is 1.6004 mm, worst signed outward gap is 1.6003 mm, and worst penetration is 0.7732 mm.

The five superseded seam groups are absent: OCRU head-pad seam, recovery-pillow seam and the three old berth-pad bound seams. The retained recovery-foam wrapped seam stays within 1.501 mm of its support and within 1.501 mm penetration.

The maintenance card now retains its substrate thickness through rigid translation. Its 718 vertices / 694 faces have zero zero-area mesh faces, no inconsistent winding and no nonmanifold internal edges. All 154 target meshes have finite `MED_Physical_1m` coordinates and zero zero-area physical UV faces. The updated builder now asserts both finiteness and nonzero face area, so the prior logged-only UV defect cannot silently pass that build assertion.

The independent cold open resolves the existing library set, and original medical module, assembled map and approved spawn hashes remain unchanged. Candidate SHA remained identical throughout this review.

Limits: this closes the three specific geometry/contact/UV repair findings. It does not replace the next fresh formal technical/visual review, exhaustively prove unrelated object contacts, validate every triangle interior between sampled seam vertices, or establish a render/performance/engine result. I did not rerun the complete existing validator because the root is already doing that; this audit independently checked the expanded contact coverage and actual mesh/UV data.

Successful commands:

- `/workspace/tools/blender-5.2.2-linux-x64/blender -b --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python /tmp/medical_cycle9_technical_probe.py`
- `/workspace/tools/blender-5.2.2-linux-x64/blender -b --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python /tmp/medical_cycle9_contact_probe.py`

Numerical scratch evidence is `/tmp/medical_cycle9_technical_probe.json` and `/tmp/medical_cycle9_contact_probe.json`.
