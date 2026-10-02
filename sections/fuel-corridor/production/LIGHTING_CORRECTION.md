# Fuel corridor fixture-lighting correction

The owner rejected the broad, unexplained fill in the F17 assembled-map image.
F17's historical 99 scores do not approve this revision. Updated acceptance
requires fresh actual renders, all-area review, and the existing strict >98 gate.

## Source diagnosis

The F17 native contains 43 powered emitter objects and one zero-power failed
lamp. Every powered emitter belongs to a fabricated luminaire and is within
3.2 cm of an actual emitting optic face. These are real fixture sources, not
unmounted fill lights. The standalone world had an unmotivated constant 0.012
contribution. The assembled map additionally retained five global sun/bounce
lights: Southern sky bounce, Warm ground bounce, Afternoon sun, Open sky fill,
and Cliff sky bounce.

Actual fixed-camera ablations showed that suppressing those map suns removes
the broad floor/service-wall wash. Zeroing the remaining physical outdoor sky
contribution made little further visible difference in the enclosed hero view.

## Correction

- Standalone world ambient contribution is zero.
- The live installer excludes the corridor instance and all its 420 renderable
  source surfaces from the five map sun/bounce helpers through light linking.
- Existing receiver policies are retained on private copies where present.
  Other map receivers, helper energies and the physical outdoor sky are retained.
- Real room fixtures, their locations, powers, emitting surfaces and flicker
  timing remain unchanged. No replacement fill light is added.
- Cold validation now checks every powered source against real optic geometry.
  The normal launcher check also verifies all fuel exclusions and repeat-install
  idempotence.

The actual development C03 exclusion render matches the diagnostic with all
five map suns disabled to a mean 0.248/255 channel difference (95th percentile
1/255). This confirms visible behavior, not just collection metadata. Both
development C03 and C01 were opened by the builder and pessimistic Luna: local
lamp pools and contact shadows read, with visible paths and floor arrows. These
640×427 / 16-sample captures receive no final scores.

## Validation scope

Main-map and native area captures must be inspected after the correction.
Readability through dim states is reviewed from real event stills. Native
frame/key evaluation and source hashes remain technical evidence. Target-speed
cadence, Unity, collision, controllers and performance remain unverified.
No canonical map, immutable preview, exterior or other-room native is saved.

## Fresh F18 native self-critique

The builder opened all 19 full area views, the closed freight pose and all four
native-lit detail closeups, verifying the 24 PNG hashes against the hosted
native `e67b4c7e4fc6cbf1d989791040b88d9e515ba5abd0755853119401e8017c1fd4`.
These are 1280×853 /32-sample captures. The four actual spawn craft references
and five manifest-listed PR54 mood references were also reopened.

- Entry/refinery: C01/C04 retain visible arrows, door identity and bounded task
  pools. Roof and service-wall shadows keep the requested gloomy intervals.
- Staging: D01's undercarriage is low contrast in its close view. C03/C09 show
  the carrier supports, wheel silhouettes and floor contact; the wider evidence
  does not substantiate floating or lost support. D02/P01 retain legible tools,
  connector retention and cable routing. D03's gauge face is subdued but readable.
- Freight: D05 exposes the motor, rail and mounting contacts; open/closed E03
  distinguish the passage and seated leaves. The floor path stays visible.
- East turn: C05's arrows, return housing and reactor/waste destinations remain
  discernible. The dead east optic is distinct from the nearby live task fixtures.
- Waste: E01 retains the handoff, arrival paperwork, sealing station and route
  under local sconces and restrained warning spill.
- Reactor: C06/D04 keep the portal, inspection hardware, check console and red
  warning source legible. P03 confirms the mounted call point and its cable.
- Bypass/recess: C07/D06 are deliberately dark, with a traceable route and a
  readable locally lit manifold/tag; no pitch-black passage is visible.
- Plant: C10/P04 show the maintained plant end, pipe/valve construction and flush
  recessed strainer without an unexplained bright floor patch.
- Clean: C08/E02 stay cooler and brighter beneath their visible real fixtures;
  the bounded floor staining and open aisle remain clear.

Pessimistic Luna independently opened the same native set. Its initial bounded
D01 separation concern was reassessed in C03/C09 and fresh actual-map D01/C03/C09:
the grounded carrier and local light falloff read, with no confirmed contact
defect. The builder opened all 19 actual-map F18 views and verified their PNG
hashes. This complete pass shows removal of the broad service-wall and floor
wash. It also exposed a closed-door meeting-joint defect, described below;
F18/F19 do not form an accepted final pair. This self-critique awards no scores
and does not inherit F17 acceptance.

## Actual-map glazing check

C04's refinery vision pane and C06's round reactor panes are brighter in the
assembled map than in the standalone module. These highlights remain inside
the glazing and produce no visible broad floor or wall wash. The builder traced
C04 sample rays to the fuel glass material (zero emission, transmission 0.96,
roughness 0.12), with exterior sightlines beyond the pane. Straight rays do not
establish the exact reflected or refracted light path.

Pessimistic Luna reopened C04/C06 and compared C10's diffused door glazing. It
withdrew the tentative finish concern: the localized highlights read as
transmitted or reflected brighter adjacent light, with no concrete repair
justified by these views. This was a visual reassessment, not a score override
or technical evidence substituting for visual quality.

## Closed boundary meeting-joint repair

The full F18 actual-map review exposed bright center slits in the closed waste
and clean double doors. Although adjacent physical illumination can explain
their brightness, pessimistic Luna identified a concrete finish defect: the
closed leaves need a fabricated overlapping meeting seal. The builder accepted
the finding. No score override was used.

The freight gate already has an astragal. The other five closed boundary
portals now receive a bolted steel spine, a folded painted overlap and a rear
compressible rubber seal, integrated into the original left-leaf mesh. Leaf and
frame transforms, outer footprints, light powers and neighboring rooms remain
unchanged. Cold validation samples three positions across each center joint at
four heights to verify a physical barrier. Fresh actual-map captures must
establish the visible result; a geometry test does not award a finish grade.
Two new stable full review cycles are required after this repair.
