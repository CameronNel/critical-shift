# 0058 Switchgear Circuit Label Geometry Preflight

## Scope and result

This is a read-only preflight of the frozen owned label correction, before the exact-camera full-quality view13. It covers only the nine circuit-label plates and glyphs, the declared source delta, and the corresponding declared cold-scope comparisons. It is not a rendered legibility review, production-pipeline acceptance, whole-scene equivalence claim, or source promotion.

No obvious geometry or material-placement blocker is present in the reviewed module and records. The nine existing white strip meshes are enlarged vertically to 90 mm and each existing `C01`–`C09` curve is set to 62 mm, centered on its own strip, and assigned the existing matte label-ink material. The measured world bounds keep each glyph wholly within its plate. The correction record reports 216 selected strip vertices, all unselected strip vertices unchanged, topology and material graphs unchanged, and nine per-label bounds passing the plate-margin assertions.

The exact-camera 1280×720 view13 remains mandatory to confirm rendered readability, strip association, and absence of visual clipping. No artistic criterion is accepted by this preflight.

## Candidate and owned module identities

- Warm candidate: `/workspace/scratch/reactor-refinement-switchgear-label-working/hall_final.blend`
- Warm source SHA-256: `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`
- Cold candidate: `/workspace/scratch/reactor-refinement-switchgear-label-working-cold/hall_final.blend`
- Cold source SHA-256: `b4d3e7afebdf9380bb5bbcd90be90e6fdaed19219690e79f925ae03bb8015c1b`
- Owned module: `/workspace/scratch/rh_switchgear_circuit_label_fit.py`
- Owned module SHA-256: `3433b172031c25ebea9a4c6c0fbe487e948d87f54a6af27d6895cb6e0efd4fc4`
- Production module copy: `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/rh_switchgear_circuit_label_fit.py`
- Production module SHA-256: `3433b172031c25ebea9a4c6c0fbe487e948d87f54a6af27d6895cb6e0efd4fc4` (byte-identical to the owned module)

## Measured correction record and delta

- Correction record: `/workspace/scratch/reactor-refinement-switchgear-label-working/correction-stage.json`
- Correction-record SHA-256: `3480fd23ee17a333753ee34a2139d36e915d72db32f9a151fdc5cb2f7446449f`
- Scene delta: `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`
- Scene-delta SHA-256: `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`

The declared delta is exactly nine existing circuit FONT objects and `RH stations east WHITE` changed, 1,944 objects unchanged, with no additions, removals, or unexpected changes. Glyph bounds in the correction record range from 43.4 mm in height to about 102.3 mm in width. Against the 90 mm plate height and 200 mm plate width, the measured glyphs leave at least 23 mm vertical margin and about 48 mm horizontal margin per side. The module asserts that all selected vertices belong to the intended strips, that unselected strip vertices remain bitwise unchanged, and that the glyph fronts remain in front of the plate faces.

## Declared cold comparisons

- Cold scope record: `/workspace/scratch/reactor-refinement-switchgear-label-working-cold/scope.json`
- Cold scope SHA-256: `fcfbeff91d61ff33470c86ab0897d1c66ee5dafef2db97469c50e2d23b784062`

The record binds warm source `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714` to cold source `b4d3e7afebdf9380bb5bbcd90be90e6fdaed19219690e79f925ae03bb8015c1b`. It declares 103 owned comparisons, all `true`, with `pass_check: true`; that scope includes the switchgear circuit-label correction and other named owned corrections. This result is limited to those declared comparisons and does not establish full-scene warm/cold equivalence or completion of the separate warm/cold 14-check and control-room gates.

## Review gate

Proceed to the exact-source view13 only after root confirms the separate warm/cold technical gates and control-room checks. Review all nine glyphs at native resolution for legibility, contrast, and strip association. Keep all issue dispositions and production promotion pending until the full-quality pixels and technical gates are independently accepted.
