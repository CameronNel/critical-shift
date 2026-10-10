# 870b bounded historical review: issue 99 housing conduit entry

## Source chain

- Receiving source: `/workspace/scratch/reactor-refinement-bearing-lit-working/hall_final.blend`, SHA-256 `870bca11bd9fc1f43a90a411d573ff990d1f7f41b7c52ec9a627c13a97b753da`.
- Frozen prior source: 0058, SHA-256 `0058ee5c84b01e2345dab93d36a4997e4ba7bff795da87048f9ea24fd9087714`.
- Pixel source for both reviewed full views: 677c, SHA-256 `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`.
- 677c→0058 delta: `/workspace/scratch/reactor-refinement-switchgear-label-working/scene-delta.json`, SHA-256 `6de9cc017c0943286f5f7d2426899e4bcc1df2c0a36f8b6dc0aed3d96e6042ae`; it changes nine circuit-label curves and the east white label-strip mesh. The A/B conduit entries are outside that set.
- 0058→870b delta: `/workspace/scratch/reactor-refinement-bearing-lit-working/scene-delta.json`, SHA-256 `d2f459528aff38b56ef2ef05b3accbdf33db6bf24b73ee26a5cd6533befcdebe`; it adds only roof-bearing maintenance fixtures, with 1,954 unchanged objects. There is no pixel-identity or global-lighting claim.

## Actual full-quality pixels

| Bank | Original PNG and SHA-256 | Original manifest and SHA-256 | Renderer SHA-256 | Camera |
|---|---|---|---|---|
| A | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/67/67_bank_a_conduit_entry.png` — `d8fc12a2d1a892715e2bd728ff733ba4e86a1579c1d9ff957b9bad880ec4ecd1` | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/67/render_manifest.json` — `ceff1b0584a78ef3098a5b5e1af555870569dc2d229fa87ad9278e33f489276e` | `d2b92f1d430e70ada763ce1923eba9e48c4652691bdf038bf810a9e9eac4bf61` | `[-0.1,-3.8,11.35]` toward `[-0.78,-1.06,11.0]`, 40 mm |
| B | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/68/68_bank_b_conduit_entry.png` — `1c20efb6ef6c8b8a7b51705cb4dc76ee49073e093daa278815260f0a42b33149` | `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/68/render_manifest.json` — `20df4ed1797e1da08cb4c47865695f4dd9ba498b9f43ae21b863232dc738ff15` | `d2b92f1d430e70ada763ce1923eba9e48c4652691bdf038bf810a9e9eac4bf61` | `[3.2,-3.8,11.35]` toward `[2.02,-1.06,11.0]`, 40 mm |

Both originals are 1280×720 full-quality Cycles renders: 96 maximum / 32 minimum adaptive samples, threshold 0.015, 16-bit, OIDN, 12 bounces, path guiding 64, exposure 0. Each image clearly shows its labeled A/B housing side and its copper conduit turning into a flanged case entry. The fastening heads and entry ring are visible; the tube does not merely disappear against the case. The DRIVE A/B and CRD-A/B labels associate each entry with its correct housing.

## Bounded geometry corroboration

`/workspace/scratch/reactor-refinement-bearing-lit-working/wall-bores.json`, SHA-256 `c7cc380fce3db144a4b14bdb204f1d4ba618a1817533f5eccd5f632611c5887e`, records eight named service cores at 65 rays per core with no reported enclosure hits. Its A/B service-core rows corroborate passage through the envelope only; they do not establish internal electrical continuity or universal maintenance access.

870b's current 14 checks and source-bound support/signage audit also pass. Their full hashes and limits are recorded in `LUNA_870B_GEOMETRY_AUDIT_140.md`; they support the receiving source chain, not pixel identity.

**Disposition:** accept #99 as a bounded representative paired A/B housing-entry review. The original 677c images retain their source identity. This does not cover internal service routing or other penetration families.
