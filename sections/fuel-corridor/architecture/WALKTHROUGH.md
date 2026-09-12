# Fuel Corridor walkthrough — 11 September 2026

Scope: the live Fuel Corridor scene, its measured shape, doorway inventory and player wayfinding. This is a scoped correction to full04; it is not final acceptance of the paused complete art/build programme.

## Layout and connection inventory

The irregular floor envelope is **22.40 × 24.00 m**. It contains a freight route with two main turns and a parallel service bypass, rather than a single rectangular room. Fourteen floor meshes match the P07 plan. The freight centreline is 38.20 m; the service bypass is 23.40 m. Main freight corridor gross width is 4.40 m; the western service leg retains its 2.00 m dressed route inside a 2.40 m gross width. The northern bypass is 3.00 m gross.

| Visible code | Connection | Section seam centre, metres | Clear opening W × H |
|---|---|---|---|
| F01 | Refinery / fuel assembly | (0, 0, 0) | 2.60 × 3.00 m |
| F02 | Reactor | (14.2, 24, 0) | 5.00 × 5.00 m |
| S01 | Shared plant services | (-5.4, 17.4, 0) | 2.00 × 2.50 m |
| S02 | Clean / medical / compliance | (6.6, 21, 0) | 2.00 × 2.50 m |
| S03 | Waste | (16.4, 16, 0) | 2.40 × 3.00 m |
| FG01 | Internal freight gate | (6.35, 10, 0) | 3.40 × 3.40 m |

There are **five external connection doors and one internal freight gate: six assemblies, twelve sliding leaves**. Boundary doors are presented closed; the internal gate is open. The bypass is an open internal route, not a sixth external connection. These are connection counts, not certified emergency-exit counts.

The assignment and GAME_SPEC chapter 23 require freight circulation, a service bypass, measured interfaces and a coherent facility route. They do not mandate a numeric door count or a rectangular footprint. Shared plant and clean headers serve several future destinations; their downstream rooms and runtime door controllers are not proven by this local scene. Full travel time through assembled neighbouring rooms remains unverified.

## Corrections

- Replaced eight ambiguous or clipped wall labels with supported 1.65 × 1.10 m panels. Steel spacers span the existing structural posts; new panels remain in the wall margins. No floor, seam or doorway geometry was extended or moved.
- Destination codes now match the plan: F01/F02, S01/S02/S03 and FG01. Door headers, access hatches, leaf identities and left/right serials use the same codes.
- All large route titles and primary door identities use a 0.245 m font setting. Large route codes use 0.400 m; route subtitles use 0.105 m. Header and advance signs use 0.115 m. Secondary equipment inscriptions retain their smaller functional hierarchy. Long text was given adequate backing rather than individually shrunk.
- Shifted labels clear of door pulls and a service-air union. Moved a hidden tool-case tag to the visible side of its own case.
- Tool cases have unique TK-01/TK-02/TK-03 IDs; electrical enclosures have E-01/E-02/E-03 IDs. BAY A denotes the staging bay. AR-07 remains the repeated regulator model designation; gauge numerals remain pressure graduations, not destination numbers.
- Strengthened the plant advance cue to S01 / PLANT and the clean blade to S02 / CLEAN. Moved the clean panel clear of its light in the oblique approach view.

## Verification and evidence

The saved-file comparison covers **809 original floor/door mesh objects**, with no missing or changed meshes. All 32 panel mounting feet find existing wall or post support. A CPU-only replay reproduces all 135 text objects' content, sizes and world transforms from the preserved live state.

The evaluated glyph/arrow audit covers **143 objects**: no glyph is unbacked and no opaque geometry blocks it along its face normal. The only reported intersection is the first-aid lettering behind its transparent lid. This audit is complemented by actual viewport walkthroughs at 1.70 m eye height; it does not establish legibility from every possible position or certify final game lighting.

Evidence lives in `production/evidence/walkthrough/`: `saved-geometry-verification.json`, `replay-verification.json`, `wayfinding-walk02.json`, and walking-height PNGs. The first `clean.png` frames the door closely and crops its adjacent sign at the image edge; `clean_approach_final.png` shows the complete panel on approach. The revised plant cue is in `service_advance_final.png`.

Independent review is by **Luna**, per the user's cost preference. Initial walk01 readability scored 88 and was corrected. Final scores are size/hierarchy **93**, shape/integration **92**, door compliance **94**, destination semantics **96**, player-height readability **92**, and backing/construction **93**. See `production/critics/luna-walkthrough-final.md`. This approves only the scoped walkthrough/signage correction. Astra's earlier completed report is historical evidence only.

The original dirty live state was preserved as `production/checkpoints/walkthrough/live-before.blend`; the corrected review copy is `corrected.blend`. Base full04 source provenance is retained separately from the wayfinding patch hash. No neighbour section was edited and no GPU render was started for this walkthrough.
