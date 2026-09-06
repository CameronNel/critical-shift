# Review 12 — Pass 12

Independent visual review against the unchanged Briefing, Hall, and Locker targets. Scores are 0–100 per category; 90 means close visual correspondence, and every one of the nine categories must reach 90 for the gate to pass.

| Room | Lighting | Art style | Layout fidelity |
|---|---:|---:|---:|
| Briefing | 82 | 86 | 89 |
| Hall | 82 | 87 | 85 |
| Locker | 79 | 85 | 84 |

The gate is **not met**. Pass 12 is recognizable and materially closer, but the remaining gaps are visible in tonal balance, surface wear, and camera composition.

## Briefing

The two benches and board arrangement are close to the target, so layout is the strongest category. The render still has a strong tonal inversion: normalized wall samples are much brighter than the target (upper plaster 123.3 vs 93.5 luminance; teal 85.8 vs 66.1), while the timber floor is much darker (42.9 vs 69.2) and less orange (warmth 39.5 vs 62.3). The surface language is cleaner and less distressed than the target, especially on the teal paint and floor boards. The lower/right bench is tight against the frame, and the target's side poster and doorway edge have more breathing room.

Highest-value edits:

1. **Lighting:** locally reduce wall fill by roughly 20–30 luminance points and add a warm floor pool; preserve the already close ceiling value and warmth.
2. **Material:** strengthen worn-but-maintained paint chips and timber grain/variation on the wainscot, floor, and benches.
3. **Composition:** open the bottom/right framing enough to retain both benches' breathing room and keep both side anchors readable, without changing the two-bench arrangement.

## Hall

Poster framing is repaired and the passage is readable, but the corridor remains flatter and cooler than the target. Normalized samples show the end wall at 139.7 vs 123.9 luminance and 38.0 vs 58.1 warmth, the lower teal at 96.5 vs 81.4 and -1.0 vs 9.1 warmth, and tile at 148.6 vs 132.8 and 20.6 vs 35.3 warmth. The right-side portrait, briefing sign, and door top sit materially low in the render; the cart is also more cropped at the bottom. This is a camera/composition issue, not a reason to move the room architecture. The extinguisher cylinder is fully in frame; only the edge pipe is partial.

Highest-value edits:

1. **Lighting:** lower the wall/tile levels and restore selective warmth; do not globally brighten the already slightly dark ceiling.
2. **Composition:** raise/re-center the right-side anchor group by about 50–100 render pixels and give the cart more bottom clearance while preserving the clear passage and open doorway.
3. **Material/content:** add stronger worn edges and layered paper detail to the shift board and corridor dressing; keep the extinguisher fully visible and the pipe edge treatment as in the target.

## Locker

The physical arrangement remains acceptable: the supplementary detail confirms four identical locker bodies in two banks, and the corner render retains the entrance and two benches. The visual match is held back by the large pod blocking the right bank and laundry/peg dressing, plus a severe tonal split. Normalized back plaster is 170.2 vs 119.4 luminance while the ceiling is 72.6 vs 90.4; the lower wall is slightly dark and too brown (warmth 22.0 vs -0.2), and tile is 168.1 vs 153.1. Locker, tile, and plant materials read credibly, but the target has clearer muted teal, metal highlights, small-tile variation, and legible shelf/cloth detail.

Highest-value edits:

1. **Lighting:** recover the ceiling locally by about 18 luminance points while cutting back-wall fill by about 50; keep recesses readable without whitening the plaster.
2. **Composition:** reduce the pod's apparent width by roughly 8–10% and reframe so the right bank, laundry/peg station, and trolley read around it; preserve the four-locker/two-bank layout and clear entrance.
3. **Material/content:** return the lower wall and tile palette toward muted teal with varied small tiles, and improve folds, shelf contents, and locker metal edge highlights. Jackets and towels are allowed belongings; no displayed suits are needed.

## Quantitative evidence and judging limits

The render dimensions are 1600×900 and targets are 1672×941. Measurements use corresponding semantic patches expressed in normalized coordinates in `review-12.json`, with 3-pixel sampling. The target's AI camera projection is not treated as a projective blueprint. `DETAIL_FourLockers.png` is context-only for confirming the physical locker count/banks. Scene contacts, portal rays, and Blender state were not used to raise scores.

Exact image paths and the source SHA are recorded in `review-12.json`.
