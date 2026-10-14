# Cafeteria R4 independent review

Reviewed on 2026-10-13. Scope: the authored cafeteria candidate, its thirteen R4 rendered cameras, three independently authored game-asset previews, and Blender source/rebuild evidence. The models and scripts were not edited, and no images were generated for this review. Prior critic reports and builder scores were not read.

The governing references were `design/ART_DIRECTION.md`, `design/ART_REFERENCE_INDEX.md`, `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md` (especially sections 6–9, 14.1 and 18), and the cafeteria portion of `design/facility-layout/front-end-area/DESIGN.md`. This review uses the supplied default category weights. Runtime/Unity acceptance is outside this review.

## Result

**90.55/100 overall; formal completion FAIL for the reviewed R4 state.** The visual result is strong enough for the default visual bar, but technical quality is below the required 85% category floor. The support-contact validator does not reject unregistered support-dependent props, and substantial inherited cafeteria dressing is unregistered. No critical visible scene failure was found in the thirteen supplied views. The cold-render comparison is pending, not a pass or a demonstrated regression.

The room convincingly reads as a warm staff cafeteria. The lilac/navy shell, tiled floor, seating groups, full lounge, serving counter and game corner form a coherent institutional place. Broad circulation is legible in both directions. The game equipment has specific construction and remains recognizable in the ordinary room cameras; it does not depend on its labels or studio previews to identify it. The remaining visual weaknesses are close-range finish and repetition rather than a failed room composition.

| Category | Score /100 | Weight | Earned points | Pixel/evidence basis |
|---|---:|---:|---:|---|
| Layout / route readability | 95 | 20 | 19.00 | Clear central axis and door approaches; dining, serving, lounge and games retain distinct usable areas. The lounge has not been reduced to filler seating. |
| Art direction / silhouettes | 91 | 20 | 18.20 | Believable scale, authored molded dining chairs, bent frames, specific doors, restrained architecture and a coherent palette. Large upholstery faces and some ancillary stock still look unusually uniform. |
| Hero objects / focal clarity | 92 | 15 | 13.80 | Foosball cabinets, rods, players, score sliders and returns; arcade frames, nets, baskets and return lanes; and the dart cabinet are visibly specific. The coffee machine is a weaker close-range focal asset, and the dartboard has a small bull-surface defect. |
| Materials / anti-plastic | 89 | 15 | 13.35 | Tile, painted wall, wood, metal, rubber, glass and upholstery are distinguishable. No dominant glossy-plastic failure. Sofa upholstery, serving stock and several ceramics remain too even in the close views to represent the highest craftsmanship requested. |
| Lighting / atmosphere | 91 | 10 | 9.10 | Warm practical zones, cooler overhead light, readable contact shadows and controlled emissives create depth without hiding the room. The distant red hall opening is conspicuously bright in the entry view, and a suspended sign catches strong glare in the dining hero view. |
| Dressing / worldbuilding | 89 | 10 | 8.90 | Meals, cups, cutlery, books, a remote, notices, league material and a cleaning/return area communicate daily use. Repeated aligned serving stock and similarly neat furniture reduce the sense of individual workers using the space. |
| Technical cleanliness / reproducibility | 82 | 10 | 8.20 | Independent asset creation/reimport, editable components, packed dependencies, preserved interfaces and fresh-process rebuild are supported. Required support-registration coverage is incomplete; cold-render comparison is pending; a small coplanar bull defect and redundant shader copies remain. |

The visual categories earn **82.35/90**. The overall score cannot override the category floor or the support-contact gate.

## Per-camera visual result

All thirteen PNGs in `renders/review_r4/` were opened individually at their native **960 × 540** resolution. PASS below means the view has a coherent authored read and no observed critical visual veto, obstructed principal route, gross clipping or visibly floating main asset. It is not a declaration that every small contact or surface has been geometrically validated.

