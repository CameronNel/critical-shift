# State Ownership and Behaviour Contracts

**Revision 2.0 | Planning proposal | No runtime behaviour implemented**  
Source constraints: GAME_SPEC sections 2.2-2.7, 4.3, 28-31 and 38; Gullet AGENT_READ_FIRST and scenery specifications. Read [architecture](ARCHITECTURE_PLAN.md) for dependency boundaries and [validation](VALIDATION_PLAN.md) for the test IDs below.

## S01. One writer does not mean one copy

The host owns authoritative shared state. Replication, UI views, diagnostic records and save snapshots may contain derived or copied values, but cannot accept independent authoritative writes. Every projection carries enough identity/version information to reject stale data. A stale view is replaced or marked unavailable, not used as truth for a new outcome.

The catalogue describes logical responsibilities. It does not authorize creating every module now. Aggregate boundaries may be smaller than a feature, but each fact still has one writer. The initial implementation steps are in DELIVERY_PLAN.md.

| Responsibility | Canonical writer and state | Other systems may do | Must not become |
| --- | --- | --- | --- |
| Session/shift | Session owner: world epoch, phase, seed/clock context, accepted command receipts, terminal result | Request start/end; read phase; contribute explicitly owned snapshots | A second copy of all machines/workers or a universal GameManager |
| Object custody and claims | Interaction owner: registered entity custody, exclusive/shared claim, reservation and lease generation | Request grab/release/insert/transfer; display carried-object projection | Worker, inventory, machine and network each owning a separate holder field |
| Worker | Player owner: health, consciousness, locomotion/posture, suit/exposure and recovery transitions | Submit validated impact/recovery intents; display state | One giant mutually exclusive enum mixing clothing, health and carrying |
| Material/batch | Materials owner: quantity, composition, moisture, quality, defects and processing lineage | Query properties; propose validated transformations | Independently updated duplicate inventory quantities or UI-owned grade |
| Production equipment | Production owner per machine: mode, process progress, safety/bypass settings, faults | Request start/stop/process; supply typed observations | General-purpose machine state that directly owns all other features |
| Reactor | Reactor owner: abstract operating state, interlocks, instability and cooling requirement | Supply validated fuel/cooling/power inputs; read outputs | Real nuclear-engineering simulation, UI-driven truth or a parallel client simulation |
| Power/contracts | Power owner: source contributions, allocation, energy delivered and committed costs; session/contracts own quota/result | Request a budget/cost transaction; read totals | Each consumer subtracting from separate copies of emergency energy |
| Mine sector | Mining owner per sector: maximum unlocked depth, collapse generation and uncleared rubble IDs | Submit fictional mining event or rubble-removal intent | Collapsed as a replacement for remembered excavation depth |
| Physical motion | Host Unity Rigidbody/constraint adapter for the physical entity | Read observations; request controlled force/attachment through explicit ports | A domain transform integrator competing with physics or a client claiming final pose |
| Incidents | Incident owner: eligible scheduled consequences, cause IDs, lifecycle and recovery windows | Propose/observe incidents through contracts | Arbitrary scene scripts creating untraceable random disasters |
| Compliance/evidence | Compliance owner: scrutiny/escalation; evidence records have a named owner and causal relation | Submit discovered facts or approved actions | An observer mutating production state to make a narrative outcome happen |
| Infiltrator/NPC decisions | NPC owner: objective, memory, decision state | Send the same authorized interaction/workflow requests as other actors | Privileged direct mutation of reactor, inventory or worker internals |
| Persistence/operation progression | Live progression owner when introduced; persistence adapter writes detached versioned snapshots only | Capture/restore at approved boundaries | A second continuously writable RunState or an ad hoc scene dump |

For the first slice, inventory presentation is a view over Interaction custody and Materials data, not a third ownership system. Machine slots and container contents are custody relations. A worker's carried-object display is derived from the current claim. Material properties and custody describe different facts; updates spanning both use a named transaction. Cart load metrics are derived from contents/material definitions; Unity remains the writer of motion.

A RunState snapshot may aggregate the above for persistence or replication. It is not permission to give every system write access to a single mutable global object.

## S02. Command envelope and outcome

Proposed neutral command identity: world/session epoch, authenticated connection epoch, actor ID, increasing command sequence, target logical ID, command kind/version, expected target revision when relevant, and bounded payload. Infrastructure derives the sender from its authenticated connection. An actor ID supplied in a payload does not grant authority.

State-changing client intentions use one ordered critical stream per connection in the first design. A transport adapter must provide ordering/retry or explicitly implement it before this contract can pass. Frame-by-frame aim/motion samples may use a separately specified snapshot channel; do not force them into this transactional stream.

Host processing order:

1. Validate connection, protocol/content compatibility, world epoch, actor binding, size and rate limits.
2. Check command sequence and replay receipt before invoking gameplay again.
3. Validate current actor state, target existence, access/reach/line of sight where applicable, lease token and expected revision.
4. Evaluate domain preconditions using host state, not client-declared success.
5. Prepare the bounded change; commit it on the host simulation thread; record its result/revision and causal ID. A terminal gameplay rejection is also recorded as specified in S03.
6. Publish the outcome and committed projections. Observers never see half a logical commit.

