# Compliance dock s06 — independent local technical review

**LOCAL TECHNICAL FAIL.** Two exposed, partially coincident jamb/wainscot surfaces remain in the submitted slice. The existing validator passes its five applicable static checks, but its exact-duplicate test does not detect these partial overlaps. Full-room scores, full-room acceptance and runtime performance are unscored.

Reviewed immutable source: `module_overhaul_R1.blend`, scene `COMPLIANCE_EDIT_LOCAL`, SHA-256 `a78d03bb5822ce0133cac551ee6e81151e8d7643a9b66050c2c1f9940561e34f`. Fresh processes opened the selected baseline and the saved s06 source with auto-execution disabled. No source, builder, material, camera or render was edited or saved by this critic. Witness files are confined to `revamp/production/critics/slice-s06-technical*`.

## Required repair

| Objects | Confirmed geometry | Action |
| --- | --- | --- |
| `D1 frame jamb -1` / `Office front wainscot west` | Same-facing positive-area overlap on outward plane **Y = 3.500000 m**, approximately **0.0911882 m²** | Remove redundant wainscot volume behind the jamb, or otherwise create a real noncoincident construction joint while preserving the inherited matrices and combined envelope/opening. |
| `D1 frame jamb 1` / `Office front wainscot mid` | Same plane and approximately **0.0911882 m²** | Apply the equivalent repair on the other side. |

This is not an AABB inference. Independent triangle clipping measures positive area, and six rays at X = −5.97 / −4.83 m and Z = 0.20 / 0.50 / 0.90 m return **both** relevant objects at the identical point, distance and outward normal. They are tied first surfaces from the apron. The objects have different material families (`CD | charcoal` and `CD | navy`), so retained coplanar faces can produce unstable shading. The defect is in the reviewed wall/door slice even though inherited construction caused it. The door and lower-wall regions in the fixed views are the affected pixels; a quiet beauty frame does not remove this geometric defect.

The wider coplanar witness also records hidden/mating overlaps: undersides at the floor, sill/leg/gusset tops below the worktop, linoleum/grille-bottom undersides, a concealed handle-wear back, and transom/trim end surfaces. Those are not counted as additional visible blockers without exposure evidence. This review does not assert that all arbitrary intersections are absent.

## Independently verified

- **Ownership and protection:** all 1,077 inherited object matrices are retained, with no missing original object. The five protected inputs match their recorded SHA values: canonical map, selected module, frozen accepted module, interface contract and approved spawn module. Every editable-scene object/datablock is local; the map remains a read-only relative library dependency. All 25 library paths resolve. The existing validator checks 119 image resources without errors, and witness font records resolve or are packed/builtin.
- **Intentional construction repairs:** the mid and east architectural piers each change height from **3.05 m to 2.35 m**, retaining their X/Y envelope, matrix and lintel datum. The counter slab receives a folded cross-section with the same footprint/top datum; the speaking ring becomes a correctly oriented cast grille; the stamp, pad and pen-holder bases extend to **Z = 1.042 m**; the form has a corner curl. Exactly these eight inherited mesh vertex clouds change at 1 µm rounding. It would be false to say every individual mesh dimension is unchanged.
- **Envelope and apertures:** the combined architectural bounds remain `[-7.1, -2.1, -0.2]` to `[7.1, 16.08, 4.44]` m. All other inherited architectural vertex clouds match at 1 µm. A separate 208-cell nominal front-wall occupancy check finds no envelope or aperture change. Existing external opening, scanner/cart, screen, service and office geometry outside the named repairs retains its evaluated vertex cloud. Thin bevel strips at the repaired pier/lintel junctions are not literally certified as an identical surface union: a much denser near-tangent ray partition gives unstable hits and local edge-profile differences, preserved in the witness rather than suppressed. This is preservation evidence, not full route/portal acceptance; the existing validator correctly marks full clearance not applicable to `slice`.
- **Topology and normals:** all 163 local authored/surfaced mesh objects are closed and consistently wound: zero nonmanifold edges, zero inconsistent manifold-edge winding, zero zero-normal faces, and positive signed volumes. The tiny key cylinder and six grille-slit bevels contain 96 numerical sliver faces below `1e-12 m²` in total count, totaling approximately `2.57e-11 m²`; these are cleanup observations, not a visible blocker or missing surface. No blanket mesh repair was performed.
- **Per-face metric UV:** all 163 meshes have `CD_Physical_1m`; 15,477 faces were measured, including 14,696 non-axis cap/slope/bevel faces. Coordinates are finite; no nontrivial face has degenerate UV area. All measured edge-length absolute errors are below **0.78 µm**. For edges longer than 10 µm, the largest relative error is **0.165%**, consistent with float rounding on tiny bevels. The apparent 40% relative error on the form is confined to sub-10 µm edges and does not establish meaningful texture distortion. Every local material UV node uses the named layer. Overlaps/repeats are intentional tiled face charts, not a unique lightmap/bake atlas. The checker images show useful coverage on door, reveal, trim and worktop faces; the numerical test covers caps and bevel strips hidden or too small in those views.

## Actual support paths

The paired rays in `slice-s06-technical-probe.json` test actual component surfaces, separately from root ancestry.

