# Slice s07 independent technical review — LOCAL FAIL

Frozen source SHA-256: `269c04fe6b45870873baf1985e21e7ad915dc12a07136378cb639ffc46acc612`.

Scope is front-office architecture, D1, check-in, its new practical and utility. This report cannot approve the restroom, the full room, or runtime integration. No visual quality scores were inferred from code. Production scene and builder were not edited; source and all five protected hashes matched before and after the audit.

## Measured defects

1. **Detached counter wear.** All three `CD | Counter lip rubbed spot` meshes have actual nearest slab witnesses 20.025 mm away (scar Y=3.2300/Z=1.0190, slab Y=3.2500/Z=1.0180). Adjacent pairs overlap on an exposed same-facing plane at Y=3.2294, approximately 0.00028715 m² per pair per face. This is actual surface evidence, not a bounding-box contact assumption. Remove or integrate this wear into the manufactured lip.
2. **Reader wall penetration.** Three rays from interior points on the reader back to the actual intact wall measure **20.0001 mm penetration**, versus the protocol's 2 mm default. Housing back Y=3.5400; wall front Y=3.5200. The reader shares the floor-supported D1 root, so assembly contact passed without testing this wall seat. Provide an actual seat/recess and explicit wall support ownership while preserving the inherited matrix.
3. **Missing physical UV inputs.** Twenty curve/font consumers request `CD_Physical_1m` but evaluate only `UVMap`: D1 lever/closer, ballpoint, bead chain, cloth hems, conduit, and text. Mesh UV success does not certify these shader consumers. Supply a valid mapping contract while preserving editable text.
4. **Exposed partial coincident faces.** Both retained counter legs occupy wall-sill volume and share same-facing front/back planes, **about 0.071424 m² per face per leg**. East-front witness `(-2.73245, 3.52000, 0.51213)` and west-rear witness `(-4.26732, 3.68000, 0.51820)` have no outward surface cover. These are partial overlaps missed by the validator's exact-duplicate test. Top/bottom coincidences buried in floor/worktop are contact, not the exposed defect. Repair redundant construction without changing the combined envelope or bearing.
5. **Collapsed bevel geometry.** The scoped audit finds **644 exactly zero-area evaluated triangles across 21 objects**: 32 each on the key cylinder, six grille slits, twelve pad ribs and ink-pad lid lip, plus four on the manifest. Use appropriate edge treatment or scoped topology cleanup. This is distinct from submicron UV precision noise.

## Checks that passed

The existing validator, run in a fresh Blender **5.2.2 LTS** process with `--factory-startup --disable-autoexec --threads 1 --python-exit-code 1`, explicit `contracts/interface.json`, and expected `slice` stage, passed its five applicable checks: **21 assembly roots, 50 anchors, 12 cameras**, resources and exact duplicates. Its five explicit exclusions remain exclusions.

Direct read-only opening of the protected original confirms all **1,077 inherited world matrices** unchanged. The combined architectural bounds are equal. Rays through the combined wall/frame system confirm D1 still measures approximately **1.05 × 2.20 m**; hatch side/head landmarks match. The sill ray differs by 0.212 mm on a beveled surface. Other portal/scanner/cart architecture has unchanged evaluated geometry fingerprints; full open-route clearance was not rerun for slice acceptance.

All **25 libraries use relative paths and resolve**; the 119 image records pass resource checks. The active scene owns local authoring geometry. The targeted LFS fetch failed for missing Git credentials, but active native inputs were hydrated and opened. The unused frozen `accepted.blend` remains its protected LFS pointer.

All **192 mesh UV consumers** have finite, nondegenerate UVs on nondegenerate triangles. World-metric checks include sloped caps and actual applied bevels; edges longer than 0.1 mm have UV/metre ratios **0.998354–1.001585**, with no >1% errors. Extreme ratios on submicron paper edges are precision noise. The 20 curve/font consumers fail separately. All 192 closed scoped meshes have positive signed volume; this does not establish every individual face normal or corner shading.

Actual surface witnesses, directed bearing rays and triangle intersections substantiate the glass/clamp/stanchion/foot/worktop/leg chain; stamping pad and stamp base; case, felt seat and lid pins; cloth lower-ply bearing; service lid/conduit/saddles; practical bracket/shade/lens; and D1 hinge connections. Felt and cloth bearing rays differ from intended support by roughly 0.00000012 m. D1 strap-to-leaf gap is 1.000 mm, within the 5 mm tolerance. Reader seating fails separately. These checks do not establish engineering strength or hinge swept clearance.

Scene counters are **330,488 evaluated triangles, 1,157 material submeshes, and 44 used local material families**. Triangles are within the 450,000 planning estimate; submeshes/families exceed 1,150/36 estimates and require full-production review. No runtime performance claim follows.

## Evidence and limits

Opened all three beauty images in `renders/slice-s07`, Entry/Door checker images in `renders/slice-s07-uv`, neutral Material in `renders/slice-s07-neutral`, and the four supplied spawn references. All current beauty/diagnostic source and image hashes match their manifests. No new renders were made.

- [Validator](slice-s07-technical-validator.json) and [log](slice-s07-technical-validator.log)
- [Detailed probe](slice-s07-technical-probe.json), [script](slice-s07-technical-probe.py) and [log](slice-s07-technical-probe.log)
- [Surface witnesses](slice-s07-technical-surface-witness.json), [script](slice-s07-technical-surface-witness.py) and [log](slice-s07-technical-surface-witness.log)
- [Pre hashes](slice-s07-technical-hashes-pre.json) and [post hashes](slice-s07-technical-hashes-post.json)
- [Structured verdict](slice-s07-technical.json)

Arbitrary self/inter-object intersections and all hidden components were not exhaustively certified. Native cold open is verified; reproducible rebuild/cold-render comparison was not run by this critic. Full-room routes, restroom, engine collision/navigation/interactions, draw calls/FPS, owner art approval and merge status are unverified. The local defects prevent technical slice acceptance.
