# Centered east Control room - architectural proposal P02

Latest user clarification: center the Control room along the east wall, aligned with the reactor. The stairwell must remain very small and the floorplan comes before more 3D work. This new 2D set replaces the rejected exposed stair/catwalk layout. It is a schematic for the game environment, ready for layout review, not a completed 3D scene or construction-permit package.

## Drawing set

`output/reactor_compact_stair_architectural_set.pdf` contains five A2 sheets (594 x 420 mm). Print at 100% for the stated scales; dimensions are millimetres and levels are metres.

| Sheet | Content | Scale |
|---|---|---|
| A100 | Hall floorplan, equipment schedule, circulation and stair footprint | 1:100 |
| A101 | Control room, furniture, doors and five stair-level plans | 1:50 |
| A201 | Reactor/pool section, schematic sightlines and stair section | 1:100 / 1:50 |
| A202 | East elevation, landing/door and entry sections, observation detail | 1:50 / 1:10 |
| A301 | Enlarged stair, dimension chains, rail and rise/going details, schedules | 1:25 / 1:20 / 1:5 |

Matching SVG files are complete vector sheets. `output/reactor_compact_stair_editable.dxf` is **geometry-only CAD**, with 15 named and labeled model-space view blocks in millimetres. It does not contain the PDF's paper-space title sheets. Dimensions are editable linework/text, rather than associative DIMENSION entities. Dashed linetypes are preserved. `drawing_validation.json` lists the views and insertion offsets.

## Spatial decisions

- Hall remains 21.60 m across, 420.48 m2, with the spec pool and two banks.
- Enclosed stair: 6.25 x 3.20 m gross (20.00 m2), entirely behind the east wall. Four flights stack in two bands. P02 shifts the core north to X12.46..18.71, Y3.20..6.40 while keeping its size.
- Flights: 1.20 m between inner handrail faces; landings 1.25 m clear. Four flights of 14 rises and 13 goings; 56 rises exactly reach +10.000 m.
- D01: 1.20 x 2.10 m inner stair door at Y4.20..5.40, north-hinged so the open leaf clears the south approach through the retained 1.30 m-deep vestibule. The retained 4.00 x 5.00 m east route is distinguished from it in elevation E01.
- D02: direct top-landing doorway at Y3.20 into the adjacent 3.60 x 6.40 m clear Control room (23.04 m2), with two desks and a rear mimic panel. The room clear bounds are X11.16..14.76, Y-3.20..3.20: exactly centered on Y=0.
- W01: 5.40 x 2.60 m main observation pane spanning Y-2.70..2.70, centered on the reactor axis with equal 500 mm room end jambs. A 650 mm interior glazed floor strip and lower pane improve near-wall observation. Section rays are schematic; actual 3D occlusion must be checked after plan review.
- The latest user direction removes the historic +4.8 m overview and all exposed hall stairs/catwalks. All 15 equipment sectors and four route thresholds remain represented.

Required dimensions come from `../scenery/reactorroom.md`; style direction is the brighter second A02 concept and the current art bible. Decisions are recorded in `../production/FOUNDATION_DECISIONS.md`. No old 3D assets were opened and no computer use or new ImageGen was used for these drawings.

## Authoring and software

`build_drawings.py` authors PDF, SVG and DXF from shared dimensioned primitives. Its reusable stair/room module keeps P01 local coordinates; the P02 View transform adds 1.20 m north to both rendered and CAD plan geometry. World coordinates are explicit in validation. P01 source/outputs/review are preserved under `archive/P01/` as superseded drawing history. Python/ReportLab and Poppler use the bundled runtime. The downloaded CAD library is ezdxf 1.4.4 (MIT), installed with dependencies under the ignored `.deps` directory. No graphical application was installed or automated.

Official references: [ezdxf installation](https://ezdxf.readthedocs.io/en/stable/setup.html), [drawing/export documentation](https://ezdxf.readthedocs.io/en/stable/addons/drawing.html).

Run `./build.ps1` to build and render with the configured local runtime. Alternatively, use Python 3.12 with ReportLab/pypdf and install `ezdxf==1.4.4` into `.deps`, then run:

```powershell
python sections/reactor-room/architecture/build_drawings.py
pdftoppm -png -scale-to 2400 sections/reactor-room/architecture/output/reactor_compact_stair_architectural_set.pdf sections/reactor-room/architecture/output/previews/sheet
```

## Review and handoff

Checks cover exact stair/room arithmetic, station-to-ring clearances, sheet bounds, five PDF pages, and a reopened DXF with populated view blocks and zero audit errors. Every page is also rendered and visually inspected. Independent Sol scores are recorded in `SOL_REVIEW.md`; these apply to the schematic drawings, not final 3D art.

The next checkpoint is user review of the floorplan. Previous Blender checkpoints 01-10 are preserved history with a rejected stair layout. Rebuild accepted geometry from scratch after this review, then verify actual first-person circulation and panoramic sightlines. Preserve the separate user-rating checkpoint for generated references before detailed art.
