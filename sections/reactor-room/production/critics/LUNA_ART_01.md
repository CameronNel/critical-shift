# Luna art critique 01 — baseline render batch

Independent visual review of `art-01`, completed after inspecting each of the ten rendered images once against `reference-a02-hall.png` and `reference-b01-controls.png`.

This is a baseline art critique. Scores are for visible rendered evidence and, for the technical row, the supplied `validation.json`. No score is granted for object count, build time or stated intent. The scene is **FAIL**. It is nowhere near the required all-categories-90 gate because lighting, materials, construction specificity and environmental credibility are visibly weak.

## Scores

| Rubric category | Score /100 | Evidence status | Review finding |
|---|---:|---|---|
| Scale, construction and circulation | **87** | Measured checks pass; camera proof is mixed | The open pool ring and turbine-side aisle read as traversable in 01, 04 and 10. The envelope, 1.312 m turbine clearance, stair width and ten-camera checks pass in `validation.json`. View 02 is heavily occluded by a large foreground teal object, and views 06–07 do not prove the control/stair relationship from a useful room context. The room reads human-scaled in the broad views, but access and route readability are not consistently demonstrated. |
| Shape specificity and art direction | **68** | Direct pixel evidence across all ten views | The paired bank silhouette is clear, but most visible assets resolve as smooth teal cylinders, rounded boxes and flat panels with the same treatment. View 09 exposes the repeated generic construction: large cylindrical housings, identical edge bands, broad blank access plates and small pasted labels. Perimeter consoles and tanks repeat the same visual grammar. The result is clean blockout polish rather than the specific, grounded Valorant-influenced construction in the references. |
| Reactor hierarchy and focal clarity | **82** | Direct pixel evidence | View 01 establishes the pool and exactly two banks, and views 03, 05 and 10 retain the paired columns. The pool is visibly recessed, but its cyan is pale and evenly distributed; the shaft does not carry the strong deep luminous focal read seen in A02/B01. View 02 lets the foreground console dominate, view 09 crops away the pool entirely, and view 10 crops the bank housings at the top. The hierarchy survives only in the best angle. |
| Material separation and tactile finish | **55** | Direct pixel evidence, strongest in 08 and 09 | The scene is overwhelmingly pale matte teal/white. In view 08, white pipework, wall panels and nearby equipment have nearly the same soft response; in view 09, the bank housings, carriage shells and trim read as one smooth painted-plastic family. The large white pipes look like untextured plastic, the teal equipment lacks convincing roughness breakup, and there is effectively no localized wear, contact grime, dents or service history visible in any view. The references have clearer painted steel, bare metal, rubber, glass and flooring separation. |
| Lighting, depth and exposure | **45** | Direct pixel evidence across all ten views | This is the largest visible failure. Views 01–05 and 08–10 are bright to the point of flattening: white walls, white pipes, pool rim and floors sit in a narrow value band; practical lights barely create local falloff; contact shadows are weak; the cyan pool does not produce controlled directional bounce. View 07 has a darker stair pocket, but it reads as an isolated exposure change rather than deliberate depth. View 06 contains blown bright glazing/ceiling areas and a blocked foreground, so it does not establish readable control-room lighting. The reference images have stronger warm/cool separation and more grounded shadow structure. |
| Colour and detail discipline | **66** | Direct pixel evidence | The restrained grey/teal/cyan family is present and the yellow gate/red emergency control remain legible in view 03. However, the whole room is desaturated and pale rather than deliberately colour-blocked. Teal is repeated on nearly every machine, the pool is too weakly separated from the white shell, and the broad surfaces have almost no authored wear or detail clustering. Labels are readable but do too much of the identification work in views 01, 04 and 10. |
| Environmental credibility | **60** | Direct pixel evidence; operator-space proof incomplete | The room contains plausible station names, gauges, pipe families, a fuel rack, carts and a visible south emergency control. It still feels staged and unused: no convincing maintenance traces, human handling wear, paperwork, tools, gloves, repair evidence or local service mess are visible. View 06 is especially weak evidence: a large green console/desk fills most of the frame and the control-room interior is not readable. The rendered room therefore looks like labelled equipment placed in a clean shell rather than a maintained workplace. |
| Technical cleanliness and reproduction | **92** *(provisional)* | `validation.json` plus visible camera batch | `validation.json` reports passing shell area/span, two fixed housings, two moving banks, bank axes/travel, turbine clearance, stair checks, ten cameras, cold start and no old 3D imports. All ten files rendered. This score is provisional because the images do not prove animation motion, pivot behavior, contact correctness in every hidden region or final state progression. The failed art rows still block approval. |

The weighted rubric result is not an approval score. The scene fails the independent category gate even with the provisional technical score because five visual categories are below 90 and there are unresolved camera-evidence defects.

