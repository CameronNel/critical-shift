"""Distinct contact histories for the four parked leaves; no interface edits."""
import json
import bmesh
from mathutils import Vector


def apply(k, m):
    import bpy
    old = sorted(
        o.name for o in bpy.data.objects
        if o.get('assembly_member') in {'D01_Turbine', 'D02_Waste'}
        and o.name.startswith(('Localized chipped paint', 'Wear at repeatedly handled edge'))
    )
    assert len(old) == 104, 'Expected the exact inherited door-only decorative wear set'
    for name in old:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    bpy.context.scene['electrical_door_history_revision'] = 'R6'
    bpy.context.scene['electrical_retired_door_wear'] = json.dumps(old)
    k.collection('Individual door contact history')

    def bounds(o):
        vs = [o.matrix_world @ Vector(v) for v in o.bound_box]
        return [Vector(tuple(fn(p[i] for p in vs) for i in range(3))) for fn in (min, max)]

    def scar(name, x, y, z, width, height, sign, mat, skew, depth=.00035):
        # Closed irregular paint-loss boundary, with a separate exposed-metal core.
        # Contours vary in aspect, skew and location; they are not repeated decals.
        points = [(-.50, -.14), (-.31, -.48), (.19, -.37), (.50, -.08),
                  (.29, .26), (.04, .49), (-.26, .32), (-.44, .10)]
        def draw(b):
            rows = []
            for yy in (y, y + sign * depth):
                rows.append([b.bm.verts.new((x + width*(u+skew*v), yy, z+height*v)) for u, v in points])
            for row in rows:
                f = b.bm.faces.new(row); f.material_index = b._idx(mat)
            for i in range(len(points)):
                j = (i+1) % len(points)
                f = b.bm.faces.new((rows[0][i], rows[0][j], rows[1][j], rows[1][i]))
                f.material_index = b._idx(mat)
            bmesh.ops.recalc_face_normals(b.bm, faces=list(b.bm.faces))
        return k.add(name, draw)

    # Each plan encodes its own maintenance/contact history, rather than seeding
    # a mirrored scatter. Tuples are offsets from the measured handle or shoe.
    plans = [
        # Turbine positive-X leaf: frequently pulled; a few low shoe strikes.
        ([(.045, 1.18, .046, .009, .20), (-.030, 1.10, .025, .006, -.40),
          (.036, 1.03, .037, .007, .55), (.012, .96, .014, .004, -.20),
          (-.012, 1.25, .028, .005, .30)],
         [(-.26, .19, .082, .010, .40), (.09, .23, .032, .008, -.25), (.32, .17, .045, .006, .10)]),
        # Turbine negative-X leaf: quieter handle, one oblique boot-edge cluster.
        ([(.022, 1.22, .017, .005, -.50), (-.031, 1.00, .039, .008, .15)],
         [(-.35, .31, .034, .013, -.65), (-.28, .29, .059, .008, -.60),
          (-.17, .28, .029, .006, -.45), (.16, .18, .024, .004, .20)]),
        # Waste negative-X leaf: cart rubbing at a higher, one-sided shoe zone.
        ([(-.048, 1.15, .028, .006, .60), (-.014, 1.08, .013, .004, -.10),
          (.033, .99, .020, .005, -.35)],
         [(-.34, .38, .089, .010, .12), (-.19, .37, .065, .007, -.20),
          (-.05, .36, .030, .005, .30), (.08, .35, .044, .009, -.40),
          (.34, .23, .019, .005, .45)]),
        # Waste positive-X leaf: less-used/recently maintained; restrained marks.
        ([(.038, 1.04, .023, .005, -.25), (-.027, 1.24, .011, .004, .50)],
         [(.28, .28, .033, .006, -.30)]),
    ]
    leaves = sorted((o for o in bpy.data.objects if o.name.startswith('Parked sliding leaf')), key=lambda o:o.name)
    shoes = sorted((o for o in bpy.data.objects if o.name.startswith('Door impact shoe')), key=lambda o:o.name)
    assert len(leaves) == len(shoes) == len(plans) == 4
    for i, (leaf, shoe, (handle_marks, shoe_marks)) in enumerate(zip(leaves, shoes, plans)):
        lo, hi = bounds(leaf); cx = (lo.x + hi.x)/2
        sign = 1 if (lo.y+hi.y)/2 < 1 else -1
        face = hi.y if sign > 0 else lo.y
        handle_x = 1.48 if cx > 0 else -1.48
        dx, z, w, h, skew = handle_marks[0]
        k.root('Leaf '+str(i+1)+' handle contact', leaf.name, [[handle_x+dx, face, z]],
               'WORLD_-Y' if sign > 0 else 'WORLD_+Y')
        for j, (dx, z, w, h, skew) in enumerate(handle_marks):
            y = face + sign*.00012
            scar('Leaf '+str(i+1)+' irregular handle loss '+str(j), handle_x+dx, y, z, w, h, sign, m['oxide'], skew)
            if (i+j) % 2 == 0:
                scar('Leaf '+str(i+1)+' rubbed metal core '+str(j), handle_x+dx, y+sign*.00035,
                     z, w*.54, h*.38, sign, m['steel'], -skew*.3, .00012)
        slo, shi = bounds(shoe); scx = (slo.x+shi.x)/2
        face = shi.y if sign > 0 else slo.y
        dx, z, w, h, skew = shoe_marks[0]
        k.root('Leaf '+str(i+1)+' shoe contact', shoe.name, [[scx+dx, face, z]],
               'WORLD_-Y' if sign > 0 else 'WORLD_+Y')
        for j, (dx, z, w, h, skew) in enumerate(shoe_marks):
            scar('Leaf '+str(i+1)+' individual shoe strike '+str(j), scx+dx, face+sign*.00012,
                 z, w, h, sign, m['zinc'] if (i+j) % 3 == 0 else m['oxide'], skew)
