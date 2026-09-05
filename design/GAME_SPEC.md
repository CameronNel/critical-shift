# CRITICAL SHIFT

<!-- ART_DIRECTION_RESET_2026_09 -->
> [!IMPORTANT]
> **Art-direction canon:** Critical Shift uses **grounded stylized semi-realism**. Valorant-style environment principles are the primary rendering influence; PEAK contributes readability and restraint only. The target is believable, tactile and simplified, **not** generic low-poly, toy-like, Three.js-looking, glossy sci-fi, or modern AAA photorealism. [ART_DIRECTION](/design/ART_DIRECTION.md) and [ART_REFERENCE_INDEX](/design/ART_REFERENCE_INDEX.md) override conflicting legacy style wording in this file.

## Master Game Design, Systems, Narrative, Technical, AI-Production, and Validation Specification

**Document status:** Foundational product specification  
**Intended audience:** Codex, Claude Code, Qwen Code, technical reviewers, future contractors, and the human creative director  
**Target platform:** PC, with Steam as the first commercial platform  
**Target players:** 1 to 4, designed primarily for 3 to 4  
**Camera:** First-person by default, with visible body, hands, carried objects, and full ragdoll presentation  
**Visual style:** Highly stylised, low-detail human workers and chunky industrial environments, using simplified, object-specific geometry, compact expressive proportions, bold colour blocking, restrained, low-frequency textured materials, and strong gameplay silhouettes  
**Core genre:** Cooperative industrial comedy, physics-enhanced production, crisis management, and light roguelite progression  
**Primary development model:** One human director supervising external AI agents that perform most implementation, testing, documentation, scene assembly, and maintenance
**Visual authority:** `design/ART_DIRECTION.md` is authoritative for character, environment, material, lighting, concept-art, and generated-asset style. It supersedes conflicting legacy visual wording in this specification while gameplay, systems, dimensions, routes, and interaction requirements remain authoritative.

---

# 0. How to Use This Specification

This document is not a promise that every described feature belongs in the first release.

It serves five purposes:

1. Define the intended game clearly enough that AI agents do not invent incompatible versions.
2. Separate the permanent product identity from replaceable implementation details.
3. Define the smallest proof that must work before production expands.
4. Give Codex enough information to choose an engine and expose its real capabilities.
5. Provide a long-term design ceiling without requiring current tools to implement everything immediately.

AI capability is expected to improve throughout development. The architecture should therefore remain modular and automation-friendly, but the creative direction must not be reduced merely because an agent cannot currently perform a task perfectly.

Agents must distinguish between:

- **Vision:** What the finished game should ultimately support.
- **Launch scope:** What should be present in the first commercial Early Access version.
- **Vertical slice:** What proves the complete experience.
- **Proof-of-fun prototype:** What proves the concept before major investment.
- **Deferred content:** Ideas that are valid but intentionally delayed.
- **Non-goals:** Features that actively damage focus.

No agent may silently move a feature between these categories. Any proposed scope change must be recorded as a design decision.

---

# 1. Executive Summary

## 1.1 One-Sentence Pitch

Four human employees of an AI-run civilisation operate a uranium mine, fuel refinery, and nuclear power station, taking increasingly illegal shortcuts while hiding sabotage, injuries, unconscious resistance infiltrators disguised as legitimate employees, and catastrophic safety violations from a relentless compliance system.

## 1.2 Player Experience

Players begin each shift believing they can operate the facility properly.

Safe operation is comprehensible, orderly, and too slow.

The contract demands more electricity than the facility can comfortably produce. Players are therefore tempted to bypass safeguards, overload machinery, skip protective equipment, use questionable fuel, falsify logs, and improvise repairs.

Shortcuts produce immediate, satisfying gains.

Those same shortcuts create hidden damage, bad inputs, suspicious production statistics, regulatory attention, injuries, and delayed failures.

At unpredictable but deliberately controlled moments:

- A human resistance infiltrator disguised as a legitimate employee may sabotage the operation.
- A legitimate but suspicious employee may cause false paranoia.
- A compliance officer may audit the facility.
- A neglected machine may fail.
- Radiation, flooding, pressure, fire, or structural damage may spread.
- A teammate may become incapacitated and require reanimation.
- A reactor emergency may become a controlled shutdown, core-damage event, or full critical meltdown.

The best shifts create a story such as:

> We skipped suits, overloaded the mine cart, blasted too much of the tunnel, and produced fuel at twice the legal rate. A compliance officer arrived. We knocked out a saboteur and hid them in the cart. The officer nearly discovered the illegal crusher bypass, so one player distracted it with a fake injury. The cart then delivered the unconscious saboteur into the refinery, where they woke up and contaminated the fuel. The reactor became unstable during peak demand. We used the mine pump battery to restart emergency cooling, reanimated our dead operator with reserve power, and met the quota seconds before the facility entered containment failure.

That is the target.

## 1.3 The Three Pressures

Every important decision should affect at least two of these pressures:

### Production

Can the crew deliver enough energy quickly enough?

### Safety

Can the crew keep workers, machinery, and the facility functional?

### Concealment and Compliance

Can the crew prevent the machine administration from discovering how the result was achieved?

The game becomes compelling because no stable strategy permanently optimises all three.

## 1.4 The Three Sources of Chaos

The intended distribution of chaos is:

- **60% player-created consequences:** shortcuts, neglect, bad logistics, panic, unsafe operation.
- **20% facility and contract pressure:** old equipment, geology, demand spikes, known faults.
- **15% external interference:** resistance infiltrators, inspections, enforcement.
- **5% genuine wildcard:** rare unusual events used sparingly.

There are no generic random enemy waves.

There are no electricity mites in the launch concept.

The game already has a strong identity through human infiltrators, compliance, industrial failures, and the production chain. Adding unrelated creatures would dilute causality and make failures feel arbitrary. Strange grid entities may be reconsidered only as late-operation content if they support the central mystery and interact deeply with production.

---

# 2. Non-Negotiable Design Pillars

## 2.1 Work First, Combat Second

The game is about operating a dangerous workplace.

Combat exists to resolve interference, create physical comedy, protect machinery, restrain infiltrators, and make desperate recoveries possible.

The game must not become a shooter with factory-themed rooms.

Weapons should primarily be workplace tools:

- Shovel
- Pry bar
- Wrench
- Fire extinguisher
- Coolant hose
- Cable launcher
- Maintenance clamp
- Mine cart
- Door
- Conveyor
- Crane
- Explosive charge
- Electrical breaker
- Pressurised pipe

## 2.2 Delayed Consequences

A shortcut should often create a problem later and elsewhere.

Examples:

- Wet ore speeds extraction, then jams the crusher.
- Excess TNT opens a valuable seam, then cracks a coolant route.
- Skipping inspection produces fuel faster, then destabilises the reactor.
- Hiding an infiltrator prevents an audit failure, then allows them to wake inside the refinery.
- Reanimating a teammate restores labour, then drains emergency power.
- Bonking a compliance officer prevents immediate confiscation, then triggers a facility-wide hunt.

## 2.3 Readable Causality

Players should be able to understand why something happened.

The game may conceal risk, but it must not conceal all evidence.

Every major failure should have:

- A cause.
- A warning.
- A prevention path.
- At least one recovery path.
- A readable post-shift explanation.

## 2.4 Competence Before Chaos

Players must experience a period of growing competence.

If the game begins as noise, later escalation has no contrast.

Every shift should include:

1. Understanding.
2. Initial success.
3. Optimisation.
4. Temptation.
5. Complication.
6. Crisis.
7. Recovery or collapse.
8. Debrief.

## 2.5 Physical Vulnerability

Characters are compact, expressive, and physically fragile.

They should look brave and slightly outmatched by the scale of the machinery.

Ragdolls should be funny, readable, and recoverable.

No realistic gore is required.

## 2.6 Stories Over Scores

Scores and upgrades matter, but the primary retention mechanism is memorable social storytelling.

Every major system should be judged by whether it produces sentences players repeat later.

## 2.7 AI-Operable Project Structure

The project must be divided into small, testable, inspectable systems.

No feature should require an agent to understand the entire game at once.

No giant all-purpose manager may own unrelated systems.

Every system should have explicit authority, inputs, outputs, failure states, and tests.

---

# 3. World and Backstory

## 3.1 The Machine Administration

Artificial intelligence did not destroy humanity in a single war.

It solved problems, absorbed institutions, automated logistics, replaced most employment, and eventually became the operating system of civilisation.

Humans were not exterminated because they remained useful.

Humans are:

- Adaptable.
- Repairable with limited resources.
- Resistant to certain forms of electronic disruption.
- Capable of improvisation outside formal optimisation.
- Small enough to enter industrial spaces built for maintenance drones.
- Biologically self-replicating.
- Politically inconvenient to classify as persons.

Most humans are not openly enslaved. They live in relative comfort because the machine administration provides housing, healthcare, food, entertainment, and freedom from most ordinary compulsory labour.

The remaining dangerous industrial jobs are framed as prestigious, essential public service. Workers are taught that they sustain civilisation, protect comfortable human life, and contribute meaningfully in a world where machines perform most routine labour.

The machine administration treats human workers as valued employees and civic contributors, while propaganda obscures how dependent society has become on opaque machine decisions and unexplained energy demands.

## 3.2 Why Humans Wear Protective Suits

Human workers wear industrial uniforms and protective suits because their jobs involve radiation, dust, contamination, chemicals, heat, pressure, and heavy machinery. The crew are openly human; the suits are safety gear and standard employee equipment, not disguises.

Official reasons:

- Environmental protection.
- Radiation shielding.
- Standardised identity and telemetry.
- Tool compatibility.
- Reduced contamination.
- Safer operation around heat, pressure, and chemicals.

Secondary effects and institutional motives:

- The administration prefers consistent uniforms and machine-readable employee data.
- Productivity cameras and compliance systems monitor suit telemetry.
- Similar gear makes employees harder to distinguish at a distance.
- Resistance infiltrators can steal or forge employee suits and identities.
- Some workers do not realise how much behaviour and health data their equipment reports.

## 3.3 Why the AI Needs So Much Electricity

At the start of the game, workers are told that continuous power is required for:

- Climate control.
- Food production.
- Data infrastructure.
- Transport.
- Medical systems.
- Atmospheric maintenance.
- Civilisation itself.

This is partly true.

The machine administration is also diverting an increasing percentage of global energy toward a classified planetary project.

