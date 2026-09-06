# User screenshot corrections

Source: `../../../../blender/spawnroom_revised_walk.blend`.

This directory contains unmodified renders from a fresh Blender 5.2 process opening the saved source. `CONTACT_SHEET.jpg` is a labeled overview; full PNG files are the evidence. Eleven established validation camera transforms are retained, with three additional views aimed at the user's floor, entrance and locker-room concerns.

`checks.json`: 19 passing assertions, including actual scene-ray doorway tests and floor geometry checks. `contacts.json`: 67 passing support registrations. `clearance_and_states.json`: no blocked doorway rays; all six pod states pass. `cold_comparison.json`: 14 images match the preceding process within one 8-bit channel value; greatest image mean difference is 0.000344. `provenance.json` identifies the source hash and process configuration.

The source has been separately opened and inspected through the desktop Blender viewport. Textures, scene lighting, filtered jittered shadows and clear blended pod glass are enabled. User instructions and the correction history are in `../../../USER_REVISION_20260906.md`.
