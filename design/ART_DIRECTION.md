# Art Direction

## Authority and Visual North Star

Critical Shift is a **highly stylised, low-detail 3D co-op game** built around simple readable forms, expressive physical characters, bold colour blocking, and hazardous industrial spaces.

**PEAK is the visual north star for the degree of stylisation, simplicity, readability, and character appeal.** Use the same broad design virtues rather than copying another game's protected designs. Critical Shift must not reproduce PEAK-specific scouts, outfits, faces, badges, props, locations, logos, textures, or other distinctive assets. The result should feel immediately at home beside that level of stylisation while remaining unmistakably Critical Shift.

This document is the final authority for all visual decisions. If any older repository text, concept image, filename, prototype, screenshot, generated asset, or subsystem specification asks for Sea of Thieves styling, painterly materials, grounded realism, believable anatomical realism, photorealism, realistic industrial rendering, or dense PBR detail, that visual instruction is obsolete. Preserve the underlying gameplay requirement, dimension, route, machine function, or interaction hook and restyle its presentation according to this document.

## Core Visual Thesis

The world should look **simple enough to read instantly and strong enough to be memorable in silhouette**.

Critical Shift should combine:

- Compact, expressive human workers.
- Simplified and slightly faceted geometry.
- Chunky industrial machinery with large visual masses.
- Bold, controlled colour blocks.
- Mostly texture-light materials.
- Clear functional silhouettes.
- Strong atmospheric lighting and fog.
- Big, readable physical interactions.
- Dark industrial danger without muddy visibility.
- Physical comedy created by animation, physics, scale, and panic.

The facility can be dangerous, oppressive, radioactive, wet, scorched, or failing without becoming visually realistic. Danger should come primarily from **composition, motion, lighting state, sound, scale, and readable damage states**, not layers of photographic grime.

## What “PEAK-Led” Means Here

Use these high-level qualities throughout the game:

- **Simple geometry:** large clean masses before detail; faceting is welcome when intentional.
- **Readable silhouettes:** a player, tool, machine, valve, cart, door, or hazard should remain identifiable from a distance and while moving.
- **Compact characters:** deliberately stylised proportions with simplified limbs and enlarged interaction features rather than realistic anatomy.
- **Soft graphic materials:** broad colour and value changes instead of texture noise.
- **Limited visual frequency:** avoid fields of tiny bolts, scratches, wires, seams, panels, labels, and surface breakup.
- **Playful shape language:** machinery may lean, taper, bulge, pinch, or exaggerate functional parts while remaining usable and industrial.
- **Strong colour separation:** player identity, departments, hazards, interactables, powered states, contamination, and emergencies should be readable through controlled colour families.
- **Lighting-led atmosphere:** fog, bloom, emissive equipment, directional pools of light, alarm states, and darkness establish mood.
- **Physics-friendly design:** silhouettes and collision volumes should support grabbing, carrying, ragdolling, climbing, dragging, throwing, and machine interaction.

Do not interpret this as a request to clone PEAK. The visual grammar is the reference; Critical Shift's industrial workplace, hazmat equipment, machine administration, uranium production chain, compliance systems, and reactor imagery provide the original design identity.

## Character Direction

Workers are stylised adult humans, but **adult identity comes from context, gear, posture, voice, and role rather than realistic anatomy**.

Target character qualities:

- Compact overall proportions, approximately in the broad 5.5–6.5-head-tall range rather than fashion-model anatomy.
- Slightly enlarged head/helmet volume for expression and instant recognition.
- Simplified torso and limb masses.
- Readable, somewhat oversized hands/gloves and boots because players grab, carry, climb, drag, and operate machinery constantly.
- Strong silhouette differences through helmets, hoods, packs, harnesses, tools, suit modules, and department equipment.
- Simple faces with restrained features where faces are visible.
- Minimal skin and fabric surface detail.
- Deformation and rigging designed for broad physical motion rather than anatomical subtlety.
- Ragdolls that remain readable as characters rather than collapsing into visually noisy anatomy.

Avoid:

- Realistic human anatomy as the visual target.
- Skin pores, realistic subsurface skin rendering, facial microdetail, realistic hair-strand rendering, or cloth weave.
- Hero-shooter muscle anatomy.
- Chibi/baby coding, toddler proportions, giant anime heads, or intentionally juvenile presentation.
- Mascot costumes or plush-toy materials.

