# Worktree and Blender isolation evidence

Read-only inspection at task start found:

- Original checkout: `C:/Users/Camer/Games/critical-shift`, branch `codex/spawn-room-peak-fresh`, with four modified tracked Spawn production documents and numerous unrelated untracked files.
- Occupied worktree: `worktrees/spawn-reference-rebuild`, branch `codex/spawn-reference-rebuild`.
- Interactive Blender PID 75876, started 2026-09-06 23:40:40 +02:00.
- Spawn background renderer PID 27036, started 2026-09-07 00:05:02 +02:00, running `run_valorant_readability.py` on `spawnroom_valorant_walk.blend`.

The refinery task never claimed a Blender MCP instance, sent UI commands, closed/killed/restarted either process, saved an occupied `.blend`, stashed changes, or ran checkout/reset/restore/clean/pull/rebase. The Spawn background renderer subsequently disappeared while the original interactive PID remained; no termination command was issued by this task.

`git fetch origin` updated remote refs without changing working files. A new branch/worktree was created at `origin/main` commit `97bb68c`:

`C:/Users/Camer/Games/critical-shift/worktrees/refinery-compact`

`codex/refinery-compact-20260907`

All authoring mutations are confined to the new worktree's `sections/refinery/` package. Source from the mine and Spawn sections was read or copied into that package, never edited. The cart geometry snapshot makes the build independent of the occupied worktree.

Blender builds use fresh background processes, six CPU threads, `--disable-autoexec`, and factory startup. The wrapper also assigns a private `BLENDER_USER_RESOURCES` directory. The first unwrapped diagnostic launch reported an extension-cache write failure in Blender's normal profile; the wrapper was added to isolate subsequent profile writes. No interactive document state was accessed.

The physical-interface audit uses a separate two-thread background process and private profile, opens only a refinery-owned diagnostic file and never saves it.

This records the actions performed and process observations; it does not claim that another active task stopped changing its own files during this work.

On the user's stop request, only the refinery-owned PID 85376 was stopped after executable/start-time verification. No other Blender process was targeted. The previously observed GUI PID was no longer present at the final read-only process check; this task did not terminate it.
