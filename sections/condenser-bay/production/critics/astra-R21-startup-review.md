# Turbine Condenser Bay — R21 startup qualitative review

**Reviewer identity:** independent Luna (gpt-5.6-luna) critic subagent
**Revision:** R21 (startup calibration; no numeric scores issued)
**Scope:** Turbine Condenser Bay authored module and its documented U04/U02/local cooling boundaries only. Scene/source files were not modified.

## Evidence inspected

- Warm review set: `renders/review/R21/C01_ENTRY.png` through `C10_MATERIALS.png` and `W01_ENTRY_CORNER.png` through `W08_GALLERY_TURN.png`, opened at 1920×1080.
- Historical cold set: matching 18 images under `renders/review/cold-R21/`, opened across the full set. Warm/cold hashes differ for all 18 pairs; all files are 1920×1080. The old package does not prove separate-process cold-open provenance, so cold-process validation remains unverified until a new audited render.
- `RUBRIC.md`, `CONTINUE_GROK.md`, `grok-R19-full-review.md`, `grok-R20-full-review.md`, `R21-validation.json` and reviewer identity record.
- Canonical `ART_DIRECTION.md` and `ART_REFERENCE_INDEX.md`.
- Neighbor/reference pixels: turbine R07 `C02_hero.png`, cooling final `C05_PUMP_A.png`, reactor `reference-a05-user-edited-orange.png`.

The R21 scene has a readable ivory/charcoal/oxide industrial family, a distinct condenser silhouette, and visibly improved stairs, operator rotaries, and the SE hall compared with R19. These positives are calibration observations only. The binding rule requires a fresh complete warm+cold set and every category strictly above 90; no R21 score is issued at startup.

## Three most consequential visible defects

1. **C04_EXHAUST.png · upper centre exhaust/hood view · blocker ·** The frame is dominated by a close underside of the corrugated hood and a bright diagonal pipe; the required U04 receive, continuous flange/gasket, and slab landing are not visible. **Consequence:** the mandatory exhaust contract cannot be verified from the supplied exhaust view, and the view does not prove the condenser receives the turbine opening.

2. **C05_RETURN.png and C03_REVERSE.png · condensate return riser and level equipment · blocker ·** The condensate drop visibly terminates at a grey collar/ring rather than a readable closed nozzle/return line, while the level tubes read as opaque rods. **Consequence:** the steam-to-condensate process and U02 return story remain visually incomplete; the level indication is not legible as glass instrumentation.

3. **C06_COOLING.png · overhead cooling-water run · major ·** Multiple circular hanger/saddle pieces visibly float at the ends of thin vertical rods without a clear pipe or structure landing. **Consequence:** the required supported supply/return routing reads as disconnected decorative hardware, lowering machinery logic, construction/detail, and fidelity.

## Other observed defects

- **W01_ENTRY_CORNER.png · connector alcove · major ·** A blank recess carries only `UNBOUND CONNECTOR`; no visible socket, flange, or threshold establishes the boundary. This leaves the local interface unverified.
- **C09_ROOF.png and W08_GALLERY_TURN.png · roof/upper gallery · major ·** The roof opening/hood edge forms a repetitive jagged zigzag and the gallery view contains visibly unfinished or unsupported railing/hoist pieces. The roof is not yet a convincing slab/service system.
- **W03_NW.png · west aisle · major ·** Large black pipe and posts dominate the player path and occlude equipment; the aisle reads as cramped and obstructed in the supplied view.
- **W04_NE.png and W07_EAST_PULL.png · floor keep-clear zones · minute/major clustered ·** Oversized amber floor fields consume the views; `3.5 m BUNDLE KEEP CLEAR` is inverted in W04, and W07 shows a broad empty marked area with a small orange termination. This reads as debug-like overlay rather than restrained diegetic marking.
- **C01_ENTRY.png · entry framing · major ·** Camera is too close to the condenser and door edge; the first volume and complete receiving threshold are only partially readable.
- **C07_OPERATOR.png · operator board · major ·** Labels and gauges are readable, but the board is a largely flat repeated gauge/rotary panel with little secondary housing or service context compared with the turbine and cooling reference pixels.
- **C08_MAINT.png · maintenance platform · major ·** The view exposes a dense stack of rails/grates and narrow clearances; removal access and support landings are not convincingly demonstrated.
- **C10_MATERIALS.png · motor/coupling close crop · minute/major ·** Bolt rings, cage and motor fins are present and readable, but the orange/cream surfaces remain very uniform and smooth compared with the tactile, selectively varied neighbor references.

## Missing or unverified evidence

- Separate-process cold reopen with PID/manifest evidence for this R21 package.
- Full U04 slab opening, gasket/bolt ring, jamb and support in an honest view.
- Closed condensate nozzle and readable routed handoff toward the documented U02 story.
- Level glasses as glass, including edge/thickness/readable fluid state.
- Cooling hanger/saddle landings and deliberate local termination/supports.
- Roof slab/service construction and complete gallery standing turn.
- Numerical access/maintenance clearances from reconciled measured geometry, beyond pixels.

## Review status

R21 is a qualitative startup calibration only. I will score only a new R22+ pack after inspecting every new warm and cold image in the complete 18-view set, with the ten categories independently assessed and no scores copied from R19/R20. The current evidence does not support a pass.

**REJECT — startup evidence is incomplete; no numeric score issued.**
