# 0058 Finite Geometry Audit Scope

## Exact candidate and delta

- Warm candidate: `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend`
- Warm SHA-256: `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`
- Cold candidate: `/workspace/scratch/reactor-refinement-switchgear-label-working-cold/hall_final.blend`
- Cold SHA-256: `b4d3e7afebdf9380bb5bbcd90be90e6fdaed19219690e79f925ae03bb8015c1b`
- Scene delta: `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`.

The 677c→0058 delta is exactly nine existing switchgear circuit FONT curves and the `RH stations east WHITE` mesh, with 1,944 unchanged objects and no added, removed, or unexpected objects.

## Current and cold technical gates

Warm checks: `/workspace/scratch/reactor-refinement-switchgear-label-working/checks.json`, SHA-256 `e530906d95bd30345d3bd66933796012fce4013c40414930ad73ba4f23632ee9`. The record binds source 0058 and reports all 14 checks passing.

Warm control-room check: `/workspace/scratch/reactor-refinement-switchgear-label-working/control-room-check.log`, SHA-256 `b6eb701dcdf54d349ddfbee520baa8d3c3abc60178d88133f017eb9efe2cc618`; result `PASS`.

Cold checks: `/workspace/scratch/reactor-refinement-switchgear-label-working-cold/checks.json`, SHA-256 `c5f849a1d7a2fec12cd2cc3c4d3e2c663e8be6a45968d96f66d0f7c2b6830a7e`. The record binds cold source b4d3 and reports all 14 checks passing.

Cold control-room check: `/workspace/scratch/reactor-refinement-switchgear-label-working-cold/control-room-check.log`, SHA-256 `1030553eeb255af14bb3f91ed39a4ee07c704a6feb2143eb92b29cea9079c514`; result `PASS`.

Cold declared comparison scope: `/workspace/scratch/reactor-refinement-switchgear-label-working-cold/scope.json`, SHA-256 `fcfbeff91d61ff33470c86ab0897d1c66ee5dafef2db97469c50e2d23b784062`. It binds warm source 0058 to cold source b4d3, with 103 declared owned comparisons all true and `pass_check: true`; the declared set includes the corrected white plate and all nine circuit-label curves.

## Limit of this acceptance

Accept issue 140 only for the current finite geometry/control-room scope and the declared 103 owned warm/cold comparisons. This is not full-scene warm/cold equivalence, exhaustive collision testing, rendered readability, or final art acceptance. The exact-source full view13 remains necessary for circuit-label appearance, and all ten full-quality main views remain mandatory before a final review or score.
