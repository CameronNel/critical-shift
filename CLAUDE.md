# CLAUDE.md

Guidance for Claude Code working in this repository.

[`AGENTS.md`](AGENTS.md) is the authority on working rules for every agent,
including this one. Read it first, then [`GAME_SPEC.md`](GAME_SPEC.md),
[`docs/CANON.md`](docs/CANON.md) and
[`docs/ART_DIRECTION.md`](docs/ART_DIRECTION.md). Where this file and the
specification disagree, the specification wins.

## Pull requests

- **Merge your own pull requests.** Once checks are green, mark the pull
  request ready and merge it. Do not wait for a human review, and do not leave
  finished work sitting open for someone else to land.
- Open a pull request for every change. Never push directly to `main` — the
  branch and the pull request stay; only the wait for approval is gone.
- Do not merge past red checks, unaddressed review comments, or a decision
  that is genuinely the owner's to make (visibility, paid resources,
  infrastructure that affects other projects). Say what is blocking and leave
  the pull request open.
- Keep a pull request to one bounded change. If a second concern appears
  mid-branch, land the first and start again.

## Prototypes

`prototype/threejs-facility/` is the Three.js facility greybox: a level-design
and layout-review tool, not game code, and removable by deleting that
directory. Its layout reasoning, scale rules and known simplifications are in
[`prototype/threejs-facility/DESIGN_NOTES.md`](prototype/threejs-facility/DESIGN_NOTES.md).

Before reporting a layout change as done, run `npm run validate` and
`npm run check` in that directory. The validator catches the failures that are
invisible from inside the building — stairs too steep to climb, doorways that
have slipped off the end of their wall.
