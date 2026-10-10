# 677c bounded carry and rolling disposition

**Candidate:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Candidate SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`  
**Direct parent:** 5fd `5fd5f7b0f21383348f8fa450609057be01f17cd9426758bfe7ab6ada48565779`  
**Status:** rolling review only; no full-quality 677c image has been accepted and no score is assigned.

## Snapshot

- Accepted IDs: **117** (1–16, 18, 21–79, 81, 83–87, 89, 91–96, 98, 100–107, 109–115, 117–121, 123–124, 126, 130, 134–135, 140).
- Pending IDs: **23**: 17, 19, 20, 80, 82, 88, 90, 97, 99, 108, 116, 122, 125, 127, 128, 129, 131, 132, 133, 136, 137, 138, 139.
- Partial IDs (subset of pending): **6**: 19, 108, 131, 133, 136, 137.
- `score` and all area scores remain null. The final gate still requires all 140 dispositions, overall ≥90, and each of the nine areas ≥85.
- All ten 677c main views 01–10 remain required. Prepared focused views70/71 are not yet full-quality acceptance evidence.

The 114 accepted C89 visual/criterion dispositions remain historical, carried only within their subject scope. This includes #120, newly accepted in C89 from views16/24/25 plus finite foot/head/landing contacts and fixed-opening checks; the ladder, landing, gate and contact surfaces are unchanged through the five 677c source legs. #74 is accepted as a bounded carry from the full-quality 9b view69. #86 is accepted as a bounded carry from the full-quality 79e view21 after the revised pool-liner appearance was reviewed; its original image/source identities are recorded separately. #140 is accepted anew only for the finite current 677c checks and independently verified tasklight interfaces. Four prior acceptances are reopened: #108, #133, #136, and #137. This produces the 117/23/6 snapshot.

## Exact source chain

Every source leg below is checked against its recorded source/candidate hashes. Original images are never relabeled as 677c.

| Leg | Source → candidate | Delta SHA-256 | Changed retained objects | Added objects | Unchanged |
|---|---|---|---|---|---:|
| C89→9b | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` → `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7` | `742aa950d30574149dddc41578207aa3ede6befac99f9571bc7d9ff91eea2ca8` | COOLING PLANT.link wall, COOLING PLANT.link wall.001, FUEL HANDLING.link wall, FUEL HANDLING.link wall.001, MAIN ACCESS.link wall, MAIN ACCESS.link wall.001, R2 pool pool lining TILE | none | 1929 |
| 9b→79e | `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7` → `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c` | `0d89fdfe0bd679317dde47d46dbd60a0ff630b6c922db469e9b534e299b47575` | R2 pool pool lining TILE | none | 1935 |
| 79e→f79d | `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c` → `f79d0bf32c7f339f78796953332b3db347968c23cc75562bed5d0c9ba9acc5ff` | `6280636c48c2bd8ac6e04df356d15d6d86c08e14ed643221e68340e34a343c2d` | RH stations props BLACK, RH stations props STEEL, RH stations props WHITE, RH stations props YELLOW | none | 1932 |
| f79d→5fd | `f79d0bf32c7f339f78796953332b3db347968c23cc75562bed5d0c9ba9acc5ff` → `5fd5f7b0f21383348f8fa450609057be01f17cd9426758bfe7ab6ada48565779` | `bc5040fb11e5645728e0665b0480b8576816a92ee0d24546e698fc6f95a84b1c` | R2 crane trolley crane OLIVE | RH hoist anchor bolt shank 1 -1, RH hoist anchor bolt shank 1 1, RH hoist anchor bolt shank 2 -1, RH hoist anchor bolt shank 2 1, RH hoist anchor hex head 1 -1, RH hoist anchor hex head 1 1, RH hoist anchor hex head 2 -1, RH hoist anchor hex head 2 1, RH hoist anchor washer 1 -1, RH hoist anchor washer 1 1, RH hoist anchor washer 2 -1, RH hoist anchor washer 2 1, RH hoist drum end clamp 1, RH hoist drum end clamp 2, RH hoist inspection aperture frame | 1935 |
| 5fd→677c | `5fd5f7b0f21383348f8fa450609057be01f17cd9426758bfe7ab6ada48565779` → `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295` | `10058827bfc2ae32887862b2938f41490ec02d0d78630e0ddf9f0d126960b2b1` | none | RH hoist anchor maintenance LED, RH hoist anchor tasklight housing, RH hoist anchor tasklight lens | 1951 |

