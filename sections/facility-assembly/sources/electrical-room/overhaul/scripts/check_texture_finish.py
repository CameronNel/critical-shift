"""Receipt for the texture finish: what changed between the reviewed R11 module and the texture-finished source.

Dump a signature from each file (Blender), then compare (plain Python 3):
    blender -b FILE.blend --python check_texture_finish.py -- --dump OUT.json
    python3 check_texture_finish.py --compare BEFORE.json AFTER.json RECEIPT.json

Dump records, per object: type, rounded world matrix, vertex/polygon counts, material names, modifier parameters, custom
properties, collections and visibility; plus cameras, lights, colour management, world strength, and (when present) the
grip pads' floor contact and equipment overlap. The comparison fails if anything outside the declared set changed.
"""
import json
import sys


def dump(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    scene = bpy.context.scene
    objs = {}
    for o in bpy.data.objects:
        entry = {
            'type': o.type,
            'matrix': [round(v, 5) for row in o.matrix_world for v in row],
            'hide_render': o.hide_render,
            'collections': sorted(c.name for c in o.users_collection),
            'props': {k: str(o[k]) for k in o.keys() if not k.startswith('_')},
        }
        if o.type == 'MESH':
            entry['verts'] = len(o.data.vertices)
            entry['polys'] = len(o.data.polygons)
            entry['materials'] = [m.name if m else None for m in o.data.materials]
            entry['modifiers'] = [
                [m.type, round(getattr(m, 'width', 0), 5), getattr(m, 'segments', 0)] if m.type == 'BEVEL' else [m.type]
                for m in o.modifiers]
        if o.type == 'LIGHT':
            entry['light'] = [round(o.data.energy, 3)] + [round(v, 4) for v in o.data.color]
        if o.type == 'CAMERA':
            entry['lens'] = round(o.data.lens, 4)
        objs[o.name] = entry
    result = {
        'objects': objs,
        'materials': sorted(m.name for m in bpy.data.materials),
        'view_transform': scene.view_settings.view_transform,
        'look': scene.view_settings.look,
        'exposure': scene.view_settings.exposure,
        'world_strength': scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value,
        'texture_revision': scene.get('electrical_texture_revision'),
    }
    pads = [o for o in bpy.data.objects if o.get('electrical_grip_pad')]
    if pads:
        deps = bpy.context.evaluated_depsgraph_get()
        ground = [o for o in bpy.data.objects if o.type == 'MESH' and (o.name == 'Floor' or 'slab' in o.name or 'epoxy panel' in o.name)]
        verts, polys = [], []
        for o in ground:
            m = o.evaluated_get(deps).to_mesh()
            base = len(verts)
            verts += [o.matrix_world @ v.co for v in m.vertices]
            polys += [tuple(base + i for i in p.vertices) for p in m.polygons]
        tree = BVHTree.FromPolygons(verts, polys)
        solid = [o for o in bpy.data.objects if o.type == 'MESH' and o not in ground and not o.get('assembly_member', '').startswith('Grip pad')
                 and 'wall' not in o.name.lower() and o.name not in ('Ceiling',) and 'curb' not in o.name.lower()]
        boxes = []
        for o in solid:
            corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
            lo = (min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners))
            hi = (max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners))
            if hi[2] > .02 and lo[2] < .3:
                boxes.append((o.name, lo, hi))
        report = []
        for root in pads:
            body = next(c for c in root.children if c.type == 'MESH')
            corners = [body.matrix_world @ Vector(c) for c in body.bound_box]
            lo = Vector((min(c.x for c in corners), min(c.y for c in corners), 0))
            hi = Vector((max(c.x for c in corners), max(c.y for c in corners), 0))
            samples = [(lo.x + (hi.x - lo.x) * a, lo.y + (hi.y - lo.y) * b) for a in (.05, .5, .95) for b in (.05, .5, .95)]
            gaps = []
            for x, y in samples:
                hit = tree.ray_cast(Vector((x, y, 1.0)), Vector((0, 0, -1)))
                gaps.append(None if hit[0] is None else round(hit[0].z, 4))
            overlaps = [n for n, blo, bhi in boxes
                        if blo[0] < hi.x and bhi[0] > lo.x and blo[1] < hi.y and bhi[1] > lo.y and blo[2] < .04]
            report.append({'pad': root.name, 'floor_top_z_under_samples': gaps,
                           'footprint_xy': [round(lo.x, 2), round(lo.y, 2), round(hi.x, 2), round(hi.y, 2)],
                           'equipment_overlapping_footprint_below_4cm': overlaps})
        result['pads'] = report
    with open(out, 'w') as f:
        json.dump(result, f)
    print('dumped', len(objs), 'objects')


