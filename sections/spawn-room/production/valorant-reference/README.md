# Valorant reference-led iteration

The current desktop scene was copied through Blender MCP to `../checkpoints/before_valorant_reference_20260906.blend`. The inhabited delivery and earlier user edits remain preserved. The three `before/*_corner.png` images were captured from the actual live Blender viewport and posted in chat before editing began.

The user explicitly requested browser ChatGPT image generation, Blender MCP, native Computer Use, and an independent Luna review loop. The supported Codex in-app browser was used through the native Computer Use browser APIs. No custom input driver or hidden browser API was used. An earlier Firefox attempt was stopped by the Computer Use browser-policy limitation; it was not retried.

## Reference provenance

| Room | Browser conversation | Target |
|---|---|---|
| Briefing | https://chatgpt.com/c/6a9dc293-e9e8-83eb-8cca-8079349362cd | `targets/BRIEFING_reference.png` |
| Hall | https://chatgpt.com/c/6a9dc307-6a40-83eb-a28b-72f7c56d5c67 | `targets/HALL_reference.png` |
| Locker | https://chatgpt.com/c/6a9dc584-ce18-83ed-b78f-6bef10c8a547 | `targets/LOCKER_reference.png` |

Each conversation was given its exact room screenshot and asked to preserve the camera, architectural openings, major furniture and pod while generating one finished Valorant-style concept. Prompts requested warm practical pools, cooler shadows, broad restrained material variation, maintained wear, matte surfaces and grouped workplace detail. All generated images were exported from the browser's observed image assets and posted in the task chat.

Specific requests: matte timber and existing rug/two benches in briefing, refreshments/manuals/notices/plants; a modern dark-metal rear staff door, plants, culture poster, shift board, first aid, extinguisher and utility trolley in the hall; small 10 cm porcelain tiles and four identical low-sheen metal lockers with personal belongings, greenery and useful dressing in the locker room. No suits, new windows, closed room doors, invented sunlight or changed architecture. Incidental image-generation architecture discrepancies do not override the user's explicit layout constraints.

## Review policy

`reviews/review-00.*` contains the independent Luna baseline. Every category (lighting, art style, layout) is scored separately for every room against its target. A score below 90 requests concrete edits and another rendered comparison. A high average cannot hide a failed category. No score is a claim of human acceptance or literal perfection.

The deterministic authoring script is `../../blender/valorant_polish.py`; it consumes the protected live-state checkpoint and saves a new `spawnroom_valorant_walk.blend`. Scene edits and new assets remain editable native meshes, curves, text and materials. Existing CC0 packed textures are retained. Refer to each pass folder for contact checks, renders and source provenance.
