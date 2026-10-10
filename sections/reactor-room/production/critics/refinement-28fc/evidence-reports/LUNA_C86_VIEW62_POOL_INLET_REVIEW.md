# C86 view62: over-rim pool inlet appearance

## Evidence

- Candidate: `/workspace/scratch/reactor-refinement-cycle86/hall_final.blend`
- Candidate SHA-256: `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f`
- Image: `/workspace/scratch/reactor-refinement-cycle86/parallel-720p/inspection/green/62/62_pool_inlet_diffuser_fit.png`
- Image SHA-256: `ff0c8279a5c37d76f83cf22d9af40182811c98be26ff964090ea5c79e0b038b9`
- Manifest: `/workspace/scratch/reactor-refinement-cycle86/parallel-720p/inspection/green/62/render_manifest.json`
- Render: 1280×720, Cycles CPU, 96 maximum / 32 minimum samples, adaptive threshold 0.015, OIDN, 12 bounces, guiding64, 16-bit, AgX Medium High Contrast, exposure0.

## Finding: #85 remains open

The image shows the feed pipe entering a separate top collar and a dark cylindrical head beside the liner. At full resolution the head reads as a smooth dark cylinder with five continuous black circumferential bands. No side outlet apertures are visible, so the part reads more like a corrugated coupling than a constructed diffuser. A bright vertical pool element also cuts into the left edge of the head's silhouette.

The source geometry confirms this is not only a lighting or camera issue. `rh_services.py` builds the head and each of its five “slot” bands as capped `Kit.prism` cylinders. The C86 fit stage scales their radii but preserves their topology; it does not cut apertures through the head or bands. The 200-vertex/110-face black slot mesh is therefore five continuous closed bands, not a perforated diffuser surface.

The saved clearance probe is positive at its sampled points: minimum separation is 8.57 mm for the diffuser body, 6.59 mm for the slot mesh, and 3.66 mm for the flange. That establishes a useful fit check, not the visual construction requested here. The current pixels do not resolve the construction defect.

Recommended local correction: replace or interrupt the continuous rings with clearly visible, actual side openings while staying within the measured slot envelope (radius 0.072 m) and preserving the 3.66 mm sampled flange-to-liner clearance. Keep the pipe route and liner unchanged. Re-render the same full-quality view after correction.