| Camera | Result | Observation |
|---|---|---|
| `CAF_01_ENTRY_NORTH` | PASS | Central route and hall destination are immediately legible. Serving and games read at room distance. Distant red opening is over-bright relative to the room. |
| `CAF_02_DINING` | PASS | Tables, curved chairs, serving, medical and return area form a believable dining space. Large surfaces are restrained; neat repeated stock and tableware are the main finish limitation. |
| `CAF_03_SERVING` | PASS | Counter, glass guard, kiosk and queue are specific and grounded. The medical approach stays open. Glass reflections reduce food clarity somewhat without losing the function. |
| `CAF_04_LOUNGE` | PASS | Lounge remains a full seating destination, with both sofas, armchairs, TV wall, rug and bookcase. Open floor and local warm lighting keep it readable. |
| `CAF_05_GAME_CORNER` | PASS | Two foosball tables, two basketball machines and the wall dart cabinet have clear silhouettes. The corner has useful separation from the travel lane. |
| `CAF_X1_AIRLOCK_DOOR` | PASS | Door framing, leaves, seals, portholes and booth scale read plausibly. The approach is clear. Booths and upholstery are very regular. |
| `CAF_X2_YARD_DOOR` | PASS | Open doorway and threshold establish a visible connection beyond the cafeteria. Lounge and games remain on their sides of the approach. |
| `CAF_X3_MEDICAL_DOOR` | PASS | Distinct door construction and framing, with a clear threshold and sensible nearby drinks station. No observed gross contact fault. |
| `FE_05_CAFE_REVERSE_NORTH_TO_SOUTH` | PASS | Reverse route points naturally to the airlock. Furniture groups preserve negative space. Kiosk backs are plain but plausible. |
| `R8_GAMES_HERO` | PASS | The best detailed room view: rod grips, bearings, player teams, cabinet returns, nets, ball seams and machine frames remain readable. No obvious room-scale clipping. |
| `R8_LOUNGE_HERO` | PASS | Armchair frames, sofa seams, coffee-table contents and slatted media wall hold up. Sofa backs/cushions still have a relatively rigid, uniform surface read. |
| `R8_COFFEE_DETAIL` | PASS | Recognizable dual-group coffee machine and grinder with distinct metal, glass and ceramic. Weakest supplied detail view: portafilter handles visually merge with cups, top cups read filled/closed, and the control face remains spare and box-like. |
| `R8_DINING_HERO` | PASS | Molded chair shells and bent-tube frames are visibly authored; table dressing is legible. Suspended sign glare and repeated neat table/stock arrangements limit final polish. |

## Standalone game assets

`renders/assets/foosball.png`, `dartboard.png` and `basketball.png` were opened individually at **1200 × 1000**. The foosball table and basketball machine have convincing primary and secondary construction, with appropriately selective small detail. The dart cabinet has hinges, legible score sheets, modeled scoring sectors, metal divisions and darts. All three substantially exceed blockout quality.

**Minor factual defect:** the dartboard preview renders the inner bull as a dark center rather than a clean red disk. A read-only mesh probe confirms overlapping coplanar faces: the green outer-bull disk (radius 0.0158 m) and red inner-bull disk (radius 0.00635 m) both have their front face at local **y = −0.1330000013 m** and rear face at **y = −0.1289999932 m**. The smaller disk overlaps the larger disk's faces. This is a source defect, not an inference from an object name, and not a critical room-scale failure.

## Technical evidence

Reviewed `validation_r4.json`, the completed `validation_final.json`, `logs/cold_rebuild_final.log`, `logs/rebuild_validation.log`, `build_assets.py`, `revamp_room.py`, `rebuild.py`, `kit.py`, `review_images.py` and `../validate_front_end.py` in the technical role. The earlier unsuccessful cold-rebuild log is not used as the final gate result.

The finished rebuild log runs graphics generation, three standalone asset builds, room rebuilding and validation in fresh processes, then reports all twelve of its enumerated gates true. The final validation records:

