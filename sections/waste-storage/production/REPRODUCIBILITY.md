# Saved-artifact and source verification

W21 was rebuilt from factory-empty Blender using the full original construction and correction sequence. The resulting2341 objects match the working artifact's evaluated geometry, transforms, hierarchy, cameras, lights and material assignments exactly under the six-decimal fingerprint representation. Material node fingerprints and embedded connection contract also match. See `validation/W21/rebuild-comparison.json` and `source-replay.log`.

The W22 material refinement was then applied independently to each matching W21 artifact. Their W22 object, material and contract fingerprints also match exactly: `validation/W22/rebuild-comparison.json`. The retained full authoring entry point includes the same final pass. This is a factory-empty W21 replay plus independently verified final pass, not a falsely claimed second complete factory-empty W22 execution.

The initial W20 replay failure is retained as `validation/W20/source-replay-failed.log`. It exposed a shader-loop variable that shadowed the geometry linking helper. Both collisions were corrected before successful replay.

The final artifact was separately cold-opened in the live Blender instance. Readback confirmed W22,2341 objects,20 cameras and no unsaved changes. The old W02 live file was preserved. The bridge reported a stale camera reference after opening; fresh discovery/re-claim/readback succeeded and the lease was released. See `validation/W22/live-open.json`.

Raw mesh boundary edges were checked on temporary evaluated copies welded at1µm. Remaining non-font boundaries are intentionally open paint-wear/coating surfaces. This is topology classification, not a claim of engineering certification or engine collision behavior.

External dependencies: procedural materials and native text; no external geometry libraries or unpacked texture assets required. Numerical route, door-pose and process checks remain distinct from visual approval.

The full20-image cold repeat completed with identical camera/settings manifests. Decoded pixels differ by at most1/255 in122–213 pixels per1,296,000-pixel image; largest mean absolute channel difference0.00005478395 on the0–255 scale. This is visually stable, not mathematically identical pixel output. The artifact SHA256 remained unchanged. See `validation/W22/cold-pixel-comparison.json` and the exact cold fingerprint comparison.
