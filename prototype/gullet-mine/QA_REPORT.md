# Gullet Mine visual and collision QA

Date: 2026-08-03

The prototype was served from `prototype/gullet-mine/` over a local HTTP server
and inspected in the bundled headless Chromium through Playwright. Desktop
captures are 1200×720; the mobile capture is 706×1536 with a coarse pointer and
touch enabled. The container renders through SwiftShader at roughly 1–2 frames
per second, which is a capture-environment number and not a device benchmark —
the collision pass below therefore steps the player controller at a fixed
timestep rather than relying on wall-clock time, which the previous pass did
not, and which is why it reported surfaces as solid that were not.

## Defects found and fixed in this pass

| Defect | Cause | Fix |
| --- | --- | --- |
| Floor invisible; the mine appeared to float over a void | The ground strip was wound clockwise, so its normals faced down and it was backface-culled from above | Rewound the triangles; the walked surface is generated from the same route stations as everything else |
| A five-metre drop hidden under the floor | The cave shell was a full ellipse whose lower half fell to `-height`; only a 4 cm plane covered it | The section is now a horseshoe with a flat invert, so the rock meets the walked surface |
| No textures anywhere | The shell had no `uv` attribute at all, and every primitive sampled its texture 0..1 per face regardless of size | Shell UVs are generated from ring and path arc length; `worldUvBox` / `worldUvCylinder` rescale every primitive so all materials tile in metres |
| Rail made no sense | 1.8 m sleepers under a 1.04 m gauge, spaced 1.18 m, floating; the line ran to the shaft and simply stopped; the cart sat 2 m off the track | One 900 mm tramway bedded on sleepers, following the route spline, with a buffer stop at the shaft lip and a stranded stub on the far side; carts sit on the rail |
| Props clipping through rock | Timber sets, lamps, signs and crates used hand-typed coordinates against a tunnel whose width they did not know | Everything is placed from the route: `ribPoint` raycasts the actual shell, and timber sets size themselves from the section at their own station |
| Hero seam floating in mid-air over the water | The cluster hung off a single station on a stretch where the drift turns | Anchored on the chord of the rib it spans, rebuilt as deep host-rock bosses with the seam in the cracks, shoring, and spoil at the foot |
| Too dark to read | Fog from 24 m, near-black ambient, and a shadow-casting "moon" lighting an enclosed drift from outside | Fog pushed back, hemisphere and ambient raised, shadow maps off, practical lamps carrying the rooms; baked vertex occlusion on the shell keeps form without a shadow map |
| Bridge deck 0.77 m proud of the floor, needing ramps that caught the capsule | Deck authored at `y = 0.62` | Deck laid flush on bearers; no ramps, no step, no seam |

## Budget

Measured from `renderer.info` after load:

| Metric | Before | After |
| --- | --- | --- |
| Draw calls | 527 | 77 |
| Meshes in scene | 1171 | 61 |
| Materials | 673 | 61 |
| Triangles | 38.6k | 31.4k |
| Lights | 21 | 18 (12 point, 1 spot, hemisphere, ambient) |

The mine is still authored as several hundred small placed meshes; `mergeStatics`
bakes their world transforms and concatenates everything sharing a material once
placement is finished. Collision proxies share one invisible material and are
kept out of the scene graph entirely.

## Collision

The player controller was stepped at a fixed 1/60 s for 2 s from 0.6 m above
each point, with collision enabled and no ghost mode:

| Point | Settles at | Surface |
| --- | --- | --- |
| Maw Camp, Crooked Rail, Saint Glimmer, Powderworks, Foreman's Vault | eye 1.65 | drift floor at 0.00 |
| Blackshaft lip | eye 2.65 | on top of the rail buffer stop |
| Blackshaft bridge, mid and far end | eye 1.70 | flush deck at 0.06 |
| Drowned Pocket walkway | eye 2.08 | boardwalk at 0.40 |

Stepping off the side of the bridge at x = 2.6 drops the player down the shaft
and respawns them at Maw Camp with collision still enabled, so Blackshaft
remains a real fall hazard.

## Visual checkpoints

Captured and inspected: Maw Camp portal and staging, the portal seen from
inside, Crooked Rail, the Blackshaft reveal, the bridge, the shaft looking down,
the Drowned Pocket entry and walkway, Saint Glimmer head-on and on approach,
Powderworks, the Foreman's Vault gate and the ledger room. Mobile framing was
checked at 706×1536: joystick, LAMP and JUMP controls and the route HUD are all
clear of the scene.

## Known limitations

- The shaft-head buffer stop sits on the rail centreline, so the player can
  climb onto it. It reads as an obstacle rather than a bug, but it is a
  climbable 1 m box in the walking line.
- Point lights are static; there is no distance culling, so all twelve are
  evaluated per fragment. If a real device struggles, a nearest-N light pool is
  the next lever.
- The sump is walkable rather than a swim: the water is 0.5 m deep over the
  rock invert, and the boardwalk is the dry route.

## Second pass — tighter layout, continuous rail, mining loop

The mine was compressed from roughly 103 m of route to 81 m and narrowed
(maximum half-width 4.1 m, down from 4.8 m), removing the long empty runs
between beats without dropping any of the seven rooms.

The tramway now runs unbroken from the portal to the Foreman's Vault. It was
previously two disconnected stubs either side of the Blackshaft. Making it
continuous meant laying the shaft crossing flush with the drift floor and
replacing the Drowned Pocket boardwalk with a timber trestle at the same
level, so the track never climbs or breaks. Measured from the rail's own
geometry after load:

```text
rail spans z 20.5 .. -59.1, gaps: none
worst offset from the 0.45 m half-gauge: 0.106 m   (tube radius is 0.05 m)
rail head y range: 0.080 .. 0.180                  (level track)
```

Collision was re-walked at fourteen points with the controller stepped at a
fixed 1/60 s; every probe settles on the right surface, including the flush
bridge deck and the sump trestle at eye 1.70, and the drift floor at 1.65.

Two defects found and fixed in this pass:

- The rock plugs at both ends of the route were pushed *inward* along the
  tangent rather than outward, so the plug at the entrance sat 1.6 m inside
  Maw Camp and the player spawned inside the cone. `capEnd` now takes a
  negative push at the start and a positive one at the end.
- Ore-face art was authored at positive face-local Z, which is the axis
  running into the rock, so the crust and chalk marks were buried inside the
  wall. Face-local +Z into the rock is now the stated convention and
  everything meant to be seen sits at negative Z.

The drill / powder / blast / pick loop was driven end to end headlessly on
Saint Glimmer: three holes drilled, three sticks charged, the round fired
while standing at the face (player correctly respawned at Maw Camp), eight ore
nodes exposed, all eight picked for 496 credits, sold and powder rebought at
the store. Draw calls after the static merge: 83.
