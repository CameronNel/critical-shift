# ChatGPT Work handoff — rebuild The Gullet Mine

## Repository coordinates

- Repository: `CameronNel/critical-shift`
- Working branch: `prototype/gullet-mine-work`
- Prototype entry point: `prototype/gullet-mine/index.html`
- Current V5 source fragments: `prototype/gullet-mine/source/v5-part-*.htmlpart`

The V5 source is split into four fragments only because it was uploaded through a connector with payload limits. `index.html` fetches and concatenates the fragments at runtime. **Your first cleanup step should be to consolidate/refactor this into a normal maintainable prototype structure**. You may replace all of V5 if that produces a better result.

## Read before editing

Follow the repository rules and read in this order:

1. `GAME_SPEC.md`
2. `docs/CANON.md`
3. `docs/ART_DIRECTION.md`
4. `AGENTS.md`
5. this handoff

Do not push to `main`. Continue work on `prototype/gullet-mine-work`. Use the existing draft PR for this task. Keep changes scoped to the mine prototype unless a tiny supporting repo change is truly necessary.

## Why this needs a rebuild

The user has rejected the previous visual passes. The recurring failures were not small polish issues. They were structural:

- ugly procedural/demo-like geometry
- floating or intersecting props
- cave forms that did not look authored
- random cones / primitive-looking spikes
- awful ore treatment
- weak or fake-looking lighting
- giant bloom/glow discs
- poor composition and route readability
- rails, supports and props not convincingly grounded
- random scatter used as a substitute for art direction
- collision either absent or visually disconnected from the level
- overall look reading as an AI-generated Three.js tech demo rather than a designed game space

Treat V5 as a disposable reference implementation, not a quality baseline.

## Goal

Rebuild this into a genuinely attractive, playable, stylised mine prototype for **Critical Shift / Friendslop** using Three.js.

The visual language should have the readability, exaggeration, crooked hand-built shapes, warm/cool lighting contrast and painterly broad-form confidence associated with stylised pirate-adventure environments, while staying within this repository's shippable low-to-mid fidelity art direction. Do not chase photorealism or AAA micro-detail.

A **smaller beautiful mine is better than a larger ugly mine**.

## Required level beats

You may redesign the exact layout, but preserve roughly this progression:

1. **Maw Camp** — entrance/staging area with strong first impression, rails, cart, supplies, rope, signs, lamps, believable working clutter.
2. **Crooked Rail** — narrowing rail tunnel with varied supports, embedded ore seams, occasional tools and a deliberate light/dark rhythm.
3. **Blackshaft** — major vertical-shaft landmark with a dangerous bridge, real depth cues, hoist/winch structure, ropes, broken platforms and eerie lights below.
4. **Drowned Pocket** — partially flooded chamber with damaged mining infrastructure, wet rock, water reflections and a believable walkway/route.
5. **Saint Glimmer** — the hero mineral discovery chamber. Valuable ore/mineral geology must look embedded in rock, mined around, and deliberately composed. No random neon gem forest.
6. **Powderworks** — blasting/work area with reinforced timber, powder storage, crates/barrels, drilling/blasting evidence and warmer dangerous light.
7. **Foreman's Vault** — reward/end chamber with ironwork, storage, valuables and strong environmental storytelling without visual noise.

## Non-negotiable visual rules

### Authored, not scattered

Do not use random scatter as the main detail-generation strategy. Every major prop needs a compositional or storytelling reason to exist.

Before keeping an object, ask:

- what is it doing here?
- what is supporting it?
- does its scale make sense?
- is it touching the floor/wall/beam correctly?
- does it improve navigation, composition or story?

If not, remove it.

### Cave geometry

Do not build the cave from hundreds of disconnected primitive boulders.

Use coherent cave surfaces with clear primary forms, secondary shelves/fractures and selective tertiary detail. Natural cave and mined/excavated areas should read differently.

Useful techniques include custom `BufferGeometry`, spline-based sections, authored mesh clusters, merged geometry and selective decals/material variation.

### Ore / minerals

Redo the ore completely if necessary.

Ore must look like geology, not pasted-on glowing primitives.

Use concepts such as:

- irregular branching veins through host rock
- mineral crust and matrix
- exposed seams partially covered by rock
- mining scars around valuable deposits
- embedded crystalline faces only where justified
- restrained emissive response

No cone ore. No floating gemstones. No generic octahedron wall stickers. No room-filling self-illumination.

### Timber construction

Timber should make structural sense:

- feet on the ground
- tops contacting ceiling/beam structure
- horizontal and diagonal bracing where plausible
- dimensions related to tunnel width
- repairs/damage that still read structurally

No floating beams and no meaningless intersections.

### Grounding

Use surface placement helpers, raycasts, known ground transforms or authored anchors so props reliably touch surfaces.

