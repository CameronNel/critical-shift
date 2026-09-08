# Runtime Architecture and Code Health

> [!IMPORTANT]
> **Start here before runtime, Unity, C#, package, serialization or architecture work.** This is the visible engineering planning entrypoint, linked from the repository README, root AGENTS.md and engine decision. Do not create another competing architecture guide.

**Revision:** 2.0, 8 September 2026  
**Status:** Documentation-only proposal for independent review. No runtime, tests, analyzers, CI jobs, project settings or branch protections are implemented by this revision.  
**Inspected baseline:** `8235e7b10ee5cb7ba11d1a90dc6c4677991e20f6`.

## The decision in one paragraph

Build a small modular Unity game, not an all-purpose framework. Each state has one mutation owner. Pure C# owns rules; Unity owns engine simulation and presentation. Application workflows coordinate explicit feature operations. The host decides shared outcomes; clients send intentions and display replicas. Dependency allowlists, lifecycle tests, reference-aware deletion and evidence-backed review will enforce the boundaries once implemented. No document or analyzer can guarantee the absence of all dead code or poor design.

## Read the right document

| Document | The question it answers |
| --- | --- |
| [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) | Where does code belong, and which assemblies may depend on which others? |
| [STATE_AND_CONTRACTS.md](STATE_AND_CONTRACTS.md) | Who owns a value, who can change it, and what happens on contention, retries or failure? |
| [CODE_HEALTH_PLAN.md](CODE_HEALTH_PLAN.md) | How do we prevent accumulation and safely remove obsolete code and assets? |
| [VALIDATION_PLAN.md](VALIDATION_PLAN.md) | Which checks prove each rule, with what fixtures, thresholds and evidence? |
| [DELIVERY_PLAN.md](DELIVERY_PLAN.md) | In what order is this established, and what blocks the next production gate? |
| [DECISIONS_AND_RISKS.md](DECISIONS_AND_RISKS.md) | What is decided, proposed, unverified, deferred or still risky? |
| [AGENT_CHECKLIST.md](AGENT_CHECKLIST.md) | What must an agent establish before work and report before handing it over? |

**First implementation task:** read all seven once. For subsequent bounded tasks, read this index, the checklist, the touched contracts and their validation rows. Reviewers should start with the decisions/risk register, then trace the affected rule IDs to evidence. Do not require unrelated room artists to read every runtime contract; they must read the asset handoff boundary when changing exported interfaces.

## Authority and scope

The [game specification](../GAME_SPEC.md) determines gameplay, player count, host authority and product scope. The [engine decision](../ENGINE_DECISION.md) records the selected stack. The [roadmap](../ROADMAP.md) controls sequencing. [Art direction](../ART_DIRECTION.md), the [section build protocol](../AUTONOMOUS_SECTION_BUILD_PROTOCOL.md) and section-local specifications continue to govern visual production. This section specifies engineering boundaries; it does not silently change any of those authorities.

The recorded engine target is Unity `6000.4.3f1`, C#, Built-in Render Pipeline and Unity 3D physics. That is a repository decision, not a claim that this session verified an installed editor or working project. Earlier engine evidence predates the documented removal of the Unity implementation. Gate 0 must reproduce the required capabilities. Networking, Steam, voice, input/UI packages and build-tool versions remain subject to the decision register.

The game specification's section 32.6 requires one task/branch, no direct main edits and no agent merging its own work. These requirements apply to this planning revision too. An implementation task must be separately authorized; approving this planning does not itself authorize building the whole game.

## What is fixed and what is not

- **Existing constraints:** one-to-four-player cooperative game; host authority; no initial mid-shift joining or host migration; staged physics proof before content expansion; independently reviewed branches.
- **Proposed engineering decisions:** dependency matrix, state contracts, lifecycle, deletion protocol and validation requirements in this revision. These become the working baseline when this proposal is accepted.
- **Provisional acceptance fixtures:** numeric budgets in VALIDATION_PLAN.md are explicit reviewable project targets, not measured results or claims about Unity. Confirm them before the first relevant spike, not after a failed run.
- **Unimplemented safeguards:** every future gate currently has no runtime evidence supplied by this revision. A listed check is not an installed check.

In normative sections, **must** means a required acceptance condition after adoption; **review trigger** means a reasoned reviewer decision is required, not automatic rejection. A change to an adopted rule needs the decision procedure, not a quiet edit to make a failing test pass.

## Change map from revision 1

The earlier linear assembly sketch is replaced by a dependency allowlist with an explicit arrow meaning. Overlapping Gameplay/feature state ownership is replaced by a state-owner catalogue. Collapse is separated from excavation depth; worker posture, health and suit condition are separate dimensions. Networking rules now cover stale commands, ownership leases and application-level idempotency without claiming reliable networks provide exactly-once execution. Dead-code review explicitly includes Unity serialization and dynamic invocation. Test gates specify discovery, failure, artifacts and honest blocked states. Initial scope remains small: do not generate empty systems for the future catalogue.

## Navigation and maintenance

Keep durable rules here, runtime source in the future engine project, and physical-section source under `sections/`. New implementation evidence will have an index on its feature/PR and the gate record; do not copy raw logs into every plan. Update the owner map, decision row and affected test IDs in the same change when an architecture boundary moves. Root AGENTS.md and the README are navigation pointers, not duplicate copies of these rules.
