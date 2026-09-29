# Non-flat environment construction

Practical guidance for future environment sessions. Read with
[ART_DIRECTION.md](ART_DIRECTION.md) and [PIPELINE.md](../PIPELINE.md).
This records the method behind the refinery/courtyard result the owner approved
on 2026-09-27. It is a reusable construction guide, not a scene-rebuild instruction
or a claim of whole-map/runtime acceptance.

## The main lesson

**Model how the object is assembled, not just its outside colour.**

The rejected wall had large flat faces, line-like seams and shallow patches.
Changing teal to grey/rust did not solve that structural problem. The successful
pass added surfaces facing different directions, actual recesses and real openings.
Their edge highlights, occlusion, parallax and cast shadows make the construction
read as three-dimensional from multiple views.

The final joint pass kept the existing materials and lighting unchanged. Its
improvement was not a new noise texture, a darker exposure or stronger fake AO.
The previously authored material variation and selective wear supported the new
geometry; they did not replace it.

## Build in the right order

1. **Primary form:** silhouette, human scale, machinery purpose and clear routes.
2. **Secondary construction:** thickness, returns, lips, frames, recesses,
   supports, door rebates, separated mating parts and functional openings.
3. **Material response:** distinguish mineral surfaces, coated metal, bare metal
   and rubber with controlled values, roughness and broad variation.
4. **Tertiary evidence of use:** a few fixings, labels, edge nicks, runoff marks,
   repairs and contact wear where the construction explains them.

If a grey-material view still looks like stacked primitives or a printed wall,
fix stages 1–2 before adding scratches or more props. Detail density is not depth.

## Construction recipes

### Wall panels

- Use solid panels with visible side returns and modest material-appropriate
  chamfers. Do not use coplanar rectangles as the final panel construction.
- Leave an actual space between panels. Recess the bedding, seal or substrate
  behind their front faces so the gap has a floor and side walls.
- Keep backing behind the joint; do not accidentally expose the room interior.
- Separate facing material from cut edges/returns where appropriate. Avoid
  outlining every edge in bright paint or black geometry at the front surface.
- Fit panels around existing doors, piers and services. Preserve opening sizes.
- After adding thickness, reseat wall labels and warning plates; otherwise the
  new face can bury text or leave signage floating.

### Cabinets, access doors and vents

- Build the enclosure/frame around a real opening, with a back or internal
  cavity where needed. A solid box behind an inset-looking rectangle defeats it.
- Give removable doors a narrow perimeter reveal and a recessed seal. Keep the
  door, frame, gasket and back at deliberate, different depths.
- Louvres need separated blades, blade thickness/angle and depth behind them.
  A dark backing may close the enclosure, but must not fill the blade openings.
- Give a removable vent cover a lip, flange, gasket and plausible fixings.
- Support wall-mounted equipment on rails or brackets that actually connect
  the wall and enclosure. Handles need return legs; conduits need an entry/gland.

### Structure and pipework

- Use a formed channel where the assembly calls for a channel, rather than a
  solid rectangular pier with lines painted on it.
- Seat baseplates on concrete/grout; seat washers and bolt heads on the plate.
  Check all contacts after moving or resizing any component.
- Make bolted pipe joints from separate flange faces with a smaller, recessed
  gasket between them. The pipe remains continuous inside; the visible recess
  does not imply a leaking process line.
- Treat pump casing splits similarly, with a seal and through-fixings.
- Do not put open gaps everywhere. Welded panels stay joined; compression seals
  contact their mating surfaces. Add visible weld returns only where justified.

### Floors, drains, hatches and grating

- Preserve walking height and thresholds. Give paving thickness and lower the
  joint bed rather than raising the entire route to manufacture a shadow.
- Real grating has openings through it. Remove the solid plate underneath the
  bars when that plate wrongly blocks the openings, and provide supporting frames.
- Cut drain openings into the owned paving; add a recessed seat, sump and open
  bars. A black rectangle beneath bars is not a substitute for a cut opening.
- Use hollow hatch curbs, seated lids and compression gaskets. Keep handles
  attached and maintenance access plausible.
- Retaining coping needs a bearing/bedding relationship, not arbitrary overlap
  or an unsupported air gap. Existing good slab gaps should simply be retained.

## Dimensions from the accepted pass

These are **reference values from this scene**, not engineering standards or
defaults for every object. Measure actual world scale and judge the intended
camera distance before adapting them. Do not multiply bevels by unapplied scale.

