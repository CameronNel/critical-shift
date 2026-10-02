# Texture finish T1 (owner request, October 2026)

The owner found the electrical room's textures flat and asked for: detailed wet concrete with rubber grip padding
scattered at stations (not all over), rougher more rustic wall paint, and sharper corners on hero props for a more
Valorant-like look. Scope chosen by the owner: this room only; hero props only for the edge change; wet patches by equipment
with rubber pads at stations.

The reviewed R11 module (SHA-256 `eb962ce7…a1df`, kept as `checkpoints/full-R11.blend`) is the "before". The current
`../module.blend` is the "after" and is **not** independently reviewed: the R11/R12 scores in `critics/` describe R11 only.

## What changed (`scripts/texture_finish.py`, applied once to the palette-finished source)
- **Wall and ceiling paint (`EOH | cream`)**: chipped paint over dark primer with rust in the deeper chips (more toward the wall
  bases and in cavities), soft vertical drip streaks, blotchy tone, an orange-peel and trowel relief, cavity grime, matte roughness.
- **Concrete (`floor`, `route`, `Coarse service epoxy`, `Floor contact history`)**: aggregate flecks, pits, hairline cracks, and
  seven bounded wet zones with noisy edges: darker, near-mirror gloss with reflections, flattened relief and a dark pooling rim.
  Zones are by the transformer gate, transfer cabinet, reserve-bay approach, switchgear draw-out, bench and the two door ends.
  The rest of the slab stays dry. Zones are in room metres; `route` and the epoxy panels use room coordinates and the `Floor`
  object uses its centred coordinates (offset 8.2 m in Y).
- **Metals, enamels, rubber**: micro-scratch roughness breakup, cavity grime and mottling; enamel, oxide, ochre, replacement and
  steel/zinc also get edge wear that reads as crisp bright edge highlights (Cycles Bevel and AO nodes). Rubber gets a stipple relief.
- **Crisp hero edges**: 952 bevel modifiers on the switchgear, transformer, transfer cabinet, reserve modules, cabinet front
  frames, door frames and reserve-opening returns change from two-segment roundings to single-segment chamfers of at least 6 mm.
  Walls, floors, ducts and every other object keep their bevels.
- **Eight rubber grip pads** (`Grip pad …`, new `EOH | grip rubber` material, ribbed and chamfered, registered to the Floor like the
  existing insulating mats) at the transformer gate and service side, transfer cabinet, reserve threshold, bench, switchgear
  draw-out end and the two door sides. None is on a sampled walking line.

## Evidence that ran
- `validation-T1.json`: the room's own `validate.py` against `checkpoints/baseline.blend`: **PASS, no failures**: 318 protected
  geometry and camera checks unchanged, 59 registered support assemblies, five sampled 0.60 m route envelopes with zero defects,
  no missing dependencies, manufactured-mesh checks clean. This validator does not count the new pads (it still reports 59).
- `texture-compare-T1.json` (`scripts/check_texture_finish.py`): **PASS**: 3,177 objects before, 3,193 after; 2,225 identical;
  952 changed only in bevel parameters; 16 added, all grip-pad objects; zero other changes; cameras, lights, colour management
  and world strength unchanged; one material added (`EOH | grip rubber`); all eight pads rest on the floor (top within 3 mm under all nine samples) and none
  overlaps equipment below 4 cm.
- Renders: `renders/T1/` holds the 14 formal cameras (1280x720, 16 samples, seed 73) and the capture manifest.

## Not done / not claimed
- No independent critic review and no scoring: the scores in `critics/` are for R11. This change has not been rescored.
- The linked map candidate (`facility_electrical_overhaul_candidate.blend`) and its map-view renders were not regenerated or
  re-checked; the candidate links `../module.blend`, so it picks the new source up, but its integrity receipts describe R11.
- The R11-era hash statements in `../contracts/HANDOFF.md` and `TASK_STATE.md` now refer to `checkpoints/full-R11.blend`, not the current module.
- The material definition count rose by one, and the shaders add Cycles Bevel and AO nodes; render time was not measured and
  engine-side look (Unity) is unverified.
- Hard edges are a modifier and shader change, not remodelled geometry; the effect at room-view distance is moderate.

## Reproduce
```sh
R=sections/facility-assembly/sources/electrical-room
blender -b $R/overhaul/checkpoints/full-R11.blend --python $R/overhaul/scripts/texture_finish.py -- --output /tmp/t1.blend --receipt /tmp/t1.json
blender -b $R/overhaul/checkpoints/full-R11.blend --python $R/overhaul/scripts/check_texture_finish.py -- --dump /tmp/before.json
blender -b /tmp/t1.blend --python $R/overhaul/scripts/check_texture_finish.py -- --dump /tmp/after.json
python3 $R/overhaul/scripts/check_texture_finish.py --compare /tmp/before.json /tmp/after.json /tmp/receipt.json
```
Never run `texture_finish.py` twice on the same source (it asserts `electrical_texture_revision` is unset).
