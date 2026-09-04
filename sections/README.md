# Section Package Structure

Every playable location should live under sections/<section-name>/ and use the same internal structure.

## Required folders

### scenery/
Authoritative room or area specification: layout, dimensions, routes, interaction positions, dressing, lighting, materials, narrative environmental detail, and acceptance criteria.

### prompt/
The model-facing execution prompt used to build the section. Prompts should require repeated visual inspection, objective validation, correction, and re-rendering rather than a one-pass generation.

### blender/
Editable Blender source for the section. Prefer one clearly named primary source file, for example spawnroom.blend, plus scripts or procedural generation helpers when useful.

### art/
Approved concept art, composition studies, paintovers, visual references, material studies, signage concepts and other look-development sources.

### assets/
Section-specific production assets and exports: FBX/glTF meshes, textures, decals, reference documents and licensing notes for any external material.

## Naming

Use lowercase folder names with hyphens. Keep explicitly requested filenames for authoritative specs and prompts.

Do not mix generated screenshots, Blender sources and shipped exports into the same folder. Humans already invented enough entropy without help.
