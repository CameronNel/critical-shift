# C89 lower bank service identification review

Candidate: C89, source SHA-256 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`.

Issue #104 is accepted from the exact-C89 full-quality main05 and bank-service view19. Main05 places the A and B bank faces together in one 1280×720 frame. Both `CRD-A / MATCHED BANK` and `CRD-B / MATCHED BANK` strips are present; the B text is smaller in perspective than A in the closer view19, but is legible in the original unresized main05 pixels and is not covered by a frame rail or adjacent object. The bank headings and large A/B door letters make each lower service label's location unambiguous. View19 gives a close, clear A-side example of the same lower-strip design.

The exact C89 saved signage audit independently records `RH refine bank lower id A` (`CRD-A / MATCHED BANK`, 110 samples, 0 blocked, no occluders) and `RH refine bank lower id B` (`CRD-B / MATCHED BANK`, 101 samples, 0 blocked, no occluders). The shared builder loop in `rh_refine_geometry.py` line 89 generates both labels with the same 0.045 m font size, placement, and material path, varying only the A/B identifier. Audit SHA-256 is `a0fbaac8de6b62d7d6d49f582e05d4f63c78dbe5b83289315fef2d0ee3740537`; builder SHA-256 is `49845b0e65eff9e474e1ddf49ec1b185c2b4d94c16705d5fb91c8003628fc3fa`.

## Exact rendered evidence

| View | Image SHA-256 | Manifest SHA-256 | Quality |
|---|---|---|---|
| Main05 `05_control_rods_upper.png` | `46e17bd10ddd4e86e5f2f6233019b8ef845663bb205f435ea3fdc15db7d01349` | `98c81e641631091d2674014bb257d3a02c981a9124e56cabd1e2b3b99e4b87ad` | 1280×720, Cycles 96 max/32 min, 16-bit |
| Inspection19 `19_bank_service_face.png` | `4c41e8ecce7bb39b4c00514b5cbc4d9bd250a5660c1ad02de340b29f69c4d45f` | `be6b0350f0ad6145baca82e5daa6730851feb2c35524dd60ff28c78479ec82e4` | 1280×720, Cycles 96 max/32 min, 16-bit |

This disposition covers lower bank ID readability and identification only. It does not close bank construction, paired-bank variation, access, suspension, or conduit-entry criteria.
