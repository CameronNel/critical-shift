# Spawn user revision — 6 September 2026

**Subsequent direction:** [INHABITED_REVISION_20260906.md](INHABITED_REVISION_20260906.md) replaces the displayed suits with personal belongings and adds timber flooring, a rug, sockets and workplace dressing. The current editable file is `../blender/spawnroom_inhabited_walk.blend`; the screenshot-correction file below remains preserved as its base.

The user's latest direct instructions supersede conflicting older Spawn room reference rows. Seven screenshots were attached; written instructions numbered 8 and 9 were also implemented.

| User request | Implemented result | Evidence |
|---|---|---|
| Remove the random door intersecting the hall bench | Briefing leaf and attached hardware removed; bench retained | USER_BriefingFrame, VALIDATE_ExitReverse, live Spawn viewport |
| Fix clipping doorframes and clean both entrances | New open reveals; wall ends recessed behind jambs; no leaves, pocket rail or window fittings | 170 clearance rays; VALIDATE_Walk_A/C |
| Fix odd wall/floor patterns | Shadow-map striping isolated with on/off test; filtered jittered shadows restore contact lighting without the pattern | USER_Floor; live viewpoint change |
| Large flat-screen TV, remove its old surrounding unit | Slim wall-mounted display, no heavy console housing, speakers or control block | VALIDATE_BriefingDoor |
| Two two-person briefing benches | Two 1.50m benches, 0.45m seat height, four places total | counts, support contacts, VALIDATE_BriefingDoor/Walk_C |
| Remove Geiger counter, make a very large metal airlock | Meter removed; heavy twin-leaf 2.56m-wide airlock with compression seal and locking hardware | VALIDATE_HallForward |
| Remove weird window | Both borrowed-light observation windows removed and openings infilled | VALIDATE_Spawn/ExitReverse |
| Move suits toward entry; chamber middle-back; add benches and lockers | Four bays at x=3.0/4.5, two changing benches, two personal storage units, pod at x=6.82 y=4 | VALIDATE_LockerDoor/Reverse, USER_LockerEntry; counts |
| Clear glass, metal futuristic pod | Curved sliding glazing, machined rings, metal service spine, overhead scanner and compact physical controls | VALIDATE_Hero_A, six-state checks |

The new geometry uses existing packed CC0 finishes and three small dedicated materials for steel and the display, plus clear pod glazing. No new external models or texture downloads are required.

The new authoritative walking source is `../blender/spawnroom_revised_walk.blend`. Reproduction is documented in `../blender/README.md`. Final images and JSON verification are in `renders/final/user-corrections/`.

The shadows were investigated with Blender's direct scene API. The official [EEVEE light settings](https://docs.blender.org/manual/en/5.0/render/eevee/light_settings.html) provided the terminology for jitter and resolution limits; the actual correction was accepted from on-machine renders and live viewport checks. No web source is treated as an instruction to modify the project.

Review limitations: this is a bounded correction pass, not renewed approval of the entire room's art direction. The old fixed front camera no longer fits all four forward bays at once; their count/placement is verified geometrically and reverse views cover the near pair. Blended glazing favors stable realtime clarity over physically exact multilayer refraction.
