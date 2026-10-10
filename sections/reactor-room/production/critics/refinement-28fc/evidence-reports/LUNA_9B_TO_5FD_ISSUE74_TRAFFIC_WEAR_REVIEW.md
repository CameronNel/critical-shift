# Issue 74: D1 approach wear, exact 9b pixels and bounded later-source carry

## Original pixel evidence

The full-quality source image is [`69_floor_doorway_travel_wear.png`](/workspace/scratch/reactor-refinement-next-corrections-working/proof/green/69/69_floor_doorway_travel_wear.png), SHA-256 `b1f0b83ad62900a5253fd3fdb95e4db12dd956495d81839ecd6e5f1e179d76f1`. Its manifest is SHA-256 `5f0a8940c5d06833b5f5a15ac610e57daf2a6708e9863ad2fdf85522de7120f6` and identifies source `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7`, camera `(-6.9, 0, 1.4) → (-10.2, 0, 0.03)`, 28 mm, 1280×720, Cycles 96 max/32 min, OIDN, 16-bit, 0 exposure, AgX Medium High Contrast.

The D1 marked approach reads as an actual travel path: irregular longitudinal scuffing runs from the threshold toward the floor arrow, within the two route stripes. Chipped paint, fine cracking and threshold wear remain distinct from the darker rubber-like lane scuffs. The marks are directional without forming a set of identical straight parallel lines. This is enough to accept #74 for the visible D1 access-lane movement-wear pattern. It does not establish wear in every floor region or close separate wet/oil/dirt, crack, route-continuity or material-family criteria.

## Exact bounded carry to 5fd

The image stays attributed to source 9b. The floor wear is usable as bounded unchanged-scope corroboration for the later exact candidate 5fd because the four intervening deltas preserve the floor object/material and the render neighborhood:

| Delta | Exact source → candidate | Declared changed objects | SHA-256 |
|---|---|---|---|
| C89→9b | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` → `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7` | Six door-return meshes and `R2 pool pool lining TILE`; 1,929 unchanged | `742aa950d30574149dddc41578207aa3ede6befac99f9571bc7d9ff91eea2ca8` |
| 9b→79e | `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7` → `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c` | `R2 pool pool lining TILE`; 1,935 unchanged | `0d89fdfe0bd679317dde47d46dbd60a0ff630b6c922db469e9b534e299b47575` |
| 79e→f79d | `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c` → `f79d0bf32c7f339f78796953332b3db347968c23cc75562bed5d0c9ba9acc5ff` | Four switchgear-prop meshes; 1,932 unchanged | `6280636c48c2bd8ac6e04df356d15d6d86c08e14ed643221e68340e34a343c2d` |
| f79d→5fd | `f79d0bf32c7f339f78796953332b3db347968c23cc75562bed5d0c9ba9acc5ff` → `5fd5f7b0f21383348f8fa450609057be01f17cd9426758bfe7ab6ada48565779` | Crane trolley hood mesh and 15 local hoist parts; 1,935 unchanged | `bc5040fb11e5645728e0665b0480b8576816a92ee0d24546e698fc6f95a84b1c` |

Each delta’s declared comparison includes object transforms/parents, mesh geometry/material assignments and graphs, lights and camera settings. The floor material, floor geometry, D1 approach camera, lights and exposure are outside each changed-object list and are compared as unchanged. This is a narrow transfer of the pictured floor-wear result, not a claim that the 9b image was rendered from 5fd or that all five scenes are globally identical.

**Disposition:** accept #74 on the exact 9b image and carry that D1-lane wear scope to 5fd. Keep all other floor claims separate. The 5fd view70 hoist-lighting issue is unrelated to this floor image and remains open under its own report.
