# Worn-suit walking tradeoff, 19 October 2026

Task branch `codex/suit-mobility-tradeoff-20261019`, based on draft PR130
`3f0be906f76a90d5599e519b03b56ce789e8c41d`. Root is sole implementing author;
independent ultra review tracks inspect gameplay composition and worker recovery.
The owner's continued-building instruction authorizes this bounded prototype.

GAME_SPEC6.1/6.4 requires safer-but-slower protective gear. Timed fitting and
protection already exist, but ongoing walking uses carried mass alone. Workers
will derive one immutable walking factor: no suit1000permille, worn intact or
compromised suit800permille. A compromised suit retains its physical bulk. These
are prototype fixture values, not accepted balance or a new stamina system.

The current worker view exports that canonical factor. The existing motor
composes it with carried mass for voluntary planar walking and air-steering
targets. It does not alter cart stance correction, vertical hopping, look,
passive gravity, ragdoll/crawl or controller eligibility. Pending fitting retains
original suit/factor until exact completion. The temporary HUD makes the walking
cost visible before fitting and shows the current worker's factor.

S01/S07 worker and physical-motion ownership remain unchanged; no command,
mutable speed state, package, asset/schema migration or new assembly. Relevant
PHYS/WORKER/LIFE checks include fitting completion/cancel, immutable views,
contamination/aid, cargo composition, pause and physical handoff. Native checks
remain Planned/NotRun until pinned Unity executes them. No performance, physics
feel, multiplayer or gate acceptance is inferred from pure property tests.

Focused check:46 fitting/mobility workflow cases passed, zero failures/skips,
including6 new protection/bulk/washing, cancel/injury/aid/recovery and fresh-world
projection cases. Existing exact-fitting completion and historical-retry cases
now assert original/current factors too. Four declared native comparisons use
simultaneous real motors/controllers: worn versus unworn travel with equal load,
hop/look/idle falling, midair retained momentum, and cart-stance correction.
They remain NotRun; catalogue170 total. Static checks passed202 metadata GUIDs,
21 asmdefs/131 C# files. Final full verification and review follow below.
