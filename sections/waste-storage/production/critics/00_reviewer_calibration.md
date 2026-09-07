# Waste Storage independent reviewer calibration

Reviewer identity: `/root/astra_reviewer`, independent agent assigned by `/root` on 2026-09-08. This identity is the agent task identifier, not an assertion about model routing.

Authorized write scope: `sections/waste-storage/production/critics/` only. No geometry authoring, render modification, or GPU work.

Status: references inspected; no Waste Storage render has yet been supplied or scored. This file is not an acceptance.

## Authority read

- `C:/Users/Camer/Games/critical-shift/ops/facility-run/BUILD_BRIEF.md`
- `C:/Users/Camer/Games/critical-shift/ops/facility-run/briefs/waste-storage.md`
- `C:/Users/Camer/Games/critical-shift/ops/facility-run/README.md`
- Current `design/ART_DIRECTION.md`, `ART_REFERENCE_INDEX.md`, and full `AUTONOMOUS_SECTION_BUILD_PROTOCOL.md` in the reactor-valorant worktree.
- Relevant `GAME_SPEC.md` requirements for waste, contamination/radiation, cart/body transport, compliance inspection and modular routes. The current facility brief overrides legacy mine-lift wording.

The assignment is stricter than the default production protocol: scale/circulation, shape/art direction, hierarchy, materials, lighting, color, environmental storytelling, and technical correctness must each reach 90/100. The threshold is not a scoring target or reason to inflate scores.

## Approved reference pixels inspected

Both images were opened through `view_image` and visibly inspected, not judged from filenames.

1. `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/sections/reactor-room/art/reference/generated/reference-a02-hall.png`
   - SHA-256: `9F7F553AF85EDB34BC131079F4FD2E2BC432DA69CFDEF123E3E3F081CA413CBB`
   - Visible baseline: quiet broad warm wall planes; subdued teal machines; dark structural frames; warm local light cones; distinct open floor routes; metal rim highlights; restrained localized wear; specific supports and door reveals; density concentrated around functional machines.
2. `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/sections/reactor-room/art/reference/generated/reference-b01-controls.png`
   - SHA-256: `8D34340D857361714E4F44F49CBFC4B811A03C1B4F53B86D8B15537F34FC2D49`
   - Visible baseline: tactile painted metal distinct from unpainted rods and stone-like floor; readable mechanical controls; contact shadows; restrained yellow and red accents; broad imperfect material variation; dark doorway depth; forms readable without relying on text.

These are rendering and construction-quality references. The reactor pool, layout, and control-bank arrangement are not Waste Storage requirements.

## Review method and evidence limits

- Inspect every supplied fixed-camera image at each formal cycle. Record actual file, revision, camera and observed visual defects.
- Describe defects and their practical impact. Do not supply coordinates, replacement shapes, or modeling recipes; the builder owns design decisions.
- Score visible quality from pixels. Source claims and object counts do not raise visual scores.
- Treat route dimensions, hidden support contact, missing dependencies, pivot sanity, and cold-start behavior as technical evidence questions. Images alone cannot establish those facts.
- The style slice is an expansion gate; a partial view cannot prove the whole room.
- Require at least four genuine complete correction/review cycles after the first complete version, every one of ten fixed cameras, stable final two cycles, objective validation, and fresh-process cold reopen/render comparison.
- Inadequate or missing evidence remains unverified, not a pass. Effort and deadline do not earn acceptance.