Results distinguish rejection, committed logical change and any pending physical completion. Rejection returns a stable reason such as WrongEpoch, InvalidActor, TargetMissing, OutOfReach, RevisionConflict, AlreadyClaimed, SequenceGap, TooOld or InvalidPayload; it does not consume gameplay resources. A logical grab lease is not proof that the physics attachment successfully settled.

Local solo/host input follows the same gameplay validation path without a network round trip. Internal incident/machine requests have an explicit system authority and identity; they do not use an unrestricted bypass API.

## S03. Replays, duplicates and stale commands

For the initial critical stream, accept only the next sequence; reject a forward gap without gameplay mutation and request retry/resynchronization. A repeated sequence with an available matching receipt returns the recorded result without rerunning the operation. Reusing a retained identity with different payload is rejected. A sequence older than the retained receipt window is rejected as TooOld, never treated as new work. The high-water mark remains for the connection even after receipts expire.

**Terminal rejection rule:** once an authenticated, well-formed next-sequence command reaches gameplay validation, both success and gameplay rejection finalize that sequence and store a receipt. The next command can proceed even after OutOfReach, AlreadyClaimed or RevisionConflict. Pre-admission failures such as wrong epoch, unauthenticated actor or a forward sequence gap do not advance that world's stream. No gameplay resources change on rejection; updating the protocol receipt is not a gameplay mutation. Retry/resync and bounded rate-limit recovery must be specified by the selected adapter so a throttled connection cannot remain permanently wedged.

The proposed initial receipt window is 256 completed commands per connection; it is a bounded fixture to ratify in Gate 0, not a general performance guarantee. Retries retain their original identity and payload. A state conflict requires refreshing state and issuing a genuinely new intent, not changing the content of a retry. Separate per-connection limits prevent a malformed client growing memory without bound.

This provides application-level duplicate suppression within an explicitly scoped session. It does not claim exactly-once network delivery or crash-durable transactions. When the world restarts/restores it receives a new epoch. Commands and async callbacks from the old epoch are rejected. A transport reconnect receives a new connection identity; mid-shift reconnect/join support is not introduced by this plan.

## S04. Custody, contention and physical attachment

Interaction is the sole writer of custody: World, Held by an allowed actor set, Slotted, Contained, Reserved by an operation, Consumed or Despawned. A logical entity is in one custody state at a time. Claim generation and entity revision change on transfer. References held by views are projections, not independently writable custody.

| Situation | Required result |
| --- | --- |
| Two actors grab an exclusive object on one host tick | Host serializes arbitration; exactly one lease is granted and the other receives a rejection. Both peers converge to the same owner. |
| Duplicate grab arrives after acknowledgment loss | Original result is returned; no extra lease, joint or resource use. |
| Actor A releases after the object was transferred to B | A's old lease generation is rejected; B keeps the current claim. |
| Holder disconnects or its lease expires | Host cancels reservations, releases the claim and requests attachment cleanup; no orphaned permanent holder. |
| Holder becomes incapacitated | Player transition and Interaction policy resolve possession together through a named workflow; no invisible held object. |
| Physics attachment fails after logical lease acceptance | Adapter reports failure for that exact lease; host releases/marks the operation failed and replicates the correction. It does not silently preserve a false success. |
| Two-person carrying | Only explicitly tagged capability and an accepted contract may create a joint claim. Default remains exclusive. No accidental two-owner state. |
| World/scene teardown | Commands stop, attachments are removed and session-owned claims are cleared before next activation. |

Proposed lease fixture: renewal at most one second apart and expiry after three seconds without renewal, using monotonic host time. Cleanup must complete within two simulation ticks after the host processes disconnect/expiry, or mark the entity unavailable and fail the test. A stalled host cannot promise real-time cleanup while not executing. End-to-end disconnect-detection timing must be recorded separately by the selected transport.

Joining is allowed at the between-shift boundary only in the first version. Host loss stops shared play and returns clients to a clear menu/error state. Do not silently elect another host, fabricate state or add mid-shift join because a package makes it convenient.

## S05. Material transfers and machine completion

A named Application workflow coordinates Interaction custody, Materials quantities/history and Production process state. It validates all participants before commit. Do not transfer an object by letting two unrelated event listeners each update their own count.

Example insertion: check actor/claim and machine interlock; verify material suitability and free slot/capacity; prepare new custody and machine input reference; commit both; release the hold binding; publish one correlated outcome. A rejected insertion leaves the object and quantities unchanged. If physical placement cannot complete, expose PendingBinding/Unavailable and use an explicit recovery operation; do not present the machine as ready while its required binding is broken.

Example completion: a stable process-cycle ID identifies input consumption and output creation. Each batch has one active material identity. A repeated completion callback cannot mint another output. A process fault records what was consumed, retained or turned into waste according to its authored recipe; it cannot delete unexplained quantity. Transformations conserve the configured accounting quantities across input, output, waste and declared conversion/loss terms. Do not assert that raw wet-ore mass equals finished-fuel mass.

