# C84 native17 state-bar direction review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`

## Finding

The board title, threshold legends, ten bars, and current status are visible. The current C84 orange and red state renders show a reversed margin fill: the printed numeric scale reads 0 to 100 percent from left to right, but the orange state lights the rightmost five segments and the critical state lights only the rightmost segment. Lower stability margin therefore appears at the high end of the displayed scale.

The source explains the reversal. In `scripts/rh_refine.py`, bars are generated at increasing wall coordinate `u = u - 1.40 + i*.285` and material `LEVELi`; drivers enable level `i` when `s >= (i+1)/10`. The wall lettering is oriented with local X opposite increasing wall-u, so increasing u maps to screen-left. Consequently the low-index segments that light at low values appear on the screen-right. This conflicts with the legible 0–100% scale.

The board's previous obstruction finding is resolved, but the board cannot receive a whole-item acceptance while this state-to-scale relation is backwards. Keep #7 pending until the saved candidate maps the low-margin/critical segments to the low end of the printed scale, and full-quality direct frames confirm green, warning, and critical behavior. The independent text-family scope in #131 and room-wide visibility audit #139 remain separate and open.

## Exact image evidence

- C84 orange state: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/orange/17_board_direct.png`, SHA-256 `3172f826c56af87e6dfe09b0b20b5e0974423e69552659e389b9b1daf54fc388`.
- C84 red state: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/red/17_board_direct.png`, SHA-256 `2138fe6f9210a98d5d8a217375b0a03f12a0e9c281141356daa308f99e2254c3`.
- C84 green state: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/17_board_direct.png`, SHA-256 `b5d8bcdc9c039a7e7437baf3f933dee17a4978bcc08657a3c61fe22bba7edc4c`.

These are native 640×360/96-sample direct views. The orange/red evidence establishes the current direction defect; it does not establish a corrected candidate.
