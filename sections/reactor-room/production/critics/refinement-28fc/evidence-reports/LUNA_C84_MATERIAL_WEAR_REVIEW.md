# C84 material-specific wear review

**Disposition: accepted for the visible material classes below.** This closes #137 on exact C84 full-quality pixels. It does not close #74, which asks for a convincing room-scale traffic-wear pattern.

## Evidence

- Candidate: `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`
- Candidate SHA-256: `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`
- Full view03: `/workspace/scratch/reactor-refinement-cycle84/parallel-720p/main/green/03/03_floor_access_lane.png`
- View03 image SHA-256: `d37f0ba794c131d8122c318205881431842c3a1515b99ac526e343175b74ce70` (1280×720, 96 samples)
- Full view04: `/workspace/scratch/reactor-refinement-cycle84/parallel-720p/main/green/04/04_floor_pool_circulation.png`
- View04 image SHA-256: `a1342ba56482fa577d1040831f67b622162ebd627da187ba74528621eb9db641` (1280×720, 96 samples)
- Full inspection31: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/inspection-720p/31_props_drum_group.png`
- Inspection31 SHA-256: `ca70652e1f16ee719820bc3541d362af29bba5aed105e2dd014900bde9dca811` (1280×720, 96 samples)

## Finding

The exact images show distinct wear treatment by material: the yellow floor paint has localized chips and edge abrasion; the orange cone has dirt/scuffing concentrated near its lower body and foot; adjacent concrete keeps restrained aggregate/mottling instead of receiving the same high-contrast noise. In view04 the floor wear remains subordinate to the pool route and floor joints. In inspection31 the drum finish remains smooth and legible, which prevents the wear pass from becoming a blanket grunge layer.

This is enough evidence for material-specific wear at the visibly demonstrated painted floor, molded cone, and concrete surfaces. It does not imply every surface in the room is worn. The yellow chips and cone grime do not by themselves establish a directional, room-scale traffic-wear pattern; #74 remains open for that separate criterion.

## Separate traffic-wear check

A low-quality, transient route-aligned shader diagnostic is at `/workspace/scratch/c84-route-03-diagnostic/03_floor_access_lane.png` (SHA-256 `a44c4a7c8e80ddae16ed0797780094d3172bda889ff7601be688f3aa30c1fa90`, 480×270/16). It changes the owned floor shader in memory and is not acceptance evidence. A second diagnostic, [03_floor_access_lane.png](/workspace/scratch/c84-route-03-diagnostic-2/03_floor_access_lane.png), SHA-256 `c2c6b11b6dac98283ccabcfa8d7f1e7283d7c0212da91ec8595138e088c5d418`, keeps the same physically aligned west, north, and diagonal routes and leaves arrow/paint/water materials untouched while strengthening and lengthening the directional scuffs. In my review the marks beside the west arrow are more directional than the earlier broad mottling, but remain faint and too uniformly parallel to establish convincing traffic wear. The third diagnostic, [03_floor_access_lane.png](/workspace/scratch/c84-route-03-diagnostic-3/03_floor_access_lane.png), SHA-256 `d0844e7392708f6513eee6a3ca74bafb5f8f85cc5af9d211162524e6732adcc4`, reduces the arbitrary scuff field and replaces the straight streaks with shorter irregular longitudinal marks. It is a better candidate direction, but still a 480×270/16 diagnostic; the lane marks are faint at this size and cannot close #74. Require exact candidate full-quality pixels showing purposeful but irregular traffic wear clear of the arrow, painted stripe, and wet film.

No global score is assigned here.
