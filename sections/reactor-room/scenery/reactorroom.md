# Reactor Room Visual Specification

**Status:** authoritative visual-production specification for the reactor hall art pass  
**Gameplay authority:** ../../../design/GAME_SPEC.md  
**Facility-layout authority:** `prototype/threejs-facility/DESIGN_NOTES.md`  
**Art-direction authority:** `../../../design/ART_DIRECTION.md`
**Surface-style rule:** this document remains authoritative for reactor layout, dimensions, object separation, interaction positions, and animation requirements; `../../../design/ART_DIRECTION.md` is authoritative for proportions, geometry language, materials, texture density, lighting treatment, and overall visual stylisation. Legacy realistic/PBR wording below is subordinate to that art bible.

This document defines how the existing compact reactor gameplay room is to be represented in finished 3D art. It does not replace the reactor simulation or its clockwise gameplay layout. Where the previous greybox used a simple central core cylinder and containment frame, the finished visual target uses a recessed water pool with two large visible control-bank drive assemblies.

The visual reference for this specification is the approved clean, sterile dual-bank reactor-room concept generated on 6 August 2026: a bright grey/silver industrial chamber with a cyan reactor pool, two labelled overhead `CONTROL BANK A` / `CONTROL BANK B` actuators, perimeter consoles, a visible control-room window, white coolant pipework, a fuel-handling position, sampling station and front-centre emergency shutdown. The reference image is an external production reference rather than a geometry source; absolute dimensions below are governed by the facility layout and the fit calculations in this document.

## 1. Non-negotiable visual identity

The reactor hall is a **clean 1990s industrial-science-fiction power room**, not a rusty bunker, steampunk room, contemporary laboratory or ultra-futuristic hologram set.

Required qualities:

- Sterile, maintained, bright working environment.
- Cool grey and off-white architectural shell.
- Broad cool-grey/off-white/blue-green machine colour blocks that suggest industrial metal without realistic brushed-metal microdetail.
- Restrained blue-grey / desaturated green equipment paint.
- White or very light grey coolant pipework with simple blue direction markings.
- A strongly luminous cyan-blue reactor pool as the room's visual hero.
- Two, and only two, dominant visible control-bank drive columns.
- Large physical buttons, guarded toggles, lever handles, analogue gauges, CRT-like displays and early flat-panel/industrial screens mixed together.
- Sparse graphic wear only where it communicates use or damage; no blanket rust, soot, grime, scratch noise, or realistic surface ageing.
- Functional labels, warning plates, numbered equipment and floor markings.
- No Soviet flags, red stars, hammer-and-sickle imagery or real-world political insignia.
- No dense forest of control rods. The room must read instantly from first-person gameplay distance.

The target remains consistent with `../../../design/ART_DIRECTION.md`: broad modular forms, readable silhouettes and production-feasible detail. The concept's clean finish must not become photoreal micro-detail or unique bespoke geometry on every surface.

## 2. Coordinate system and inherited room envelope

The facility authoring convention is metres, +X east, +Z south and +Y up. `SITE_SCALE = 0.6` scales plan coordinates and machine footprints but does not scale vertical dimensions or human clearances.

The authored reactor shell vertices are:

```text
(-10,-18) (10,-18) (18,-10) (18,10)
(10,18) (-10,18) (-18,10) (-18,-10)
```

After the 0.6 plan scale, the finished in-game shell vertices are exactly:

```text
(-6.0,-10.8) (6.0,-10.8) (10.8,-6.0) (10.8,6.0)
(6.0,10.8) (-6.0,10.8) (-10.8,6.0) (-10.8,-6.0)
```

Therefore:

| Quantity | Confirmed value |
|---|---:|
| Maximum X span | 21.60 m |
| Maximum Z span | 21.60 m |
| North / south straight wall length | 12.00 m |
| East / west straight wall length | 12.00 m |
| Each diagonal wall length | 6.788 m |
| Plan area inside shell polygon | 420.48 m² |
| Clear reactor-hall height | 16.00 m |
| Main floor datum | Y = 0.00 m |
| Existing overview datum | approximately Y = +4.8 m |

The 420.48 m² area is the polygon area of the scaled shell, not an estimate.

## 3. Central pool geometry

The pool replaces the old simple central-core visual while preserving the central gameplay footprint and the surrounding clockwise station ring.

