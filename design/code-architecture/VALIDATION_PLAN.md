# Validation and Acceptance Plan

**Revision 2.0 | Planning proposal | All runtime checks below are NOT IMPLEMENTED by this revision**

This document defines what future evidence must establish. It contains no test implementation, CI configuration or measured results. Rule references Axx, Sxx and Hxx point to the architecture, state-contract and code-health documents in this directory. Production gate numbers match [ROADMAP.md](../ROADMAP.md).

## V00. Evidence states and anti-false-green rules

Use exactly these status labels: **Planned** (not implemented), **NotRun** (implemented but not executed on the stated revision), **Passed**, **Failed**, **Blocked** (a prerequisite prevents acceptance), or **NotApplicable**. NotApplicable requires a scoped reason and reviewer. Missing Unity, missing licenses, unsupported hardware or absent required tests are not NotApplicable and never Passed.

Each execution record identifies commit SHA; test/check ID; runner/editor/OS/package versions; build target/backend/defines; fixture/configuration hash; seed where applicable; start/end time; discovered/executed/passed/failed/skipped counts; result artifact and logs; and reviewer/limitations. Multiplayer records additionally identify every process, role, build hash and network profile. Performance records identify hardware and sampling method.

A required suite fails acceptance if it has zero discovered tests, missing/malformed result files, unmatched expected test IDs, unexpected skips, a non-zero process outcome or an unhandled application error. Parse Unity's test result output, not only its exit code. Document exact commands for the pinned Test Framework version when implemented; source U8 describes the command-line facilities but does not validate our future runner.

A first failing run remains recorded. A retry may help diagnose environment or flakiness but cannot erase the failure. Quarantining a critical invariant test blocks its gate until replaced or repaired. A checker itself needs a deliberately failing fixture; otherwise a broken discovery filter can appear healthy indefinitely.

## V01. Check suites and activation

Names below are proposed stable check identifiers, not existing GitHub workflows. Enable enforcement incrementally as the prerequisite project/toolchain exists. Do not demand a full game build for a Markdown-only proposal.

| Check | Applies to | Must produce | Required by |
| --- | --- | --- | --- |
| docs-scope | Documentation-only changes | Changed-path allowlist; valid internal links/IDs; authority/conflict review; accurate proposed/implemented status | This proposal and every documentation PR |
| toolchain-import | Runtime/package/project changes | Pinned editor/package/tool inventory; clean import/compile log; relevant platform symbols | Gate 0 |
| analysis-boundaries | First-party code/asmdef changes | Resolved editor/Player reference graph, analyzer diagnostics and negative-fixture results | Gate 0 before gameplay expansion |
| domain-contracts | Rules, commands, state/schema changes | Deterministic contract tests, expected-ID discovery and failing-seed reproduction | Gate 1 for its rules; each later feature gate |
| unity-bindings | Scene/prefab/import/serialization changes | Required-reference and ID inventory; lifecycle and representative Player evidence | Gate 1 |
| multiplayer-smoke | Networked behaviour and shared-state changes | Per-process outcomes, logical-state convergence and command/lease trace | Gate 1 |
| player-build | Runtime integration/package/asset changes | Clean build, startup/readiness, representative interactions and shutdown logs | Gate 0 basic build; relevant functionality thereafter |
| multiplayer-soak | Physics/authority/lifecycle milestones and risky regressions | N0/N1/N2 traces, invariant failures, reset/teardown metrics | Gate 1 and later affected milestones |
| content-migration-health | Replacements, serialization and content changes | Deletion ledger, root/reference scan, supported-format tests and post-removal build | Whenever applicable |

Pure Domain tests should use the lowest practical C# test layer. Unity EditMode may host pure tests without loading scenes; a separate .NET runner is an optional tooling decision, not an extra mandatory framework. Player/PlayMode tests are required when Unity lifecycle, serialization, build stripping or physics matter. Neither Editor success nor a Blender render proves a working Player.

A docs-only PR can accurately pass docs-scope while runtime gates remain Planned. Source changes cannot label themselves docs-only because the files contain extensive comments. CI must determine scope from changed paths and review rule changes explicitly.

