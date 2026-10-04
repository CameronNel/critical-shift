"""Extract the wooden R39 "Old mine" set from the assembled map into its own module.

Run against the (retiring) assembled map; the map file itself is not modified:
    blender -b sections/facility-assembly/blender/facility_environment.blend --python extract_r39_mine.py -- --output module_r39.blend --receipt extract-receipt.json

Keeps the collections R36 | 04 Mine toe rockfall, R38 | Old mine, R38 | Mine dressing, R39 | Old mine, R39 | Portal shed,
R40 | Mine cliff and R40 | Mine cliff dressing (with their children), every light they own and the scene world. Everything else
(all other rooms, the concrete mine collections, linked libraries) is removed from the saved copy.
"""
import json
import re
import sys

import bpy

KEEP = re.compile(r'^(R36 \| 04 Mine toe rockfall|R38 \| Old mine|R38 \| Mine dressing|R39 \| Old mine|R39 \| Portal shed|'
                  r'R40 \| Mine cliff|R40 \| Mine cliff dressing)')


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    return (a[a.index('--output') + 1] if '--output' in a else None,
            a[a.index('--receipt') + 1] if '--receipt' in a else None)


def main():
    roots = [c for c in bpy.data.collections if KEEP.match(c.name)]
    keep = set()
    for c in roots:
        keep.update(o.name for o in c.all_objects)
    before = len(bpy.data.objects)
    doomed = [o for o in bpy.data.objects if o.name not in keep]
    for o in doomed:
        bpy.data.objects.remove(o, do_unlink=True)
    keep_cols = set(c.name for c in roots)
    for c in roots:
        for ch in c.children_recursive:
            keep_cols.add(ch.name)
    for c in list(bpy.data.collections):
        if c.name not in keep_cols:
            bpy.data.collections.remove(c)
    scene = bpy.context.scene
    for c in list(scene.collection.children):
        scene.collection.children.unlink(c)
    mine = bpy.data.collections.new('MODULE_mine-r39')
    scene.collection.children.link(mine)
    for c in roots:
        if not any(c.name in p.children_recursive for p in roots if p is not c) and c.name not in [x.name for x in mine.children]:
            mine.children.link(c)
    for lib in list(bpy.data.libraries):
        bpy.data.libraries.remove(lib)
    for _ in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    return {'objects_before': before, 'objects_kept': len(bpy.data.objects), 'collections': [c.name for c in roots]}


if __name__ == '__main__':
    out, receipt = opts()
    r = main()
    if receipt:
        json.dump(r, open(receipt, 'w'), indent=2)
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print('EXTRACT:', json.dumps(r)[:400])