Within the initial single-threaded host, prepare/validate all affected proposed states, then install the accepted change without awaits, callbacks or Unity side effects between owner updates. Publish only after all participants are installed. The implementation must prove its commit path cannot partially fail under expected conditions. Unexpected integrity exceptions stop the affected simulation and preserve diagnostics rather than continuing with a silently partial transaction. No distributed database or generic transaction framework is required.

Power spending, reanimation cost and contract-result publication use the same once-per-operation identity principle. A debrief or visual observer is never allowed to repeat a material/power mutation.

## S06. Mine state is two-dimensional

Per sector, store **maximum unlocked depth** separately from **uncleared rubble and collapse generation**. Sealed, shallow, extended and deep describe depth. Collapse describes obstruction. Accessibility also requires the corresponding runtime collision/navigation bindings to be ready.

| Before and operation | Required after |
| --- | --- |
| Deep; later smaller valid mining event | Depth remains deep. No previously opened volume is closed. |
| Deep with uncleared rubble; another blast | Existing uncleared rubble remains. A new event cannot implicitly clear it. |
| Oversized event at a fresh eligible sector | Deep geometry is unlocked but blocked by the authored collapse set; current Gullet source supplies 22 identified pieces per sector. |
| Remove one authorized rubble piece | Only that piece is marked cleared; one correlated physical removal occurs. |
| Retry the same removal | No second reward, count decrement or removal of a different piece. |
| Change dry sector | Wet and deep-sector state remains unchanged. |
| Restart/restore | Apply the explicit reset/checkpoint state for a new world epoch; old commands cannot mutate it. |

Preserve authored stable piece IDs. A truly new collapse after a fully cleared one needs an explicit generation policy before implementation; the current handoff does not justify silently respawning cleared pieces. This is open decision D-06. The contractual rules for existing uncleared rubble are already clear and are not blocked by that future choice.

Use fictional game tokens/indices for mining events. This plan adds no real explosive design, charge calculation or real nuclear process instruction.

## S07. Worker and hazard state

Do not flatten the game specification's list into one mutually exclusive enum. A worker can be contaminated, wearing a suit, incapacitated and being dragged simultaneously. Separate health/consciousness, posture/motion, suit/exposure and interaction claim state. Define legal cross-dimension combinations and the owner of each transition.

Normal locomotion and full ragdoll cannot simultaneously drive the same body. The host authorizes incapacitation/recovery; the Unity adapter switches the physical controllers. Recovery requires a validated pose/clearance and a single ownership handoff. A visual interpolation arriving late cannot resurrect an incapacitated worker. Body dragging is a controlled Interaction attachment to a worker entity, not a second health system.

Hazard observations include source, target, epoch, observation/tick identity and configured magnitude. Repeated observations are handled by the authored damage/cooldown rule, not an unqualified rule that every collision callback causes full damage. Gameplay bounds and units are named and testable. Randomness for incidents is owned and seeded explicitly; decorative effects use a separate stream so an extra particle cannot change a failure outcome.

## S08. Causality and bounded events

A significant committed event records event ID, cause/correlation ID, host tick, feature/entity IDs, previous/resulting revision and a typed reason. Batch lineage links a delayed downstream failure to its initiating shortcut or defect. The debrief reads those records; it does not retrospectively invent a cause from the final gauge value.

Separate required operational effects from optional notifications. Resource transfers are coordinated commands, not best-effort events. Failure of a cosmetic subscriber cannot roll back or replay a committed transaction. Required scheduled consequences have a bounded queue and explicit processing identity so a duplicate tick cannot schedule or apply the same consequence twice.

No unbounded event log is required in memory. Gate 2 must specify retention for shift causality and include dropped-event diagnostics. Logging must not contain credentials, account tokens, captured voice or private machine paths. Content-hidden information may exist on the host, but client projections expose only the information the gameplay design permits.

## S09. Persistence and reset contracts

Gate 1 requires in-memory reset and teardown, not a full save system. Save-format decisions are due before shipping persistent data. When implemented, capture a detached consistent snapshot at an approved boundary. The first save proposal is between-shift checkpoints; mid-action autosave is not silently added. The exact checkpoint scope remains D-04.

Snapshots identify schema version, content/definition version, operation/shift IDs, logical IDs and required feature state. Do not serialize Unity instance IDs, scene object references, live joints, connection handles or command receipts as portable truth. Restored gameplay receives a new world epoch; any physical pose restoration policy is separately validated.

Future save writing must preserve the previous known-good file, write and validate a temporary candidate, then use a tested replacement strategy on the target filesystem. Loading validates schema, required IDs, bounds and integrity before altering live state. Unknown future versions fail visibly without overwriting data. Migration works on a copy, is repeatably tested on fixtures and preserves the original on error. A checksum detects corruption; it does not establish trusted authorship.

Reset acceptance compares logical state with a fresh run from the same definitions, not with whatever happened to survive the last scene unload. Claims, timers, listeners, generated entities and command queues must return to declared baseline counts. Historical authoring files and validated source assets are not part of runtime teardown.