A worker should read as a **small, brave, highly legible industrial person swallowed by machinery**, not a realistic simulation character.

## Hero Hazmat Suit Language

The protective suit is the signature character asset of Critical Shift and should carry the game's identity.

The base hero suit should use:

- One unmistakable helmet/hood and visor silhouette that remains readable in first person, third person, and ragdoll.
- A compact sealed body suit with broad uninterrupted colour areas.
- Chunky gloves and boots with simple protective shapes.
- A clear chest or waist closure/seal mechanism large enough to read during the suiting sequence.
- One strong back silhouette: telemetry/life-support/filter pack, small tanks, or a combined service module.
- A large physical rescue/grab handle integrated into the upper back or pack.
- A visible dosimeter/status module with simple emissive state colours.
- A small number of functional hoses/cables, kept thick and readable rather than realistic and numerous.
- Department/player identification through colour panels, tape bands, helmet/visor accents, badges, and replaceable modules.
- Separate visual states for unsealed, sealed, damaged, contaminated, low-integrity, and emergency conditions.

The suit should feel **purpose-built, slightly awkward, charming, and immediately iconic**. Do not bury it under realistic seams, stitch lines, MOLLE-style detail, tactical clutter, dense hard-surface panels, or military operator styling.

Room-specific concept and build prompts belong inside each section package under ../sections/<section>/prompt/.

## Environment Shape Language

Architecture should be simple, bold, and modular.

Preferred forms:

- Thick walls and doorframes.
- Broad floor and wall modules.
- Large pipes with simple elbows and clamps.
- Oversized valves, levers, switches, handles, wheels, and breaker shapes.
- Strong ceiling ribs, supports, tanks, ducts, hoppers, conveyors, carts, and machine housings.
- Intentional tapering or mild asymmetry where it helps character.
- Visible structural logic without engineering completeness.
- Large empty/rest areas between important visual clusters.

A room should generally read in this order:

1. Hero landmark or machine.
2. Main gameplay route.
3. Interaction points.
4. Hazard state.
5. Secondary supporting forms.
6. Sparse set dressing.

Do not fill negative space simply because a real facility would contain more hardware.

## Department Families

### Mine

The mine is rough in **shape**, not texture density.

Use:

- Large faceted rock masses.
- Chunky steel supports.
- Broad wet/dry colour changes.
- Thick rails, carts, cables, pumps, lamps, and explosive placements.
- Strong shadow and work-light pools.
- Readable cracks, collapses, flooding, and blast damage as large visual changes.

Avoid photogrammetric rock, realistic gravel fields, dense debris, and noisy rock normal maps.

### Refinery

The refinery is the most kinetic department.

Use:

- Big conveyors and rollers.
- Oversized crusher jaws/housings.
- Broad vats, pipes, chutes, batch containers, and processing drums.
- Strong motion and colour-state changes.
- Large spill shapes and contamination zones.
- Simplified mechanical logic that players can understand at a glance.

Avoid dense chemical-plant pipe spaghetti or tiny instrumentation everywhere.

### Reactor and Power Plant

The power plant is the largest, cleanest, most dramatic department.

Use:

- Monumental but simple machinery.
- Large clean architectural planes.
- A bright cyan reactor pool as a major colour/emissive landmark where required by the reactor spec.
- Two dominant control-bank assemblies in the reactor hall.
- Thick coolant routes.
- Large consoles and physical controls.
- Controlled off-white/grey/blue-green bases with clear state lighting.
- Emergency red/orange used selectively rather than permanently washing the room.

The reactor may preserve its 1990s industrial-science-fiction influence in **technology vocabulary** such as physical switches, CRT-like screens, analogue gauges, and chunky housings, but it must render those objects with the same simplified PEAK-led geometry and texture-light material treatment as the rest of the game.

## Materials and Textures

The game should not depend on painterly texture work or realistic PBR authoring.

Preferred material strategy:

- Broad base colours.
- Simple roughness/metalness families where the renderer needs them.
- Vertex colour or masks for controlled variation.
- Gentle gradients when useful.
- Sparse decals for essential labels, hazards, contamination, damage, and identifiers.
- Very limited edge wear applied as a graphic accent, not a physically simulated history.
- Simple transparent materials for visors, liquids, glass, steam, and contamination effects.
- Emission for power state, alarms, radiation, screens, and machine feedback.

