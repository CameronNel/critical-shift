# Independent R51 bounded code and evidence review

## Scope

Read-only review of the canonical and archived R51 builder setting, main/detail render manifest handling, cold comparison, and selected-revision HANDOFF. This is a workflow check, not runtime certification or art acceptance.

## Findings

No new code defect found in the reviewed R51 changes. The archived `history/R51_build.py` explicitly saves `scene.cycles.use_light_tree=False` into the native scene. The current R51 main manifest records `use_light_tree: false`; the canonical main and detail renderers record the actual scene flag in each settings map. Both renderers normalize a missing historical manifest flag to the prior enabled default, so a prior cache is reusable only when it matches the currently loaded scene setting; an enabled/fieldless cache is rejected against R51's disabled native setting. The cold comparison requires exact warm/cold settings equality for both the 21 main cameras and D02/D03, so a light-tree mismatch cannot pass the own-revision pixel proof.

The archived R51 builder includes the prior revision-output collision guard. The existing `workflow_guard_checks_R50.json` remains evidence for the earlier canonical guard remediation only; I did not claim to rerun those checks for R51. R50's archived builder remains frozen.

The HANDOFF identifies R51 and documents its light-tree-disabled setting and R49-to-R51 sampling-method change. I inspected the complete `production/comparison_R49_R51.json`: it contains all 21 paired main views and both supplemental details, marks every pose/optics pair equal, verifies the only settings delta as `use_light_tree: true → false`, and records all other settings equal. I independently recomputed the D02/D03 PNG hashes against its supplemental records; both match. The pair artifact reports no material regression. This closes the previously pending cross-revision comparison evidence.

## Actual diagnostic confirmation

I opened the actual R49 W02, incomplete R50 W02, packaged [R50_W02_no_lighttree.png](../diagnostics/R50_W02_no_lighttree.png), and first actual R51 W02. The diagnostic image SHA-256 `d1a62827d535c4e2fdd790bd8ad42cac041a916077266c2fd3fd31c6185ef3de` matches `sampling_diagnostic_R50.json`, which records the enabled-to-disabled flag change and the unchanged 24-sample settings. R51's recorded false light-tree flag is consistent with the restored receiving-wall light pool and portal-jamb readability in the actual R51 image. This supports the stated sampling-method provenance; it does not establish material-only causality or complete-cycle acceptance.
