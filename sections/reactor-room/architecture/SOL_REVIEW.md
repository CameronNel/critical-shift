# Sol architectural review — P02 centered east Control room

**Reviewed:** fresh A100, A101, A201, A202, and A301 page renders; `build_drawings.py`; `drawing_validation.json`; and reopened exported DXF geometry.  
**Decision:** **PASS.** Every category relevant to the requested floorplan set scores at least 90/100. P02 is suitable for user review and, if approved, for a new dimension-locked 3D foundation. P02 supersedes the archived P01 layout.

| Category | Score | Review basis |
|---|---:|---|
| Compactness | **97** | Four flights remain stacked in one 6.25 × 3.20 m gross core (20.00 m²). The centered Control room remains 3.60 × 6.40 m clear (23.04 m²), directly adjoins the top landing, and adds no corridor or exposed hall stair. |
| Layout and circulation | **96** | The retained east route feeds a closed 1.30 × 4.00 m vestibule, bends north inside it, and reaches D01 without entering the hall circulation ring. D01 is north-hinged so its open leaf parks against the vestibule's north side. D02 directly joins the west top landing to Control. |
| Access and door operation | **96** | Exported D01 clear limits are Y4.20–5.40 with the open leaf from (12.46, 5.40) to (11.26, 5.40). The southern vestibule approach remains clear. D02 spans X12.71–13.91 on the shared Y3.20 wall, with its 1.20 × 1.20 m interior swing space reserved. |
| Dimensional fidelity | **99** | Independent DXF measurements confirm the Control clear bounds X11.16–14.76, Y−3.20–3.20; W01 Y−2.70–2.70; stair core X12.46–18.71, Y3.20–6.40; and unchanged exact-fit stair chains. Four sets of 14 × 178.571 mm risers still produce exactly +10.000 m. |
| Architectural completeness and conventions | **95** | Coordinated plans, five stair levels, sections, centered east elevation, entry and landing sections, glazing detail, enlarged stair plan, rail/riser details, schedules, section references, door swings, break symbols, UP/DN direction, and destination levels adequately define this schematic game layout. |
| Legibility and presentation | **96** | The five A2 sheets have consistent hierarchy, scale notation, datums, line weights, and revision labels. The final typography pass cleanly separates the A101 axis from `CONTROL`, moves the A202 axis label beside its line, and separates the A301 continuation note from the break symbol. No visible annotation collision remains. |
| Deliverable usability | **96** | The PDF contains five current sheets; matching SVG files provide editable sheet graphics. The actual DXF reopens with zero audit errors or fixes, all 15 named model-space blocks populated, and 1,089 drawable entities. The DXF is correctly identified as geometry-only millimetre blocks; PDF/SVG remain the sheet-composition authority. |
| Coordination and traceability | **98** | P02 world coordinates agree across plan, elevation, section, detail, schedules, and exports. The source and handoff policy clearly identify this as newly authored 2D work and mark the rejected 3D01–10/P01 layouts as superseded. |

## Independent geometry evidence

- The exported A100 block contains the shifted core at **(12,460, 3,200)–(18,710, 6,400) mm**, the centered Control outer shell at **(10,800, −3,400)–(14,960, 3,400) mm**, and the retained vestibule at **(11,160, 1,600)–(12,460, 5,600) mm**.
- The vestibule is physically closed in the export by the south closure, north closure, and east return. Its D01 swing envelope measures **(11,260, 4,200)–(12,460, 5,400) mm**.
- The exported A101 Control block contains the exact clear-room rectangle **(11,160, −3,200)–(14,760, 3,200) mm**, W01 at **Y−2,700–2,700 mm**, the 650 mm interior glazed strip, the shifted core, and D02's correct inward swing.
- The exported A202 elevation places both observation panes symmetrically at **Y−2,700–2,700 mm**. The main pane is **+10,300–+12,900 mm**, the lower pane **+8,000–+10,200 mm**, and each side shoulder is **3,300 mm**.
- The C-C section export uses the shifted world positions: Control terminates at Y3.20 m and the stair begins there, so D02 is a real shared-wall connection rather than a diagram-only adjacency.
- The exported A301 detail uses the same shifted core and D01 swing. Its cropped vestibule has a conventional break and an explicit continuation note back to A100.
- Independent per-block entity counts exactly match `drawing_validation.json`; this review did not accept validation metadata as proof of exported geometry.

## Items intentionally pending

- A201 correctly labels its sightlines as schematic. Whole-room visibility and plan occlusion must be tested later in the approved 3D layout from physical operator eye points.
- Preserve the P02 world coordinates and exact stair chains during 3D translation. Construction tolerances and permit engineering are outside this game-layout review.
- Final 3D art, materials, lighting, Valorant-style detail, and rendered-scene quality are **not assessed** here and remain subject to the separate requirement of **at least 90/100 in every relevant category**.
