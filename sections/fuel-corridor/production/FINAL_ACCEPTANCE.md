# Fuel Corridor final acceptance — F10

**PASS: all 17 independently reviewed categories are strictly above 90 (91–95).** All 16 fixed views and all 12 player-eye views also exceed 90. Independent reviewer: grok-4.6 independent critic. Builder: Astra. These scores cover the authored corridor's integration readiness, not whole-map polish or engine runtime validation.

Saved artifact: `blender/Fuel_Corridor.blend` · SHA256 `a8e742a10cf5691098adabc0c2518384db3d82444517637bd67e362af4146403`.
The canonical file is byte-identical to the reviewed candidate and survives fresh-process reopening. It contains 7,978 objects, 34 materials, 16 saved cameras and 3 packed images, with no linked libraries. Original scene authoring is reproducible from the section-local source.

| Category | Independent score |
|---|---:|
| specification coverage | 93 |
| facility/process logic | 93 |
| human scale | 94 |
| player circulation | 94 |
| freight/cart handling | 94 |
| maintenance access | 94 |
| interface consistency | 91 |
| machinery construction | 94 |
| physical support/contact | 93 |
| Valorant shape language | 93 |
| material separation/anti-plastic | 93 |
| lighting/readability | 92 |
| no-teal color discipline | 95 |
| signage/numbering | 91 |
| environmental storytelling | 93 |
| camera coverage | 94 |
| saved-artifact/source/dependency reproducibility | 94 |

## Evidence

- Complete 16-view final pack: `renders/review/final-F10`; 1440 × 960, 32 samples, frozen camera poses.
- Complete 16-view canonical cold repeat: `renders/review/final-F10-cold`; every view separately passes max ≤2/255 and mean ≤0.02/255. Largest observed channel difference: 1/255. Each primary and repeat image uses its own fresh Blender process; the original per-view manifests are retained with the complete aggregate manifests. PNGs are not claimed byte-identical.
- Twelve player-eye observations: `renders/review/final-F10-walkthrough`; 1200 × 800, 32 samples, eye height 1.70 m. All approaches have grounded positions and clear near-camera space.
- Fresh CPU geometry/support/routes: `evidence/final-pass/F10-technical.json`.
- Factory-empty object/world-geometry replay and separate material/UV/packed-texture replay: `F10-source-replay.json` and `F10-material-replay.json`.
- Exact branch/handoff and 39 sampled gate positions: `F10-branch-handoff.json` and `F10-engineering-motion.json`. Zero-depth roller tangencies are intentional contacts; no penetrating mechanical obstruction is accepted.
- Independent final scores: `critics/final-pass/grok-f10-score.json`. Final hash-bound receipt: `evidence/final-pass/delivery-receipt.json`.
- Interactive image gallery: `FINAL_GALLERY.html`; dimensioned plan and exact interfaces are in `../architecture`.

## Corrections and preserved failures

F00 was rejected for a black overlapping floor patch, competing/hidden wayfinding, mounting/source mismatches, weak reactor-header contrast and insufficient door construction. F01–F04 repaired geometry and presentation but retained their failed or partial status. F05's broad visual pack passed, then its canonical C08 repeat exposed a real narrow coplanar flange/lining strip; Luna correctly revised reproducibility to 90/fail.

F06–F08 were rejected engineering candidates. F09 separates the rear steel flange from the lining by 4 mm, fits waste-sign feet to the exposed upright face, and separates the service grille and corner lamp from sign mounts. No required machinery, portal, route or fixed camera was added, removed or relocated. Exact geometry delta is retained in `F05-F09-delta.json`. The rejected images, scores and technical failures remain available; none were averaged away.

F09's complete cold pack exposed the intersecting first-aid cross bars (C07 max31/255) and four tiny beam-edge outliers (C04 max4/255). F10 replaces only the two coplanar cross bars with one continuous stamped cross; `F09-F10-delta.json` confirms no other object changed. Its paired fresh-process rendering catches each view's repeatability immediately. The invalid pre-promotion F09 attempt is explicitly excluded from all F10 evidence.

## Integration limits

Five external connections and one internal freight gate are authored. F01/F02 retain their exact local refinery/reactor mating equations; S01/S02/S03 are reserved destinations. Neighbors were not moved or rebuilt. Their closed doors, shared-world placement, destination adapters and refinery-unit/reactor-cartridge conversion remain unresolved external work. The handoff supplies authored collision sources, routes, carriages, spawn/incident markers, audio volumes and network cells. Collider cooking, navmesh, controllers, runtime physics, audio/network behavior and full facility travel timing are not certified by Blender renders.

Repository delivery is section-only on `codex/fuel-corridor-final-20260911`; the final shared status/user response supplies the verified commit and remote result.