### 3.1 Authoritative dimensions

| Feature | Dimension |
|---|---:|
| Pool centre | X 0.00, Z 0.00 |
| Open water aperture diameter | 6.80 m |
| Structural pool rim outer diameter | 7.80 m |
| Radial solid rim width | 0.50 m |
| Outer service/circulation-ring diameter | 10.40 m |
| Service-ring width outside structural rim | 1.30 m |
| Water surface | Y = -0.45 m |
| Finished floor | Y = 0.00 m |
| Pool shaft bottom | Y = -6.50 m |
| Minimum modelled shaft depth below water surface | 6.05 m |
| Pool guardrail height | 1.10 m |
| Nominal rail-post spacing | 1.30-1.50 m |
| Front fuel/service gate clear width | 1.40 m |
| Front-centre stair / approach clear width | 1.80 m |

The 7.80 m structural rim deliberately matches the current scaled containment footprint: the existing `13 m` authored containment dimension becomes `13 × 0.6 = 7.8 m` in plan.

The 10.40 m circulation envelope has radius 5.20 m and occupies 84.949 m². It leaves 335.531 m² of the 420.48 m² shell polygon outside that circular envelope before perimeter stations are counted. The annular circulation area between the 7.80 m rim and 10.40 m outer service ring is 37.165 m².

### 3.2 Fit against existing station ring

With a 5.20 m outer service-ring radius, the nearest existing perimeter-machine footprint remains outside the pool envelope. Fit was checked against the current scaled machine centres and X/Z footprints in the future reactor gameplay implementation.

Approximate minimum planar clearance from the 5.20 m service-ring radius to the nearest edge of each existing major station footprint:

| Station | Minimum clearance |
|---|---:|
| Fuel receiving | 2.05 m |
| New fuel rack | 2.30 m |
| Control position | 1.86 m |
| Waste transfer | 3.72 m |
| Vent valve | 3.66 m |
| Turbine throttle | **1.31 m** |
| Grid breakers | 3.21 m |
| Grid demand | 2.21 m |
| Sensor | 4.54 m |
| Coolant pump | 2.32 m |
| Coolant valves | 2.30 m |
| Emergency cooling | 1.57 m |
| Backup generator | 2.60 m |
| Reserve power | 3.05 m |
| Live repair bay | 3.04 m |

The turbine-throttle side is the tightest at about 1.31 m, which is acceptable for a compact workroom but should not be further narrowed by decorative clutter.

The old central-south alarm/SCRAM island is the one greybox element that conflicts with the new pool. In finished art, its function moves onto the **south pool-side emergency console / front-centre gate**. This preserves the intended central visibility and short run while freeing the pool centre. The gameplay meaning does not change.

## 4. Reactor pool internals

The pool is a fictionalised power-reactor service/cooling pool chosen for visual readability and gameplay, not a claim of exact real-world reactor engineering.

Required internals:

- Deep cylindrical/segmented shaft with broad pale wall segments that suggest tile, enamel or metal without realistic surface microdetail.
- Cyan emissive light source concentrated low in the shaft rather than a uniformly glowing flat water plane.
- Two submerged circular guide/manifold assemblies aligned to Control Bank A and B.
- Simplified submerged structural frame and core housing visible through the water.
- Sparse pipes, intake/outlet openings and service brackets on shaft walls.
- Enough visible depth that the pool reads as a dangerous volume, not a shallow basin.
- Water surface and emissive underlayer must be separate assets/materials so normal, high-output and emergency states can be animated independently.

Normal water should be clean cyan-blue. Cherenkov-inspired light is intentionally exaggerated for game readability.

## 5. Two-control-bank system

There are **exactly two dominant visible moving drive assemblies**. They represent two reactor control banks, not two individual absorber rods. Any smaller absorber elements are implied below the water and must not become a visible rod forest.

### 5.1 Placement

| Feature | Control Bank A | Control Bank B |
|---|---:|---:|
| Axis X | -1.40 m | +1.40 m |
| Axis Z | 0.00 m | 0.00 m |
| Axis separation | \- | 2.80 m centre-to-centre |

Each lower interface must remain inside the 3.40 m water-aperture radius.

### 5.2 Per-bank dimensions

