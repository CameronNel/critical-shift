# Luna cold-open review — R10

**Evidence reviewed:** all ten actual images in `production/renders/cold/R10/`, compared visually with the approved R10 production images in `production/renders/review/R10/`, plus `technical/R10-cold-start.json` and `technical/R10-cold-start.md`.

## Verdict

**Artifact survival approved. Visual stability approved.** The cold-open images preserve the room's visible geometry, materials, lighting, camera composition, and native labels across all ten primary views. The CP-P01 / REACTOR identity, HX-01 markings, pump labels, service labels, withdrawal signs, route markings, reserve controls, hoist, and workshop text remain present and visibly usable.

The exact-pixel comparison correctly remains `REVIEW`: decoded RGB equality is false for all ten views. This is not being relabeled as equality. The measured differences are sparse and low amplitude, with the larger differences localized to HX-01 conformed lettering; no visible material, geometry, label-loss, or lighting defect was found in the cold images.

## Observations

- **C01_ENTRY:** Whole-room composition, central route, two pump skids, service room, HX-01, hoist, and signage survive. The same secondary sign edge cropping present in the approved R10 view remains unchanged.
- **C02_HERO:** HX shell, flange bolts, gauges, supports, pipework, hoist, pull-out signage, and HX-01 label survive with stable appearance.
- **C03_REVERSE:** CP-P01 / REACTOR identity, portal, pumps, exchanger, and route markings survive. The neutral gray beyond-portal boundary remains neutral and unassembled.
- **C04_ROUTE:** Lane, arrows, service-room identity, pump equipment, and withdrawal signage survive without a visible material or layout change.
- **C05_PUMP_A:** P-01 machinery, guards, coupling, gauge, feet, and label survive; the warm ivory/charcoal/oxide/yellow palette remains stable.
- **C06_EXCHANGER:** HX-01 shell, flange, gauge, hoist, pipework, supports, and labels survive. This is one of the views with the largest measured channel deltas, but no visible difference is apparent beyond localized lettering rasterization.
- **C07_PINCH:** Pinch route, service signage, pump hardware, and HX edge survive.
- **C08_WORKSHOP:** Workbench, drawers, tools, repair note, tool board, and enclosure survive. Fine note text remains present.
- **C09_BUNDLE_BAY:** Bundle face, exchanger end, supports, hoist context, and bay markings survive. The HX lettering variation remains localized and does not erase the label.
- **C10_MATERIALS:** Doorway, bench, wall finish, hardware, and material palette survive with no visible instability.

## Exact comparison retained honestly

`R10-cold-start.json` reports `artifact_unchanged: true`, matching Blender-file hashes, equal settings, and all ten primary cameras rendered. Exact decoded pixels are false for all ten images. Changed channels range from 211 to 2,113; maximum per-channel differences are 1 in C04, C05, C07, C08, and C10, and 7–9 in C01, C02, C03, C06, and C09. Mean absolute differences remain at or below 0.00062693 on the 0–255 scale, and RMS differences at or below 0.03143. The report's inference that the larger deltas localize to conformed HX-01 lettering is consistent with the visible images; it is not treated as proof of bit identity.

The cold-open comparison covers saved-artifact survival and render repeatability only. It does not certify whole-map assembly, runtime-engine behavior, or a neighboring reactor corridor. The built-in Blender font and external-dependency limitations documented in the live inspection remain applicable, while native text visibly survives the cold renders.
