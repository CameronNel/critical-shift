# Environment image inputs

These were created with ChatGPT's built-in image generator. Concept images are targets, not screenshots of completed work. The facility geometry in the Blender file remains authoritative when a generated image differs from it.

## mine-yard-wide-angle1-target.png and mine-yard-wide-angle3-target.png

Current one-shot finish targets. Generated with ChatGPT's built-in image tool
from `MineYardAngle1Wide.png` and `MineYardAngle3Wide.png` after both screen-wall
assemblies and their separate cladding were removed. Cameras retain their original
positions but use 11 mm instead of 22 mm lenses, doubling the framing dimensions.
The concepts are paintovers, not screenshots. Generated sky/clouds and changes to
distant silhouettes are not authority to remodel the map.

Prompt set used (shared brief plus view-specific details):

- Style-transfer edit of the exact current Blender scene. Premium
  Valorant-inspired grounded stylized semi-realism. Preserve widened camera,
  aspect, framing, horizon, perspective, building positions, canopy, pillars,
  doors, mine cart, routes and scale. Never recreate the removed screen walls.
  An achievable one-pass material and edge-dressing brief, not a redesign.
- Entrance: broad slate/blue-grey rock planes, warm exposed faces, restrained
  strata and unchanged mountain silhouette. Matte concrete with subtle seams,
  localized wheel wear and a small repair. Thin irregular gravel/grass only at
  the cliff foot and wall bases. Preserve existing reels/cases and quiet central
  yard. Muted blue-grey panels, pale warm concrete, dark steel, ochre safety
  accents; warm daylight, cool shadows, useful warm canopy fixtures.
- Reverse: retain every wall, roof edge, drain, downspout, conduit, opening,
  bollard and prop position. Broad concrete variation, localized wheel scuffs,
  small flush slab repair, worn existing route paint, faint runoff below real
  caps and sparse low corner wear. Material separation on cabinet and conduit;
  tiny edge grass/gravel, never blocked drainage or circulation. Bright playable
  daylight and readable roof structure, warm localized practical lights.
- Avoid new architecture, moved structures, invented mountains/openings/roads,
  large new props, people, weapons, logos, text overlays, sci-fi glow, photographic
  micro-noise, excessive grime, wet plastic, random clutter, outlines, cinematic
  fog/darkness or exaggerated saturation. Output a single matching landscape
  paintover for each supplied scene view.

## mine-yard-angle1-target.png and mine-yard-angle3-target.png

Superseded for current work by the widened concepts below. These older concepts
still contain the two screen walls that the user subsequently requested removed.

Generated with the built-in image tool from the actual close player-height
`MineYardAngle1.png` and `MineYardAngle3.png` captures. The second image also used
the first concept as a material/detail consistency reference. These supersede
aerial concepts for the mine-yard art pass. The original layout and camera remain
authoritative; concept-only altered rock shapes and shifted structural details
must not silently replace source geometry. Geometry repair is the first gate.

Prompt set:

1. Style-transfer paintover of the actual mine-yard screenshot, exact camera,
   walls, roof, pillars, openings, scale and layout preserved. Polished AAA
   Valorant-inspired grounded stylized game environment, no copied game assets.
   Lightly worn large concrete slabs, sparse joints, narrow edge drain, worn ochre
   route lines, resolved slab/ground contact, capped slate-blue steel panels and
   warm concrete. Two small margin-only maintenance clusters with cable reel,
   supply crate, service box and tidy conduit. Sparse edge gravel/tufts, readable
   daylight and warm practical fixtures. No people, guns, logos, neon, new
   structures, changed viewpoint, overgrown ruin or blocked circulation.
2. Preserve the exact Angle3 camera and all existing geometry; use concept1 only
   for coherent material/detail direction. Warm segmented concrete, restrained
   wear, ochre edge paint, drain and downspout catch basin, existing blue/white/
   orange palette, purposeful utility details at margins. Soft skylight and warm
   canopy practical lights. Keep existing 02/refinery label, distinguish concrete,
   steel and rubber. No new walls, roads, doors, aerial view, photoreal noise,
   characters, excessive clutter or fantasy redesign.

## environment-target.png

Input: the actual `OriginalMapReference.png` headless render, with the original 194 × 155 metre floor and original map geometry/materials.

