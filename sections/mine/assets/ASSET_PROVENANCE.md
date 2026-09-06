# Gullet Mine — Asset Provenance

The committed Gullet production source does **not** depend on copied game assets, scraped texture packs, or third-party mine meshes.

## Original generated assets

`../blender/gullet/tools/prepare_assets.py` deterministically authors:

- the continuous geological mine shell;
- carved floor mesh and state barriers;
- stylized material texture families;
- roughness and normal textures;
- fictional in-world shift card and navigation labels;
- localized scuff mask.

These outputs are generated into the section-local `blender/gullet/assets/` and `blender/gullet/textures/` directories and are consumed by `build_mine.py`.

## Procedural / code-authored geometry

The Blender builder authors all architecture, structural supports, rails, carts, blast gate, operator equipment, charge-issue cabinet, workbench, tools, ventilation, cables, pipework, pump/sump, excavation-state dressing, rubble, collision proxies, sockets and cameras from versioned source.

## External material

None is required by the current build. If future agents introduce any external asset, texture, decal, font, HDRI or mesh, they must record its source URL, creator, license, modification status and redistribution terms here before committing it. High-level visual principles from other games are not licenses to copy their assets.
