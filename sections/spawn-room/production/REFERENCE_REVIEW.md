# Spawn Room Reference Review

**Status:** mandatory pre-build evidence  
**Rule:** this file must be updated before any new Spawn Room style-validation build begins.

The builder is not allowed to rely on memory, one mood board, or a previous failed render.

## Required source

Read:
- [../art/SPAWN_REFERENCE_BIBLE.md](../art/SPAWN_REFERENCE_BIBLE.md)

Inspect every numbered SVG in:
- `../art/reference/00_*.svg` through `../art/reference/27_*.svg` where present.

## Review checklist

- [x] 00 master overview
- [x] 01 hallway composition
- [x] 02 briefing room
- [x] 03 locker room overview
- [x] 04 suit bay anatomy
- [x] 05 hazmat suit
- [x] 06 integrity chamber
- [x] 07 radiation checkpoint
- [x] 08 door/wall architecture
- [x] 09 ceiling/floor
- [x] 10 material/wear
- [x] 11 lighting
- [x] 12 signage
- [x] 13 small props
- [x] 14 larger-building illusion
- [x] 15 camera validation
- [x] 16 do/don't summary
- [x] 17 overhead functional plan
- [x] 18 furniture
- [x] 19 wall graphics/portraits
- [x] 20 colour palette
- [x] 21 prop scale lineup
- [x] 22 integrity chamber states
- [x] 23 suit bay variation
- [x] 24 first-person scale
- [x] 25 validation slice
- [x] 26 modeling progression
- [x] 27 wear placement

## Five strongest rules extracted

Reviewed 2026-09-05 against main 8603063. All 28 numbered plates were rasterized and visually inspected, along with the three legacy Spawn overview plates and global visual grammar. Plate 26 had four invalid closing rect tags; removed only those stray tags to make the reference renderable. These are schematic direction plates, not modeling blueprints. All global and section markdown documentation was read; the art reset overrides conflicting legacy wording.

1. Believable adult scale holds the style together (05, 08, 18, 21, 24). PPE is hanging clothing with soft folds; furniture has real supports and thin material sections.
2. Construction comes before surface polish (04, 08, 26): folded sheet, rebated door jambs, welded tube furniture, fabric volume, physical latches and cradle supports. Bevels finish edges only.
3. Different materials must respond differently under the same practical (10, 20): porous warm walls, desaturated equipment paint, absorbent rubber and cloth, modest glass and dull exposed metal.
4. Preserve quiet fields and functional hierarchy (00, 01, 12, 13, 17): three routes read first; four suits and central chamber are the locker focus. Text and personal objects stay subordinate.
5. Light and use have physical causes (11, 27): local fixture falloff and recess shadows; wear belongs at hands, feet, seat edges and maintenance points. Most surfaces remain maintained.

## Three failure modes this build will explicitly prevent

1. Faceted toy/mannequin PPE: use adult garment proportions, joined cloth volumes, broad folds and suspended posture; no armor plates or inflated extremities.
2. Universal beveled-cube / satin-plastic language: derive the door, station and furniture from different construction methods and inspect a plain-grey stage before materializing.
3. Decoration replacing design: no plants, no device grid, no label wallpaper; only small functional IDs and one personal-use cluster in the slice.

## Validation-slice composition

A 6.2 m wall segment and shallow floor/ceiling return. Left: a 1.30 x 2.20 m steel personnel door with rebated jamb, seal, protected wired-glass pane, lever and closer. Center: one 1.05 x 0.62 x 2.25 m folded-sheet PPE station, hanging coveralls, visor/hood, upper cradle and storage. Right: a 1.8 m institutional bench with thin seat and tubular steel structure. One overhead practical throws light down the wall; one clamped utility pipe terminates through the ceiling. Four storytelling groups: work boots, used clipboard, enamel mug, spare filter. No other bays, chamber or full room until the slice passes its visual gate.

## Scale anchors

- player eye height: 1.63 m
- interior door: 1.30 m clear width, 2.20 m clear height
- bench: 1.80 x 0.45 m, 0.45 m seat height
- suit bay: 1.05 x 0.62 x 2.25 m
- adult PPE presentation: approximately 1.75 m wearable stature
- later integrity chamber: 2.00 x 2.00 x 2.75 m, minimum 1.20 m clear circulation

## Material families to prove

- [x] painted metal
- [x] wall/concrete/plaster
- [x] floor
- [x] rubber
- [x] PPE fabric
- [x] restrained plastic
- [x] glass
- [x] paper/card

## Approval

Reference review complete: **YES**

Change to **YES** only after the references above were actually inspected.

## Detailed written references

- [x] SPAWN_REFERENCE_BIBLE.md read
- [x] SPAWN_ASSET_REFERENCE_MATRIX.md read
- [x] SPAWN_MATERIAL_REFERENCE.md read
- [x] SPAWN_LIGHTING_REFERENCE.md read
- [x] SPAWN_SIGNAGE_REFERENCE.md read

## User-directed wear revision — 2026-09-06

The user requests an old, dirty but maintained workplace with visible mild damage, rough stylized concrete/plaster, used PPE/equipment and less perfect geometry. This supersedes the earlier prohibition on scanned concrete inputs: CC0 scans are now expressly requested, with palette compression and controlled relief to retain stylization. Plates 09, 10 and 27 were reinspected before editing. Preserve adult scale, clear routes and the fixed camera baselines. Concentrate actual chips and repairs at tile corners, lower walls, furniture edges and thresholds. Retain low-cost SOLID startup; do not interrupt the user's game with Computer Use.

Remote refreshed during this revision: main advanced from 8603063 to d849d3d with the separate Gullet mine section. The updates were merged cleanly into this branch; no Spawn art guidance changed.
