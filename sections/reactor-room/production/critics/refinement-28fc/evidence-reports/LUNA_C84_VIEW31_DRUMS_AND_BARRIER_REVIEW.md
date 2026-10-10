# C84 full view31: drums, spill pan and barriers

## Provenance

- Candidate: `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`
- Candidate SHA-256: `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`
- Image: `/workspace/scratch/reactor-refinement-cycle84/inspection-720p/31_props_drum_group.png`
- Image SHA-256: `ca70652e1f16ee719820bc3541d362af29bba5aed105e2dd014900bde9dca811`
- Manifest: `/workspace/scratch/reactor-refinement-cycle84/inspection-720p/render_manifest.json`
- Render: Blender 5.2.2, Cycles CPU, 1280×720, 96 maximum/32 minimum adaptive samples, threshold .015, 12 bounces, path guiding 64, OIDN, 16-bit, exposure 0.

## Dispositions from the image

- **#43 — Drum reinforcing hoops and proportions: accepted.** The two rolled hoops on the visible drums read as narrow beads, with clean highlights and no broad swollen bands. Their size is proportionate to the 0.88 m shells. Current saved profile probe confirms 18 mm-wide/6 mm-projecting bands and 48-sided shells; the pixels show the resulting silhouette, not just the dimensions.
- **#44 — Drum bung and lid construction: accepted.** The recessed lid steps and two separate plugs are visible on the foreground tops, with raised rims and dark centers. They are distinct fittings, not flat dots painted on the shell.
- **#45 — Yellow drum fitting proportion: accepted.** The two small top fittings are in proportion to the yellow shell and match the other drums; neither dominates the lid.
- **#46 — Drum steel material response: accepted for this group.** The galvanized shell carries a restrained mottled metallic response; red and yellow read as coated shells with a softer satin response. The hoop highlights remain distinct and there is no broad mirror glare or plastic-like single gloss across all three finishes.
- **#47 — Drum identification: accepted for the inventory-label system.** DR-10 and DR-11 are legible on the aisle-facing galvanized and yellow drums. The current source names thirteen plaques DR-01 through DR-13; the exact C84 signage audit has a separate record for each with 100–185 glyph samples and 0 blocked samples. This image does not show every far-side label at once; acceptance is supported by the readable native pixels plus the bounded per-label face/obstruction records, not a claim that all thirteen labels fit in this camera.
- **#48 — Drum grouping and contact: accepted.** Four drums are visibly grouped on one open grate pan; their bases sit down inside its perimeter rather than appearing scattered or floating. The current finite contact audit includes the registered drum and pan interfaces with no failed sample; this is not an all-pairs collision proof.
- **#53 — Barrier frame/support construction: accepted.** The left-side barriers show continuous upper/lower rails joined to uprights, plus separate weighted feet/plates. The feet visibly meet the floor; the assembled frame does not read as disconnected bars.
- **#57 — Containment tray construction: accepted.** The raised yellow perimeter, open grate slats and grouped drum placement read clearly as one spill pan at full resolution. The pan is not a solid slab disguised as an open tray.

## #136 bounded material-family response

C84 full31 closes the changed drum-material part of #136. The older C79 full01/full02 images remain historical support for the other room material families. Their original source was C79 SHA-256 `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b`; full01 SHA-256 `82d14ffa3cd1f44100e4fff758b18ef79c67caa87924f4c93d7d80d0d336403d` and full02 SHA-256 `fd50d9e7c9ac0dd0cfbefd1ec3c3620ecd020a287ad30b056d66d924eb854bc1`. Their preserved images are [full01](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79-superseded/main-720p/01_machinery_turbine_grid.png>) and [full02](</workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c79-superseded/main-720p/02_machinery_coolant_eccs.png>). The exact C79→C82 cumulative comparator `/workspace/scratch/reactor-refinement-cycle82/cumulative-c79-scene-delta.json` reports the crane identity and six door-leaf meshes changed, three crane identity objects added, and 1,910 unchanged; it does not report other room-material or camera changes. The C82→C84 comparator `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json` changes exactly the five drum meshes, with 1,915 unchanged and no additions/removals. Current C84 view31 therefore verifies the red/galvanized/yellow drum response after that change. This is a bounded combined-source acceptance, not a claim that historical images are C84 renders or that every material in every room region has been photometrically measured. See also [the earlier C82 bounded material-family review](LUNA_C82_MATERIAL_FAMILY_RESPONSE_CARRY.md).

## Still open in this frame

- **#54/#55 — Bollard mounting and cap/finish:** No bollard is in this composition. Do not use it to close either issue.
- This image does not close unrelated cone (#49–51), stool (#56), whole-room prop/material hierarchy, or overall-area scoring criteria.
