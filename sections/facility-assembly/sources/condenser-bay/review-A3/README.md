# Condenser A3 review evidence

All renders are of `../module_aaa_A3.blend` (sha256 `20df13009f57…`, the full hash is in each manifest), on the cloud CPU (the owner's
choice for review renders), Cycles with OpenImageDenoise, seed 0.

- `frames/`: the 19 named cameras (the room's 18 review cameras and `C11_WEST_VENT`, added for the vent extension) at 1920 x 1080,
  24 samples, rendered in one process by `../render_review_A3.py`. The JPEGs (quality 92) are for reading; `frames/manifest_png.json` records the PNG originals' hashes, the process id, the settings and the camera transforms,
  so the hashes are of the PNGs, not of these JPEGs.
- `crops/`: 1:1 crops of those frames (exhaust flange, condensate controls, cooling isolator and its wall tags, operator labels, gauge
  glass, floor contacts, pump volute, the D01 doorway reveal, the west vent extension).
- `cutaway_plan_clipped_z4.9.jpg`: the labelled cutaway (`../render_cutaway_A3.py`, everything above module z 4.9 m clipped; not a player
  view). `plan_dimensioned.jpg`: the same with measured dimensions, levels, a scale bar and the main items (`../annotate_plan_A3.py`).
- `cold_report.json`: two complete 19-camera sets at 960 x 540, 16 samples, from two separate fresh Blender processes of the same file
  (`cold_A_manifest.json`, `cold_B_manifest.json`), compared by `../compare_cold_A3.py` under
  `sections/condenser-bay/production/COLD_COMPARISON_POLICY.md` (CPU screen: mean at most 0.01/255, maximum 2/255): every camera within it
  (largest single channel difference 1/255). The cold PNGs themselves are not kept.

In the module file the D01 doorway ends on a "SERVICE CONNECTION" blind plate (W01, W06); in the combined map that stub opens onto the
condenser stair corridor (`combined/build_compact_map.py`, `patch_condenser`).
