# Independent fresh review — R4

**Candidate:** `full-R4.blend`, SHA-256 `2ebf7d15af65d62b869e1d1b438f04b965cde4a0c95f3c87a898e6aebba8e364`
**Review basis:** user-specified spawn-room reference pixels; all 14 R4 formal views (C01–C10, W01–W04); all five R4 diagnostics; all five actual-map context views; and the named R4 technical/audit receipts. Visual points below come from the images. I did not read historical score, critic, rubric, or task-state files.

## Scores

Each normalized category must be strictly above 98. All seven clear at 99; the weighted total is 99.0/100. The total does not substitute for the category gate.

| Category | Normalized score | Weighted points | Pixel/evidence basis |
| --- | ---: | ---: | --- |
| Spatial/readability | 99/100 | 19.8/20 | C01/C03/C04 and map EI_C01/EI_C03/EI_C04 show the central route, work zones, and doors at legible scale. EI_W01/EI_W02 show the thresholds and continuation into the assembled map. No route obstruction is visible. |
| Construction/art direction | 99/100 | 19.8/20 | C02/C05/C06/C10 show constructed cabinet frames, inset controls, drawout assembly, transformer winding/cooling forms, cage, and transfer panel. The result uses restrained industrial colors and authored forms rather than relying on labels or flat boxes. Repeated feeder layout reads as standardized equipment; no repeated wear defect is established in C02/W04. |
| Machinery/hero fidelity | 99/100 | 14.85/15 | C05 makes the withdrawn breaker assembly and contacts legible; C06 identifies the transformer through its winding bands, spacers, and enclosure; C07 shows the sealed reserve cartridges, service faces, pull loops, terminals, and keeper rails; C10 communicates manual transfer state. DG02–DG04 resolve the stored leads, trolley, and meter details. I do not infer missing internals behind the sealed reserve trays. |
| Materials | 99/100 | 14.85/15 | Across C01/C06/C08/DG02/DG05, painted enclosure, structural metal, copper/oxide accents, ceramic, rubber, concrete, and the vision pane separate by value and response. The optical pair is supplemental and binds to R3 (`692f589b…`), not R4; it shows diffusion through the pane versus a sharp no-pane control. `legacy-compatibility-R4.json` records unchanged visible assignments, and the R3→R4 14-view comparison is pixel-identical, so I use it only to resolve the pane behavior, not as new R4 dressing. |
| Lighting | 99/100 | 9.9/10 | C01/C03/C04 provide readable route light and falloff; C05/C06/C09 retain useful contact shadows and practical-light accents. C07’s shadowed cavities remain distinct from the visible pale service faces and pull hardware. Some zones are more even than the spawn reference, but no evaluated feature is lost at its intended camera scale. |
| Story/dressing | 99/100 | 9.9/10 | C09/C08 and DG01–DG04 show a repair bench with active test pieces, meter/leads, clipboard, gloves/fuses, rescue equipment, and stored service leads. Wear is localized to contact areas. At wide views the bench details are subordinate, then resolve in close views; the room still reads as maintained and in use. |
| Bounded technical | 99/100 | 9.9/10 | `validation-R4.json` binds to the reviewed source and reports no failures: 318 protected geometry/camera items unchanged; 51 registered support assemblies with none unregistered; 303 sampled route positions across five routes with no defects; dependencies and manufactured-mesh checks pass. `candidate-audit-R4.json` passes containment and original-ID compatibility, with 128 inherited missing spawn-wrapper IDs unchanged and no new missing IDs/object data. `context-R4.json` binds all five context images to the R4 module and map candidate. |

## Camera-specific review and defects

No material defect remains that warrants a score below 99 in the defined categories. Specific checks:

- **C01/C03/C04 and EI_C01/EI_C03/EI_C04:** route and both portal approaches read clearly. The black portal fields in the portable-room images are resolved by the assembled-map views; they are not a room defect.
- **C02/W04:** feeder panels repeat the expected control arrangement, but visible wear varies by panel and no cloned damage pattern is apparent. The repeated controls alone are not a defect.
- **C05/C06/C07/C10:** drawout contacts/springs, transformer winding/cooling assembly, reserve service hardware, and transfer states remain identifiable. The shadow behind the sealed cartridges does not hide a required visible component.
- **C08/C09 and DG01–DG04:** service dressing reads as purpose-linked. Small objects recede in C09 but are legible in the close diagnostics; no random filler stands out.
- **DG05:** the pane itself has low contrast against the plain wall behind it, so this view alone cannot prove transmission. The controlled optical pair supplies that distinction; it does not justify extra dressing credit.
- **EI_W01/EI_W02:** the room’s portal frames meet the neighboring openings and route surfaces. The captured adjoining context is sufficient to judge the openings and immediate thresholds, not neighboring-art quality.

There are no required visual corrections before this R4 review clears the stated >98 category gate. Minor polish could add more local light falloff and bring the bench story forward in a wide composition, but neither issue obscures function or story in the designated views.

## Bounded acceptance

**R4 independent visual and bounded technical review: PASS.** The weighted 99.0 is reported for context only; every category independently clears the required 99 minimum. This is not certification of exhaustive collisions, Unity integration, navigation mesh, carried-body runtime sweeps, or FPS. Those remain separate gates. I am also not claiming a distinct same-hash cold-reopen test from the reports reviewed here.