- **799,582 evaluated triangles** for the full module: cafeteria 453,408; yard 252,594; hall 90,584; shared 2,996. This passes the 800,000 module budget, leaving only **418 triangles**. The cafeteria alone exceeds the repository's 400k flag; this is a flag and authoring headroom concern, not a measured runtime performance failure.
- Five reimported instances: two foosball tables at 32,830 triangles each, two basketball machines at 14,592 each, and one dartboard at 15,410. Component counts are 26, 18 and 111 respectively. Recorded reimport bounds errors are zero; the build also checks component and triangle preservation before placement.
- Seven unchanged interfaces, no violations in the six declared lane rectangles, and unchanged yard/hall/shared geometry signatures against the source.
- 108 interior floor bounding-box checks and 113 yard floor checks, with no reported gap or penetration failures. Yard checks deliberately use 0.12 m tolerance and are not strict millimetre-scale contact proof.
- **94 explicit anchors across 42 registered objects**, all passing the recorded gap/penetration/angle limits. Recorded gaps range from −0.0005 m to 0.005 m.
- All file images packed, all external fonts packed, no missing image/font dependencies, and no linked libraries. The built-in Blender font correctly requires no external file.

An independent read-only fresh Blender 5.2.2 process opened the saved candidate successfully with auto-execution disabled. The source uses metre units (metric, scale length 1), retains named cameras, and has unit-scale asset roots with floor-center or bull/mount origins. Foosball rods have separate pivot assemblies; airlock and medical leaves have hinge roots. The probe found no negative world determinants, zero local scales, or duplicate objects sharing both an identical mesh datablock and identical world transform in the cafeteria. This is a narrow duplicate check, not a full arbitrary mesh-intersection or normals audit.

The probe also found **155 material datablocks actually referenced by cafeteria polygons/curves**, including many numbered copies of the same palette materials after reimport. This is a source-consolidation issue. It is not a per-view material-family measurement, and the design's per-view material cap has not been demonstrated by these reports.

### Acceptance-blocking support coverage

The current validator checks registered anchors but never fails an unregistered support-dependent prop. The inherited floor routine silently skips absent `support` tags and exempts other support kinds. Walking the ancestors of tagged cafeteria props against the registered-root list found at least **69 standalone props without a registered support ancestor**:

- 28 table-supported objects, including table trays/cups, serving stacks and `lounge_table_lamp_0`.
- 30 wall-supported objects, including `rules_game`, `caf_E_bulletin_0`, signs, clocks, first-aid boxes, extinguishers and sockets.
- Five hanging zone signs: `zone_dining`, `zone_lounge`, `zone_game`, `zone_serving`, `zone_order`.
- Six rug-tagged objects, including the game stools, game side table, rugs and oche.

Additional unregistered `assembly` objects were not counted in this minimum because structural assemblies need classification. The supplied images do not establish that these props float. The defect is that **required coverage and the required missing-registration failure gate do not exist**, contrary to protocol 14.1. A pass over 94 selected anchors cannot certify the complete cafeteria's support-dependent dressing.

### Cold-render status

Fresh-process rebuilding and reopening are proven. At the time of this R4 review, the later thirteen-camera cold-render batch in `renders/review_r5/` and its exact same-camera comparison were in progress. Their result is **PENDING** and needs a separate evidence check. This R4 report does not claim the mandatory cold-render comparison or the last-two-cycle stability gate passed.

## Three highest-impact remaining issues

1. **Close the support-contact coverage gate.** Register inherited independently supported cafeteria dressing against actual targets and make the validator fail missing registrations. Revalidate from the saved source. This is the formal completion blocker.
2. **Bring the coffee station to the quality of the games.** Improve readable group-head/spout/handle separation, give the warming cups convincing open rims, and add a little specific control and drip-tray construction. `R8_COFFEE_DETAIL` exposes the largest disparity between a hero close-up and the room's strongest assets.
3. **Introduce selective human and material variation in the lounge and dining furniture.** Use localized cushion compression, a little asymmetry, worn contact areas and fewer perfectly aligned identical stock arrangements. Keep the existing clear routes and broad material restraint; avoid solving the uniformity with blanket grunge.

Also repair the small dart-bull coplanarity defect, consolidate repeated palette datablocks, and complete the pending cold-render comparison. None of these findings establishes a Unity import, collider, interaction, animation, networking, frame-time or gameplay acceptance result; those were not tested here.
