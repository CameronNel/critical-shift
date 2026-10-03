"""Promote the turbine rebuild (`rebuild/turbine_room_v2_geo.blend`) to `module.blend`.

WORK IN PROGRESS, DO NOT RUN YET. KNOWN DEFECT: `clamp()` calls `remove_doubles` and `dissolve_degenerate` on the whole mesh, which
deleted about 65,000 faces of machinery and 20,000 of architecture (shipping triangles fell from about 390k to 219k). It must be
replaced by a targeted fix that only deletes faces the clamp flattened (zero area). The trim, marker, doorway and texture steps
passed the numeric checks in `verify_promotion.py`. No promoted `module.blend` has been committed.

    blender -b rebuild/turbine_room_v2_geo.blend --python promote_v2.py -- --old module_pre_promotion.blend \
        --output module.blend --receipt promotion_receipt.json

What it does (MAP.md "Overhauling a room", promotion step):
 1. Trims the rebuild's door dressing back to the room's measured envelope (y -0.36 .. 25.4, the old module's extents):
    whole islands that lie entirely outside are deleted, islands that cross the limit lose only the faces beyond it.
 2. Carries over from the old module the 16 interface and interaction markers (6 IF_*, 6 INTERACT_*, 2 FAULT_*, AUDIO, HOOK)
    with names, properties and rotations unchanged. The 6 IF_* contract markers keep their exact positions. The 6 gameplay anchors
    that no longer lie on the new equipment are re-seated onto the equivalent new equipment. The 41 SUPPORT_* contact markers
    belonged to old props that no longer exist and are NOT carried over.
 3. Wraps everything in the `MODULE_turbine-room` collection the map links, and points textures at `//rebuild/...`.
The old module is never modified; this reads it only to append the markers.
"""
import json
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

YS, YN = -0.36, 25.4
KEEP_PREFIXES = ('IF_', 'INTERACT_', 'FAULT_', 'AUDIO_', 'HOOK_')
TRIM_OBJECTS = ('TURBINE_ARCH', 'TURBINE_DECAL', 'TURBINE_DECAL_E', 'TURBINE_MACH', 'TURBINE_PROPS', 'OCCLUDER_ONLY', 'TURBINE_GLASS')
# New equipment positions (control station units at x = -2.95, y = 2.95 / 4.0 / 5.05; panel slope from machinery.controls)
CX, SLOPE = -2.95, (.4, .76, -.05, 1.12)
NRM = (.62, .78)


def panel_point(yc, t, dy=0.0, lift=.05):
    x = CX + SLOPE[0] - (SLOPE[0] - SLOPE[2]) * t
    z = SLOPE[1] + (SLOPE[3] - SLOPE[1]) * t
    return (round(x + NRM[0] * lift, 4), round(yc + dy, 4), round(z + NRM[1] * lift, 4))


RESEAT = {
    'INTERACT_TURBINE_THROTTLE': (panel_point(4.0, .30), 'control unit 2 toggle bank'),
    'INTERACT_TURBINE_LOAD': (panel_point(2.95, .22), 'control unit 1 indicator and switch row'),
    'INTERACT_OVERSPEED_TRIP': (panel_point(5.05, .28, -.28), 'control unit 3 red guarded button'),
    'INTERACT_TURBINE_REPAIR': ((-0.9, 17.0, 1.0), 'maintenance-bay rotor, mid span'),
    'HOOK_SHARED_RESERVE': ((-3.78, 4.0, 2.45), 'mimic display screen on the west wall (marker is a display for the shared electrical reserve)'),
    'FAULT_STEAM_LEAK': ((8.4, 0.4, 4.9), 'steam inlet flange at U01 (marker means the actual inlet flange)'),
}


def opts():
    a = sys.argv[sys.argv.index('--') + 1:]
    g = lambda k: a[a.index(k) + 1] if k in a else None
    return g('--old'), g('--output'), g('--receipt')


