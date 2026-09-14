# A05 exterior integration handoff

All twelve sections have generated concept previews and editable additive exterior builds. The master retains A04 placement, original source room geometry and the 21 unbuilt connection reservations. Four actual Cycles HIP views per section (48 total) are hash-bound to their current saved revision. Generated concepts are clearly separated from scene renders in the [local gallery](../exteriors/gallery.html).

## Open

- [Assembled A05 master](../blender/facility_master_A05_exteriors.blend)
- [Concept/render comparison gallery](../exteriors/gallery.html)
- [Actual assembled exterior](material-views-A05/E03_COMPLETE_EXTERIOR.png)
- [Actual power-wing exterior](material-views-A05/E02_FACILITY_EXTERIOR.png)
- [Current revision map](../exteriors/CURRENT.json)
- [Concept prompt set](../exteriors/CONCEPT_PROMPTS.md)
- [Cold integration check](COLD_EXTERIOR_MASTER_CHECK.json)
- [Exterior placement/route screen](EXTERIOR_LAYOUT_AUDIT.json)

## Verification and limits

Fresh-process integration checks pass for all twelve linked rooms and exterior collections, unit scale, exact A04 poses, frozen source hashes, image dependencies, per-section portal/reservation audits, and added-mesh support/connectivity broadphase. No new foreign-room or reserved-route candidates remain in the conservative layout screen. Turbine/condenser U04 centers remain within 0.000005395 m. The screen excludes four-metre endpoint transition zones; explicit aperture checks cover named local interfaces. This is not runtime collision/navmesh certification.

Art acceptance is **not claimed**. The latest independent visual scores below are out of the visual portion's 90 points; technical scoring is separate. Some reviews precede small current-revision corrections: use each section's critic files for exact scope. Exterior finish, wear/storytelling and some labels remain below the full protocol threshold. No two stable accepted exterior rounds are claimed. Existing accepted interiors are not rescored by these outside views.

| Section | Built revision | Actual views | Latest independent visual score |
|---|---|---:|---:|
| compliance-dock | R08 | 4 | 81 / 90 |
| spawn-room | R05 | 4 | 79 / 90 |
| medical-reanimation | R04 | 4 | 80 / 90 |
| waste-storage | R01 | 4 | 76 / 90 |
| electrical-room | R03 | 4 | 78 / 90 |
| turbine-room | R04 | 4 | 78 / 90 |
| condenser-bay | R02 | 4 | 74 / 90 |
| cooling-plant | R03 | 4 | 74 / 90 |
| reactor-room | R05 | 4 | 72 / 90 |
| fuel-corridor | R02 | 4 | 73 / 90 |
| refinery | R01 | 4 | 76 / 90 |
| mine | R02 | 4 | 74 / 90 |

## Integration details

Original A04 `facility_master.blend` remains preserved. A05 links `EXTERIOR_<section>` collections from `exteriors/<section>/exterior-<revision>.blend` at the same unit-scale transform as its room. Keep the whole `sections/facility-assembly` folder together so relative libraries resolve.

Source practical lights with demonstrated exterior leakage are copied locally: spawn, turbine, cooling, mine and reactor emitter dimensions are reduced to fit their shells. Source shadow-disabled lights are enabled in local copies where applicable. Original source files are never rewritten. Reactor/cooling/mine wrappers retain source collection hierarchy and visibility; spawn/turbine/refinery legacy wrappers were independently checked for inherited flag changes. Reactor's hidden QA annotation transforms are not acceptance geometry; non-QA physical source geometry/transforms match at the common review frame.

No connecting corridors, stairs/lifts, facility cooling loop, terrain infill or new utility continuations were fabricated. Source-owned closed caps/doors remain, including the mine/condenser stubs and turbine return cap. Compliance exterior gate dressing still requires attachment to its corresponding moving leaf during engine import. No merge to main or engine integration is included.

## Replay

Use Blender 5.2 LTS headlessly. Set `EXTERIOR_SECTION` and a new `EXTERIOR_REVISION`, then run `blender/build_exteriors.py`; validate with `audit_exterior.py` and `audit_exterior_support.py`. Update `exteriors/CURRENT.json` only to the intended candidate. `render_exterior.py` resolves CURRENT by default; set `EXTERIOR_USE_CURRENT=0` for historical revisions. All GPU renders use the facility GPU gate, owner `astra-facility-assembly`. Render settings are Cycles HIP/HIPRT, GPU denoising, 32 samples, 1600x900; persistent render data is disabled after severe successive-frame slowdown was observed.

Run `audit_exterior_layout.py`, `integrate_exteriors.py`, and a fresh `check_exterior_master.py` before handing off another assembly. Reviews, failed intermediate revisions and original concept/source evidence remain preserved.
