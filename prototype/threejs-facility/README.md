# Critical Shift — Facility Greybox (Three.js prototype)

A browser-based **level-design prototype**. It exists to answer spatial questions
about the Critical Shift facility — room scale, routes, chokepoints, sightlines,
vertical relationships, machine footprints — from a phone or a desktop browser.

**This is not production game code.** It contains no networking, no physics
engine, no gameplay simulation, and it is deliberately isolated in
`prototype/threejs-facility/` so it can be deleted in one step once the engine
decision in [`docs/ENGINE_DECISION.md`](../../docs/ENGINE_DECISION.md) is made
and the real facility is built in Unity or Godot.

## Run it

```bash
cd prototype/threejs-facility
npm install
npm run dev          # already binds 0.0.0.0:5173 for phone access
```

Then open `http://<your-machine-ip>:5173` on the phone, on the same network.

```bash
npm run build        # typecheck + production bundle into dist/
npm run preview      # serve the production bundle on 0.0.0.0:4173
```

## Status

Scaffold: renderer, scene, shared input state and the free-fly inspection
camera. The facility schema and zone plan are in `src/facility/`.