## V02. Architecture and health cases

| ID | Given / action | Observable pass condition | Rule / timing |
| --- | --- | --- | --- |
| ARCH-01 | Resolve all first-party assemblies for editor and target Player | Every edge is allowlisted; no cycle, engine reference in pure assemblies, or runtime-to-editor/test edge | A02-A03 / Gate 0 |
| ARCH-02 | Deliberately add a forbidden UI/domain or domain/SDK reference in an isolated fixture | The intended check fails; removing the violation restores pass | A03 / Gate 0 |
| ARCH-03 | Put a first-party runtime fixture outside its declared asmdef or add an implicit plugin dependency | Discovery flags the escape; a filename-only scan cannot pass it | A03 / Gate 0 |
| ARCH-04 | Inventory public ports and live owner construction | Each catalogue fact has one mutation owner; clients/views have no mutable owner instance | S01 / review plus integration, Gate 1 onward |
| LIFE-01 | Start/stop the same fixture for 10 cycles | Claims, registrations, timers, listeners and world-owned entity counts return to their declared baseline each cycle | A06 / Gate 1 |
| LIFE-02 | Complete delayed work after teardown, then create a new world | Old-epoch callback/command changes nothing in the new world | A06, S03 / Gate 1 |
| LIFE-03 | Run lifecycle fixture with the selected reload configuration; test disabled reload before adopting it | No retained static game state or duplicate subscriber invocation | A06 / adoption gate |
| ASSET-01 | Validate declared shipped/editor/test roots and section bindings | Zero missing required references, duplicate logical IDs or unresolved binding roles | A08, H04-H05 / first import |
| ASSET-02 | Rename/move a serialized fixture, including a prefab variant and authored callback | Values and intended callbacks survive supported migration; source/metadata pairing is intact | H04 / serialization change |
| DEAD-01 | Remove an obsolete fixture after migrating code and dynamic/serialized consumers | Post-removal import/tests/Player pass; old references are absent or explicitly classified | H01-H05 / replacement PR |
| DEAD-02 | Mark a dynamically/serialized-used fixture as a removal candidate | Review/check retains and classifies it; it is not blindly deleted | H02-H03 / Gate 0 health tooling |
| CI-01 | Return a success process code with missing or zero-test results | Validation reports failure, not green | V00 / Gate 0 |
| CI-02 | Inject a known test failure, unexpected skip or unhandled runtime error | Correct suite blocks acceptance and retains artifacts | V00 / Gate 0 |

ARCH-04 includes human/independent semantic review. Do not present duplicate-writer detection as something reflection or an asmdef file can prove generally.

## V03. Behaviour cases

Counts below are starting acceptance fixtures to ratify before execution. Tests must assert outcomes, not merely run a method without throwing. Use fixed named seeds and report the smallest reproducible failed sequence. For the combined pure claim/transaction rules, begin with 100 seeds of 200 valid/invalid actions; this is a bounded exploration target, not proof over every possible input.