| Part | Target dimension / range |
|---|---|
| Fixed upper actuator housing | 1.80 m max diameter / width |
| Fixed upper housing height | 2.60 m |
| Lower moving carriage | 1.45 m max diameter / width |
| Moving carriage height | 1.55 m |
| Visible drive column | 0.46 m diameter |
| Submerged lower guide/interface | 1.45 m diameter |
| Overhead structural support centre | approximately Y = +14.2 m |
| Upper housing vertical zone | approximately Y = +9.8 to +12.4 m |
| Moving carriage nominal centre | approximately Y = +8.6 m |
| Normal visible drive-column span | from submerged guide to moving carriage |
| Usable animated vertical travel | 1.80 m |

The exact actuator silhouette may be adjusted within these maxima to match the approved concept, but axes, two-bank count and room clearances are fixed.

### 5.3 Animation meaning

The two banks are major gameplay-readable moving objects:

- **Normal power:** slow, deliberate independent trim movements measured in centimetres to tens of centimetres.
- **Load change:** one or both banks visibly reposition over several seconds.
- **Instability:** small unequal hunting/oscillation makes the problem readable before catastrophic effects begin.
- **SCRAM:** both moving carriages / visible columns make a rapid downward emergency movement using the available 1.80 m travel, followed by a hard mechanical stop and small damped rebound. The animation should read as one decisive event, not dozens of tiny rods moving.

Do not animate the entire fixed motor housings as if they are free-hanging pistons. Separate fixed support, moving carriage and sliding drive column.

## 6. Pool-side circulation and emergency console

The room must preserve a continuous, readable circulation loop around the pool.

- Keep at least 1.20 m usable path width at the tightest point after art dressing.
- The existing station-fit calculation leaves about 1.31 m at the turbine side; this is the hard minimum. Do not put trash, decorative tanks, cable coils or structural feet in that clearance.
- Provide one 1.40 m service/fuel gate in the pool rail at the south/front side.
- Put the physical **EMERGENCY SHUTDOWN** control at the south/front rail or immediately outside it, centred and visible from most of the room.
- Put alarm acknowledgement / automatic-shutdown bypass on the same south-side emergency console family but as distinct controls.
- Keep the SCRAM control as a separate animatable/button/guarded-handle asset.

This replaces the greybox's old central-south island without changing the emergency role of that station.

## 7. Clockwise gameplay-to-art mapping

The art pass must preserve the reactor gameplay logic already defined in `../../../design/GAME_SPEC.md` and the future reactor gameplay implementation.

| Sector | Required visual functions |
|---|---|
| North | fuel receiving, new/uncertain fuel position, reactivity/control-bank control |
| North-east | waste transfer, illegal-waste opportunity, containment vent |
| East | turbine throttle, grid breakers, demand/output displays, sensor/containment instrumentation |
| South | coolant controls, pump status, emergency cooling, central emergency shutdown presentation |
| West | backup generator, reserve power, live repair / spares |
| Centre | reactor pool, submerged core, Control Bank A/B |
| Overlook / control side | plant mimic, reactor status, demand, operator desk visibility |

The art may combine several greybox blocks into a convincing console bank, but each gameplay interaction must remain separately addressable in the eventual game implementation.

## 8. Control-room window and operator space

The visual reference shows an enclosed operator room behind glazing. This corresponds to the existing raised Control zone east of the reactor rather than creating a new separate room.

For the reactor-hall art composition:

- Present a large internal observation window toward the existing control side.
- Target visible glazing module: approximately 5.4 m wide × 2.6 m high.
- Use a chunky 1990s industrial frame, laminated/safety glass and a deep sill/reveal.
- Show desks, CRT/early-digital displays, chairs and plant mimic equipment through the glass.
- The finished level must still respect the Control room's actual +10 m gameplay datum and direct link defined in the facility layout. A beauty camera may compress perspective but must not redefine the route.

## 9. Architectural and prop language

### 9.1 Shell

- Octagonal room geometry remains readable.
- Ceiling height remains 16 m; use overhead trusses, bank supports, cable trays and pipes to occupy the upper volume without visually lowering it into a tunnel.
- Wall panels should be modular, broad and lightly segmented.
- Floor should be clean industrial plate / sealed composite with service hatches and restrained yellow-black hazard lines.

### 9.2 Pipework

Use a small number of thick, legible routes rather than engineering spaghetti.

Required labelled families:

