# Standalone Reactor Room

This is the compact Three.js reactor-room prototype for Critical Shift. It is deliberately isolated from both the facility greybox and the mine: the scene is a single self-contained `index.html` with its own authored geometry, materials, controls, simulation loop, and touch UI.

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

## Room loop

The room exposes the reactor controls called out in `GAME_SPEC.md`: coolant valves, pump activation, emergency cooling, fuel insertion, control position, turbine throttle, grid breakers, backup generator, reserve power, waste transfer, venting, alarm acknowledgement, automatic-shutdown bypass, component repair, and emergency shutdown.

The authored shell is 22m × 18m. The six stations sit around one central containment core so a player can cross the room in seconds, with no facility-wide traversal required.
