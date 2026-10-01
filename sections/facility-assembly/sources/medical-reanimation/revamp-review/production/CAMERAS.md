# Fixed 600p medical evidence cameras

Renderer: `render_overhaul.py`. All new evidence is 1067 x 600, Cycles 24 samples, denoised, AgX Medium High Contrast. Actual transforms and focal lengths are in each render manifest. Camera framing is fixed between comparisons.

Gameplay checks: ENTRY / CAM_ENTRY, REVERSE / CAM_REVERSE, PINCH / MED_ROUTE. Functional checks: HERO_OCRU / CAM_HERO; HERO_DECON; HERO_RECOVERY; HERO_SUPPLIES; HERO_WASH; HERO_CABINET; HERO_RESTART; HERO_CARTRIDGES; HERO_RESERVE; HERO_CART. Material close-ups: DETAIL_OCRU and DETAIL_SUPPLIES. Four whole-footprint corner cutaways and four wall elevations complete the 24 labelled useful views.

Cutaways temporarily hide ceiling and nearest wall planes to expose the entire room. Hero and gameplay renders use the saved authored lights. HIDDEN_BAG alone is an explicitly labelled owner-inspection view with a temporary 2 W area fill; it is never saved in the source. Review labels are camera-attached geometry and never saved into the source.

Style comparisons at 600p begin with style-slice-600. Detail camera baselines begin with style-slice-4. Formal full-room review begins after slice acceptance.

Cycle-2 correction: PINCH now uses MED_ROUTE because inherited CAM_PINCH aimed at the bed and did not show circulation. Corner projection is orthographic with a deterministic full-footprint fit, avoiding oversized empty margins at 600p. These views establish new comparison baselines; all other poses and lenses remain fixed.

Final stability evidence must refer to the current saved source and complete render manifests. The final comparison passes cycles 16 HOT and 17 COLD: all 24 decoded RGB images and camera matrices match exactly, with the same source and renderer hashes. The historical cycle 10/11 comparison matched decoded RGB and camera transforms exactly, but that source failed small-part contact review and cannot establish final acceptance.

Interrupted cycle14 is incomplete (23 of24 actual PNGs) and is excluded from acceptance/stability. Current renderer requires each real1067×600 PNG before adding its camera checkpoint and rejects an incomplete full batch.

Cycle 15 is also incomplete (19/24 real PNGs). Its actual cancellation test raised a render-cancelled error, exited 1 and kept `complete: false`. It is excluded from full-cycle and stability counts.
