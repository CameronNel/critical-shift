# Astra independent visual review — full03

Date: 2026-09-11. **Completed visual verdict: FAIL.** All 16 actual PNGs were inspected after the batch completed. Fifteen contain assessable scene imagery; D05 is effectively black and cannot provide the required mechanism evidence. The visible scene also remains below 90 in art direction, hierarchy and lighting. The engineering pass is not art credit.

## Evidence and scope

Inspected C01–C10 and D01–D06 directly from `production/renders/review/full03`, at their supplied 1440 × 960 resolution. Independently verified that all 16 file hashes match the completed render manifest; recorded them in `astra-full03-image-hashes.json`. No view was scored from a change description or carried forward without opening its current image.

Reopened actual reactor A05 and mine entry/heading/sump reference viewing copies, plus the actual approved `C07-full01-crossing-r02.png`, `C08-full01-bypass-r01.png`, `C09-full01-reactor-door-r01.png` and the C06 staging paintover viewing copy. Relevant comparisons are material treatment, manufactured detail, destination hierarchy, functional specificity and illumination. The connector is not required to reproduce mine rock or unrelated reactor machinery.

The full03 manifest identifies 7,679 objects and blend SHA-256 `1faf3c9fa16133081916bc1c9bc235e866e0507b9aa645e997aee340055d146a`. Frozen build/detail/interface hashes and all camera definitions agree with eng06. The ten formal camera definitions are unchanged from full02. **D05 is the disclosed new diagnostic framing baseline**, not a pixel-identical comparison with full02's D05. Its failed new image is assessed as delivered.

## Criterion scores

These scores judge the assessable pixels independently; they are not averages of view scores. The unusable D05 is a separate evidence failure, not an invented score for unseen geometry.

| Criterion | Score / 100 | Observed basis |
|---|---:|---|
| Human scale | **91** | Doors, rails, bench, carrier, controls and the complete large reactor opening have plausible relationships. D04 establishes the whole tall portal. |
| Circulation — visible spatial reading | **90** | Freight and service widths read distinctly; staging stays peripheral; floor arrows explain the turns. This is visual assessment, not a replacement clearance audit. |
| Required equipment | **91** | Carrier/restraints/brakes, service air, workbench, distribution hardware, emergency provision and destination doors are visible. D05 cannot independently establish its intended mechanism subject. |
| Logical flow / wayfinding | **90** | Reactor/service wall destinations are now unobscured and readable; the two blade signs name previously weak branches. Refinery, waste, plant and reactor approaches have clear identity. Freight priority from C01 remains weaker than the service path. |
| Shape / art direction | **89** | The staged carrier and utility equipment have specific manufactured forms. Reactor borders improve the leaf construction, but the large door fields, sparse repeated plates and thin type still look considerably simpler than the approved C09 treatment. Broad route bays remain comparatively uniform. |
| Hierarchy | **89** | C02's destination and C03's staging focus work. C01 still emphasizes SERVICE straight ahead; the dark plant sign and reflective clean sign have weaker visual priority than their lighting fixtures. D04's header also loses contrast in its bright pool. |
| Material separation / tactility | **90** | Concrete, wall coating, painted steel, bare hardware, rubber, enamel, textile, brass and filter glass separate convincingly in the usable views. Close props carry stronger tactile detail than the broad door fields; those fields remain a weaker part of the reference match. |
| Lighting | **88** | The recess task light successfully reveals D06's station. Across the route, uneven sign exposure remains: C07's plant blade is backlit/dark, C08's clean blade has a strong white reflection, and D04's header is washed. This score is based on visible lighting conditions, not an assumed cause for the black D05. |
| Color | **92** | Off-white, cool grey, dark metal and restrained orange remain consistent. Warm practicals and cooler structure fit the approved palette. |
| Environmental storytelling | **90** | Checked payload, park controls, maintenance tools, consumables, permit paperwork, first aid, distribution equipment and named destinations now establish a coherent handling/service setting across the route. Some repeated door/plate treatment still feels generic. |
| Technical correctness | **Not numerically rescored** | No CPU geometry replay was requested for this visual review. The separate eng06 targeted engineering pass remains bounded; it does not approve this image batch. D05's failed rendered evidence is independently confirmed below. |

No average overrides a criterion below 90 or the unusable diagnostic evidence.

## Per-view visual scores

Each score is a holistic judgment of the visible view's clarity, finish and success at its stated purpose against the references. It is not a geometric clearance score or an arithmetic category average. N/S means scene content is unavailable for an honest art score.

