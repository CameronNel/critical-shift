# Compact shift objectives,19 October2026

Branch `codex/compact-shift-objectives-20261019`, based on mixed-probe
checkpoint4848041a. Primary author Codex. Independent ultra reviewer
`audit_gameplay_integration` identified a concrete usability gap: hiding the
control panel removes the current countdown, authored upcoming-demand warning
and settled missed-window information. These existing projections matter while
the player is moving and operating equipment.

This bounded presentation change formats those read-only projections in a pure
canonical Presentation helper, linked exactly into offline tests. The hidden
panel retains a compact title/current/countdown, upcoming warning when authored,
and latest missed-window shortfall/count. The full panel uses the same current
and warning formatter. No timer, quota, control or mutation owner changes; no
input/UI framework, package, art or assembly edge is added. S08 and pure
projection/source-link checks apply; no serialized consumer is removed.

Seven targeted tests passed on their first run using real WorldSession views
across warning/window/early-terminal/pause boundaries, latest settled misses and
frozen old snapshots. Repeated reads do not mutate the world. Static source
checks passed183 GUIDs/21 asmdefs/112 C# files; Python tooling passed182 tests.
Final full/commit verification is reported with the review PR. Native GUI
layout/readability remains NotRun because
Unity is unavailable. The sustained mixed-probe snapshot remains frozen at its
own commit and does not validate this new presentation code.

Independent ultra reviewer `audit_gameplay_integration` found no blocking source
findings, including terminal guards, warning timing, settled-only misses and exact
source linking. Their review ran no builds or native tests. Physical/readability
acceptance remains pending. No merge or roadmap gate claimed.
