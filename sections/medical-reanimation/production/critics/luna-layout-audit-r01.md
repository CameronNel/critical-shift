# Independent Luna layout and interface audit — OCRU R01

Reviewer: Luna (independent, pre-pixel contract review)

Scope: `scenery/interface.json` and its companion architecture contract for the existing full medical/reanimation layout. Sources checked: `GAME_SPEC.md` §4.5 and chapter 5, the medical/reanimation brief, `ART_DIRECTION.md`, and the existing interface contract. This is a bounded requirements audit. It does not score the scene or claim visual evidence; pixel scores remain pending inspection of actual renders.

## Decision

**Conditional layout baseline; integration contract incomplete.** The footprint contains the major named room allocations and is a plausible baseline for the existing R09 room. The interface does not yet make the complete reanimation loop executable or safely integrable: several required machine functions are only names or prose, and clearances, state transitions, ownership, and failure recovery are absent. Preserve the current west OCRU / rear controls / east recovery / southwest cart / rear decon arrangement unless a later pixel or collision review demonstrates a consequential failure.

## Required machinery and contract coverage

| Required function from the brief/spec | Interface evidence | Audit finding |
|---|---|---|
| Body/cart arrival and retrieval | `main_entry`, `CartParking`, `cart_m` | Allocation exists. Cart turning, handle clearance, approach orientation, and a no-soft-lock body route are unspecified. |
| Gross decontamination before loading | `Decon`, `decon_threshold` | Alcove and opening are named. No contamination input/output, drainage, waste handling, occupancy, or skip/failure state is defined. |
| Human-sized OCRU chamber and access | `OCRU`, `adult_berth_m` | Machine allocation and berth size exist. Chamber opening dimensions, threshold, access/closure state, seals, restraint, and load/unload clearance are absent. |
| Suit-service hookup | Mentioned in `implementation_decisions` and architecture prose | No connector ID, port contract, hose reach/flexibility, attach/detach state, or failure behavior exists in the JSON. |
| Power and reserve battery | `ReservePower`, `PowerPanel` | Two allocations exist. No mains/reserve topology, draw, selection authority, connection, depletion, blackout, or interruption semantics are defined. |
| Cartridge insertion and consumable stock | `Cartridges`, `SuppliesCabinet` | Storage allocations exist. Receiver geometry, accepted cartridge types/counts, carrying state, insertion confirmation, stock depletion, and restock behavior are absent. |
| Physical restart controls | `Console` | Console allocation exists. No interaction IDs, control order/count, guarded/abort behavior, timeout, or partial-sequence recovery is specified. |
| Monitoring and vulnerable cycle | `Console` | A console is named, but required subject/power/cartridge/service/cycle signals and the state shown to players are not contracted. |
| Maintenance access | `PowerPanel` is the only explicit panel; architecture mentions maintenance panels | No OCRU service hatch, access envelope, repair interaction, damaged-state behavior, or safe bypass is represented in the interface. |
| Recovery position | `Recovery` | A footprint exists. Gurney dimensions, transfer clearance, route from OCRU, occupancy, and post-cycle egress are unspecified. |
| Human supplies and wash support | `SupplyBench`, `Wash`, `SuppliesCabinet` | Supporting allocations exist. Inventory, refill, contamination reset, and interaction ownership are not defined. |

The canonical procedure is retrieve → gross decontaminate → place in chamber → connect suit service → supply power → insert cartridge → physical restart → vulnerable monitored cycle → recovery. The contract has names for most endpoints but no machine-readable sequence or handoff between them.

## Spatial and operational failure risks

1. **Cart route and parking are only nominally dimensioned.** The parking allocation is about 1.40 m wide by 2.30 m long for a 0.74 m by 2.10 m cart, leaving little longitudinal margin and no stated handle/worker clearance. Its boundary meets the OCRU allocation at the same Y edge, while the OCRU loading face is described separately. The contract does not state how a cart exits parking, turns, stages, or reaches the loading face without occupying the arrival lane.

2. **The doorway/cart relationship is under-specified.** The 2.20 m entry is nominally wider than the 2.10 m cart length only by a small margin when the cart is treated as transverse. There is no orientation, turning, door-leaf, handhold, or threshold collision contract. A body or cart at the prescribed arrival obstruction test may therefore block the only exterior portal and leave no defined recovery behavior beyond manual dragging.