- `COOLANT SUPPLY`
- `COOLANT RETURN`
- `SAMPLING LINE`
- local vent / relief route
- cable trays / power conduits

Primary coolant pipe visual diameter target: 0.30-0.45 m. Secondary utility lines: 0.08-0.18 m. Pipe clamps, flanges and elbows should be modular/reused.

### 9.3 Consoles

Console proportions should be chunky and human-operable:

- standing console worktop height: approximately 0.95-1.05 m
- sloped control face: roughly 25-40 degrees
- typical single-bay width: 0.9-1.4 m
- typical console depth: 0.65-0.90 m
- screens should be individually replaceable objects/material slots
- major lever, guarded switch, breaker handle and emergency control meshes must remain separate where animation is likely

Use a 1990s mixed-instrument language: analogue gauges, segmented indicators, CRT-like displays, early flat industrial displays and physical controls can coexist.

## 10. Fuel handling and sampling features

Required visual features from the approved concept:

### Fuel handling position

- One compact wheeled fuel-handling caddy/cart near the south-west/front pool side.
- Maximum parked footprint approximately 1.25 m × 0.85 m so it does not destroy circulation.
- Cart, wheels, rack, retaining mechanism and payload slots should be separable for animation.
- It must be movable away from the pool; do not bake it into architecture.

### Sampling station

- South-east/front floor position, visually quieter than the emergency control.
- Small labelled panel, hose/line connection and sample container position.
- Approximate standing interaction footprint: 0.8 m × 0.6 m.
- Sampling hose/connector should be separate.

## 11. Individual asset / animation contract

The Blender scene must not be a single merged environment mesh. At minimum, the following require separate objects or clean parented assemblies:

### Architecture

- shell wall modules
- floor modules
- pool shaft
- structural rim
- service ring
- guardrails and gate
- front stair / steps
- control-room glazing and frame
- operable door leaves / frames
- ceiling supports

### Reactor

- water surface
- blue emissive underlayer / core-light source
- submerged core structure
- Bank A fixed housing
- Bank A moving carriage
- Bank A drive column
- Bank A submerged guide
- Bank A indicators / label plate
- Bank B fixed housing
- Bank B moving carriage
- Bank B drive column
- Bank B submerged guide
- Bank B indicators / label plate

### Interactive room equipment

- fuel handling cart and wheels
- emergency shutdown control
- alarm acknowledgement control
- automatic-shutdown bypass control
- turbine throttle handle
- major breaker handles
- coolant valve wheels / manual controls
- vent valve wheel/control
- door leaf
- warning beacons
- important gauge needles where used
- individual screen meshes/material surfaces

Objects intended to rotate must have origins at their hinges/shafts. Sliding objects must have local axes aligned to the intended travel. Bank A and B moving assemblies must have local Z/Y motion set up cleanly for vertical animation.

## 12. Material families and texture-light sourcing

The reactor room uses a restrained reusable material palette consistent with `../../../design/ART_DIRECTION.md`. Materials should read by **large value/colour blocks and simple response**, not by photographic texture detail.

Required material families:

1. off-white / pale structural shell
2. cool grey machine body
3. blue-grey / muted green equipment accent
4. dark sealed floor / floor-panel family
5. white or very light coolant pipe family
6. dark rubber / grip / boot-like utility material
7. simple clear / smoked glass for windows and protective covers
8. dark screen glass
9. emissive cyan reactor light
10. coloured indicator / emergency emissives
11. small yellow-black hazard marking / decal set
12. sparse contamination / scorch / damage decal family

Preferred implementation:

- Solid colours, gradients, vertex colour, simple masks and restrained roughness variation first.
- Little or no normal-map detail on ordinary architecture and machines.
- Reuse the same material families across many objects.
- Use sparse decals only for labels, hazards, contamination and meaningful damage.
- Do not use realistic brushed-metal normals, dense scratches, photographed grime, cloth weave, or high-frequency wear as a finishing layer.
- Most ordinary assets should need no unique texture set. When textures are necessary, prefer small reusable textures; 512–1024 px is generally sufficient, with 2K reserved for a demonstrated hero/close-interaction need.
- Any externally sourced texture or material retained in production must have a compatible licence and recorded source, but the art pipeline should not depend on realistic PBR libraries.

## 13. Lighting and state progression