Audit all visible clusters for:

- floating
- sinking
- clipping
- mismatched scale
- rails not seated on sleepers
- sleepers not seated on terrain
- lamps/signs attached to nothing

### Lighting

The mine should be eerie **and readable on a phone**.

Use a limited number of important real lights plus cheaper emissive/fake-light treatments for secondary fixtures. Warm lantern pools should reveal nearby rock, timber and props. Use subtle cool ambient/bounce between warm areas. Keep fog and bloom restrained.

Do not solve darkness by globally nuking exposure.

Do not use huge glow sprites that become orange circles.

### Collision

Collision is mandatory and must be manually tested.

Use a capsule player against simplified static collision proxies. The player must collide sensibly with:

- cave walls
- floor
- bridge/platforms
- supports where appropriate
- large props
- gates/major blockers

Avoid colliding against every decorative detail. The player should not snag constantly.

Blackshaft must be a genuine fall hazard.

## Controls to preserve

- WASD desktop movement
- mouse look
- sprint
- jump
- hand lantern
- mobile joystick movement
- mobile drag look
- mobile jump / lantern controls

A debug fly/ghost mode may remain behind a debug toggle.

## Performance target

Target a modern Android phone. Prefer broad art direction and strong composition over brute-force detail.

Use sensible approaches such as:

- merged static geometry
- instancing for truly repeated pieces
- limited shadow-casting lights
- modest shadow maps
- restrained post-processing
- cheap secondary light cards/emissive fixtures
- reasonable pixel ratio on mobile

Do not trade the entire framerate for tiny visual detail.

## Mandatory browser-driven visual QA

**Do not judge success from code. Render the game and look at it.**

Use ChatGPT Work's browser/visual capabilities throughout the task.

Required loop:

1. run the prototype through a local HTTP dev server
2. open it in the browser
3. test desktop view
4. test approximately **706×1536** mobile viewport
5. walk/fly to the next QA viewpoint
6. capture a screenshot
7. visually inspect the screenshot
8. write down what looks wrong
9. fix it
10. rerun and recapture

Repeat until the screenshots themselves are convincing.

### Required screenshot checkpoints

Capture and inspect at minimum:

1. Maw Camp entrance looking into the mine
2. Crooked Rail
3. first reveal of Blackshaft
4. standing on the Blackshaft bridge
5. Drowned Pocket
6. entrance/reveal of Saint Glimmer
7. close/medium view of the hero mineral deposit
8. Powderworks
9. Foreman's Vault
10. normal mobile gameplay HUD at ~706×1536

For every checkpoint ask:

- Is anything floating?
- Is anything clipping or intersecting nonsensically?
- Is the route legible?
- Is there a clear focal point?
- Does lighting reveal the materials?
- Does the space have primary/secondary/tertiary visual hierarchy?
- Does it look deliberately authored?
- Are there obvious primitive/debug shapes?
- Does it look good at actual gameplay camera height?
- Would I be comfortable showing this screenshot to the user as evidence of quality?

If the last answer is no, keep working.

## Manual gameplay QA

Do not only fly the camera. Walk the collision route with normal controls.

Test at minimum:

- entrance to end chamber traversal
- bridge crossing
- jumping near supports/props
- walking into cave walls at angles
- navigating narrow rail sections
- Drowned Pocket route
- Powderworks clutter
- vault gate/blockers
- deliberate fall into Blackshaft and respawn/recovery
- mobile controls at the mobile viewport

Fix any obvious sticking, tunnelling, falling-through or invisible-wall issues.

## Refactoring

The current prototype is a split legacy upload. Refactor it early into something maintainable. A reasonable shape would be:

```text
prototype/gullet-mine/
  index.html
  src/
    main.js
    world/
      cave.js
      zones.js
      props.js
      ore.js
      lighting.js
      collision.js
    player/
      controller.js
    materials/
      materials.js
```

This is a suggestion, not a requirement. Do not spend hours refactoring while the screenshots still look bad.

## Completion bar

Do not call the task done until:

- the prototype actually runs
- you personally inspected browser screenshots
- desktop and mobile were both checked
- the complete route was manually traversed with collision enabled
- there are no obvious floating objects in the QA shots
- the cave no longer reads as random primitive geometry
- ore/mineral formations look authored and embedded
- Blackshaft reads as a strong landmark and actual hazard
- lighting is eerie but readable
- the environment has coherent visual hierarchy
- the level no longer looks like a throwaway Three.js tech demo

At completion, update the PR with:

- screenshots for all required QA checkpoints
- a concise summary of the rebuild
- exact viewports/browsers tested
- approximate observed performance
- collision tests performed
- any remaining known visual or collision issues

Follow the repository's PR/merge rules in `AGENTS.md`. Do not claim visual QA you did not actually perform.