Prompt:

Use case: stylized-concept. This is an EDIT of the attached ACTUAL Blender game-map render, not permission to design a new map. Create one high-quality 16:9 environment concept paintover matching this exact elevated camera. Preserve EVERY existing industrial building, courtyard, route, structure, portal, material identity, position, scale and relative spacing exactly. Preserve the full facility silhouette. The bare rectangular concrete platform is the existing playable footprint, about 194 by 155 metres. Allowed additions ONLY outside that footprint, except replace/engulf the obvious floating brown mine roof sheet at upper left with a believable continuous mountain that encloses the mine. Add a substantial asymmetrical blue-grey bedded schist mountain behind that existing mine on the left/back, with long angular rock planes, a few terraced outcrops and restrained grassy shoulders, NOT jagged noise or rounded blobs. Outside the right-hand edge of the map add a glacial teal lake, broad forested banks and distant layered low-poly mountains; at the near/front end of the lake a practical warm-concrete hydro dam with two teal sluice gates, service catwalk and small maintenance building; two readable cascades into one river winding off the foreground. Lake stays BELOW the facility floor; no inundation or rebuilding. Grouped distant conifers with clearings, credible tree scale. Grounded stylized semi-realism inspired by Valorant's environmental principles: broad controlled colour blocks, specific sculpted forms, readable material separation, restrained low-frequency textures, subtle warm sun/cool shadows and atmospheric depth. This is a target for an actual economical game backdrop, not a photoreal matte painting. No new facility buildings, no invented combat arena, no brand marks, no text, no UI. Keep map layout absolutely locked.

## mine-rock-target.png

Inputs: actual `MineApproach.png` work-in-progress render and `environment-target.png`.

Prompt:

Use case: stylized-concept, precise environment paintover. Image 1 is the EXACT ground-level game scene and edit target; image 2 is supporting whole-site art direction only. Keep the same viewpoint/framing. Preserve every industrial mine structure in image 1 EXACTLY, especially the dark metal entrance canopy and beams, supports, walls, lights and equipment visible in the lower right. Do not add, remove, resize or shift any architecture. Redesign ONLY the mountain rock in the upper/left portions. Replace the overly pale, smooth, triangular bands with believable stylized blue-grey schist: broad irregular angular vertical planes, several stepped bedding ledges, fine sparse cleavage cracks, grounded buttresses, modest moss/grass on horizontal shelves. Shapes need specific authored geology, not conical peaks, noisy stone, a stack of blocks or a sci-fi cliff. The mine should visibly enter one continuous massive mountain. Warm afternoon light across ridges, restrained cool shadow planes, balanced grey stone exposure, contrast that keeps entrance readable. Match high-quality Valorant-style environmental principles, not photorealism; texture detail must remain restrained and attainable in economical game assets. No characters, no text, no new buildings, no changed camera, no impossible floating rocks. Output one polished 16:9 concept paintover.

## ../blender/environment-textures/schist-basecolor.png

Actual material input, packed inside the environment Blender file. Base colour only; not a scanned PBR material or a generated normal map. Triplanar projection and separate modest procedural bump are used on the new rock materials.

Prompt:

Use case: stylized-concept. Asset type: actual seamless game-material BASE COLOR texture, square, edge-to-edge, not a scene or concept picture. Create a professionally painted tileable blue-grey schist rock albedo for a grounded Valorant-style mountain environment. Orthographic flat surface with NO perspective, NO objects, NO scenery, NO cast shadows, NO directional illumination, NO ambient occlusion baked in, NO specular highlights. One uninterrupted rock surface. Deliberate broad angular geological colour planes, elongated near-vertical cleavage with a subtle diagonal tilt, sparse thin dark grey fissures, broad warm grey lighter mineral patches and slate muted blue-grey midtones. Mid-grey exposure, subtle colour contrast, no pure black/white. Several large irregular rock planes rather than a grid of paving stones, no bricks, no honeycomb cells, no stripes. Restrained hand-painted edge definition and very sparse small chips. Believable geology simplified for a high quality stylized PC game, NOT photoreal scan noise, NOT cartoon outlines. Most of the image quiet broad rock; large clefts distributed unevenly. Strictly seamless/tileable on all four edges, no border, text, watermark or presentation layout. This texture will tile every approximately 6-8 metres across actual authored rock geometry.

