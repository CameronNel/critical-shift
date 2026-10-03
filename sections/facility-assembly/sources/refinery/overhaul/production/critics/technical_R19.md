# Independent technical audit — R19 human props

**Artifact inspected:** immutable `production/checkpoints/R19.blend` (read-only copy).\
**Revision:** R19; checkpoint, source, and validation SHA-256 `c91dcfcf1cbcfca4cdae50c5619d95b097aa0424f6f845889fe8da63589ee9f7`.\
**Formal validation:** PASS; 29 protected interfaces unchanged, world strength 0. This is a measured contact and geometry review, not a visual score or runtime certification.

## Human props and worktop contact

The evaluated timber worktop spans `x=0.58…1.22 m`, `y=−6.13762…−5.03762 m`, with top at `z=0.98 m`.

- Both glove groups are fully on the top face and separated. Group 0 bounds are `x=0.713606…0.975206`, `y=−5.498368…−5.325813`, `z=0.98…1.013 m`; its minimum top contact is exact at `z=0.98`. Group 1 bounds are `x=0.870657…1.136118`, `y=−5.275743…−5.062908`, `z=0.98…1.013 m`; it also touches the top. The groups have a 50.07 mm Y gap. Their minimum worktop edge margins are respectively 133.6/244.8/639.3/288.2 mm and 290.7/83.9/861.9/25.3 mm (left/right/front/back, based on X/Y bounds). Thus both fit with at least the requested 22 mm margin.
- One glove component is a probable attachment defect: the furthest finger mesh on each glove lies much farther from its palm than the other fingers. Closest evaluated surface clearances are 9.48 mm (`Glove finger.003`, group 0) and 11.8 mm (`Glove finger.007`, group 1); the other finger-to-palm clearances are 0–1.1 mm, with the thumbs about 0.54–0.55 mm. This may be an intentional separated finger pose, but the two outliers merit inspection for a missing palm join.
- The tipped enamel mug body contacts the worktop at `z=0.98 m` (two evaluated vertices). Its handle is 68 mm above the worktop at its lowest point, but it is joined to the cup: the evaluated meshes have 0.324 mm minimum surface separation in a nearest-point query and a Boolean intersection volume of `1.4195×10⁻⁵ m³`.
- The dry spill is a 10-vertex sheet exactly 20.0 µm above the top, with its face normal upward. It remains inside the tabletop outline. Its closest surface clearance to the mug is about 20.1 µm, so the spill sits close to the rim without a measured solid intersection.
- The pin penetrates the rotated paper physically: Boolean intersection volume is `1.2868×10⁻⁶ m³`. The pin axis crosses the sheet depth. Header and handwritten text geometry are seated about 0.01–0.03 mm off the sheet.

## Paper drawing marks need seating

The page itself is tilted around the pin, but the rigidly rotated pump sketch marks retain millimeter-scale offsets from its plane. Signed normal offsets are `−0.18…+3.42 mm` for `RF1 | Pump sketch case`, `+0.645…+2.595 mm` for `Pump schematic line` and `.001`, and `+0.494…+2.746 mm` for line `.002`. The ring partly penetrates the paper and floats at its far side; the three schematic rods float above it. Project these marks onto the page face at a consistent small film offset. Header and note seating pass, so this is limited to the schematic geometry.

## Limits

Distances above come from evaluated world-space mesh bounds, nearest-surface queries, and Boolean checks on the R19 checkpoint. The glove finger outliers need author intent to distinguish an intentionally splayed finger from a detached mesh. This review does not certify exhaustive intersections, visual legibility, or runtime behavior.