Texture detail should survive at gameplay distance. If a detail disappears when the camera moves a few metres away, it is probably not worth authoring unless it serves a specific close interaction.

Avoid:

- Hand-painted Sea of Thieves-like brushwork.
- Painterly grime passes.
- Photographic textures.
- Photogrammetry.
- Realistic fabric weave.
- Tiny scratches across every asset.
- High-frequency normal maps.
- Dense edge wear.
- Unique 4K texture sets for ordinary props.
- “Realistic metal” as a default finishing goal.

## Colour

Colour should carry gameplay information and character appeal.

General principles:

- Give each major department a controlled identifying family.
- Keep structural/background colours comparatively restrained so characters, hazards, and interactables read clearly.
- Use saturated colour in purposeful blocks rather than confetti-like detail.
- Let player colours survive on suits and equipment without being swallowed by environment lighting.
- Reserve strong emergency colours for actual state changes.
- Use cyan/blue emission carefully around reactor systems so it stays special.
- Contamination needs a distinct readable presentation that does not rely solely on realism or subtle stains.

Colour must never be the only gameplay signal. Pair it with shape, animation, sound, labels, or light patterns.

## Lighting and Atmosphere

The game can be dark, eerie, and hazardous while remaining easy to navigate.

Use:

- Strong local light pools.
- Simple directional lighting.
- Volumetric or height fog where affordable.
- Emissive equipment and signage.
- Clear alarm-state transitions.
- Silhouette lighting around important machinery and players.
- Intentional darkness outside navigable/readable zones.
- Bloom in moderation for reactor, electrical, and emergency states.

Avoid solving atmosphere with muddy exposure, crushed blacks, permanent red alarm lighting, or realistic grime. The player should be able to understand the room before admiring it.

## Interaction Readability

Interactive objects should be intentionally exaggerated.

Examples:

- A valve wheel should have a strong shape and hand clearance.
- A breaker should visibly move between states.
- A safety guard should be large enough to understand before use.
- A machine input/output should have distinct silhouettes.
- A cart handle should be obvious from approach angles.
- A suit seal, grab handle, tool socket, or emergency control should not depend on tiny UI text.

When realism conflicts with interaction readability, readability wins.

## Damage, Wear, Contamination, and Failure

Damage must be **state-driven and graphic**, not a universal realism layer.

Prefer:

- Large scorch patches.
- Bent or displaced silhouette pieces.
- One broken panel hanging visibly.
- Strong cracks.
- Broad leaks and puddles.
- Steam jets.
- Pulsing lights.
- Changed emission.
- Clear contamination splashes/footprints.
- Large missing/broken machine elements.

Avoid covering every object with generic dirt and scratches. A clean machine becoming visibly damaged is more readable than a permanently filthy machine becoming slightly dirtier.

## Props and Clutter

Prop density should be low enough that gameplay objects remain obvious.

Each prop must earn its place by doing at least one of the following:

- Supports gameplay.
- Establishes scale.
- Identifies a department.
- Communicates state or story.
- Improves composition.
- Creates a physics/comedy opportunity.

Do not add filler merely to make a screenshot look “detailed.”

## UI, Labels, and Signage

Diegetic UI should follow the same large-shape principle:

- Big buttons.
- Chunky toggles.
- Large gauge needles.
- Short labels.
- Strong icons.
- Simple screen layouts.
- High contrast at interaction distance.

Typography and safety graphics should be original to Critical Shift. Do not mimic another game's UI or signage.

## Spawn/Start Room Visual Target

The spawn/start room is the cleanest introduction to the game's character style and must immediately establish the new direction.

- **Form language:** Simple, chunky, slightly faceted industrial forms with strong silhouettes and mild playful exaggeration.
- **Characters/PPE:** The hero hazmat suit and its modular PPE pieces are the dominant visual focus. Lockers should present large readable helmets, gloves, boots, packs, and suit pieces rather than realistic clothing clutter.
- **Materials:** Broad colour blocks and texture-light materials. No painterly Sea of Thieves treatment and no realistic fabric/metal surface pass.
- **Architecture:** Thick modular wall/floor panels, ribbed ceiling forms, bold industrial doors, large vents/pipes, and clear safety zones.
- **Lighting:** Welcoming enough to inspect equipment, with stronger contrast at the threshold into dangerous production spaces.
- **Clutter:** Minimal and purposeful.
- **Integration:** Geometry must remain export-ready with correct pivots, clean hierarchy, sensible colliders, and all gameplay hooks preserved.

