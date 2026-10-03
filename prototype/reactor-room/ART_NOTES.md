# Reactor room — art notes

What the room is made of, why it is made that way, and where to change it.

Companion to [`README.md`](README.md), which covers the layout and the gameplay
loop. This file covers the visual build only.

## Target

Stylised industrial science fiction at the fidelity a solo developer can
actually ship — the standard set in [`docs/ART_DIRECTION.md`](../../docs/ART_DIRECTION.md).
Concretely, that means a small kit of modular parts, a handful of shared
material families, and atmosphere carried by lighting, motion and colour rather
than by unique geometry or bespoke texture work.

Two references drive the look:

- **Sea of Thieves** for the *treatment*: chunky bevelled forms, visibly painted
  surfaces, saturated but controlled colour, and readable silhouettes at
  gameplay distance.
- **A Soviet RBMK control hall** for the *subject*: cream and pale-green enamel
  over riveted steel, brown bakelite consoles, brass toggles and chrome bezels,
  big analogue dials, sodium worklights, and a lot of poured concrete.

Against that warm, dusty envelope the pool is the only cold light in the
building. That contrast is the whole image.

## No binary assets

Nothing here loads a file. Every texture is painted once at boot into a 2D
canvas and uploaded; every mesh is generated from the kit. The prototype stays a
drop-in directory with no build step, and a colour change in
[`src/art/palette.js`](src/art/palette.js) repaints the entire plant.

The cost is roughly 1–2 s of canvas work at boot on desktop hardware, which is
why the start button is disabled until the scene exists.

## The two rules that do the heavy lifting

**1. World-scale UVs.** `boxUV` in [`src/art/kit.js`](src/art/kit.js) projects
texture coordinates from a mesh's own dimensions, in tiles of `TEXEL_METRES`
(2 m). A rivet is therefore the same physical size on a 12 m wall as on a 0.4 m
junction box, and no piece ever needs a hand-tuned `repeat`. This is most of
what separates the room from the greybox it replaced.

**2. Everything is bevelled.** `bevelBox` returns a `RoundedBoxGeometry`. A
chamfered edge is what catches a worklight, and it is the cheapest possible way
to stop a box from reading as a box.

## Files

| File | What it owns |
|---|---|
| `art/palette.js` | Every colour in the room, as CSS strings shared by the painters and the materials |
| `art/canvas.js` | The painting toolkit: tiling value noise, fbm, height→normal, streaks, chips, scratches, rivets |
| `art/textures.js` | The surface families, painted lazily and cached |
| `art/materials.js` | Material families and the `tint` helper that dresses one family as many machines |
| `art/kit.js` | The modular geometry kit — panels, rails, pipes, valves, gauges, lamps, signs, fuel assemblies |
| `art/water.js` | The pool: surface shader, glow volume, Cherenkov shafts, caustics, bubbles |
| `art/lighting.js` | The light rig and the shadow budget |
| `art/post.js` | Bloom and the colour grade |
| `art/particles.js` | Dust and steam |
| `scene/room.js` | Hall, deck, pool structure, core lattice, rod drives, crane, services, signage |
| `scene/booth.js` | Control booth, console banks, viewing bay, mimic board, landing, ramp |
| `scene/machines.js` | Fuel rack, loading gantry, pumps, switchgear, generator, waste |
| `main.js` | Quality tiers, simulation, movement, input, HUD, frame loop |

## Surface families

Each family is authored as one **two-metre square** of real surface, and ships
albedo, a normal map derived from the same height field that carved the albedo,
and a roughness map.

`concrete` · `screed` · `enamelCream` · `enamelGreen` · `steel` · `darkSteel` ·
`tread` · `hazard` · `bakelite` · `liner` · `graphite`

Everything else in the room is a **tint** of one of these. The dozens of machine
shells are all "the same steel, painted a different colour" rather than separate
assets, which is the reuse the art direction asks for — made legible through
coherent industrial design instead of hidden.

