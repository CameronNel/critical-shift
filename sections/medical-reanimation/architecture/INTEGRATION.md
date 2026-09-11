# Medical / Reanimation integration contract

This is an original art rebuild around Grok's R09 saved room arrangement. The original `ocru.blend` is preserved; its SHA-256 and evaluated survey are recorded in `interface.json` and `existing-saved-survey.json`. No original mesh was imported or edited. The exact inherited hall and decon footprint remain unchanged. Scene units are metres, threshold origin `(0,0,0)`, inward `+Y`, up `+Z`.

## Owned boundaries

| Identifier | Center / threshold XYZ | Outward normal | Clear size | Ownership |
|---|---|---|---|---|
| main_entry | (0,0,0) | (0,-1,0) | 2.20 W × 2.50 H | Medical owns wall, frame, two sliding leaves; exterior face Y=-0.18 |
| MED_POWER | (-2.15,9.18,2.65) | (0,1,0) | 0.20 × 0.20 reserved interface | Medical capped termination |
| MED_DATA | (-0.40,9.18,2.65) | (0,1,0) | 0.12 × 0.12 reserved interface | Medical capped termination |
| MED_WATER | (3.36,10.70,0.60) | (1,0,0) | 0.12 × 0.12 reserved interface | Medical capped termination |
| MED_DRAIN | (2.33,11.30,0.15) | (0,1,0) | 0.15 × 0.15 reserved interface | Medical capped termination |
| MED_EXTRACT | (2.33,11.30,2.25) | (0,1,0) | 0.40 × 0.30 rectangular sleeve | Medical capped termination |

Utility sizes describe reserved mounting/interface envelopes; the small round cap is not a claim that the whole envelope is a pipe bore. Read exact `IF_*` markers and their normals from the saved scene. The decon opening is internal: X=1.55..2.75 at Y=9, floor Z=0, clear height2.15. It does not add an external portal.

## Topology without moving neighbors

Fuel Corridor `S02_CLEAN` is a separately measured, unbound header at its own `(6.6,21,0)`, outward `+Y`, clear2.00×2.50. Waste `WS_DISPATCH` is at its own `(0,18,0)`, outward `+Y`, clear2.40×2.80. These local coordinates must not be mistaken for a shared global placement. A connector-owned clean service junction can serve Medical and Compliance while preserving Waste/service circulation. Do not make Medical the mandatory route through Waste discharge. No global transform is asserted; connector ownership must resolve junction shape, translation, rotation, utilities and runtime connectivity. Effective corridor width remains2.00m if S02_CLEAN is used, despite Medical's2.20m entry.

## Layout and access

The8×9×3.6m hall,1.70×2.12m rear decon alcove, west OCRU, rear console/stock/reserve, east recovery/supplies and southwest cart parking are inherited. Artwork adds service projections beyond reserved rectangular equipment bodies; actual evaluated extrema are recorded in the technical report. Treat those extrema as authoritative collision input, not the simplified plan rectangles. The existing northeast PowerPanel reservation now contains the local isolation panel.

The cart is nominally2.10m long and0.74m wide; the conservative sweep includes its plaque projection, using2.124m length. Extract the parked cart sideways from(-3.12,1.33) to(0,1.33), without first shifting it toward the OCRU. The M11 entrance hardware sits closer to its wall so the cart clears both parked leaves and the OCRU end. The stool parks under the rear console. A5m retractable decon wand reaches the adjacent cart apron; do not force the full cart to turn inside the1.20m internal opening. The standing decon route is separate from the cart wash position.

Measured M11 clearance notes: the OCRU rear envelope ends at Y6.785 and the reserve cabinet begins at Y8.3125, leaving a1.5275m rear service band. The OCRU's forward control projections reach X=-1.17860; the recovery assembly begins at X=2.665, a3.8436m bounding separation across the central room. Do not mistake this for a uniform empty rectangle: cart and transfer poses occupy part of it. The tested two-person carry envelope is1.80m wide, leaving0.20m per side at the2.20m entry. A0.60m player envelope leaves0.30m per side through the1.20m internal decon opening. The cart extraction now provides approximately95mm to the OCRU envelope and109mm to the leaf's foremost trim, replacing the rejected5mm margin. A separate sweep expands the conservative cart envelope by75mm on every side. Runtime handling should retain lateral extraction rather than assume free turning in the parked bay.

The OCRU adult berth is2.20×0.88m at Z=1.02. At transfer, cart center is(-1.08,4.63,0), the deck lift is0.088m, cart surface Z=1.008, and bridge surface Z=1.008. A slide-assisted bridge pivots from its under-tray parked position. The static transfer design allows12mm to the berth cushion top. The host must implement the lift/bridge interlock, occupancy and body handling; the art package supplies editable roots and evidence poses.

## Host behavior

`HOOK_*` anchors cover load, suit coupling, cartridge insertion, physical restart, power/reserve, maintenance, decon, recovery exit, compliance lock and audio. Required host sequence: retrieve worker; remove gross contamination; load adult berth; service suit; establish power; consume cartridge; perform restart; run vulnerable monitored cycle; return worker with temporary debuff. Power loss pauses recoverably. Repair, compliance lock and identity/firmware failure must remain recoverable states. Runtime owns authority, network replication, inventory, energy cost, ragdoll physics, navmesh and state transitions. The Blender scene does not implement that game logic.

The delivered open door state is suitable for inspection. Closed entry leaves slide1.12m each inside their owned housing. The reserve service door can open for battery access. These are editable art mechanisms and demonstrated poses, not an assertion of motor or clinical engineering certification.

## Limits

Specific conservative player/cart/carry paths and dropped-body/cart bypass scenarios are measured. They do not prove every possible dynamic ragdoll arrangement. Because this modest room has one external entrance, host interaction must always allow recovery or repositioning of an obstruction at that entrance. Whole-facility circulation and runtime integration require the neighboring modules and connector transform to be assembled and tested.