## Camera evidence

### 01 HERO

The central pool and two banks are immediately identifiable, which is the strongest view. The pool rim and rail are readable, but the shaft is a pale cyan tube with little depth hierarchy. The upper bank housings are cropped near the ceiling and the foreground gate/emergency console is small relative to the room. The wall shell, floor, rails and equipment share a pale, soft response. The east glazing reads as a bright rectangle with little operator-space information.

### 02 WEST_ENTRY

The route around the pool is visible, but the large teal foreground equipment slab blocks the left side and makes the entry feel like a camera placed behind an obstruction. The bank columns dominate without the upper assemblies completing their silhouette. The glazing is visible but small and washed out. Pipework, walls and floor have almost no value separation.

### 03 SOUTH_GATE

The south gate, red emergency control, bypass control and acknowledgement control are legible and physically separated. This is the best interaction proof. The pool remains pale and shallow-looking because the lower shaft has little tonal falloff. Rail posts and the gate sit cleanly in the frame, but there is no visible wear or tactile material variation on the control family.

### 04 TURBINE_AISLE

The aisle reads open and the turbine/grid-breaker area is legible. The right turbine is cropped heavily by the frame, and the repeated teal boxes and white pipe stand-ins dominate. The floor route markings are visible but look like flat graphic arrows. The view does not show enough shadow or roughness variation to make the machinery feel heavy or used.

### 05 REVERSE_NORTH

The full pool ring and paired columns remain readable. The reverse view exposes the same flat cyan shaft and nearly uniform white shell. Perimeter equipment is small and visually interchangeable. The pipe route and rails are cleanly placed, but the room has no convincing depth cues beyond size reduction.

### 06 CONTROL_ROOM

This camera is a serious evidence failure. A large dark green console or desk fills most of the foreground and blocks the scene. The reactor is only a narrow blurred background slice; the operator interior and glazing relationship cannot be judged. The bright background is blown and the view reads as an accidental obstruction rather than a control-room review angle.

### 07 COMPACT_STAIR

The stair itself is visible and its handrails read, but the view is a tight isolated stairwell with no room context. It cannot prove adjacency to the east control room north side. The lower flight is dark and the upper landing is lost against the pale walls. The image also does not establish whether the stair feels compact in the room or merely exists as a separate shaft.

### 08 MATERIAL_SLICE

The close-up makes the anti-plastic failure undeniable. White pipe, teal vessel, teal ribbed turbine and wall panel all have smooth, low-information surfaces. Yellow wheels are flat colour discs with little material distinction. The pipe route is legible, but the surfaces do not show the broad roughness breakup, localized service wear or controlled bare-metal response visible in the references.

### 09 BANK_MECHANISMS

The two-bank count and fixed/moving vertical layering are clearly visible. The close-up also shows the construction weakness: the housings are repeated smooth cylinders with identical trim rings and large blank doors, while small labels and indicator strips carry the specificity. The surfaces are pale, uniform and toy-clean. There is no convincing mechanical grime, fastener variation, contact shadow or material shift between actuator body, trim, carriage and drive column.

### 10 EAST_HIGH

The high view shows the pool ring, open circulation and paired columns. The bank housings are cropped at the top, the pool is cut at the bottom and the east-side workstations become tiny interchangeable teal blocks. The broad room reads, but the hero is weakened by framing and by the same pale exposure seen in the other angles.

## Hard defects visible in this pass

- The normal-state lighting is flat and over-even across the room; practicals do not establish useful local falloff.
- Material response is too uniform and plastic-looking, especially on the white pipes, teal bank assemblies and perimeter equipment.
- The pool is recessed but its cyan light is pale and evenly distributed; it does not carry the deep luminous hero read of the references.
- Wall panels, floors, pipes and machines lack the roughness/value separation needed to read as distinct materials.
- There is almost no visible localized wear or evidence that people maintain and operate the plant.
- View 06 is obstructed and cannot serve as control-room evidence.
- View 07 is isolated and cannot prove the compact stair’s relationship to the east control room.
- Several camera framings crop important hero elements: upper banks in 01/02/10, turbine in 04, and pool context in 09/10.
- The bank assemblies are legible as two, but the close-up reads as repeated smooth cylinders and blank panels rather than authored industrial machinery.
- Labels carry too much of the station identification in the otherwise generic silhouettes.

## Decision

**FAIL — art-01 is not ready for approval.** The measurable foundation evidence is useful, and the two-bank/pool concept is visible, but the rendered finish misses the required grounded stylized semi-realism. The material and lighting rows are far below 90, and the control-room/stair camera evidence remains incomplete. A later review must judge the corrected render batch from the same ten views and verify that these visible defects have actually cleared.
