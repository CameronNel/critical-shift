# Procedural surfacing contract

Materials belong to the additive editable candidate. The original source and its material library remain unchanged. Every used material is embedded in the blend; no image textures, linked libraries, baked maps, atlas or trim-sheet files are required.

`material_contract_<revision>.json` records the exact source hash, visible material coordinate inputs and named mesh UV layers without changing the source. R51 has 290 visible materials, no image-texture nodes and no UV shader consumers. Existing named UV layers remain on 2,046 visible meshes; new/rebuilt procedural surfaces do not require a UV map for this Blender source. This is a coordinate/dependency inventory, not checker-based UV approval or runtime material equivalence.

| Family | Coordinate/scale policy | Response |
|---|---|---|
| Concrete and traffic floor | World position in metres; restrained low-frequency variation, local joint/impact damage | Rough, nonmetallic; actual slab joints and aggregate recesses |
| Coated and oxidized steel | World-position weathering; Generated coordinates locate edges, with the transition converted to a measured 2–12 mm band | Rough coating, more metallic exposed steel; quiet broad coating fade and distinct contact runoff/roughness; true surface-projected losses at selected collar/handling zones, with interrupted substrate coverage and no continuous perimeter line and localized lower contact wear |
| Wood | World-position grain stretched `(2,95,18)`; local handling/oil masks | Rough timber, exposed edge plies and actual damage |
| Cloth/felt and webbing | World-position small-scale variation; volume and folds carry the shape | Matte, nonmetallic; supported/draped surfaces |
| Rubber | Physical profiled parts and compression/distortion | Dark, matte low-specular elastomer with rounded compliant profile and failed-seal compression; no decorative glow |
| Paper | Thin folded geometry with supported printing | Matte paper and ink |
| Inspection glass | Embedded Principled transmission, IOR 1.46 | Clear sealed panes with modeled rims/wires |
| Lamp lenses | Source-paired emission in a modeled fixture aperture | Every active lens is tracked; failed circuits emit zero |

Fixed production images are the material/style evidence, with the same practical fixtures, camera optics and color management across comparisons. No external diagnostic lights are added. Baking/converting these procedural materials for Unity or another renderer is outside this editable-source package and remains unverified.

The R44 validator additionally checks recursive material graphs for links to disabled sockets. Earlier R40–R43 broad coating fields used the disabled LENGTH Vector output; their intended spatial localization is not credited. R44 uses the enabled scalar Value output and passes this expanded check. Appearance remains subject to the actual fixed-view review.

R49 introduced small single-layer exposed-undercoat losses on measured visible collar/carrier handling faces. Their vertices are projected to the actual curved shells and every face gap is validated; there is no surrounding primer border or broad cloudy mask. R50 enlarges seven of these losses at the measured visible collar/carrier/handling faces. Both independent targeted C02/W04 reviews find the broad-shell material gap resolved without outline/cloud/camouflage artifacts; final full-cycle judgment remains separate.

R51 retains exactly the R50 geometry, material graphs and fixture powers; its native Cycles light-tree sampling is disabled after the actual single-setting W02 diagnostic restored missing portal pools. This sampling mode is recorded explicitly in new main/detail manifests. No new illumination or material is introduced by the sampling correction. Both final full independent material scores are99; all23 actual views and selected own cold pixels complete.
