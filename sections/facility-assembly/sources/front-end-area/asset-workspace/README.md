# Asset workspace (front-end area)

Separate review space for every prop and door leaf built for the cafeteria and hall. The builders (`../fe_assets_*.py`, `../fe_cafeteria.py`, `../fe_wallart.py`, `../fe_doors.py`) stay the source of truth; this folder collects their output so assets can be reviewed and budgeted one by one without opening the whole scene.

## Run
```
blender -b <built scene>.blend -P make_library.py -- <outdir> [samples]
```
Writes `asset_library.blend` (objects in per-group collections `LIB_dining`, `LIB_serving`, `LIB_lounge`, `LIB_game`, `LIB_doors`, each tagged with `tri_count`, `tri_cap`, `group`), `asset_report.json`, and one labelled contact sheet per group (`sheet_*.png`, one auto-framed 3/4 tile per asset, label shows triangles against the cap).

## Triangle caps (agreed with the owner)
Hall props have explicit caps in `make_library.py` (lockers 7,000, gantry 7,000 to 8,000, cable tray 4,000, shift desk 3,500). Hero props (counter, kitchen block, fridge, vending, arcade, foosball, sofa, booth, bookcase, kiosk) up to 15,000; furniture and doors up to 4,000; small props about 2,000 (recycling station 2,500, notice board 3,000). Wall quality comes from textures and normal maps, not geometry.

## Latest result
See `asset_report.json` and `sheet_*.png`. Every asset is inside its cap; 115 assets are collected (cafeteria, hall, yard and door leaves); none is over its cap. Hall groups: hall_ops, hall_work, hall_safety, hall_shell; yard groups: yard_vehicles, yard_site, yard_stock. Yard vehicles are the heaviest props (pickup about 9.4k, van 7.6k); the real limit is the 800k scene budget. Sheets are shot from the front of each asset.

Status: unreviewed by anyone other than the author.
