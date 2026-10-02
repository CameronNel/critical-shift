# Headless execution reference

This reference supplements the [existing production protocol](../../../../design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md).
It does not authorize replacing section scripts or rebuilding the map.
Run shell examples from the repository root after inspecting their inputs and outputs.

## Preflight only what the task needs

- Read current [MAP.md](../../../../MAP.md) and [MAP.json](../../../../MAP.json).
  For section-only work, also read the section's own toolchain and state.
- Locate the approved Blender executable and run `blender --version`. MAP.md
  currently specifies Blender 5.2 LTS; treat the live project requirement as the
  authority. Do not silently downgrade, upgrade or save through an incompatible
  version. This skill does not install Blender.
- Confirm disk/time/memory and image-inspection capabilities. Headless does not
  imply that a GPU, graphics context, network or vision tool is available.
- Hydrate only the required LFS assets. For current whole-map work use MAP.md's
  documented minimal pull list; do not invent a wildcard or omit indirect libraries.
  A Git LFS text pointer is not a usable `.blend` or image. No LFS pull is needed
  just to read or edit this skill.
- Resolve relative dependencies in their proper library context. Check linked
  libraries, image textures, fonts and external caches that the actual scene needs.
  Do not repack or rewrite frozen source records to conceal missing dependencies.
- Identify the existing section build/render/audit entrypoints and inspect them
  before execution. Historical rebuild scripts may overwrite historical caches or
  load obsolete sources. A filename alone is not proof of current compatibility.

## CLI patterns, not a new pipeline

Use a fresh process and make Python failures visible to the caller. Blender parses
arguments in order: load the intended file before executing a script against it,
and set `--python-exit-code` before the script. These are templates; replace the
uppercase placeholders with inspected, task-specific paths before running:

```sh
blender --background --disable-autoexec INPUT.blend   --python-exit-code 1 --python EXISTING_REVIEW_SCRIPT.py -- SCRIPT_ARGUMENTS
```

For an existing procedural builder that owns scene creation:

```sh
blender --background --factory-startup --disable-autoexec   --python-exit-code 1 --python EXISTING_BUILD_SCRIPT.py -- SCRIPT_ARGUMENTS
```

Do not open the whole map and then run a builder that clears the scene. Do not
change a section's documented argument contract to match these templates.
Disable embedded auto-execution by default. If a trusted project feature requires
registered handlers/drivers, inspect its documented initialization and dependencies;
record a scoped exception only when needed. Do not globally enable auto-execution.

Capture the actual exit code and log. With a shell pipeline such as `tee`, preserve
the Blender exit status (`set -o pipefail` in Bash). A printed completion message
or an old output file is not evidence that the current run succeeded.

Use a fresh, task-owned output directory or uniquely named iteration files. Record
the input/checkpoint, command, Blender version, camera, frame, renderer and settings
with each review batch. Never silently reuse stale renders after a failed run.
Do not clean unrelated directories, reset the working tree or delete old evidence.

## Preview strategy

Reuse the section's approved renderer and color management. Use cheaper previews
for exploration only, with fixed settings for before/after pairs. A diagnostic
preview with changed exposure, camera or engine is not an art-acceptance comparison.

A graphical backend may still be required by Eevee or Workbench even in background
mode. Verify availability rather than assuming `--background` removes that need.
If unavailable, a documented CPU Cycles preview may help diagnose geometry, but it
must be labeled as a different renderer and cannot certify the intended-engine look.
Do not silently alter committed scene settings or install a virtual desktop/MCP bridge.
Escalate render quality only after major defects are resolved and within the task budget.

## Existing map verification

The repository already provides
[verify_map_checkout.py](../../../../sections/facility-assembly/blender/verify_map_checkout.py).
Read it before use. It opens the authoring and inspection scenes, checks dependencies,
frozen source hashes and bundled preview controls, and writes the existing
`production/MAIN_CHECKOUT_VALIDATION.json` report beneath the map section.
It is not read-only: its report is overwritten. Run it only when applicable to a
hydrated map checkout, and inspect the resulting diff before committing evidence.

Its stated scope is **not** rendered art acceptance, gameplay collision, Unity
integration or FPS certification. Do not create a competing validator or claim
these other properties from its pass result. Room tasks still need their own
applicable geometry/support/interface checks. Preserve the current MAP.md promotion
procedure and immutable provenance when integrating a room.
