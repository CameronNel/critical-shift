# Luna art critique 04 — wear-pass regression

Independent visual review of `art-04`, completed after inspecting all ten renders once. Comparison set: `reference-a02-hall.png`, `reference-b01-controls.png`, and the previous Art 03 batch. Camera-purpose rules from `production/CAMERAS.md` are applied: dedicated bank and stair views are judged for their stated subjects, while room-level hierarchy is judged from the applicable room views.

Art 04 keeps the improved camera framing and the readable pool/two-bank composition. It introduces a severe visible regression: a speckled wear pattern covers broad side faces, undersides and front panels across many machines. This does not read as localized authored maintenance. It reads as procedural damage applied to whole assets and pushes the scene toward grunge-covered decay. The pass is **FAIL**.

## Scores

| Rubric category | Score /100 | Art 03 delta | Evidence status | Review finding |
|---|---:|---:|---|---|
| Scale, construction and circulation | **89** | 0 | Direct camera evidence plus measured envelope checks | The room envelope, pool ring, open route and broad human scale remain legible. View 02 stays clear, 04 shows an open turbine aisle, 06 shows the observation position, and 10 carries the room relationship. The broad circulation read is intact, but the speckled assets add visual clutter around the route and prevent a clean maintained-facility read. |
| Shape specificity and art direction | **71** | -4 | Direct pixel evidence | The silhouette and framing remain strong, but the new speckles obscure the designed surfaces and make repeated cylinders/rounded boxes look like distressed procedural props. View 09 still exposes the same repeated housing, trim-ring and access-panel language. The reference’s controlled simplification is replaced by high-frequency damage on otherwise generic forms. |
| Reactor hierarchy and focal clarity | **87** | -1 | Direct room-view evidence | Views 01 and 10 still clearly establish the cyan pool and exactly two banks, and 03 keeps the south emergency controls readable. The pool remains the strongest focal mass. Speckle contrast on the carriages and perimeter equipment pulls attention away from the paired bank construction and makes the scene busier than A02/B01. The shaft still reads as evenly cyan-lit rather than strongly layered at depth. |
| Material separation and tactile finish | **45** | -25 | Direct pixel evidence, strongest in 01, 04, 08 and 09 | This is the main failure. The wear pattern covers whole side faces of both moving carriages in 01/09, broad faces of consoles and grid-breaker banks in 01/03/04, and multiple perimeter machines in 02/05/10. The pattern is pale and irregular without visible contact logic. It reads as a material mask or noise overlay, not chipped paint at handles, edges or service points. White pipes and pale wall panels remain smooth/plastic-like, so the speckle does not create genuine material separation. |
| Lighting, depth and exposure | **74** | -2 | Direct pixel evidence | Practical falloff and dark structural steel remain closer to the reference than the early passes. The room-level exposure is generally readable and the cyan pool separates from the shell. The speckled surfaces catch attention as bright noise under the lights, flattening the intended material hierarchy. The shaft still has a uniform cyan wash, and view 06 retains a visible milky optical band across the control glazing. |
| Colour and detail discipline | **51** | -24 | Direct pixel evidence | The base palette remains coherent, and the south gate’s yellow/red controls still read. The full-face speckles destroy detail discipline: they appear across the hero banks, consoles, breaker panels, turbine-side equipment and high-view perimeter objects. This turns the clean maintained reactor into a noisy distressed set. The references use sparse wear and quiet wall/floor breathing room; Art 04 distributes high-frequency contrast almost everywhere equipment appears. |
| Environmental credibility | **55** | -17 | Direct pixel evidence; no credit for planned mask correction | The room still has gauges, carts, racks, shift paperwork and functional labels. The visible wear contradicts the stated maintained setting: broad speckles appear on areas with no apparent handling or impact reason, while the scene otherwise lacks corresponding localized service evidence. In 04 and 09 especially, the equipment looks artificially weathered rather than used by workers. View 06’s optical glazing defect remains visible and weakens the operator-space read. |
| Technical cleanliness and reproduction | **UNASSESSED** | — | Provisional; no final cold-start evidence | The supplied validation file reports passing envelope, bank-count, axis/travel, clearance, stair, camera and support checks, but `cold_start` remains `false`. No technical score is awarded until the final cold-start reopen evidence exists. Object/material counts and build effort are not scoring evidence. |

The scene fails the visual 90/100 gate in every scored category. The wear mask is a material/detail regression, not a successful finish pass. Reproduction remains unassessed pending final evidence.

## Camera evidence

### 01 HERO

