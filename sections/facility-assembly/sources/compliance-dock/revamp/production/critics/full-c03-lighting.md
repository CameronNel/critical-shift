# Full cycle 03 — independent lighting review

**Category 5: 89/100. FAIL against the strictly >93 category gate.** This is a lighting score only; it does not certify an overall score, technical quality, runtime lighting or final acceptance.

Source SHA256: `1e2507dc6f0c245cc6552d940a03fe6888949f68509bdbaacd7f315c22815b53`. The beauty manifest was `complete=true` with 27 shots. All 27 actual PNGs were individually opened with `view_image`; all 27 image hashes match the complete manifest. The four actual spawn-reference originals were also individually opened. No prior reviews, scores, builder code or rationale were used.

The warm check-in and office practicals establish convincing working areas against the cooler inspection bay. The dark ceiling gives depth, practical fixtures visibly affect nearby structure, contact shadows ground equipment, and small indicators avoid overwhelming the room. WALL_OFFICE_FRONT, C03_CHECKIN_COUNTER and DETAIL_CHECKIN demonstrate the clearest lighting hierarchy. The exposure remains usable across the fixed views.

The score stops at 89 because the broad main-bay illumination merges the approach, inspection threshold and background floor into a near-continuous value field. The machinery is readable, but local lighting does not consistently separate its functional surfaces. The cargo front, roller bed and operating side need more directional definition; the warm support bay lights its wall more effectively than the trolley undercarriage; the sealed arrival gate has weak structural separation. These are visible shortcomings against the spawn references' distinct practical pools and the brief's requirement to expose important forms while keeping storage dim.

## Critical vetoes

None in the lighting discipline. The dominant read is not flat even lighting: warm/cool zoning, dark ceiling masses and local practical response are present. No important route is blacked out. The remaining deficits still fail the stricter category gate; absence of a critical veto is not a pass.

## Exact failing views at the lighting gate

| Views | Visible defect |
| --- | --- |
| C01_ENTRY, C02_HERO_DOCK, C04_SCANNER_APPROACH, HERO_SCANNER | Broad floor and wall fill weakens the inspection threshold's local pool. Bright header and coloured indicators provide stronger guidance than light on the functional inner faces. |
| C05_CONVEYOR_LEAD_TUNNEL, HERO_CARGO | Cargo face, front curtain, rollers and lower frame crowd the dark range. The blue side receives clearer definition than the cargo-facing work surface. |
| C06_CART_GATE_G1, PLAYER_REVERSE | Dark gate leaves and supporting posts lack consistent directional separation. Reverse lighting places stronger accents on overhead members than on the gate's functional faces. |
| C08_CONCEALED_SUPPORT_H1, HERO_TROLLEY | Wall illumination exceeds the useful light on the trolley. Lower rail, shelf and caster construction merge into near-black masses, especially in C08. Concealment can remain dim while retaining form. |
| C09_ARRIVAL_GATE_P2 | Door leaves, centre joint and frame sit too close in value. Small amber overhead accents do little to articulate the large manufactured surface. |

CORNER_SW, CORNER_SE, CORNER_NW and CORNER_NE confirm the broad floor illumination and stronger top lighting on the cargo machine; their cutaway treatment is contextual evidence, not a substitute for the player-height defects above.

## Four concrete fixes within the preserved layout

1. Rebalance and aim the existing bay practicals so the scanner threshold and cargo working zone have distinct soft pools. Reduce spill across the approach and interstitial floor without lowering route readability. Verify C01, C02, C04 and HERO_SCANNER together.
2. Redirect a restrained practical or bounced component across the cargo-facing curtain, crate latches and roller bed. Preserve the dark tunnel interior, but separate the curtain edges and lower frame from it. Verify C05 and HERO_CARGO.
3. Add low, soft indirect fill to the support bay from its existing practical lighting. Lift the trolley's lower rail, shelf and caster silhouette just enough to show construction and floor contact, while keeping this area darker than check-in. Verify C08, HERO_TROLLEY and HERO_EVIDENCE.
4. Give the arrival gate and cart gate restrained grazing definition from existing nearby sources. Reveal the centre joint, frame depth and gate-leaf edges; keep the arrival gate subordinate to inspection. Verify C06, C09, PLAYER_REVERSE and PLAYER_PINCH.

## Inspected evidence

Beauty PNGs under `renders/full-cycle-03/`: C01_ENTRY, C02_HERO_DOCK, C03_CHECKIN_COUNTER, C04_SCANNER_APPROACH, C05_CONVEYOR_LEAD_TUNNEL, C06_CART_GATE_G1, C07_OFFICE_INTERIOR, C08_CONCEALED_SUPPORT_H1, C09_ARRIVAL_GATE_P2, C10_ROOF_SERVICES, CORNER_SW, CORNER_SE, CORNER_NW, CORNER_NE, WALL_SOUTH, WALL_NORTH, WALL_EAST, WALL_WEST, HERO_SCANNER, HERO_CARGO, HERO_EVIDENCE, HERO_TROLLEY, HERO_UTILITIES, DETAIL_CHECKIN, PLAYER_REVERSE, PLAYER_PINCH, WALL_OFFICE_FRONT.

Actual spawn-reference originals under `renders/spawn-reference/`: VALIDATE_Material_A.png, VALIDATE_LockerDoor.png, VALIDATE_Spawn.png, BRIEFING_INDIRECT.png.

This review writes only its Markdown and JSON records. Layout and source were not edited. A source-linked complete beauty batch proves the reviewed image set; it does not establish cold-open stability or the other production hard gates.
