# Critic A — style slice 07

## Scope and evidence

I inspected the actual `renders/slice07/C10_Workbench.png` and `C03_Reverse.png` pixels, compared the workbench with slice02, and checked the supplied `production/validation_slice07.json`. References inspected: Spawn `VALIDATE_Hero_A.png` and refinery R24 `CAM_MATERIAL.png`. This is an independent repair-corner style review. C03 is lighting/palette context; its far opening is outside this isolated module and does not establish how an adjoining room should look. No whole-room, runtime, or cold-start acceptance is implied.

## Finding

Slice07 is a material improvement over slice02. The folded steel tool board, more individual tool profiles, articulated task lamp, exposed plywood edge, salvage tray, and draped item make the corner feel constructed and used. The muted green-grey palette continues to fit the pessimistic direction. The remaining visual gap is concentrated in the close view: most of the new wear reads as a few clean, decorative marks, while the bench and tools remain unusually orderly and the task light does not produce a strong enough local lighting hierarchy in the pixels. This is a much better slice, but it still falls short of the Spawn finish reference and does not yet prove a deeply neglected repair corner.

In `C10_Workbench`, the broad scratched panel and plywood grain add useful surface history, but the wear is sparse and evenly legible as marks rather than a convincing pattern of handling, repair and residue. The top has prominent straight grain that makes the worktop read as clean wood; where plywood is intentional, the exposed plies are a good start, but the top needs edge damage and repair staining that tie it to the repair task. The white draped object reads more like a stiff sheet or paper than a rag because it has a flat, sharp silhouette and little visible thickness or folding. The tool row is still carefully spaced, while the bench surface has ample empty area and the lower salvage tray/filter forms are barely legible from this camera.

The task lamp is a useful authored addition, but its bright white underside is a blank disc and the surrounding bench does not show a distinct pool, cast shadows from the vice/tools, or a clear falloff in this render. Against Spawn, the slice has less separation between the light's focal area and surrounding wall. Against refinery R24, the gloomy value range is closer, but that reference is already near the dark-detail limit; keep Waste's useful local contrast rather than pushing the whole view down.

`C03_Reverse` looks visually unchanged from slice02. It keeps the room dark, but does not provide evidence about the task lamp or the repair corner's local value hierarchy. Its central opening reads black; given the isolated-module boundary, I do not treat that as a defect in this repair-corner review or infer a neighboring room. I cannot determine the receiving-aperture treatment from these two images.

## Highest-impact residual fixes

1. **Make the wear tell one coherent maintenance story.** Add a restrained, concentrated residue and handling pattern around the vise, tool hang points, bench front edge and the place where the removed seal is worked. Use a few distinct rubbed, stained, chipped and repaired areas with varied size and opacity. Avoid scattering more clean scratches across every surface.
2. **Make the draped material read as cloth.** Add a folded, thicker edge and broad slack folds, with a muted dirty fabric response. Give it believable contact with the worktop. At this camera its current thin white angular silhouette is the most obvious storytelling prop that fails to read immediately.
3. **Break the showroom order with purposeful repair use.** The tools are still lined up evenly and the bench is sparse. Show one or two pieces in active use or recently set down, plus a readable damaged/replaced seal or small amount of task-specific repair stock. Keep the corner functional and uncluttered.
4. **Give the task lamp visible lighting work.** In the close view, the lamp should pick out the vice and the worked surface with a legible local pool, directional shadows, and a measured falloff on the wall. The shade can retain a dirty diffuser value instead of reading as a clean white disk. The validation file establishes registered fixture/lens proximity and alignment, but pixel appearance must still carry the lighting design.
5. **Clarify the lower salvage cluster from this camera.** The tray and filters are mostly lost under the bench. Improve their visible silhouette/value grouping or their placement within the crop so the claimed salvage/use cluster reads at gameplay scale; do not add detail that cannot be seen here.
6. **Temper the worktop grain and strengthen material separation.** Preserve the exposed ply as a specific repair, but reduce the dominant straight grain if it makes the bench feel like clean furniture. Differentiate worn plywood, painted/folded steel, tool metal, rubber grip and fabric through broad value/roughness response, not more high-frequency texture.

## Bounded technical evidence

The supplied validation JSON reports PASS, with 247 protected original transforms and no changes; world strength 0; 20 registered fixture/lens pairs passing; 68 new and 57 inherited contacts passing; zero unregistered new supports, route obstructions, or issues; 48 closed-mesh normal checks passing; and the sampled lane clear. These are useful checks for this checkpoint, not proof of all contacts, complete fixture beam coverage, collision certification, adjacent-section integration, or cold rebuild. The report itself states that anchor/lane rays are sampled and nearest-lens distance does not prove full beam aperture coverage. I assign no numeric technical score from this evidence and do not claim whole-room acceptance.

## Gate status

**Visual style slice: improved substantially; revise the remaining close-view issues before treating it as a >=99 finish-quality proof.** The dominant remaining defects are the paper-like rag, overly orderly tools, weak visible task-light pool, and wear that reads as sparse added marks rather than an authored maintenance history. I assign no score in this slice review. The current evidence is insufficient for whole-room or final technical acceptance.
