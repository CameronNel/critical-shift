# Spawn exterior + rescue courtyard review rubric

Status: Concept 02 approved for implementation; no built pixel, technical, or runtime acceptance is recorded here. Approval record: `CONCEPT_APPROVAL.md`.

Scope is the spawn exterior and its adjoining rescue courtyard, including the visible roof, shell, entry/apron, garden/rescue route, courtyard edge, and their interfaces. Interior art is out of scope except where it is visible through an exterior opening or where an exterior claim depends on preserving a source interior. The review must use exactly four locked views from the same saved revision: one top/plan view and three exterior gameplay-camera views. A view is only evidence for the pixels and geometry actually visible in that view. For the current A14 baseline, the IDs are `01_COURTYARD`, `02_SOUTH` (replacement for invalid `02_SOUTH_WEST`), `03_EAST`, and `04_TOP`, as recorded in `FIXED_CAMERAS.json` after final lock.

## Decision gates

1. **Evidence completeness gate.** A review package must identify the exact revision, source/assembly hash, camera names/transforms, render settings, and file paths for all four locked views. Missing, substituted, stale, cropped, or unreadable views are `UNVERIFIED`.
2. **Concept gate.** Before any polish or detail score, compare a clearly identified concept image/prompt to the same four-view composition. The concept must be explicitly `APPROVED` by the art owner, with deviations logged. Concept existence, a gallery thumbnail, or a build log is not approval.
3. **Pixel gate.** Inspect all four actual rendered images at native resolution, with no score awarded to unviewed pixels. A category that depends on a hidden side, occluded roof, or absent view is `UNVERIFIED`, never inferred from the scene file or a neighboring section.
4. **Technical gate.** Geometry, support, source preservation, route, and runtime claims require their own reproducible reports. Visual plausibility cannot substitute for a technical check, and a technical report cannot substitute for pixels.
5. **Threshold gate.** Score each category on a 0–100 scale only after its evidence is complete. Every category must be strictly greater than 93; `93` is a reject. Any `UNVERIFIED`, veto, missing evidence, or score at or below 93 makes the section `REJECT` and blocks polish/acceptance.

## Required view manifest

Record for each view: filename, revision, camera ID, projection/FOV, transform, resolution, render engine/settings, visible coverage, and reviewer initials/date.

| Locked view | Minimum coverage | Required checks |
|---|---|---|
| `04_TOP` | Whole spawn shell, roof, rescue courtyard, approach, edges, and adjoining reservations | footprint, roof plan, route continuity, scale/layout, terrain boundaries, occlusion |
| `01_COURTYARD` | Spawn arrival/courtyard relationship and apron from gameplay height | entry silhouette, door/apron, approach readability, scale, lights, signage |
| `02_SOUTH` | South exterior gameplay view with spawn shell and adjoining route | massing, rescue courtyard relationship, utilities, materials, focal hierarchy, shadows |
| `03_EAST` | East/reverse-service elevation and return route | reverse completeness, roof edge, supports, access, service logic, no façade-only dressing |

## Acceptance categories

Each category must include: score, `PASS`/`REJECT`/`UNVERIFIED`, observed evidence by view, and exact artifact or pixel coordinates. Do not average away a failed subcheck.

### 1. Reference fidelity and concept adherence

Concept 02 is the approved target. The built exterior must reconcile it with ART_DIRECTION, CANON, GAME_SPEC, and the section contract. Spawn reads as institutional, safe-but-oppressive, maintained and human; the courtyard reads as a purposeful rescue/clean connection. The approved palette is warm ivory plaster/concrete, deep desaturated olive sheet metal, restrained burnt orange accents, graphite trims, warm timber, and broad warm paving groups. Log every intentional deviation from Concept 02. Evidence: `CONCEPT_APPROVAL.md`; side-by-side crops from all four views; references to `design/ART_DIRECTION.md`, `design/CANON.md`, `design/GAME_SPEC.md`, and the applicable section contract. Pixel/build comparison remains required.

### 2. Silhouette and massing

Stepped spawn shell, roofline, entry, courtyard edge, and major rescue elements have specific, readable silhouettes at gameplay distance. Check negative space, skyline, overlap order, and recognition in front, oblique, reverse, and top views. Reject generic bevelled boxes, noisy clutter, or any major form identifiable only by labels/detail. Evidence: native-resolution crops and silhouette/flat-value overlays for all four views.

### 3. Scale and spatial layout

Doors, walls, parapets, service pieces, lights, vegetation/planters, rescue equipment, and courtyard proportions use believable human and facility scale. Spawn exterior aligns with the authoritative plan and adjoining rooms without visual or spatial drift. Evidence: top-view dimension overlay, known scale markers, source/assembly transform report, and front/reverse comparison. Unknown scale is `UNVERIFIED`.

### 4. Circulation, access, and rescue route

The arrival apron, spawn garden walk, adjoining rescue courtyard, clean/rescue shortcut, service access, and all visible portals read as traversable and purposeful. No route is blocked by dressing, inaccessible stairs, bad thresholds, dead-end visual promises, or unsafe pinch points. Preserve the required medical/rescue relationship. Evidence: top route overlay plus exterior views showing portal/route endpoints; route-width/headroom/threshold report; collision/navmesh evidence when available. A decorative path without technical route evidence cannot pass.

### 5. Construction and load/support logic

Roofs, coping, wall skins, canopies, stairs, planters, signs, lamps, rails, service flashing, and rescue fixtures visibly contact or plausibly anchor to the structure. No floating, intersecting, unsupported, paper-thin, or impossible cantilevered parts. Support/connectivity evidence must distinguish broadphase proximity from actual support/penetration. Evidence: reverse and oblique pixels, top roof contacts, evaluated geometry/support report, and source-preservation check.

