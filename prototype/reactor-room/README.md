# Standalone Reactor Room

This is the compact Three.js reactor-pool prototype for Critical Shift. It is deliberately isolated from both the facility greybox and the mine, with its own authored geometry, collision world, controls, simulation loop, and touch UI.

For how the room is *made* — the procedural texture library, the modular kit, the pool shader, the light rig and the post chain — see [`ART_NOTES.md`](ART_NOTES.md).

## Run it

Serve this directory over HTTP so the browser can load the Three.js module:

```sh
cd prototype/reactor-room
python3 -m http.server 4173
```

Then open `http://localhost:4173/` on desktop or a phone on the same network.

There is no build step and no binary assets: every texture is painted into a canvas at boot, and every mesh is generated from the kit in `src/art/kit.js`. The start button stays disabled for the second or so that takes.

## Controls

- Desktop: `WASD` move, mouse look, `Shift` sprint, `Space` jump, `E` use, `R` reset, `G` graphics tier.
- Touch: left stick moves, drag the right side to look, `USE` activates the focused control, `JUMP`, `RESET` and `GFX` are available at the lower right.

## Reactor loop

The player starts in an elevated control booth overlooking an open, water-filled reactor pool. The booth contains coolant authorisation, control-rod position, turbine load, and SCRAM controls, split across two console banks with a clear viewing bay between them — you work at a bank, then step into the bay to look down into the water. A side door opens onto a guarded landing and ramp down to the containment deck.

The deck contains the physical jobs: start the primary pumps, open coolant valves, collect a visible fuel rod from storage, carry it to the pool loading gantry, lower it into the core lattice, close the grid breakers, start reserve generation, and transfer waste. The active loop remains within a compact 24m × 20m hall.

Movement uses a capsule against an authored collision octree, including the elevated booth, landing, sloped access ramp, deck, guard rails, walls, and open pool. Large decorative machines are intentionally non-blocking so the first-person route stays clean.

## Reading the room without the HUD

The visuals carry the reactor state, so the numbers in the corner are confirmation rather than instruction:

- **Pool brightness** tracks reactivity. A cold pool is nearly clear; a hot one throws cyan light onto the liner, the deck and the ceiling.
- **Shafts in the water** — one per loaded assembly. Count them to know the fuel state.
- **Surface agitation** tracks coolant flow: still water means the pumps are not moving anything.
- **Desk buttons** breathe when their action is the next step in the chain.
- **The mimic board** on the booth's back wall lights per subsystem, and the safety tile strobes with the alarm.
- **Emergency luminaires** around the hall are dead until the alarm, then they are most of what you can see.

## Rendering tiers

Quality is chosen at boot from the pointer type and the reported core count, and shown at the lower right. `G` toggles the parts that can change without rebuilding the scene — bloom, shadow casting and resolution. Full tier detail is in [`ART_NOTES.md`](ART_NOTES.md).
