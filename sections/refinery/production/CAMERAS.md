# Fixed camera contract

All review cameras are 1.68 m above the nominal floor with a 36 mm sensor. Positions, targets and focal lengths are authored in `../blender/config.py` before the first successful render batch. Review, correction and cold-start renders use identical framing.

| Camera | Purpose | Lens |
|---|---|---:|
| CAM_ENTRY | South entrance and room/process readability | 23 mm |
| CAM_MINE_TO_CRUSHER | Authentic cart, cradle, hopper, incline and crusher | 21 mm |
| CAM_MAIN_ROUTE | Shared work floor and continuous production frontage | 22 mm |
| CAM_PROCESS | Sorter, process vessel and distinct dryer | 20 mm |
| CAM_ASSEMBLY | Press, inspection and reactor-side dispatch | 22 mm |
| CAM_REVERSE | Opposite direction and arrival-side circulation | 22 mm |
| CAM_PINCH | Crusher/sorter operating strip | 22 mm |
| CAM_MATERIAL | Near-view paint, bare metal, rubber and glass response | 30 mm |

No elevated beauty camera substitutes for these views. The named state previews select an appropriate fixed camera; they do not simulate final gameplay.