Seamlessness and visual quality still require scene review; a generation prompt is not proof that those constraints were met.

## Mine exterior refinement concepts — 2026-09-20

The following four images were generated with the built-in ChatGPT image tool
from actual headless Blender captures of `facility_environment.blend`. They are
concept paintovers, not evidence of completed geometry. The saved scene,
measured interfaces and fixed player cameras remain authoritative. All four
were independently inspected by Luna before implementation. No concept in
this bounded set was rejected; actual geometry/render reviews did require
corrections, including the courtyard rock scores of 86 for geology and 88 for
materials before its targeted pass.

| Concept | Actual input | Luna concept score range | Purpose |
| --- | --- | --- | --- |
| `mine-entrance-refinement-target.png` | `02_THRESHOLD`, original scene SHA `9f6b0d3d…` | 92–97 | Entry material separation, useful warm lighting and the existing mine identifier backing. |
| `mine-approach-construction-target.png` | `01_ENTRY`, scene SHA `e66738a9…` | 94–97 | Existing narrow continuation walls, coping, edge protection and concrete approach. |
| `mine-canopy-cliff-junction-target.png` | `04_SOUTH_APPROACH`, scene SHA `e66738a9…` | 92–96 | Canopy construction, visible cliff toe and yard-edge material transitions. |
| `mine-courtyard-rock-target.png` | `09_COURTYARD_SKYLINE`, scene SHA `4980a239…` | 93–96 | Irregular bedded rock planes visible from the existing courtyard route. |

Prompt constraints shared by the set: strict grounded Valorant environmental
art principles, original industrial construction, tactile matte materials,
clear primary forms, controlled broad values, restrained industrial colours,
useful daylight and warm practical fixtures. No teal, cyan, neon, copied game
assets, cinematic fog, photographic micro-noise, people or changed map layout.

Prompt details:

1. Preserve the exact threshold camera, jambs, canopy, rails, cart, two gate
   equipment assemblies and octagonal mine portal. Refine warm concrete,
   bolted steel and matte materials; combine readable warm practicals with
   daylight. Correct the existing identifier to `GULLET / 01`. No lift, new
   wall or larger opening. Any concept perspective/plate-size drift is not
   authority to change the measured opening or backing.
2. Preserve the exact open approach and existing 150 mm thick, 3.6 m high
   walls, mountain, trees and railings. Use warm-grey cast concrete, restrained
   panel joints, charcoal narrow coping and leading-edge protection with
   fixings, an ochre datum and matching slab joints. No roof, gate or clutter;
   retain at least 4.4 m clear passage.
3. Preserve canopy, posts, panels, rails, drain, bollard, cart, reel, case and
   portal. Refine only the visible cliff/yard junction using broad angular
   bedrock, grounded shoulders, sparse edge grass, matte concrete slabs and
   warm daylight with soft fill. Keep the roof structure readable. No changed
   major silhouette, added wall or blocked route.
4. Edit only the visible mountain behind the courtyard; preserve camera,
   overall silhouette and volume, shelf elevations, trees, sky, architecture,
   roof edges, panel walls, benches, planter, signs, shadows and paths. Resolve
   artificial triangular ribbons as continuous grey-brown schist with broad
   asymmetric interlocking planes, offset stepped seams and selective narrow
   fractures. Keep the large slopes and terraces. No floating overhangs,
   repeating blocks, giant zigzag stripes, noisy photogrammetry, new foreground
   rock, new room or new door. Retain controlled warm sun-facing stone and
   charcoal recesses under the same daylight direction.

Generation provenance: thread `01a07deb-e7a7-7ee1-b3c6-03e0ad16ca0c`; output IDs
`exec-02137ede-e765-4a32-adcf-fd8befc29a85`,
`exec-7cf5abdd-f932-43cb-92d8-38b40c71a9ec`,
`exec-92137fba-bc48-48ce-851a-88df397da9c3`, and
`exec-b8d8693c-7a74-4a70-b0bd-ef2463355134`, respectively. Originals remain in
the generation output folder; the project copies above are the durable inputs.

## Mine-to-refinery transition concepts — 2026-09-27

