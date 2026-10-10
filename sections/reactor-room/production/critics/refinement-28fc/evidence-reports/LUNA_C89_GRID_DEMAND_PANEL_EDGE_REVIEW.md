# C89 GRID / DEMAND Panel Edge Check

**Candidate:** C89, source SHA-256 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`

**Image:** `parallel-720p/main/green/01/01_machinery_turbine_grid.png`, 1280×720 Cycles 96; image SHA-256 `80de2a9981d783bfee3a23320c6b1b4c7a342b299706e4a88794490240bfe353`. The one-view manifest SHA-256 is `93dbf134b059d5b29f3c93f9c95b6b93ea32b0b7f099356d48fe009c20e6480b`.

## Finding

In the rendered main01, the GRID / DEMAND plaque's outer right edge sits close to the stainless riser in projection. A read-only check of the saved panel and exact main01 camera finds no pipe crossing over the plaque's exposed face. The panel object `RH refine sign GRID / DEMAND PANEL` has a visible face at world x=10.685 m, spanning y=−2.591…−0.709 m and z=3.954…4.286 m. Its eight bounding corners project inside the frame (approximately x=0.516…0.625, y=0.867…0.976 in normalized device coordinates).

I sampled that complete exposed face on an 81×17 grid, inset 1 mm from its long edges and 6 mm from its top and bottom bevels. All 1,377 rays missed the adjacent meshes `RH services R2 PIPING lag GALV`, `RH services R2 PIPING band ORANGE`, and `RH services R2 PIPING pipe PIPE`. This resolves the specific suspicion that the vertical riser physically masks the panel's visible face. Rays aimed at the plaque's rear/thickness side can encounter the riser; that surface is behind the exposed front face and does not establish a visible sign-face overlap.

The independent audit's 147/147 clear glyph samples agree with the face test, but neither check closes the room-wide #139 visibility criterion. Other signs and intended approach views remain to be assessed from their mapped current pixels.

## Durable probe

- Script: `review/evidence/C89_GRID_DEMAND_FRONTFACE_PROBE.py`
- Result: `review/evidence/C89_GRID_DEMAND_FRONTFACE_PROBE.json`
- Scope: the named plaque's full front face versus the three adjacent pipe meshes in the exact main01 camera. No scene, lighting, material, or render changes were made.
