# C89 material-specific wear review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
**Source SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`

## Actual full-quality evidence

- Main03: `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/main/green/03/03_floor_access_lane.png` — image SHA-256 `b22f107f4f1726af8af84c6ca28c19569735f91ec5212be5d004201cfaca789b`; manifest `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/main/green/03/render_manifest.json` — SHA-256 `00b89048097d63e94eedc291eba95e436c4d19b88a13d8f3c9ba5cdfe0fb5485`.
- View61: `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/61/61_floor_service_oil.png` — image SHA-256 `0462478d73dccb5e47a0e75f120e4ae8c1fdcfab9c8d2a2c9e9a9a0a48ba9e36`; manifest `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/61/render_manifest.json` — SHA-256 `8189cb2ee44d31eec74768fe4995656146bbd578643d2f053116a7f13f57090d`.

Both are original 1280×720 full-quality Cycles CPU renders, 96 max/32 min adaptive samples, OIDN, 12 bounces, 16-bit output, and canonical exposure. Their manifests bind them to C89.

## Review

Main03 shows wear cues on the appropriate surfaces: chipped/scuffed yellow route paint remains legible, the exposed concrete has restrained aggregate and narrow wear/crack detail, and the orange/white cone shows a dirty scuffed lower section against its cleaner upper band. The wear does not collapse the painted, concrete, and rubber responses into a single texture. View61 separately shows the service oil film as a dark warm-brown glossy surface with an irregular edge and reflected practical, distinct from the adjacent dry gray floor.

## Disposition

- **#137 Material-specific wear: accept current C89** for the evidenced paint, concrete, cone/base, and oil-film responses.
- This does not accept a coherent traffic/wheel movement path (#74), and it does not close pool-wall mineral staining (#86).
