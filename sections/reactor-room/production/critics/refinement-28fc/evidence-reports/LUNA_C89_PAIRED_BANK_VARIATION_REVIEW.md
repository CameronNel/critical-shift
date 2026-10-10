# C89 paired-bank variation review

Candidate: C89, scene SHA-256 `099be8168f948915436e200c57939c134dd2c44baec6c68bcc23528425bb420a`.

## Disposition: #100 accepted in its stated scope

The exact-C89 full-quality main05 frame shows both control banks together. Their housings, upper frames and displayed heights read as a deliberately matched pair. `CONTROL BANK A` / `A` and `CONTROL BANK B` / `B` identify the two faces; the lower `CRD-A / MATCHED BANK` and `CRD-B / MATCHED BANK` strips add paired-service identification. The lower B strip is smaller and lower-contrast in perspective, but it remains legible in the original 1280×720 pixels and is not occluded. Inspection19 supplies a closer view of the A-side service face; it is corroboration, not a substitute for the both-bank comparison in main05.

This is the controlled pairing described by the criterion. I do not require deliberately asymmetric bank geometry: both banks are labeled as a matched pair. This acceptance does not close frame-corner construction, service access, housing conduit entry, suspension joints, or other rod-system construction criteria.

## Saved-source corroboration

The exact-C89 `rod-guide.json` reports both banks with the same housing radial bounds (about `0.3445844 m`), guide inner radius (about `0.2472018 m`), and 480 evaluated poses per bank; both bank checks pass with no housing or guide surface intersections. Its scope is housing/guide fit and sampled stem travel, not a complete symmetry proof. The full05 pixels supply the visual matched-pair judgment.

The exact-C89 signage audit records both lower bank ID strips with zero blocked samples: A `110/110`, B `101/101`. The audit verifies label visibility, not physical motion. The earlier C89 #104 report independently documents the label legibility evidence; this report records #100's matched-pair scope.

## Evidence identity

| Evidence | Image SHA-256 | Manifest SHA-256 | Scope |
|---|---|---|---|
| Main05 `05_control_rods_upper.png` | `46e17bd10ddd4e86e5f2f6233019b8ef845663bb205f435ea3fdc15db7d01349` | `98c81e641631091d2674014bb257d3a02c981a9124e56cabd1e2b3b99e4b87ad` | Both banks together, full 1280×720, Cycles 96 max/32 min, 16-bit |
| Inspection19 `19_bank_service_face.png` | `4c41e8ecce7bb39b4c00514b5cbc4d9bd250a5660c1ad02de340b29f69c4d45f` | `be6b0350f0ad6145baca82e5daa6730851feb2c35524dd60ff28c78479ec82e4` | A-side service-face corroboration, full 1280×720, Cycles 96 max/32 min, 16-bit |

Geometry report `/workspace/scratch/reactor-refinement-cycle89/rod-guide.json`, SHA-256 `8ca34a5865732d72f7d6456513d285408a4e057429eab16a749b3f1a9ebfae4a`; signage audit `/workspace/scratch/reactor-refinement-cycle89/audit.json`, SHA-256 `a0fbaac8de6b62d7d6d49f582e05d4f63c78dbe5b83289315fef2d0ee3740537`.
