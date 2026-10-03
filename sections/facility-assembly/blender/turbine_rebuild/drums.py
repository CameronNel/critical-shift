"""Two 200 L steel drums, built as proper lathe-turned objects with their own painted + worn texture maps (drumtex.py).
Profile: rolled bottom chime, pressed rolling hoops, rolled top chime, recessed head with a reinforcing bead and two
bungs (2 in and 3/4 in) with flanges. Objects: PROP_DRUM_n (body + head + bungs)."""
import os, math, subprocess, bmesh, bpy
from mathutils import Vector

R0 = .285
BODY = [(0, .035), (.2, .035), (.245, .028), (.262, .0), (.28, .0), (.292, .01), (.295, .03), (.289, .048), (R0, .058),
        (R0, .19), (.289, .202), (.297, .216), (.289, .23), (R0, .242),
        (R0, .59), (.289, .604), (.297, .62), (.289, .636), (R0, .65),
        (R0, .80), (.289, .815), (.296, .83), (.296, .845), (.29, .858), (.275, .866), (.262, .868), (.252, .862), (.248, .85),
        (.236, .848), (.2, .848), (.19, .851), (.18, .858), (.17, .851), (.1, .848), (0, .848)]
HEAD_FROM = 26    # profile index where the head starts (planar steel UVs from here)
SEG = 40

def make_materials(out):
    subprocess.run(['python3', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drumtex.py'), out], check=True)
    mats = []
    for k in ('a', 'b'):
        m = bpy.data.materials.new('M_drum_' + k); m.use_nodes = True; nt = m.node_tree; pb = nt.nodes['Principled BSDF']
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'
        al = bpy.data.images.load(os.path.join(out, f'drum_{k}_albedo.png')); al.colorspace_settings.name = 'sRGB'
        orm = bpy.data.images.load(os.path.join(out, f'drum_{k}_orm.png')); orm.colorspace_settings.name = 'Non-Color'
        ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = al; ta.name = 'ALBEDO'; to = nt.nodes.new('ShaderNodeTexImage'); to.image = orm; to.name = 'ORM'
        for t in (ta, to): nt.links.new(uvn.outputs[0], t.inputs[0])
        sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(to.outputs[0], sp.inputs[0])
        nt.links.new(ta.outputs['Color'], pb.inputs['Base Color']); nt.links.new(sp.outputs['Green'], pb.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], pb.inputs['Metallic'])
        mats.append(m)
    return mats

def _lathe(cx, cy, cz, prof, seg, uvf, verts, faces, uvs, rot=0.0):
    """append a revolved profile; uvf(i_frac, k, x, y, z, r) -> (u, v)"""
    n = len(prof); base = len(verts)
    for k, (r, z) in enumerate(prof):
        for i in range(seg):
            a = 2 * math.pi * i / seg + math.pi / seg + rot; verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz + z))
    for k in range(n - 1):
        (r0, _), (r1, _) = prof[k], prof[k + 1]
        if r0 < 1e-6 and r1 < 1e-6: continue
        for i in range(seg):
            j = (i + 1) % seg; ia, ja = base + k * seg + i, base + k * seg + j; ib, jb = base + (k + 1) * seg + i, base + (k + 1) * seg + j
            quad = [ia, ja, jb, ib]
            if r0 < 1e-6: quad = [ia, jb, ib]            # fan at the bottom pole: collapse
            elif r1 < 1e-6: quad = [ia, ja, jb]
            # unique vertices per ring point are shared; collapse degenerate (pole) rings
            faces.append(tuple(dict.fromkeys(quad)))
            lp = []
            for vi in faces[-1]:
                kk, ii = (vi - base) // seg, (vi - base) % seg
                iu = ii + (seg if (ii == 0 and i == seg - 1 and vi in (ja, jb)) else 0)
                x, y, z = verts[vi]; lp.append(uvf((iu) / seg, kk, x - cx, y - cy, z - cz, prof[kk][0]))
            uvs.append(lp)

def build(coll, out, drums):
    mats = make_materials(out); objs = []
    for di, (cx, cy, rot, z0) in enumerate(drums):
        verts, faces, uvs = [], [], []
        def uv_body(u, k, x, y, z, r, rot=rot):
            if k >= HEAD_FROM or k < 4:                                      # head and underside: bare steel, planar
                return (.03 + (x + .3) * .72, .03 + (y + .3) * .72 * .98 * .5 / .5 * .9) if False else (.03 + (x + .3) * .72 * .8, .03 + (y + .3) * .72 * .8)
            return ((u + .75 - (rot / (2 * math.pi)) - .0) % 1.0 if False else u, .5 + .5 * z / .87)
        # u offset so that the label (u=.75) faces -Y for rot=0 drums: angle of -Y is 270deg = u .75 already
        def uvf(u, k, x, y, z, r): return uv_body(u + (rot / (2 * math.pi)) * -1, k, x, y, z, r)
        _lathe(cx, cy, z0, BODY, SEG, uvf, verts, faces, uvs, rot)
        # bungs on the head
        BUNG = [(0, 0), (.046, 0), (.046, .008), (.037, .012), (.037, .022), (.031, .026), (.0, .026)]
        for (bx, by, s) in ((.125, .085, 1.0), (-.12, -.09, .62)):
            ca, sa = math.cos(rot), math.sin(rot); wx, wy = cx + bx * ca - by * sa, cy + bx * sa + by * ca
            _lathe(wx, wy, z0 + .848, [(r * s, z * s) for r, z in BUNG], 14, lambda u, k, x, y, z, r, bx=bx, by=by: (.03 + (x + bx + .3) * .72 * .8, .03 + (y + by + .3) * .72 * .8), verts, faces, uvs)
        me = bpy.data.meshes.new(f'PROP_DRUM_{di}'); me.from_pydata(verts, [], faces); me.update()
        uv = me.uv_layers.new(name='UVMap'); k = 0
        for fi, f in enumerate(faces):
            for j in range(len(f)): uv.data[k].uv = uvs[fi][j]; k += 1
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces: f.smooth = True
        for e in bm.edges:
            if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(55): e.smooth = False
        bm.to_mesh(me); bm.free()
        me.materials.append(mats[di % 2]); ob = bpy.data.objects.new(f'PROP_DRUM_{di}', me); coll.objects.link(ob); objs.append(ob)
    return objs
