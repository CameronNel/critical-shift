# C677c wall-service penetration family review

**Candidate:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Candidate SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`  
**Disposition:** bounded source and camera assessment only; #90 appearance remains pending current full-quality view 71. No score assigned.

## The 71 camera target

The 71 camera at `(2.1, 9.3, 9.2) → (2.9, 10.421, 8.9)`, 50 mm, targets the **north-wall bank A service sleeve** centered at `(2.9, 10.8, 8.9)`. It does not target bank B at `(-5.4, 10.8, 8.9)`. The old f79d calibration image shows the red bank A fire-main run entering the square sleeve plate at the orange north-wall trim. Its 480×270 pixels identify the intended object, but they are preview-only and do not establish appearance acceptance. Require the queued C677c full-quality 71 pixels before closing #90.

## One shared construction family, eight fitted instances

All eight active receivers call `sleeve_wall(P, d, r)` in `scripts/rh_services.py` with the default `esc=True`. The helper generates the same hollow annular sleeve and seal, bored escutcheon, square plate, four wall-bearing legs, and four bolt heads. The instances differ in radius (0.030–0.110 m), pipe run, and wall-normal orientation:

| Receiver | Center (m) | Radius (m) | Wall normal |
|---|---:|---:|---|
| EC vent | `(5.0, -10.8, 3.9)` | 0.085 | `+Y` |
| EC-A drain | `(3.3, -10.8, 1.05)` | 0.038 | `+Y` |
| EC-B drain | `(1.8, -10.8, 1.05)` | 0.038 | `+Y` |
| Turbine steam | `(10.8, -3.8, 6.4)` | 0.088 | `−X` |
| Turbine exhaust | `(10.8, -3.3, 1.15)` | 0.110 | `−X` |
| Waste vent | `(8.1, 8.7, 5.2)` | 0.030 | diagonal `(-.707, -.707, 0)` |
| Bank A service | `(2.9, 10.8, 8.9)` | 0.057 | `−Y` |
| Bank B service | `(-5.4, 10.8, 8.9)` | 0.057 | `−Y` |

The service runs and receiver sizes vary, but no port uses a second sleeve construction. The largest exhaust is a scaled instance of the same helper; its orange pipe identification band is on the adjoining run, not a distinct sleeve type. One clear full-quality representative can establish the shared visible construction when combined with the exact per-instance fit and support checks. This is not a claim that every receiver is visually clear from every angle.

The exact C677c `wall-bores.json` (`ef52cbde29383d7ed92c68a60662bad189be751216cff183ca174905f7625ae0`) records 65/65 rays without hits for each of the eight receivers. The source-bound support audit (`audit.json`, SHA-256 `15050f5b42a6556246fb5d0c8bc9bea336a47b99293a170b8be223631b25c8bd`) records 40 passing sleeve-related anchors: eight pipe-to-seal contacts and 32 escutcheon-leg-to-plate contacts. These are finite fit/support scopes, not exhaustive collision or visual proofs.

## Room-side camera access check

The bounded preflight places a camera 0.68 m inward from each receiver plane, aimed at a point 0.18 m inward, with LP haze volumes hidden from opaque-ray tests. It tests local sleeve front-face samples, projection and six short camera-origin rays. Exact C677c source is recorded in:

- Probe: `/workspace/scratch/luna_677c_nearwall_penetration_preflight.py`, SHA-256 `6865c86133732a35eebaf1ad8e5daf34b206b4e94f99a7becbd79f6b06b6e159`.
- Results: `/workspace/scratch/luna_677c_nearwall_penetration_preflight.json`, SHA-256 `63bd5d14b9efad07b12aac57060c4dceec2586836a362066b6e8a66a9e6454f0`.
- Log: `/workspace/scratch/luna_677c_nearwall_penetration_preflight.log`, SHA-256 `31cf6f06bae54c6fbea717424d6751c38fc15a861fac56d1cba11fb306c6f5bc`.

The chosen south-wall EC drain camera location is only 10 mm from the station's AUDI_SATIN surface and 64 mm from station IRON. It produces no direct first hits on either drain sleeve. The test shows that this particular camera does not fit cleanly between the station and wall; it does not prove a physical maintenance-clearance defect or exhaust every possible room-side camera pose. The east exhaust near-wall camera is clear at its origin, but its view is dominated by the sleeve mount/flange and does not expose a useful clean annulus view. The north bank A axial near-wall camera is obscured by the red fire-main pipe; the reviewed 71 diagonal approach is the appropriate representative view. Bank B's near-wall view yields 12 of 58 sampled sleeve-face first hits and no nearby opaque camera-origin neighbor.

These sparse local tests describe camera placement only. They do not claim maintenance access, prove all-angle visibility, or establish a physical interference failure. No source or lighting change is indicated by them.

## Why existing equipment views do not substitute for 71

Preserved C69 full-quality images were inspected as historical corroboration only; their scene identity is C69 (`36f0c158ca8b81d4b67b1c20bccbc7fbaa510a4895b445a54a6a6ffd980f444c`), not C677c:

| Image | Image SHA-256 | Actual content | Relevance to #90 |
|---|---|---|---|
| `12_ec_local_controls.png` | `b638a5d5df00a81bf953a62af6a7e1866f7e39e0ca096d42e84bb63da777bfba` | Close EC controls box, adjacent horizontal pipe run, and nearby vessels | Does not show the south-wall drain sleeve, seal, plate, or legs. |
| `14_turbine_base.png` | `2c74f610d1ef786f8fd02f69e8a892f735f869605d63429b38f93e4027fc93bd` | Turbine casing/base, service guard, local pipework | Does not show the east-wall steam or exhaust receiver interface. |

The preserved C69 manifest is `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c69/inspection-720p/render_manifest.json`, SHA-256 `2d8e90a522651267a25ad5695abf4095c9ece4df52507a1bc4c4a6f44c0ab6b6`; it records both originals as 1280×720 renders. Neither image is relabeled as current evidence, and neither closes wall-sleeve appearance.

## Conclusion

The current source contains one shared sleeve construction family instantiated at all eight ports; the exact-source fit audit and 40 support contacts cover each instance. A clear current full-quality 71 image of bank A can serve as the representative visual check for that shared family. The C69 equipment views do not substitute for that image. Keep #90 open until the current 71 pixels are independently reviewed; no extra view per duplicated port is required unless those pixels reveal a scale- or orientation-specific defect.