These three built-in image-tool paintovers use the actual textured
`facility_environment.blend` capture
`mine-to-refinery-angle-review-textured-20260927.png` as their locked camera and
layout reference. They are design directions only, not authority to move doors,
change the railway alignment, block circulation or alter measured interfaces.

| Concept | Direction |
| --- | --- |
| `mine-refinery-transition-maintenance-frontier.png` | Mixed track repairs, purposeful off-route equipment and material stacks, with the strongest general mine-to-plant gradient. |
| `mine-refinery-transition-failed-modernization.png` | A halted upgrade: replacement sleepers, ballast work, road plates, gantry parts and heavier construction staging. |
| `mine-refinery-transition-runoff-corridor.png` | Drainage and containment as the transition: runoff channels, sumps, low retaining structures and old pump equipment. |

Shared constraints: preserve the exact camera, cliff, mine shed, refinery
buildings, doors and railway route; keep the railway completely unobstructed;
retain a continuous 2.5–3 metre walking corridor and cross-connections to every
visible entrance; compress non-playable space with landform, retaining elements,
dead machinery and stacked bulk materials before the distant perimeter fence.
The refinery remains operational but neglected rather than pristine or ruined.
Wear follows water, traffic and maintenance. No teal, giant new building,
pipe-spaghetti, random trash carpet, blocked route, people, logos or copied game
assets.

Generation provenance: thread `01a0df7d-8228-7772-a0eb-10bd8070df17`; output IDs
`exec-9f9a7b41-1205-4db7-80e5-c8f749b8df7b`,
`exec-cd93e0c4-9092-46ac-bbb3-50583bb6bb9e`, and
`exec-be84ee0e-8eac-4d04-a84b-33167c5f1c2b`, respectively. Originals remain in
the generation output folder; the project copies above are the durable inputs.

### Valorant-style correction

The first three transition paintovers above were rejected as implementation
targets because their surface treatment drifted toward photoreal industrial
grunge: too much micro-noise, debris and cinematic weathering, with insufficient
graphic shape hierarchy. They are retained only as rejected design history.

The corrected `-valorant-v2` set keeps the three spatial ideas while enforcing
the project art direction: crisp silhouettes, chunky specific geometry, broad
hand-painted matte colour blocks, low-frequency gradients, restrained localized
wear and quiet surfaces between focal clusters.

| Corrected concept | Direction |
| --- | --- |
| `mine-refinery-transition-maintenance-frontier-valorant-v2.png` | General-purpose transition with the clearest dark-mine to warm-grey plant gradient and sparse maintenance clusters. |
| `mine-refinery-transition-failed-modernization-valorant-v2.png` | Interrupted upgrade language using replacement track components, retaining modules and one compact maintenance trolley. |
| `mine-refinery-transition-runoff-corridor-valorant-v2.png` | Drainage-led transition using a shallow segmented runoff spine, culvert covers and an obsolete pump housing. |

All three preserve a readable rail and pedestrian corridor and use large blocker
masses before the perimeter fence rather than treating the entire yard as
playable. They add no authority to change measured architecture or circulation.

Corrected generation output IDs: `exec-dfae2e6f-a2c2-44e2-ac2f-2e72bc1d5cf6`,
`exec-bf0dcba5-1a7f-44f8-a882-44b16343dd7d`, and
`exec-3955d08f-d247-463e-8ec3-d212ca4cc5a8`, respectively.

### Approved courtyard implementation reference — 2026-09-27

The owner approved `mine-refinery-transition-valorant-fidelity-v3.png` and then
commissioned only the courtyard/outside of the mine, with additional copies of
existing boulders along the fence on the mine's left. The finished Gullet Mine
is locked. The generated image is not permission to rebuild the mine, cliff,
or neighbouring refinery buildings. Their saved geometry and materials remain
authoritative.

The bounded implementation lives in `ART | Courtyard mine-to-refinery` in the
main `facility_environment.blend`, plus explicitly scoped local exterior ground
and track derivatives. Current actual CPU 1280×720 renders and verification are
under `runtime/out/environment/courtyard/`. Generated concept images and actual
Blender renders must not be confused. Independent review and fresh-process
checks refer to the saved scene hash in that folder's manifest.
