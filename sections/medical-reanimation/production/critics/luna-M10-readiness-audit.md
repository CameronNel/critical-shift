# Independent Luna M10 readiness audit — pre-pixel evidence

Reviewer: Luna (independent)

Scope: current M10 architecture/integration contract, requirements, checklist, interface, technical validation, interaction validation, sign/contact audits, cold fingerprints, source replay, and live-open record. The M10 final fixed renders and five M10 state renders were not yet supplied when this audit was written. The prior M09 final folder is not treated as M10 evidence.

**Status: evidence audit only; no scene approval and no visual score claimed.** The final visual gate remains strict `>90` in every applicable category and requires actual M10 pixels, including the fixed pack and state views.

## Evidence snapshot

| Evidence | Result | What it establishes |
|---|---|---|
| `validation/M10/technical.json` | PASS, 13/13 checks | Finite geometry, 23 assigned materials, required equipment, floor, 14 player-height cameras, roots, player/cart routes, openings, utility markers, hooks, saved bytes, dependency audit |
| `validation/M10/interaction.json` | PASS, 5/5 checks | Two-person carry, dropped-body bypass, dropped-cart bypass, transfer contact design, opposed door stroke |
| `validation/M10/signs.json` | PASS | Plaque fit and local front-obstruction audit, including new `DECON`/`BEFORE LOADING` treatment |
| `validation/M10/contact_candidates.json` | PASS / isolated `[]` | No conservative evaluated AABB contact candidates; text and oblique pixel readability remain separate checks |
| `validation/cold-A.json` | M10 fingerprint | Blend SHA `e7480f...b99ea9a0`; state SHA `2725a1...e3b668bd7` |
| `validation/cold-B.json` | Matches cold-A | Same M10 blend and state fingerprints |
| `validation/source-replay.json` | State match | Replay state SHA matches cold-A/B; replay blend SHA is a separate generated artifact |
| `validation/live-open.json` | Clean | M10, 1203 objects, 14 cameras, no dirty readback, lease released; only Blender built-in Bfont is reported as a dependency interpretation limitation |

The hashes above are recorded as abbreviated identifiers for readability; the JSON files remain the evidence authority.

## Requirement and integration audit

### Layout, topology, and inherited placement

`INTEGRATION.md`, `REQUIREMENTS.md`, `CHECKLIST.md`, and `interface.json` agree on the preserved R09 baseline: an 8 × 9 × 3.6 m hall, 1.70 × 2.12 m rear decon extension, 2.20 × 2.50 m single entry, west OCRU, rear console/cartridges/reserve, east recovery/supplies, and southwest cart parking. The connector-owned clean-service junction and Waste/service topology remain unbound; no neighboring-room transform is invented. The technical floor, root support, opening, route, and marker checks pass.

This establishes contract consistency and measured static evidence. It does not establish the final M10 image scores until the actual fixed views show the arrangement and its camera readability.

### Required machinery and equipment

The M10 technical report marks all required equipment present: OCRU, adult berth, body cart, restart console, cartridge bank, reserve power, recovery berth, supply bench, supplies, decontamination, and handwash. The checklist also calls for the OCRU transfer bridge, suit service, physical restart controls, monitoring, maintenance access, decon drain/extract, consumable stock, and recovery artifacts; the current technical scene includes the corresponding roots/hooks and the M10 source manifest records 1203 objects.

Presence is a static implementation result. Machinery construction, operation readability, material separation, and authored Valorant quality remain pixel-gated.

### Construction and measured physical envelope

The interface contract records the adult berth at 2.20 × 0.88 m with 1.02 m surface height, cart at 2.10 × 0.74 × 0.92 m, 1.20 m internal decon opening, and five owned capped utility interfaces. Root-support and exact-marker checks pass. The interaction report records a 0.088 m cart lift, 1.008 m cart/bridge surface design, 12 mm cushion step intent, and no obstructions in the tested static paths.

There is one consequential margin risk. The measured cart lateral extraction passes about **5 mm ahead of the OCRU envelope at Y=2.475**. That is an authored constrained path, not a free-turning clearance. A 5 mm margin is too small to call robust integration readiness by itself: small collider, pose, or host-sweep tolerance can turn the passing static case into a snag. This is not a demand for a room relocation or a coordinate recipe. The host must preserve the tested authored path and recheck it with the final state poses and the actual interaction tolerances. If that margin cannot be held in the integrated runtime, the physical-envelope category cannot clear the strict gate.

