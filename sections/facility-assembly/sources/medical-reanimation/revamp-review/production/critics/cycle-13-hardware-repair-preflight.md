# Cycle 13 hardware repair preflight

**Bounded geometric repair clears the 28 previously floating hardware pieces.** No formal score or acceptance is assigned. No confirmed blocker remains within the checked repair scope.

Current source SHA256: `4da6305df4b0618012696bf29baa82db2a9a625511e10ede0afc7ef442937ac7`. Source remained unchanged. All cycle 12 evidence is preserved.

## Direct measurements

All 28 previous hardware IDs were matched and independently checked. Signed contact gaps range from -0.000249 to 0.500908 mm; normal deviations are 0 degrees, and actual part-surface witnesses pass. These are directed contacts to the intended components, not an overlapping bounding-box inference.

Both lower pressure heads now have contact points on the vertical guide faces with world normals `(0,−1,0)` and `(0,+1,0)`, at Z 0.865588 m and 0.868000 m. Their rooted paths are head → guide → backing → original formed service panel. Diagnostic plugs route plug → port → backing → original panel. Drawer pulls and bolts route through face → carcass → original bench apron. Cabinet bolts contact the matching sliding pane at approximately 0.5 mm gaps.

All **130 declared part contacts** across eight joined assemblies pass independent raycast, normal, actual own-surface witness and acyclic support-path checks. Every declared path reaches inherited room geometry; any intervening new whole group traverses its separately checked support registration.

All **60 body-bag part contacts** are now rooted. The fold sequence is fold 4 → fold 2 → fold 0 → sealed chamber pan, with binding, closure teeth, slider/pull and webbing attached through those supports. Bag signed gaps range from -0.000019 to 3.651947 mm; normal deviations are 0 degrees; maximum own-surface witness distance is 0.296569 mm. The broad 1,825-island contact scan no longer flags the formerly unresolved bag group.

## Preservation and regressions

The independent replay also passes 102 group supports / 111 anchors, ten sewn-surface objects / 10,362 vertices and 26 declared case/battery print components / 8,638 vertices. There are no unexpected changes among 1,203 inherited layout objects; the original map, medical module and approved spawn hashes remain unchanged. Added geometry leaves the reserved lane clear. All 1,126 mesh objects have consistent winding with no inward closed components or exact duplicate world geometry. Evaluated triangle count remains 433,314.

Named UV consumers remain available, and the 34 material/assigned-face UV records contain no missing layers, nonfinite UVs or degenerate consumed faces. The exploratory print scan compares 36 objects / 19,358 vertices against cycle 12: no outlier-count changes and zero maximum-gap changes. The prior print/substrate qualifications persist; these results establish **no measured regression**, not exhaustive proof for every unregistered printed island.

Fresh saved-source opens under Blender 5.2.2 LTS resolve all 25 linked libraries and all 124 packed FILE images with nonzero pixels.

## Coverage qualifications

The two fabricated cabinet faces retain 14 INT point part IDs each, while each has four individual bolt contracts. IDs 0–4 and 9–13 on each face are not individually contracted. Their geometry appears attached in the broad scan, but the 130 declared anchors must not be described as complete coverage of all 150 present part IDs across these eight assemblies.

The only remaining broad nearest-sample candidate is tray trim island 74. It intersects `Inventory clipboard`; it is not classified as unsupported from sparse distances. The 15 prior exploratory printed-substrate qualifications also persist, including alternative original packaging substrates and intentional raised artwork/frame geometry. None is a new measured regression in this repair.

## Commands and limits

The exact successful commands are recorded in JSON. Four critic-owned scripts ran using:

`/workspace/tools/blender-5.2.2-linux-x64/blender -b --factory-startup --disable-autoexec -t 1 --python-exit-code 1 --python SCRIPT`

Scripts and logs live in `/workspace/scratch/medical-cycle13-hardware-independent`: `probe.py`, `part_contract_probe.py`, `uv_print_probe.py`, `followup.py`. Every command exited 0. No source, builder, art or native file was edited or saved; only new critic-owned scratch and reports were written.

This preflight does not replace fresh full hot/cold renders or formal critics. No renders or full rebuild were launched. Contact witnesses are appropriate to thick hardware; every outer vertex need not touch backing. Global intersection/penetration, runtime collision, Unity import, interactions, host/network behavior, navmesh, runtime draw calls and performance remain untested. No score, promotion, merge or runtime acceptance is assigned.
