# GROK TASK — CRITICAL SHIFT SCENE RESCUE + REWORK

## HARD RULE 1 — SYNC FIRST, READ FIRST, TOUCH NOTHING FIRST

Before changing any file, use MCP and do the following in order:

1. Inspect the repo state.
2. Pull the latest changes safely.
3. Read the core specs.
4. Inspect the current scene/art files.
5. Produce a short implementation plan.
6. Only then begin edits.

Use MCP tools heavily. You have full permission to use them.

---

## REQUIRED FIRST STEPS

### A. Sync and protect work
Use MCP terminal / filesystem tools and do the following:

1. Run `git status`
2. Run `git branch --show-current`
3. Create a safety branch before rescue work if helpful, for example:
   - `git switch -c rescue/grok-scene-fix`
4. If there are uncommitted changes, do not lose them blindly.
   - Stash or commit them safely if needed.
5. Run:
   - `git fetch --all --prune`
   - `git pull --rebase`
6. Inspect recent scene-related history and diffs so you understand what Gemini changed.

Prioritize inspection of changes involving:
- `Assets/Scenes/GrokShiftMap.unity`
- `art/blender/grok-shift-unity-source.blend`
- `GrokShiftEnvironment.fbx` or equivalent exported FBX/environment assets
- stylized shader/material files
- hazmat suit assets
- locker art / signage / UI-like 2D inserts
- any prefabs used by the scene

### B. Read the specs before editing
Read at minimum:

- `AGENTS.md`
- `GAME_SPEC.md`
- `docs/CANON.md`
- `docs/ART_DIRECTION.md`

If present and relevant, also read:
- `docs/REACTOR_ROOM_VISUAL_SPEC.md`
- any room-specific visual spec
- any art-concept docs for hazmat suits / spawn / arrival / lockers / mine / hallway / reactor

Do not begin implementation before reading those files.

### C. After reading
Provide a concise implementation plan before major edits:
- What is broken
- What must be reverted / removed
- What must be remodeled / repainted / relit
- What external licensed assets (if any) you want to use
- What 2D assets you will generate with Imagine
- What files you expect to modify

---

# PRIMARY MISSION

Rescue and rework the current Critical Shift scene into a polished, coherent, gameplay-safe stylized environment.

This is a rescue pass first, quality art pass second.

The goal is to:
1. Undo bad scene decisions and structural visual mistakes.
2. Restore clarity and playability.
3. Improve the art quality substantially.
4. Preserve gameplay layout and intended function.
5. Use the repo’s current art direction as the authority.
6. Produce a visually cohesive, polished result.

PEAK may only be used as a **high-level** north star for:
- simplicity
- readability
- broad shapes
- stylization
- low texture noise
- strong lighting hierarchy
- restrained detail

Do **not** copy PEAK assets, locations, characters, props, or distinctive designs.

---

# KNOWN CURRENT PROBLEMS TO FIX

These are explicit current issues:

1. **Blocked doors**
   - Doors that should be traversable/usable must no longer be blocked.
   - Restore intended movement and access.

2. **Useless new landing zone / mini-sitkamer in the hallway opposite the door to the mine**
   - Remove the pointless added space/landing/lounge-like insert if it is not called for by the spec.
   - Restore the hall to a purposeful, readable, gameplay-valid form.

3. **Double and floating highway walls**
   - Remove duplicated, floating, offset, or visually broken wall layers.
   - Highway / hallway architecture must be clean, intentional, and structurally believable within the stylized look.

4. **Plants, chairs, etc. look terrible / toddler-modeled**
   - Replace, remodel, or remove low-quality props.
   - Props must either:
     - be much better quality and fit the style, or
     - be omitted if unnecessary.

5. **Hero hazmat suits look bad**
   - Rework the hero hazmat suits so they feel like a signature asset.
   - Improve proportions, silhouette, material treatment, visor, gloves, boots, backpack/life-support unit, suit readability, and overall polish.
   - They must fit Critical Shift’s stylized art direction.

6. **Locker pictures look bad**
   - Replace bad locker imagery / inserts with cleaner, higher-quality visual assets.
   - Use generated 2D art if appropriate and present them properly in-world.