The separate 1.5275 m rear service band is materially better documented and is suitable for the service-access review, subject to final pixels.

### Host hooks and runtime boundary

`interface.json` lists hooks for OCRU load, suit port, cartridge, restart, power, maintenance, decon wand, recovery exit, compliance lock, and medical audio. The contract assigns authority/network replication, occupancy, power cost, inventory, sequencing, contamination, locks, ragdoll physics, and temporary debuffs to the host. The interaction report explicitly says no engine navmesh/network/state implementation is asserted.

These are appropriate local integration hooks. They support a room-art readiness review without pretending that Blender implements the game loop. Final state images are still needed to inspect pose correctness, visible contacts, labels, and obstruction evidence.

### Signage and readability risk

The M10 sign audit passes local plaque fit and reports no front obstructions, including `DECON` and `BEFORE LOADING` on the revised backing. That is useful evidence that the former M09 wand obstruction was removed from the local construction. The audit itself states its limitation: it does not prove player-view legibility in oblique renders. Actual `CAM_DECON`, `CAM_MAINT`, and state pixels remain mandatory. Canonical identity remains **Organic Continuity and Recommissioning Unit (OCRU)**; no generated long-name replacement is authorized.

### Materials, lighting, color, and storytelling

The technical report confirms 23 assigned materials and a saved M10 source with no missing external texture/library dependency beyond the documented built-in Bfont interpretation. The contract and requirements preserve the neutral grey/graphite/orange direction and explicit no-teal rule. These facts establish scene setup and dependency readiness only. Materials, lighting hierarchy, restrained wear, environmental storytelling, and strict Valorant fidelity must be judged from actual M10 pixels.

## Pixel-gated categories

The following categories are required for the final review. Scores are deliberately withheld until M10 images exist; assigning numbers from JSON or cold fingerprints would fabricate visual evidence.

| Category | Current non-pixel evidence | Pixel status |
|---|---|---|
| Layout / scale / circulation | Contract, roots, floor, player/cart routes pass | Unverified |
| Machinery / operational readability | Required equipment and hooks pass | Unverified |
| Materials | 23 assigned materials pass | Unverified |
| Lighting hierarchy / contact | Scene saved; contact candidate list empty | Unverified |
| Color discipline / no-teal | Direction and material inventory support it | Unverified |
| Environmental storytelling | Checklist equipment/artifact inventory present | Unverified |
| Label / sign readability | Local sign audit passes; oblique limitation remains | Unverified |
| State-pose / physical-envelope evidence | Interaction checks pass; 5 mm extraction margin is conditional | Unverified |
| Spec/procedure fidelity | Contract covers retrieve → decon → load → suit → power → cartridge → restart → monitored recovery | Unverified |
| Equipment completeness | Technical required-equipment check passes | Unverified |
| Construction specificity | M10 source includes authored equipment roots/parts | Unverified |
| Camera readability | 14 camera registrations pass | Unverified |
| Static state evidence | Cold-A/B and replay fingerprints match | Unverified until state pixels |

Every applicable category must score strictly greater than 90 in the final pixel review. The current audit does not grant any category a visual score.

## Required evidence before final review

1. M10 final fixed pack: all 14 named renders with manifest.
2. M10 state pack: five corrected state renders, including the transfer pose and bypass/decon/closed-entry/reserve views.
3. Confirmation that the M10 final render manifest and image hashes correspond to the M10 source, rather than the prior M09 folder.
4. Pixel inspection of `CAM_DECON` and `CAM_MAINT` for the revised `DECON`/`BEFORE LOADING` signage from their actual oblique cameras.
5. Pixel inspection of transfer support/contact and the constrained cart extraction in the corrected state pose.
6. Final cold-open and source-replay comparison retained alongside the image evidence.

**M10 is technically promising and internally coherent, but this audit records no approval. The 5 mm cart extraction margin is the one consequential integration risk already visible in the static contract; all visual categories remain open until actual M10 pixels are reviewed.**

### Pixel coverage correction added after the M11 review

The required header coverage was misattributed in this pre-pixel checklist. The actual `DECON` / `BEFORE LOADING` header is judged in `CAM_ENTRY` and `CAM_ROUTE`. `CAM_DECON` and `CAM_MAINT` are machinery/service views; they must verify the removed fixture plaque, clear wand/reel/PPE construction, and usable maintenance reading. This correction preserves the audit history and does not retroactively score M10.
