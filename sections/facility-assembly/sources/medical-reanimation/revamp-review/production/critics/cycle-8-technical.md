# Cycle 8 technical review — FAIL, 7.8 / 10

Reviewed source SHA `045d77ded3329a43c2fed0fb3d3bc39f370548a8ca8c4b9d468de65d7b86b714`. This fresh technical review inspected the current builders, specialist scripts, validator and renderer and ran three read-only Blender 5.2.2 probes. No art, original module, spawn, map or interface files were edited or saved.

The blocker is physical attachment of the new upholstery welts. `skill_redo.py` builds seam points from the edge of the reshaped cover and adds `sp.z * .18` to their height. The resulting joined group also contains stitches, and `overhaul_room.py` chooses only the group's closest vertex for its support anchor. The supplied validator therefore reports PASS even where other welt sections float.

| Tailored cover group | Maximum distance to actual upholstery surface | Vertices beyond 5 mm |
|---|---:|---:|
| Recovery pillow | 13.61 mm | 347 |
| OCRU head pad | 10.48 mm | 444 |
| Cart mattress, each of three | 12.12 mm | 444 each |

The welt tube has a 1.5 mm radius. Even subtracting its full 3 mm diameter leaves more than the protocol's 5 mm gap allowance at these detached sections. Fit or remove these runs and validate witnesses on each actual welt, including corners/end regions. The room cannot pass the support-contact gate with this defect.

Old pre-revision seam groups also remain. The old recovery pillow seam reaches about 9.93 mm inside its newly shaped pillow; OCRU pillow and berth seams reach about 7.76–9.56 mm inside their new covers. Review and remove/refit the superseded construction. The Dated OCRU maintenance card additionally has eight collapsed mesh faces and eight zero-area physical UV faces; the UV report records them but checks only finiteness.

The separate numerical passes are solid: fresh full-file cold open succeeded; all 25 libraries resolved; all five local file images are packed; there are no missing unpacked images; 159 reviewed meshes have consistent winding and no nonmanifold internal edges or mirrored world transforms. The original module and full map hashes match the baseline, spawn is unchanged, and the existing validator reproduces its 1203 inherited-object checks and 107 group/116-anchor PASS. Its contact sampling is the failed coverage boundary described above.

Texture map semantics are correct in the inspected source: poster artwork remains on its render UV, bottle labels explicitly read `Clinical_Label`, both color images are sRGB, and packed height/roughness maps are Non-Color with height wired through Bump. All 159 target meshes have finite `MED_Physical_1m` UVs; the card's eight degenerate faces are the exception to area coverage. Cabinet additions follow each sliding pane, cart guards and tailored mattress groups follow `CART_LIFT_DECK`, and reserve cover follows its service door. The reshaped wheels meet the floor at approximately zero gap. Pillows retain contact, and cart pads have approximately 2.5 mm nearest gap to the deck.

The light count is exactly one red area, one warm area and two spots: 45 W, 34 W, 35 W and 240 W respectively. Perceived dimness belongs to the pixel review. The closed bag and four note-corner contact witnesses remain present.

Current evaluated local geometry is 429,308 triangles versus 133,888 baseline (3.21 times). A numeric room budget and engine performance are unverified. No build rebuild, exhaustive collision audit, runtime export, Unity test or cold/hot pixel comparison was performed. Current full renders were still being produced; this report does not award visual acceptance. Read-only fresh-open behavior and dependency availability are independently verified.

Exact successful commands and copied numerical contact evidence are in `cycle-8-technical.json`. Scratch probes and output remain under `/tmp/medical_cycle8_*`. The source hash was unchanged after review.
