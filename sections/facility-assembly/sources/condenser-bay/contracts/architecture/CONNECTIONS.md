# Condenser Bay connections

Metres, Z up. Local origin D01. `turbine = local + (1.6, 7.4, −6.0)`.

| ID | Local | Outward | Size | Status |
|---|---|---|---|---|
| D01 / `IF_PORTAL_D01_SERVICE` | (0, 0, 0) | −Y | 2.0 × 2.4 m | Owned opening, leaves parked open. Remote corridor unbound. |
| U04 receive / `IF_LP_EXHAUST_CONDENSER` | (3.00, 4.05, 6.00) | +Z (into bay from turbine) | 2.5 × 1.5 m | Geometric receive of accepted turbine U04. Not an assembled facility join. |
| `IF_CONDENSATE_HANDOFF` | (7.90, 0.00, 5.42) | −Y | Ø 0.2 m class | Local stub only. Turbine U02 cap at (9.5, 0, 0.45) remains turbine-owned. Integrator must continue the line; this module does not cut turbine. |
| `IF_CW_SUPPLY` | (9.60, 3.20, 3.15) | +X | Ø 0.3 m | Capped. Not a proven cooling-plant loop. |
| `IF_CW_RETURN` | (9.60, 4.90, 3.15) | +X | Ø 0.3 m | Capped. Not a proven cooling-plant loop. |
| `IF_DRAIN_OUT` | (9.60, 8.55, −0.08) | +X | — | Unbound. |
| `IF_VENT_OUT` | (3.00, 9.40, 5.55) | +Y | — | Unbound extract. |

Cooling Plant already owns its pump/exchanger room. This bay does not duplicate HX-01 / P-01 / P-02.
