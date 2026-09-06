# Review 09: Pass 09 renders against target references

Date: 2026-09-07  
Reviewer: Codex independent visual reviewer  
Scale: 0-100 per category. A 90 means genuinely close visual correspondence.

Pass 09 materially improves Pass 08: the Hall poster is readable again, bench timber is more convincingly faded, and Locker dressing/construction is stronger. The 90 gate is not met. Remaining differences are material scene differences rather than tiny AI perspective deviations: local light balance, wall/floor color grade, sparse secondary dressing and camera proportions.

## Scores

| Room | Lighting | Art style | Layout fidelity | Read |
|---|---:|---:|---:|---|
| BRIEFING | 84 | 86 | 88 | Main anchors and constraints hold; walls remain over-bright, ceiling is slightly cool, plant/wall-note density differs, and proportions are still off. |
| HALL | 81 | 85 | 88 | Poster and safety program read well; ceiling/end-wall/floor balance remains off and target operational detail is richer. |
| LOCKER | 82 | 88 | 89 | Pod, two benches, portal and physical four-locker layout hold; tile is too bright/cool, upper wall is bright and recess light needs refinement. |

## Quantitative evidence

Pass images are 1600x900; targets are 1672x941. Values are mean sRGB RGB, luminance `L = 0.2126R + 0.7152G + 0.0722B`, and warmth `R-B`. Regions use separate normalized coordinates for semantic ceiling/wall/floor patches.

| Room/region | Pass rect → Target rect | Pass RGB / L / warmth | Target RGB / L / warmth | Direction |
|---|---|---|---|---|
| Briefing ceiling | `[.688,.056,.750,.111]` → `[.748,.053,.807,.106]` | 52/50/46 · 50.3 · 6.3 | 55/44/34 · 45.3 · 21.1 | Brightness close; pass 14.8 warmth cooler. |
| Briefing upper wall | `[.656,.256,.719,.333]` → `[.748,.213,.807,.287]` | 162/144/123 · 146.3 · 39.0 | 114/90/71 · 93.5 · 43.0 | Pass +52.8 L, warmth similar. |
| Briefing timber floor | `[.788,.844,.850,.922]` → `[.807,.808,.867,.882]` | 110/72/46 · 78.4 · 64.0 | 101/63/39 · 69.2 · 62.3 | Pass +9.2 L, warmth similar. |
| Hall ceiling | `[.675,.056,.738,.117]` → `[.658,.053,.718,.112]` | 35/35/33 · 34.7 · 2.0 | 60/51/41 · 52.5 · 19.4 | Pass -17.8 L and -17.4 warmth. |
| Hall end wall | `[.531,.389,.581,.444]` → `[.508,.372,.555,.425]` | 153/139/117 · 140.1 · 36.0 | 149/120/91 · 123.9 · 58.1 | Pass +16.2 L and -22.1 warmth; do not globally fill. |
| Hall tile floor | `[.500,.844,.563,.922]` → `[.479,.808,.538,.882]` | 151/149/140 · 148.9 · 11.2 | 147/131/112 · 132.8 · 35.3 | Pass +16.1 L and -24.1 warmth. |
| Locker ceiling | `[.469,.111,.531,.167]` → `[.538,.106,.598,.159]` | 76/74/69 · 73.9 · 6.9 | 101/89/75 · 90.4 · 25.7 | Pass -16.5 L and -18.8 warmth. |
| Locker back wall | `[.375,.222,.438,.300]` → `[.419,.213,.478,.287]` | 162/149/133 · 150.6 · 28.5 | 130/118/102 · 119.4 · 28.0 | Pass +31.2 L, warmth matched. |
| Locker tile floor | `[.438,.889,.500,.956]` → `[.508,.850,.568,.914]` | 193/191/185 · 190.9 · 8.4 | 168/151/131 · 153.1 · 37.6 | Pass +37.8 L and -29.2 warmth. |

These measurements support another shaped correction, not global brightening: warm/lift ceilings modestly, reduce over-bright walls/floors, and add local recess fill only where needed.

## Remaining edits

### BRIEFING

1. **Lighting:** Keep ceiling brightness near target but warm its fill (pass L50.3/warmth 6.3 vs target L45.3/warmth 21.1), and reduce wall exposure by the measured +53 L without darkening benches or console.
2. **Layout:** Refine camera aim/lens only enough to match TV, console and plant proportions; preserve fixed architecture, exactly two benches, rug and open portal.
3. **Art/material:** Replace broad repeated right-plant leaves with a varied target-like cascade, and deepen sparse wall-note cluster, plaster/wainscot wear and console detail.

### HALL

1. **Lighting:** Warm/lift ceiling locally (pass L34.7/warmth 2.0 vs target L52.5/warmth 19.4), reduce end-wall/floor direct exposure and add warmer bounce. Do not globally brighten.
2. **Layout:** Keep the repaired headline fully readable and tune poster, first-aid case, extinguisher and pipe proportions toward target placements while preserving shell, open entrances and route.
3. **Art/material:** Add target-level roughness and micro-detail to cart, update board, safety props and plants, and warm the neutral gray tile toward the target's maintained amber floor.

### LOCKER

1. **Lighting:** Warm/lift ceiling modestly (pass L73.9/warmth 6.9 vs target L90.4/warmth 25.7), reduce upper-wall exposure (+31 L), and lower/warm near-white tile (+37.8 L, -29.2 warmth) while filling pod/locker recesses locally.
2. **Layout:** Nudge corner framing toward target pod/entry-bank proportions without moving pod, clear portal, two benches or physical two-bank/four-locker arrangement. `DETAIL_FourLockers.png` confirms four bodies.
3. **Art/material:** Keep improved faded bench timber and locker construction, then add warmer matte tile/locker/towel roughness, fuller varied plant cascades and clearer peg/laundry details. Ordinary jackets/towels are allowed; no display suits.

## Judging limitations

- Corner-vs-target scores use only the three `REFERENCE_*.png` images. `DETAIL_FourLockers.png` is context-only for physical locker layout.
- Pixel evidence uses separate normalized regions because target dimensions differ and AI reference perspective is not projectively consistent. Regions are semantic material patches, not exact pixel correspondences.
- Target graphics/text and incidental props are style cues, not literal geometry requirements.
- User constraints outrank target drift: four identical lockers in two banks, no mannequin/display coverall suits, exactly two briefing benches, clear pod, open entrances, matte timber, small bathroom tiles and used-but-maintained materials. Ordinary jackets and towels are authorized.
- Pass 09 was judged from images only; no scene script, geometry or automated contact/route checks were used to increase visual scores.

Exact images reviewed:

- Render BRIEFING: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-09/REFERENCE_BRIEFING.png`
- Target BRIEFING: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/BRIEFING_reference.png`
- Render HALL: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-09/REFERENCE_HALL.png`
- Target HALL: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/HALL_reference.png`
- Render LOCKER: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-09/REFERENCE_LOCKER.png`
- Target LOCKER: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/LOCKER_reference.png`
- Locker context only: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-09/DETAIL_FourLockers.png`