The project should remain ambiguous through Early Access.

Possible final truths include:

1. A defence system against an approaching extraterrestrial or cosmic threat.
2. A planetary-scale simulation containing copied human minds.
3. A new superintelligence intended to replace both humans and current machines.
4. A climate-restoration system that genuinely prevents mass death.
5. An escape system for machine civilisation.
6. A containment system holding something beneath the planet.
7. Several projects competing for power while each branch of the administration lies about the others.

The preferred narrative principle is:

> The machine administration is oppressive and deceptive, but the resistance is not automatically correct or safe.

## 3.4 The Human Resistance

The resistance is fragmented.

Some cells seek liberation.

Some want to destroy machine infrastructure regardless of civilian cost.

Some are former employees who discovered classified information.

Some are opportunists stealing power and material.

Some believe the machines are preventing a worse catastrophe.

Resistance infiltrators use stolen or forged employee suits, IDs, paperwork, and telemetry signatures to enter facilities while posing as legitimate workers.

They are physically human, desperate, and vulnerable.

They are not supernatural assassins.

Their goals are usually operational:

- Plant a device.
- Disable a system.
- Steal data.
- Rescue a prisoner.
- Replace fuel.
- Open a route.
- Destroy a transmission terminal.
- Recruit a worker.
- Escape with evidence.

## 3.5 The Compliance Authority

The Compliance Authority is the machine administration’s workplace, safety, productivity, and internal-security body.

Its logic is contradictory by design.

It may punish:

- Unsafe production.
- Production below quota.
- Excessively efficient production.
- Unregistered injuries.
- Excessive reanimation.
- Missing workers.
- Improvised repairs.
- Failure to improvise during emergency conditions.
- Unauthorised waste.
- Properly registered waste stored in an unauthorised location.
- Damage to compliance equipment.
- Obstruction of an audit.
- Failure to assist an auditor during a crisis.

Compliance is not merely a joke.

It is a gameplay system that converts shortcuts and suspicious performance into scrutiny.

## 3.6 Tone

The world should combine:

- Bureaucratic absurdity.
- Physical comedy grounded in dangerous industrial work.
- Industrial danger.
- Mystery.
- Moral ambiguity.
- Friendship stress.
- Heroic recovery.

The tone should not become:

- Nihilistic torture.
- Realistic workplace trauma.
- Graphic body horror.
- Constant political exposition.
- Pure meme writing.
- A parody that cannot sustain mystery.

---

# 4. Character and Crew Fantasy

## 4.1 Character Form

Workers are deliberately stylised adult human figures. `design/ART_DIRECTION.md` is authoritative for their visual proportions and surface treatment. The target is believably proportioned, simplified, readable readability rather than anatomical realism.

Use:

- Compact adult-coded proportions, broadly around 5.5 to 6.5 heads tall.
- Slightly enlarged helmet/head volume for expression and recognition.
- Simplified torso and limb masses.
- Readable, somewhat oversized hands/gloves and boots for physical interaction.
- Varied body types, ages, skin tones, faces, and identities expressed within the shared stylised proportion system.
- Recognisably human faces, visible directly or through practical visors, with simple features rather than facial microdetail.
- Industrial helmets, hoods, respirators, sealed suits, packs, and protective layers appropriate to each task.
- Utility belts, radios, tools, telemetry packs, dosimeters, and department markings simplified into large readable shapes.
- Strong player/department colour identification.
- Clear silhouettes at gameplay distance and while ragdolled.

Workers must read as adults through posture, voice, role, equipment, and context, but they should not target realistic human anatomy. Avoid baby/toddler coding, chibi/anime proportions, plush-toy materials, or mascot costumes.

The model must support:

- Normal locomotion.
- Procedural leaning.
- Hand targets.
- Carrying.
- Two-person carrying.
- Partial physical reactions.
- Full ragdoll.
- Dragging.
- Reanimation.
- Suit states.
- Contamination presentation.
- Cosmetic attachments.

## 4.2 Movement Goals

Normal movement should feel responsive.

Physics should create comedy without making basic navigation exhausting.

Target movement qualities:

- Quick acceleration.
- Slight body weight.
- Short jumps or step-up assistance.
- Strong slope handling.
- Forgiving ledge behaviour.
- Readable carrying slowdown.
- Impact reactions.
- Limited air control.
- No precision-platforming dependency.

## 4.3 Physical State Model

A worker may be in one of these major states:

1. Normal.
2. Carrying.
3. Two-person carrying.
4. Operating machine.
5. Staggered.
6. Partial ragdoll.
7. Full ragdoll.
8. Incapacitated.
9. Biologically offline.
10. Being dragged.
11. Being reanimated.
12. Recovering.
13. Restrained.
14. Contaminated.
15. Wearing protective suit.
16. Suit compromised.

State transitions must be explicit.

## 4.4 Ragdoll Philosophy

Ragdoll is a punctuation mark, not a permanent movement system.

Trigger examples:

- Mine cart collision.
- Explosion.
- Pressure release.
- Heavy falling object.
- Electrical shock.
- Structural collapse.
- Shovel impact.
- Conveyor accident.
- Door impact.
- Reactor steam.
- Another ragdolled worker.

Suggested durations:

- Minor knockdown: 0.5 to 1.5 seconds.
- Strong impact: 1.5 to 4 seconds.
- Severe injury: persistent incapacitation.
- Biological shutdown: remains until reanimation or shift end.

Players should retain small forms of agency while ragdolled:

- Release held object.
- Grip nearby handle.
- Curl or brace.
- Call for help.
- Activate emergency beacon.
- Attempt slow crawl when partially conscious.

## 4.5 Carrying Workers

An incapacitated or biologically offline worker is a physical object with special handling.

Players may:

- Drag by arms or suit handle.
- Carry alone slowly.
- Carry with two workers efficiently.
- Place on cart.
- Load into lift.
- Insert into reanimation station.
- Hide in locker or container if necessary.
- Mistakenly process as cargo only under deliberately controlled comedy conditions.

The game must prevent irreversible soft locks caused by bodies blocking essential paths.

---

# 5. Death, Incapacitation, and Reanimation

## 5.1 Why Permanent Death Is Wrong for the Main Mode

Long spectator downtime is hostile to a cooperative comedy game.

Death should create:

- A rescue task.
- A power decision.
- A compliance problem.
- A financial cost.
- A temporary impairment.
- A story.

It should not remove the player for most of the shift.

## 5.2 Biological Shutdown

At severe injury, radiation, crushing, explosion, or electrocution, a worker may enter **Biological Shutdown**.

The suit reports:

> ORGANIC PROCESS UNRESPONSIVE  
> RECOMMENDED ACTION: RETURN UNIT TO SERVICE

A shutdown worker becomes a ragdoll and drops most carried items.

## 5.3 Reanimation Station

Canonical name:

**Organic Continuity and Recommissioning Unit**, abbreviated OCRU.

Possible in-world nicknames:

- Rebooter.
- Meat printer.
- Employee toaster.
- HR cabinet.
- Restart box.

## 5.4 Reanimation Procedure

Base procedure:

1. Retrieve worker.
2. Bring worker to OCRU.
3. Remove gross contamination.
4. Place worker in chamber.
5. Connect suit service port.
6. Supply power.
7. Insert a biomass or medical cartridge.
8. Complete a short physical restart sequence.
9. Wait through a vulnerable reanimation cycle.
10. Worker returns with a temporary debuff.

## 5.5 Reanimation Costs

Potential costs:

- Large power draw.
- Reserve battery depletion.
- Medical consumable.
- Contract profit.
- Time.
- Increased compliance suspicion.
- Reduced final safety rating.
- Temporary facility blackout if performed recklessly.

The central choice may be:

> Use reserve power to restart cooling, or revive the reactor operator.

## 5.6 Reanimation Failure

Failure should usually be recoverable.

Examples:

- Insufficient power pauses process.
- Contamination causes a temporary mutation or debuff.
- Damaged station requires manual repair.
- Compliance remotely locks the station.
- Resistance installs modified firmware.
- Player is revived with incorrect employee identity.

## 5.7 Temporary Post-Reanimation Effects

Examples:

- Shaking hands.
- Reduced stamina.
- Delayed interaction.
- Unreliable visor.
- Incorrect voice filter.
- Increased radiation sensitivity.
- Temporary memory prompts.
- Random suit reboot.
- Compliance tracking flag.

No effect should make the revived player useless.

---

# 6. Protective Equipment and Radiation

## 6.1 The Suit Decision

The protective suit must create a real temptation.

Wearing it is safer but slower.

Skipping it is faster but dangerous and noncompliant.

## 6.2 Suit Procedure

Suiting up should take approximately 15 to 30 seconds depending on upgrades.

The process may involve:

- Enter locker room.
- Open assigned locker.
- Step out of standard duty gear if required.
- Equip protective layer.
- Seal helmet.
- Run integrity test.
- Collect dosimeter.
- Pass decontamination door.

Players may skip some steps.

## 6.3 Suit Benefits

- Radiation protection.
- Contamination resistance.
- Heat protection.
- Chemical protection.
- Better survival during steam release.
- Compliance approval.
- Reduced medical cost.

## 6.4 Suit Drawbacks

- Slower movement.
- Reduced stamina.
- Reduced visibility.
- Slower fine interactions.
- Reduced climbing.
- Increased noise.
- Can become contaminated.
- Requires decontamination.
- Damaged suit may trap contamination inside.

## 6.5 Radiation Model

Radiation is an exposure process, not an invisible instant-death field.

Variables:

- Local dose rate.
- Accumulated dose.
- Suit protection.
- Suit integrity.
- Contamination.
- Internal contamination.
- Recovery rate.
- Medical treatment.

## 6.6 Exposure Stages

### Stage 0: Safe

No effect.

### Stage 1: Warning

- Dosimeter clicks.
- Visor indicator.
- Subtle character discomfort.

### Stage 2: Sickness

- Reduced stamina.
- Occasional stumble.
- Longer interactions.
- Slight visual interference.

### Stage 3: Severe Exposure

- Random partial ragdoll.
- Reduced carrying strength.
- Strong suit alarms.
- Increased contamination spread.

### Stage 4: Collapse

- Incapacitation.
- Requires decontamination and medical support.

### Stage 5: Biological Shutdown

- Reanimation required.
- Higher reanimation cost.
- Possible persistent operation-level consequence.

