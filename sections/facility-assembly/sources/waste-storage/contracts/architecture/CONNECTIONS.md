# Waste Storage connection and topology contract

Local origin is the receiving opening's interior threshold center. +Y enters the hall; +Z is up. All measurements are metres. Clear room: X −6…6, Y 0…18, Z 0…4.8. Walls are 0.32 thick. Door dimensions are clear width × height.

| ID | Center | Outward normal | Opening | Owner / binding |
|---|---|---|---|---|
| WS_RECEIVING | (0,0,0) | (0,−1,0) | 3.0 × 3.2 | Waste rolling shutter; measured Electrical D02 proposal |
| WS_PERSONNEL | (6,2.4,0) | (1,0,0) | 1.2 × 2.3 | Waste outward leaf; clean service network unbound |
| WS_DISPATCH | (0,18,0) | (0,1,0) | 2.4 × 2.8 | Waste rolling shutter; onward freight/service network unbound |
| WS_MONITOR_BOOTH | (−2.4,2.2,0) | (1,0,0) | 1.1 × 2.3 | Waste internal glazed inward leaf |
| WS_POWER | (6.32,16.8,3.6) | (1,0,0) | 0.20 × 0.20 | Waste capped boundary sleeve; low-voltage source unbound |
| WS_EXTRACT | (−4.8,18.32,4.0) | (0,1,0) | 0.65 × 0.60 | Waste capped duct face; facility extract network unbound |
| WS_DATA | (−6.32,1.2,2.8) | (−1,0,0) | 0.12 × 0.12 | Waste capped data sleeve; network unbound |

## Electrical alignment

The read-only saved-artifact survey is `electrical-saved-survey.json`, source SHA256 `01447dce65a406afa84448e440176aefd37cdda702dc0a4cd51cee366c298dfd`. It measures Electrical D02 at (0,16.4,0), exterior Y16.65, with a 2.4 × 2.7 opening. Its `Waste seam slab` covers X±1.5 and Y16.4…16.97, top Z0.

Proposed Waste transform in Electrical coordinates: translation **(0,16.97,0)**, rotation Z **0°**. Waste's receiving exterior Y−0.32 becomes Electrical Y16.65. The joined clear opening is therefore **2.4 × 2.7**, not 3.0 × 3.2. Both floor elevations are Z0.

Electrical owns the threshold floor through Waste's local Y0. Waste removes its duplicate slab only in X±1.5, Y−0.32…0. Each module retains its own wall. The owned room floor starts at Y0; a freestanding Waste scene does not claim support on the unassembled Electrical side of that seam. No Electrical geometry was edited or imported. This is a measured placement proposal, not whole-map assembly certification.

## Circulation topology

Electrical D02 → WS_RECEIVING → receiving/scan apron → central freight spine → selected storage cell or repair/extraction service → WS_DISPATCH → future service network toward Medical and Compliance. WS_PERSONNEL supplies a separate worker branch from the receiving apron. Two-person carry uses receiving/dispatch, not the narrow personnel branch.

Fuel Corridor S03_WASTE is a reserved 2.4 × 3.0 connection at its own (16.4,16,0), outward +X. It has no shared transform here. It should join shared freight circulation rather than create an invented second receiving door. Medical's evolving single 2.2 × 2.5 entry and Compliance's 2.4 × 2.6 entry require connector-owner reconciliation. No direct wall mating is asserted.

## Door states and reservations

Receiving and dispatch shutters are fully parked above their openings. Personnel hinge is (6.36,3.065,0): closed −90° Z, open 0°. Its exterior swing reservation is approximately X6.32…7.65, Y1.80…3.14; the leaf is Waste-owned and the future neighbor must keep this space clear. Booth hinge is (−2.48,2.815,0): closed −90°, open −180°. Cell gates retract into captive side housings; no fixed crossbar crosses an open cell entrance.

The physical artifact contains host-state anchors; opening/closing gameplay, locks, capacity, transfer, contamination, sound and incident behavior are engine work. Static measured clearance is not a runtime physics test.

