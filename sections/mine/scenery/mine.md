# Gullet Uranium Mine — Section Specification

**Status:** production foundation / generated Blender source supplied  
**Visual authority:** `design/ART_DIRECTION.md`  
**Gameplay authority:** `design/GAME_SPEC.md` Department One: Uranium Mine  
**Build protocol:** `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`

## 1. Section purpose

The Gullet is the raw-material department. It must make scanning, drilling/blasting, wet-ore decisions, structural risk, cart haulage and mine maintenance physically legible. It is a working industrial mine connected to a larger facility, not a cave-themed corridor or a decorative background set.

Players should be able to understand the basic work loop from the environment itself: prepare -> inspect/scan -> choose a face -> prepare/blast -> clear or support -> load ore -> haul toward refinery intake -> repair/reset -> repeat.

## 2. Macro layout

The mine begins in a **covered preparation and dispatch bay** attached to the facility and built against the mountain face. From this bay, the main rail/haulage route enters the portal and descends continuously at **2.5%**. There is no elevator.

The route is deliberately compact and composed rather than procedurally sprawling. It contains distinct work zones and branches while maintaining immediate first-person readability and a practical route back to the facility.

Major zones:

1. Facility connection / ore handoff edge.
2. Covered preparation, charge issue and cart staging bay.
3. Blast-door portal and threshold.
4. Main sloped haulage heading.
5. Dry seam work sector (A).
6. Wet seam / pumping sector (B).
7. Deep cut sector (C).
8. Maintenance return/service loop and selected recesses.

## 3. Preparation bay

The bay must feel like the last controlled workspace before entering rough ground. It contains:

- charge/dynamite issue point with physically separate pickup props;
- fictional blast/cut instruction chart;
- workbench and mining tools;
- cart parking/staging position;
- PPE/maintenance/storage evidence where composition allows;
- restrained paperwork and shift-use storytelling;
- mine portal controls;
- a visually substantial blast door;
- service routing that plausibly enters the mine;
- obvious connection back to the rest of the facility.

The bay should be dense only around its workstations. Preserve negative space around circulation and cart movement.

## 4. Blast door

The blast door is a functional industrial barrier, not a sci-fi decoration. It uses two independently authored leaves with frame/reveal construction, tracks/carriages, lower clearance around the rail path, drive/operator hardware and believable thickness. Closed and open states must not visibly destroy child transforms or intersect the rail system.

## 5. Haulage route

- Grade: 2.5% descending into mountain.
- Rail gauge authored around 1.10 m.
- Maintain a separate readable walking strip beside/around the cart path where required.
- Main route should remain comfortably navigable by a believable adult worker and avoid accidental pinch points.
- Rails require recognizable profile, sleepers, chairs/fasteners and joints at gameplay distance.
- Carts require recognizable chassis, hollow/tapered body, flanged wheels/axles, brake/handle detail and a movable hierarchy suitable for later Unity conversion.
- The route should visually communicate that loaded carts return toward the facility/refinery handoff without requiring an elevator.

## 6. Geology and structure

The underground shell is continuous authored geology generated from smooth excavated volumes and displacement fields. The visible result must not read as spheres, voxel blobs or a pile of primitive rocks.

Structural language:

- heavy mining arches/supports;
- anchor/splice/fastener detail where it matters;
- localized damaged support dressing in collapse states;
- selected quiet stretches with exposed geology;
- no repeated identical support every metre merely to fill space.

Rock surfaces should use broad tonal/roughness variation and controlled fresh-break contrast. Avoid noisy photogrammetry and procedural grunge everywhere.

## 7. Progressive excavation system

Each mineable sector has independent state alternatives:

- **sealed** — face not yet opened;
- **shallow** — small first pocket;
- **extended** — deeper/wider pocket;
- **deep** — full sector and shoulder/branch excavation;
- **collapsed** — the large excavation exists but access is blocked by rubble and damaged-support dressing.

Fictional cut/blast index mapping in the supplied authoring control:

- 0: no new work / retain state;
- 1–2: shallow;
- 3–4: extended;
- 5–6: deep;
- 7+: collapse.

These are **fictional game-balance indices with no physical units**. They must never become real-world explosive formulas.

Unlock behaviour is monotonic. A lower later index does not close deeper geometry. A new blast does not erase uncleared collapse rubble.

Each collapsed sector contains 22 individually identified removable rubble pieces. The gameplay implementation may later tune removal interactions, mass and teamwork requirements, but the authored state demonstrates the intended obstruction and clearance progression.

## 8. Sector identities

### A — Dry seam

Dry, dusty, comparatively stable. Serves as the clearest introduction to progressive excavation. Deeper states expand beyond a single straight face and create shoulder/fork space.

### B — Wet seam

Moisture is visually and mechanically important. Includes drainage, service water evidence, a working pump installation, recessed sump/grating and localized wet ground. It supports the safe-process versus wet-ore-shortcut decision from the game specification.

### C — Deep cut

The most spatially substantial excavation. Larger states broaden into shoulder excavations and are the strongest place to demonstrate the visual cost of an oversized blast/collapse.

## 9. Services

Use simplified real mining vocabulary:

- ventilation trunk/fan;
- cable trays and selected hanging leads with believable support/sag;
- water/drainage lines;
- pump and sump infrastructure;
- localized practical work lights;
- service brackets and penetrations that appear to lead somewhere.

Avoid decorative pipe spaghetti, glowing sci-fi strips and meaningless greebles.

## 10. Materials and lighting

Target material families include layered/fresh/dark rock, damp ground, concrete, painted steel, bare steel, timber, rubber/fabric and paper/signage.

Lighting should be constrained and practical underground, with clearly localized fixtures, contact shadow and darker secondary spaces. The preparation bay is safer and brighter without becoming flatly exposed. Wet areas may carry slightly cooler reflected value, but colour must remain functional rather than neon.

## 11. Environmental storytelling

Use restrained evidence of work: a used clipboard/shift card, tools, maintenance kit, scuffed traffic routes, repaired service wrap, slight cart wear, localized stains, one or two misplaced worker items. Do not blanket the mine in debris or wall text.

## 12. Fixed-camera review

The generated source provides ten review cameras covering entry, bay/dispatch, charge issue, main route, reverse route, dry cut, wet cut/sump, deep/collapse and other problem views. Once formal review begins, keep transforms fixed unless a camera is proven invalid and the change is recorded.

Every review must inspect actual rendered pixels for geometry seams, floating objects, rail/gate intersections, route clearance, support contacts, readability, material separation, over-gloss, excessive darkness, sign orientation and state overlap.

## 13. Runtime integration boundary

Blender is the visual source of truth. Unity receives static art, state variants, sockets/metadata and simplified collision where appropriate. Unity owns physics, cart behaviour, pickup/drop, explosive placement, detonation/state authority, network replication, rubble interaction, navigation, audio, particles and game-state causality.

Static concave geological collision must not be reused as dynamic rigid-body collision. Dynamic cart/rubble collision should use appropriate simplified convex representations.

## 14. Acceptance

The mine is not complete because a `.blend` saves. It must pass the repository protocol: deterministic fresh build, fixed-camera render review, scored criticism, correction cycles, regressions, and fresh-process cold-start verification. The initial supplied source has passed non-Blender geometry/state checks only; real Blender pixel approval is still required.
