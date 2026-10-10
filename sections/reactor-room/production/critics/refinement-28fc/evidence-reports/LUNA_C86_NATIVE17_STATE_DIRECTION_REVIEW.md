# C86 stability board state and visibility review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle86/hall_final.blend`  
**Source SHA-256:** `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`

## Current image evidence

The three direct board frames are native 640×360 Cycles renders at 96 maximum samples, 32 minimum adaptive samples, threshold 0.015, CPU, OIDN, path guiding, and fixed AgX Medium High Contrast at exposure 0. Their separate manifests and PNG hashes are:

| State | Image | SHA-256 | Visible fill |
|---|---|---|---|
| Green 1.0 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c86/native-signs/green/17_board_direct.png` | `b1aef6f7789d47146ec2ad4850e7a8dc106adfea93307986952614cb4feec69e` | All ten cells green; NORMAL active |
| Orange 0.5 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c86/native-signs/orange/17_board_direct.png` | `1b70e13c78a87b913f0d83bd91c309bb99b376071dcc67ad41464e9dc0fcac54` | Five leftmost cells amber; WARNING active |
| Red 0.1 | `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c86/native-signs/red/17_board_direct.png` | `7cb70f23a3038884e6da7c4a4720f53fe181f249abf8dbbfae9f120e39d1d97d` | Leftmost cell red; CRITICAL active |

The three images show the full REACTOR STABILITY board face. Its title, “REACTOR STABILITY MARGIN” caption, all ten scale cells, 0/25/50/75/100% labels and active state wordmark are legible. Green fills all ten cells; orange fills the first five from the left; red fills only the leftmost cell. This confirms the corrected severity progression in the rendered result. I find no board-face obstruction in the direct view.

The earlier C84 defect was that the orange and red fills advanced from the wrong end. The C85 correction reordered the physical cells; C86 changes only the seated oil-film mesh relative to C85. The C86 state images therefore directly verify the corrected board and its readability in the current candidate. They close #7. This decision is limited to the stability board and its three state frames; it does not close room-wide typography or unrelated signage criteria.
