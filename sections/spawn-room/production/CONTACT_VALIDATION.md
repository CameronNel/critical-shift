# Spawn Room — Support Contact Validation

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


Cameras are necessary for composition and appearance, but they cannot prove that every prop physically touches the surface it is supposed to touch.

The Spawn Room therefore has a mandatory geometry-contact audit.

## What must be checked

At minimum:
- papers
- portraits
- framed art
- signage
- notice boards
- wall-mounted displays
- wall-mounted utility props
- floor plants where hovering could occur
- bins
- benches/chairs when procedural placement is used
- ceiling fixtures
- hanging utility props

## Collections

Every support-dependent prop belongs to `CS_SUPPORT_REQUIRED`.

Support-dependent dressing also belongs to the appropriate audit collection:
- `CS_WALL_DRESSING`
- `CS_FLOOR_DRESSING`
- `CS_CEILING_DRESSING`

An object in an audit collection but not in `CS_SUPPORT_REQUIRED` fails validation. This prevents the builder from escaping the test by forgetting to tag the object.

## Per-object metadata

Required:
- `cs_support_target`
- `cs_support_direction`

Defaults:
- max gap = 0.005 m
- max penetration = 0.002 m
- max support-angle deviation = 12 degrees

## Support anchors

Thin/simple props may use their support-facing bounding-box face.

Irregular props should use child Empty objects with:

`cs_support_anchor = true`

Put each anchor exactly where the prop is intended to touch its support.

Examples:
- one anchor per chair leg
- plant-pot base anchors
- bench-foot anchors
- pipe-bracket anchors
- fixture mounting points

## Command

```bash
blender -b spawnroom.blend --python validate_contacts.py
```

Expected output:

`../production/contact_validation.json`

The command must exit as a failed Blender job when any contact check fails.

A PASS report is mandatory before the Spawn Room can pass technical validation or cold-start acceptance.


## Visual-contact requirement

Geometric contact passing is necessary but not sufficient. A prop must also **look grounded from the gameplay camera**.

For every support-dependent prop, review:
- visible contact shadow;
- believable mounting hardware or support logic where appropriate;
- no suspicious millimetre gap;
- no deep penetration that hides poor placement;
- no wall panel that appears to float because its shadow/light response is missing;
- no furniture foot that visually hovers despite technically intersecting the floor.

A mathematically valid contact can still fail art review.

## Grounded rebuild audit coverage

The rebuilt scene registers assemblies at actual mounting/foot locations, with separate registrations for stored boots, cartridges, inspection cards, loose clipboards, mug, door-contact wear, portraits, notices, signs, duct hangers and the return-air grille. The fifth build has **59 registered props, zero contact failures**. The same report is copied into each cycle folder for traceability.

During review, a passing bay-root contact did not prove its boots touched the tray. The 14.5 mm boot gap was corrected and each boot now has its own shelf-target registration. A cabinet-foot offset was also corrected at the actual mesh rather than moving its anchors. `validate_grounded.py` independently measures all 36 furniture feet, plus room clearances and required asset counts. This supplements, rather than replaces, the original validator.

Painted wall linings, window reveals and floor joints are architectural construction. The machine's attached internals and PPE's sewn components are nested under their supported asset roots. Anchor tests do not certify arbitrary mesh intersections; fixed-camera visual inspection remains mandatory.


## Reference-aware contact review

Use plate 24 for first-person scale and plates 04, 06, 08, 13 and 18 for expected support logic. Contact validation should confirm not only that objects mathematically touch a support, but that their mounting method visually matches the reference family.
