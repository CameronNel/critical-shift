# Facility expansion coordination

User direction, 7 September 2026: create independent Astra chats through the ChatGPT desktop UI, each with its own reviewer, to build useful unfinished facility areas before 03:00 SAST on 8 September. Do not create facility-builder subagents inside the reactor conversation. The mistaken spawn/refinery/cooling subagents were interrupted before any delivered result and must remain stopped.

## Existing work: preserve

- Spawn/preparation: worktrees/spawn-reference-rebuild, branch codex/spawn-reference-rebuild, commit17cbff1; additional user work in the original checkout. Do not rebuild this area.
- Refinery: worktrees/refinery-compact, branch codex/refinery-compact-20260907, commite5820a6. Do not rebuild this area.
- Mine: existing Gullet source and evidence on its branches; preserve the shallow descent, never invent a mine lift.
- Reactor: worktrees/reactor-valorant, branch codex/reactor-valorant-20260907; active parent build. Do not edit it.

## New chat assignments

Separate, original section packages: cooling plant; turbine room; electrical room; waste storage; medical and reanimation; compliance dock; fuel corridor and service connections. The connector builder documents topology and shared interfaces. Each builder owns only its section and creates its own independent reviewer.

Read design/ART_DIRECTION.md and design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md from the reactor worktree, and design/GAME_SPEC.md plus relevant existing section interfaces. Architecture is metric and human scale. Where dimensions are unspecified, record an explicit implementation decision. Modular local origin: main doorway threshold at (0,0,0), +Y points into the section, +Z up. Record entry widths/heights and all additional portals in section-local interface.json. Do not move completed sections.

## Isolation and shared GPU

Use an isolated worktree and section-local private BLENDER_USER_RESOURCES. Never open or manipulate another chat's live Blender process. Authoring and CPU validation are independent. All HIP/GPU render commands must run through this shared gate:

    C:/Users/Camer/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe C:/Users/Camer/Games/critical-shift/ops/facility-run/gpu_gate.py --owner SECTION -- "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background ...

The gate serializes render jobs and releases on process exit. Exit75 means the queue wait expired; continue source/review work and retry later. Use a few low-sample preview cameras while refining, then a complete final batch. Never kill another worker to acquire GPU access.

Write concise progress to ops/facility-run/status/SECTION.md in this original checkout, with your chat id, worktree, branch, source, current render revision, reviewer id, unresolved defects and next action. No external human messages. Commit only your section; push its branch and hand off. No automatic main merge and no fictional acceptance scores. Exact proof and honest limitations accompany the result.