Scope notes: the C82→C84 storage-barrel edits are not crane-hoist-drum edits; the f79d→5fd edits add the hoist clamps and hood opening; 5fd→677c adds only the local tasklight housing/lens/light. The C89→9b and 9b→79e legs change the pool lining/door return scope, so #136/#137 and neutral-wall #133 were reopened. The four switchgear-prop meshes moved in 79e→f79d, so corrected13 signage remains pending.

## #120 fixed gantry access bounded carry

The C89 issue-120 composite is documented in [`LUNA_C89_ISSUE120_ACCESS_COMPOSITE_REVIEW.md`](LUNA_C89_ISSUE120_ACCESS_COMPOSITE_REVIEW.md), with original C89 source/image/manifest hashes and the finite support/opening evidence. C89→9b changes six door-return meshes and the pool lining; 9b→79e changes the pool lining; 79e→f79d changes four station-prop meshes; f79d→5fd changes the hoist trolley plus adds remote drum clamps/inspection opening; 5fd→677c adds the local 1.2 W tasklight at the hoist anchor. None changes the gantry ladder, fixed head ties, foot seats, platform landing or guard opening. The final added light is remote from the ladder (x≈−6.5 m versus x=7.17 m) and is aimed at hoist clamps. Carry #120 is limited to the fixed access-route/landing/gate subject and does not claim dynamic-gate sweep. The C89 images keep their original source identities.

## #74 D1 lane-wear bounded carry

