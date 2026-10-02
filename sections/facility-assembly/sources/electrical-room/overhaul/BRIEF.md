# Electrical room overhaul

Owner palette correction, 2 October 2026: the previous accepted review does not
approve its pale color palette. The owner finds the room too light, washed out
and bland, and requests gunmetal, wet concrete, dark accents, functional safety
colors, rough surfaces and selective wear. This direction supersedes the earlier
pale material choices. Keep the constructed assets and strict Spawn fidelity
reference, with readable controls/routes and localized work lighting. Dampness is
localized to mineral surfaces near walls; the protected central epoxy route stays
dry. No blanket glossy film, noise-only finish or dark exposure trick.

Owner request, 2 October 2026. Rework the existing `../module.blend`, which is the
portable electrical source for the main map. The current map bakes its old
interior into a local preview cache; a direct-link integration candidate is
prepared separately for the map owner. Preserve the shell, origin, floor,
portals, utilities, interactive anchors and protected 2.4 m central aisle.
The owner's direct request authorizes the module edit; the main map and immutable
accepted source remain unchanged. Baseline is recoverable from base commit
`75983b9`, Git LFS and the retained baseline survey/renders.

Use the reworked spawn room as the 100-point pixel reference. Grounded stylized
semi-realism: assembled forms, actual cavities, distinct tactile materials,
functional light hierarchy, localized wear and evidence of work. No sterile
showroom, arbitrary debris, primitive assets, flat textures or uniform plastic.

Pessimistic independent reviewer: gpt-6-luna, high effort. Every category must
exceed 98/100; no compensating strengths or reduced standards. Record disagreements
with exact pixel/geometry evidence; a builder override of an individual false
positive cannot alter an independent score. Four full cycles minimum and stable
final two cycles, then cold-start validation.

## Twenty ideas for the build

1. Recessed cabinet compression seals.
2. Folded steel enclosure frames and separate door returns.
3. Slatted ventilation with thickness and clear cavities.
4. Exposed drawout breaker contacts and racking mechanism.
5. Ribbed ceramic insulators.
6. Braided protective earth straps.
7. Transformer winding bands and cooling spacers.
8. Bolted lifting eyes.
9. Cable glands and strain relief.
10. Sagging service leads with real end connections.
11. Wall-connected conduit clamps.
12. Contact wear at frequently used handles.
13. One mismatched replacement cabinet panel.
14. Padlocks on a seated lockout station.
15. Tagged repair trolley with castor construction.
16. Multimeter, range selector and probe leads.
17. Spare cartridge fuses in a service cradle.
18. Folded insulating gloves at the repair bench.
19. Stained enamel mug, hollow rim and handle.
20. Curled shift paperwork on a clipboard.

## Toolchain

Repository MAP.md requires Blender 5.2 LTS. Its authoring CI pins 5.2.1 and
Python 3.11. Official Blender 5.2.1 Linux archive was installed in
`/workspace/toolchains/blender-5.2.1-linux-x64` after SHA-256 verification against
the official checksum file. Build hash `9e2066aef7ef`; embedded Python 3.13.13.
Standalone Python 3.11.16 is installed in
`/workspace/toolchains/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11`.
The preinstalled Blender 4.3.2 is not used for authoring or saved-file validation.
Use one CPU Blender worker in this cloud environment; four render threads, no GPU.

## Evidence cameras

Preserve the fourteen saved C01–C10 and W01–W04 camera transforms and lenses.
The capture script writes source hashes, camera matrices and settings. Baseline
captures are made before modification. Style slice is the repair-bench wall bay;
expansion waits for an actual visual review of that slice.
