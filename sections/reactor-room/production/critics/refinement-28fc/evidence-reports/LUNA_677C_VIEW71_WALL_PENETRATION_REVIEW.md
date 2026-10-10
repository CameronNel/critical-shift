# 677c full71 wall penetration review

Candidate: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/hall_final.blend`  
Candidate SHA-256: `677c4d090ea416256f267d93b0b79c04724a908a58df8adc7353cedf5f4ef295`

Original full-quality image: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/71/71_bank_wall_sleeve.png`  
Image SHA-256: `0a53622cfbb8fdec3d2588f030b646e44efe3e35143e928171c2bbf7bee70775`  
Manifest: `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/proof/green/71/render_manifest.json`  
Manifest SHA-256: `870b9b6df8c4b416d700f41e8375d708d1550c0bf3f60be77f26ddc7bcf8e64d`  
Renderer SHA-256: `947afcf6fc717519d2bafd01547595003da0a267a240935e12f3f6c202341453`  
Profile: 1280×720, Cycles CPU, 96 max / 32 min adaptive samples, exact 0.015 threshold, 16-bit RGB, OIDN, 12 bounces, path guiding, exposure 0, preview=false.

## Visual finding for #90

The bank A red pipe visibly enters the raised annular wall sleeve. The square mount plate, four corner fasteners, stepped annular escutcheon and recessed dark inner ring are all visible. In this frame the black annular area reads as the shadowed/recessed seal bore inside the raised sleeve, rather than a pipe floating outside an unframed wall hole. The narrow dark circumferential line on the straight-to-elbow transition reads as a joint seam; it is away from the wall mouth and does not appear to separate the pipe. No visible unsupported gap or malformed sleeve edge is evident at the actual penetration.

This is a representative visual check for the shared sleeve construction family, not a claim that every port has been viewed from every angle.

## Exact-source family corroboration

The helper `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/scripts/rh_services.py` (SHA-256 `61422e6216e7b944941d381d073b75781e7b9afb3ad05e243d755de52c0208a8`) creates one shared hollow annular sleeve/seal, bored escutcheon, square mount plate, four wall-bearing legs and four bolt heads for all eight active receivers. The family review `/workspace/critical-shift/sections/reactor-room/production/overhaul-R1/review/LUNA_677C_WALL_PENETRATION_FAMILY_REVIEW.md` (SHA-256 `30894677056a9f32e6fc236fff567f858c607265a6c9af6448bc0681115ea902`) maps view71 to the north bank A service port at (2.9, 10.8, 8.9), not bank B.

The exact-source wall-bore record `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/wall-bores.json` (SHA-256 `ef52cbde29383d7ed92c68a60662bad189be751216cff183ca174905f7625ae0`) reports 65/65 rays per each of eight named routes, with no enclosure-layer hits. The exact-source support audit `/workspace/scratch/reactor-refinement-hoist-anchor-lit-working/audit.json` (SHA-256 `15050f5b42a6556246fb5d0c8bc9bea336a47b99293a170b8be223631b25c8bd`) has zero support failures; the family review identifies eight pipe-to-seal contacts and 32 escutcheon-leg-to-plate contacts. These finite checks support the eight instances; they do not replace the visible construction evidence or claim exhaustive collision coverage.

**Disposition:** accept #90 for the current shared wall-service sleeve family. The bank A full71 image supplies the visible construction evidence, and the exact-source fit/support records cover the other seven fitted instances. No additional distinct sleeve construction family is identified.