| ID | Given / action | Observable pass condition | First gate |
| --- | --- | --- | --- |
| CMD-01 | Client spoofs actor/target, wrong epoch, stale revision or invalid payload | Typed rejection; no custody, resource or health change | 1 |
| CMD-02 | Same retained command identity is retried, then reused with changed payload | Matching retry returns the same result with no second side effect; changed payload is rejected | 1 |
| CMD-03 | Send an old evicted sequence or a forward gap | Neither re-executes; host high-water mark is preserved; retry/resync path is explicit | 1 |
| CMD-04 | A well-formed next command is rejected by gameplay | Terminal rejection receipt advances the stream; the next valid command is not permanently blocked | 1 |
| HOLD-01 | Two peers contend for an exclusive crate for 100 cycles | One logical holder and at most one authoritative hold attachment; loser receives feedback | 1 |
| HOLD-02 | Transfer a claim, then deliver the old owner's release | New lease remains intact; no unauthorized drop | 1 |
| HOLD-03 | Disconnect, expire a lease or incapacitate a holder at each claim/attach phase | No orphaned reservation/claim; failed attachment has explicit recovery and converged projections | 1 |
| HOLD-04 | Use an ordinary object in a two-person request | Rejection unless tagged and the shared-carry contract is implemented; no accidental dual authority | 1 |
| PHYS-01 | Push cart into worker; transition to ragdoll, drag and recover | One motion controller is active per phase; no unrecoverable stuck attachment; host-approved recovery pose is usable | 1 |
| PHYS-02 | Move permitted objects/bodies through conveyor and obstruction fixtures | No observed tunnelling beyond declared fixture tolerances, runaway energy or unlimited pile growth; failures are recorded | 1 |
| PHYS-03 | Pull lever on a remote peer and trigger duplicate input | Exactly one intended machine transition; all visible state converges | 1 |
| TX-01 | Insert an item while the machine is full/faulted or custody changes | Rejection is side-effect-free; no lost item or double occupancy | 2 |
| TX-02 | Complete one process cycle twice, including a lost acknowledgment | One input consumption and one output identity per cycle; configured material accounting balances | 2 |
| TX-03 | Interrupt a prepared multi-owner change or fail physical binding | No partially published logical transaction; binding failure produces explicit unavailable/recovery state | 2 |
| CAUSE-01 | Process wet/defective input or use the chosen shortcut | Configured delayed consequence occurs once and links to the initiating event/batch; unrelated visual randomness does not alter it | 2 |
| POWER-01 | Competing consumers request the remaining reserve | No overspend; one committed cost per operation; denied request preserves state | 2, extended for reanimation in 4 |
| WORKER-01 | Combine contaminated/suited/incapacitated/dragged states | Valid orthogonal combinations survive; impossible controller/health transitions are rejected | 1, expanded in 4 |
| NPC-01 | Infiltrator/officer attempts a shared interaction or arrives during teardown | Uses validated authority path; cannot directly overwrite another feature's state | 3 |
| SHIFT-01 | End in success/failure, teardown and restart 10 times | Single terminal outcome per epoch and clean baseline for each new shift; old commands have no effect | 1 basic, 4 complete |
| MINE-01 | Deep unlock followed by smaller events, with and without rubble | Maximum depth never regresses within the epoch; uncleared rubble remains | 5 mine integration |
| MINE-02 | Remove one of the current 22 collapse pieces; retry; affect a different sector | Correct piece only, no duplicate reward; other sectors unchanged; runtime blockage matches authored state | 5 |
| SAVE-01 | Capture/restore each supported schema fixture | Logical state/identity and allowed checkpoint invariants match; new world epoch created | Before persistent data is shipped |
| SAVE-02 | Truncated/corrupt/unknown-version save or failed replacement/migration | Clear error, original known-good save preserved, live state unchanged until complete validation | Before persistent data is shipped |

MINE cases do not require implementing mining before the roadmap's small-mine milestone. Explicitly authorized isolated rule tests may precede integration; they do not make that milestone complete. SAVE cases likewise do not authorize premature full persistence.

## V04. Multiplayer fixtures and convergence

**Peer count includes the host:** two peers means one host and one client; four peers means one host and three clients. Use separate processes with recorded build/configuration hashes. Running four visual cameras in one local simulation is not a multiplayer test.

The following are proposed initial engineering acceptance fixtures, not measured networking capability. D-09 must ratify or explicitly revise them before the spike. The adapter's actual simulation timestep, send cadence, timeout and interpolation settings must be recorded.

| Profile | Network conditions | Workload / required observation |
| --- | --- | --- |
| N0 | Local/LAN, no artificial delay or loss | Two-peer interaction suite, then four-peer 20-minute Gate 1 soak; repeat contention, cart/ragdoll/drag, lever and disconnect cases |
| N1 | 100 ms imposed round-trip latency, independent per-direction jitter up to plus/minus 20 ms, 1% independent per-direction packet loss; seeded profile | Four-peer 20-minute soak on the same workload; critical commands cannot create duplicated outcomes or permanent claims |
| N2 | N1 plus a two-second blackhole for one client at scripted holding/transfer/teardown points, plus hard disconnect cases | Either documented recovery/resync within five seconds after delivery resumes or a clean disconnect; never indefinite corrupt play |

