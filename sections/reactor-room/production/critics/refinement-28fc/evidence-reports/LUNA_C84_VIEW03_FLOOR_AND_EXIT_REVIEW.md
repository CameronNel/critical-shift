# C84 view03 floor and view40–42 EXIT pictogram review

**Current scene:** `/workspace/scratch/reactor-refinement-cycle84/hall_final.blend`  
**Scene SHA-256:** `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06`

## Current view03

Image: [03_floor_access_lane.png](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/main-720p/03_floor_access_lane.png)  
Image SHA-256: `d37f0ba794c131d8122c318205881431842c3a1515b99ac526e343175b74ce70`  
Manifest: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/parallel-originals/main/green/03/render_manifest.json`  
Render: 1280×720, Cycles CPU, 96 maximum / 32 minimum adaptive samples, OIDN, 16-bit RGB.

The reflective film is clearly distinct from the surrounding matte concrete. Its edge narrows into the visible rectangular grate; the grate has a readable perimeter frame, individual open bars, and a dark recessed pocket. The floor also shows thin slab seams and restrained, nonuniform concrete tone. These full-resolution pixels support #60, #62, #63, and #69. The image also reconfirms the previously accepted local route-paint wear and white-arrow silhouette (#66/#67), but the wider route-continuity question (#68) still needs view04.

For #72, the visible current-C84 grate top is combined with the exact C79 saved-mesh contact probe in [`LUNA_C79_STATION_DRAIN_GRILLE_CONTACT_REVIEW.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C79_STATION_DRAIN_GRILLE_CONTACT_REVIEW.md) (report SHA-256 `26143a5b8170ecf85bfbf854b3adc22d84c8b1d83edeb1b4a40787fafefd5b95`). The probe is bound to C79 scene SHA `d80ab49f330cddddf6044e96f76b96c24e889bce924fbf9375a42e479ff6ee2b` and measures the correct station drain at `(-6.95,-0.60)`: two IRON grille undersides meet STEEL rail tops at `z=-0.035 m`, and four frame undersides meet the floor rebate at `z=-0.04 m`. The exact C79→C82 delta (SHA-256 `022729ebc720a61b971cfb010e7c3125aee7a8b0bf4101faf1be75f31acbfb0a`) changes crane identity and six door-leaf meshes; the exact C82→C84 delta (SHA-256 `af97f6cb155b394ce907ecac255d6b42b38b30a7c6e4e91be42ba3d17e360e67`) changes only five drum meshes. The station drain, its materials, supports, camera, and lighting remain outside both changed sets. This is a narrow mixed-source disposition for that drain only, not a claim about the three remote catch basins or every grate.

Items retained as open after view03:

- **#61:** wet-versus-dry is clear, but the pixels do not separate oil from dirt well enough to close the full wet/oil/dirt criterion.
- **#64–65:** crack depth and main/branch hierarchy need the dedicated grazing macro36.
- **#68:** one lane section does not prove room-route continuity; retain view04.
- **#70:** the circular manhole covers are outside this view; retain view04.
- **#74–75:** this close view does not establish a coherent room-scale traffic-wear pattern or the overall pool-area clutter/noise; retain the wider view04.
- **#137 from view03 alone:** this frame shows paint wear and concrete/water response but is not enough by itself to judge material-specific wear across the room. The separate multi-image C84 review later accepted #137 from views03, 04, and 31; see [LUNA_C84_MATERIAL_WEAR_REVIEW.md](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_C84_MATERIAL_WEAR_REVIEW.md). That separate acceptance does not close #74.

## Current native40

Image: [40_exit_north.png](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/40_exit_north.png)  
Image SHA-256: `2b4b77e1180bcf523482e265fb1248c03e6ef6499f58e4336615f6c4514210dc`  
Manifest: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/render_manifest.json`  
Render: 640×360, Cycles CPU, 96 maximum / 32 minimum adaptive samples, OIDN, 16-bit RGB.

The north overhead exit face and its white door/arrow pictogram are fully in frame, high-contrast, and unobstructed. This closes **#13** for the overhead-sign criterion. Native41 and native42 show the west and southeast fixtures. Together, the three direct views support accepting **#14** as resolved by high-contrast functional pictogram replacements for the older red wordmarks. The whole-room intended-view sweep (#139) remains open pending broader mapped signage evidence. These images are pictogram signs, so this is a contrast/readability disposition, not a text-curve sample for #131.

## Current native41

Image: [41_exit_west.png](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/41_exit_west.png)  
Image SHA-256: `df3190df832b72686b33ac851b10957ae3b5b1bc24c3fffc8015c73c7a9cfb15`  
Manifest: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/render_manifest.json`  
Render: 640×360, Cycles CPU, 96 maximum / 32 minimum adaptive samples, OIDN, 16-bit RGB.

The west-facing evacuation pictogram is fully framed and sharply contrasted against its dark backing. This is a second clear instance of the high-mounted directional pictogram class and corroborates #13. It does not show the older red-backed wall EXIT wordmark at z=3.9; the exact saved-scene probe finds no such wordmark. The supported pictogram fixtures replace that lower-sign approach for the contrast/egress criterion. This remains a local sign result, not a room-wide disposition for #139.

## Current native42

Image: [42_exit_diagonal.png](/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/42_exit_diagonal.png)  
Image SHA-256: `fa12540fa918761eafb4b63a76f838ea1a08d5e2ed60c32d9da291ffda6562b2`  
Manifest: `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c84/native-signs/green/render_manifest.json`  
Render: 640×360, Cycles CPU, 96 maximum / 32 minimum adaptive samples, OIDN, 16-bit RGB.

The southeast wall fixture is fully framed. Its white directional arrow, running-person figure, and doorway are sharply distinguished from the dark panel, with no obstruction. Together with views40/41, this resolves #14's contrast/egress function without requiring an additional literal wordmark. The result does not close #139.

## Exact current dispositions

Accepted from these current pixels: #13 (native40, corroborated by native41) and #14 (native40–42), plus #60, #62, #63, #69. Accepted for visible top plus bounded historical underside/contact geometry: #72. No overall/area score is assigned here.