### 6. Utility and service continuity

Visible pipes, conduits, cable trays, drains, vents, roof services, lights, and service panels have believable entry/exit, brackets, clearances, and destination logic. Avoid decorative pipe spaghetti and unexplained dead ends. Exterior additions must not fabricate uncontracted connections or cover reserved interfaces. Evidence: top/reverse/oblique annotated utility paths and a connectivity/clearance report naming endpoints and reservations.

### 7. Exterior materials and surface response

Painted metal, mineral/concrete wall, roof membrane, bare metal, glass, rubber, wood/planter surfaces, and paving are distinguishable, grounded, and consistent with stylized semi-realism. Use broad tonal variation, restrained roughness, localized contact wear, and no plastic/photographic-grunge failure. Evidence: material-ID or shader inventory plus native crops from each view under the approved lighting; hidden/unseen material faces remain `UNVERIFIED`.

### 8. Lighting, palette, and readability

Lighting establishes a readable key/fill hierarchy, practical entry/courtyard influence, contact shadow, falloff, and controlled warm/cool contrast. Spawn palette follows the approved warm ivory, deep desaturated olive, restrained burnt-orange, graphite, and warm timber grouping with purposeful safety accents; do not reintroduce a teal/cyan wash. Lights do not erase form or create unexplained roof patches/leakage. Evidence: all four actual renders, exposure/color-management manifest, light audit, and same-camera comparison against Concept 02. Saved flags without pixels are insufficient.

### 9. Environmental storytelling and human use

The exterior and courtyard communicate active work and rescue purpose through sparse, plausible objects: PPE/entry evidence, notice board or paperwork, maintenance kit, route markers, planters/cleaning, rescue staging, or repaired components. Placement must explain use and preserve breathing room; no filler clutter or walls of text. Evidence: front/oblique/reverse crops with an object-purpose ledger tied to visible items.

### 10. Terrain, drainage, and ground transitions

Paving, soil/planter beds, edge drains, coping, ramps, thresholds, courtyard grade, and terrain cutouts meet cleanly and shed water plausibly. No z-fighting, floating slabs, abrupt unart-directed voids, or unclaimed terrain infill. Evidence: top view and all low-angle views, ground-contact probes/height report, and transition/reservation map. Areas hidden in every locked view are `UNVERIFIED`.

### 11. Roof and elevated detail

The complete roof read is intentional from `TOP`, oblique, and reverse: membrane, seams, parapets/coping, girder/purlin rhythm, drains, vents, service housings, access points, and weathering are proportionate and supported. Check all roof planes for artifacts, emitter intersections, holes, repeats, and accidental bright patches. Evidence: top and oblique native crops, roof object inventory, emitter/extents/shadow diagnostics, and roof support report.

### 12. View-to-view consistency

The same revision, materials, lights, objects, route markings, and story beats remain coherent across all four locked views. No camera-specific dressing, pop-in, impossible occlusion, disappearing supports, contradictory doors, or concept drift. Evidence: four-view contact sheet, manifest hashes, and a discrepancy log. A missing or stale view rejects the category.

### 13. Interface and reservation integrity

Spawn shell and rescue courtyard preserve adjoining room portals, clean header, route reservations, source-owned doors/caps, and future connector space. No new exterior geometry claims an unbuilt corridor, floor, roof, or utility continuation. Evidence: top reservation overlay, portal/aperture audit, assembly transform/source hash report, and pixels from front/reverse interfaces.

### 14. Runtime and delivery readiness

For this exterior deliverable, runtime readiness means Blender assembly readiness: reproducible load of the reviewed assembly, relative dependencies, stable naming, no missing textures, no unintended hidden/holdout objects, validated geometry/support/route evidence, and a documented assembly performance check. This does not claim Unity game runtime readiness. Evidence: Blender cold-load log, dependency/hash manifest, geometry/collision or route audit appropriate to the assembly, material/texture validation, and assembly benchmark. Unity collision, navmesh, controller, cart/body-carrying behavior, and Unity performance remain a separate `UNVERIFIED` status until those checks exist. If Blender assembly evidence is deferred, score this category `UNVERIFIED` and reject.

### 15. Art-direction veto and professional finish

Across all four views, no hard veto dominates: generic low-poly or bevelled-box construction, toy-like scale/PPE, plastic materials, flat exposure, sci-fi greebling, excessive signage, procedural grime/cleanliness, photoreal noise, floating props, or unreadable silhouettes. The exterior must plausibly read as a commercially released stylized PC game environment. Evidence: reviewer checklist with pixel references for every veto and a final native-resolution contact sheet. Any veto is immediate `REJECT` regardless of numeric score.

## Review record template

```text
Revision:
Source/assembly hash:
Concept ID + explicit approval owner/date:
Locked view manifest:
Category scores (1–15):
Unverified items:
Vetoes:
Top blockers with pixel/artifact evidence:
Decision: REJECT / PASS (PASS only if every category >93 and all gates pass)
Reviewer/date:
```

## Baseline to beat

The current handover records spawn R05 with four actual views and a visual subtotal of 79/90, suitable for continued integration but explicitly not whole-section acceptance. Earlier R02–R04 reviews found roof light artifacts and support/connectivity limits; R05 reports the white roof patches gone after emitter shrink and raises lighting to 9/10, but technical readiness, full protocol acceptance, and two stable accepted rounds remain unclaimed. The A05 exterior handoff also states that terrain/large ground-cutout treatment, final materials/lighting, wear/storytelling, runtime collision/navigation, and Unity performance remain open or separately scoped. These historical scores and claims are context only; they do not score any pixels in this rubric.