## Reactor Hall Visual Target

The dimensional, route, and interaction constraints in [the reactor-room scenery specification](../sections/reactor-room/scenery/reactorroom.md) remain authoritative.

Its **surface treatment is subordinate to this document**. Preserve the reactor pool, two-control-bank concept, physical 1990s-style control vocabulary, functional positions, and required clearances, but interpret them with simplified low-poly/faceted geometry, broad colours, sparse material detail, large controls, and lighting-led atmosphere.

Where that specification uses terms such as brushed stainless, galvanised metal, realistic engineering detail, or material-specific finishing, treat them as functional/material identity cues rather than requests for realistic rendering.

## Concept-Art and AI-Generation Standard

Every generated concept should look achievable in the shipped game.

Prompts should request:

- Stylised 3D game concept/render.
- Simple/faceted low-to-mid-poly geometry.
- Strong silhouettes.
- Broad colour blocks.
- Minimal texture detail.
- Readable interactions.
- Clear gameplay-scale composition.
- Original Critical Shift industrial design.

Prompts should explicitly reject:

- Photorealism.
- Realistic cinematic rendering.
- Sea of Thieves painterly styling.
- Dense microdetail.
- Realistic military/tactical gear.
- Complex texture wear.
- Protected characters, logos, costumes, props, or locations from reference games.

When a reference screenshot from another game is supplied, analyse only high-level qualities such as silhouette, density, colour hierarchy, material simplicity, lighting, and proportion. Do not recreate its specific content.

## Production Target

This direction is intentionally suited to a small team with heavy AI assistance.

Prefer:

- Reusable modular kits.
- Simple meshes with deliberate silhouettes.
- Shared material families.
- Small material counts per asset.
- Sparse decals.
- Easy LOD generation.
- Clean pivots and hierarchy.
- Simple collision.
- Easily recoloured player/department variants.
- Assets that remain coherent even when generated or assembled by different agents.

A scene is finished when it is readable, atmospheric, cohesive, and fun to move through, not when every surface has received another detail pass.

## Prohibited Drift

Do not approve assets or concepts that drift toward:

- Sea of Thieves-inspired painterly art.
- Photorealism or grounded realism as the rendering target.
- AAA cinematic fidelity.
- Photogrammetry.
- Realistic skin, cloth, rock, rust, or metal microdetail.
- Dense greebling.
- Engineering spaghetti.
- Tactical/military operator aesthetics.
- Generic realistic sci-fi corridors.
- Dirty brown/grey visual noise everywhere.
- Massive prop density.
- Hyper-detailed hero assets surrounded by low-detail gameplay assets.
- Direct copies of PEAK or any other game's protected characters, outfits, props, environments, logos, or textures.

The desired result is **simple, bold, expressive, hazardous, readable, low-detail, physics-friendly, and unmistakably Critical Shift**.


---

# Autonomous Visual Validation Standard

All production environment sections must follow [AUTONOMOUS_SECTION_BUILD_PROTOCOL.md](AUTONOMOUS_SECTION_BUILD_PROTOCOL.md).

Visual quality is judged from fixed-camera rendered pixels, not from:
- scene-tree complexity;
- script output;
- asset counts;
- builder descriptions;
- a single flattering beauty render.

Formal reviews should use fresh-context specialist critics where tooling permits:
- spatial readability;
- stylized art direction;
- materials / anti-plastic;
- lighting / atmosphere;
- environmental storytelling;
- Blender technical quality.

For environment art, the default completion standard is:
- >=90/100 overall;
- >=85% of available points in every rubric category;
- zero critical failures;
- final two cycles materially stable;
- cold-start render PASS.

If a below-threshold scene gains less than one rubric point across two consecutive full cycles, stop adding decorative detail and perform a structural pass.

The art-direction goal remains simple: low-detail does not mean unfinished, and stylized does not mean plastic. Every major form must look intentionally authored.