## The pool

Five cooperating layers, driven by two numbers from the simulation: `glow`
(reactivity) and `agitation` (coolant flow).

1. **Surface** — scrolling ripple normals from a ridged-noise map, Fresnel, a
   broken specular glint, and a Cherenkov term. Alpha follows the emission:
   a glowing patch of water has to reach the frame at full strength, or it reads
   as tinted glass. Base alpha is deliberately thin, because the point of an
   open pool is that you can see the lattice in it.
2. **Glow volume** — a stack of 14 additive horizontal slices. This started as a
   single box, which only ever shows the viewer its *far* faces — and the far
   faces are exactly what the core lattice hides, so the brightest part of the
   pool ended up behind the thing making the light. Slices sit above the
   lattice and accumulate towards the surface. Each slice's falloff must
   complete inside its own quad or the square corners show.
3. **Shafts** — one flickering column per loaded assembly, so fuel count is
   legible from the booth without reading the HUD.
4. **Caustics** — two counter-scrolling layers of the same ridged noise,
   multiplied, projected onto the liner, the deck and the ceiling. Two texture
   reads, and it is what convinces the eye there is water.
5. **Bubbles** — a slow riser stream, so a still pool is never quite still.

## Lighting

Lit like a night shift: a warm sodium key from the ceiling gantry, a very soft
neutral ambient from a `RoomEnvironment` probe so no metal reads as flat grey,
and the pool as the only cold source. Every lamp carries a couple of percent of
uncorrelated flicker, which is enough to stop the room looking baked.

Shadow casting is rationed hard — two spots on desktop, none on mobile. The two
that cast are the pair over the pool, because that is what the player looks at.

## Post

`RenderPass → UnrealBloomPass → grade → OutputPass`.

Bloom is not decoration: it is the only reason glowing water reads as *emitting*
light rather than as a bright blue rectangle. The grade that follows keeps it
from turning the room milky — a warm/cool split tone, a vignette, and a shadow
lift so the deck never crushes to black the way the greybox did. The
highlight-desaturation term is masked to warm pixels only, so sodium lamps bloom
to white while the pool stays cyan however hot it gets.

## One thing the layout had to change

The booth floor sits 5.7 m above the water and about 7 m back from the pool
centre, so the sightline down to the lattice is roughly 47°. **Any console
within arm's reach of that window blocks it.** The first pass had a single
continuous desk, and the result was a control room that could not see the thing
it controlled.

The console is now split into two banks with a clear viewing bay between them,
the sill is down to 0.35 m, and the bay carries nothing but a lean-on rail
pushed against the glass. The operator works at a bank, then steps into the bay
to look at the water. Everything else about the greybox layout — deck plates,
wall lines, pool size, every guard rail, the ramp, and all collision — is
unchanged, because the movement tuning depends on it.

## Quality tiers

Picked at boot from pointer type and core count; `G` (or the GFX button)
toggles what can change without rebuilding the scene.

| | HIGH | LOW |
|---|---|---|
| Shadows | 2 casters, 1024 maps | none |
| Normal maps | yes | no (albedo and roughness kept) |
| Bloom | 0.58 / threshold 0.92 | 0.5 / threshold 0.95 |
| Pool surface | 96² segments, 14 glow slices | 40² segments, 7 slices |
| Dust | 240 motes | 90 |
| Pixel ratio | ≤1.5 | ≤1.15 |

## Known simplifications

- The water does not refract. The surface is a transparent shader over honest
  geometry, not a render-target refraction pass.
- Caustics are projected onto flat quads sized to the liner, the deck and the
  ceiling. They do not follow the geometry underneath them.
- Bloom is global, not selective. Bright *painted* surfaces bloom a little; the
  threshold is tuned so signs and dial faces stay under it.
- The overhead crane traverses on a sine, and never lifts anything.
- Steam and dust are looping fields, not simulations.
- The rod drive frame is decorative structure; the rods slide through it rather
  than being carried by it.
