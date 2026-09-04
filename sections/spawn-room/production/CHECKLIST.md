# Spawn Room — Production Checklist

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