---

# HARD RULE 2 — PRESERVE GAMEPLAY, DO NOT WRECK THE LAYOUT

The scene is not a blank canvas.

Do not arbitrarily redesign gameplay-critical structure.

Do not casually change:
- intended routes
- access flow
- traversal widths
- meaningful door placements
- stair function
- gameplay-critical interactions
- machine logic
- station relationships
- scene purpose

If something visual is ugly but functionally correct, improve it **without** breaking the underlying gameplay purpose.

If something is both ugly and structurally unnecessary (like the useless hallway sitting area), remove or correct it.

Think:
- rescue first
- polish second
- no unnecessary chaos

---

# BLENDER + UNITY WORKFLOW

The environment exists in both:
- Blender source:
  - `art/blender/grok-shift-unity-source.blend`
- Unity scene:
  - `Assets/Scenes/GrokShiftMap.unity`

Treat Blender as the source for geometry/authored environment work where appropriate, and Unity as the place where the full playable scene, materials, lighting, collisions, scripts, and staging are validated.

## Expected workflow
1. Inspect Unity scene as it currently is.
2. Inspect Blender source scene.
3. Determine whether broken geometry lives in Blender source, Unity scene setup, or both.
4. Fix geometry in the proper source.
5. Re-export / reconnect as needed.
6. Re-validate inside Unity.
7. Ensure materials, colliders, and scene references still behave correctly.

Do not leave Blender and Unity out of sync if you change geometry.

---

# MATERIALS, TEXTURES, AND ASSET QUALITY

## Materials
Use the project’s stylized material system and art direction.
Keep materials:
- stylized
- broad in value/color
- low-noise
- coherent
- readable
- suitable for the current scene

Avoid:
- photoreal scan-heavy realism
- noisy materials
- sloppy placeholder surfacing
- muddy flatness
- random clashing prop materials

## External assets
You may use external assets, but only if they are:
- free
- clearly licensed for use
- legally safe / clearly reusable
- stylistically compatible
- worth using

Good sources are the kind that clearly state license/usage rights (for example CC0/public domain or clearly usable free assets).

Do **not** use assets with missing, unclear, or no visible license.

If an asset is low-quality, over-detailed, or style-breaking, do not use it.

## Generated 2D assets with Imagine
You are encouraged to use Imagine for certain assets where 2D inserts make sense.

Examples:
- clipboard face graphics
- locker photos / pinned notes / worker portraits
- warning posters
- training posters
- ID cards
- inspection sheets
- hazard signage
- wall notices
- equipment labels
- small framed or pinned imagery

### Important placement rule
If you generate a flat image asset, do not leave it as floating nonsense.
Mount it correctly on a thin physical support when appropriate.

Examples:
- a clipboard image should be placed on a thin clipboard/board
- a printed notice should be placed on a thin backing sheet / paper plane
- a sign should sit on a thin plate / panel
- a small poster should be placed on a wall surface or thin card
- a locker photo should be a thin printed sheet or pinned card

In other words:
**generate the image, then place it on a simple thin physical mesh so it exists believably in the world.**

---

# HERO HAZMAT SUITS — QUALITY REQUIREMENTS

The hero hazmat suits are important and currently poor.
Rework them carefully.

Desired traits:
- compact, readable silhouette
- strong stylized proportions
- appealing oversized helmet/visor
- clean suit segmentation
- good glove and boot shapes
- visible but simple life-support or utility pack
- one or two clear accent details instead of clutter
- good color blocking
- attractive materials
- polished front/readable 3/4 view
- strong identity for Critical Shift

Avoid:
- ugly lumpy forms
- messy hoses everywhere
- random clutter
- weak silhouette
- bland mannequin result
- overly realistic military/tactical direction
- low-quality placeholder look

If needed, rework both model presentation and material presentation.

---

# LOCKERS / WALL ART / SMALL VISUAL STORY ASSETS

The locker imagery currently looks bad.

Upgrade these using a clean stylized approach.
Possible additions:
- worker snapshots
- tiny printed reminders
- hazard cheat sheets
- laminated procedures
- suit-up instructions
- pinned notes
- shift checklists
- cartoonishly bureaucratic warning slips
- equipment issue tags
- “do not forget your dosimeter” style notices

