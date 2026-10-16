# Mine exterior: fixed-camera reference contract

## Task and source

Cameron requested native full-map screenshots of the mine exterior, ChatGPT-generated style references derived from those actual views, and Blender revisions compared against the references from the same cameras. Earlier imaginary mine concepts are excluded. They are not screenshots, accepted designs, or evidence of the current map.

Base main commit: `a82c7d9b80456153a0c65ca4897044a7f62c7d1c`.
Task branch: `art/mine-exterior-camera-match-20260914`.
The authoring source is the full R17 scene named by `MAP.json`; its full-map material-preview scene is used to select inspection cameras. Do not replace the map with a standalone mine, older master, or newly invented layout.

The first actual native open recorded 55,390 objects, 24 linked libraries and 105 image datablocks. The first software-EEVEE capture did not produce usable image evidence before it was superseded. The replacement capture uses Cycles on CPU for bounded offline screenshots; it does not change or save the source scene's EEVEE setup. No visual acceptance follows from the native open.

## Camera discipline

The capture script is `../../blender/capture_mine_fixed.py`. Camera selection happens inside the actual assembled map. Record the matrix, lens, sensor, shift, clipping planes, image resolution and aspect in `CAMERAS.json` with the capture artifact. A viewpoint must be checked for obstruction before it becomes the fixed comparison camera.

Once selected, the reference-source frame and every candidate comparison use that exact framing. Do not move the camera, crop the render, hide adjoining buildings, change focal length, or replace the scene to make a result look better. If a camera is demonstrably invalid, record why, establish a new actual baseline, and regenerate the corresponding reference before grading.

A generated reference is a design target, never evidence that Blender has been changed. No reference-image billboard or camera-projected picture may substitute for three-dimensional geometry. Preserve the mine entrance, rail/haulage route, pedestrian access and adjoining map connections.

## Nine-category gate

Each category is scored from 0 to 100. **Every category must reach 92.** The minimum score governs the decision; a high average cannot hide a failing category. Scores are not assigned before the current same-camera images exist.

| Category | Required evidence |
| --- | --- |
| Reference fidelity | Same-camera composition, feature placement, major surface grouping and intended art treatment match the chosen actual-scene-derived reference. |
| Geometry and scale | Believable portal, canopy and structural proportions; specific primary and secondary forms rather than a primitive-only finish. |
| Materials and palette | Readable painted metal, concrete, rock and ground; broad controlled variation, restrained wear and no toy gloss or photographic grunge blanket. |
| Lighting and values | Consistent light direction, readable shaded entrance, contact shadows and focal hierarchy; darkness and exposure do not conceal defects. |
| Rock and ground transitions | Authored rock planes and convincing terrain/paving/wall junctions without coarse accidental triangulation, floating edges or random debris. |
| Construction and utilities | Credible canopy supports, joins, drainage, cable/pipe continuity and mounted-fixture contact. |
| Storytelling and detail control | Purposeful work props, restrained readable signage and human use, balanced against quiet surfaces and clear movement space. |
| Route and map integration | Door openings, freight/rail and pedestrian paths remain clear and consistent with the adjacent full map. |
| Professional finish and cross-view consistency | No clipping, floating props, mismatched surfaces or camera-specific tricks; the secondary fixed views also hold up. |

## Independent checks and honest status

Native dependency/file checks and visual criticism are separate. Preserve original source-module and texture file hashes. Reopen delivered scene assets in a fresh Blender process. Record the exact artifact, image and camera hashes for each review.

Reviewer provenance must be explicit. Author self-review must not be described as a separate independent reviewer. A scripted pass cannot award artistic scores. Missing independent review, missing renders, unverified runtime behavior or unsuccessful tests remain pending or failed, never silently passed.

After a score below 92, record concrete visible defects, repair the corresponding scene/source, rerender the same camera and reassess. Record regressions and retain a known-good state. No direct edits or self-merge into main.

## Status when this contract was committed

Actual full-scene open: completed. Camera captures: in progress. Scene-derived reference generation: not yet completed. Scene editing: not started. Visual scores and independent acceptance: pending. This file is a fixed contract, not a completed-art claim.
