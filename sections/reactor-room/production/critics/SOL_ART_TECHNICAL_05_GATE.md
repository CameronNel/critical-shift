# Sol bounded gate recheck — Art 05

**Result: PASS**

I opened only the newly authored Art 05 `blender/reactor_scene.blend` in Blender 5.2.0 LTS using `--background --factory-startup --threads 2`. The scene was inspected read-only. Its recorded source SHA-256 exactly matches `production/revisions/art-05/build_scene.py`: `faa862ab0ecda725b3047b45a797b068d2e4d05a94c137e7e3cd7af7b0dbbe61`.

The measurement used evaluated mesh vertices, including conversion of every gate curve to its evaluated mesh. It did not use curve `bound_box` values.

- Left fixed upright inner surface: X `-0.6999999881` m.
- Right fixed upright inner surface: X `+0.6999999881` m.
- Fixed surface clearance: `1.3999999762` m.
- Opened-leaf maximum X at the inward 90° pose: `-0.7024998665` m.
- The leaf remains `0.0024998784` m outside the left aperture surface.
- Actual open surface clearance: `1.3999999762` m.
- Required clearance: `1.40` m; result passes within the `0.00001` m validation tolerance.

Observed source geometry is at `build_scene.py:671–689`; its evaluated-geometry validation is at `build_scene.py:1333–1341,1356–1368`. This bounded result covers only the formerly failing service-gate clearance and does not constitute a full technical or visual acceptance.
