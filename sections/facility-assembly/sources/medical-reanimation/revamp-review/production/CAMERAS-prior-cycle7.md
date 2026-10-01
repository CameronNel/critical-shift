# Fixed 600p medical evidence cameras

Renderer: `render_overhaul.py`. All new evidence is 1067 x 600, Cycles 24 samples, denoised, AgX Medium High Contrast. Actual transforms and focal lengths are in each render manifest. Camera framing is fixed between comparisons.

Gameplay checks: ENTRY / CAM_ENTRY, REVERSE / CAM_REVERSE, PINCH / MED_ROUTE. Functional checks: HERO_OCRU / CAM_HERO; HERO_DECON; HERO_RECOVERY; HERO_SUPPLIES; HERO_WASH; HERO_CABINET; HERO_RESTART; HERO_CARTRIDGES; HERO_RESERVE; HERO_CART. Material close-ups: DETAIL_OCRU and DETAIL_SUPPLIES. Four whole-footprint corner cutaways and four wall elevations complete the 24 labelled useful views.

Cutaways temporarily hide ceiling and nearest wall planes to expose the entire room. Hero and gameplay renders use the saved authored lights. HIDDEN_BAG alone is an explicitly labelled owner-inspection view with a temporary 2 W area fill; it is never saved in the source. Review labels are camera-attached geometry and never saved into the source.

Style comparisons at 600p begin with style-slice-600. Detail camera baselines begin with style-slice-4. Formal full-room review begins after slice acceptance.

Cycle-2 correction: PINCH now uses MED_ROUTE because inherited CAM_PINCH aimed at the bed and did not show circulation. Corner projection is orthographic with a deterministic full-footprint fit, avoiding oversized empty margins at 600p. These views establish new comparison baselines; all other poses and lenses remain fixed.

Final source8c353ae9: cycle6 hot append and cycle7 full-file cold open retain all24 actual camera matrices, lenses, orthographic scales, labels, visibility adjustments and production lighting. All24 decoded RGB images match exactly (zero maximum difference). PNG bytes differ in Date, RenderTime, File and Cycles timing metadata only. See `cold-render-comparison.json`.
