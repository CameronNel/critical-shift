# Standalone Reactor Room

This is the compact Three.js reactor-pool prototype for Critical Shift. It is deliberately isolated from both the facility greybox and the mine, with its own authored geometry, collision world, controls, simulation loop, and touch UI.

## Run it

Serve this directory over HTTP so the browser can load the Three.js module:

```sh
cd prototype/reactor-room
python3 -m http.server 4173
```

Then open `http://localhost:4173/` on desktop or a phone on the same network.

## Controls

- Desktop: `WASD` move, mouse look, `Shift` sprint, `Space` jump, `E` use, `R` reset.
- Touch: left stick moves, drag the right side to look, `USE` activates the focused control, `JUMP` and `RESET` are available at the lower right.

## Reactor loop

The player starts in an elevated control booth overlooking an open, water-filled reactor pool. The booth contains coolant authorisation, control-rod position, turbine load, and SCRAM controls. A side door opens onto a guarded landing and ramp down to the containment deck.

The deck contains the physical jobs: start the primary pumps, open coolant valves, collect a visible fuel rod from storage, carry it to the pool loading gantry, lower it into the core lattice, close the grid breakers, start reserve generation, and transfer waste. The active loop remains within a compact 24m × 20m hall.

Movement uses a capsule against an authored collision octree, including the elevated booth, landing, sloped access ramp, deck, guard rails, walls, and open pool. Large decorative machines are intentionally non-blocking so the first-person route stays clean.
