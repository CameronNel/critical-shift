# Independent Luna M11 clearance audit — pre-pixel review

Reviewer: Luna (independent)

Scope: M11 measured entry/cart correction, updated integration contract, M11 technical and interaction validation, signs/contact audits, and the M11 saved build manifest. The M11 fixed render pack and six M11 state renders were not yet available when this audit was written. The cancelled M10 render queue and prior final folders are not treated as M11 pixel evidence.

**Status: pre-pixel clearance review; no scene approval and no visual score claimed.** The final report remains `production/critics/luna-scene-M11.md` after the M11 manifest and all 14 fixed plus six state images are supplied. Every applicable final category must still score strictly greater than 90.

## Disposition of the prior 5 mm risk

The M10 contract recorded an approximately 5 mm cart extraction margin at the OCRU end. I flagged that as consequential because a static pass with almost no margin could become a snag under collider, pose, or host sweep tolerance.

M11 addresses that specific risk by moving only the entry hardware depth inward: leaf roots are now at Y=0.10, the capture housing is within the wall envelope, and the main-entry threshold, clear width/height, exterior ownership, and all other room/equipment placements remain unchanged. The cart now extracts laterally at the original Y=1.33 path without the earlier rearward jog. The updated contract records approximately:

- **95 mm** clearance to the OCRU envelope
- **109 mm** clearance to the foremost door trim
- a separate **75 mm padded sweep** around the conservative cart envelope

The validator uses the conservative 2.124 m cart length including plaque projection and reports five cart paths passing. This is a materially safer margin than M10 and resolves the prior static-clearance objection at the measured-envelope level. It still requires the final state pose and actual host interaction tolerance to be visually and operationally checked; the margin is evidence of clearance, not a claim that runtime collision or ragdoll behavior is implemented.

## M11 non-pixel evidence

| Evidence | Result | Review interpretation |
|---|---|---|
| `validation/M11/technical.json` | PASS, 13/13 checks | Finite geometry, assigned materials, required equipment, floor, cameras, roots, player/cart routes, openings, connection markers, hooks, source bytes, dependencies |
| `validation/M11/interaction.json` | PASS, 5/5 checks | Two-person carry, dropped-body bypass, dropped-cart bypass, transfer contact design, opposed door stroke |
| `validation/M11/contact_candidates.json` | `isolated: []` | No conservative evaluated AABB contact candidates; final pixel contact review remains required |
| `validation/M11/signs.json` | PASS | Plaque fit and local front-obstruction audit; oblique camera readability remains open |
| `checkpoints/M11/build_manifest.json` | M11, 1203 objects | Saved source and listed script fingerprints identify the M11 build |

The interaction report retains the correct limits: the tests cover specific static recoverable arrangements, do not cover every ragdoll pose, and do not assert host navmesh/network/state implementation.

## Requirement and integration assessment

### Entry and cart envelope

The updated `architecture/INTEGRATION.md` preserves the original 2.20 m × 2.50 m main entry and medical ownership while reducing only the hardware projection into the room. The lateral extraction path starts from the original cart parking Y=1.33 line and avoids the prior rearward jog. The new 95/109 mm margins plus 75 mm padded sweep are sufficient to remove the earlier 5 mm static risk from the art/integration gate, provided the final state pose uses the same authored path.

No neighbor room is moved, and no global connector transform is invented. The measured rear service band remains 1.5275 m. The exact external connection and host-hook contracts remain unchanged.

### Static equipment/spec contract

M11 technical validation still reports the complete required equipment inventory and 23 assigned materials. The interface/checklist contract still covers the adult OCRU berth, cart transfer, suit service, cartridge receiver and bank, physical restart controls, monitoring, normal/reserve power, maintenance, decon wand/drain/extract, recovery berth, supply bench, and handwash. The procedure remains a host sequence: retrieve → decon → load → suit service → power → cartridge → physical restart → monitored recovery.

These checks establish static presence and contract readiness. They do not create visual scores for construction, readability, materials, lighting, or storytelling.

### Sign and decon correction

The M11 sign audit passes local fit and front-obstruction checks, including `DECON` and `BEFORE LOADING`. This directly addresses the M09 oblique-view failure by removing the fixture-level long label and using the enlarged supported threshold backing. Because the audit itself warns that local geometry does not prove an oblique player view, `CAM_DECON`, `CAM_MAINT`, and the relevant state view must be inspected from actual M11 pixels before the label category can pass.

### Static art versus runtime responsibilities

The M11 scene supplies editable geometry, support roots, state poses, connection markers, and host hooks. Runtime remains responsible for authority/network replication, occupancy, power and cartridge state, contamination, compliance locks, ragdoll physics, navmesh, temporary debuffs, and recovery/repositioning at the single entry. The 95/109 mm clearance and five passing static cart paths are art/integration evidence; they are not proof of runtime implementation.

## Pixel-gated final categories

No visual scores are assigned before the M11 images arrive.

| Category | Current evidence | Pixel status |
|---|---|---|
| Layout / scale / circulation | Preserved contract, updated entry hardware, routes pass | Awaiting M11 pixels |
| Machinery / operational readability | Required equipment and hooks pass | Awaiting M11 pixels |
| Materials | 23 assigned materials | Awaiting M11 pixels |
| Lighting hierarchy / contact | Static setup and isolated contact candidates pass | Awaiting M11 pixels |
| Color discipline / no-teal | Requirements and source contract preserve rule | Awaiting M11 pixels |
| Environmental storytelling | Checklist inventory and room contract complete | Awaiting M11 pixels |
| Label / sign readability | Local audit pass; oblique limitation remains | Awaiting M11 pixels |
| State-pose / physical envelope | 95/109 mm margins; five cart paths pass | Awaiting M11 state pixels |
| Spec/procedure fidelity | Contract covers the complete chapter 5 flow | Awaiting M11 pixels |
| Equipment completeness | Technical required-equipment check pass | Awaiting M11 pixels |
| Construction specificity | M11 source/build manifest and authored roots present | Awaiting M11 pixels |
| Camera readability | 14 cameras registered | Awaiting M11 pixels |
| Static state evidence | Interaction checks pass; six state renders pending | Awaiting M11 state pixels |

## Required before final M11 review

1. M11 manifest identifying all 14 fixed renders and six state renders.
2. Pixel inspection of `CAM_DECON` and `CAM_MAINT` for unobstructed `DECON` and `BEFORE LOADING` text from the actual oblique cameras.
3. Pixel inspection of `S06_CART_EXTRACTION` and the other five state views, including cart/OCRU/door contact and the corrected 95/109 mm path.
4. Cold-A/B and source-replay evidence tied to M11, with matching source/state fingerprints.
5. Final category scores and per-view scores in `luna-scene-M11.md`, with no score inferred from technical JSON.

**M11 resolves the prior 5 mm clearance objection at the measured static-envelope level. No final approval is possible yet: actual M11 fixed and state pixels remain required, especially the revised decon signage and the new cart-extraction state.**

### Pixel coverage correction added after the final review

The earlier required-evidence wording asked `CAM_DECON` and `CAM_MAINT` to prove the revised `DECON` / `BEFORE LOADING` header. That attribution is incorrect. The header is visible and judged in `CAM_ENTRY` and `CAM_ROUTE`; `CAM_DECON` and `CAM_MAINT` judge the corrected removal of the obstructed fixture plaque and the service machinery/readability. This is an explicit correction to the pending checklist, not a silent rewrite of the pre-pixel record.
