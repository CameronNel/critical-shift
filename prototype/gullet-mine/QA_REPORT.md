# Gullet Mine visual and collision QA

Date: 2026-08-03

The prototype was served from `prototype/gullet-mine/` with a local HTTP server and inspected in bundled headless Chromium through Playwright. Desktop captures are 1365×768. The mobile capture is exactly 706×1536 with coarse pointer and touch enabled. The cloud browser could not reach the container loopback address, so the local Chromium render was used for the actual screenshot inspection.

The container’s software-rendered Chromium measured roughly 1–2 rendered frames per second during capture (desktop/full-quality and coarse/low-resolution respectively); this is an environment capture metric, not a device-GPU benchmark. The prototype stayed functional and responsive enough for the visual and collision passes, with shadows disabled on coarse-pointer devices.

## Required visual checkpoints

The inspected screenshot artifacts are in the QA working set under `qa-v4/`:

| Checkpoint | Capture | Inspection result |
| --- | --- | --- |
| Maw Camp entrance | `01-maw-camp-final.png` | Connected rail, staged camp props, readable first room. |
| Crooked Rail | `02-crooked-rail-final.png` | Repeated timber frames and a connected damaged brace establish the route. |
| Blackshaft reveal | `03-blackshaft-reveal-final.png` | The BLACKSHAFT sign, raised crossing, pit and approach read as one landmark. |
| Blackshaft bridge | `04-blackshaft-bridge-final.png` | Deck, posts, handrails and ropes remain physically legible at gameplay height. |
| Drowned Pocket | `05-drowned-pocket-final.png` | Opaque teal sump, repaired boardwalk and Saint Glimmer tease are readable without the old grid artifact. |
| Saint Glimmer entrance | `07-saint-glimmer-entrance-final.png` | The warm work area opens onto the embedded mineral wall. |
| Saint Glimmer hero seam | `06-saint-glimmer-final.png` | Dark matrix, branching mineral seam, limited facets and mounted sign form a single authored deposit. |
| Powderworks | `08-powderworks-final.png` | Barrels, crates, drill and timber staging create a deliberate work vignette. |
| Foreman’s Vault | `09-vault-final.png` | Gate bars, posts, sign and ledger table are visible and physically framed. |
| Mobile gameplay HUD | `10-mobile-706x1536-final.png` | Exact portrait viewport shows the joystick, LAMP/JUMP controls and route HUD. |

## Manual collision checks

- Walked from Maw Camp through Crooked Rail and across Blackshaft with collision enabled and normal W/D controls. Both bridge ramps now align to the deck ends; the prior capsule catch at the entrance is gone.
- Followed the Drowned Pocket bend with W/D/A, crossed the repaired walkway, continued through Saint Glimmer and Powderworks, and reached the Foreman’s Vault zone without enabling ghost mode or teleporting.
- Deliberately stepped off the Blackshaft bridge with D. The player fell into the shaft and recovered to Maw Camp with collision still enabled.
- Tested the mobile joystick at 706×1536; a held diagonal joystick input moved the player from the spawn area with no page errors. Mobile LAMP and JUMP pointer actions also completed without errors.
- Final smoke load returned one canvas, no page errors, no missing asset responses, and no QA debug object exposed to the page.

## Iteration notes

The visual loop replaced the disposable fragment geometry with a compact authored spline cave, connected timber/rail structures, a real raised bridge hazard, a flooded boardwalk, an embedded mineral seam, Powderworks staging and a barred vault. It also removed the floating Drowned fixture, corrected the water/shadow artifact, mounted the practical bridge lamps to the structure, and added collision bars to the vault gate.
