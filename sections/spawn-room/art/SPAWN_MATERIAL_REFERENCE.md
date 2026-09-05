# Spawn Room Material Reference

**Visual plates:** [10 material/wear](reference/10_material_wear_matrix.svg), [20 colour palette](reference/20_spawn_colour_palette.svg), [11 lighting](reference/11_lighting_plan.svg)

This is a Blender-oriented material calibration guide. Numeric roughness values are starting ranges, not rigid renderer law. Final approval comes from gameplay-camera renders.

## 1. Painted industrial metal

Use for:
- door frames;
- lockers;
- suit bay structure;
- utility cabinets;
- chamber body;
- radiation meter housing.

Starting behavior:
- metallic: 0–0.25 depending on coating;
- roughness: ~0.55–0.75;
- broad roughness variation only;
- subtle color drift over large areas;
- chips localized to impacts/handles/feet.

Do not use a procedural edge-wear mask on every edge.

## 2. Bare / exposed metal

Use sparingly:
- hinge pins;
- threshold plates;
- fastener heads;
- machine shafts;
- internal wear areas.

Starting behavior:
- metallic: 0.7–1.0;
- roughness: 0.25–0.60;
- never mirror chrome;
- do not make every trim piece exposed metal.

## 3. Wall / plaster / coated structural surface

Use:
- main wall fields;
- ceiling fields;
- structural infill.

Starting behavior:
- metallic: 0;
- roughness: 0.70–0.90;
- low-frequency color variation;
- rare patch/repair;
- no scanned concrete micro-noise.

## 4. Restrained plastic

Use:
- knobs;
- housings;
- handles;
- small instrument covers.

Starting behavior:
- metallic: 0;
- roughness: 0.40–0.65;
- molded surface variation;
- specular highlight should be softer than current failed renders.

A plastic part should look intentionally molded, not like the whole room shares a plastic shader.

## 5. Rubber

Use:
- seals;
- boots;
- gloves where appropriate;
- floor mats;
- bumpers;
- cable insulation.

Starting behavior:
- metallic: 0;
- roughness: 0.75–0.95;
- dark but not crushed black;
- subtle soft normal/roughness variation.

## 6. PPE fabric

Use:
- hazmat suit;
- soft straps;
- cloth bag/rag.

Starting behavior:
- metallic: 0;
- roughness: 0.70–0.90;
- broad shading from modeled folds;
- weave should be invisible at normal gameplay distance;
- localized use dirt only.

The silhouette and folds do more work than the texture.

## 7. Institutional floor

Starting behavior:
- metallic: 0;
- roughness: 0.45–0.70;
- subtle panel/tile variation;
- route wear slightly changes roughness/value;
- no permanent wet-resin look.

## 8. Glass / acrylic

Use:
- chamber partial enclosure;
- door viewport;
- screen covers.

Starting behavior:
- roughness: 0.05–0.20;
- modest reflection;
- slightly imperfect touch areas;
- avoid pristine invisible glass and blue sci-fi glass.

## 9. Paper / card

Use:
- clipboard;
- notice board;
- posters;
- checklists.

Starting behavior:
- roughness: 0.80–1.0;
- small bend/curl where it improves silhouette;
- no every-sheet-perfectly-flat repetition.

## 10. Wear distribution

Use the 80/20 discipline:
- 80–90% maintained;
- 10–20% evidence of use.

High-wear zones:
- handles;
- thresholds;
- bench contact edges;
- floor routes;
- suit-bay standing zones;
- frequently touched controls.

Low-wear zones:
- ceiling;
- upper wall;
- inaccessible panel centers;
- rarely touched machine backs.

## 11. Material review render

Before dressing the room, render one validation frame containing:
- wall;
- painted metal;
- plastic;
- rubber;
- fabric;
- floor;
- glass;
- paper.

FAIL if the seven non-paper families could plausibly be the same shader with different colors.