The pool, rails, south gate and paired bank silhouette still compose well. The regression is immediately visible: the side faces of both lower carriages are covered in pale speckles, and the small console/turbine-side equipment at right show the same treatment. The pattern is too broad and too evenly available on exposed side faces to read as authored wear. The cyan pool is bright and legible, but the upper bank/structural support remains close to the frame edge and the pool shaft still has a uniform cyan appearance.

### 02 WEST_ENTRY

The clear entry lane and room perspective remain useful. Speckles appear on the near console, bank bodies, and several perimeter machines, making the scene noisier than Art 03. The lower pool is readable and the glazing remains in the background. The room is still pale and smooth in its architectural shell, so the scattered damage reads as an overlay on top of clean primitives rather than a coherent maintenance history.

### 03 SOUTH_GATE

The emergency gate and controls remain readable, with strong yellow/red accents. The pool is clear behind the rail. The grid-breaker bank at right has speckles across broad face areas, and the nearby consoles show the same repeated pattern. This competes with the emergency interaction and makes the perimeter look distressed despite the otherwise sterile shell.

### 04 TURBINE_AISLE

The aisle is open and the turbine/breaker area is legible. This view makes the regression especially obvious: the front of the center console and broad faces of the grid-breaker bank carry dense pale speckles, while the surrounding pipes and walls remain smooth and spotless. The contrast is inconsistent and reads as a procedural material failure. Floor route arrows remain flat graphics, and the turbine itself is still partly cropped at the right edge.

### 05 REVERSE_NORTH

The pool ring, paired columns and pipe route remain readable. Speckles are visible on the generator-side and perimeter equipment, adding unrelated bright noise behind the rails. The architectural shell remains quiet, but the machine faces no longer feel selectively maintained. The pool is still evenly cyan-lit with limited lower-source depth.

### 06 CONTROL_ROOM

The observation camera remains usable for the room subject, but the glazing still shows a broad milky/opaque optical band and distorted reflection across the lower-middle view. The equipment visible through the glass includes the same speckled faces, which are further softened by the optical defect. The room beyond is readable only as a hazy overview, not as clean control-space evidence.

### 07 COMPACT_STAIR

The enclosed stair remains readable as a dedicated interior subject. Treads, rails and wall light are clear, and the wear regression is mostly absent here. It still provides no adjacency evidence, as expected from the camera brief. Its material story is simple and low-detail compared with the heavily speckled equipment elsewhere, adding to the inconsistency between spaces.

### 08 MATERIAL_SLICE

The shift-check page, white pipe route, yellow wheels and ribbed teal machine remain clear. This close-up shows the underlying material issue: pipes and fittings are still smooth, molded-plastic-looking forms, while the nearby dark teal base and machine do not show convincing differentiated wear. The speckle is not dominant in this particular view, but the scene still lacks tactile separation even where the camera is dedicated to materials.

### 09 BANK_MECHANISMS

This is a valid dedicated bank-detail view. The two banks, fixed housings, carriages and drive columns are clear. It is also the strongest rejection evidence for the wear pass: both moving carriage side faces and the underside areas of the fixed assemblies are densely speckled across broad surfaces. The pattern ignores the object’s functional boundaries and repeats across both banks, making the assets look procedurally damaged. The underlying repeated-cylinder/blank-panel construction remains visible beneath the noise.

### 10 EAST_HIGH

The wider high view preserves the room relationship and pool. The speckles are now visible on the upper/lower bank faces, perimeter consoles and equipment around the room. At this distance they read as bright visual noise rather than useful wear and compete with the paired-bank focal read. The cyan pool remains clear, but the architecture still has little roughness or service variation of its own.

## Observable changes from Art 03

- Camera framing and room-level composition remain stable and generally usable.
- The pool/two-bank hierarchy is still readable in 01 and 10, with a clear south gate in 03.
- The broad wall and floor exposure remains closer to the reference than the early passes.
- Full-face speckled wear appears across moving carriages, actuator undersides, consoles, breaker banks and perimeter equipment.
- The speckles are not localized to visible contact, edge or service regions and read as procedural noise.
- The material pass therefore regresses sharply despite adding more visible variation.
- White pipes, pale walls and flooring remain smooth and weakly separated in close-up view 08.
- The control-room glass still has a milky optical defect in view 06.
- The cyan shaft remains evenly lit instead of carrying a stronger lower-source depth read.
- Technical reproduction remains unassessed because the supplied run has no final cold-start evidence.

## Decision

**FAIL — art-04 is a material/detail regression despite usable camera composition.** The speckled full-face wear is plainly visible across the scene and contradicts the maintained bright reactor target. The room retains a readable pool, two-bank hierarchy and open circulation, but material separation, colour/detail discipline and environmental credibility fall sharply. No planned future mask correction is counted. The next review must be judged from fresh renders after the visible regression is actually gone, with the control-glass defect and final cold-start evidence still outstanding.
