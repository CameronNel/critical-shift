# Spawn visual correction — 11 October 2026

The owner rejected the harsh Unity walls. This follow-up corrects the runtime
conversion on the PR95 six-room assembly, preserving all Blender source rooms,
the assembly builder and gameplay bindings. It does not advance art acceptance.

## What I did wrong

1. I omitted Blender's dielectric IOR/specular level from the material contract.
   The three wall paints use IOR 1.5 and Specular IOR Level 0.3. Unity's Standard
   metallic shader uses its default dielectric response. Exporting base colour,
   metallic, roughness and normals alone did not preserve that paint response.
2. I used the converted wall maps without a material isolation comparison.
   I described the grain as an excessive bump effect before separating normal,
   roughness and colour contributions. That was a hypothesis, not a measured cause.
3. I switched the practicals to real-time direct point lighting after solving a
   self-occlusion problem. The sharp pendant silhouettes visibly differ from the
   Blender reference. Passing the light bake did not establish light equivalence.
4. I allowed the completed gameplay/import work to sound like finished spawn
   visuals. Native physical tests and CI establish their stated behavior; they
   do not establish a visual match. The earlier captures show open visual defects.

## Correction and evidence

The same-camera controls separated fine normal-map grain from broad colour
variation. Turning normals off reduced fine grain strongly; it did not remove
the broad colour variation. Constant roughness made fine grain worse. Removing
point shadows removed the large pendant silhouettes. My earlier blanket claim
that the grain was mainly colour was therefore also too broad.

The runtime conversion now:

- Preserves constant Principled IOR/specular reflectivity. The wall paint's
  dielectric F0 is 0.024 (upper wall) and 0.0304 (dado), rather than the
  previous Standard default of 0.04.
- Rebakes the original procedural recipes for 52 wall/dado meshes into a dedicated
  4096px atlas. Derived delivery UVs retain evaluated source geometry, with the
  same triangle counts and a 2mm bounds guard. No wall recipe is blurred or replaced.
- Keeps finite-emitter baked shadow masks for the two mixed pendant lights.
  The remaining practicals are baked. Movable objects retain real-time caster
  shadows under the pendants. The old post-bake switch to real-time lighting and
  clearing of the mask was removed.
- Uses probe lighting for the six tiny socket faces, as for the existing two-sided
  whiteboard, to avoid dark chart faces. Their geometry and collision stay intact.

The original Blender render, previous Unity capture and corrected Unity capture
are compared in the [correction gallery](spawn-visual-correction-20261011/README.md).
The pale pink/navy colour-only diagnostic was rendered in Blender with wall
lighting removed; it is explicitly labelled a diagnostic, not the final Unity view.
Claude's screenshot review is useful direction, but screenshot colour estimates
are not treated as source material values or used to repaint the authoring scene.

The final evidence records native capture, physical tests and Player validation.
A local upper-wall patch measurement checks fine grain; it is not a whole-scene
colour grade or acceptance score. The final correction reduced its high-pass RMS
from 1.726 to 0.775 (source 0.585), while retaining authored surface detail.
This approximately 55% reduction applies only to that measured patch. The darker
upper wall and charcoal lower wall are visibly closer; floor illumination and
surface response still differ.

The corrected view has much closer terracotta/charcoal walls and soft pendant
falloff. Blender still differs in sideboard illumination, screen reflections and
some material response. This correction is not a claim of perfect Cycles matching,
target-GPU performance or human art acceptance. All source rooms and the PR95
assembly are preserved. The other five rooms remain preview conversions.


## Reflection import regression during suit work (11 October 2026)

A suit appearance refresh rewrote metadata for existing generated assets. That
reset the three room reflection imports from specular convolution to unfiltered
cubemaps. The reflection capture code had relied on the previous importer state
instead of setting this required state explicitly. Metadata reset also changed trilinear/clamped reflection sampling to bilinear/repeating.
Rough walls then sampled sharp
fixture reflections through their fine source normals, producing the severe
cream speckles. The same regression made rubber and pod parts too shiny.

Restoring the shared room shader alone did not remove the speckles. Same-camera
controls retained the original baked wall texture hashes: disabling normals
removed the speckles but left broad glossy bands; restoring specular convolution
removed the speckles with source normals still enabled. The earlier approved bake
log also records convolution, while the failed refresh log does not. The final
lighting and reflection snapshots are regenerated after this correction.

Preparation now creates metadata only when missing, retaining existing importer
settings. Reflection baking explicitly sets linear cubemap import, mipmaps and
specular convolution, trilinear mip blending and clamped sampling. The saved
approved Player independently confirms trilinear/clamped RGBAHalf cubemaps with
nine mip levels. Capture and prepared-scene build validation reject imports
that lose these settings, and a native integration test inspects all three
persisted reflection textures. The hanging hood uses its own shader; the shared
room surface shader is byte-identical to the approved `467a4112` version. No source
wall material, room geometry or Blender file is edited to hide this regression.

Final suit and room evidence is recorded in the
[suit correction gallery](spawn-suit-correction-20261011/README.md). Earlier failed
captures remain in ignored scratch output, not in the final comparison gallery.