The healthy room is **bright**, not depressing.

### Normal

- cool-white ceiling practicals provide the majority of illumination
- cyan pool provides a strong secondary bounce and local glow
- neutral grey walls remain clearly visible
- small amber/red/green indicators punctuate consoles

### High output

- pool cyan grows brighter and more directional
- subtle water agitation and brighter lower-core emissive
- bank positions visibly change
- normal room lights stay functional

### Instability

- asymmetric bank motion/hunting
- pool emissive pulses rather than merely changing UI bars
- a few amber alarm states begin

### Cooling emergency

- water level may visibly fall by up to approximately 0.60 m for dramatic readability
- steam/fog begins at the pool and coolant equipment
- pump/pressure indicators transition to emergency state

### SCRAM

- both control-bank moving assemblies drop together through their 1.80 m emergency travel
- hard mechanical impact, brief vibration and water disturbance
- emergency lights activate
- pool intensity should begin decreasing if shutdown succeeds

### Core damage / meltdown

Do not make the whole scene uniformly red.

- retain cyan/blue water around the perimeter initially
- introduce increasingly white-hot light below the core, then controlled orange-white contamination of the lower glow
- use steam, haze, violent water motion, pipe vibration and local lighting failures
- escalation should be staged and readable

The pool is effectively a giant diegetic reactor-health display.

## 14. Beauty-camera target

The approved concept composition should be reproducible with a dedicated Blender beauty camera:

- elevated position near the south/front side of the room
- looking slightly downward into the pool
- both foreground console banks frame the lower corners
- front-centre stair / emergency control leads the eye to the pool
- both Control Bank A and B dominate the central vertical silhouette
- control-room glazing is visible in the rear field
- coolant pipework and tanks frame the upper/side walls

Start camera tuning around a 26-30 mm full-frame-equivalent lens and adjust position rather than using extreme wide-angle distortion. The gameplay camera is not required to match the beauty camera.

## 15. Explicit prohibitions

Do not introduce:

- more than two dominant visible bank drive columns
- dozens of exposed control rods
- an enormous hall that breaks the 21.60 m envelope
- dark horror lighting as the normal state
- extensive rust or abandoned-facility decay
- steampunk brass/copper language
- glossy Apple-lab futurism
- holographic interfaces everywhere
- Soviet symbols or political insignia
- decorative clutter inside the 1.20 m minimum circulation path
- fused animation-critical machinery that would have to be remodelled to move later

## 16. Relationship to the current Three.js greybox

The existing Three.js reactor remains the authoritative route/interaction greybox until deliberately updated. The Blender art pass should use this document to interpret that geometry rather than silently changing gameplay.

Visual reinterpretations introduced here:

1. `reactor.core` + `reactor.containment` become the **central recessed pool / submerged core** visual family.
2. The reactor gets **two visible Control Bank A/B drive assemblies** above the pool.
3. The old central-south alarm/SCRAM island is visually relocated to the **south pool-side emergency console / service gate** because the pool now occupies the centre.
4. The control-room relationship is rendered as prominent observation glazing while preserving the existing Control-zone route and elevation.
5. The pool, banks, water, consoles and interactive controls are built as animation-ready individual assets.

No other clockwise sector or door relationship changes in this visual specification.

## 17. Production acceptance checklist

A reactor-room Blender scene conforms to this specification only if all of the following are true:

- shell fits the confirmed 21.60 m scaled reactor envelope
- clear vertical volume respects the 16.00 m room height
- central pool outer structural rim is 7.80 m diameter
- water opening is 6.80 m diameter
- outer pool circulation envelope is 10.40 m diameter
- exactly two dominant visible control-bank drives exist
- their axes are at X ±1.40 m, Z 0.00 m unless a documented art review changes them
- minimum dressed circulation remains at least 1.20 m
- clockwise gameplay station logic remains legible
- emergency shutdown remains centrally visible/reachable on the south pool side
- normal lighting is bright, sterile and readable
- pool cyan is the hero visual
- Control Bank A/B, water, doors, major controls, cart and important valves remain individually animatable
- shared texture-light materials follow `../../../design/ART_DIRECTION.md`; any external material sources used are permissively licensed and recorded
- the room reads as clean 1990s industrial science fiction rather than steampunk, abandoned Soviet industrialism or ultra-modern laboratory futurism
