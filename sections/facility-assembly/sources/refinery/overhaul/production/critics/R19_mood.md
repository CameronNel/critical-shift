# Independent visual review — R19

## Review scope

I opened all 11 images in `production/renders/R19/` at full resolution and judged them against the current refinery brief, the fixed-camera route requirements, and the supplied Spawn quality references. The Spawn reference was used for finish control and physical construction only; R19's darkness and palette were judged against the owner's updated mood direction.

## Scores

| Category | Score | Weight | Pixel and evidence basis |
|---|---:|---:|---|
| Route readability | 94 | 20% | The open central aisle, worn lane marks, and clear doorway approaches remain readable in ENTRY, MAIN_ROUTE, REVERSE, and DISPATCH. The darkest machinery zones lose secondary controls, but the walking route stays distinct. |
| Art direction and silhouettes | 95 | 20% | Purpose-built process equipment, restrained grey-green concrete, faded oxide, and isolated practical pools give the room a coherent hostile industrial identity. Machine silhouettes remain clear despite the black ceiling and unlit bays. |
| Hero process equipment | 94 | 15% | The PV vessel, gauge faces, locking ring, valves, and interstage coupling read as authored working equipment. In HERO_DETAIL the staining is visible, though it remains localized and relatively smooth against broad panels. |
| Materials and anti-plastic quality | 88 | 15% | The color families and metal/concrete response separate well. The thin wall trails have crisp graphic edges, and the broad wall and floor fields remain smooth; those areas still need more convincing, physically placed wear. |
| Practical lighting and atmosphere | 96 | 10% | Dark ceiling, failed fixtures, and separated cold light pools make the room feel bleak and depleted. The strips are bright but visibly physical; PROCESS and MATERIAL remain dark enough that some control and material detail is difficult to judge. |
| Purposeful dressing and worker storytelling | 95 | 10% | WORK_NOOK now reads as an interrupted break: an empty mug lies on its side, work gloves sit separately, and the seal notice hangs crooked beside the radio and shift papers. This is a clear, restrained story cue without blocking the work surface. |
| Technical cleanliness and reproducibility | 94 | 10% | `validation_R19.json` reports PASS, zero protected-interface changes, world strength 0, no route obstructions, 21 in-room practical lights bound to fixture lenses, six registered failed fixtures confirmed dark, 409 support-contact records, and 963 closed-mesh normal checks. `build_R19.json` records 29 protected interfaces and a source hash matching the validation report. Its `coldstart_rebuild` field is false; a fresh-process rebuild was not supplied, and the independent human-prop audit was still pending. |

**Weighted score: 93.6/100.** R19 does not meet the rubric's 99 points in every category or weighted threshold. No automatic visual veto was observed in the 11 current renders. The room's dark, gloomy mood and interrupted-shift cue are working; the remaining gap is the visible character of its wear.

## Highest-impact corrections

1. **Soften the wall-trail edges.** In PROCESS, MAIN_ROUTE, PINCH, and MINE_TO_CRUSHER, the tapered gravity marks have plausible placement, but their dark, sharply bounded silhouettes read as painted graphics. Let the edges fade into the concrete and vary their width and opacity along each path so they read as thin water residue.
2. **Spread wear across the surfaces that carry the room.** The lane paint is visibly worn and the route remains legible, but much of the concrete and floor still reads smooth and evenly finished. Add restrained, localized wear that follows leak paths and service traffic while retaining quiet areas and clear route marks.
3. **Preserve the nook's new story cue.** The tipped empty mug, separated PPE gloves, and crooked seal notice communicate interruption immediately. Keep those elements readable at the fixed nook camera and keep the workbench itself clear enough to use.
4. **Keep the present lighting hierarchy.** The ceiling blackness, isolated cold pools, and failed fixtures carry the requested atmosphere. Any local legibility adjustment should target controls or work surfaces that disappear, not raise the room's overall fill.

## Technical limits

Formal R19 validation passed the checks it represents; it does not certify exhaustive intersections or runtime collision. The build manifest explicitly records `coldstart_rebuild: false`, so this review does not establish fresh-process reproducibility or final acceptance. The aperture rays demonstrate unblocked fixture openings; they do not measure task-plane illumination or runtime readability.
