# 677c finite geometry/support review (#140)

**Candidate:** `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
**Source SHA-256:** `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`  
**Status:** accepted only for the declared finite current/cold QA scope. No final score or full-scene collision claim is made.

## Current and cold authored checks

- Current build: 14/14 checks pass; separate control-room verifier passes.
- Cold build: 14/14 checks pass; separate control-room verifier passes.
- The cold owned-scope file reports 93/93 declared comparisons matched. This is a finite owned-scope comparison; it is not whole-scene equivalence.
- Current audit: 203 sampled signage records with 0 blocked; 3473 sampled support/contact records with 0 failed; 290 protected objects unchanged. These are finite samples and registered contacts, not exhaustive pairwise collision detection.

## Added hoist tasklight interfaces

The exact 5fd→677c scene delta adds three objects—tasklight housing, diffuser lens, and maintenance LED—with no retained-object changes, 1,951 unchanged objects, and no unexpected changes. The independent Blender 5.2.2 probe checks the exact saved 677c hash. The steel housing and lens are closed positive-volume meshes; their faces have assigned materials. Two housing-frame contacts are within 0.48 μm and two lens-housing contacts are coincident. All three objects parent to the retained moving trolley body and preserve their parent-relative transforms at sampled frames 1, 150, 450, and 900. The 1.2 W warm-neutral area light is aimed at the clamp tops and direct rays first hit those clamps.

The inspected 480×270 preview of view70 supports proceeding with the full-quality view, but closes no appearance criterion. The new light is localized and changes nearby appearance; #133, #136, and #137 remain reopened until exact-source pixels are reviewed. #108 and #116 remain open for the full view70 and bounded composite review.

## Hash-bound artifacts

| Artifact | SHA-256 |
|---|---|
| Scene delta 5fd→677c | `10058827bfc2ae32887862b2938f41490ec02d0d78630e0ddf9f0d126960b2b1` |
| Current checks | `471d4c83870b4935cf5a15f64e85d20fd370b7d061533991634fd176fffe1184` |
| Current control-room result | `64b529723f388a810e513441e3293e4413f9cebe0a747b62154166583ba59c92` |
| Current audit | `15050f5b42a6556246fb5d0c8bc9bea336a47b99293a170b8be223631b25c8bd` |
| Cold checks | `da64cfd6086724989477fdeca2fdc4cf8470dea471fb30a520cdd511a2d4e31d` |
| Cold control-room result | `c3c10a8f821bd86b8a0bfe38d5cd6f834e07d1a33c76f5e8cc629a8d43ece071` |
| Cold owned scope (93 declared comparisons) | `21859b1895007e07e2b6547d1dcb1483296d2fe4c2a23694707671347dfd64a5` |
| Independent probe result | `ceb40cf5e7624ea2512b19950f6de0f63a8a92530755529e68956db2adf7b297` |
| Independent probe script | `4431ec375a7246f0a52734ca290b948fb97bbd2205d7e9fc95aa643871c58142` |
| View70 calibration preview | `0239e3369d38ede37e0fa038e1f76fa259223024e5c8a6b8ebca08aeb339d453` |

The full chain and original pixel/source identities are recorded in [`LUNA_677C_BOUNDED_CARRY_REVIEW.md`](/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_677C_BOUNDED_CARRY_REVIEW.md).
