# Luna art critique 02 — first correction cycle

Independent visual review of `art-02`, completed after inspecting all ten renders once. Comparison set: `reference-a02-hall.png`, `reference-b01-controls.png`, and the previous `art-01` batch.

Art 02 is a visible improvement over Art 01 in contrast, pool visibility and broad lighting separation. It remains **FAIL**. The scene still misses the required material/tactile target, the bank construction still reads as repeated smooth primitives at close range, and the control-room camera remains obstructed. The supplied `validation.json` also reports `cold_start: false`, so the technical gate is not clear.

## Scores

| Rubric category | Score /100 | Art 01 delta | Evidence status | Review finding |
|---|---:|---:|---|---|
| Scale, construction and circulation | **87** | 0 | Measured checks pass; camera proof is mixed | The pool ring and turbine aisle remain visibly traversable in 01, 04, 05 and 10. The measured envelope, 1.312 m turbine clearance, stair checks and ten-camera count pass. View 02 is still blocked by the large foreground teal object. View 06 remains obstructed, so room access and control-side readability are still incomplete from the camera set. |
| Shape specificity and art direction | **72** | +4 | Direct pixel evidence | Darker values improve the silhouette read, especially in 01 and 09. The close bank view still shows repeated smooth cylindrical housings, identical trim rings, broad blank doors and small labels carrying most of the specificity. Perimeter stations continue to share the same rounded box/cylinder language. It is cleaner than Art 01 but still closer to polished blockout language than the reference’s authored industrial construction. |
| Reactor hierarchy and focal clarity | **86** | +4 | Direct pixel evidence | The pool is now a stronger cyan focal point in 01, 03 and 05, and the two-bank read remains immediate in the room views. The pool still reads as evenly illuminated cyan wall bands rather than a concentrated lower source with convincing depth. View 01 keeps both banks and the gate in a useful hierarchy; view 10 still crops the upper bank housings and lower pool context. Dedicated view 09 is judged as bank evidence only and is not penalized for omitting the pool. |
| Material separation and tactile finish | **64** | +9 | Direct pixel evidence, strongest in 08 and 09 | Art 02 adds darker teal, brighter trim response and broad wall variation. It still does not separate materials convincingly. In 08, white pipes remain smooth and plastic-like, the ribbed teal machine reads as the same painted family as the tanks, and the yellow wheels remain flat colour. In 09, the bank body, carriage and trim show stronger highlights but still lack believable material transitions, wear or contact history. The references have more convincing painted steel, bare metal, rubber, glass and used flooring differences. |
| Lighting, depth and exposure | **65** | +20 | Direct pixel evidence | This is materially better than Art 01: 01, 03, 04 and 05 now show darker structural steel, local wall falloff and a more readable cyan pool. The correction overshoots in places. View 07 is very dark, with stair treads and the lower landing losing readable detail. View 09 is mostly deep teal/black with the lower drive columns fading into the background. Broad room views still have relatively even wall illumination, and the cyan shaft remains a uniform wash rather than a controlled low source. The normal state is closer to the target but not yet balanced like A02/B01. |
| Colour and detail discipline | **72** | +6 | Direct pixel evidence | The teal/charcoal/cyan hierarchy is clearer, and view 03’s yellow gate/red emergency button read well. Floor scuffs and the partial `P-10 SHIFT CHECK` sheet in 08 add some authored evidence. The room still repeats teal across most equipment, uses labels heavily for station identity and has little focal detail variation outside the banks and pool. The broad wall mottling is visible in 01–05 but often reads as generalized dirt instead of selective wear. |
| Environmental credibility | **66** | +6 | Direct pixel evidence; operator-space proof incomplete | The shift-check sheet, gauges, carts, racks, pipe labels and emergency controls make the space more operational than Art 01. It still looks staged and sparsely inhabited. There is little visible handling wear, maintenance residue or local repair evidence. View 06 remains a blocked foreground of the same large dark console, with only a blurred reactor slice behind it; control-room use cannot be judged from that camera. |
| Technical cleanliness and reproduction | **84** *(provisional)* | -8 | `validation.json` plus visible camera batch | Hall area/span, two fixed housings, two moving banks, bank axes/travel, turbine clearance, stair measures, ten cameras and support checks pass. `old_3d_imports` is empty. The batch rendered, but `cold_start` is explicitly `false`, which is a critical reproduction failure for this gate. Image evidence also cannot establish motion, pivots or final state progression. |

The scene remains below the independent 90/100 gate in every visual category except none; the technical score is also below the gate because cold start is false. The darker pass should not be treated as approval simply because it is better than Art 01.

## Camera evidence

### 01 HERO

