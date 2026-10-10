"""Owned finish contrast for drive guides and absorber pins.

Updates the inputs actually linked to each surface, including existing scene
materials. Geometry, bores, guides, animation and the shared library are untouched.
"""
import json

FINISHES = (
    ('RH refine absorber satin', (.10, .105, .10), .60, .70),
    ('RH refine drive guide metal', (.68, .69, .685), .30, .75),
)


def apply(scene, materials):
    rows = []
    for name, colour, roughness, metallic in FINISHES:
        material = materials[name]
        tree = material.node_tree
        surfaces = [n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED']
        bases = [n for n in tree.nodes if n.type == 'VECT_MATH'
                 and n.operation == 'SCALE' and not n.inputs[0].is_linked]
        assert len(surfaces) == len(bases) == 1, ('Unexpected owned finish graph', name)
        surface = surfaces[0]
        links = surface.inputs['Roughness'].links
        assert len(links) == 1 and links[0].from_node.type == 'MAP_RANGE', name
        variation = links[0].from_node
        before = (tuple(bases[0].inputs[0].default_value),
                  surface.inputs['Metallic'].default_value,
                  variation.inputs['To Min'].default_value,
                  variation.inputs['To Max'].default_value)
        bases[0].inputs[0].default_value = colour
        surface.inputs['Metallic'].default_value = metallic
        variation.inputs['To Min'].default_value = roughness * .82
        variation.inputs['To Max'].default_value = roughness * 1.18
        after = (tuple(bases[0].inputs[0].default_value),
                 surface.inputs['Metallic'].default_value,
                 variation.inputs['To Min'].default_value,
                 variation.inputs['To Max'].default_value)
        rows.append({'material': name, 'changed': before != after,
                     'base_colour': colour, 'roughness_range': after[2:],
                     'metallic': metallic})
    report = {'materials': rows, 'scope': 'Two owned material inputs only; no geometry, animation or shared-library edits'}
    scene['rh_rod_finish_correction'] = json.dumps(report, sort_keys=True)
    return report
