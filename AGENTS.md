# AGENTS.md

## Read Order

1. `GAME_SPEC.md`
2. `docs/CANON.md`
3. `docs/ART_DIRECTION.md`
4. Relevant architecture and subsystem documents once they exist
5. The issue or task assigned to you

For **visual, character, environment, material, lighting, concept-art, and asset-generation decisions**, `docs/ART_DIRECTION.md` is the final authority. If older text, screenshots, prototypes, filenames, comments, or specifications conflict with it, follow `docs/ART_DIRECTION.md` and treat the conflicting visual direction as obsolete. Gameplay rules, dimensions, routes, and interaction requirements remain authoritative unless the task explicitly changes them.

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

- **PEAK is the visual north star for level of stylisation and readability.** Translate its high-level strengths into Critical Shift's own industrial identity: simple/faceted geometry, compact expressive characters, exaggerated readable silhouettes, bold colour blocking, restrained surface detail, and strong lighting.
- This is a direction reference, not permission to copy another game's IP. Never reproduce PEAK-specific scouts, costumes, props, badges, logos, environments, textures, or distinctive asset designs. Critical Shift must remain recognisably its own game.
- Character proportions should be deliberately stylised rather than anatomically realistic: compact body masses, simplified limbs, readable hands/boots, and strong gear silhouettes. Characters must still read as adult workers through scale, posture, voice, equipment, and context.
- Prefer low-poly or low-to-mid-poly forms with intentional faceting and clean large shapes. Silhouette and motion matter more than small geometry.
- Prefer broad, mostly texture-light materials and colour blocks. Use material response, gradients, vertex colour, simple masks, and sparse decals before adding texture noise.
- Do not generate or approve photorealism, grounded realism, AAA-cinematic realism, photogrammetry, realistic fabric/skin microdetail, dense PBR wear, or small-scale greebling.
- Do not use Sea of Thieves-inspired painterly distortion, brushy texture language, nautical exaggeration, or painterly grime as a target.
- Keep industrial machinery chunky, legible, and slightly exaggerated. Controls, handles, valves, hazards, doors, and pickup objects must read immediately at gameplay distance.
- Use lighting, fog, emission, scale, motion, colour contrast, and sound to create danger and atmosphere. Do not rely on realistic dirt, rust, scratches, or material complexity to make a scene feel finished.
- Concept art and AI-generated references must depict a feasible shippable target using the same simplified geometry/material language expected in game.
- Preserve clear gameplay routes and interaction readability over environmental clutter.
- Reuse modular assets intentionally. Repetition should feel like coherent machine-admin standardisation, not something hidden under extra detail.
- When updating an older area, convert its **surface style** to this direction without silently changing gameplay dimensions, routes, machine functions, interaction hooks, or canonical setting.