def compare(before_path, after_path, out):
    b, a = json.load(open(before_path)), json.load(open(after_path))
    changed = {'modifiers_only': [], 'other': []}
    for name, entry in b['objects'].items():
        new = a['objects'].get(name)
        if new is None:
            changed['other'].append((name, 'missing after'))
            continue
        diff = [k for k in entry if entry[k] != new.get(k)]
        if diff == ['modifiers'] and all(m[0] == x[0] for m, x in zip(entry['modifiers'], new['modifiers'])):
            changed['modifiers_only'].append(name)
        elif diff:
            changed['other'].append((name, diff))
    added = sorted(set(a['objects']) - set(b['objects']))
    pads_ok = all(
        all(g is not None and -.003 <= g <= .003 for g in p['floor_top_z_under_samples']) and not p['equipment_overlapping_footprint_below_4cm']
        for p in a.get('pads', []))
    bevel_changes = sorted({(tuple(m), tuple(x)) for n in changed['modifiers_only']
                            for m, x in zip(b['objects'][n]['modifiers'], a['objects'][n]['modifiers']) if m != x})
    receipt = {
        'objects_before': len(b['objects']), 'objects_after': len(a['objects']),
        'unchanged_objects': len(b['objects']) - len(changed['modifiers_only']) - len(changed['other']),
        'objects_with_bevel_changes_only': len(changed['modifiers_only']),
        'distinct_bevel_changes': [[list(m), list(x)] for m, x in bevel_changes][:20],
        'objects_changed_in_other_ways': changed['other'],
        'objects_added': added,
        'added_are_only_grip_pads': all(n.startswith('Grip pad') for n in added),
        'materials_added': sorted(set(a['materials']) - set(b['materials'])),
        'materials_removed': sorted(set(b['materials']) - set(a['materials'])),
        'cameras_and_lights_unchanged': all(
            b['objects'][n].get(k) == a['objects'][n].get(k)
            for n in b['objects'] if b['objects'][n]['type'] in ('CAMERA', 'LIGHT') for k in ('matrix', 'lens', 'light')),
        'colour_management_unchanged': [b[k] == a[k] for k in ('view_transform', 'look', 'exposure', 'world_strength')],
        'grip_pads': a.get('pads', []),
        'grip_pads_on_floor_and_clear_of_equipment': pads_ok,
        'texture_revision': a.get('texture_revision'),
    }
    receipt['pass'] = (not changed['other'] and receipt['added_are_only_grip_pads'] and pads_ok
                       and receipt['cameras_and_lights_unchanged'] and all(receipt['colour_management_unchanged']))
    json.dump(receipt, open(out, 'w'), indent=2)
    print('PASS' if receipt['pass'] else 'FAIL', json.dumps({k: receipt[k] for k in ('objects_with_bevel_changes_only', 'objects_changed_in_other_ways', 'objects_added', 'grip_pads_on_floor_and_clear_of_equipment', 'materials_added')})[:600])


if __name__ == '__main__':
    argv = sys.argv
    if '--compare' in argv:
        i = argv.index('--compare')
        compare(*argv[i + 1:i + 4])
    else:
        dump(argv[argv.index('--dump') + 1])
