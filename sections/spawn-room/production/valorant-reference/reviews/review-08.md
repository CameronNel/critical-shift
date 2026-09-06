# Review 08: Pass 08 renders against target references

Date: 2026-09-07  
Reviewer: Codex independent visual reviewer  
Scale: 0-100 per category. A 90 means genuinely close visual correspondence.

Pass 08 keeps the room architecture and explicit constraints intact, but the shaped-light change overshoots in the wrong places: ceilings are now too dark in all three rooms, while several walls/floors remain brighter than target. Hall's poster headline is clipped again at the top. The 90 gate is not met.

## Scores

| Room | Lighting | Art style | Layout fidelity | Read |
|---|---:|---:|---:|---|
| BRIEFING | 76 | 85 | 87 | Anchors and two-bench/open-portal constraints hold; ceiling is near-black and wall exposure is too high against target. |
| HALL | 73 | 82 | 82 | Corridor remains recognizable, but ceiling is severely underlit, end wall too bright/cool, and poster headline clips at top. |
| LOCKER | 75 | 86 | 88 | Pod, benches, portal and physical locker banks hold; ceiling is dark, tile/back wall split is too bright, and corner framing remains tighter. |

## Quantitative lighting evidence

Pass images are 1600x900; targets are 1672x941. Values below are mean sRGB RGB, luminance `L = 0.2126R + 0.7152G + 0.0722B`, and warmth `R-B`. Rectangles are normalized separately per image to select semantic wall/floor/ceiling patches.

| Room/region | Pass rect → Target rect | Pass RGB / L / warmth | Target RGB / L / warmth | Direction |
|---|---|---|---|---|
| Briefing ceiling | `[.688,.056,.750,.111]` → `[.748,.053,.807,.106]` | 16/15/12 · 14.5 · 3.1 | 55/44/34 · 45.3 · 21.1 | Pass too dark/cool. |
| Briefing upper wall | `[.656,.256,.719,.333]` → `[.748,.213,.807,.287]` | 157/137/113 · 139.6 · 43.8 | 114/90/71 · 93.5 · 43.0 | Pass too bright, warmth matched. |
| Briefing lower wall | `[.650,.567,.713,.633]` → `[.748,.553,.807,.616]` | 100/108/94 · 105.5 · 6.0 | 63/68/58 · 66.1 · 5.0 | Pass too bright, warmth matched. |
| Briefing timber floor | `[.788,.844,.850,.922]` → `[.807,.808,.867,.882]` | 110/72/46 · 78.4 · 64.0 | 101/63/39 · 69.2 · 62.3 | Slightly too bright, warmth matched. |
| Hall ceiling | `[.675,.056,.738,.117]` → `[.658,.053,.718,.112]` | 4/4/4 · 4.1 · 0.0 | 60/51/41 · 52.5 · 19.4 | Pass severely too dark/cool. |
| Hall end wall | `[.531,.389,.581,.444]` → `[.508,.372,.555,.425]` | 155/139/119 · 141.2 · 36.6 | 149/120/91 · 123.9 · 58.1 | Pass too bright/cool; do not add global fill. |
| Hall lower wall | `[.675,.689,.738,.756]` → `[.670,.659,.730,.723]` | 68/80/72 · 76.9 · -4.2 | 81/83/71 · 81.4 · 9.1 | Pass slightly dark/cool. |
| Hall tile floor | `[.500,.844,.563,.922]` → `[.479,.808,.538,.882]` | 151/149/140 · 148.9 · 11.2 | 147/131/112 · 132.8 · 35.3 | Pass too bright/cool. |
| Locker ceiling | `[.469,.111,.531,.167]` → `[.538,.106,.598,.159]` | 53/52/47 · 51.6 · 6.4 | 101/89/75 · 90.4 · 25.7 | Pass too dark/cool. |
| Locker back wall | `[.375,.222,.438,.300]` → `[.419,.213,.478,.287]` | 156/143/127 · 144.3 · 28.4 | 130/118/102 · 119.4 · 28.0 | Pass too bright, warmth matched. |
| Locker lower wall | `[.438,.556,.500,.622]` → `[.419,.531,.478,.595]` | 71/64/52 · 64.8 · 19.2 | 70/76/71 · 74.4 · -0.2 | Pass darker and warmer. |
| Locker tile floor | `[.438,.889,.500,.956]` → `[.508,.850,.568,.914]` | 193/193/188 · 192.2 · 5.4 | 168/151/131 · 153.1 · 37.6 | Pass too bright/cool. |

