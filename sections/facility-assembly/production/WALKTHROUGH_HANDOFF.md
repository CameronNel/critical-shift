# Optimized Blender walkthrough

Open `../blender/facility_walkthrough.blend` in the configured Blender session, or run `../blender/OPEN_WALKTHROUGH.ps1` to restore the walkthrough profile and installed control add-ons.

- Shift+F starts native Blender Walk Navigation with gravity disabled. WASD moves, E/Q changes height. Mouse looks; left-click confirms and Escape cancels. This is inspection movement, not game collision.
- N > Walkthrough exposes the fast display toggle and reserved-connection guides. Turn fast display off to inspect original linked authoring assets; individual section files remain the editing sources. The display caches are intentionally unselectable and never rendered.
- 24 consolidated meshes replace approximately 44,000 individual visible source objects, retaining 5,882,756 evaluated faces and section bounds. No geometry was decimated. Original source files and A05 master remain unchanged; a pre-optimization copy preserves the user's open scene state.
- Baseline redraw test: 4.86 FPS. Optimized same-view redraw: 68.35 FPS. Rotating redraw: 115.43 FPS. These are redraw measurements on this machine, not guarantees for every walking viewpoint.
- Fast caches preserve evaluated positions, faces and material colors. They omit UV/animation/custom shading data and are for Solid viewport inspection. Turn fast display off for material/render review and rebuild caches after editing source geometry.
- Blender MCP is enabled and registered in the walkthrough window. Computer use successfully selected the window, changed editors and enabled MCP. Synthetic instantaneous key taps did not establish sustained walking movement; the native walk operator and Shift+F keymap were independently verified through MCP.

Replay cache generation with `blender/build_walkthrough_proxies.py` using Blender 5.2 headlessly. It reads the pre-optimization copy and writes `walkthrough_proxy_meshes.blend` plus a face/bounds report. Install the repository's `facility_walkthrough_tools.py` as the matching Blender add-on to retain the panel and gravity-safe shortcut.