| Actual view | Score / 100 | Principal assessment |
|---|---:|---|
| C01_ENTRY | **88** | Clear staging glimpse and plausible corridor; straight SERVICE alignment dominates the entry while the freight continuation remains visually weak. |
| C02_PRIMARY_ROUTE | **90** | Readable, unobscured 04 / REACTOR identity, purposeful light and floor turn cue; adequate functional focus. |
| C03_HERO | **91** | Coherent carrier/bench/service composition and legible freight/service split. |
| C04_REVERSE | **90** | Refinery return is clearly identified; restrained, readable approach with comparatively plain repeated wall finish. |
| C05_EAST_TURN | **90** | Waste and reactor destinations distinguish the branch and continuation. |
| C06_REACTOR_THRESHOLD | **88** | Identity and new border construction read, but broad smooth leaf fields and sparse generic secondary detail fall short of approved C09 at this close range. D04 supplies the complete-portal coverage absent from this crop. |
| C07_BYPASS | **89** | Service identity is strong and plant destination is now readable; the plant blade is markedly dark/backlit despite the adjacent bright fixture. |
| C08_SERVICE_JUNCTION | **88** | Clean/medical destination is now present and readable in context, but white glare on the blade reduces letter/background contrast. |
| C09_MATERIALS | **92** | Clear enamel/metal/rubber separation and identifiable restraints, lifting eyes, carrier deck and checked tag. |
| C10_PLANT_HEADER | **90** | Plant identity and permit board give a clear operating destination; construction remains simple but coherent. |
| D01_CARRIER_OPERATION | **92** | Restraint hardware, orange brake controls, wheel assemblies and payload support have readable relationships. |
| D02_WORKBENCH | **90** | Material variety and worker equipment are clear. Coarse glove weave and neatly arranged contents remain minor limitations. |
| D03_UTILITY | **91** | Gauge, valve, regulator, glass bowl/core and hose mounting show useful functional and material detail. |
| D04_REACTOR_WIDE | **89** | Complete portal proportions and destination are established; uniform broad leaf finish and low-contrast bright header limit the presentation. |
| D05_GATE_MECHANISM | **N/S — unusable** | Effectively black. No honest shape, material or mechanism score can be inferred from this image. |
| D06_SERVICE_RECESS | **90** | Task lighting reveals station identity, gauge, regulator, metal pipe and hose. The inlet still partly overlaps the heading, but the former concealed/dark-board failure is substantially resolved. |

## Important remaining defects

1. **Critical evidence failure — D05 is nearly black.** Independent PNG verification and full decoding succeed. All RGB channels are only **0 or 1 out of 255**; **91.79022%** of pixels are pure black, and mean encoded luminance is **0.08210/255**. This is a failed image, not a preview-decoding problem. No gate motor, bracket, housing or other mechanism can be assessed. Its cause was not investigated or inferred. Hash: `698ed4a4a9d20f74de803309812c86db5829b6687f86fc184d50608ac0bc5e26`. See `astra-full03-evidence-check.json`.

2. **Moderate — branch signs have inconsistent exposure (C07/C08; supporting D04).** C07's PLANT SERVICES blade is dark against the bright fixture behind it; its grey lettering has limited contrast. C08's blade has a strong white reflection across its right portion, reducing the clean/medical lettering's contrast. D04's reactor-approach header is similarly pale in a bright pool. Destinations are much better communicated than before, but lighting does not yet reveal them with the consistency of the approved references.

3. **Moderate — freight priority is still weak at entry (C01).** SERVICE is the strongest forward destination, reinforced by the long straight sightline and the distant service graphic. The carrier suggests freight use, but the freight continuation is mostly outside the visible emphasis. This is a reading of the supplied image; no absence of signage elsewhere is inferred.

4. **Moderate — reactor close-up remains visually sparse relative to C09 (C06/D04).** The new chamfered borders establish more construction, but the broad grey surfaces are smooth and uniform, the small repeated access plates carry little differentiation, and the principal type is much thinner than the approved door reference. Localized finish and handling cues are weaker than the reference's integrated panel/hardware/marking treatment. This observation does not prescribe replacement geometry or exact copying.

5. **Minor — secondary props can feel presented rather than used (D02).** The glove weave is prominent and the bench contents/tools remain neatly arranged. Their identities and materials still read; these are smaller concerns than failed D05 coverage and destination-lighting problems.

## Established progress and conclusion

C02 and C07 now communicate their forward destinations without the former post/seam obstruction. C08 and the plant turn have named branches. D06 now exposes service-air function and materials. Reactor borders add a readable manufactured layer. Carrier, bench and utility details remain coherent. These improvements are visible and were judged independently; they do not establish that the remaining deficiencies are acceptable.

The batch has been completely reviewed, but it is **not a passed or stable final visual cycle**. The black D05 prevents complete usable diagnostic coverage, and art direction, hierarchy and lighting remain below 90. This report performs no render, scene edit, geometry probe or neighbor operation and makes no claim about future corrections.
