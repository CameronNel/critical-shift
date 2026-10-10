# 870b withdrawal of issue 9 acceptance: generator plaque visibility

## Receiving source and pixel evidence

- Candidate: `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`.
- Intended west-wall main10 original: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/10/10_walls_west_access.png`, SHA-256 `e4a661840a636a5c9d4e962a27e562892ef7b8e06b89a78497ba083b08c316d0`.
- Main10 manifest: `/workspace/scratch/reactor-refinement-bearing-lit-working/standard-720p/green/10/render_manifest.json`, SHA-256 `af2157a0a31be7df9bd7f430041eb10048a66e327d8e7c49e6bbcd2775691b1f`.
- Canonical renderer: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/render_detail_views.py`, SHA-256 `06d0ac982dd1a217fa1fae8448633299dba993e391627979848dc0e39608b8ef`.
- Candidate signage audit: `/workspace/scratch/reactor-refinement-bearing-lit-working/audit.json`, SHA-256 `d4db2d53e22af7cd6846a6e1f9993c83a8f20b0994d4d34a2e8908215d1067f2`.

## Finding and disposition

Withdraw the 870b bounded carry for issue #9, “STANDBY GENERATOR plaque obstructed.” In the intended full10 west-wall image, the diagonal R2 piping conduit visibly crosses the plaque face and obscures part of the `GENERATOR` lettering. The source-bound camera audit corroborates the rendered overlap: 94 of 107 projected glyph samples are clear, while 13 are blocked by `RH services R2 PIPING conduit GALV`. This is a confirmed physical visibility defect; the fact that the wording remains partly decipherable does not satisfy an unobstructed plaque criterion.

The prior 0058 accepted evidence remains nested in the issue record as historical evidence. It does not establish the 870b placement. Issue #9 returns to pending until a corrected source and fresh intended-view pixels establish clear lettering and plate visibility. The broader physical-sign audit, issue #139, also remains pending.

This report withdraws only the 870b acceptance of #9. It does not assign a score or change unrelated issue dispositions.
