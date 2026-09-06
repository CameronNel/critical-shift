# Spawn Room — Production Checklist

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.


## Headless reproducibility
- [x] documented Blender CLI entrypoint exists
- [x] scene can build/open from fresh process
- [x] no MCP-only dependency
- [x] authoritative .blend saved in ../blender/
- [x] build scripts retained if required

## Objective layout
- [x] briefing room left
- [x] locker room right
- [x] operational exit forward
- [x] exactly four primary suit stations
- [x] two suit stations left
- [x] two suit stations right
- [x] integrity chamber central
- [x] Geiger station directly associated with exit
- [x] hallway/doors/circulation pass clearance checks

## Support-contact validation
- [x] CS_SUPPORT_REQUIRED collection exists
- [x] all support-dependent wall/floor/ceiling dressing is registered
- [x] all registered props identify an exact support target
- [x] all registered props define a support direction
- [x] irregular props use explicit support anchors where needed
- [x] validate_contacts.py returns PASS
- [x] no wall-mounted prop exceeds 5 mm gap
- [x] no registered prop exceeds 2 mm penetration
- [x] support orientation checks pass
- [x] contact_validation.json exists and contains zero failures

## Visual quality
- [x] no final-greybox read
- [x] no generic web-demo read
- [x] no dominant plastic/default-PBR response
- [x] strong stylized silhouettes
- [x] materials visibly differentiated
- [x] lighting hierarchy clear
- [x] room implies larger building
- [x] required portraits, papers, furniture and tile variation present; zero plants and no rubble filler under the current art direction
- [x] clutter supports, rather than obscures, gameplay

## Review protocol
- [x] fixed cameras established
- [x] at least four full review cycles completed
- [x] review provenance recorded: builder self-review only; delegated critics were not authorized in this session
- [x] same-camera regression comparison recorded
- [x] stagnation rule respected
- [x] final overall score >= 90
- [x] every category meets floor
- [x] zero critical failures
- [x] final two cycles materially stable

## Cold start
- [x] active Blender process closed
- [x] fresh process launched
- [x] dependencies verified
- [x] objective checks rerun
- [x] contact validation rerun from fresh process
- [x] final cameras rerendered
- [x] cold-start images match approved quality
- [x] TASK_STATE.md marked PASS


## Grounded semi-realism style gate

Before any full-room rebuild:
- [x] validation slice only, not whole room
- [x] believable door and wall thickness
- [x] one locker/PPE station with specific construction
- [x] one bench/furniture asset with believable proportions
- [x] 3–5 storytelling props with plausible placement
- [x] no repeated bevelled-box language
- [x] no generic sci-fi control panels
- [x] no uniform satin-plastic material response
- [x] PPE reads as fabric/clothing, not polygon mannequin
- [x] signage reduced to functional necessities
- [x] no random plant used as filler
- [x] localized lighting creates depth and contact
- [x] quiet surfaces remain between focal clusters
- [x] all support-contact validation passes
- [x] generated Spawn Room reference plates reviewed
- [x] style slice scores 8/10+ with no visual veto


## Reference-preload evidence

- [x] `REFERENCE_REVIEW.md` exists and is updated for this build
- [x] all numbered Spawn reference plates were inspected
- [x] five extracted visual rules are recorded
- [x] three explicit failure modes are recorded
- [x] chosen scale anchors are recorded
- [x] validation-slice composition is recorded before modelling

Validation completed 2026-09-06. Evidence: renders/final/, cold_start_comparison.json, stability_comparison.json, RUBRIC.md and critics/. Visual checklist entries are builder judgments; measured entries are backed by the source/contact reports. Active build processes exited before the separate cold-start process launched. Runtime integration is outside this Blender art checklist.

## Maintained-wear revision validation

- [x] Six CC0 downloads and published checksums recorded.
- [x] Packed texture bytes verified after opening the saved source.
- [x] Three slice iterations and documented full-room corrections completed.
- [x] All eleven fixed views and two detail views reviewed.
- [x] All eleven mandatory views rerendered from a saved scene in fresh processes.
- [x] Full-camera comparison inspected with no material regression.
- [x] 83 contacts and 29 objective checks pass without relaxed tolerances.
- [x] Ten saved viewport spaces start in SOLID.
- [x] Unexpected old-scene resave preserved; unchanged source rebuilt and protected copy verified again.
- [x] Current gallery, source hashes and render provenance updated.

See critics/worn-surface-review.md and TASK_STATE.md for the exact scope of current and historical evidence.
