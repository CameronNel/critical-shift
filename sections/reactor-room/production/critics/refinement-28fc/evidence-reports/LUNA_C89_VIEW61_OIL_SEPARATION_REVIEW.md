# C89 view61 oil separation review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
**Source SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`  
**View61 image:** `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/61/61_floor_service_oil.png`  
**View61 image SHA-256:** `0462478d73dccb5e47a0e75f120e4ae8c1fdcfab9c8d2a2c9e9a9a0a48ba9e36`  
**View61 manifest:** `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/inspection/green/61/render_manifest.json`  
**View61 manifest SHA-256:** `8189cb2ee44d31eec74768fe4995656146bbd578643d2f053116a7f13f57090d`  
**Paired main03 image:** `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/main/green/03/03_floor_access_lane.png`  
**Main03 image SHA-256:** `b22f107f4f1726af8af84c6ca28c19569735f91ec5212be5d004201cfaca789b`  
**Main03 manifest:** `/workspace/scratch/reactor-refinement-cycle89/parallel-720p/main/green/03/render_manifest.json`  
**Main03 manifest SHA-256:** `00b89048097d63e94eedc291eba95e436c4d19b88a13d8f3c9ba5cdfe0fb5485`

Both manifests bind the original 1280×720 Cycles CPU renders to the exact C89 source. View61 used 96 maximum / 32 minimum adaptive samples, 16-bit output, OIDN denoising, and the canonical exposure and lighting. Main03 is the matching full-quality floor view.

## Review

View61 shows a localized dark warm-brown film beside the service equipment. Its perimeter is irregular, and the surface carries a crisp bright reflection from a rectangular existing practical fitting plus a smaller edge highlight. The surrounding exposed slab remains matte gray. The film is clearly a separate glossy material response rather than another patch of concrete discoloration, and its visible edge does not cross the nearby yellow route stripe.

Main03 supplies the other parts of the distinction: shallow water has a broader reflective film and visible reflected detail, while dry concrete and worn route paint retain a subdued, non-glossy response. Taken together, the full-quality C89 pixels distinguish water, oil film, and ordinary dry slab/wear. The localized oil patch remains plausible at this scale despite the bright practical reflection; it does not read as a flat brown stain.

## Disposition

- **#61 Wet/oil/dirt separation: accept current C89.** Evidence is the paired exact-source main03 and view61 images above.
- This is limited to the visible material distinction in these areas. It does not accept floor movement wear (#74), pool-wall mineral staining (#86), or any other floor criterion.
- Any later carry must bind the exact C89 images and demonstrate that the oil film, underlying floor, relevant lighting, and view61 camera neighborhood remain unchanged in the later candidate's recorded delta. This report does not accept a later source hash.
