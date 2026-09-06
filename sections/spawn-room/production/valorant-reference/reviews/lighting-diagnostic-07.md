# Lighting diagnostic: Pass 07 versus fixed targets

This is a quantitative lighting audit, not a scoring pass. It samples unobstructed-looking wall, floor and ceiling patches from the three Pass 07 corner renders and semantically corresponding patches in the fixed targets. Regions are expressed in normalized coordinates because Pass 07 is 1600x900 and each target is 1672x941. Mean RGB and luminance are 8-bit sRGB averages; `Warm` is mean R minus B. Values are approximate because the cameras do not map the same material to identical coordinates.

## Measurements

### BRIEFING

| Region | Pass normalized rect | Target normalized rect | Pass RGB / L / Warm | Target RGB / L / Warm |
|---|---|---|---|---|
| Ceiling | `[.688,.056,.750,.111]` | `[.748,.053,.807,.106]` | 157/140/116 · 142 · 41 | 55/44/34 · 45 · 21 |
| Upper wall | `[.656,.256,.719,.333]` | `[.748,.213,.807,.287]` | 185/162/135 · 165 · 50 | 114/90/71 · 94 · 43 |
| Lower wall | `[.650,.567,.713,.633]` | `[.748,.553,.807,.616]` | 112/109/79 · 108 · 33 | 63/68/58 · 66 · 5 |
| Bare timber floor | `[.788,.844,.850,.922]` | `[.807,.808,.867,.882]` | 77/34/1 · 41 · 77 | 101/63/39 · 69 · 62 |

Pass walls and ceiling are much brighter than target (+41 to +96 luminance), while its sampled timber floor is darker and more orange (+15 warmth). The remaining Briefing issue is contrast/exposure balance across surfaces, with a smaller warmth/saturation component. Reduce broad wall/ceiling exposure, lift the floor/console region locally, and preserve warm fixture pools rather than applying a global warm fill.

### HALL

| Region | Pass normalized rect | Target normalized rect | Pass RGB / L / Warm | Target RGB / L / Warm |
|---|---|---|---|---|
| Ceiling | `[.675,.056,.738,.117]` | `[.658,.053,.718,.112]` | 115/104/86 · 105 · 29 | 60/51/41 · 53 · 19 |
| End wall | `[.531,.311,.581,.367]` | `[.508,.298,.556,.351]` | 93/78/58 · 79 · 35 | 105/82/60 · 86 · 45 |
| Lower wall | `[.675,.689,.738,.756]` | `[.670,.659,.729,.723]` | 74/73/52 · 72 · 22 | 81/83/71 · 81 · 9 |
| Tile floor | `[.500,.844,.563,.922]` | `[.478,.808,.538,.882]` | 139/119/87 · 121 · 52 | 147/131/112 · 133 · 35 |

Hall does not need a global brightness or warmth increase. The sampled ceiling is already much brighter than target (+53 luminance), while the end wall and floor are slightly darker (-6 and -12 luminance) and more orange (+10 and +16 warmth). Lower overhead/near-camera exposure, add restrained neutral-to-warm fill toward the end wall and floor, and reduce the orange bias in the tile/wall bounce. This preserves practical pools without flattening the corridor.

### LOCKER

| Region | Pass normalized rect | Target normalized rect | Pass RGB / L / Warm | Target RGB / L / Warm |
|---|---|---|---|---|
| Ceiling | `[.469,.111,.531,.167]` | `[.538,.106,.598,.159]` | 155/144/125 · 145 · 30 | 101/89/75 · 90 · 26 |
| Back wall | `[.375,.222,.438,.300]` | `[.419,.213,.478,.287]` | 187/170/149 · 172 · 38 | 130/118/102 · 119 · 28 |
| Lower wall | `[.438,.556,.500,.622]` | `[.419,.531,.478,.595]` | 96/79/54 · 81 · 42 | 70/76/71 · 74 · 0 |
| Tile floor | `[.438,.889,.500,.956]` | `[.508,.850,.568,.914]` | 202/186/163 · 187 · 40 | 168/151/131 · 153 · 38 |

Locker is broadly over-bright in the sampled ceiling, back wall and tile (+34 to +55 luminance), with similar floor warmth and a warmer lower-wall sample. Reduce broad overhead/floor exposure and use local warm bounce in the locker and pod recesses so the dark geometry is readable without making the pale tile and ceiling brighter. The main gap is brightness/contrast, not color temperature.

## Direction for the next lighting edit

- Briefing: lower wall/ceiling exposure, lift floor/console locally, and keep warm fixture pools. Avoid a global warm or bright pass.
- Hall: lower the already-bright ceiling, lift the distant end wall/floor modestly, and neutralize excessive orange bounce. The end wall is not a reason for a global fill increase.
- Locker: lower broad ceiling/back-wall/tile exposure, then add localized fill to locker/pod recesses. Keep floor warmth close to target.

The samples support shaped lighting and exposure balancing rather than one shared temperature or brightness adjustment. These measurements are diagnostic only; no review score is changed here.

Exact sources:

- Pass 07 renders: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-07/REFERENCE_BRIEFING.png`, `REFERENCE_HALL.png`, `REFERENCE_LOCKER.png`
- Fixed targets: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/BRIEFING_reference.png`, `HALL_reference.png`, `LOCKER_reference.png`
