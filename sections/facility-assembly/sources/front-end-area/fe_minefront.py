"""Mine entrance: the front panel only of the existing R39 portal shed (reference mine), cut out, rotated to face the yard."""
import bpy, bmesh, os
from mathutils import Vector, Matrix
from fe_common import *

NAMES = ['R39 | Shed boards', 'R39 | Shed frame', 'R39 | Shed tin patches', 'R39 | Shed ironwork', 'R39 | Shed signs', 'R39 | Shed footings']

def build_mine_front(F, C, src, x_cut=-23.7, log=print):
    yard = C['YARD']
    with bpy.data.libraries.load(src, link=False) as (df, dt):
        dt.objects = [n for n in NAMES if n in df.objects]
    parts = []
    for o in dt.objects:
        if o is None: continue
        me = o.data.copy(); me.transform(o.matrix_world)
        bm = bmesh.new(); bm.from_mesh(me)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(x_cut, 0, 0), plane_no=(1, 0, 0), clear_inner=True)
        bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary]) if False else None
        if len(bm.faces) == 0: bm.free(); continue
        parts.append((o.name, o.data.materials[:], bm))
        bpy.data.objects.remove(o, do_unlink=True)
    if not parts: raise RuntimeError('no mine front parts found')
    # bounds of the cut front panel in source coordinates
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for _, _, bm in parts:
        for v in bm.verts:
            for i in range(3): mn[i] = min(mn[i], v.co[i]); mx[i] = max(mx[i], v.co[i])
    log('FRONT BOUNDS', [round(x, 2) for x in mn], [round(x, 2) for x in mx])
    cy = (mn.y + mx.y) / 2
    # the portal (rail exit) faces +X in the source: keep the east slab, put its outer plane at plan x=-48.0 centred on plan y=-70, base on z=0
    tri = 0; out = []
    for name, mats, bm in parts:
        for v in bm.verts:
            v.co = Vector((LX(-48.0) + (v.co.x - mx.x), LY(-70.0) + (v.co.y - cy), v.co.z - mn.z))
        me = bpy.data.meshes.new('mine_front_' + name.split('| ')[-1].replace(' ', '_')); bm.to_mesh(me); bm.free()
        for m in mats: me.materials.append(m)
        o = bpy.data.objects.new(me.name, me); yard.objects.link(o); out.append(o)
        tri += sum(len(p.vertices) - 2 for p in me.polygons)
    log('FRONT TRIANGLES', tri, [o.name for o in out])
    return out