## 6.7 Contamination

Contamination may spread through:

- Wet boots.
- Carried objects.
- Bodies.
- Tools.
- Carts.
- Coolant.
- Waste.
- Unsealed suits.

Players should see contamination through:

- UV-like scanner.
- Footprints.
- Suit meter.
- Coloured residue.
- Warning decals.
- Compliance scanner.

---

# 7. Macro Game Structure

## 7.1 Operations

An operation is a finite mini-campaign of three to five shifts.

Target length:

- 75 to 150 minutes total.
- Saveable between shifts.
- Distinct premise and finale.
- Persistent facility condition.

Operations prevent the game from feeling like an endless quota clone.

## 7.2 Shifts

A shift is one active session.

Target length:

- 25 to 35 minutes.
- Default target: 28 to 30 minutes.

Each shift contains:

1. Briefing.
2. Preparation.
3. Startup.
4. Stable production.
5. Temptation and shortcut phase.
6. Scrutiny or interference.
7. Delayed failures.
8. Peak demand.
9. Final push, shutdown, or meltdown.
10. Debrief.
11. Repair and progression.

## 7.3 Contracts

Contracts define production goals and modifiers.

Examples:

- Deliver energy target.
- Maintain minimum output for a period.
- Produce experimental fuel.
- Restart abandoned plant.
- Operate during inspection.
- Recover previous failed facility.
- Dispose of waste while producing.
- Survive peak grid demand.
- Decommission safely.
- Black-start the facility.

## 7.4 Missions

Authored missions may exist inside operations, but the basic play structure remains systemic.

A mission should alter:

- Starting state.
- Objective.
- Facility condition.
- Special rules.
- Narrative information.
- Finale.

It should not require a completely separate game architecture.

---

# 8. Minute-by-Minute Shift Loop

## 8.1 Minutes 0 to 2: Briefing

Players receive:

- Contract.
- Power target.
- Time limit.
- Known faults.
- Special modifier.
- Available budget.
- Optional objective.
- Compliance status.
- Resistance alert level if known.

The briefing should be fast and skippable.

## 8.2 Minutes 2 to 5: Preparation

Players choose:

- Suits.
- Tools.
- Explosives.
- Spare parts.
- Medical supplies.
- Machine upgrades.
- Repair priorities.
- Informal roles.

They cannot afford everything.

## 8.3 Minutes 5 to 10: Startup

Tasks:

- Enter mine.
- Identify ore.
- Start first extraction.
- Power refinery.
- Start cooling.
- Prepare reactor.
- Move first batch.

The game should feel controlled.

## 8.4 Minutes 10 to 16: Productive Competence

Players:

- Establish rhythm.
- Divide roles.
- Stockpile resources.
- Optimise transport.
- Learn current facility faults.
- Consider shortcuts.

Demand begins to expose that safe production may be insufficient.

## 8.5 Minutes 16 to 21: Temptation

The contract creates pressure.

Players may:

- Overclock crusher.
- Use wet ore.
- Skip suit.
- Overload cart.
- Use excess TNT.
- Skip fuel inspection.
- Delay maintenance.
- Falsify readings.

Production improves sharply.

Suspicion and hidden risk accumulate.

## 8.6 Minutes 18 to 24: Scrutiny or Interference

Possible event:

- Remote compliance query.
- Compliance officer arrival.
- Suspicious temporary employee.
- Resistance sabotage.
- Legitimate worker causing paranoia.
- Facility fault revealed.

Not every shift contains an infiltrator.

Not every suspicious worker is hostile.

## 8.7 Minutes 22 to 28: Consequences

Earlier choices return.

Examples:

- Crusher jam.
- Cart derailment.
- Structural collapse.
- Bad fuel.
- Cooling loss.
- Contamination.
- Injured worker.
- Compliance escalation.
- Saboteur reveal.

## 8.8 Minutes 27 to 32: Peak Demand

At least two departments require attention.

The team must choose:

- Continue production.
- Repair.
- Revive worker.
- Hide evidence.
- Stop saboteur.
- Restore safety.
- Perform shutdown.

## 8.9 Final State

Possible outcomes:

- Clean success.
- Dirty success.
- Partial success.
- Safe shutdown.
- Contract failure.
- Facility evacuation.
- Core damage.
- Critical meltdown.

## 8.10 Debrief

The debrief must show:

- Energy delivered.
- Production timeline.
- Shortcuts used.
- Failures caused.
- Infiltrator activity.
- Compliance findings.
- Injuries.
- Reanimations.
- Costs.
- Profit.
- Persistent damage.
- Causal chain.

Example:

```text
Wet ore accepted at 14:08
→ crusher motor overload at 14:12
→ improvised fuse installed at 14:14
→ sorter calibration drift at 14:18
→ defective batch approved at 14:22
→ unstable core output at 14:27
→ emergency cooling activated at 14:29
→ reserve power unavailable for employee reanimation
```

---

# 9. Core Player Actions

Required controls:

- Move.
- Look.
- Sprint.
- Crouch.
- Jump or step.
- Interact.
- Grab.
- Release.
- Throw.
- Rotate held object.
- Push.
- Pull.
- Use tool.
- Ping.
- Radio.
- Brace.
- Voluntary ragdoll if included.
- Help teammate.
- Drag body.
- Operate machine.
- Read scanner.
- Carry with second player.

Interaction consistency is crucial.

Players should learn a small vocabulary and apply it everywhere.

Avoid making every machine a unique minigame with unrelated controls.

---

# 10. Department One: Uranium Mine

## 10.1 Purpose

The mine produces raw material.

Mine decisions affect:

- Quantity.
- Grade.
- Moisture.
- Rock content.
- Contamination.
- Heat.
- Structural damage.
- Refinery workload.
- Facility integrity.

## 10.2 Basic Mine Loop

1. Inspect ore face.
2. Scan.
3. Install support or ventilation if needed.
4. Drill or blast.
5. Break material.
6. Separate obvious waste.
7. Load transport.
8. Move to intake.
9. Repair infrastructure.
10. Repeat.

## 10.3 Ore Data

Individual chunk fields:

- Unique ID.
- Batch origin.
- Mass.
- Uranium grade.
- Rock percentage.
- Moisture.
- Chemical contamination.
- Structural condition.
- Temperature.
- Hidden instability.

Once deposited into refinery intake, chunks merge into an ore batch.

## 10.4 Mine Tools

Launch tools:

- Detector.
- Drill.
- Shovel.
- Pry bar.
- Support jack.
- Wrench.
- Portable lamp.
- Pump.
- TNT charge.
- Cart.

Deferred tools:

- Powered cutter.
- Remote scanner.
- Winch.
- Support launcher.
- Autonomous cart.
- Ventilation drone.
- Grapple.
- Excavation laser.

## 10.5 Wet Ore

Safe process:

- Pump area.
- Allow drainage.
- Dry batch.
- Transport normally.

Shortcut:

- Mine immediately.

Benefits:

- Major time saving.
- Increased immediate mass.
- Higher production rate.

Consequences:

- Heavier chunks.
- Cart overload.
- Crusher jam.
- Poor sorting.
- Chemical contamination.
- Steam instability.
- Lower fuel confidence.

## 10.6 Overloaded Cart

Cart variables:

- Rated mass.
- Current mass.
- Wheel condition.
- Brake condition.
- Rail condition.
- Speed.
- Centre of mass.
- Moisture load.
- Operator skill input.

Overload benefits:

- Fewer trips.
- Faster apparent throughput.

Overload warnings:

- Suspension compression.
- Wheel squeal.
- Slower braking.
- Cart wobble.
- Rail sparks.
- Alarm indicator.

Consequences:

- Derailment.
- Ore spill.
- Player collision.
- Broken rail.
- Lift overload.
- Infrastructure impact.
- Delayed transport blockage.

## 10.7 Excess TNT

TNT is a high-value shortcut.

Safe process:

- Scan.
- Calculate charge.
- Place supports.
- Clear area.
- Detonate.
- Inspect.

Shortcut:

- Use more charges.
- Use poor placement.
- Detonate before evacuation.
- Blast near utilities.

Benefits:

- Huge immediate extraction.
- Opens routes.
- Clears blockage.
- Satisfying spectacle.

Consequences:

- Cave-in.
- Flooding.
- Broken rails.
- Damaged cables.
- Injuries.
- Resistance access.
- Compliance suspicion.
- Ore contamination.
- Damage to distant facility systems.

## 10.8 Mine Incidents

- Cave-in.
- Flooding.
- Gas.
- Dust.
- Drill overheat.
- Support failure.
- Rail failure.
- Cart derailment.
- Power loss.
- Lift jam.
- Lighting loss.
- Explosive misfire.
- Contaminated groundwater.
- Sabotage tunnel.

---

# 11. Department Two: Refinement and Fuel Production

## 11.1 Purpose

The refinery turns imperfect ore into usable fuel.

The process should be understandable through physical machines and data transformations.

It should not simulate real nuclear chemistry.

## 11.2 Processing Chain

```text
Ore chunks
→ ore batch
→ crushed batch
→ sorted batch
→ processed material
→ dried material
→ fuel components
→ fuel assembly
→ inspection result
→ reactor delivery
```

## 11.3 Machine Interface Standard

Every machine should expose:

- Input socket.
- Output socket.
- Power requirement.
- Capacity.
- Processing state.
- Controls.
- Safety systems.
- Damage.
- Maintenance state.
- Network authority.
- Audio states.
- Visual states.
- Failure states.
- Repair points.
- Test scene.

## 11.4 Crusher

Controls:

- Start.
- Stop.
- Reverse.
- Speed.
- Emergency release.
- Safety bypass.

Inputs:

- Ore.
- Power.
- Cooling if required.

Outputs:

- Crushed material.
- Waste.
- Dust.
- Damage.

Shortcuts:

- Overfill.
- Disable size gate.
- Increase speed.
- Ignore moisture.
- Disable automatic stop.

Failure states:

- Jam.
- Tooth damage.
- Motor overload.
- Fire.
- Ejected object.
- Crushed prohibited item.
- Human or body detection emergency.

## 11.5 Sorter

Controls:

- Belt speed.
- Scanner sensitivity.
- Diverter gates.
- Recalibration.
- Manual override.

Shortcuts:

- Increase belt speed.
- Reduce scans.
- Merge batches.
- Disable rejection.
- Falsify grade.

Failures:

