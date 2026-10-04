# Waste Storage editable scene — R51 candidate

The room has sharp cast, pressed and folded construction, exhausted cool values, localized practical task pools, worn segregated equipment and supported traces of interrupted work. The freight spine stays clear. Seal-service tools, gloves, paperwork, a chipped cup, restraints and logging controls provide small human details without filling the route.

Open `../module_overhaul_R1.blend` relative to the overhaul directory. It matches the frozen `production/checkpoints/R51.blend` exactly, SHA-256 `4165b2ce869cc581e247c6110a91b8f7f4c6a97b5370f6744fb0f372fd5c669f`. Run `git lfs pull` after checkout. The original `../module.blend` remains SHA-256 `8912b5c3b3d2525abb64e838d1fe83a1ea90aa12fea0c9b5a730d4449caecedf`.

Blender 5.2 LTS, embedded procedural materials and modeled geometry are the dependencies. No image texture, linked library, HDRI, SUN or unmodeled fill is used. World illumination is zero; 26 modeled fixture/source pairs include three failed circuits and 23 active luminous surfaces. R51 has 3065 objects, 290 visible materials and 589943 evaluated triangles. These are authoring statistics, not measured runtime costs.

## Evidence status

Both independent pessimistic GPT-6 Luna full reviews ([A](critics/critic_a_R51.md), [B](critics/critic_b_R51.md)) PASS every category at 99 or higher: A weighted **99.00**, B weighted **99.10**. Neither found a critical veto or material regression. Each reviewer opened all 21 main views and both details against actual R49 counterparts and the Spawn/refinery references.

R51 hot and original-source cold expanded validation pass at 589943 evaluated triangles, with 335 new and 57 inherited supports, all 247 protected poses/optics preserved, zero disabled material links and zero issues. The fresh rebuild matches all 3065 object and 290 material records and the fingerprinted scene state. Every one of the 21 main and two detail RGB images matches exactly, with maximum channel delta zero. Native serialized blend hashes differ; the proof establishes authoring state and pixel reproducibility, not file-byte identity.

The final two completed comparisons, R45→R49 and R49→R51, have no material regression in both independent reviews. R49 itself failed materials98.5. R49→R51 explicitly records the sole sampling-method change, Cycles light-tree sampling enabled→disabled; every other review setting and all camera poses/optics remain fixed. R51 saves that setting after the actual R50 W02 single-setting diagnostic restored missing modeled-fixture pools. No fixture, power or material changed in that sampling repair. Earlier rejected revision proofs do not transfer to R51.

The fixed render settings are Cycles CPU, 24 samples, seed 73, 960×540, denoising, eight bounces, light-tree sampling disabled, exposure zero and AgX Medium High Contrast. `CAMERAS.md` defines every required view. Own cold evidence is in `coldstart/{comparison,pixel_comparison,detail_comparison}_R51.json`, `validation_R51_cold.json`, `renders/R51_cold` and `details/R51_cold`. Current evidence lives in `renders/R51`, `details/R51`, `validation_R51.json`, `material_contract_R51.json`, `PRIMARY_INSPECTION_R51.md` and `critics`.

## Exact selected replay

From the repository root, set `WASTE_BLENDER` to the Blender executable and `WASTE_ROOT=sections/facility-assembly/sources/waste-storage/overhaul`. Use the archived selected builder, not a later canonical builder, for this exact revision:

```bash
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/checkpoints/R51.blend" -t 8 --python-exit-code 1 --python "$WASTE_ROOT/blender/fingerprint_overhaul.py" -- R51_checkpoint
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/../module.blend" -t 8 --python-exit-code 1 --python "$WASTE_ROOT/blender/history/R51_build.py" -- R51 coldstart
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/coldstart/R51/R51.blend" -t 8 --python-exit-code 1 --python "$WASTE_ROOT/blender/validate_overhaul.py" -- R51_cold
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/coldstart/R51/R51.blend" -t 8 --python-exit-code 1 --python "$WASTE_ROOT/blender/fingerprint_overhaul.py" -- R51_rebuild
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/coldstart/R51/R51.blend" -t 8 --python-exit-code 1 --python "$WASTE_ROOT/blender/render_overhaul.py" -- R51_cold
"$WASTE_BLENDER" -b --disable-autoexec "$WASTE_ROOT/production/coldstart/R51/R51.blend" -t 8 --python-exit-code 1 --python "$WASTE_ROOT/blender/render_detail.py" -- R51_cold
python "$WASTE_ROOT/blender/compare_coldstart.py" R51
```

Pillow is required for the last comparison. Replay writes cold derivatives and evidence under the overhaul package; it does not overwrite the editable alias or original source. Native serialized file hashes may differ even when all authoring fingerprints and rendered pixels match.

Registered support/aperture/route probes are bounded samples. Unity export, collision/navmesh, procedural-material conversion, lighting bake and runtime performance were not evaluated. This is an additive scene candidate. Publication and independent PR review are recorded externally in the exact-HEAD delivery run and PR body. This handoff freezes before publication; owner merge remains a separate action. the retired map is not promoted or relinked.
