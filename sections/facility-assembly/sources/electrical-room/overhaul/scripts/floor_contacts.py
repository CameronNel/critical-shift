"""Seat localized coating loss on the actual floor finish it belongs to."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def correct(k):
    root=bpy.data.objects[k.PREFIX+'Localized service plinth contacts']
    assert root['cs_support_target']=='Floor'
    contacts=sorted((o for o in bpy.context.scene.objects
                     if o.name.startswith(k.PREFIX+'Individual service floor contact ')),key=lambda o:o.name)
    assert len(contacts)==6
    def bounds(o):
        pts=[o.matrix_world@Vector(p) for p in o.bound_box]
        return [tuple(fn(p[i] for p in pts) for i in range(3)) for fn in (min,max)]
    panels=[(o,*bounds(o)) for o in bpy.context.scene.objects
            if o.name.startswith(k.PREFIX+'Service zone epoxy panel')]
    anchors=list(root['cs_support_anchors']);assert len(anchors)==6
    k.collection('Service edge finish history')
    moved=[];floor_anchors=[];probes=[];trees={}
    exposed_x=[-2.22,-2.28,-2.20,-2.31]
    def first_surface(x,y):
        hits=[]
        for o in bpy.context.scene.objects:
            if o.type!='MESH' or o.hide_render or o in contacts:continue
            lo,hi=bounds(o)
            if not (lo[0]-.001<=x<=hi[0]+.001 and lo[1]-.001<=y<=hi[1]+.001 and lo[2]<.1):continue
            if o.name not in trees:
                trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],
                                                  [list(p.vertices) for p in o.data.polygons])
            hit,normal,index,distance=trees[o.name].ray_cast(Vector((x,y,.1)),Vector((0,0,-1)),.11)
            if hit is not None:hits.append((distance,o.name,hit.z))
        assert hits
        return min(hits)
    for i,(contact,anchor) in enumerate(zip(contacts,anchors)):
        x,y,z=anchor
        original_x=x
        if i<4:x=exposed_x[i]
        matches=[(o,hi[2]) for o,lo,hi in panels if lo[0]<x<hi[0] and lo[1]<y<hi[1]]
        if not matches:
            floor_anchors.append(list(anchor));continue
        assert len(matches)==1
        target,height=matches[0]
        assert abs(height-.0013)<1e-6
        # Each mark retains its original closed contour/thickness and sits
        # 0.12mm above the finished epoxy rather than below that layer.
        delta=contact.matrix_world.inverted().to_3x3()@Vector((x-original_x,0,height))
        for v in contact.data.vertices:v.co+=delta
        contact.data.update()
        support=k.root('Epoxy service contact '+str(i+1),target.name,[[x,y,height]])
        contact['cs_assembly']=support.name
        moved.append({'object':contact.name,'vertical_shift_m':height,
                      'horizontal_shift_m':x-original_x,
                      'support_target':target.name,'support_anchor':[x,y,height]})
        points={(round((contact.matrix_world@v.co).x,7),round((contact.matrix_world@v.co).y,7))
                for v in contact.data.vertices}
        points.add((x,y))
        for px,py in sorted(points):
            distance,name,surface_z=first_surface(px,py)
            assert name==target.name,(contact.name,px,py,name)
            assert abs(surface_z-height)<1e-6
            probes.append({'contact':contact.name,'xy':[px,py],'first_surface':name,'surface_z':surface_z})
    assert len(moved)==4 and len(floor_anchors)==2
    root['cs_support_anchors']=floor_anchors
    bpy.context.scene['electrical_floor_contact_revision']='R7'
    return {'moved_contacts':moved,'remaining_original_floor_contacts':2,
            'exposed_surface_probes':probes,'all_contours_clear_of_insulating_mats':True,
            'new_registered_support_roots':4,'existing_floor_root_restricted_to_its_two_contacts':True}
