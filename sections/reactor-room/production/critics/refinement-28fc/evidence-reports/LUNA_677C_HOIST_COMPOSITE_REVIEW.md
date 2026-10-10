# 677c hoist construction review: #108

**Disposition:** accept #108 as a bounded multi-source composite. The original images remain attached to their rendered scene hashes; only view70 is a 677c render. The composite covers the motor-side trolley context, drum and reeving, hook and lower path, plus the new drum-end retention and opened hood.

## Current candidate and 677c pixel

- Candidate: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`
- Candidate SHA-256: `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`
- Current image: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/70/70_hoist_rope_anchors.png`
- Image SHA-256: `d1050f9f7c9aa7bfda234e7aa2759b4daba50e9032f8fa634c13f8b7824f2a8a`
- Manifest SHA-256: `6b4c9882495c0958dba7a1ae96230a0e0e6b21d06922f591289fa8e264fe32b4`
- Frozen renderer SHA-256: `947afcf6fc717519d2bafd01547595003da0a267a240935e12f3f6c202341453`

View70 is 1280×720, Cycles CPU, 96 maximum / 32 minimum adaptive samples, 16-bit RGB, OIDN, 12 bounces and path guiding. It shows both clamp blocks and their paired bolt heads inside the inspection opening; the rope legs leave the blocks, and the drum grooves remain visible. The local task light makes the new clamp faces readable without washing out the hood interior. This is full-quality evidence for the changed opening and clamp assembly, not a room-lighting judgment.

## Bounded composite components

| Subject | Original source | Original image SHA-256 | Manifest SHA-256 | What the image establishes |
|---|---|---|---|---|
| Upper trolley / motor-side context, C82 view52 | `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` | `766e5c5fad1da45bb060711c9a7af1377aa51c4145411b1eb9bbf1ac8b914372` | `cf73a532086607acd33ee43a3ff2b95b602fd3cee9a494e874d45f0ad4313b5e` | Motor-side housing, upper frame, drum-side drive and trolley context. The red bridge rail partly masks the lower block/hook; this frame is only the upper-context component. |
| Drum / reeving entry, C89 view27 | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `34ec531ee22a2392f60ee2cc64b5f399c0797d44f483050c1de1ad488f847a8f` | `721b2c6b5ec16804cfcf529a962e62a86f0fb7dc766b585fba077acbd3000edf` | Twin grooved drum surfaces, wound ropes, flanges and braided entry. View70 supplies the later-added end clamps and opened hood. |
| Hook / socket, C89 view26 | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `a66e4de936cdd0207119222154eba19d9047bb96d0ecd62f5ebc34afd50595a0` | `676325deb06f2ac19a510eef81fef77a7ed5cddba352f0ce812d3d0b341ebf0d` | Hook throat, curved shank, tapered tip, suspension sheave and socket. |
| Continuous lower rope path, C89 view28 | `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` | `cd6d598dc873ced43a6b4f679051d5b0ed67f19c41fb431978e609e9884a327f` | `93b74dcd78dcb4c217c3d36b470cb925db55e080cdf2ceaac488735ee62ce2b3` | Trolley-to-block rope path in context, continuing to the hook. The plate is broad-view evidence and does not replace the close hook image. |
| Changed clamp / aperture assembly, 677c view70 | `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295` | `d1050f9f7c9aa7bfda234e7aa2759b4daba50e9032f8fa634c13f8b7824f2a8a` | `6b4c9882495c0958dba7a1ae96230a0e0e6b21d06922f591289fa8e264fe32b4` | Two fitted rope-end clamps, four heads, drum grooves and the open inspection hood in the same frame. |

The C82 and C89 frames are not relabeled as current 677c. C82 view52 supplies only the upper motor/trolley context; C89 views26–28 supply the unmodified motor/drum and lower path subjects where visible; current677c view70 covers the later hood, aperture and clamp changes.

## Source-chain limits