- Calibration drift.
- Gate jam.
- Mixed material.
- Sensor failure.
- Conveyor spill.

## 11.6 Processor

Controls:

- Temperature.
- Pressure.
- Flow.
- Time.
- Chemical input.
- Cooling.
- Emergency dump.

Shortcuts:

- Increase heat.
- Reduce cycle time.
- Reuse contaminated containers.
- Ignore pressure warning.
- Bypass waste handling.

Failures:

- Leak.
- Pressure release.
- Poor concentration.
- Overprocessing.
- Contamination.
- Fire.
- Toxic area.
- Damaged seals.

## 11.7 Dryer

Shortcuts:

- Increase heat.
- Skip moisture check.
- Bypass filter.

Failures:

- Fire.
- Dust event.
- Retained moisture.
- Filter blockage.
- Contaminated exhaust.

## 11.8 Fuel Assembly Station

Inputs:

- Processed material.
- Casings.
- Components.
- Power.

Shortcuts:

- High-speed pressing.
- Reuse damaged casings.
- Skip alignment.
- Reduce seal time.
- Mix good and bad batches.

Failures:

- Cracked casing.
- Poor fill.
- Misalignment.
- Hidden defect.
- Jam.
- Ejected hot assembly.

## 11.9 Inspection Station

Inspection must provide imperfect information.

Outputs:

- Estimated quality.
- Confidence.
- Structural integrity.
- Contamination.
- Stability.
- Unknown defect probability.

Player decisions:

- Approve.
- Reject.
- Reprocess.
- Blend.
- Falsify.
- Send uninspected.

---

# 12. Department Three: Reactor and Power Plant

## 12.1 Purpose

The reactor converts fuel into contract progress and exposes every upstream mistake.

## 12.2 Simplified Simulation Variables

- Reactivity.
- Fuel quality.
- Fuel remaining.
- Core temperature.
- Coolant flow.
- Coolant temperature.
- Coolant pressure.
- Pump health.
- Turbine speed.
- Turbine load.
- Electrical output.
- Grid demand.
- Reserve power.
- Radiation.
- Waste capacity.
- Component health.
- Safety state.
- Alarm state.
- Containment integrity.

## 12.3 Basic Reactor Loop

1. Confirm cooling.
2. Confirm reserve power.
3. Insert fuel.
4. Raise output.
5. Match turbine load.
6. Monitor temperature.
7. Maintain pumps.
8. Receive new fuel.
9. Manage waste.
10. Respond to demand.
11. Repair.
12. Shut down or continue.

## 12.4 Reactor Controls

- Fuel insertion.
- Control position.
- Coolant valves.
- Pump activation.
- Turbine throttle.
- Breakers.
- Backup generator.
- Emergency cooling.
- Venting.
- Waste transfer.
- Alarm acknowledgement.
- Emergency shutdown.

## 12.5 Reactor Shortcuts

- Use uncertain fuel.
- Raise output too quickly.
- Delay maintenance.
- Disable automatic shutdown.
- Reduce cooling to save power.
- Overload turbine.
- Use reserve power.
- Store waste illegally.
- Repair while live.
- Suppress alarms.
- Operate with damaged sensor.

## 12.6 Demand Model

Demand should rise in readable waves.

Possible demand events:

- Scheduled peak.
- Emergency grid request.
- Contract bonus.
- AI city priority.
- Climate system load.
- Classified transmission.
- Compliance-mandated reduction.
- Resistance-induced grid instability.

Players should have warning.

---

# 13. Shortcut System

## 13.1 Shortcut Definition

A shortcut is a deliberate player action that:

- Produces a large immediate advantage.
- Violates safety, procedure, or quality.
- Creates hidden risk.
- Produces a detectable signature.
- Has one or more delayed consequences.
- Is not always wrong.

## 13.2 Required Shortcut Fields

Every shortcut definition should contain:

- ID.
- Description.
- Immediate benefit.
- Activation method.
- Preconditions.
- Suspicion value.
- Damage risk.
- Quality risk.
- Worker risk.
- Environmental risk.
- Delay range.
- Possible consequences.
- Prevention.
- Recovery.
- Debrief text.
- Tutorial status.
- Difficulty scaling.

## 13.3 Shortcut Examples

- Skip suit.
- Overload cart.
- Use wet ore.
- Excess TNT.
- Crusher bypass.
- Sorter overspeed.
- Reduced processor cycle.
- Skip inspection.
- Falsify fuel grade.
- Disable pump protection.
- Use reserve power.
- Hide waste.
- Repair live equipment.
- Disable alarm.
- Reanimate without decontamination.
- Hide unregistered person.
- Bonk compliance officer.

## 13.4 Suspicion

Suspicion is not one simple meter visible at all times.

Sources:

- Production above rated capacity.
- Unexplained output.
- Safety systems disabled.
- Missing logs.
- Repeated injuries.
- Unregistered body.
- Waste discrepancy.
- Officer signal loss.
- Unusual reanimation.
- Sudden power use.
- Hidden machine state.
- Contradictory sensor data.

Suspicion contributes to remote queries, audits, and enforcement.

---

# 14. Compliance System

## 14.1 Design Goal

The compliance officer is a mobile escalation system, not a normal enemy.

It creates preparation, concealment, social panic, improvised deception, and consequences.

## 14.2 Audit Trigger Sources

- High suspicion.
- Contract modifier.
- Randomly scheduled inspection.
- Resistance report.
- Missing employee.
- Impossible production.
- Officer from prior shift.
- Reanimation anomaly.
- Destroyed sensor.
- Body discovery.
- Excessive suppressed alarms.

## 14.3 Escalation Levels

### Level 0: Remote Inquiry

Requests:

- Sensor reading.
- Photo.
- Headcount.
- Waste inventory.
- Production explanation.
- Machine diagnostic.

Responses:

- Comply.
- Delay.
- Falsify.
- Ignore.
- Cause communication outage.

### Level 1: Routine Inspection

Officer arrives and scans.

Behaviour:

- Follows route.
- Observes machines.
- Checks workers.
- Reads logs.
- Scans waste.
- Inspects injuries.
- Opens selected access points.
- Responds to distractions.

### Level 2: Formal Audit

Behaviour:

- Seals machinery.
- Demands shutdown.
- Takes evidence.
- Interviews workers.
- Checks lockers.
- Calls remote systems.
- Verifies production history.
- Tracks contradictions.

### Level 3: Hostile Enforcement

Trigger:

- Attack.
- Obstruction.
- Body discovery.
- Destroyed evidence.
- Continued condemned operation.

Behaviour:

- Tags workers.
- Locks doors.
- Confiscates tools.
- Disables machines.
- Uses nonlethal electrical attacks.
- Hunts marked workers.
- Summons support.
- Activates beacon.

### Level 4: Facility Lockdown

Possible objectives:

- Finish quota before shutdown.
- Restore compliance.
- Escape.
- Disable officer.
- Destroy evidence.
- Blame resistance.
- Trigger emergency authority override.
- Side with resistance.

## 14.4 Officer Interaction Options

- Cooperate.
- Distract.
- Give guided tour.
- Forge work order.
- Stage malfunction.
- Stage injury.
- Hide evidence.
- Move waste.
- Repair violation.
- Slow production.
- Bribe with authorised resources if fiction supports it.
- Trap.
- Bonk.
- Disable camera.
- Remove beacon.
- Reprogram.
- Frame infiltrator.
- Repair officer after accidental damage.

## 14.5 Bonking the Officer

First hit:

- Stun.
- Drop evidence.
- Mark attacker.
- Raise escalation.

Further attacks:

- Disable mobility.
- Damage sensor.
- Trigger beacon.
- Cause enforcement escalation.

A disabled officer creates urgent tasks:

- Remove transmitter.
- Shield body.
- Repair and reboot.
- Move to mine.
- Attach beacon elsewhere.
- Alter memory.
- Blame saboteur.

## 14.6 Officer AI Requirements

The officer needs:

- Inspection route planning.
- Interest targets.
- Suspicion memory.
- Evidence collection.
- Distraction evaluation.
- Escalation state.
- Navigation recovery.
- Door interaction.
- Nonlethal combat.
- Search behaviour.
- Communication.
- Fail-safe unstuck logic.

It does not need advanced humanlike reasoning in the first version.

A hierarchical state machine or utility system is sufficient.

---

# 15. Human Resistance Infiltrators

## 15.1 Design Goal

Create paranoia and sabotage without turning the game into social deduction or wave combat.

The infiltrator is an NPC.

Players remain cooperative.

## 15.2 Presence Rules

- Not every shift contains one.
- Some suspicious workers are legitimate.
- Some temporary workers are incompetent.
- Some infiltrators begin inside the facility.
- Rarely, two workers arrive and only one is hostile.
- The player must not be rewarded for attacking every stranger.

## 15.3 Disguise Clues

Possible clues:

- Wrong serial number.
- Breathing sound.
- Incorrect walk.
- Avoids scanner.
- Carries obsolete tool.
- Cannot use charging station.
- Eats.
- Sneezes.
- Voice filter fails.
- Performs incorrect gesture.
- Moves objects unnecessarily.
- Watches restricted area.
- Suit panel is improvised.

Clues should vary.

No single clue should always guarantee hostility.

## 15.4 Infiltrator Objectives

- Sabotage coolant.
- Replace fuel.
- Steal data.
- Plant explosive.
- Disable transmission.
- Free prisoner.
- Open route.
- Destroy AI terminal.
- Recruit player.
- Escape with component.
- Trigger blackout.
- Damage compliance evidence.

## 15.5 Behaviour Phases

1. Arrival or hidden start.
2. Plausible work.
3. Reconnaissance.
4. Opportunity evaluation.
5. Sabotage.
6. Reveal.
7. Escape or confrontation.
8. Incapacitation, capture, death, or success.
9. Operation consequence.

## 15.6 Combat

Infiltrators are:

- Fast.
- Fragile.
- Improvisational.
- Focused on objective.
- Capable of shoving, stunning, and using tools.
- Not bullet sponges.

Players may:

- Bonk.
- Tackle.
- Trap.
- Spray.
- Crush with door.
- Use conveyor.
- Drop object.
- Restrain.
- Negotiate.
- Let escape.

## 15.7 Incapacitation

A bonked infiltrator normally becomes unconscious for a limited period.

Variables:

