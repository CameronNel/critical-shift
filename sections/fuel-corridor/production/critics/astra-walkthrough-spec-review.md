# Fuel Corridor walkthrough specification review

Read-only specification review, 11 September 2026. No scene, render, source edit, neighboring geometry, or live MCP inspection. The current interface and frozen full04/interface.json are byte-identical: SHA256 `ce6ddfa16e0bbea71030e9c190f6507b8fa69fa2e489c548f3a04a3cd21a872e`. This binds the numeric contract, not the actual saved geometry or visible text.

## Mandated scope versus chosen count

- No explicit numeric Fuel Corridor exit, doorway, or leaf count appears in the reviewed chapter 23, assignment, master brief, or facility README. No sequential visible door-numbering scheme is specified.
- Authoritative GAME_SPEC chapter 23 places Fuel Corridor between Fuel Assembly and Reactor Hall (lines 2404–2406), gives adjacent travel 10–20 s, refinery-to-reactor 15–30 s, and full crossing under 60 s (2414–2419). The shortcut list (2421–2432) is facility-wide; it does not assign a separate Fuel Corridor exit to every listed route. Modularity requirements are at 2434–2448.
- The Fuel Corridor assignment, line 2, requires a coherent freight route with turns, thresholds/doors, service bypass and junctions, sized to actual handling needs. It requires measured interface/topology documentation and explicit unverified connections; it does not require a direct door to every later facility room.
- Current P07 implementation commits to **five external ports**: F01 REFINERY, F02 REACTOR, S01 PLANT, S02 CLEAN and S03 WASTE (interface.json lines 10–105). The connection contract adds **one internal 3.40 × 3.40 m freight sliding gate** (CONNECTION_CONTRACTS.md:31). Therefore six door/gate assemblies are the documented design interpretation, not a chapter-23 numeric exit mandate, nor a leaf count or proof of six usable exits.
- PLANT is explicitly one shared cooling/turbine/electrical header; CLEAN is one medical/reanimation/compliance header; WASTE is one transfer branch. Destination seams are unverified. The contract explicitly says Plant is one shared header, not three completed connections (CONNECTION_CONTRACTS.md:35–41).
- F01/F02 are section-owned removable presentation caps distinct from neighboring doors; neighboring reactor doors remain closed (CONNECTION_CONTRACTS.md:16,73). A displayed closure, a port, and a usable through-exit are different counts.

## Dimensions and footprint

- BUILD_BRIEF.md:5 permits plausible metric dimensions to be chosen and recorded where unspecified; :9 requires a dimensioned floorplan/interface, local main threshold at (0,0,0), +Y inward, +Z up, human scale, access, door swings, headroom and cart/stretcher routes. README.md:16 requires entry dimensions and all additional portals in interface.json. Neither prescribes a numeric Fuel Corridor footprint.
- P07 floor cells span X[-5.4,17.0], Y[0,24]: **22.40 × 24.00 m overall floor envelope**, also explicitly labeled in A101-plan.svg:293,299. This is the bounding envelope of an irregular floor plan, not filled rectangular area or measured outer wall/fixture bounds.
- Port nominal W × H: F01 2.60 × 3.00 m (interface.json:23–24); F02 5.00 × 5.00 (:45–46); S01/S02 2.00 × 2.50 (:67–68,:84–85); S03 2.40 × 3.00 (:101–102).
- Freight approach/cross passage is 4.40 m gross, staging bay 6.60 × 6.20 m, reactor adapter 5.60 m gross (CONNECTION_CONTRACTS.md:31). The inlet is 3.20 m gross (:77). Freight height 4.40 m, service 3.00 m, inlet 3.90 m, reactor adapter 5.90 m (:55). Service bypass is 2.40 m nominal / 2.00 m dressed target (:67), with the north leg widened to 3.00 m gross (:75). Upstand target is at most 5 mm (:57).
- Freight centerline is 38.20 m; bypass 23.40 m (:33). 25.47 s connector-only and 28.67 s including owned neighboring sill/stub are estimates at assumed 1.50 m/s, excluding room legs, turns, handling and door delays (:71). They do not establish runtime travel compliance.

## Numbering and wayfinding

- The dimensioned plan uses **FG01** for the internal gate (A101-plan.svg:247), **F01/F02** for freight seams (:274,277), and **S01/S02/S03** for service branches (:280,283,286). These are distinct identifier families. Their numeric suffixes are not a mandated contiguous exit-number sequence.
- ART_DIRECTION.md:433–444 requires sparse signage serving navigation, hazards, interaction, procedure or institutional character. :332–338 supports department identifiers and says color is never the only gameplay signal. GAME_SPEC.md:2454–2459 requires accessible critical information and color not to be the only signal; :3922 calls signage functional and sparse. No prescribed visible number, label wording, arrow count or numbering placement is stated in these passages.
- SPEC_CONTENTS.md:14 includes route signs, labels and safety markings as authored content. Whether actual approach faces communicate destinations correctly must be judged from the saved scene/text and walkthrough pixels; this document does not assume it.

## Exact source roots

- Master and assignment: `C:/Users/Camer/Games/critical-shift/ops/facility-run/{BUILD_BRIEF.md,README.md,briefs/fuel-corridor.md}`.
- Authoritative design: `C:/Users/Camer/Games/critical-shift/worktrees/reactor-valorant/design/{GAME_SPEC.md,ART_DIRECTION.md}`. This is the design root required by BUILD_BRIEF.md:5.
- Current local contract: `C:/Users/Camer/.codex/worktrees/3598/critical-shift/sections/fuel-corridor/interface.json` and `architecture/{CONNECTION_CONTRACTS.md,A101-plan.svg,SPEC_CONTENTS.md}`.
- The assignment and README preserve the completed shallow mine decline. Chapter 23's older Mine Lift wording does not authorize adding a mine lift to this connector (briefs/fuel-corridor.md:2; README.md:9).
