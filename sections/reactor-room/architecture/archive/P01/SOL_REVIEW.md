# Sol architectural review — compact reactor stair and Control layout

**Reviewed:** A100, A101, A201, A202, A301; `build_drawings.py`; `drawing_validation.json`; reopened raw DXF structure.  
**Decision:** **PASS.** Every category relevant to this requested floorplan set scores at least 90/100. The drawings are suitable to approve the compact layout and resume dimension-locked 3D foundation work.

| Category | Score | Review basis |
|---|---:|---|
| Compactness | **97** | The four flights occupy one 6.25 × 3.20 m gross core (20.00 m²) outside the hall. The 23.04 m² Control room remains compact and directly adjoining. No stair or catwalk intrudes into the reactor hall. |
| Layout and circulation | **94** | The sequence from the retained east route opening through the 1.30 m vestibule, D01, four switchback flights, west top landing, and D02 is continuous and legible. Flights provide 1.20 m clear width and landings 1.25 m clear. The north station arrangement preserves a 2.30 m straight door apron and 2.30 m lateral gaps. |
| Dimensional fidelity | **98** | Both core chains close exactly: 6.25 m longitudinal and 3.20 m transverse. Four sets of 14 risers at 178.571 mm produce exactly 10.00 m total rise; each flight has 13 × 250 mm goings. The stated 35.538° nosing pitch is mathematically correct. The closest station-to-ring clearance is explicitly dimensioned at 1.312488 m. |
| Architectural completeness and conventions | **93** | The set includes coordinated ground and level plans, all five stair datums, hall and stair sections, east elevation, both entry/landing sections, glazing detail, enlarged stair plan, rail/riser details, door and stair schedules, section/detail references, cut/overhead line distinctions, UP/DN direction, and destination levels. This is complete for the requested game-layout design stage. |
| Legibility and presentation | **95** | The five A2 sheets have consistent hierarchy, scale labels, datum notation, line weights, active-landing tint, and readable dimensions. Dense information is separated into enlarged details rather than compressed into the general plans. No text or drawing points are reported outside the content bounds. |
| Deliverable usability | **94** | The PDF contains five sheets; SVG sheets provide editable page graphics. The fixed DXF reopens with all 15 named model-space view blocks populated. An independent raw-DXF count found 1,064 drawable entities, and every per-block count matches the saved validation. The DXF is correctly described as geometry-only millimetre blocks; the PDF/SVG set is the paper-sheet authority. |
| Coordination and traceability | **95** | Plans, sections, elevation, details, schedules, and validation values use the same core, stair, door, glazing, and Control-room geometry. The source policy and stated limitations clearly distinguish new 2D work from any legacy 3D content. |

## Evidence and checks

- Stair arithmetic is internally consistent: 14 × 178.571 mm = 2.50 m per flight, four flights = 10.00 m; the tread pitch uses one riser over one going rather than the full-flight endpoint ratio.
- The 6.25 m core length is fully allocated by 0.20 wall + 1.30 landing + 3.25 run + 1.30 landing + 0.20 wall. The 3.20 m width is fully allocated by 0.20 wall + 1.30 flight + 0.20 well + 1.30 flight + 0.20 wall.
- A202 makes the two-stage east entry explicit: the retained 4.00 × 5.00 m route opening is the outer hall boundary, while D01 is the smaller 1.20 × 2.10 m stair door behind the vestibule.
- The top landing aligns with D02 and the Control room without a residual corridor or dead end. The 5.40 × 2.60 m main observation pane and lower observation strip have explicit vertical datums and a dedicated detail.
- DXF verification did not rely on registry counts alone: the exported ASCII structure was parsed independently and every named view block contains LINE, LWPOLYLINE, CIRCLE, or TEXT entities as applicable.

## Nonblocking items for the next stage

- The exact-fit core dimensions are sound as design geometry. Preserve the nominal chains during 3D translation; construction tolerance and code compliance are outside this game-layout review.
- The sightlines on A201 are correctly labeled schematic. Whole-room visibility and occlusion remain pending until the approved layout is rebuilt and tested in 3D from physical operator eye points.
- Use the PDF/SVG files when sheet composition matters. The DXF intentionally contains separated model-space view blocks rather than paper-space sheets.

Final 3D art, material, lighting, Valorant-style detail, and rendered-scene scoring are **not assessed** by this floorplan review and remain subject to the separate ≥90-per-category acceptance requirement.

## Final typography confirmation

The rebuilt A301 preview resolves the last annotation collision: `UP F1` now sits clearly above the visible-flight arrow with ample separation from the rotated `1 200 CLEAR` dimension. The adjacent well, landing, tread, rail, and riser annotations remain unobstructed. The typography correction does not change the review scores or pass decision.