All of this should still fit the Critical Shift tone and visual style.

Keep them:
- readable
- restrained
- funny/characterful only where appropriate
- visually crisp
- not over-cluttered

---

# PROPS — FIX BAD ONES, DON’T FILL SPACE WITH TRASH

Bad props should be:
- replaced
- improved
- simplified
- or removed

Plants, chairs, and similar secondary dressing assets must not look amateurish.

Use one of these approaches:
1. Find clearly licensed free assets that fit the style.
2. Modify/retexture them to fit the style.
3. Model simple stylized replacements in Blender.
4. Remove props that do not add value.

Do not fill the scene with clutter just to make it look “detailed.”

Every prop should help one of:
- function
- atmosphere
- hierarchy
- story
- spatial readability

---

# LIGHTING PASS

After structural cleanup and core material sanity are restored, perform a real lighting pass.

Lighting should:
- create atmosphere
- improve readability
- separate focal areas from background
- make large forms feel intentional
- avoid flat “everything evenly lit” ugliness

Use:
- strong key/fill relationships
- readable pools of light
- practical fixtures
- modest atmospheric depth
- darker recesses where safe
- emphasis on important paths / doors / stations / hero elements

Avoid:
- full-scene bland brightness
- random colored disco lights
- crushed darkness that hurts gameplay
- extreme bloom
- ugly flat editor-looking lighting

---

# SPECIFIC EXECUTION PRIORITY

Do the work in this order:

## Phase 1 — Audit and rescue
- Pull latest
- Read specs
- Inspect diffs/history
- Identify exactly what Gemini broke
- Make a short rescue plan

## Phase 2 — Remove regressions
Fix:
- blocked doors
- useless added hallway room/landing zone
- double/floating walls
- obviously broken scene composition
- broken / ugly / placeholder props

## Phase 3 — Restore scene integrity
- Ensure scene structure is coherent
- Ensure Blender/Unity source relationship is sane
- Re-export / reconnect environment if needed
- Clean up obvious broken staging

## Phase 4 — Asset quality upgrades
- better chairs / plants / props
- better hero hazmat suits
- better locker imagery
- better small wall/notice assets
- use Imagine where appropriate for 2D inserts mounted on thin meshes

## Phase 5 — Material and polish pass
- harmonize materials
- improve texture presentation
- ensure stylized consistency
- improve signage, boards, clipboards, posters, inserts

## Phase 6 — Lighting and final art pass
- proper lighting
- atmospheric polish
- readability check
- visual hierarchy check

## Phase 7 — Validation
- inspect the scene in Unity
- ensure obvious movement/access is not broken
- ensure doors are usable/readable
- ensure no floating/double geometry remains
- ensure the scene no longer looks hacked together
- summarize all changes clearly

---

# WHAT GOOD LOOKS LIKE

At the end, the scene should:
- feel intentional
- be cleaner than before
- be more readable
- preserve gameplay function
- no longer contain the stupid hallway lounge / sitkamer
- no longer have blocked doors
- no longer have floating / doubled walls
- no longer contain embarrassingly bad chairs/plants/etc.
- have much better hero hazmat suits
- have much better locker visuals
- have stronger overall polish and lighting

The result should look like a properly art-directed stylized environment, not an AI accident.

---

# OUTPUT EXPECTATIONS

Before major edits, provide:
1. short audit summary
2. short action plan
3. list of files expected to change

After edits, provide:
1. summary of what was fixed
2. summary of what was removed
3. summary of what external licensed assets were used
4. summary of what was generated with Imagine
5. summary of any Blender→Unity re-export flow performed
6. list of changed files
7. validation notes / known caveats if any

---

# HARD RULE 3 — USE MCP

Use the MCP tools actively.
Do not work “blind.”

Use MCP to:
- inspect files
- inspect git state
- inspect diffs
- inspect scene-relevant assets
- inspect generated files
- inspect license/source notes for external assets where needed
- perform the actual rescue work safely and deliberately

You have full permissions. Use them.
