# AGENTS.md

## Read Order

1. `GAME_SPEC.md`
2. `docs/CANON.md`
3. `docs/ART_DIRECTION.md`
4. Relevant architecture and subsystem documents once they exist
5. The issue or task assigned to you

## Global Rules

- Work on one bounded task at a time.
- Do not edit `GAME_SPEC.md` unless explicitly instructed.
- Do not introduce a new package, framework, or architectural pattern without approval.
- Multiplayer is host-authoritative.
- Clients submit intentions, not outcomes.
- Every multiplayer change requires a deterministic or automated multiplayer test.
- Every machine requires a standalone test scene.
- Merge your own pull requests. Open one for every change, drive it to green,
  then merge it yourself rather than leaving finished work waiting for a human.
- Never push directly to `main`. Everything still goes through a branch and a
  pull request; the merge is the part you no longer wait for.
- Do not merge past red checks, unresolved review comments, or a decision that
  is genuinely the owner's to make. Say so and leave the pull request open.
- Do not modify unrelated files.
- Run relevant validation before reporting completion.
- Report missing assets, unclear requirements, and unverified assumptions.
- Prefer reversible, modular changes.
- Keep player-facing causality readable.
- Preserve the production, safety, and compliance design triangle.

## Art Direction Guardrails

- Character art must use stylised adult human proportions; avoid childlike anatomy, mascot faces, stubby limbs, and toy-like presentation.
- The game targets low-to-mid visual fidelity suitable for a solo developer with AI assistance.
- Do not generate or approve photorealistic, AAA-cinematic, photogrammetry-heavy, or micro-detailed environment art.
- Prefer modular kits, shared materials, trim sheets, decals, repeated machine structures, broad forms, and strong lighting.
- Concept art must represent a plausibly shippable visual target, not an expensive aspirational version.
- Preserve clear gameplay routes and interaction readability over environmental clutter.
- Reuse assets intentionally and expose that reuse through coherent industrial design rather than hiding it with unnecessary detail.