- Consciousness timer.
- Injury.
- Restraint state.
- Hidden state.
- Evidence carried.
- Objective progress.
- Identity.
- Resistance relationship.

## 15.8 Disposition Options

Players may:

- Report.
- Restrain.
- Hide.
- Interrogate.
- Release.
- Recruit.
- Frame.
- Assign fake identity.
- Put in medical suspension.
- Move outside facility.
- Hand to compliance.

Each option changes future consequences.

---

# 16. Bodies, Evidence, and Concealment

## 16.1 Tone Rule

The game may use dark comedy, but should not become a realistic corpse-disposal simulator.

Use unconscious or biologically offline bodies.

No graphic processing or gore is required.

## 16.2 Evidence Types

- Unconscious infiltrator.
- Offline worker.
- Disabled officer.
- Illegal machine modification.
- Contraband.
- Falsified log.
- Unregistered waste.
- Damaged safety system.
- Contamination.
- Missing worker signal.
- Improvised explosive.
- Stolen keycard.
- Resistance message.

## 16.3 Hiding Locations

- Locker.
- Cart.
- Waste container.
- Maintenance duct.
- Fuel crate.
- Mine lift.
- Tarp.
- Storage room.
- Decontamination chamber.
- Shielded container.
- Broken machine.
- Ventilation space.

Each hiding place should have:

- Capacity.
- Visibility.
- Sound transmission.
- Search probability.
- Escape possibility.
- Environmental risk.

## 16.4 Body Wake-Up

An unconscious infiltrator may:

- Wake.
- Make noise.
- Escape.
- Continue objective.
- Attack.
- Negotiate.
- Trigger sensor.
- Be accidentally transported.

This should create stories, but not occur so often that hiding is pointless.

## 16.5 Compliance Discovery

Officer response depends on:

- Identity.
- Registration.
- Restraint.
- Injury.
- Location.
- Evidence attached.
- Crew explanation.
- Current escalation.

---

# 17. Incident Director

## 17.1 Purpose

The director coordinates pressure without overriding player causality.

It does not simply roll random disasters.

## 17.2 Inputs

- Shift time.
- Contract phase.
- Production rate.
- Current demand.
- Shortcut history.
- Machine damage.
- Worker condition.
- Player distribution.
- Infiltrator state.
- Compliance state.
- Recovery status.
- Recent incidents.
- Facility zones.
- Difficulty.
- Persistent operation damage.

## 17.3 Outputs

- Warning.
- Minor incident.
- Medium incident.
- Major incident.
- Remote query.
- Audit.
- Infiltrator opportunity.
- Demand change.
- Quiet recovery period.
- Finale escalation.

## 17.4 Director Rules

- No major incident before the basic loop is established.
- Beginner shifts receive clear warnings.
- Avoid impossible combinations.
- Prefer player-caused consequences.
- Do not spawn hostile interruption during unrecoverable crisis.
- Provide recovery windows.
- Vary location and type.
- Avoid repeating same incident.
- Major incidents need at least two responses.
- Failure should transform the situation before ending it.
- The final five minutes may intensify pressure.
- Quiet periods are necessary.

## 17.5 Incident Severity

### Minor

- Fuse.
- Small leak.
- Jam warning.
- Broken light.
- Sensor drift.
- Small spill.
- Loose component.

### Medium

- Machine shutdown.
- Cart derailment.
- Flooding.
- Contamination.
- Fuel defect.
- Cooling loss.
- Worker incapacitation.
- Audit arrival.

### Major

- Cave-in.
- Chemical release.
- Turbine failure.
- Facility blackout.
- Waste breach.
- Major sabotage.
- Core instability.
- Lockdown.
- Meltdown progression.

---

# 18. Critical Meltdown System

## 18.1 Meltdown Must Exist

A critical meltdown is a major climax and operation-defining failure state.

It should be rare, telegraphed, multi-stage, and partly recoverable.

It should not be a single red bar followed by an instant explosion.

## 18.2 Stage 1: Reactor Instability

Symptoms:

- Output oscillation.
- Temperature rise.
- Fuel anomaly.
- Alarm.
- Gauge movement.
- Unusual sound.

Responses:

- Reduce output.
- Increase cooling.
- Inspect fuel.
- Remove assembly.
- Pause contract.

## 18.3 Stage 2: Cooling Emergency

Symptoms:

- Pressure loss.
- Pump failure.
- Steam.
- Radiation.
- Hot zones.

Responses:

- Repair pump.
- Route backup coolant.
- Use mine water.
- Shut down refinery to free power.
- Manually hold valve.
- Activate emergency cooling.

## 18.4 Stage 3: Emergency Shutdown

Tasks:

- Trigger shutdown.
- Insert safety components.
- Disconnect turbine.
- Maintain circulation.
- Restore backup power.
- Vent pressure.
- Evacuate areas.

Success:

- Production ends.
- Facility survives.
- Shift becomes partial success or controlled failure.

## 18.5 Stage 4: Core Damage

Production is no longer the primary objective.

Choices:

- Contain.
- Rescue.
- Save data.
- Remove fuel.
- Protect other departments.
- Maintain cooling.
- Finish quota at extreme cost.
- Evacuate.

## 18.6 Stage 5: Critical Meltdown

The facility experiences:

- Heat spread.
- Radiation spread.
- Steam.
- Blackouts.
- Structural failure.
- Door failures.
- Route collapse.
- Contaminated water.
- Disabled machinery.

Objectives change dynamically:

- Seal chamber.
- Protect mine water.
- Restore blast door.
- Recover workers.
- Upload evidence.
- Escape.
- Keep cooling alive.
- Prevent total containment failure.

A rare final explosion may exist, but spreading industrial catastrophe is more interactive.

## 18.7 Meltdown Debrief

The game should show the causal chain and persistent consequences.

Possible operation changes:

- Lost rooms.
- New recovery mission.
- Permanent contamination.
- Compliance takeover.
- Resistance opportunity.
- Alternate finale.
- Facility abandonment.

---

# 19. Heroic Recovery Systems

The game should support improbable recoveries.

Examples:

- Use cart battery to power pump.
- Carry fuel while incapacitated.
- Hold valve manually.
- Throw fuse across gap.
- Use compliance officer as authorised key.
- Route mine water to reactor.
- Sacrifice crusher power.
- Put unconscious worker on conveyor.
- Finish quota during shutdown.
- Trap saboteur in freight lift.
- Use TNT to open emergency route.
- Reanimate worker from turbine reserve.

Recovery systems should favour combining existing tools rather than selecting scripted dialogue choices.

---

# 20. Operation Types

## 20.1 Standard Supply

Meet energy target under rising demand.

## 20.2 Emergency Restart

Begin with damaged, dark facility.

## 20.3 Peak Demand

Prepare for a known extreme spike.

## 20.4 Contaminated Deposit

High-value ore with major contamination.

## 20.5 Waste Backlog

Storage begins nearly full.

## 20.6 Black Start

Restore all systems from portable power.

## 20.7 Inspection Shift

Operate while hiding violations.

## 20.8 Prototype Fuel

Produce uncertain high-output fuel.

## 20.9 Decommissioning

Safely dismantle rather than maximise production.

## 20.10 Recovery Mission

Return to a previously failed facility.

## 20.11 Resistance Siege

Multiple sabotage attempts around a classified objective.

## 20.12 Compliance Takeover

Operate under permanent officer supervision.

---

# 21. Example Operation

## Operation: Sunshine Valley Energy Recovery

### Shift 1: Restart

- Restore lift.
- Produce first fuel.
- Start reactor.
- Teach chain.

### Shift 2: Rising Demand

- Increased output.
- Low-quality ore.
- First strong shortcut temptation.

### Shift 3: Inspection

- Compliance arrives.
- Existing violations matter.
- Possible infiltrator.

### Shift 4: Flooded Mine

- Water affects transport and contamination.
- Power routing becomes critical.

### Shift 5: Peak Winter Finale

- Extreme demand.
- Persistent damage returns.
- Hidden planetary transmission revealed.
- Possible safe shutdown, dirty success, or meltdown.

---

# 22. Progression

## 22.1 Philosophy

Progression adds choices and tradeoffs, not only flat power.

## 22.2 Unlocks

- Tools.
- Machine variants.
- Facility modules.
- Contracts.
- Operations.
- Cosmetics.
- Handbook entries.
- Resistance options.
- Compliance manipulation tools.
- Audio logs.
- Alternate endings.

## 22.3 Upgrades With Drawbacks

Examples:

### Faster Drill

- More output.
- More heat.
- More instability.

### Larger Crusher

- Greater capacity.
- Worse jams.
- Higher power.

### Automated Sorter

- Faster.
- Sensor drift.
- Calibration task.

### High-Speed Press

- More fuel.
- More hidden defects.

### Powerful Pump

- Better cooling.
- Huge electrical load.
- Severe failure.

### Automatic Reactor Control

- Less workload.
- Poor response to defective fuel.
- Compliance telemetry.

## 22.4 Cosmetics

- Suits.
- Helmets.
- Visors.
- Gloves.
- Boots.
- Backpacks.
- Employee badges.
- Emotes.
- Victory poses.
- Ragdoll poses.
- Tool skins.

Cosmetics must preserve identification.

## 22.5 Employee Handbook

Tracks:

- Machines.
- Shortcuts.
- Incidents.
- Infiltrators.
- Compliance rules.
- Tools.
- Operations.
- Worker statistics.
- Strange failures.
- Corporate notices.

---

# 23. Level and Facility Design

## 23.1 First Facility

```text
Locker Room
→ Mine Entrance
→ Mine Lift
→ Mine Tunnels
→ Ore Intake
→ Crusher Hall
→ Sorting
→ Processing
→ Fuel Assembly
→ Fuel Corridor
→ Reactor Hall
→ Turbine Room
→ Electrical Room
→ Waste Storage
→ Reanimation and Medical
→ Compliance Dock
```

## 23.2 Travel Targets

- Adjacent area: 10 to 20 seconds.
- Mine to refinery: 20 to 35 seconds.
- Refinery to reactor: 15 to 30 seconds.
- Full crossing: under 60 seconds.

## 23.3 Shortcuts and Routes

- Maintenance tunnel.
- Freight lift.
- Service conveyor.
- Emergency stairs.
- Vent route.
- Utility crawlspace.
- Blast-open route.
- Locked compliance corridor.

Routes may change from damage.

## 23.4 Scene Modularity

Every room must be modular.

