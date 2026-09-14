# Condenser Bay equipment / contract checklist

Map of handover scope to named scene objects. Scenic only; not certified engineering.

| # | Requirement | Scene representation | Camera |
|---|---|---|---|
| 1 | Distinctive condenser receiving U04 | `CD shell`, steam chest, bellows neck, `IF_LP_EXHAUST_CONDENSER`, hotwell, waterboxes, piers | C02, C04 |
| 2 | Condensate collection and return | hotwell, level glasses, CEP-A/B, suction/discharge, `IF_CONDENSATE_HANDOFF` | C05 |
| 3 | Cooling-water supply/return | east headers, isolation wheels, gauges, capped `IF_CW_SUPPLY`/`IF_CW_RETURN` | C06 |
| 4 | Maintenance access / lifting | south/east stairs, gallery structure datum z 3.90 with walking surface near 3.94, yellow hoist, east service reserve, davits | C08, W07, W08 |
| 5 | Operator/service station | OP enclosure, gauges, guarded switches, CSB-01 identity | C07 |
| 6 | Drainage / floor protection | east trench + grates, sump + pump, CD drip pan | W04, C03 |
| 7 | Complete architecture | walls, dado, columns, ceiling slab with real U04 hole, girders, extract fan | C01, C09 |
| 8 | Usable access / module bounds | D01 2.0×2.4 parked-open sliding leaves, real opening, unbound connector documented | C01, W01 |
| 9 | Dressing / labels / tools | cart, PPE, extinguisher, shift log, tool cabinet, cone, painted IDs | C10, C07 |

## Explicit non-claims

R34 saved geometry is measured in `validation/R34/saved-measurements.json`; the expanded saved audit passes its disclosed bore, named support, route, gallery, cart delivery and stair tests. Saved SHA256: `26edf558d2e03b16b841940d20973b74017a52e9f8c0c320d5ff5487c9d9ea3b`. Local visual acceptance is complete after two independent Luna rounds strictly above90; see FINAL_HANDOFF.md for evidence and the disclosed cross-round GPU variance. Wider local-interface, roof, glass, workbench and support views supplement the fixed 18 cameras; a labelled section view is required to expose the internal U04 opening without hiding walls in player views.

- Turbine U02 cap is **not** removed.
- CW flanges do **not** prove a cooling-plant loop.
- No RPM/MW/pressure ratings.
- No engine collision, navmesh, networking, or whole-map assembly.

