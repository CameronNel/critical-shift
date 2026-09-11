# Luna procedural closure — W22 cold repeat

Reviewed the actual cold-process PNGs for C01, C02, C08, C09, and C10 in `production/renders/cold/W22`, together with `production/validation/W22/cold-pixel-comparison.json`, the cold fingerprint comparison, and the saved-artifact receipt.

## Cold pixel evidence

The cold repeat uses the same Cycles/HIP settings, 32 samples, 1440×900 resolution, seed 17, and the same 20-camera manifest. The decoded images are **not byte-identical**, and that is recorded rather than hidden: every image has a maximum 8-bit difference of 1, with only 122–213 changed pixels out of 1,296,000. The requested five views are:

| View | Mean absolute difference (8-bit) | Maximum | Changed pixels | Pixel finding |
|---|---:|---:|---:|---|
| C01 Entry | 0.0000447531 | 1 | 174 | Same centered lane, bay labels, jib/cask silhouettes, practical pools, and matte floor response. No composition or lighting defect appears in the cold frame. |
| C02 Casks | 0.0000504115 | 1 | 196 | Same cask hardware, labels, collars, gauges, bases, and orange-post edge. No changed detail affects the machinery read. |
| C08 Extraction | 0.0000516975 | 1 | 200 | Same paired filters, fan/isolator, connected utility feeds, labels, and material separation. No utility regression is visible. |
| C09 Inventory | 0.0000516975 | 1 | 201 | Same monitor, dose gauge, scanner lead, log, orange case, and desk. No station-routing or material defect is visible. |
| C10 Workbench | 0.0000547840 | 1 | 213 | Same seal-service board, tools, vice, case, shelf, apron, and roughness response. No workbench defect is visible. |

These are sparse one-level quantization differences, not structural, material, camera, or lighting changes. The cold comparison correctly reports `all_pixel_identical: false`; the review does not claim exact pixel determinism.

## Fingerprint and artifact evidence

- `cold-fingerprint-comparison.json` reports exact object, material, and contract matches for the two cold opens.
- `cold-pixel-comparison.json` reports `same_settings: true` and `artifact_unchanged_since_first_open: true`; the artifact SHA is unchanged.
- The live-open receipt confirms the same saved W22 artifact with 2,341 objects and 20 cameras in a clean session.
- `technical.json`, `detail.json`, `motion_process.json`, `contact_candidates.json`, rebuild comparison, and the saved W22 source checks remain passing.

## Closure

**COLD STABLE — no rerender required.** The requested cold frames preserve the approved W22 local Waste presentation and the utility/material corrections. The one-level sparse pixel drift is an honest renderer quantization difference and does not indicate a visible defect. Luna's scoped W22 approval remains valid for the authored Waste module and local integration readiness. Neighboring-room assembly and whole-map continuity remain outside this closure.