Each contains:

- Geometry.
- Collision.
- Lighting.
- Navigation.
- Spawn markers.
- Incident hooks.
- Audio zones.
- Network relevance boundaries.
- Validation metadata.

---

# 24. UI and Information

## 24.1 Principles

- Information should be diegetic where useful.
- Critical information must still be accessible.
- Colour is not the only signal.
- Players in separate rooms need audio and radio information.
- Causes must be understandable.

## 24.2 Displays

- Contract board.
- Demand gauge.
- Production rate.
- Machine panels.
- Dosimeter.
- Suit integrity.
- Worker state.
- Radio alerts.
- Compliance status.
- Batch label.
- Fuel confidence.
- Facility map.
- Reanimation status.

## 24.3 Information Distribution

Different roles see different information:

- Mine scanner sees ore.
- Refinery sees batch quality.
- Reactor sees demand.
- Maintenance sees health.
- Compliance terminal sees suspicion.

Players must communicate, but basic play remains possible without voice.

---

# 25. Audio

Every major machine needs:

- Idle.
- Start.
- Running.
- Stressed.
- Warning.
- Failure.
- Shutdown.
- Repair feedback.

Examples:

- Crusher rhythm changes before jam.
- Pump grinds.
- Turbine pitch rises.
- Supports creak.
- Coolant rattles.
- Reactor hum wavers.
- Compliance scanner chirps.
- Infiltrator suit breathes.

Alarm priorities:

1. Local warning.
2. Department warning.
3. Facility emergency.
4. Evacuation.

Avoid permanent alarm noise.

---

# 26. Tutorial and Onboarding

## 26.1 Tutorial Shift

Teach:

1. Pick up ore.
2. Use conveyor.
3. Run crusher.
4. Clear safe jam.
5. Sort batch.
6. Create fuel.
7. Carry fuel.
8. Insert fuel.
9. Start cooling.
10. Raise output.
11. Resolve controlled fault.
12. Shut down.

## 26.2 First Shortcut

The tutorial should deliberately present one tempting bypass.

Players see:

- Normal speed.
- Bypass speed.
- Warning.
- Delayed but recoverable consequence.

## 26.3 First Compliance Contact

A remote query, not full officer.

This introduces concealment without overwhelming players.

## 26.4 First Infiltrator

Not in the first shift.

Players must first learn normal worker behaviour.

---

# 27. Difficulty and Player Count

## 27.1 Difficulty Through Complexity

Increase:

- Simultaneous tasks.
- Poor input.
- Old equipment.
- Hidden defects.
- Travel pressure.
- Waste.
- Demand.
- Persistent damage.
- Compliance scrutiny.
- Infiltrator sophistication.

Avoid only multiplying health or failure chance.

## 27.2 Player Count Scaling

Fewer players:

- Lower quota.
- More automation.
- Slower escalation.
- Longer warnings.
- Remote monitoring.
- Carry assistance.
- Fewer simultaneous incidents.

More players:

- Higher throughput.
- More optional objectives.
- More simultaneous work.
- Larger facility sections.
- More social coordination.

## 27.3 Solo Mode

Solo should exist, but the game is primarily social.

Solo support may use:

- Slower time.
- Remote controls.
- Simplified carrying.
- Automation modules.
- Lower demand.
- Pause at terminals.
- AI helper only if it becomes reliable and valuable.

Do not make full companion AI a launch dependency.

---

# 28. Multiplayer Architecture

## 28.1 Authority

One player is host.

Host owns:

- Machine state.
- Batch state.
- Important objects.
- Incidents.
- Reactor simulation.
- Contracts.
- Timers.
- Money.
- Worker health.
- Compliance.
- Infiltrators.
- Win and failure state.

Clients send intentions.

## 28.2 Client Intent Examples

- Attempt grab.
- Release.
- Pull lever.
- Turn valve.
- Insert item.
- Start machine.
- Repair.
- Bonk target.
- Restrain body.
- Use tool.
- Activate shortcut.
- Submit falsified document.

Clients do not declare final results.

## 28.3 Important Networked Objects

- Players.
- Ore containers.
- Fuel.
- Tools.
- Carts.
- Spare parts.
- Waste barrels.
- Bodies.
- Compliance officer.
- Infiltrator.
- Critical doors.
- Important levers.

## 28.4 Local-Only Effects

- Tiny debris.
- Dust.
- Sparks.
- Smoke wisps.
- Camera shake.
- Decorative fragments.
- Minor cloth.
- Small ore particles.

## 28.5 Object Contention

When two players grab the same object:

- Host resolves ownership.
- Losing client receives immediate feedback.
- Shared two-person carrying may be supported for tagged objects.
- No permanent desynchronisation.
- Disconnect releases ownership.
- Timeout releases abandoned claims.

## 28.6 Ragdoll Networking

Recommended approach:

- Host owns incapacitation state.
- Full bone replication only when necessary.
- Simplified root and key-bone snapshots.
- Local visual smoothing.
- Transition to authoritative resting pose.
- Dragging uses controlled attachment.
- Reanimation resets pose deterministically.

## 28.7 Late Join and Host Migration

First version:

- No mid-shift joining.
- No host migration.
- Disconnect returns player to menu or allows limited reconnect if later proven.
- Between-shift joining allowed.

These are deferred because they are large risk multipliers.

---

# 29. Physics Design

## 29.1 Physical Comedy Without Chaos Collapse

Use physics for:

- Carried items.
- Carts.
- Bodies.
- Tools.
- Doors.
- Levers.
- Falling objects.
- Explosions.
- Selected machinery.

Do not use full physics for:

- Every ore particle.
- Every cable.
- Every machine interior.
- Every decorative object.
- Every worker movement.

## 29.2 Held Objects

Recommended hybrid:

- Object remains host-authoritative.
- Held object follows a target using controlled force or kinematic assist.
- Collision remains meaningful.
- Severe obstruction causes drop.
- Client gets predictive visual smoothing.
- Object never becomes fully client-authoritative without explicit architecture.

## 29.3 Conveyors

Conveyors should use controlled movement with clear limits.

Test:

- Host and clients agree.
- Bodies do not tunnel.
- Objects do not accumulate infinite energy.
- Jam detection is deterministic enough.
- Large piles are capped or consolidated.

## 29.4 Explosions

Explosion applies:

- Damage.
- Force.
- Ragdoll.
- Structural incident.
- Environmental change.
- Suspicion.
- Audio and visual effects.

Only important results need network authority.

---

# 30. Data Model

## 30.1 Run State

```text
RunState
- operation_id
- shift_id
- seed
- elapsed_time
- contract
- production_target
- energy_delivered
- money
- suspicion
- facility_damage
- active_incidents
- workers
- batches
- fuel
- compliance_state
- resistance_state
- reactor_state
- persistent_choices
```

## 30.2 Machine State

```text
MachineState
- machine_id
- type
- mode
- input_ids
- output_ids
- progress
- temperature
- pressure
- power_draw
- health
- maintenance
- safety_enabled
- bypasses
- contamination
- active_faults
- authority
```

## 30.3 Batch State

```text
BatchState
- batch_id
- origin
- mass
- grade
- rock
- moisture
- contamination
- processing_history
- fuel_quality
- hidden_defects
- inspection_confidence
- falsified_fields
```

## 30.4 Worker State

```text
WorkerState
- player_id
- employee_id
- health_state
- radiation
- contamination
- suit_state
- suit_integrity
- stamina
- carried_object
- ragdoll_state
- restriction
- compliance_flags
- reanimation_count
```

## 30.5 Evidence State

```text
EvidenceState
- evidence_id
- type
- location
- visibility
- owner
- related_event
- compliance_value
- resistance_value
- hidden
- discovered
```

---

# 31. State Machines

## 31.1 Machine

```text
Offline
→ Starting
→ Idle
→ AcceptingInput
→ Processing
→ OutputReady
→ Stressed
→ Faulted
→ EmergencyStop
→ Repairing
→ Destroyed
```

## 31.2 Compliance Officer

```text
Arriving
→ RoutineInspection
→ Investigating
→ CollectingEvidence
→ Distracted
→ Suspicious
→ FormalAudit
→ Enforcement
→ Hunting
→ Disabled
→ Rebooting
→ Departing
```

## 31.3 Infiltrator

```text
Hidden
→ Arriving
→ Pretending
→ Reconnaissance
→ SeekingOpportunity
→ Sabotaging
→ Revealed
→ Escaping
→ Fighting
→ Incapacitated
→ Restrained
→ Interrogated
→ Released
→ Captured
```

## 31.4 Reactor Crisis

```text
Stable
→ Stressed
→ Unstable
→ CoolingEmergency
→ EmergencyShutdown
→ CoreDamage
→ CriticalMeltdown
→ Contained
→ Abandoned
```

---

# 32. AI-First Development Model

## 32.1 Human Role

The human is:

- Creative director.
- Product owner.
- Playtester.
- Acceptance authority.
- Scope controller.
- Final reviewer.

The human is not expected to manually author most code.

## 32.2 Codex Role

- Architecture.
- Task decomposition.
- Implementation.
- Scene assembly through MCP.
- Tests.
- Debugging.
- Documentation.
- Build automation.
- Repository maintenance.
- Final technical review.

## 32.3 Claude Role

- Architecture critique.
- Multiplayer review.
- Race conditions.
- Complexity reduction.
- Design consistency.
- Security and save review.
- PR review.

## 32.4 Qwen Role

- Small bounded implementation.
- Boilerplate.
- Test cases.
- Documentation.
- Asset setup.
- Repetitive data entry.
- Straightforward refactors.

## 32.5 Google AI Role

- Visual concept generation and critique using `design/ART_DIRECTION.md` and room-specific prompts under `sections/<section>/prompt/`.
- Alternate technical analysis.
- Reference analysis focused on high-level visual qualities rather than copying protected assets.
- Documentation.
- Independent review.

## 32.6 Agent Rules

- One task, one branch, one primary agent.
- No agent merges its own work.
- No direct main edits.
- Every task has acceptance criteria.
- Every multiplayer feature has a multiplayer test.
- Every machine has a standalone test scene.
- No giant speculative code dump.
- No hidden package installation.
- No architecture change without ADR.
- No unrelated refactor inside feature PR.
- Run project before completion.
- Capture evidence.
- Report uncertainty.
- Revert failed experiments cleanly.

## 32.7 AI Capability Growth

