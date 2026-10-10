# C89 material-family response review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle89/hall_final.blend`  
**Source SHA-256:** `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`  
**Evidence:** original full-quality current-C89 main and inspection frames listed below. Each is 1280×720 Cycles CPU with 96 max/32 min adaptive samples, OIDN, 12 bounces, 16-bit output, and canonical exposure; manifests bind each image to this source.

| View | Image SHA-256 | Manifest SHA-256 |
|---|---|---|
| 01 | `80de2a9981d783bfee3a23320c6b1b4c7a342b299706e4a88794490240bfe353` | `93dbf134b059d5b29f3c93f9c95b6b93ea32b0b7f099356d48fe009c20e6480b` |
| 02 | `9ac3bd6e9929b1c0cffcd1eb08d6a6921bd2b8f170676bdabd5dffa8f4194bb1` | `e6fd40e86145592485051ab01ce3d2442b9a9c190f50564be8f30a93174fb68a` |
| 03 | `b22f107f4f1726af8af84c6ca28c19569735f91ec5212be5d004201cfaca789b` | `00b89048097d63e94eedc291eba95e436c4d19b88a13d8f3c9ba5cdfe0fb5485` |
| 04 | `2a3ac3d2a793445e8134fc18bcdfbfe570c17d0c8b98c453ae1bc2c02765a27a` | `0a03204f7ca70f81ae03778b5b422ff91e5d2c35542a896481150009359f852a` |
| 05 | `46e17bd10ddd4e86e5f2f6233019b8ef845663bb205f435ea3fdc15db7d01349` | `98c81e641631091d2674014bb257d3a02c981a9124e56cabd1e2b3b99e4b87ad` |
| 06 | `c307dcee81ff32bb51da031f7ed68c093e2698614d5d61d3e34936fda1e7096d` | `ee4731aa4c0b4a34f478106d23d64585e03460982881ff765f6ce9eabaae8676` |
| 08 | `5ef0dfa095b1eea05683cec62e2e0f547b50c9de44d09171bf6534808cd0e72d` | `78f016c3452613bd83c08daab4f4eee045b987655d45c8b689f347f4eff8f5ee` |
| 09 | `08243d7a41d45027250694eb34b29f974a043ebaa3edcfde2b0daa322aa3d4c0` | `fe4eb7240c715646763924db6e767316ab9028b668bb969ba3aa1912157e5c83` |
| 10 | `0a6c7887eb0f418361aa08990ad0e761c98bb37bd404ee98af2a7b2c84a5ba3d` | `f5e0375a00bcb2b9b866af53fbf03b992907de11154b46461e02747503c4ea0e` |
| 61 | `0462478d73dccb5e47a0e75f120e4ae8c1fdcfab9c8d2a2c9e9a9a0a48ba9e36` | `8189cb2ee44d31eec74768fe4995656146bbd578643d2f053116a7f13f57090d` |

## Review

Across the exact-C89 images, the concrete walls and slabs stay matte and show restrained aggregate; the yellow and orange painted steel reads as coated and mostly diffuse; machined/galvanized pipes, casing rings, and structural steel have narrower metal highlights and visible joints; dark rubber/absorber surfaces remain substantially less reflective. Pool lining, shallow water, and the separate warm-brown oil film each keep distinct color and surface responses. Red/yellow drums and cone coatings separate from the gray concrete and the metallic machine bodies. The new rod-drive finish is legible as a brighter machined part beside the darker absorber/cage assembly in main05/06.

There are dark recesses in main02, but they do not erase these family distinctions in the exposed surfaces. The conclusion is based on actual current pixels across several intended views, not material-node presence alone.

## Disposition

- **#136 Material family response distinction: accept current C89.** The mapped full-quality views show the scene’s concrete, painted steel, machined/galvanized metal, rubber/dark absorber, coated props, water, and oil with distinct responses.
- This does not accept the separate material-specific wear criterion (#137), movement-wear path (#74), or any whole-room score by itself. The #137 assessment is recorded separately.
