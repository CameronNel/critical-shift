# Electrical room overhaul — October 2026

The current editable source is [../module.blend](../module.blend), promoted on
`codex/electrical-room-overhaul-20261002` from the reviewed R9 checkpoint. Use the
current facility map and its selected portable modules; the older standalone E05
handoff and placement proposals are historical. The room remains 11.0 ×16.4 ×4.8m
with a 2.8 ×4.4 ×3.6m reserve bay.

## Inspect the current work

The [overhaul package](../overhaul/TASK_STATE.md) contains the fixed-camera renders,
independent critiques, correction ledger, build scripts and hash-bound checks.
Ten full review cycles are complete. R9 and the separate fresh pessimistic Luna
R10 review score99 in all seven categories against
reworked spawn=100 after the door/material work, rejection of weak floor patches,
and final cable, glass-transmission and reserve-service lighting corrections.
The current source is byte-identical to the reviewed R9 checkpoint. R10 saved-source
validation, native checkout, bounded link audit and five actual-map captures pass.
All fourteen unchanged-source decoded RGB views match exactly. Three assembled
views match exactly; two differ in a few channel values by one8-bit step, recorded
and independently judged visually immaterial. Final R9/R10 stability and fresh
cold visual acceptance are complete; see critics/R9.md and critics/R10-FRESH.md
in the overhaul package. The source-hash-bound floor close-up resolves the fresh
reviewer's remaining finish question without a scene change. Supplemental six
details and optical pair are explicitly reused at identical source bytes.

The assembled render/link handoff is
[facility_electrical_overhaul_candidate.blend](../../../blender/facility_electrical_overhaul_candidate.blend),
prepared beside the canonical map to preserve relative library paths. Its
`EI_C01_Entry`, `EI_C03_Reverse`, `EI_C04_Route`, `EI_W01_Turbine_Return` and
`EI_W02_Waste_Approach` cameras show the room at its actual map placement. The
canonical `facility_environment.blend` and immutable R17 cache are not replaced.

The overhaul rebuilds the repair bench and service tools, reserve cartridge
cases, trolley and meter, transformer winding/cooling details, grounded runner
storage and door vision openings. Folded enclosure frames, seals, glands,
earth straps, fixings, returned wall panels, rescue equipment, supported papers
and localized wear provide construction and use history. Procedural materials
separate paint, steel, copper, ceramic, rubber, fabric, paper, concrete and glass.
The maintained room has working clutter and replacement history, while retaining
its protected central circulation.

The final lead storage has distinct retained multi-turn windings, insulated ends
and returned hooks. Trolley cables curve smoothly into the meter and ribbed probes.
Nine mounted service strips illuminate the reserve compartments. Wired panes
retain the grid and diffuse reflection while transmitting a recognizable large
form in the matched optical pair; their fully parked positions face solid wall
returns, so room crops naturally show low-contrast concrete behind the glazing.

## Established map placement and interfaces

Use local metres, +Y inward from D01 and +Z up. The actual
`LAYOUT_A12.json` electrical placement is translation **(66,27,0)** with
**Rz180°**. Earlier Turbine/Waste origin proposals in E05 documents are superseded
by this assembled-map placement; do not reposition neighbors from those proposals.

D01 at localY0 and D02 at localY16.4 remain 2.4 ×2.7m. The internal P03 opening
at X5.5,Y13.2 remains 2.4m alongY and 3.2m high. Utility markers remain
U01(−4.32,−0.25,3.88), U02(−4.32,16.65,3.88), U03(8.55,14,2.8). Keep the
2.4m central aisle, original shell/floor and existing interactive anchors.
[interface.json](interface.json) records the original local interface contract.

Saved-source validation records318 baseline geometry/camera checks, including104
explicitly retired decorative door-wear marks and214 other protected checks.
Eight leaf/
vision-trim remodels preserve exact outer bounds and transforms; the12 inherited
vision wires move only7mm in pane depth and remain fully embedded. Fourteen
inherited camera transforms and focal lengths are unchanged. All59 registered
support assemblies and direct trolley-item support checks pass. Static0.60m
body-envelope checks pass303 positions across five routes. These sampled checks
do not certify exhaustive physics, carrying, animated guards or engine navmesh.

## Integration ownership and source compatibility

The canonical map currently displays an old baked electrical interior. The
candidate retires that interior cache and adds a relative linked instance of the
current `MODULE_electrical-room`, using the established pose. Neighbor transforms,
source-library bytes and exterior cache are preserved. All26 original electrical
material IDs requested by the main map are retained, including11 unused baseline
definitions needed for old cache compatibility.

Only the map owner adopts this candidate into `facility_environment.blend`,
refreshes an owned electrical preview cache if needed, and registers the new
instance with the existing overview/focus/material-review controls. The candidate
is validated for saved links and renders; those authoring-control modes have not
been verified. Preserve the whole checkout when opening it. Use Blender Save As
with relative-path remapping if the owner chooses a different candidate directory.
Never overwrite R17 or copy a deep-directory candidate blindly over the main map.

Frozen `accepted.blend`, `SOURCES.json` and `MASTER_MANIFEST.json` provenance are
unchanged. The promoted live-module hash belongs in
[the promotion receipt](../overhaul/promotion-receipt.json), not frozen-input hash
fields. The base map has128 missing linked spawn-wrapper IDs. Candidate audits
compare their exact identities against the pre-promotion snapshot; fixing those
unrelated inherited IDs is separate map-owner work. Do not report a clean
whole-map dependency acceptance from a native checkout check alone.

## Rebuild, verification and runtime handoff

[COMMANDS.md](../overhaul/COMMANDS.md) documents the baseline-based headless rebuild,
validation, capture, compatibility repair and strict cold comparison. Use the
retained baseline, not an already overhauled file. Rebuild to a new output path.
The installed toolchain is official checksum-verified Blender5.2.1LTS with
embedded Python3.13.13, plus standalone Python3.11.16 and Pillow11.3.0 for QA.
Run one CPU Blender worker at a time with four render threads in this cloud host.

The authoring scene records580,219 triangles,3,177 objects and3,039 estimated
material/submesh draws. No overhaul budget was supplied and these are not measured
engine draw calls or FPS. Runtime collision, LOD/batching, import, interaction,
electrical simulation, network state, audio and animation remain engine-owned.
Required gameplay mechanisms and inherited interaction anchors remain present;
this visual overhaul does not implement their runtime behavior.
