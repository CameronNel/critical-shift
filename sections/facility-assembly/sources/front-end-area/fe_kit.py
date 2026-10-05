"""Quality geometry kit: rounded boxes, lathes, sweeps, subdivided cushions, leaves, merged into multi-material meshes (MB2)."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler
from fe_common import *
from fe_props import MB, bm_box, bm_cyl, bm_cyl_h, bm_blob, bm_torus

def _to_mesh(pb, name='tmp'):
    me = bpy.data.meshes.new(name); pb.to_mesh(me); return me

def subsurf(pb, levels=1):
    """Catmull-Clark through a temporary object so creases/bevels survive; returns a new bmesh."""
    me = _to_mesh(pb); pb.free()
    ob = bpy.data.objects.new('tmp_ss', me); bpy.context.scene.collection.objects.link(ob)
    md = ob.modifiers.new('ss', 'SUBSURF'); md.levels = levels; md.render_levels = levels; md.subdivision_type = 'CATMULL_CLARK'
    bpy.context.view_layer.update()
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me2 = bpy.data.meshes.new_from_object(ev)
    nb = bmesh.new(); nb.from_mesh(me2)
    bpy.data.objects.remove(ob, do_unlink=True); bpy.data.meshes.remove(me); bpy.data.meshes.remove(me2)
    return nb

def xf(pb, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    M = Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal(Vector((*scale, 1)))
    bmesh.ops.transform(pb, matrix=M, verts=pb.verts[:]); return pb

def p_rbox(sx, sy, sz, r=0.02, seg=3):
    pb = bmesh.new(); bmesh.ops.create_cube(pb, size=1.0)
    for v in pb.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    r = min(r, 0.49 * min(sx, sy, sz))
    if r < 0.012: seg = 1
    if r > 0: bmesh.ops.bevel(pb, geom=pb.edges[:], offset=r, segments=seg, affect='EDGES', profile=0.5)
    for f in pb.faces: f.smooth = True
    return pb

def p_cyl(r, h, seg=24, r2=None, bevel=0.0, caps=True):
    pb = bmesh.new(); bmesh.ops.create_cone(pb, cap_ends=caps, cap_tris=False, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    if bevel > 0: bmesh.ops.bevel(pb, geom=pb.edges[:], offset=min(bevel, 0.4 * min(r, h)), segments=2, affect='EDGES')
    for f in pb.faces: f.smooth = True
    return pb

def p_between(a, b, r, seg=14, r2=None, caps=True):
    """Cylinder from point a to point b."""
    a = Vector(a); b = Vector(b); d = b - a; L = d.length
    pb = p_cyl(r, L, seg, r2, 0.0, caps)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(pb, matrix=Matrix.Translation((a + b) / 2) @ q, verts=pb.verts[:]); return pb

def p_sphere(rx, ry=None, rz=None, rings=10, seg=16):
    pb = bmesh.new(); bmesh.ops.create_uvsphere(pb, u_segments=seg, v_segments=rings, radius=1.0)
    for v in pb.verts: v.co = Vector((v.co.x * rx, v.co.y * (ry or rx), v.co.z * (rz or rx)))
    for f in pb.faces: f.smooth = True
    return pb

def p_lathe(profile, seg=32, close=False):
    """Revolve [(radius, z), ...] about Z."""
    pb = bmesh.new(); rings = []
    for (r, z) in profile:
        ring = [pb.verts.new(Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z))) for i in range(seg)]
        rings.append(ring)
    for k in range(len(rings) - 1):
        for i in range(seg):
            try: pb.faces.new((rings[k][i], rings[k][(i + 1) % seg], rings[k + 1][(i + 1) % seg], rings[k + 1][i]))
            except ValueError: pass
    if close:
        for ring in (rings[0], rings[-1]):
            try: pb.faces.new(ring[::-1] if ring is rings[0] else ring)
            except ValueError: pass
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    for f in pb.faces: f.smooth = True
    return pb

def p_torus(R, r, ns=32, nt=12):
    pb = bmesh.new(); bm_torus(pb, 0, 0, 0, R, r, ns=ns, nt=nt, tilt=False)
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    for f in pb.faces: f.smooth = True
    return pb

def p_cushion(sx, sy, sz, r=None, levels=1):
    pb = p_rbox(sx, sy, sz, r or 0.28 * min(sx, sy, sz), seg=2)
    return subsurf(pb, levels)

def p_leaf(L, W, bend=0.5, twist=0.0, segs=7, droop=0.0):
    """Blade leaf along +Y with a midrib fold; 2*segs*2 tris. Origin at the base."""
    pb = bmesh.new(); rows = []
    for i in range(segs + 1):
        t = i / segs; y = L * t
        z = (bend * L * t * t) - droop * L * t ** 3
        w = W * math.sin(math.pi * min(t * 0.92 + 0.04, 1.0)) ** 0.7 * (1 - 0.25 * t)
        ang = twist * t
        fold = 0.12 * w
        l = pb.verts.new(Vector((-w * math.cos(ang), y, z + fold + w * math.sin(ang))))
        c = pb.verts.new(Vector((0, y, z - fold * 0.3)))
        rr = pb.verts.new(Vector((w * math.cos(ang), y, z + fold - w * math.sin(ang))))
        rows.append((l, c, rr))
    for i in range(segs):
        a, b = rows[i], rows[i + 1]
        for (p, q) in ((0, 1), (1, 2)):
            try: pb.faces.new((a[p], a[q], b[q], b[p]))
            except ValueError: pass
    for f in pb.faces: f.smooth = True
    return pb

def p_ring_prism(pts, h, bevel=0.0):
    """Extrude a 2D polygon (list of (x,y)) by h along z."""
    pb = bmesh.new(); vs = [pb.verts.new(Vector((x, y, 0))) for x, y in pts]
    f = pb.faces.new(vs); r = bmesh.ops.extrude_face_region(pb, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z += h
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    if bevel > 0: bmesh.ops.bevel(pb, geom=pb.edges[:], offset=bevel, segments=2, affect='EDGES')
    return pb

class MB2(MB):
    """MB with part-based adds: m.add(part_bmesh, loc, rot, scale, mi, rgba)."""
    def add(self, pb, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mi=None, rgba=None, free=True):
        if mi is not None: self.mi = mi
        if rgba is not None: self.rgba = rgba
        xf(pb, loc, rot, scale)
        me = _to_mesh(pb)
        if free: pb.free()
        before = set(self.bm.faces); self.bm.from_mesh(me); self._tag(before)
        bpy.data.meshes.remove(me); return self
    def quad_image(self, cx, cy, cz, w, h, mi, flip=False):
        """Upright quad in the XZ plane facing +Y with 0..1 UVs (posters, TV slide)."""
        uvl = self.bm.loops.layers.uv.verify()
        vs = [self.bm.verts.new(Vector((cx + sx * w / 2, cy, cz + sz * h / 2))) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        f = self.bm.faces.new(vs); f.material_index = mi
        for l, (u, v) in zip(f.loops, ((1, 0), (0, 0), (0, 1), (1, 1))): l[uvl].uv = (u, v)   # viewer at +y sees +x on the left
        for l in f.loops: l[self.layer] = (1, 1, 1, 1)
        f.normal_update()
        if f.normal.y < 0: f.normal_flip()
        return self
    def rbox(self, cx, cy, cz, sx, sy, sz, r=0.02, rot=(0, 0, 0), seg=3, mi=None, rgba=None):
        return self.add(p_rbox(sx, sy, sz, r, seg), (cx, cy, cz), rot, (1, 1, 1), mi, rgba)
    def cylz(self, cx, cy, z0, z1, r, seg=24, r2=None, bevel=0.0, mi=None, rgba=None, caps=True):
        return self.add(p_cyl(r, z1 - z0, seg, r2, bevel, caps), (cx, cy, (z0 + z1) / 2), (0, 0, 0), (1, 1, 1), mi, rgba)
    def between(self, a, b, r, seg=14, r2=None, mi=None, rgba=None, caps=True):
        return self.add(p_between(a, b, r, seg, r2, caps), (0, 0, 0), (0, 0, 0), (1, 1, 1), mi, rgba)
    def lathe(self, profile, loc=(0, 0, 0), seg=32, mi=None, rgba=None, close=False, rot=(0, 0, 0), scale=(1, 1, 1)):
        return self.add(p_lathe(profile, seg, close), loc, rot, scale, mi, rgba)
    def sphere(self, cx, cy, cz, rx, ry=None, rz=None, rings=10, seg=16, mi=None, rgba=None, rot=(0, 0, 0)):
        return self.add(p_sphere(rx, ry, rz, rings, seg), (cx, cy, cz), rot, (1, 1, 1), mi, rgba)
    def cushion(self, cx, cy, cz, sx, sy, sz, r=None, levels=1, rot=(0, 0, 0), mi=None, rgba=None):
        return self.add(p_cushion(sx, sy, sz, r, levels), (cx, cy, cz), rot, (1, 1, 1), mi, rgba)
    def leaf(self, loc, L, W, bend=0.5, twist=0.0, segs=7, droop=0.0, yaw=0.0, pitch=0.0, mi=None, rgba=None):
        return self.add(p_leaf(L, W, bend, twist, segs, droop), loc, (pitch, 0, yaw), (1, 1, 1), mi, rgba)
    def torus(self, cx, cy, cz, R, r, ns=32, nt=12, rot=(0, 0, 0), mi=None, rgba=None):
        return self.add(p_torus(R, r, ns, nt), (cx, cy, cz), rot, (1, 1, 1), mi, rgba)
    def finish(self, name, coll, smooth=False):
        me = bpy.data.meshes.new(name); self.bm.to_mesh(me); self.bm.free()
        for mm in self.mats: me.materials.append(mm)
        if smooth:
            for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new(name, me); coll.objects.link(o); return o