The direction is local: lift the ceilings with warmer fixture contribution, reduce over-bright walls/floors, and add only modest local fill to dark locker/pod recesses. A global brightening or global warm shift would worsen the measured wall/floor mismatch.

## Remaining edits

### BRIEFING

1. **Lighting:** Lift only ceiling/fixture contribution toward target (pass ceiling L14.5/warmth 3.1 vs target L45.3/warmth 21.1), while reducing wall exposure (pass upper/lower walls are +46/+39 L). Do not globally brighten.
2. **Camera composition:** Retune lens/aim so TV and console proportions approach target without moving architecture, benches or portal.
3. **Art/material:** Reduce repeated broad-leaf plant silhouette and deepen matte variation in wall-note cluster, console, plaster and teal paint; ordinary personal clothing is allowed and no display suits are needed.

### HALL

1. **Camera/content:** Lower or scale the left poster artwork so its headline has target-like top breathing room; Pass 08 visibly clips the first headline line at the top-left poster region, unlike Pass 07. Keep corridor architecture fixed.
2. **Lighting:** Lift ceiling locally (pass L4.1/warmth 0 vs target L52.5/warmth 19.4), reduce end-wall direct exposure (pass L141.2 vs target L123.9), and add modest warm/neutral fill to lower wall/floor. Avoid global brightening.
3. **Art/material:** Warm and texture tile/floor and safety props, then refine poster/update-board typography and plant silhouettes; equipment is present but flatter and cooler than target.

### LOCKER

1. **Lighting:** Lift ceiling locally (pass L51.6/warmth 6.4 vs target L90.4/warmth 25.7), reduce back-wall exposure (+24.9 L) and reduce/warm the over-bright tile (+39.1 L, -32.2 warmth). Add local pod/locker fill instead of a global lift.
2. **Camera composition:** Rebalance corner framing toward target pod/entry-bank proportions while preserving the physical two-bank/four-body arrangement, pod, two benches, clear portal and route. `DETAIL_FourLockers.png` confirms the bank count only.
3. **Art/material:** Restore warm matte tile/locker/towel roughness, vary foliage toward broad camera-facing leaves and keep vents/folds readable. Ordinary jackets/towels remain valid; no display suits.

## Judging limitations

- Corner-vs-target scores use only the three `REFERENCE_*.png` images. `DETAIL_FourLockers.png` is context-only for physical locker layout.
- Pixel regions are semantic patches with separate normalized coordinates because target dimensions differ and AI reference perspective is not projectively consistent.
- The target images are ChatGPT-generated; exact text, graphics and incidental props are style/dressing cues rather than literal geometry requirements.
- User constraints outrank accidental target details: four identical lockers in two banks, no mannequin/display coverall suits, exactly two briefing benches, clear pod, open entrances, matte timber, small bathroom tiles and used-but-maintained materials. Ordinary jackets and towels are authorized.
- Pass 08 was judged from images only; no scene script, geometry or automated contact/route checks were used to increase visual scores.

Exact images reviewed:

- Render BRIEFING: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-08/REFERENCE_BRIEFING.png`
- Target BRIEFING: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/BRIEFING_reference.png`
- Render HALL: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-08/REFERENCE_HALL.png`
- Target HALL: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/HALL_reference.png`
- Render LOCKER: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-08/REFERENCE_LOCKER.png`
- Target LOCKER: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/LOCKER_reference.png`
- Locker context only: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-08/DETAIL_FourLockers.png`