The correction is visible here. The cyan pool has stronger presence, dark structural members separate from the walls, and the paired bank silhouettes are clearer. The pool still has a very even cyan wall/shaft response and little indication that the strongest source is low in the depth. The east glazing remains a bright, shallow rectangle. The gate and emergency console read but are small in the overall frame. The upper bank assemblies are still cropped near the ceiling.

### 02 WEST_ENTRY

Value separation is improved, but the large foreground teal block still occupies the lower-left and blocks the entry read. The nearest bank column dominates the centre and its upper assembly is cropped. The control glazing remains visible but low-information. White pipework, pale walls and teal machinery now have more contrast than Art 01, but the construction still looks clean and generic.

### 03 SOUTH_GATE

The acknowledgement button, red bypass/SCRAM control and yellow gate are clearly legible, with better local shadow than Art 01. The pool shaft is brighter and reads as deep enough to establish danger, although the light remains evenly cyan across the visible wall bands. The surrounding consoles and pipework remain visually smooth and lightly used.

### 04 TURBINE_AISLE

The aisle remains open and the darker lighting gives the equipment more weight. The turbine is still cropped at the right edge. The breaker bank, waste cylinder, fuel rack and pipework are readable but share the same simple teal/white treatment. Floor route arrows still read as flat graphics. There is little material or wear evidence beyond broad panel variation.

### 05 REVERSE_NORTH

The pool ring, paired columns and rail route remain readable. The darker walls improve depth over Art 01, but the perimeter still consists of small interchangeable teal machines. The pool remains a uniformly cyan-lit shaft, and the upper wall lighting is still broad and even.

### 06 CONTROL_ROOM

The control-room obstruction is unchanged and remains a hard evidence failure for this pass. The large foreground console blocks most of the frame; the operator interior and glazing cannot be judged. The background reactor is blurred and partial. This known issue is deferred to Art 03, but Art 02 receives no credit for control-room presentation here.

### 07 COMPACT_STAIR

The enclosed stair is judged as a dedicated interior view, not as a requirement to show the whole hall. Within that scope, the handrails and flights are visible, but the lower steps and landing are too dark to read comfortably. The image provides no evidence about architectural adjacency, which is correctly deferred to separate scene diagnostics, but it remains weak visual evidence for safe readable circulation.

### 08 MATERIAL_SLICE

The darker pass reveals more shape than Art 01 and the shift-check page adds a human-use cue. The central defect is still material response: the white pipe and pale fittings read as smooth plastic, the teal ribbed machine and tanks share the same response, and yellow wheels look like flat emissive or untextured discs. The panel walls carry broad dark variation, but the close-up still lacks tactile separation and localized contact wear.

### 09 BANK_MECHANISMS

This is a valid dedicated bank detail view and is not penalized for omitting the pool. It clearly shows two banks, fixed upper bodies, lower carriages and separate drive columns. The contrast improvement helps. The visual weakness is unchanged in kind: repeated cylinders, identical trim bands, large blank access panels and labels dominate the construction. The housings are dark teal painted shapes with smooth broad highlights rather than convincingly serviced industrial assemblies. Lower columns fade into the dark background.

### 10 EAST_HIGH

The high view gives a useful room-level read: open ring, paired columns, perimeter stations and a stronger cyan pool. The upper bank housings are still cut by the top edge and the lower pool is cut by the bottom edge. The east-side equipment reads as repeated teal blocks at distance. The image is more legible than Art 01 but remains too dependent on labels and broad colour blocks.

## Observable changes from Art 01

- Cyan pool visibility and focal strength improved in 01, 03, 05 and 10.
- Dark structural steel and local wall falloff are clearer in the main room views.
- View 08 now includes a visible shift-check sheet and stronger equipment contrast.
- Bank close-up contrast improved in 09, making the two-bank construction easier to inspect.
- Material separation is still weak; smooth plastic-like responses remain across pipes, tanks, banks and consoles.
- Broad wall mottling is now visible but often reads as generalized dirt rather than authored maintenance wear.
- The control-room obstruction in 06 remains unchanged.
- The stair interior in 07 is darker and loses tread/landing readability.
- Cropping remains in the hero/high/turbine frames and continues to weaken complete focal proof.
- Cold-start status regressed from Art 01’s `true` to Art 02’s `false` in the supplied validation evidence.

## Decision

**FAIL — art-02 is a meaningful correction pass but not approval-ready.** The lighting direction is closer to the target and the pool/bank hierarchy is clearer, yet the rendered materials still read too uniformly, the bank construction remains generic at close range, environmental use is sparse, view 06 remains unusable for control-room evidence, view 07 is too dark internally, and the technical cold-start check is false. Art 03 needs fresh ten-view evidence before any category can be considered cleared.
