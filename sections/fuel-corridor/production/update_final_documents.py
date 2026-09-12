"""Reconcile current delivery notes while retaining historical audit records."""
from pathlib import Path
r=Path(__file__).resolve().parent.parent
def prepend(name,text):
 p=r/name;s=p.read_text(encoding='utf-8')
 if text not in s:p.write_text(text+'\n\n---\n\n'+s,encoding='utf-8')
prepend('production/FULL_CYCLES.md','''# Resumed final-pass ledger

Current authority: strict above90 in every relevant category, independent Luna. Historical two-reviewer records below are retained.

| Revision | Evidence and result | Correction-cycle credit |
|---|---|---|
| Interrupted full04 | Inherited partial images; not complete | None |
| final-F00-inherited | Fresh complete16-view review of eng12/walk02 corrections following full03; Luna rejected floor artifact, hierarchy, support and source reproducibility | Cycle3 completed; rejected |
| final-F01–F02 | CPU-only; F01 rejected, F02 support/geometry/source PASS | None |
| final-F03 | CPU PASS; stopped after2 images for known art corrections; PARTIAL.json retained | None |
| final-F04 | CPU PASS,8 targeted previews; reactor header contrast rejected | None |
| final-F05 | Complete16 fixed views at1440×960/32 samples; Luna17 categories91–94,16 views92–95; cold/player condition pending | Cycle4 completed |
| final-F05-cold | Canonical repeat of16 fixed poses; C08 strict numeric comparison exception under investigation | Stability evidence, no invented correction-cycle credit |

Four actual correction/review cycles follow the full01 baseline: full02, full03, final-F00 and final-F05. F05 and its canonical repeat are the final two complete visual passes of one corrected artifact, not two distinct correction revisions. Final acceptance and repository delivery are recorded in FINAL_PASS.md after checks complete. The ledger below is historical.''')
prepend('production/FINAL_PASS.md','''# Current F05 final-pass result

F05 complete1440×960/32-sample pack passes independent Luna:17 categories91–94 and16 fixed views92–95. No remaining concrete visual defect identified. Final acceptance remains conditional on canonical cold and twelve player-eye evidence. The canonical cold16 is complete; fifteen views pass the strict max2/255 comparison, while C08 max7/255 is being investigated. No numeric PASS is claimed for that comparison.

Canonical SHA256: f11dc1c5210f0d7c0552db0aafc1148724b54ef6beb0ce6abc6e9d0e42c85c6b. The promoted file exactly matches the reviewed checkpoint:7979 objects,34 materials,16 cameras,3 packed images,0 libraries. Fresh canonical open succeeds. Factory-empty source replay matches all objects/world geometry; separate node/material/UV/packed-texture replay matches. Geometry, support, routes, handoff and branch tests pass. The39-state gate replay contains only zero-depth tangencies, no penetrating obstruction. These finite checks are not an engine controller or whole-map validation.

## Art and readability corrections

F00 was rejected for the black overlapping floor patch, competing foreground reactor board, SERVICE-dominated entry, hidden WASTE advance cue, washed-out reactor header, sparse door leaves and dominant motor light. All rejected evidence remains.

F04 removed the redundant crossing panel, moved CLEAN into its approach sightline, moved WASTE before its turn with the correct arrow, and added F02/REACTOR freight advance identity. Primary lettering gained consistent weight. Reactor leaves gained larger bolted access panels and localized contact wear. Motor task lighting was restrained. Eight previews exposed remaining header contrast failure; these were not approved or counted as a full cycle.

F05 adds dedicated near-black, fully rough header ink with zero specular and consistent0.18m header lettering. Fixed cameras and connection contracts remain unchanged. Source and scene are frozen pending final evidence.''')
prepend('production/technical_audit.md','''# Current technical evidence — final-F05

The slice report below is historical. Current evidence/final-pass/F05-technical.json is PASS. See F05-source-replay.json, F05-material-replay.json, F05-branch-handoff.json, F05-engineering-motion.json and delivery-survey.json. Canonical SHA256: f11dc1c5210f0d7c0552db0aafc1148724b54ef6beb0ce6abc6e9d0e42c85c6b. Full render settings are1440×960,32 samples,16 frozen cameras. Independent Luna interpretation is in critics/final-pass/luna-f05-final-visual.md. Final cold numeric exception is explicitly tracked in FINAL_PASS.md; no blanket final acceptance yet.''')
prepend('CONTINUE.md','''# Current ownership and authority

Older continuation notes below are historical. Current isolated worktree is fuel-corridor-final, branch codex/fuel-corridor-final-20260911. Read production/TASK_STATE.md and production/FINAL_PASS.md. Do not act on the older3598 worktree or spawn its historical Astra reviewer. The resumed user requires strict Valorant, no teal, independent Luna and every relevant score above90.''')
print('Current notes reconciled; historical evidence retained.')
