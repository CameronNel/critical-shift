"""One wall skin per wall: a single slab with the real openings cut through it and one planar UV (u along the wall, v = z / 7.2 m)."""
import bpy, bmesh
H = 7.2

def make_wall(coll, name, frame, u0, u1, holes, mats):
    """Built in the wall's local frame (x along the wall, y into the room, z up), then placed with the frame transform."""
    (ox, oy), rz = frame
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(u1 - u0, .05, H), verts=bm.verts); bmesh.ops.translate(bm, vec=((u0 + u1) / 2, .025, H / 2), verts=bm.verts)
    me = bpy.data.meshes.new('WALL_' + name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('TURBINE_WALL_' + name, me); coll.objects.link(ob); ob.location = (0, 0, 0)
    cutters = []
    for (a, b, z0, z1) in holes:
        cb = bmesh.new(); bmesh.ops.create_cube(cb, size=1.0); bmesh.ops.scale(cb, vec=(b - a, .6, z1 - z0), verts=cb.verts); bmesh.ops.translate(cb, vec=((a + b) / 2, .02, (z0 + z1) / 2), verts=cb.verts)
        cm = bpy.data.meshes.new('cut'); cb.to_mesh(cm); cb.free(); co = bpy.data.objects.new('cut', cm); coll.objects.link(co); cutters.append(co)
    bpy.context.view_layer.objects.active = ob
    for i, c in enumerate(cutters):
        md = ob.modifiers.new(f'cut{i}', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = c
        bpy.ops.object.modifier_apply(modifier=md.name); bpy.data.objects.remove(c, do_unlink=True)
    me = ob.data; bm = bmesh.new(); bm.from_mesh(me); uv = bm.loops.layers.uv.new('UVMap'); n_top = 0
    for f in bm.faces:
        top = f.normal.y > .9 and f.calc_center_median().y > .04
        f.material_index = 0 if top else 1; f.smooth = False; n_top += top
        for l in f.loops:
            co = l.vert.co; l[uv].uv = ((co.x - u0) / (u1 - u0), co.z / H) if top else (.001, .001)
    bm.to_mesh(me); bm.free(); me.materials.clear()
    for m in mats: me.materials.append(m)
    ob.location = (ox, oy, 0); ob.rotation_euler = (0, 0, rz)
    return ob, dict(faces=len(me.polygons), top_faces=n_top, tris=sum(len(p.vertices) - 2 for p in me.polygons))