def trim(obj):
    """Delete geometry outside y [YS, YN] without cutting through solid parts."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    world = obj.matrix_world
    bm.faces.ensure_lookup_table()
    seen, islands = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack, comp = [f], []
        seen.add(f.index)
        while stack:
            x = stack.pop()
            comp.append(x)
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        stack.append(g)
        islands.append(comp)
    doomed, whole, partial = [], 0, 0
    for comp in islands:
        ys = [(world @ v.co).y for f in comp for v in f.verts]
        if min(ys) >= YS - 1e-4 and max(ys) <= YN + 1e-4:
            continue
        inside = [f for f in comp if YS <= (world @ f.calc_center_median()).y <= YN]
        if not inside:
            doomed += comp
            whole += 1
        else:
            doomed += [f for f in comp if f not in inside]
            partial += 1
    if doomed:
        bmesh.ops.delete(bm, geom=list(set(doomed)), context='FACES')
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
        bm.to_mesh(obj.data)
        obj.data.update()
    removed = len(set(doomed))
    bm.free()
    return {'faces_removed': removed, 'islands_removed_whole': whole, 'islands_clipped': partial}


def clamp(obj):
    """Snap vertices still beyond the envelope (long faces that straddle it) back onto it, then tidy degenerates."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    world, inv = obj.matrix_world, obj.matrix_world.inverted()
    moved = 0
    for v in bm.verts:
        w = world @ v.co
        y = min(max(w.y, YS), YN)
        if y != w.y:
            w.y = y
            v.co = inv @ w
            moved += 1
    if moved:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges)
        bm.to_mesh(obj.data)
        obj.data.update()
    bm.free()
    return moved


