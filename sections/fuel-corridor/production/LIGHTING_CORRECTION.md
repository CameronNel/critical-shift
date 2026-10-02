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