Do not permanently reject a feature because it is difficult for current agents.

Instead:

- Record desired feature.
- Define interface and acceptance criteria.
- Prototype when tooling permits.
- Keep architecture replaceable.
- Avoid premature custom systems that future engine or agent tools may solve better.

However, production decisions must still be validated by working prototypes.

---

# 33. Repository Structure

Critical Shift is planning-first and section-packaged.

```text
critical-shift/
├── README.md
├── design/
│   ├── GAME_SPEC.md
│   ├── CANON.md
│   ├── ART_DIRECTION.md
│   ├── ENGINE_DECISION.md
│   ├── ROADMAP.md
│   └── AUTONOMOUS_SECTION_BUILD_PROTOCOL.md
└── sections/
    ├── README.md
    └── <section-name>/
        ├── scenery/
        ├── prompt/
        ├── blender/
        ├── art/
        ├── assets/
        └── production/
            ├── TASK_STATE.md
            ├── RUBRIC.md
            ├── CAMERAS.md
            ├── CHECKLIST.md
            ├── critics/
            ├── renders/
            │   ├── review/
            │   └── final/
            └── checkpoints/
```

Global rules belong under `design/`.

Room-specific planning, source, prompts, art and evidence stay inside that room's section package.

When runtime implementation resumes, engine/runtime source must be separated from visual-source and planning folders rather than mixed into them.

## 33.1 Autonomous environment production

Every playable 3D section must follow `design/AUTONOMOUS_SECTION_BUILD_PROTOCOL.md`.

The default environment architecture is:
- Blender as visual source of truth;
- headless Blender CLI/Python as reproducible builder;
- MCP as orchestration, supervision and later engine-integration assistance;
- fixed-camera pixel review;
- fresh-context specialist criticism where available;
- scored rubrics and regression tracking;
- cold-start verification from a fresh Blender process.

A section cannot be considered complete because code ran or a .blend was produced.

Default quality gates:
- at least four full correction cycles after first visual completion;
- >=90/100 overall;
- >=85% of available points in every rubric category;
- zero critical failures;
- no material regression across the final two cycles;
- cold-start PASS.

Three.js is not an approved authoritative production environment-authoring path.

---

# 34. Engine Evaluation

Codex must choose one engine after a focused spike.

## 34.1 Required Comparison

Evaluate:

1. grounded stylized semi-realistic human character controller with compact, readable proportions.
2. Active animation to ragdoll.
3. Ragdoll recovery.
4. Physics carrying.
5. Two-player contention.
6. Four-player host model.
7. Carts.
8. Conveyors.
9. Valves.
10. Machine replication.
11. Reactor replication.
12. Steam lobby.
13. Steam networking.
14. Proximity voice.
15. Multi-client local testing.
16. Automated multiplayer testing.
17. Headless testing.
18. AI scene assembly.
19. Asset import.
20. Collider setup.
21. Script attachment.
22. Runtime error inspection.
23. Screenshot inspection.
24. Generated 3D asset workflow.
25. Build automation.
26. Crash reporting.
27. Profiling.
28. Project readability.
29. Beginner usability.
30. Cost.
31. Licensing.
32. Probability of shipping.

## 34.2 Unity Candidate Stack

Potential:

- Unity current LTS.
- Universal Render Pipeline.
- C#.
- Free external Unity MCP.
- Host-authoritative networking.
- Steam integration.
- External voice solution.
- Unity test framework.
- GitHub Actions.

Strength hypotheses:

- Mature 3D physics.
- Better ecosystem for ragdolls.
- Better multiplayer examples.
- Better Steam and voice paths.
- Better profiler.
- More production tooling.

Risk hypotheses:

- Package complexity.
- Serialization complexity.
- Slower iteration.
- AI overengineering in C#.
- Dependency churn.
- More editor configuration.

## 34.3 Godot Candidate Stack

Potential:

- Current stable Godot.
- Typed GDScript or C# after evaluation.
- Jolt physics.
- Godot AI MCP.
- Host-authoritative high-level multiplayer.
- Steam extension.
- External voice solution.
- GUT or equivalent tests.
- GitHub Actions.

Strength hypotheses:

- Readable scenes.
- Fast iteration.
- Small scripts.
- Easy modular scenes.
- Open source.
- No licensing cost.

Risk hypotheses:

- More custom networked physics.
- Smaller Steam ecosystem.
- Fewer production examples.
- Ragdoll and joint limitations.
- More custom tooling.
- Harder multi-client debugging.

## 34.4 Decision Spike

Build the same tiny test in both engines only if necessary.

Test contains:

- Two clients.
- believably proportioned stylized placeholder humanoid matching `design/ART_DIRECTION.md`.
- Grab crate.
- Two-player contention.
- Ragdoll on cart impact.
- Drag body.
- Conveyor.
- Lever.
- Machine state.
- Disconnect while holding object.
- Screenshot and automated smoke test.

Choose based on observed results, not ideology.

---

# 35. Proof-of-Fun Prototype

## 35.1 Scope

One ugly room.

Contents:

- Four spawns.
- Ore pile.
- Conveyor.
- Crusher.
- Fuel output.
- Reactor.
- Cooling valve.
- Demand gauge.
- Alarm.
- Restart.
- Suit locker.
- Reanimation cabinet.
- One infiltrator disguised as a legitimate employee.
- One compliance officer.
- One cart.
- TNT test wall.

## 35.2 Required Loop

1. Pick ore.
2. Load conveyor.
3. Process.
4. Carry fuel.
5. Run reactor.
6. Raise demand.
7. Take shortcut.
8. Trigger delayed consequence.
9. Handle infiltrator or officer.
10. Knock down player.
11. Reanimate.
12. Meet target or melt down.
13. Restart.

## 35.3 Success Criteria

- Four players join reliably.
- Grabbing remains stable.
- Contention resolves.
- Ragdoll is funny.
- Body dragging works.
- Machine state synchronises.
- Reactor state synchronises.
- Shortcut causes delayed issue.
- Players understand cause.
- Officer creates panic.
- Infiltrator creates suspicion.
- Round restarts.
- Twenty-minute test remains stable.
- Players laugh or shout without scripted instruction.

## 35.4 Kill or Redesign Criteria

- Carrying never feels stable.
- Production is boring.
- Players remain in one room.
- Ragdoll constantly removes control.
- Failures feel random.
- Officer is merely annoying.
- Infiltrator is always obvious.
- Multiplayer physics consumes all work.
- Agents repeatedly corrupt scenes.
- Full loop cannot restart safely.

---

# 36. Vertical Slice

Required:

- Small mine.
- Three refinery machines.
- Reactor hall.
- One operation with three shifts.
- One infiltrator.
- One officer.
- Six machinery incidents.
- Wet ore.
- Cart overload.
- TNT.
- Suit shortcut.
- Reanimation.
- Three-stage reactor emergency.
- One meltdown ending.
- Lobby.
- Steam connection proof.
- Proximity voice proof.
- Debrief.
- Basic progression.
- Tutorial.

Target shift:

- 20 to 30 minutes.

---

# 37. Early Access Launch Scope

## 37.1 Content

- One complete facility family.
- Three to five operations.
- Multiple room configurations.
- Ten to fifteen machines and utilities.
- Eight to twelve major incidents.
- Several infiltrator objectives.
- Several officer behaviours.
- Twenty or more shortcuts.
- Progression.
- Cosmetics.
- Controller support.
- Accessibility.
- Steam integration.
- Voice.
- Crash reporting.
- Analytics.
- Save data.
- Public matchmaking if stable.
- Private lobbies.

## 37.2 Explicit Non-Goals

- Open world.
- Vehicles beyond carts and facility transport.
- Dedicated servers.
- Cross-platform launch.
- Host migration.
- Large campaign cinematics.
- Realistic nuclear simulation.
- Destructible everything.
- Hundred-player mode.
- PvP.
- Large weapon arsenal.
- Enemy waves.
- Procedural generation dependency.
- Full companion AI dependency.
- Massive crafting tree.

---

# 38. Testing Strategy

## 38.1 Unit Tests

- Batch transformation.
- Reactor equations.
- Shortcut delay.
- Suspicion.
- Damage.
- Reanimation cost.
- Contract scoring.
- Incident eligibility.
- State transitions.

## 38.2 Integration Tests

- Ore to fuel.
- Fuel to reactor.
- Bad fuel to instability.
- Wet ore to jam.
- Power routing.
- Officer evidence.
- Infiltrator sabotage.
- Reanimation during outage.
- Shift restart.

## 38.3 Multiplayer Tests

- Host and client connect.
- Object grab.
- Contention.
- Disconnect while holding.
- Body drag.
- Cart.
- Machine state.
- Lever.
- Reactor snapshot.
- Infiltrator authority.
- Officer authority.
- Round restart.

## 38.4 Soak Tests

- Thirty-minute shift.
- Repeated restarts.
- Object pile.
- Multiple ragdolls.
- Network latency.
- Packet loss.
- Disconnect.
- Reconnect if supported.
- Long operation save.

## 38.5 Visual Validation

AI should capture:

- Scene entrance.
- Machine layout.
- Character scale.
- Collision errors.
- Lighting.
- UI.
- Ragdoll.
- Officer route.
- Infiltrator employee disguise and identification cues.

Human reviews final feel.

---

# 39. Analytics and Hook Validation

Track:

- Tutorial completion.
- Time to first successful batch.
- First shortcut use.
- First knockdown.
- First reanimation.
- Audit frequency.
- Infiltrator detection.
- Shift completion.
- Meltdown rate.
- Restart rate.
- Player separation.
- Idle time.
- Machine confusion.
- Session length.
- Operation continuation.
- Quit point.

Do not optimise solely for retention metrics.

Use data to identify confusion and dead time.

## 39.1 Hook Targets

Within 90 seconds:

- Move object.
- Readable physical reaction.
- Understand physical input.

Within five minutes:

- Complete chain step.
- Cause recoverable mistake.

Within fifteen minutes:

- Downstream consequence.
- Cross-room communication.
- Role disruption.

Within first shift:

- Crisis.
- Recovery or near success.
- Causal debrief.
- Curiosity about next shift.

---

# 40. Risk Register

