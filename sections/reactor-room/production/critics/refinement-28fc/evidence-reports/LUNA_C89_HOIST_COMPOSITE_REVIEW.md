# C89 hoist review: composite evidence for #108

**Disposition:** accept #108 (`Trolley motor/drum construction`) as a bounded composite of exact-C89 full-quality views 26–28 and the narrowly scoped historical C82 upper-trolley image. The historical frame supplies the motor/top-frame connection that the current close views do not frame; current C89 views supply the hoist drum and complete lower load path. This is not a claim that the C82 image is a C89 render.

## Source and render identities

Current scene: `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend` — SHA-256 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`.

| Scope | Original source SHA-256 | Image SHA-256 | Manifest SHA-256 | Camera |
|---|---|---|---|---|
| Current hook/block/throat, C89 view26 | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `a66e4de936cdd0207119222154eba19d9047bb96d0ecd62f5ebc34afd50595a0` | `676325deb06f2ac19a510eef81fef77a7ed5cddba352f0ce812d3d0b341ebf0d` | `(-5.2, 2.6, 10.6) → (-6.4, 4.6, 10.5)`, 45 mm |
| Current drum/flanges/reeving entry, C89 view27 | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `34ec531ee22a2392f60ee2cc64b5f399c0797d44f483050c1de1ad488f847a8f` | `721b2c6b5ec16804cfcf529a962e62a86f0fb7dc766b585fba077acbd3000edf` | `(-6.35, 4.12, 16.075) → (-6.5, 4.68, 16.015)`, 22 mm |
| Current continuous rope/block/hook path, C89 view28 | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `cd6d598dc873ced43a6b4f679051d5b0ed67f19c41fb431978e609e9884a327f` | `93b74dcd78dcb4c217c3d36b470cb925db55e080cdf2ceaac488735ee62ce2b3` | `(-5.9, 3.3, 13.15) → (-6.5, 4.6, 13.15)`, orthographic scale 12.8 m |
| Upper motor/trolley context only, historical C82 view52 | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | `766e5c5fad1da45bb060711c9a7af1377aa51c4145411b1eb9bbf1ac8b914372` | `cf73a532086607acd33ee43a3ff2b95b602fd3cee9a494e874d45f0ad4313b5e` | `(-8, 3, 16.6) → (-6.5, 4.6, 15.7)`, 35 mm |

All three current images are 1280×720 Cycles CPU frames with 96 maximum / 32 minimum adaptive samples, 16-bit RGB, OpenImageDenoise, and the canonical production color management. C82 view52 is likewise a full-quality original under its own source and manifest.

## Independent visual finding

C82 view52 shows the trolley top frame, motor-side housing and drive connection in context. The bridge rail masks part of the lower block/hook there, so that image is only partial evidence. C89 view27 makes the hoist drum flanges, wound ropes and braided cable entry readable. C89 view28 shows the reeving continuing through the block and down to the hook. C89 view26 resolves the hook throat, curved shank, tapered tip, suspension sheave and socket. The hook reads as a load-bearing lifting hook; I do not find a concrete shape defect, and a safety latch is not part of this criterion.

The C82→C84 delta changed five storage-barrel/props meshes: RH refine legacy drums GALV/RED and RH stations props GALV/RED/YELLOW. It did not change the crane-hoist drum or other hoist objects. Later C84→C86, C86→C87, C87→C88 and C88→C89 deltas also leave the upper motor/trolley assembly unchanged. The exact scoped source chain and delta hashes are in [the C89 supplemental-family carry report](LUNA_C89_SUPPLEMENTAL_FAMILY_CARRY.md). Current C89 views show the hoist drum and lower-load-path details; the C82→C84 storage-barrel edit is not the basis for this hoist evidence. This composite does not close room-wide roof, signage or visual-quality criteria.
