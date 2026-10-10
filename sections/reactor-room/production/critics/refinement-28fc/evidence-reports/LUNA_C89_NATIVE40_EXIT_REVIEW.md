# C89 native40/41/42 wall EXIT review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
**Source SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`  
**Image:** `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c89/native-signs/green/40_exit_north.png`  
**Image SHA-256:** `056dfa01113f6eac4a70a4b924073b6449586269101421708aca9538d6894362`  
**Manifest at review time:** `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c89/native-signs/green/render_manifest.json`, SHA-256 `834ddb89f431fbfa83a7062cabcb4ccf9b14a27ef38b716d6aab7c6e26e57653`. A byte-identical immutable snapshot is preserved at [C89_NATIVE_GREEN_MANIFEST_AFTER_40.json](evidence/C89_NATIVE_GREEN_MANIFEST_AFTER_40.json), with the same SHA-256. The native render is 640×360, Cycles CPU, 96 max/32 min adaptive samples, 16-bit, denoised, with path guiding.

**West corroboration:** `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c89/native-signs/green/41_exit_west.png`, SHA-256 `5ec748b05005928d7fd13d69ac48314ac3bc2029d6db2770ef5aa79c9fdaf1f9`. Its immutable manifest snapshot is [C89_NATIVE_GREEN_MANIFEST_AFTER_41.json](evidence/C89_NATIVE_GREEN_MANIFEST_AFTER_41.json), SHA-256 `363d6554e27e53fd49ed83cbefce04b9c420ae664347a895a764be000c0226a8`.

**Third diagonal-exit view:** `/workspace/critical-shift/sections/reactor-room/production/renders/hall-refined-720p-20261007/review-evidence/c89/native-signs/green/42_exit_diagonal.png`, SHA-256 `b9ce58a06b66062f73183e87112f0d1d45a06101067b2cec7c1e3c53a5d07167`. The immutable green manifest snapshot after view42 is [C89_NATIVE_GREEN_MANIFEST_AFTER_42.json](evidence/C89_NATIVE_GREEN_MANIFEST_AFTER_42.json), SHA-256 `b00229cfd6295108a6f4c5620f4bb647cce7718d8a3ea9fd2fa033a757959dae`.

## Current C89 spot-check for issue #14

All three panels show a clear white left arrow and running-person exit pictogram on a dark field. The symbols are unobstructed and have strong contrast at native resolution. In the north and west views, the figure's head nearly touches the upper door-frame stroke, but the head, torso, limbs, and left-pointing arrow remain recognizable; this contact does not make the egress direction ambiguous. The diagonal view also reads cleanly.

**Disposition:** accept #14 from the complete exact-C89 north40, west41, and diagonal42 set. This closes the three wall-mounted EXIT pictograms, not the room-wide signage visibility audit #139.