| Assembly | Implemented reference |
| --- | --- |
| Mineral facade panels | 44 mm solid thickness; 4 mm chamfer |
| Panel joints | About 22 mm horizontal / 26 mm vertical gap; 43 mm recessed bedding relative to face |
| Cabinet doors | 7 mm perimeter reveal; about 19.5 mm behind enclosure front |
| Vent front flange | 28 mm thick, with gasket recessed 17 mm behind its back |
| Pipe flange faces | 24 mm separation, containing a gasket at 84% of flange diameter |
| Roof catwalk | Separate modules with 16 mm expansion joints; roughly 40 mm clear slots between bearing bars |
| Refinery apron | 14 mm solid paving; recessed joint beds roughly 7.5–10.5 mm below face |
| Courtyard | Existing 36 mm slab gaps retained; drains rebuilt with open bars and approximately 170 mm sump depth |

Some detail is subpixel from an overview. Judge the geometry at player height
as well as in a close-up. Do not inflate every small gap until it reads from the
sky; use primary/secondary form to carry the distant view.

## Materials, weathering and lighting

For this approved exterior, keep machine grey, charcoal, warm mineral concrete,
localized oxide/rust browns and restrained ochre/orange safety accents. Do not
reintroduce teal into this exterior pass. This is not permission to recolour
unrelated departments or shared materials.

Use broad, low-frequency tonal/roughness variation and selective wear. Rust belongs
at vulnerable joints, runoff and damaged coatings; exposed edge metal belongs at
contact points. Keep substantial quiet areas. Avoid uniform speckling, blanket
grunge, a shiny plastic response or every edge receiving the same damage.

Let existing light reveal the construction. Bevels catch narrow highlights;
returns change value; recessed seals and cavities receive natural occlusion.
Check the new geometry under unchanged lighting before considering a lighting
adjustment. Do not conceal weak forms in darkness or compensate with crushed AO.
The target is grounded, readable stylized semi-realism, not copied game assets,
branding, photoreal noise or an abandoned bunker.

## Repeatable workflow and acceptance checks

1. Inspect the current saved map, ownership and actual pixels. Preserve the
   approved mine/cliff and neighbouring work; never run a recovery generator
   over a newer scene. Record the source hash and retain a recoverable checkpoint.
2. Pick one representative wall bay containing a panel joint and a fitting.
   Build its construction first; render at player height with an oblique view
   that exposes side returns. Keep the camera and lighting consistent.
3. Inspect actual pixels. Ask whether gaps have depth, fittings have support,
   openings are genuinely open, text is seated and the construction remains
   readable without microdetail. Correct this bay before repeating the method.
4. Expand only to owned parts with the same defect. Preserve welded joints,
   already-good gaps, door/track clearances and intended quiet surfaces.
5. Check manufactured meshes for manifold edges, degenerate faces and nonzero
   volume. Explicitly identify intentional surface overlays rather than silently
   exempting all objects. Check support contacts and unwanted intersections too;
   a manifold mesh alone does not prove good construction.
6. Measure representative reveals with rays or geometry, not just screenshots.
   Sample walking support and a player envelope along the actual routes. Compare
   uneven samples against the unchanged checkpoint before calling them regressions;
   never loosen a test merely to hide an obstruction.
7. Recheck the source hash before saving. Compare protected object geometry and
   transforms, materials and linked dependencies against the baseline.
8. Render complementary player views and a diagnostic overview from the same
   saved revision. Reopen in a fresh process, repeat a matching view and compare
   decoded pixels. Tie evidence to the scene hash and camera/render settings.

Follow the current resource policy: while the owner is gaming, one hidden,
BelowNormal headless Blender worker; Cycles CPU, one render thread, CPU denoising,
720p. Do not start a graphical editor, use the GPU or disturb another agent's scene.
Keep evidence in fixed transient locations, not per-iteration archives.

## Where to inspect the implementation

- Current source: [facility_environment.blend](../sections/facility-assembly/blender/facility_environment.blend).
- Geometry examples: [refine_exterior_joints.py](../sections/facility-assembly/blender/refine_exterior_joints.py).
- Saved-file checks: [verify_exterior_joints.py](../sections/facility-assembly/blender/verify_exterior_joints.py).
- Route baseline method: [inspect_joint_routes.py](../sections/facility-assembly/blender/inspect_joint_routes.py).
- Current transient evidence: `runtime/out/environment/exterior-joints/` contains
  `manifest.json`, `verification.json`, `cold-open.json` and the six reviewed views.

The builder is a revision-guarded, two-stage migration, **not an idempotent general
generator**. Its temporary first-bay candidate was removed after verification.
Read/reuse its construction helpers; do not blindly rerun it against today's file.
Transient captures may be replaced later: use their manifest to establish which
revision they show, and render the current saved scene when they are unavailable.

For the approved reference revision
`a6ca6430ed3a4dd08ae63f3cdb4d472b3f3bf00f52fcf3872bee97c2f906fa63`,
the cold-open detail matched pixel-for-pixel; 13,614 protected objects and all
855 material signatures were unchanged. The route check covered 353 sample
positions, with no new blockers/support failures; 11 uneven samples matched the
pre-edit scene. These are bounded Blender checks, not exhaustive collision tests,
an independent art score, Unity integration or a runtime performance claim.
