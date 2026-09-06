# Spawn personal-locker and inhabited-room revision — 6 September 2026

The latest direct user request removes displayed suits, keeps hangers and shoes with personal belongings, adds wooden briefing-room flooring and a carpet, and adds wall sockets. The user also authorized the previously proposed small workplace details. This supersedes the four displayed suit stations in earlier scenery documents; the previously corrected open entrances, airlock, TV, two briefing benches and rear glass/metal pod remain.

## Implemented dressing

- Four personal lockers: twelve wooden/wire hangers, retained work boots, folded cotton, two short work jackets, two canvas bags, thermoses and a personal crew photograph. Sheet-metal half doors have varied opening angles, louvers, pulls, labels and localized paint wear.
- Briefing: staggered timber boards with real joints and a shallow metal transition; a faded woven rug with bound edges, a mildly curled corner and a little fraying. Existing benches receive textured timber and sit on the rug. A booklet, remote, mug, whiteboard, wall speaker, routed cables and paused training diagram establish its use.
- Hall: shift clock, delivery note, hanging jacket and lunch bag by the bench, compact mop/bucket station, dated paint repair and sockets. The airlock gains an integrated pressure gauge, guarded amber indicator and worn floor boundary.
- Locker room: towel and hook, canvas laundry hamper, spare boots beneath a changing bench, a bracketed supply shelf with filters and glove cartons, pod service hose and wall inspection clipboard.
- Six sockets distributed across the hallway and both rooms.

Materials reuse the packed CC0 Poly Haven textures already licensed and documented in `../assets/textures/TACTILE_SOURCES.md`. The briefing floor uses the worn timber image maps with per-board UV offsets and restrained colour variation. New painted metal uses metric coordinates, roughness variation and shallow surface texture. Cloth uses broad folds, uneven fibre detail, matte roughness and subdued sheen. No paid assets, new external models or unlicensed images were added. The existing generated crew artwork is reused as a personal photograph.

The editable output is `../blender/spawnroom_inhabited_walk.blend`; `inhabit_spawn.py` builds it from the preserved corrected base. Old sources remain available. All maps remain packed. The new source does not need startup script execution. Scene-lit Material Preview and the previous filtered, jittered shadow correction remain enabled.

## Review trail

Pass 01 exposed shelf-contact gaps, misleading support anchors on stacked cloth, overly smooth rug shading and streaked locker paint. Pass 02 corrected contacts and paint, exposed periodic fabric moire, and established that all 129 registered contacts and 170 entrance rays pass. Pass 03 replaces the periodic pattern with irregular fibre shading, applies timber to bench backs, gathers the hanging towel, adds carton labels/tape and breaks up the airlock paint boundary. Pass 04 flattens the jacket bodies into hanging cloth with broader folds and finishes the remaining locker cabinets in the same metric painted metal.

Final evidence is packaged in `renders/final/inhabited/`: 17 objective checks pass, 129 support contacts pass, and 180 combined doorway/main-route rays are clear. Eighteen renders repeat after a fresh-process reopen with at most one 8-bit channel-level difference; greatest per-image mean difference is 0.000738. Source SHA256: `88d17ded84f51691628af1b9337f458dbe198834ee650a21b2f10858a0f3ac47`. The saved source also opened in the user's existing desktop Blender and passed live material/viewport inspections.

Clock-hand and amber-indicator keyframes are present as Blender animation. Ambient sound and game interactions are not implemented by this art pass. The delivered scene is editable authoring art; engine collision, optimized exports and audio remain integration work. Visual acceptance belongs to the user; no claim of perfection is implied by the geometry checks.
