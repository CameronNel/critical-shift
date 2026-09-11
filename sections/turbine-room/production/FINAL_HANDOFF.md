# Turbine Room integration handoff — R07

Original complete local turbine/generator hall, authored by Astra and independently reviewed by Luna. Strict Valorant direction: broad architectural forms, ivory/charcoal/oxide orange and safety yellow, matte tactile surfaces, purposeful practical lighting; no teal. Independently accepted for the defined local room scope; repository receipt is recorded below.

## Deliverables

- `blender/turbine-room.blend`: complete saved room, 1,661 objects, 28 materials and 16 cameras. Open in its own Blender window; AI lease released.
- `architecture/floorplan.png` and `.svg`: dimensioned 14 × 24 × 7.2 m clear shell, machinery envelopes, service clearances, routes and connection IDs.
- `architecture/TAKEOVER_REQUIREMENTS.md`: explicit required-equipment/function checklist, design choices and engine responsibilities.
- `interface.json` and `architecture/CONNECTIONS.md`: exact local opening positions, dimensions, orientation and ownership; measured neighbour surveys and proposed placement transforms.
- `art/CONCEPT_PROVENANCE.json` and `art/concepts/`: ten original generated concepts, hashes, labelled prompt summaries, approved components and rejected history. Exact prompts remain in the task's generation calls.
- `production/renders/review/R07/`: ten fixed cameras C01–C10 and six player-height supplements W01–W06, 1440 × 900, 48 samples, HIP through shared GPU gate.
- `production/renders/review/cold-R07/`: independent reopened-artifact render batch; `production/validation/R07/cold-comparison.json` records all sixteen pixel comparisons.
- `production/critics/`, `CORRECTION_HISTORY.md`, `WALKTHROUGH.md`: honest independent reviews, rejected views and corrections.
- `production/validation/R07/`: fresh-process saved geometry audit, actual exhaust-aperture audit, two semantic snapshots, source-hash readback and live scene receipt.

Paths above are relative to `sections/turbine-room/`, except the short production document links which are in this directory. The final image set is also copied byte-for-byte to `production/renders/final/R07/` for convenient inspection.

## Saved artifact evidence

Blend SHA256: `4f6a1f0d3869933f4922f5d4012bc84671150f39270ebde938042ebaafc78f3f`.

Two independent fresh-process snapshots have identical evaluated scene fingerprint `04c0a25d777cab961b8a411aed6f73ae18f7afb2925912be1cfca5ca262f4606`. Geometry, materials, font text, cameras, lights and interface metadata are included. All nine source files recorded in the saved authoring manifest match their current bytes. The later aperture auditor is read-only.

All sixteen cold renders completed successfully. They are not pixel-identical: the largest channel difference is 1/255, maximum changed-pixel fraction 0.00018210 (0.01821%), and maximum mean RGBA channel difference 0.000045525/255. This numeric evidence is kept separate from Luna's visual acceptance.

R07 technical audit is PASS. U04 is a real 2.5 × 1.5 m opening through the hood, flange, foundation, grout and slab: fifteen evaluated downward rays are clear, with an adjacent solid-floor positive control. The preceding R06 lacked a proven opening and was held at 89 for coverage; that defect and its correction are retained honestly.

Topology retains REVIEW for intentional open cloth, paint/text and other surface geometry; hidden-geometry REVIEW retains the invisible U04 boolean operand as explicit construction intent. This is not a claim that every asset is a watertight solid. The live external-dependency tool flags `Bfont Regular` at `<builtin>` as missing; that is Blender's built-in font, not an external asset. Fresh-open renders show the lettering correctly. Materials use no external image textures or linked libraries.

## Integration boundaries

Local D01 is (0,0,0), outward −Y, 2.4 × 2.7 m. D02 is (0,24,0), outward +Y, same size, with owned reveal ending y25.2. U01 steam is (8.4,0,4.9), U02 condensate (9.5,0,0.45), U03 power (−4.32,25.2,3.88), U04 exhaust (4.6,11.45,0), downward. Use the contract's full marker names and dimensions during assembly.

Proposed Turbine placement in reactor coordinates is (−18.5,0,0), Rz +90°, with a reserved 4 m connector from reactor stub x−14.5. Reactor's existing closed doors remain reactor-owned. Proposed Electrical placement in Turbine coordinates is (0,25.45,0), Rz 0°, with a 0.25 m bus bridge. These are coherent proposals, not accepted whole-map transforms. Saved neighbour surveys distinguish measured geometry from unbuilt reciprocal utilities.

The underfloor condenser, remote steam supply, connector construction and reciprocal electrical completion remain unassigned/unassembled. The liquid return is intentionally blind pending condenser design. Fuel Corridor's shared plant portal is not claimed. Full casing extraction through the personnel doors is not supported; lifting and upper-casing maintenance remain inside under the monorail.

Routes were checked with saved geometry and player-height coverage, including approaches, crossovers, controls and service points. This is not an engine playtest, navmesh/collision certification, structural rating or live machinery simulation. Runtime speed/load/output, shared reserve, alarms, audio, incidents, repair and networking are mapped to handoff hooks for engine implementation.

## Reproduction and ownership

Original scene sources are `blender/build.py`, `hall.py`, `slice_detail.py`, `wear.py` and `final_adjustments.py`. Use the section-private Blender resources. `blender/run.ps1 -Phase full -Revision <new-revision> -Cameras '<comma-separated names>'` rebuilds from factory empty and uses the shared GPU gate. Rebuilding overwrites the owned saved scene; preserve any subsequent user edits first. `-Reopen` renders the existing saved artifact without rebuilding.

Only this section is committed. Other section changes, including an existing modified Cooling Plant blend, are preserved and excluded. Historical source/checkpoint evidence remains available; temporary resource profiles, render logs and Blender autosave backups are excluded.

## Final acceptance and repository receipt

Luna final review: `critics/luna-R07-final-review.md`. All categories independently approved: specification coverage 93, layout/flow 94, machinery 94, navigation/readability 93, construction 94, materials 92, lighting 92, reference fidelity 94. All sixteen warm and sixteen cold images directly inspected; visual stability approved. Numeric non-identity remains recorded honestly.

Delivery branch: `codex/turbine-room-takeover-20260911`, remote `https://github.com/CameronNel/critical-shift.git`. The artifact commit and verified push receipt will be appended after the repository operation. No merge to main.