3. **OCRU loading is not a complete physical interaction.** The JSON gives an overall equipment bound and a berth size but no clear mouth width/height, berth axis, insertion direction, cart-to-berth transfer, subject restraint, or unload path. A dropped ragdoll can be represented in the room and still fail to become a loadable OCRU subject.

4. **The decon route is geometrically present but procedurally disconnected.** The alcove begins behind the rear hall threshold, yet the interface has no route edge from the east bypass/rear service area to decon, no one-subject occupancy rule, no contamination handoff, and no drain/waste destination. A player can reach the alcove in the plan without the game knowing when gross contamination has been removed.

5. **Rear service interactions may contend for the same working band.** Console, cartridges, reserve power, and the power panel are all flush or adjacent to the rear lining. Their bounds do not provide operator standing footprints, panel-open envelopes, cartridge carry space, or simultaneous-use rules. The contract cannot yet prove that one operator can restore power while another completes insertion or maintenance.

6. **Recovery is a footprint without a transfer contract.** The recovery allocation is narrower than the main route and has no stated gurney/cart dimensions, side-transfer clearance, body pose, or destination after reanimation. A successfully reanimated worker could remain a blocking object at the OCRU or on the recovery position.

7. **Vertical service and access are absent.** Main clear height and alcove height are recorded, but no ceiling fixture/duct clearance, OCRU top service access, lighting obstruction, or maintenance headroom is contracted. This is an integration risk for a full room even if floor bounds remain valid.

8. **Adjacency is unresolved.** `main_entry.connected_section` is `null`, and the implementation decisions explicitly leave global adjacency unresolved. The section cannot be placed into a facility graph until the receiving portal identity, transform/orientation, and ownership of the pressure-door interface are supplied.

## Missing state and multiplayer contracts

The interface should eventually expose stable IDs and state ownership for at least:

- subject eligibility: incapacitated/biologically offline, contaminated, decontaminated, loaded, recovering;
- OCRU states: empty, loading, service-connected, powered, cartridge-ready, restart-in-progress, paused, failed, complete;
- power states: mains, reserve, unavailable, depleted, interrupted;
- cartridge stock and insertion confirmation;
- abort, timeout, damage, and recoverable failure paths;
- maintenance access and repair completion;
- recovery occupancy and body release;
- host ownership/object contention for bodies, carts, cartridges, and shared two-person carrying, as required by GAME_SPEC §28.5 and §28.6;
- obstruction tests for a dropped adult and a loaded cart, including the stated rule that essential paths cannot be irreversibly soft-locked.

Without these contracts, the room can look complete while the chapter 5 loop still dead-ends at decon, loading, service hookup, restart, or recovery.

## Unspecified choices to resolve before integration

These are decisions the current interface leaves open; they are recorded as questions rather than geometry recipes:

- What section receives the main portal, and who owns its pressure-door state?
- Is decon an open threshold or a closable/lockable contamination boundary, and what clears contamination?
- What are the OCRU mouth/access, berth orientation, seals, restraint, and subject-transfer semantics?
- What is the suit-service connector identity and attach/detach rule?
- How do mains and reserve power connect, arbitrate, draw down, and recover from interruption?
- Which cartridge classes are accepted, how is stock represented, and what confirms insertion?
- What exact physical restart actions are required, and how can a player abort or resume safely?
- Which monitor signals communicate readiness, active cycle, failure, and recovery to all players?
- Where is the OCRU maintenance access and what happens when the station is damaged or locked?
- What is the recovery transfer/egress rule and how is the room cleared after reanimation?
- Which objects are host-owned when players contest a body, cart, cartridge, or control?
- Which fixed collision/navmesh tests are the integration gate for the arrival obstruction, cart route, decon access, loading, rear service, and recovery route?

## Visual review status

No scene or concept score is issued in this report. The current R09 renders and any later concept or final render pack need separate actual-pixel review against the strict Valorant-influenced grounded semi-realism target: no teal wash, no repeated bevelled-box language, no uniform satin-plastic read, and readable constructed machinery. This report should not be interpreted as a visual pass.

