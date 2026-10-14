# Cafeteria camera evidence

All positions are in metres in the original plan frame. Module-local coordinates are `(x - 8, y + 80, z)`. The original nine inspection cameras are unchanged. Review cycles use Cycles CPU, OpenImageDenoise, 960 × 540, 8 samples, Khronos PBR Neutral, exposure −0.5. Final presentation renders use the same colour transform and exposure at a higher resolution and sample count.

| Fixed camera | Purpose |
|---|---|
| CAF_01_ENTRY_NORTH | Airlock arrival, main circulation axis, kiosk, hall opening |
| CAF_02_DINING | Tables, booths, chairs, meal settings and medical access |
| CAF_03_SERVING | Food counter, coffee bay, menu, queue and kitchen |
| CAF_04_LOUNGE | Lounge seating, media wall, rug, plants and yard approach |
| CAF_05_GAME_CORNER | Both foosball tables, both basketball cabinets and dartboard |
| FE_05_CAFE_REVERSE_NORTH_TO_SOUTH | Reverse circulation view, dining and lounge balance |
| CAF_X1_AIRLOCK_DOOR | Leaf apertures, seals, hinges, wheels and threshold |
| CAF_X2_YARD_DOOR | Existing yard connection and exit sightline |
| CAF_X3_MEDICAL_DOOR | Medical leaves, vision panels, closer and accessible route |

| Added camera | Eye | Target | Lens |
|---|---|---|---:|
| R8_GAMES_HERO | −0.52, −66.65, 1.90 | −4.50, −63.70, 1.34 | 28 mm |
| R8_FOOSBALL_DETAIL | −1.40, −65.82, 1.54 | −3.65, −64.20, 0.85 | 48 mm |
| R8_DARTBOARD_DETAIL | −0.21, −61.69, 1.91 | −1.13, −60.30, 1.75 | 64 mm |
| R8_BASKETBALL_DETAIL | −2.70, −66.20, 1.88 | −6.29, −65.15, 1.32 | 28 mm |
| R8_LOUNGE_HERO | 0.35, −72.61, 1.71 | −4.35, −77.25, 1.18 | 26 mm |
| R8_COFFEE_DETAIL | 25.03, −67.19, 1.68 | 24.70, −65.35, 1.235 | 52 mm |
| R8_DINING_HERO | 11.21, −77.30, 1.59 | 20.30, −72.52, 1.11 | 26 mm |

`review_images.py` assembles fixed-camera and hero contact sheets without changing the source renders. Its optional `--compare` records exact same-camera RGB pixel differences. Numerical image agreement is evidence of reproducibility; it does not replace pixel inspection.
