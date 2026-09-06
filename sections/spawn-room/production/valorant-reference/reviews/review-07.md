# Review 07: Pass 07 renders against target references

Date: 2026-09-06  
Reviewer: Codex independent visual reviewer  
Scale: 0-100 per category. A 90 means genuinely close visual correspondence.

Pass 07 improves locker construction and dressing. The supplementary entrance view verifies two physical banks of two matching locker bodies. The corner renders still fall below the 90 gate: Briefing needs camera/material/light refinement, Hall needs prop scale and richer detail, and Locker needs camera balance and brighter recesses.

## Scores

| Room | Lighting | Art style | Layout fidelity | Read |
|---|---:|---:|---:|---|
| BRIEFING | 88 | 87 | 88 | Main anchors read; camera proportions, foliage, warm fill and wall-note/material density remain short. |
| HALL | 84 | 84 | 86 | Headline is now readable; poster and safety props are larger/left-shifted than target, and distant light/prop detail is simpler. |
| LOCKER | 85 | 87 | 89 | Pod, benches, portal and two-bank four-locker layout hold; framing, recess lighting and material/foliage finish remain. |

## BRIEFING

TV, briefing boards, discipline graphic, console, exactly two benches, rug and open portal are clear. Compared with target, the TV/console proportions are lower/right-shifted, the right foliage is broad/repeated, and wall-note/material density is lighter.

Three remaining edits:

1. **Camera/framing — layout:** Tune lens/aim toward target proportions. Pass TV is about x355-690/y245-485 versus target x365-730/y195-465; pass console x85-395 versus target x40-320. Keep architecture, benches and portal fixed.
2. **Lighting:** Add warmer, slightly brighter fill to console, left wall and lower teal paint while retaining ceiling pools and bench contact shadows.
3. **Actual content/material — art style:** Narrow/vary the right plant so notes remain readable, then add target-level texture to console, notes, plaster, wainscot and timber. Exactly two benches remain; ordinary personal clothing is allowed.

## HALL

The corridor axis, open route, briefing opening, poster headline and safety program read. Pass poster and right safety props remain larger/left-shifted than target. This is a scale/placement issue, not the earlier headline clipping issue.

Three remaining edits:

1. **Camera/framing + prop placement — layout:** Rebalance poster and safety prop scale. Pass poster is about x145-400 versus target x75-300; first-aid x1330-1485 versus target x1375-1525; extinguisher x1345-1465 versus target x1430-1515. Keep readable headline, edge-held pipe and open route.
2. **Lighting:** Warm and lift distant corridor fill so end door, plaster and tile approach target readability while preserving dark reveals and practical pools.
3. **Actual content/material — art style:** Add detail to trolley labels/mechanics, update board, safety labels and shelf/plant dressing, with broader camera-facing foliage and restrained worn matte roughness.

## LOCKER

The corner view preserves the pod, two benches, clear portal and locker room. `DETAIL_FourLockers.png` confirms two physical banks of two matching locker bodies, so the four-locker requirement is met. Remaining gaps are camera scale, dark recesses and simpler foliage/material detail.

Three remaining edits:

1. **Camera/framing — layout:** Widen/re-aim toward target proportions. Pass bank is about x40-475 and pod x875-1420; target bank is x0-335 and pod x960-1505. Preserve architecture, two benches, pod and clear portal.
2. **Lighting:** Add warm fill to locker fronts and pod recesses so side vents, folds, towels and tiles remain readable while keeping soft practical highlights/contact shadows.
3. **Actual content/material — art style:** Keep the verified four-body/two-bank layout, vary plant leaf orientation, and add roughness/edge wear to lockers, benches, small tiles, laundry station and personal towels. Add no mannequin or displayed coverall suits.

## Pixel-region evidence

Coordinates are approximate visual measurements in the 1600x900 Pass 07 corner renders.

- BRIEFING: pass TV about x355-690/y245-485; target TV about x365-730/y195-465. Pass console about x85-395; target about x40-320. Pass plant about x1270-1460; target about x1360-1530. These are scale/aim differences; the plant is shifted/oversized rather than clipped.
- HALL: pass poster about x145-400/y0-735 with headline readable from y100; target about x75-300/y0-655. Pass first-aid about x1330-1485/y270-505 and extinguisher about x1345-1465/y525-700; target about x1375-1525/y270-540 and x1430-1515/y565-760. Both pass props are fully visible. Pass pipe about x1510-1595 is edge-held.
- LOCKER: pass foreground bank about x40-475/y195-760 and pod about x875-1420/y45-875; target comparable bank about x0-335 and pod about x960-1505. `DETAIL_FourLockers.png` is context-only and visibly confirms two banks of two matching bodies.

## Judging limitations

- Corner-vs-target scores use only the three `REFERENCE_*.png` images. `DETAIL_FourLockers.png` verifies physical layout only and does not replace the corner comparison.
- Pixel evidence is approximate visual measurement from 1600x900 renders and separates scale/aim mismatch from missing or clipped content.
- The target images are ChatGPT-generated. Text, exact poster graphics, portraits and incidental props are style/dressing cues rather than literal geometry requirements.
- User constraints outrank accidental target details: preserve four identical lockers near entry in two physical banks, no mannequin/display coverall suits, exactly two briefing benches, a clear pod, open room entrances, matte timber, small bathroom tiles and used-but-maintained materials. Ordinary jackets and towels are authorized personal belongings.
- Pass-07 was judged from images only; no scene script, geometry, contact-check output or passage-ray output was used to increase visual scores.

Exact images reviewed:

- Render BRIEFING: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-07/REFERENCE_BRIEFING.png`
- Target BRIEFING: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/BRIEFING_reference.png`
- Render HALL: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-07/REFERENCE_HALL.png`
- Target HALL: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/HALL_reference.png`
- Render LOCKER: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-07/REFERENCE_LOCKER.png`
- Target LOCKER: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/targets/LOCKER_reference.png`
- Locker layout context only: `C:/Users/Camer/Games/critical-shift/worktrees/spawn-reference-rebuild/sections/spawn-room/production/valorant-reference/pass-07/DETAIL_FourLockers.png`