The accepted image is the original 9b full-quality view69 at `/workspace/scratch/reactor-refinement-next-corrections-working/proof/green/69/69_floor_doorway_travel_wear.png` (image SHA-256 `b1f0b83ad62900a5253fd3fdb95e4db12dd956495d81839ecd6e5f1e179d76f1`; manifest SHA-256 `5f0a8940c5d06833b5f5a15ac610e57daf2a6708e9863ad2fdf85522de7120f6`). It shows irregular longitudinal scuffing from the D1 threshold toward the route arrow within the marked lane. It is distinct from chipped paint and cracking. The source/image identities remain 9b. The first four exact delta legs preserve the viewed floor wear material/geometry, camera and prior lights. The final 5fd→677c leg adds a 1.2 W hoist-aperture tasklight aimed at the clamp faces; it is spatially remote from the D1 lane. This narrow carry does not claim that all lighting is unchanged and accepts no wear outside the pictured D1 movement path. See [`LUNA_9B_TO_5FD_ISSUE74_TRAFFIC_WEAR_REVIEW.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_9B_TO_5FD_ISSUE74_TRAFFIC_WEAR_REVIEW.md).

## #86 pool-wall staining-origin bounded carry

The accepted pixels are the original 79e full-quality view21, not a 677c render: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/working-originals/reactor-refinement-pool-readability-working/1.0/21_pool_depth/21_pool_depth.png` (image SHA-256 `7d45c81b5aa0ee74ee0be8b5ed428056cb9ae0fd4647416bb0d18e8346d3ec15`; manifest SHA-256 `bd480ac5c7d881811444e59c8a08c43829431b8cabd603be9793458a7c9b82cf`; 79e source SHA-256 `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c`). At native resolution, the localized warm deposits read as irregular downward traces from the upper liner grout/course toward the 3 m course. This is a restrained, frame-limited acceptance; it makes no claim about hidden liner surfaces or every authored mark.

The exact five-leg chain in this report leaves the pool-liner subject unchanged after 79e. The final 5fd→677c change adds a 1.2 W tasklight at the remote hoist aperture, aimed at the clamp faces. This does not assert that all lighting is unchanged. The carry accepts the pictured 79e stain appearance only; it does not close #88 state comparisons or #90 service-port construction. Full details and the original source/image identities are in [`LUNA_677C_ISSUE86_79E_BOUNDED_CARRY.md`](LUNA_677C_ISSUE86_79E_BOUNDED_CARRY.md).

## #140 finite 677c geometry scope

The current/cold 14-check sets and independent control-room checks pass; cold owned scope is 93/93 declared comparisons. The current audit reports 203 signage samples/0 blocked and 3473 sampled support records/0 failed, with 290 protected objects unchanged. The independent tasklight probe verifies the three additions, their material assignment, closed topology, registered seats, parent-relative motion, and the aimed local light. This does not claim exhaustive collision coverage, full-scene equivalence, or a final quality score. See [`LUNA_677C_GEOMETRY_AUDIT_140.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_677C_GEOMETRY_AUDIT_140.md) and [`LUNA_HOA_677C_TASKLIGHT_REVIEW.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_HOA_677C_TASKLIGHT_REVIEW.md).

## Reopened scopes

- **#108:** C89 views26/27/28 and historical C82 view52 remain source-bound composite pieces only. Re-review them against the exact 677c added clamps, aperture and tasklight; view70 must show the new retention clearly.
- **#133:** the source chain adds door-return staining and the local hoist light. Current wall/light appearance needs exact 677c pixels.
- **#136/#137:** the pool lining, door returns, and moved switchgear props affect the prior material/wear combination; final-source mains must be reviewed.
- **#116:** pending exact 677c full-quality view70; the preview only approved the camera and local light.

## Pending coverage plan

| Issue(s) | Current proof needed | Prepared route / gap |
|---|---|---|
| #17, #19, #20, #139 | Corrected switchgear face and surrounding sign strips after bollard relocation; room-wide intended-view audit | Exact view13 is needed. It is absent from the prepared 01–10 + 70/71 queue. Add current full-quality view13. The finite 203-sign sample is not a substitute. |
| #108, #116 | Upper drum end clamps, rope seat, washers/bolts, opened hood and readable continuation of hoist load path | Full-quality exact 677c view70 is prepared. Recheck C89 views26/27/28 and historical C82 view52 only as their original-source partials; the five-leg deltas must support the composite. |
| #120 | Ladder feet, top transfer, landing and guarded opening in one safe access composition | No current 16/25 proof is prepared. Add a direct current view16 or a measured wider access view if mains do not show the whole route. |
| #122 | Wall, plinth, threshold and adjoining floor transition | Review current09/10 first. If the base seam remains cropped, add a low-angle full-quality wall-base camera. |
| #125, #133 | Door-return staining against neutral wall/reveal and local wall illumination | Current09/10 are the first sufficient routes; no full 677c pixels yet. |
| #127 | Upper pane frame/recess and reveal depth | Review current09/10; add a direct pane view only if the framing does not show the actual recess. |
| #128 | Upper wall-post head, bracket/seat, and receiving girder in the same readable frame | Current08/09 give broad context; prepared70/71 do not target this interface. Prior main07/08 review found bearings too small/dark. The saved 677c audit places a representative north/east post at (3.6,10.54), with column-head anchors at x=3.53–3.67, y=10.47–10.61, z=16.56 m and beam seat z=16.60 m. If current08/09 remain unreadable, preflight a camera aimed at (3.6,10.54,16.85) from near (2.9,9.2,17.3), 30–35 mm; this proposed pose is unvalidated. |
| #129 | Wall-box body, standoffs and actual host surface | Inspect current09/10; add a direct wall-box view only if body-to-host attachment is too small to judge. |
| #131 | Typography quality across the unresolved label families | No specific curve/spacing defect has been established. Current13 and planned17/18 plus the prior direct text evidence are needed; 93 saved FONT objects had no degenerate-area finding, but that alone is not a visual acceptance. |
| #132 | Doorway task-light housing, mount, and useful target illumination | Inspect current09/10/18. The new 677c hoist aperture light is not the doorway task light. |
| #138 | Integrated focal hierarchy on the final corrected room | All ten current 01–10 views are required. No separate concrete composition defect is established from C89. |
| #136, #137 | Current response distinctions and wear after pool/door/switchgear changes | All ten current mains; retain the historical oil image only as scoped unchanged-surface evidence. |
| #88 | Pool-state behavior | Final-source state-comparison frames must be scheduled; no state set is in the prepared 70/71 + main queue. |
| #80, #82, #90, #97, #99 | Rail intersections/feet, actual sleeve/penetration, and bank corner/conduit entries | Current04/11/21 and actual-source contact/port probes first; #97/#99 require targeted bank macros if current broad views do not show their interfaces. The current queue lacks direct 66–68-style bank connection views. |


The prepared queues currently contain ten main views01–10 and focused views70/71. Exact view13, view16/25, pool states, bank-joint detail, and an upper wall-post/girder bearing close-up are not in those queues. Review the current mains and prepared views first; add focused cameras only where those images leave the specific interface cropped or too small.