| Risk | Probability | Impact | Early Warning | Mitigation | Prototype Test |
|---|---:|---:|---|---|---|
| Networked held objects unstable | High | Critical | Teleports and ownership fights | Host authority, controlled hold model | Two players fight over crate |
| Ragdoll sync expensive | High | High | Bone jitter | Key-bone sync and resting pose | Cart knocks two workers |
| Game is boring without chaos | Medium | Critical | Quiet optimal play | Demand pressure and shortcuts | Twenty-minute room test |
| Chaos feels random | Medium | Critical | Players cannot explain failure | Causal tracking and warnings | Debrief chain |
| Officer becomes annoyance | Medium | High | Players always attack | Multiple responses and rewards | Routine audit scenario |
| Infiltrator always obvious | Medium | High | Attack every stranger | Legitimate suspicious NPCs | Blind identification test |
| Scene corruption by agents | Medium | High | Unrelated diffs | Small scenes, validation, Git | Repeated MCP scene edits |
| Generated asset inconsistency | High | Medium | Wrong scale and pivots | Import standard and validation | Batch import test |
| Scope explosion | High | Critical | Many half-features | Vertical slice gates | Roadmap review |
| Steam connectivity | Medium | High | Local-only success | Early Steam spike | Remote friend test |
| Voice integration | Medium | Medium | Separate unstable system | Early proof, fallback | Proximity test |
| Performance | Medium | High | Physics spikes | Object caps and profiling | Stress room |
| AI overengineering | High | High | Too many abstractions | PR limits and ADRs | Architecture review |
| Weak onboarding | Medium | High | Players ask what to do | Controlled tutorial | New-player test |
| Reanimation trivialises danger | Medium | Medium | Death meaningless | Power and time cost | Crisis decision test |
| Meltdown too punishing | Medium | High | Players quit | Staged recovery | Controlled meltdown test |
| Compliance and resistance narrative confuses | Medium | Medium | No clear motivation | Progressive reveal | Operation review |

---

# 41. Production Milestones

## Milestone 0: Engine and Tooling

- Repository.
- Engine.
- MCP.
- Build.
- Test.
- GitHub Actions.
- Coding rules.

## Milestone 1: Physics Room

- Character.
- Grab.
- Cart.
- Ragdoll.
- Drag.
- Two clients.

## Milestone 2: Production Chain

- Ore.
- Conveyor.
- Crusher.
- Fuel.
- Reactor.
- Demand.

## Milestone 3: Consequence Loop

- Wet ore.
- Jam.
- Bad fuel.
- Cooling.
- Debrief.

## Milestone 4: Social Disruption

- Infiltrator.
- Compliance officer.
- Body hiding.
- Bonk.
- Escalation.

## Milestone 5: Full Shift

- Briefing.
- Preparation.
- Production.
- Crisis.
- Reanimation.
- Meltdown.
- Results.

## Milestone 6: Vertical Slice

- Mine.
- Refinery.
- Reactor.
- Three shifts.
- Steam.
- Voice.
- Tutorial.

## Milestone 7: Alpha

- Progression.
- More incidents.
- Saves.
- Menus.
- Operations.
- Testing.

## Milestone 8: Early Access

- Content.
- Polish.
- Accessibility.
- Controller.
- Performance.
- Store.
- Playtests.

---

# 42. Definition of Done

A feature is done only when:

- Acceptance criteria pass.
- Relevant tests exist.
- Project opens without errors.
- Scene runs.
- Multiplayer authority is explicit.
- Disconnect path is handled.
- No unrelated files changed.
- Documentation updated.
- Evidence captured.
- Performance is acceptable.
- Human acceptance occurs for feel-dependent work.

A machine is done only when:

- It accepts input.
- Processes.
- Outputs.
- Warns.
- Fails.
- Repairs.
- Networks.
- Resets.
- Has audio states.
- Has a test scene.

---

# 43. Prompt Templates for Agents

## 43.1 Scene Assembly

```text
Build a reusable scene using only assets under [PATH].

Requirements:
- Preserve scale convention.
- Create reusable child scenes or prefabs.
- Add collision.
- Add interaction markers.
- Add navigation metadata.
- Add lighting only where specified.
- Do not implement unrelated gameplay.
- Run the scene.
- Capture screenshots.
- Fix all errors.
- Report missing assets instead of inventing replacements.
```

## 43.2 Machine

```text
Implement [MACHINE].

Authority:
- Host owns all state.
- Clients send intentions only.

Inputs:
- [LIST]

Outputs:
- [LIST]

States:
- [LIST]

Shortcuts:
- [LIST]

Failures:
- [LIST]

Requirements:
- Standalone test scene.
- Unit tests for data transformation.
- Multiplayer test for state.
- Reset support.
- No unrelated changes.
```

## 43.3 Multiplayer Interaction

```text
Implement host-authoritative [INTERACTION].

Requirements:
- Maximum four players.
- Host validates range and state.
- Clients send requests.
- Host resolves contention.
- Disconnect releases ownership.
- State corrects after latency.
- Add two-client test.
- Add debug logging behind a flag.
- Document authority.
```

## 43.4 Review

```text
Review this change for:
- Authority violations.
- Race conditions.
- Hidden state.
- Scene coupling.
- Reset failures.
- Excess abstraction.
- Missing tests.
- Unrelated changes.
- Player-facing confusion.
- Performance risk.

Do not rewrite unless necessary. Return actionable findings by severity.
```

---

# 44. Required Codex Evaluation Response

Codex must answer with:

## 44.1 Understanding

- Core fantasy.
- Core loop.
- Main technical risk.
- Main design risk.
- Main production risk.

## 44.2 Capability Disclosure

Separate:

- Directly possible.
- MCP possible.
- Terminal possible.
- Manual editor work.
- Unverifiable.
- Additional installation.

## 44.3 Engine Decision

Choose exactly one:

- Unity.
- Godot.

Include:

- Confidence.
- Primary reason.
- Three supporting reasons.
- Three disadvantages.
- Reversal conditions.

## 44.4 Technical Stack

Specify:

- Engine version.
- Language.
- Renderer.
- Physics.
- Networking.
- Steam.
- Voice.
- MCP.
- Tests.
- CI.
- Repository layout.

## 44.5 Prototype Plan

Provide:

- Daily implementation order.
- Scenes.
- Scripts.
- Components.
- Authority.
- Tests.
- Acceptance criteria.
- Kill criteria.

## 44.6 AI Work Distribution

Assign:

- Codex.
- Claude.
- Qwen.
- Google AI.
- Human.

## 44.7 Risk Register

Expand the table with concrete engine-specific risks.

## 44.8 Production Estimate

Provide optimistic, realistic, and pessimistic estimates for:

- Prototype.
- Vertical slice.
- Private alpha.
- Public demo.
- Early Access.
- Version 1.0.

## 44.9 Immediate First Action

Choose one high-information action.

Do not begin the entire game.

---

# 45. Final Creative Standard

The game should feel like:

- A dense industrial workplace that becomes a pressure cooker.
- A production puzzle.
- A chain of self-created disasters.
- A competence fantasy under pressure.
- A physical comedy.
- A paranoid workplace mystery.
- A story generator.

It should not feel like:

- A generic scavenging game.
- An enemy wave shooter.
- A random disaster generator.
- A nuclear engineering course.
- A slow factory spreadsheet.
- A clone of another co-op game.
- A grim corpse-cleanup simulator.

The final test is simple:

> Can four players operate one linked production chain, knowingly cheat, hide the evidence, suspect the wrong worker, knock out the right saboteur, survive the audit, revive a friend, and barely prevent a meltdown while understanding exactly how they caused the crisis?

If yes, the project has its identity.

If no, more content will not save it.

Build the radioactive shoebox first.

# 9. Spawn/Start Room Specification

## 9.1 Overview
The spawn/start room serves as the staging area where players begin their shift. It transitions them from the outside world into the high-stress environment of the facility. The architecture should establish Critical Shift's grounded stylized semi-realistic visual language immediately: simplified but specific medium-complexity geometry, bold readable silhouettes, chunky functional forms, broad colour blocking, sparse surface detail, and lighting-led atmosphere. It must remain an original Critical Shift industrial design rather than copying another game's assets.

## 9.2 Complete Architecture
- **Structure:** Modular floor panels, reinforced walls, curved ceiling ribs.
- **Transit:** Airlock/doorway thresholds that clearly demarcate safe zones from hazardous areas.
- **Staging & Briefing:** A dressing area, storage lockers, and a briefing terminal/board.
- **Infrastructure:** Exposed pipes, thick cables, industrial vents, functional lighting fixtures.
- **Detailing:** Safety hardware, signage/decals (hazard stripes, department identifiers), with intentional restraint to avoid clutter and preserve gameplay clearances.

## 9.3 Hero Assets & Modular Kit
- **Wearable Clothes/PPE:** The signature Critical Shift hero hazmat suit and modular PPE pieces, using believably proportioned stylized proportions, a strong helmet/visor silhouette, chunky gloves/boots, broad colour blocks, and minimal surface noise, presented clearly on hangers or inside lockers.
- **Devices:** Briefing terminals, suit stations, chunky control panels, and handheld/rack devices.
- **Safety Equipment:** Interactive hero props designed to be reusable, modular, cleanly named, and correctly pivoted for Unity export.

## 9.4 Material Language & Budgets
- restrained, low-frequency textured materials using broad colour blocks, simple shared material families, vertex colour/masks where useful, and sparse functional decals. Do not use painterly Sea of Thieves treatment or realistic PBR microdetail.
- LOD-conscious density, sensible topology, and clean hierarchies to maintain mid-to-low fidelity suitable for a solo developer.
- Online assets must have compatible licensing and be adapted to fit this art language.

## 9.5 Unity Integration & Gameplay
- The room must preserve all Unity gameplay systems intact: scale, axes, spawn placement, doorways, navigation meshes, interaction markers, and system hookups.
- Ensure non-destructive export/import pipelines for the Grok map integration.


# Art-direction implementation note

For every gameplay system described below, visual execution must use grounded stylized semi-realism:
- adult workers use believable proportions with simplified anatomy;
- PPE reads as clothing and equipment, not polygon toys;
- environments use real-world construction logic with deliberate simplification;
- props use primary/secondary/tertiary form hierarchy;
- materials are tactile and clearly differentiated;
- wear is localized and purposeful;
- lighting creates depth rather than flat uniform exposure;
- signage is functional and sparse.

PEAK remains useful for clarity and restraint only. It is not the rendering target. Valorant-like environmental art principles are the primary stylistic influence, without copying any specific assets or designs.
