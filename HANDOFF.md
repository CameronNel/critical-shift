# Handoff note

Written at the end of a session that ran out of disk space. Read this first, then follow the entry rules in `AGENTS.md`.

## Start here

1. Read `AGENTS.md`, then `MAP.md` and `MAP.json`. They describe the current assembled map. Do not start from an older standalone room branch or the historical A04 master.
2. Run `git lfs pull` before opening any Blender files.
3. Start the new task branch from the head of PR #96, not from this branch.

## Planned work (hall fixes, not started)

- Darker wet concrete.
- Moodier lighting.
- Baked wall numbers.
- A 1.2 million triangle limit.

None of this has been done. Nothing in the repo was changed for it.

## Disk warning

The old container hit 100% disk. The causes were scratch renders, old copies of the scene and a large download, on top of 12 GB of LFS objects in `.git/lfs`.

- Keep scratch renders small and delete them as you go.
- Use a sparse checkout of only the sections the hall work needs.
- Check `df -h /` before starting a render.

## State of the old checkout

- Branch: `claude/reactor-control-room-1990`.
- Sparse checkout was switched on by a failed setup command. It shows only `.agents`, `design/blender-headless` and `sections/reactor-room`. It hides files from view and deletes nothing from git.
- About 835 files showed as modified. I believe this is LFS and sparse-checkout bookkeeping, not real edits, but I did not check every file.
- I restored 11 files under `sections/facility-assembly` that the full disk had changed.
- Do not commit or push the modified-file noise.

## Not verified

- The contents of PR #96 and any other open PRs.
- Whether the 835 modified files are all bookkeeping.
- No render, check or test was run for the hall fixes.
