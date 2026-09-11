# Waste Storage — takeover requirements

Authority read first: facility-run BUILD_BRIEF.md and briefs/waste-storage.md; reactor-valorant design GAME_SPEC.md, ART_DIRECTION.md, ART_REFERENCE_INDEX.md and AUTONOMOUS_SECTION_BUILD_PROTOCOL.md. Latest user direction takes precedence: complete room early, strict Valorant, no teal, independent Luna, autonomous concept approval and corrections. Older slice-only/Astra-reviewer instructions are historical. Original stopped worktree remains untouched.

## Explicit requirements

- Canonical facility sequence Electrical → Waste Storage → Medical → Compliance (§23). Receiving, segregated storage, designed casks/containers, controlled access, cart turns, monitoring, ventilation, maintenance and safe movement (assignment).
- Waste capacity, reactor waste transfer, illegal storage, exposure and contamination (§6,12); inventory queries, scanning and discrepancies (§13–14); waste breach (§17); nearly-full backlog scenario (§20.5).
- Physical carts, handles, tools, carried workers and hiding capacity (§4,16,29). Hiding is a tagged container volume with escape/search/risk hooks, not graphic disposal.
- Readable warnings, prevention and recovery (§2.3); host-owned state, stable IDs and machine/incident/audio hooks (§23,25,28,30). Blender delivers editable physical source and hooks; engine behavior is not claimed.

## Authored design choices

Keep inherited 12×18×4.8m clear envelope. Four cells: A residue overpacks, B shielded casks, C dry contaminated filters/tools, D quarantine. Counts are design choices: 3 residue overpacks, 2 shielded casks, 2 dry containers, 1 quarantine container, 1 transport cart, 1 handling jib, 1 inventory station, 1 ventilation/filter skid, 1 repair bench. No physical nuclear ratings are asserted.

Central cart lane X±1.8; entry turning circle diameter3.6 at(0,2.5), rear diameter3 at(0,16). Cells X±2.15..5.65, Y4.8..8.8 and9.4..13.4. Cell openings target1.8m, working service depth≥0.9m. Rear service zone Y14.5..18. Monitoring booth near southwest; personnel route across front apron. No props in reserved turns or door thresholds.

Receiving WS_RECEIVING keeps(0,0,0), outward−Y, clear3×3.2m; actual inherited wall depth.32m retained. Existing Electrical seam requires Waste origin(0,16.97,0) in Electrical frame,Rz0. Existing 2mm Waste lip may be removed within this owned rebuild for a flush threshold; record the change rather than edit Electrical.

WS_PERSONNEL keeps(6,2.4,0), outward+X,1.2×2.3m. It is a personnel branch, not a certified stretcher route. WS_DISPATCH keeps(0,18,0), outward+Y,2.4×2.8m, intended service-network continuation toward Medical/Compliance. Main receiving/dispatch route supplies the wider rescue path. No invented direct medical wall mating: Medical's single2.2×2.5m port and evolving scene require connector-owner reconciliation.

## Unresolved interfaces

Fuel Corridor S03_WASTE is reserved only, with no common facility transform. It must reach shared freight circulation; do not create a conflicting second receiving doorway. WS_POWER is a low-voltage branch, not Electrical U02's large distribution bus. WS_EXTRACT and WS_DATA are capped boundary sockets pending network ownership. Medical and Compliance are unchanged; their documents explicitly do not prove assembled connections.

## Evidence plan

Dimensioned plan and contract before build; original generated overall/reverse and machinery concepts; independent Luna review. Ten fixed player-height cameras plus supplementary approaches. Evaluated geometry, aperture rays, support-contact checks, player/cart envelope sweeps, sign bounds and machine count checks. Reopen saved artifact in fresh Blender, repeat all cameras, compare scene/source fingerprints and honest pixel stability. Section-only commit/push after approval.
