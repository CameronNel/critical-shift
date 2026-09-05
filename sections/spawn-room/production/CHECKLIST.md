# Spawn Room — Production Checklist

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


## Headless reproducibility
- [ ] documented Blender CLI entrypoint exists
- [ ] scene can build/open from fresh process
- [ ] no MCP-only dependency
- [ ] authoritative .blend saved in ../blender/
- [ ] build scripts retained if required

## Objective layout
- [ ] briefing room left
- [ ] locker room right
- [ ] operational exit forward
- [ ] exactly four primary suit stations
- [ ] two suit stations left
- [ ] two suit stations right
- [ ] integrity chamber central
- [ ] Geiger station directly associated with exit
- [ ] hallway/doors/circulation pass clearance checks

## Support-contact validation
- [ ] CS_SUPPORT_REQUIRED collection exists
- [ ] all support-dependent wall/floor/ceiling dressing is registered
- [ ] all registered props identify an exact support target
- [ ] all registered props define a support direction
- [ ] irregular props use explicit support anchors where needed
- [ ] validate_contacts.py returns PASS
- [ ] no wall-mounted prop exceeds 5 mm gap
- [ ] no registered prop exceeds 2 mm penetration
- [ ] support orientation checks pass
- [ ] contact_validation.json exists and contains zero failures

## Visual quality
- [ ] no final-greybox read
- [ ] no generic web-demo read
- [ ] no dominant plastic/default-PBR response
- [ ] strong stylized silhouettes
- [ ] materials visibly differentiated
- [ ] lighting hierarchy clear
- [ ] room implies larger building
- [ ] required portraits/papers/art/plants/chairs/rubble/tile variation present
- [ ] clutter supports, rather than obscures, gameplay

## Review protocol
- [ ] fixed cameras established
- [ ] at least four full review cycles completed
- [ ] fresh-context specialist critics used where available
- [ ] same-camera regression comparison recorded
- [ ] stagnation rule respected
- [ ] final overall score >= 90
- [ ] every category meets floor
- [ ] zero critical failures
- [ ] final two cycles materially stable

## Cold start
- [ ] active Blender process closed
- [ ] fresh process launched
- [ ] dependencies verified
- [ ] objective checks rerun
- [ ] contact validation rerun from fresh process
- [ ] final cameras rerendered
- [ ] cold-start images match approved quality
- [ ] TASK_STATE.md marked PASS


## Grounded semi-realism style gate

Before any full-room rebuild:
- [ ] validation slice only, not whole room
- [ ] believable door and wall thickness
- [ ] one locker/PPE station with specific construction
- [ ] one bench/furniture asset with believable proportions
- [ ] 3–5 storytelling props with plausible placement
- [ ] no repeated bevelled-box language
- [ ] no generic sci-fi control panels
- [ ] no uniform satin-plastic material response
- [ ] PPE reads as fabric/clothing, not polygon mannequin
- [ ] signage reduced to functional necessities
- [ ] no random plant used as filler
- [ ] localized lighting creates depth and contact
- [ ] quiet surfaces remain between focal clusters
- [ ] all support-contact validation passes
- [ ] generated Spawn Room reference plates reviewed
- [ ] style slice scores 8/10+ with no visual veto
