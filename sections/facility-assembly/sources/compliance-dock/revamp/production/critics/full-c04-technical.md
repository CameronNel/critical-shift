# Cycle 04 independent technical verdict

Category 8: **92/100 — FAIL** against the strictly greater than 93 category gate. This is a category verdict, not an overall eight-category score. Frozen revision f09 must be repaired before claiming the owner’s 99/100 acceptance.

Reviewed native: `module_overhaul_R1.blend`, SHA-256 `2820ac1c7a79a28d739d0b953d73b4490f264c119775eeeef37c46bf6792a7c6`. Blender 5.2.2 LTS. All critic native reads used one thread, never saved or mutated the scene, and all native handles/processes are released. The final filesystem hash remains identical.

## Definite defect

The manifest writing surface penetrates its flat text. All four retained FONT objects have zero extrusion and lie at Z 1.054000020 m. `Counter manifest paper` extends from Z 1.050999999 to 1.056986690 m. The curled corner changes the triangulated top face across the writing area; the native writing surface is not flat where the recipe comment says it is retained.

| Object | Buried sampled glyph vertices | Actual signed surface gap |
| --- | ---: | ---: |
| Manifest header — DUTY CLEARANCE | 225 / 501 | −1.646161 to +0.995159 mm |
| Manifest line 1 — SECTOR 04 / ARRIVAL | 18 / 772 | −0.340462 to +0.994802 mm |
| Manifest line 2 — CUSTODY 731-A | 0 / 733 | +0.265121 to +0.995278 mm |
| Manifest line 3 — RELEASE DENIED | 0 / 511 | +0.655532 to +0.996232 mm |

The faint, truncated headline in `C03_CHECKIN_COUNTER` and `DETAIL_CHECKIN` corroborates the native penetration. This is not explained away by distant pixels or ink contrast. Paper and ink have sufficient nominal value difference; the actual geometry occludes the ink. The assembly support validator does not test glyph visibility and its PASS cannot override this finding. Repair the actual ink/paper relationship, measure every affected glyph again, and rerender both fixed views. No critic scene edit was made.

## Static technical evidence

All 1,077 original objects remain with unchanged original world matrices. All five protected input hashes and pinned recipe hashes match. Final evaluated authoring counters are 367,216 triangles, 1,148 material submeshes and 36 used local material names/families, within the stated 450,000 / 1,150 / 36 planning targets. Baseline triangles were 297,672. There are 1,147 final geometry objects and 1,316 scene objects. Counters are authoring measurements, not engine draw calls or FPS.

No missing dependency, exact cross-object duplicate triangle, collapsed geometry face or consumed-UV coverage error was found. The UV audit consumed 1,095 object/layer rows. Metric tiled charts are intentional and are not being presented as packed lightmaps. Continuous tarp charts have local edge scale approximately 0.848–1.085 and aggregate area near one; the checker image shows continuous cloth mapping. The four UV diagnostics and four neutral diagnostics show no additional definite technical blocker.

The project validator independently passes seven checks with zero errors and one warning: inherited substantial architecture has false/missing circulation-solid metadata and is conservatively included. There are 44 registered supported assemblies and 91 real anchors. This metadata warning remains recorded rather than discarded.

Focused P2 probes inspect actual internal islands rather than joined-object ancestry. All four hanger, headed/grooved axle, split spring and annular roller assemblies are closed, manifold, consistently wound and have positive centered volume. Hanger feet meet the actual leaf top Z 3.48000002 m; rollers meet the actual lower rail surface Z 3.51999998 m within float precision. Each hanger has 75 lower-web interior samples, no rail-solid intersection witness and minimum sampled slot clearance 7.1001 mm. Bore sampling gives positive hanger/roller clearances approximately 0.3544–0.7729 mm. Clip-to-groove minimum sampled gap is positive at 18.8 µm; its missing angular sectors are the deliberately modeled spring split. Head/hanger contact gap is approximately 0.122 µm, and roller rear to spring front gap is zero. Brass key fronts lie 2.500 mm behind the actual glazing rear, with no pane intersection. These are static construction results; swept/open poses and load capacity are unverified.

The original preparatory rail/hanger collision was a real source-code defect, corrected before this frozen revision. Its initial source hash and findings remain archived; they are not mislabeled as a defect in f09. A front-opening rail proposal was subsequently replaced by the measured enclosed bottom-slotted track. No structural critical blocker remains established in the final static mechanism.

## Pixel inspection and limits

Every one of the 27 beauty PNGs was separately opened and received at its actual 1067×600 source resolution with original detail, including every mandatory camera, four corners, four walls, five hero subjects, the check-in detail, reverse/pinch player views and office-front elevation. All eight UV/neutral sources were separately opened at 1067×600. All four approved spawn references were separately opened at their actual 1280×720 resolution. Full-resolution sheets were supplemental; the conclusion does not rely on thumbnails. All 35 current render image hashes and three completed manifests were independently verified against frozen f09. The manifest defect is the only additional definite technical pixel failure found.

The P2 captive mechanism is largely concealed by the sign in beauty pixels, so static support is earned from actual measured native topology and contact, not an apparent silhouette or object name. Other inspected images reveal no newly demonstrated missing texture, unsupported primary assembly or malformed checker coverage. That statement is limited to this finite evidence, not a universal proof of every triangle.

The current native was independently cold opened, but the prescribed cold-open/render comparison is not established here: all three supplied cycle-04 render manifests report `cold_open=false`. Prior critic scores/reports were deliberately not read; this audit cannot independently certify four full cycles or final-two material stability. Runtime collision/navigation, dynamic P2 sweeps, structural capacity, FPS and draw calls remain unverified and must not be reported as PASS. These are limits, not invented engine failures used to reduce the score.

## Audit provenance

Raw findings and scripts are archived beside this report: `native-independent.json`, `independent-uv.json`, `validator-independent.json`, `mechanical-native.json`, `manifest-paper-ink.json`, `numerical-summary.json`, `pixel-inspection-evidence.json`, and their logs. `verdict.json` carries the machine-readable category decision.

Initial diagnostics had three numerical/caller defects which were corrected transparently: library paths were already rebased and needed direct resolution; a 1e-7 m ray step was below world-coordinate float precision and was replaced with 2e-5 m; small-part signed volume needed centered accumulation. One combined invocation used the obsolete interface path and failed; the existing validator was rerun with `contracts/interface.json` and passed. The preliminary output is retained, and none of those initial artifacts is asserted as a native scene defect.

## Raw packet links

- [pixel-inspection-evidence.json](full-c04-technical/pixel-inspection-evidence.json)
- [native-independent.json](full-c04-technical/native-independent.json)
- [independent-uv.json](full-c04-technical/independent-uv.json)
- [validator-independent.json](full-c04-technical/validator-independent.json)
- [mechanical-native.json](full-c04-technical/mechanical-native.json)
- [manifest-paper-ink.json](full-c04-technical/manifest-paper-ink.json)
- [numerical-summary.json](full-c04-technical/numerical-summary.json)
- [read-only-audit.log](full-c04-technical/read-only-audit.log)
- [mechanical-native.log](full-c04-technical/mechanical-native.log)
- [manifest-paper-ink.log](full-c04-technical/manifest-paper-ink.log)

Read-only probe sources: [native_probe.py](full-c04-technical/native_probe.py), [uv_probe.py](full-c04-technical/uv_probe.py), [mechanical_probe.py](full-c04-technical/mechanical_probe.py), [manifest_probe.py](full-c04-technical/manifest_probe.py), [static_recipe_probe.py](full-c04-technical/static_recipe_probe.py).
