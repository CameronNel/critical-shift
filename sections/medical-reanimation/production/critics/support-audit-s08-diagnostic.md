# Support audit checkpoint — s08

8 September 2026. **Diagnostic FAIL; unfinished validator augmentation.** Work stopped at the user's usage-limit wind-down instruction. No geometry, visual, slice or section acceptance follows from this report.

The completed background Blender audit opened the saved `blender/style_slice.blend`, whose scene revision was `s08`, and called `register_supports(scene)` from the new helper. It did not save the in-memory registrations back into the `.blend`. The build script has not yet been wired to call this function. No job remains in flight.

| Observed audit result | Count |
|---|---:|
| Evaluated geometric objects | 304 |
| Explicitly classified objects | 203 |
| Objects with passing chains to structural boundaries | 91 |
| Named architectural boundary roots included in that count | 6 |
| Failed objects | 213 |
| Unclassified objects | 101 |
| Geometry evaluation errors | 0 |

This is a saved concise report from the completed run. The large per-object JSON was printed to the execution trace; a full JSON artifact was not saved by that probe. Counts include the diagnostic issues below and must not be treated as 213 independently confirmed modeling defects.

## Reliable measured repair targets

These direct surface gaps exceed the current 5 mm contact tolerance:

| Object family | Intended host | Observed signed gap |
|---|---|---:|
| Door removable panel screw, including numbered duplicates | Parked sliding leaf | 0.0080 m |
| Localized pull wear, several instances | Parked sliding leaf | 0.0075 m |
| Sliding leaf number | Parked sliding leaf | 0.0088 m at backing surface |
| Bin modest inventory mark | Pressed metal linen drum | approximately 0.0101 m |

Other diagnostics showed sampled penetrations, including bin rolled beads approximately 7 mm into the drum, the hinged lid approximately 6 mm into the drum, the hinge up to 20 mm and the pedal up to 38 mm into their proposed hosts. These are **inspection targets**, because the method currently uses sampled nearest-surface signed distance and some designed joints may require explicit construction changes or reviewed mechanical-engagement specifications. Do not raise tolerances merely to make an observed defect pass.

## Known validator work still required

1. **Coincident surface vertices:** Blender's evaluated curve/font caps and side surfaces can have duplicate coincident vertices with separate indices. Current component discovery uses vertex-index connectivity, creating false disconnected-component failures for physically coincident surfaces. Weld only coincident world positions for analysis, with a documented numerical tolerance around 1 micrometre; do not bridge real support gaps or alter scene geometry.
2. **Diagnostic candidate ranking:** A distant duplicate host with zero sampled penetration can sort ahead of a nearby host with real penetration. Passing-link selection still requires measured contact, but the first failed candidate can be misleading. Rank failed diagnostics by measured nearest-surface distance before penetration magnitude, and preserve every candidate's evidence.
3. **New authored names:** s08 added detail names absent from the initial explicit host table. Extend rules from the current source, including door-edge primer, kickplate scratches, bottle label/batch lettering and closed glove tips. Each still needs measured contact; a classification never waives the checks.
4. **Contact sampling:** Triangle/vertex surface anchors are finite evidence. Curved grazing contact and seams can be missed. Add deliberate authored anchors where surface sampling cannot establish the intended connection, while checking that each anchor really lies on the source geometry.
5. **Freshness integration:** `validate_geometry.py` now fingerprints evaluated world vertices and polygon topology and rejects missing, failed or stale support-chain evidence. This newly added integration was saved but not rerun after the wind-down instruction.

## Exact next bounded work

1. Read this report and the current `build_medical.py`, `register_supports.py` and `validate_geometry.py`.
2. Repair coincident-vertex component analysis and failed-candidate ranking before interpreting the remaining curve/text failures. Extend explicit host rules to all current names.
3. Verify the support helper with small synthetic fixtures covering a supported prop, a floating prop, excessive penetration, a floating connected cluster, a separate unsupported island, coincident curve caps and a stale geometry signature. These checks have **not** been run for the new support helper.
4. Run one diagnostic background Blender reopen and save its complete returned support JSON to that revision's review directory. Review failed anchors and support chains, then make the concrete geometry repairs indicated by the measurements.
5. Integrate `register_supports(scene)` after all geometry and dependency-graph updates and **before saving** the `.blend`. Retain the returned report in final validation, merge its `pass` as a required technical check, and preserve the helper's independent freshness gate. Rebuilding from factory startup must reproduce the same classifications and measured contacts.
6. Resume the mandatory review protocol only after the technical audit is defensible. The current slice/full-room expansion gate remains open; there is no exhaustive support PASS.

The new files do not modify physical geometry. Structural floor/wall/lintel/soffit names are explicit static boundary premises; all fixtures, trim, equipment, papers, signs, textiles and other components need actual contact chains. The audit does not establish physical load stability, attachment strength, cloth dynamics or runtime physics.