For N0/N1, visible discrete authoritative fields and ownership must converge within one second of an acknowledged settled operation, with no permanent mismatch. Compare canonical **per-recipient visible projections**, not hidden host-only state that should never be sent. Record revisions and exclude documented transient presentation fields. Proposed settled-object tolerance after two seconds without new force/input: 0.10 m position and 5 degrees orientation. Moving ragdoll bones are not judged by exact equality; shared logical posture/health and the eventual resting root must converge.

Feedback target for local input is visible pending/rejected/accepted indication within 150 ms in N0; do not confuse a local pending indicator with host acceptance. In N1/N2 record confirmation latency separately. Missed thresholds are failed spike evidence until the design or implementation is independently reviewed; do not silently loosen them after observing a failure.

Run controlled disconnects in each claim phase, not only at the end. Lease cleanup is measured from host processing of detection/expiry as specified in S04. Record transport detection latency separately. Test joining between shifts and rejection of unsupported mid-shift joining. On host loss clients must leave shared play with clear feedback; host migration is not part of a passing result.

Suggested Gate 1 soak workload: at least 100 exclusive-contention cycles, 20 cart knockdown/recovery cycles, 20 drag/release cycles, 50 lever transitions, and 10 scripted disconnect/expiry cases across separate runs where lobby reconnection is needed. Interleave them with scene/reset exercises. Counts are workload definitions, not a claim that every user interaction fits into one test run. Gate 4 additionally exercises a complete 20-35-minute shift, and the broader 30-minute soak coverage in GAME_SPEC section 38 remains applicable.

## V05. Resource, performance and feel evidence

Do not invent an FPS result from source review or Blender timings. Before collecting a runtime baseline, declare hardware, resolution/render settings, build/backend, scene/content revision, peer placement, test duration, warm-up and workload. If all peers share one machine, label the result as local process-contention evidence, not representative distributed-client performance.

Record frame-time median/p95/p99, host simulation cost, allocations/GC spikes, memory before/after warm-up, active bodies/joints, ownership/queue counts, traffic per peer and command confirmation latency. Record material/render equivalence separately from gameplay performance. Target minimum PC specifications remain D-07; Cameron's documented Radeon workstation is a known supplied machine, not automatically the minimum supported target.

Initial hard resource bounds are architectural: queues/receipts/claims have explicit capacities and overflow behaviour; teardown returns owned counts to baseline; no monotonic unbounded growth under repeated identical reset cycles. Exact byte/frame budgets must be ratified with a named fixture in D-09, not fabricated here. Compare repeated warmed-up runs against an agreed baseline before accepting performance regressions. A single instantaneous memory sample is insufficient to diagnose a leak.

Human acceptance is separately required for movement responsiveness, interaction clarity, readable ragdolls, recovery, art continuity and fun. A technical soak cannot prove that friends enjoy the production loop. Roadmap Gate 2/5 playtest criteria remain human gates even when every automated case passes.

## V06. Failures, artifacts and coverage of the claim

For a failed invariant, preserve the seed, minimal sequence if reduced, host and client command/event logs, state revisions, fixture IDs, screenshots/video when relevant, package/build information and final teardown status. Logs must redact secrets and personal filesystem/account data. Store durable evidence references with the gate record; temporary artifact expiry must not leave an accepted milestone with no accessible evidence.

The future evidence record separates automatic checks, manual inspection, independent review and outstanding work. Do not infer one from another. A screenshot can support visual inspection but cannot prove a serialized field migration or network ownership race was correct.

Before a gate is accepted, the reviewer asks: did the actual latest commit run; were all intended tests discovered; did negative controls fail correctly; are conditional builds/dynamic assets covered; are all skips explained; are pending decisions resolved for this scope; and did the change remove what it replaced? Only then may the gate advance.
