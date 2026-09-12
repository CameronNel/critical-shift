# Fuel Corridor Luna independent pixel review — full01 baseline

**Decision: REJECT full01 visual baseline for correction.**

Inspected every supplied full01 render independently: the ten formal views `C01_ENTRY.png`, `C02_PRIMARY_ROUTE.png`, `C03_HERO.png`, `C04_REVERSE.png`, `C05_EAST_TURN.png`, `C06_REACTOR_THRESHOLD.png`, `C07_BYPASS.png`, `C08_SERVICE_JUNCTION.png`, `C09_MATERIALS.png`, `C10_PLANT_HEADER.png`, plus detail views `D01_CARRIER_OPERATION.png`, `D02_WORKBENCH.png` and `D03_UTILITY.png` under `production/renders/review/full01`. Compared actual pixels against the current reactor A05 authority, mine Valorant-pass references and the accepted style-slice language. This is the first full visual baseline and receives no score inheritance from style22 or from the C07 concept.

## Overall visual scores

| Category | Score /100 | Observed basis |
|---|---:|---|
| Scale / human proportions | 91 | Door, bay, bench and carrier relationships generally read adult-scale; the carrier and cask are credible in C03/C09/D01. Empty route views provide limited object references, so this is visual plausibility rather than measured proof. |
| Circulation / route readability | 78 | C03 has a readable staging box and arrow, but C02, C04, C05, C06, C07, C08 and C10 mostly show blank corridors or closed doors with little directional or junction information. The route cannot be followed confidently across the full batch. |
| Required equipment | 84 | C03/C09/D01 show the carrier, sealed cask, restraints, brakes and inspection context; D02/D03 are strong service details. Most formal route views have no visible freight or connector equipment, leaving the full module under-equipped in presentation. |
| Logical flow / operation | 80 | The staging and maintenance story is clear in the hero/detail cluster, but the empty corridors and closed threshold/header views do not establish how the freight, service bypass and neighboring destinations connect. |
| Shape / art direction | 87 | Local construction is coherent: charcoal framing, light cladding, orange accents and practical fixtures fit A05/C06. Repeated empty modules are too generic and quiet compared with A05's authored industrial density and the mine's purposeful rough service infrastructure. |
| Hierarchy / focal clarity | 84 | C03, C09 and D01 have a strong carrier focal hierarchy, while D02/D03 have useful service anchors. The formal route views lack focal markers and read as disconnected architectural studies, weakening progression through the module. |
| Materials / anti-plastic | 89 | Carrier, cask, steel, rubber, tools, cloth gloves and leather palms are differentiated in the close views. Broad route surfaces are comparatively smooth and repetitive, with limited localized material storytelling at the distances shown. |
| Lighting / atmosphere | 88 | Warm practicals and cool ambient structure work well in C03, C09 and the detail views. Several empty corridors are flat or cool, and C06/C10's closed-door views have little atmospheric or destination emphasis. |
| Color discipline | 91 | The neutral panel / charcoal frame / orange safety language remains controlled and consistent with A05/C06. Color is one of the stronger full-batch qualities, but it cannot compensate for missing route information. |
| Environmental storytelling | 80 | The cask tag, carrier hardware, workbench supplies, gloves, tools and service-air station establish a credible maintenance bay. The majority of the formal route views contain mostly walls, floors and doors, so the facility's operation disappears outside the staging cluster. |

## Per-view visual read

The scores below summarize each actual image's visual completeness and route/story value, rather than claiming technical correctness.

| Image | Score /100 | Primary observed result |
|---|---:|---|
| `C01_ENTRY.png` | 87 | Adult-scale entry and staging context are plausible, with a small carrier and service table visible; the long approach is largely empty and the freight story is distant. |
| `C02_PRIMARY_ROUTE.png` | 77 | Clean, well-lit passage with credible framing, but it ends visually at a blank wall and lacks the crossing equipment, branch cue and route hierarchy needed for a primary route view. |
| `C03_HERO.png` | 93 | Strongest formal view: carrier, service door, utility station, workbench, staging box, direction arrow and ceiling construction form a coherent bay. |
| `C04_REVERSE.png` | 82 | Proportions and cladding are readable, but the closed double-door termination and sparse side walls provide little reverse-route story or equipment. |
| `C05_EAST_TURN.png` | 81 | The turn volume reads as an architectural corner, yet the view is almost entirely empty corridor, with a weak destination cue and little operational evidence. |
| `C06_REACTOR_THRESHOLD.png` | 78 | Door construction is clean, but the tight dark threshold view lacks transition storytelling, neighboring identity and material/filler specificity. |
| `C07_BYPASS.png` | 80 | Narrow passage and scale read plausibly; route is uncluttered, but the blank end and minimal service detail make the bypass function ambiguous. |
| `C08_SERVICE_JUNCTION.png` | 78 | Junction volume and lighting are credible, while the image presents mostly empty panels and floor with no visible service junction anchor. |
| `C09_MATERIALS.png` | 94 | Strong carrier material/construction close view: restraints, lifting eyes, saddles, wheels, dark backing and cask shell read clearly. |
| `C10_PLANT_HEADER.png` | 77 | Door and header construction are legible, but the near-empty termination supplies almost no plant-branch identity or environmental story. |
| `D01_CARRIER_OPERATION.png` | 94 | Park pedals, handle, restraints, wheels, lifting eyes and inspection tag clearly communicate operation and scale. |
| `D02_WORKBENCH.png` | 93 | T03 cloth gloves, leather palms, forged tools, grease, toolbox, mug and tool board create a credible maintenance station; the upper instruction text is cropped. |
| `D03_UTILITY.png` | 94 | Gauge, regulator, wheel, piping, hose and service board provide a clear, materially differentiated utility assembly; the lower hose path is partly outside frame. |

## Major visual deficits

- The full formal route is visually under-described. C02/C04-C08/C10 are predominantly empty passages or closed-door terminations, so the batch does not communicate a connected freight corridor at the density established by A05.
- Operational equipment is concentrated at C03/C09/D01-D03. The route views need visible, purposeful transition and service identity while keeping the transport lane clear.
- The strongest materials and storytelling are confined to closeups. Broad route walls and floors repeat a quiet neutral field with too little local construction variation to carry the full module.
- C07's r02 concept demonstrates that a branch can read spatially and carry junction equipment; the actual full01 render set has not yet reached that level of route communication.

## Technical evidence boundary

Reviewed the supplied `production/evidence/technical_full01.json` without rerunning it. `camera_and_render_settings`, `geometry`, carrier envelope, cartridge core and source match report `PASS`, but the overall evidence status is `FAIL`: `support_contact` fails for named assemblies including `East_extract`, `Longitudinal_tray`, `Medical_side_key`, `REACTOR_BOUNDARY`, `REFINERY_BOUNDARY` and `Service_extract`; `internal_routes` also fails. The route evidence reports a sampled freight minimum width of 2.252 m against a 2.4 m requirement and blocked rays. These are technical blockers independent of the pixel scores above. Full acceptance must wait for corrected support and route evidence plus a later clean full visual batch.

**Full01 visual result: REJECT.** The strongest hero, carrier and detail images pass their local visual intent, but overall circulation, equipment coverage, logical flow, hierarchy and environmental storytelling remain below 90. No full-scene, runtime, cold-start or technical acceptance is supplied.

No coordinate recipe, replacement geometry prescription or GPU render is supplied in this review.