**Speaking glass/grille:** the grille contacts the isolation pad, which contacts the speaking glass. At both sides, glass and clamps interlock by 3.5 mm and clamps/stanchions by 9 mm; these are internal gripping/construction overlaps, not a floating supported prop. Each stanchion bottom contacts its base foot exactly, and each foot bears on linoleum within floating-point precision. Linoleum bears on the steel worktop, the worktop bears on both legs, and both legs contact the floor. The path is geometrically continuous. This proves static contact, not strength or clamp engineering.

**Tabletop items:** stamp base, ink-pad base and pen-holder base now contact linoleum exactly at Z = 1.042 m. Their collar/ferrule/shaft/knob, cushion and swivel components retain continuous mating connections; several internal socket overlaps are intentional. Clipboard penetration into the liner is approximately 1 mm, within the 2 mm external-contact tolerance. The form is within 0.016 mm of the clipboard at the sampled writing-plane point. Docket tray gap is 1 mm and rejected-paper gap is 0.5 mm, within the 5 mm support limit; those should be described as tolerance contacts rather than mathematically exact bearing.

**Cloth:** the underside projected area is approximately **0.025392 m²**. Actual exact contact is along boundary edges, including the registered left-edge and rear-right anchors on linoleum. No underside triangle centroid has a positive-area exact bearing patch; **0.014274 m²** of projected triangles have centroids within 5 mm of their support. The raised underside reaches approximately **16 mm** at sampled centroids. The front overhang targets the steel worktop rather than linoleum and is about 2–2.7 mm above it at tested edge points. Therefore the existing anchor pass proves real boundary contact, not that the whole rag lies on linoleum or has broad bearing area. A revised fabric shape should establish clearer contact patches and record both liner and steel support where needed. No unsupported ancestry claim is used to pass the cloth.

**Wall items:** plaque back, both light brackets and junction mounting back meet their specified wall surfaces exactly. Their assembly roots are registered. The existing support validator passes 20 assemblies / 48 anchors, but that result is not used as proof of every internal component path.

## Pixels actually inspected

All current-source manifests are complete and identify the same source SHA. No cutaway hides geometry in these slice views. Images were opened with the image-inspection tool, not inferred from filenames:

- Beauty: `renders/slice-s06/SLICE_ENTRY.png`, `SLICE_MATERIAL.png`, `SLICE_DOOR.png`. Inspected door/wainscot boundaries, counter edges, base contacts, grille and stanchions, plaque/light and junction/conduit regions.
- Checker: `renders/slice-s06-uv/SLICE_ENTRY.png`, `SLICE_DOOR.png`. Inspected wall/door/reveal/trim coverage, visible strip transitions and worktop top/front faces.
- Neutral: `renders/slice-s06-neutral/SLICE_MATERIAL.png`. Inspected stamp/pad/pen/clipboard bases, cloth profile, glass/clamp/stanchion feet and worktop contact shading.
- Spawn references: `renders/spawn-reference/VALIDATE_Spawn.png`, `BRIEFING_INDIRECT.png`, `VALIDATE_LockerDoor.png`, `VALIDATE_Material_A.png`. Used as material/construction calibration; they do not certify this dock.

The dock diagnostic/beauty frames are 1067 × 600, CPU Cycles, 24 samples, seed 8217, AgX / Medium High Contrast, exposure 0.7. The reviewer has not awarded visual category scores. The visible checker is diagnostic evidence, not final material approval.

## Commands and limits

Successful, from `/workspace/critical-shift`:

```sh
/workspace/tools/blender-5.2.2-linux-x64/blender --background --disable-autoexec sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/validate_dock.py -- --output sections/facility-assembly/sources/compliance-dock/revamp/production/critics/slice-s06-technical-validator.json --interface sections/facility-assembly/sources/compliance-dock/contracts/interface.json --expected-stage slice > sections/facility-assembly/sources/compliance-dock/revamp/production/critics/slice-s06-technical-validator.log 2>&1
/workspace/tools/blender-5.2.2-linux-x64/blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python sections/facility-assembly/sources/compliance-dock/revamp/production/critics/slice-s06-technical-probe.py > sections/facility-assembly/sources/compliance-dock/revamp/production/critics/slice-s06-technical-probe.log 2>&1
```

The witness was refined and rerun in fresh processes; the final JSON and script are the evidence. Both final Blender commands exit 0 under Blender 5.2.2 LTS. Validator: five applicable PASS checks, zero errors/warnings; full clearance is not applicable. Source SHA before and after the final witness matches exactly.

Preflight `git lfs pull --include='sections/facility-assembly/sources/compliance-dock/module.blend,sections/facility-assembly/sources/compliance-dock/accepted.blend'` failed because GitHub credentials are unavailable. This did not block this review: those files were already hydrated, their bytes match protection records, and the selected module was actually fresh-opened. No credential or remote configuration was changed.

No formal cold-render comparison was executed by this critic. The viewed render manifests say `cold_open: false`; fresh native loads alone do not complete that later production gate. Full-room cycles/scores, Unity equivalence, physics, navigation, moving-door clearance, runtime draw calls and FPS remain unmeasured. Current saved-source counters are 323,664 evaluated authoring triangles, 1,128 material submeshes and 43 used local material families across the mixed slice/inherited room; these are measurements, not runtime certification or approval of the full-room planning target.

**Next gate:** repair both exposed partial coincidences, rerun those geometric witnesses and the affected fixed beauty/checker views, inspect the results and obtain a fresh independent local review. Full expansion remains blocked.