The exact source chain is C82 `640462e30241507f150e938ec05820db309afa0d680d09373f1f7f1e0956ad36` → C84 `48cffec1ca27344da3a56a98c3104a25207d5f03b53820ff40647b23a5262c06` → C86 `3361364c2ff364e1801b2d1cdd069eb34663f0398bd646366ece32ee5d42df4f` → C87 `ed340cc0ab6b3b19ae538ed491a806086f11aa60b5c7cd36c1967bf2592ddc13` → C88 `85766edcb5cf1ba1d5fa9bc624a956132885298e9c379aad3867a1fca0560cf6` → C89 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a` → 9b `9b3be6769fc7dc92221e2303c70a74da48d0dcbd80d0c68bdd2019afa72a48a7` → 79e `79e7a46ea352610668938d2fdab25c3bfb2b83f7bc70a63110d37d8a597b6c4c` → f79d `f79d0bf32c7f339f78796953332b3db347968c23cc75562bed5d0c9ba9acc5ff` → 5fd `5fd5f7b0f21383348f8fa450609057be01f17cd9426758bfe7ab6ada48565779` → 677c above.

The exact relevant delta reports are:

| Leg | Delta file | Delta SHA-256 | Hoist-specific scope |
|---|---|---|---|
| C82→C84 | `/workspace/scratch/reactor-refinement-cycle84/scene-delta.json` | `af97f6cb155b394ce907ecac255d6b42b38b30a7c6e4e91be42ba3d17e360e67` | Five storage-barrel/props meshes changed; no crane-hoist drum change. |
| C84→C86 | `/workspace/scratch/reactor-refinement-cycle86/c84-to-c86-scene-delta.json` | `d9c8a65ef48e19b5b28b9e7fdcfbaf6505a1c505edd7d8c4cbe1fd41b70f1d19` | No trolley-motor/drum/hook change. |
| C86→C87 | `/workspace/scratch/reactor-refinement-cycle87/scene-delta.json` | `af1ff4d3e2e1e6c14c77946393d01a07f2e1ad2900e942317cdcdd494bb877be` | Pool diffuser/floor changes only. |
| C87→C88 | `/workspace/scratch/reactor-refinement-cycle88/scene-delta.json` | `852b2d50e4293200ea86437a776ab3c31a3fbec68af745bccc10046d1cb028dd` | Girder finish change only. |
| C88→C89 | `/workspace/scratch/reactor-refinement-cycle89/scene-delta.json` | `10465cf8bd40ab5583827107465da2d49ef4ebc59d45fc16b9df7a8d4abc5320` | Girder crossings only. |
| C89→9b | `/workspace/scratch/reactor-refinement-next-corrections-working/scene-delta.json` | `742aa950d30574149dddc41578207aa3ede6befac99f9571bc7d9ff91eea2ca8` | Six doorway returns and pool lining changed. |
| 9b→79e | `/workspace/scratch/reactor-refinement-pool-readability-working/scene-delta.json` | `0d89fdfe0bd679317dde47d46dbd60a0ff630b6c922db469e9b534e299b47575` | Pool lining only. |
| 79e→f79d | `/workspace/scratch/reactor-refinement-switchgear-seat-working/scene-delta.json` | `6280636c48c2bd8ac6e04df356d15d6d86c08e14ed643221e68340e34a343c2d` | Four switchgear-prop meshes only. |
| f79d→5fd | `/workspace/scratch/reactor-refinement-hoist-anchor-seat-working/scene-delta.json` | `bc5040fb11e5645728e0665b0480b8576816a92ee0d24546e698fc6f95a84b1c` | The retained `R2 crane trolley crane OLIVE` hood mesh is opened; clamps, fasteners and aperture frame are added. |
| 5fd→677c | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/scene-delta.json` | `10058827bfc2ae32887862b2938f41490ec02d0d78630e0ddf9f0d126960b2b1` | Three tasklight objects (housing, lens and AREA light) are added; 1,951 existing objects remain unchanged. The small light is local to the clamp/hood inspection. |

For the newly added current light/opening interfaces, the 14-check set is green (checks SHA-256 `471d4c83870b4935cf5a15f64e85d20fd370b7d061533991634fd176fffe1184`) and the scoped support audit passes (SHA-256 `15050f5b42a6556246fb5d0c8bc9bea336a47b99293a170b8be223631b25c8bd`). The source comparison does not assert whole-scene equivalence.

**Conclusion:** the changed end-retention detail is visibly resolved in current full-quality view70, and the historical motor/trolley and C89 path views remain sufficient only for their explicit unchanged subjects. Accept #108 as this bounded composite, not as a single-source 677c image claim or a broader room-wide quality result.
