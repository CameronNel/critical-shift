# Waste Storage — metric architecture

The module is a maintained waste receiving, segregation and controlled dispatch workplace. Its local origin is the finished-floor center of the main threshold, +Y inward and +Z upward. Dimensions below are explicit implementation decisions because GAME_SPEC supplies function and facility topology without room dimensions. The machine geometry is original fictional game design, not an engineering storage specification.

| Element | Dimension / location |
|---|---|
| Interior envelope | 12.0 × 18.0 m, 4.8 m high; x −6…6, y 0…18 |
| Receiving | y 0…4.5; 3.6 m cart turning circle centered (0,2.5) |
| Central aisle | 3.6 m clear design width; x −1.8…1.8, y 4.5…14.5 |
| Four cells | each 3.5 × 4.0 m; two on either side |
| Monitoring booth | 3.3 × 3.4 m; west of receiving |
| Rear maintenance / dispatch | y 14.5…18; 3 m turning circle |
| Main receiving portal | 3.0 × 3.2 m, no step |
| Rear dispatch portal | 2.4 × 2.8 m, no step |
| East personnel portal | 1.2 × 2.3 m, no step |
| Booth portal | 1.1 × 2.3 m |
| Route headroom | minimum 2.4 m |
| Cask transfer design envelope | cart 1.0 × 1.8 m, cargo height up to 1.8 m |

The dimensioned SVG and interface.json define the assembly boundary. Architecture remains provisional until actual evaluated-geometry validation passes; painted route markings alone do not count as clearance evidence.

The receiving station gives workers an inventory and exposure check before choosing a segregated cell. West-front accepts process-residue overpacks; west-rear holds shielded casks; east-front stores dry contaminated filters/tools; east-rear isolates inventory awaiting disposition. Controlled movement continues to rear dispatch. Containers, seal hardware, monitoring and ventilation expose future inspect, carry, repair and bypass interactions. Reserved negative space supports carts and two-person carrying rather than display-only circulation.

The east personnel exit gives medical response a short access route. Its external door sweep is part of the interface reservation. Overhead main/rear doors avoid swinging into cargo turning areas. Other sections are authoritative: no adjacent room has been moved, imported or rewritten. Final connector placement must bind these apertures to other modules.

Canonical source: GAME_SPEC §§2, 3.5, 4.5, 6, 11–14, 16, 20.5, 23, 29 and 33.1 from the reactor-valorant design directory; current ART_DIRECTION and production protocol override legacy low-poly wording. Art principles are taken from approved reference-a02-hall and reference-b01-controls only. No new generated references are adopted.
