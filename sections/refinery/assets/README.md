# Assets and dependencies

cart_geometry.json faithfully serializes the existing Gullet ore_cart geometry: 87 mesh objects, parent transforms, UV data and source-fragment SHA256 values. The normal refinery build reads this snapshot without loading the mine or an occupied Blender session. cart.py --extract can regenerate it from sections/mine/blender/gullet.

textures/concrete/ contains three unchanged maps copied from the existing project asset ambientCG Concrete046: color, height and roughness. provenance.json retains the source/license URLs and original hashes. These CC0 maps are checked before build, palette-remapped in the floor shader, and packed into Refinery.blend. No raw photographic color is used as the surface appearance.

All remaining shaders and geometry are original procedural source. No downloads, external linked libraries, add-ons or live-session dependencies are required. The copied support-contact validator is called through its read-only function and writes only refinery reports.