def clear_doorways(obj, receipt):
    """Move equipment standing inside a door's 2.4 m clear width (|x| <= 1.2, z 0.1..2.6) sideways. Pieces that touch each
    other (a cabinet and its plates, handles, panels) are moved as one cluster; if no sideways shift up to 1 m clears
    the rest of the room, the whole cluster is deleted."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.faces.ensure_lookup_table()
    seen, comps = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        st, comp = [f], [f]
        seen.add(f.index)
        while st:
            x = st.pop()
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); st.append(g); comp.append(g)
        comps.append(comp)

    def box(comp):
        vs = [v.co for f in comp for v in f.verts]
        return [min(v.x for v in vs), max(v.x for v in vs), min(v.y for v in vs), max(v.y for v in vs), min(v.z for v in vs), max(v.z for v in vs)]

    boxes = [box(c) for c in comps]
    actions = []
    for door, y0 in (('D01', 0.0), ('D02', 24.0)):
        seeds = [i for i, bx in enumerate(boxes)
                 if bx[2] < y0 + (1.0 if door == 'D01' else .1) and bx[3] > y0 - 1.0 and bx[5] > .1 and bx[4] < 2.6 and bx[1] > -1.2 and bx[0] < 1.2
                 and (bx[3] - bx[2]) < 3.0 and (bx[1] - bx[0]) < 3.0]
        if not seeds:
            continue
        cluster = set(seeds)
        grew = True
        while grew:                                   # pull in every piece whose box touches the cluster (0.04 m tolerance)
            grew = False
            lo = [min(boxes[i][k] for i in cluster) - .04 for k in (0, 2, 4)]
            hi = [max(boxes[i][k] for i in cluster) + .04 for k in (1, 3, 5)]
            for i, bx in enumerate(boxes):
                if i in cluster or (bx[3] - bx[2]) > 3.0 or (bx[1] - bx[0]) > 3.0:
                    continue
                if bx[0] <= hi[0] and bx[1] >= lo[0] and bx[2] <= hi[1] and bx[3] >= lo[1] and bx[4] <= hi[2] and bx[5] >= lo[2]:
                    cluster.add(i); grew = True
        cl = [f for i in cluster for f in comps[i]]
        cbox = [min(boxes[i][0] for i in cluster), max(boxes[i][1] for i in cluster), min(boxes[i][2] for i in cluster),
                max(boxes[i][3] for i in cluster), min(boxes[i][4] for i in cluster), max(boxes[i][5] for i in cluster)]
        centre = (cbox[0] + cbox[1]) / 2
        sign = -1 if centre < 0 else 1
        base_shift = (-1.25 - cbox[1]) if sign < 0 else (1.25 - cbox[0])
        cl_ids = {f.index for f in cl}
        rest = [f for f in bm.faces if f.index not in cl_ids]

        def tree(faces, dx=0.0):
            vl, vi, polys = [], {}, []
            for f in faces:
                for v in f.verts:
                    if v.index not in vi:
                        vi[v.index] = len(vl)
                        vl.append(v.co.copy() + type(v.co)((dx, 0, 0)))
                polys.append(tuple(vi[v.index] for v in f.verts))
            return BVHTree.FromPolygons(vl, polys)

        rest_tree = tree(rest)
        chosen = None
        for extra in [0.0] + [sign * .1 * k for k in range(1, 11)]:
            if not tree(cl, base_shift + extra).overlap(rest_tree):
                chosen = base_shift + extra
                break
        if chosen is None:
            bmesh.ops.delete(bm, geom=cl, context='FACES')
            actions.append({'door': door, 'pieces': len(cluster), 'faces': len(cl), 'box': [round(v, 2) for v in cbox], 'action': 'deleted (no sideways shift up to 1 m cleared the room)'})
        else:
            for v in {v for f in cl for v in f.verts}:
                v.co.x += chosen
            actions.append({'door': door, 'pieces': len(cluster), 'faces': len(cl), 'box_before': [round(v, 2) for v in cbox], 'shift_x': round(chosen, 3), 'action': 'moved clear of the doorway'})
    if actions:
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
        bm.transform(obj.matrix_world.inverted())
        bm.to_mesh(obj.data)
        obj.data.update()
    bm.free()
    receipt['doorway_clearance'] = actions


def main():
    old_path, out_path, receipt_path = opts()
    receipt = {'envelope_y': [YS, YN], 'trim': {}, 'markers': {}}
    scene = bpy.context.scene
    src = bpy.data.collections['TURBINE_ROOM_V2']

    # 1. trim
    for name in TRIM_OBJECTS:
        o = bpy.data.objects.get(name)
        if o and o.type == 'MESH':
            receipt['trim'][name] = trim(o)

    receipt['clamped_vertices'] = {n: clamp(bpy.data.objects[n]) for n in ('TURBINE_ARCH', 'TURBINE_MACH', 'TURBINE_DECAL', 'OCCLUDER_ONLY') if n in bpy.data.objects}
    clear_doorways(bpy.data.objects['TURBINE_MACH'], receipt)

    # 2. markers from the old module
    with bpy.data.libraries.load(old_path, link=False) as (data_from, data_to):
        wanted = [n for n in data_from.objects if n.startswith(KEEP_PREFIXES)]
        dropped = [n for n in data_from.objects if n.startswith('SUPPORT_')]
        carried_names = sorted(wanted)
        data_to.objects = wanted   # Blender swaps this list's names for Objects in place
    receipt['markers']['carried'] = carried_names
    receipt['markers']['support_markers_dropped'] = len(dropped)
    marks = bpy.data.collections.new('Interface and interaction markers')
    before = {}
    for o in data_to.objects:
        if o is None:
            continue
        o.parent = None
        marks.objects.link(o)
        before[o.name] = [round(v, 4) for v in o.location]   # old markers have no parent and no rotation, so local == world
    for name, (pos, why) in RESEAT.items():
        o = bpy.data.objects[name]
        o.location = Vector(pos)
        receipt['markers'].setdefault('reseated', {})[name] = {'from': before[name], 'to': list(pos), 'onto': why}
    receipt['markers']['interface_unchanged'] = {n: before[n] for n in before if n.startswith('IF_')}
    receipt['markers']['kept_in_place_semantics_unverified'] = sorted(n for n in before if n not in RESEAT and not n.startswith('IF_'))

    # 3. structure
    mod = bpy.data.collections.new('MODULE_turbine-room')
    for k, v in {'section_id': 'turbine-room', 'source_revision': 'v2-promoted', 'promotion': 'turbine rebuild promoted to module.blend; see promotion_receipt.json'}.items():
        mod[k] = v
    scene.collection.children.link(mod)
    scene.collection.children.unlink(src)
    mod.children.link(src)
    mod.children.link(marks)

    # 4. textures stay beside the rebuild
    fixed = []
    for img in bpy.data.images:
        if img.source == 'FILE' and not img.packed_file and img.filepath:
            name = bpy.path.basename(bpy.path.abspath(img.filepath)) if not img.filepath.startswith('//rebuild/') else img.filepath[len('//rebuild/'):]
            img.filepath = '//rebuild/' + name
            fixed.append(name)
    receipt['textures_repointed'] = len(fixed)

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=out_path, relative_remap=False)
    if receipt_path:
        json.dump(receipt, open(receipt_path, 'w'), indent=2)
    print('PROMOTE:', json.dumps({k: (v if k != 'markers' else {a: (len(b) if hasattr(b, '__len__') else b) for a, b in v.items()}) for k, v in receipt.items()})[:600])


if __name__ == '__main__':
    main()
