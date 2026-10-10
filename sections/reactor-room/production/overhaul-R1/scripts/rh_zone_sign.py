"""Relocate the retained ZONE C plaque as one mounted assembly, clear of services."""
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import rh_roof_utilities as R
import rh_support_registry as S
OWNER='zone C sightline correction'

def zone(K,M,tag,n,t,camera):
    owner='zone '+tag+' sightline correction'
    def world(x,y,z):return -n*x+t*y+Vector((0,0,z))
    sc=bpy.context.scene
    records=json.loads(sc['rh_wall_text_records'])
    record=next(r for r in records if r['body']=='ZONE '+tag)
    points=[Vector(p) for p in record['samples']]
    cy=sum(p.dot(t) for p in points)/len(points);cz=sum(p.z for p in points)/len(points)
    selected={}
    for name in ('RH walls assets AUDI','RH walls assets ORANGE','RH walls text AMBER'):
        o=bpy.data.objects[name];ids=set()
        for group in R.components(o.data):
            q=[o.matrix_world@o.data.vertices[i].co for i in group];q=[Vector((-v.dot(n),v.dot(t),v.z)) for v in q]
            lo=[min(v[k] for v in q) for k in range(3)];hi=[max(v[k] for v in q) for k in range(3)]
            if lo[0]>10.75 and hi[0]<10.801 and abs((lo[1]+hi[1])/2-cy)<.65 and abs((lo[2]+hi[2])/2-cz)<.16:
                ids.update(group)
        assert ids,('Missing retained zone component',name)
        selected[name]=ids
    assert len(selected['RH walls assets AUDI'])==24
    assert len(selected['RH walls assets ORANGE'])==8
    dg=bpy.context.evaluated_depsgraph_get()
    def transparent(o):
        if not o.data.materials:return False
        for m in o.data.materials:
            if not m or not m.use_nodes:return False
            out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
            if out and not out.inputs['Surface'].is_linked:continue
            b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if b and (b.inputs['Alpha'].default_value<.3 or b.inputs['Transmission Weight'].default_value>.95):continue
            if any(n.type in ('BSDF_TRANSPARENT','BSDF_GLASS','BSDF_REFRACTION') for n in m.node_tree.nodes):continue
            return False
        return True
    def clear(start,end):
        direction=(end-start).normalized();origin=start.copy();remaining=(end-start).length-.003
        for _ in range(48):
            hit,loc,normal,index,o,matrix=sc.ray_cast(dg,origin,direction,distance=remaining)
            if not hit:return True
            ignored=transparent(o) or (o.name in selected and set(o.data.polygons[index].vertices)<=selected[o.name])
            if not ignored:
                blocked[o.name]=blocked.get(o.name,0)+1
                return False
            remaining-=(loc-origin).length+.0001;origin=loc+direction*.0001
            if remaining<=0:return True
        return False
    blocked={}
    panel=[world(10.764,-2.59+i*.98/12,2.61+j*.24/4) for i in range(13) for j in range(5)]
    normal=n
    offsets=sorted([n*.04+t*dy+Vector((0,0,dz)) for dy in (0,.25,-.25,.5,-.5,.75,-.75,1,-1) for dz in (0,.25,.5,.75,1,1.25)],key=lambda v:v.length)
    offset=next((v for v in offsets if all(clear(camera,p+v) and clear(p+v+normal*1.2,p+v) for p in points+panel)),None)
    print('ZONE_C_BLOCKERS',blocked,flush=True)
    assert offset is not None,'No clear, nearby ZONE C plaque placement'
    # Move all merged backing, trim and glyph components together. No duplicate remains.
    for name,ids in selected.items():
        o=bpy.data.objects[name];local=o.matrix_world.to_3x3().inverted()@offset
        for i in ids:o.data.vertices[i].co+=local
        o.data.update()
    record['samples']=[list(p+offset) for p in points]
    sc['rh_wall_text_records']=json.dumps(records)
    S.reset(owner)
    receivers=[(o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('RH walls mass ','RH walls concrete ','RH walls cladding ','RH walls steel '))]
    for yy in (-2.4,-1.8):
        for zz in (2.65,2.80):
            p=world(10.8,yy,zz)+offset;hits=[]
            for name,tree in receivers:
                loc,receiver_normal,index,d=tree.ray_cast(p+normal*.10,-normal,.85)
                if loc is not None:hits.append((d,name,loc))
            assert hits,'No zone plaque wall receiver'
            _,name,loc=min(hits,key=lambda r:r[0]);gap=(p-loc).dot(normal)
            assert gap>=-.002,('Plaque penetrates wall',gap)
            if gap>.002:
                K.prism(('zone '+tag+' mounting spacers','STEEL'),p,loc,.008,.008,16,0,True,0)
                S.register(owner,'wall spacer','RH refine zone '+tag+' mounting spacers STEEL',name,[loc],-normal,'wall')
                name='RH refine zone '+tag+' mounting spacers STEEL'
            S.register(owner,'retained plaque back','RH walls assets AUDI',name,[p],-normal,'wall')
    sc['rh_zone_'+tag.lower()+'_correction']=json.dumps({'offset':list(offset),'camera':'01_machinery_turbine_grid' if tag=='C' else '02_machinery_coolant_eccs','glyph_samples':len(points),'panel_samples':len(panel),'moved_vertex_counts':{k:len(v) for k,v in selected.items()}})
    bpy.context.view_layer.update()
    print('ZONE_C_PLACEMENT',sc['rh_zone_'+tag.lower()+'_correction'],flush=True)


def build(K,M):
    zone(K,M,'C',Vector((-1,0,0)),Vector((0,1,0)),Vector((5.9,-7,2.5)))
    zone(K,M,'A',Vector((0,1,0)),Vector((1,0,0)),Vector((6,-5.4,2.4)))
    danger(K,M)


def danger(K,M):
    sc=bpy.context.scene;o=bpy.data.objects['R2 gfx DANGER AUTHORISED PERSONNEL ONLY']
    dg=bpy.context.evaluated_depsgraph_get();o.data.calc_loop_triangles()
    points=[o.matrix_world@(sum((o.data.vertices[i].co for i in f.vertices),Vector())/3) for f in o.data.loop_triangles]
    bounds=[o.matrix_world@Vector(p) for p in o.bound_box]
    x0=min(p.x for p in bounds)-.07;x1=max(p.x for p in bounds)+.07
    z0=min(p.z for p in bounds)-.06;z1=max(p.z for p in bounds)+.06
    panel=[Vector((x0+(x1-x0)*i/24,-10.784,z0+(z1-z0)*j/4)) for i in range(25) for j in range(5)]
    def transparent(obj):
        return bool(obj.data.materials) and all(m and m.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.is_active_output and not n.inputs['Surface'].is_linked for n in m.node_tree.nodes) for m in obj.data.materials)
    blocked={}
    def clear(a,b):
        d=(b-a).normalized();remaining=(b-a).length-.003;p=a.copy()
        for _ in range(48):
            hit,loc,n,index,obj,mat=sc.ray_cast(dg,p,d,distance=remaining)
            if not hit:return True
            if obj.name!=o.name and not transparent(obj):
                blocked[obj.name]=blocked.get(obj.name,0)+1
                return False
            remaining-=(loc-p).length+.0001;p=loc+d*.0001
            if remaining<=0:return True
        return False
    normal=Vector((0,1,0));camera=Vector((6,-5.4,2.4))
    header=bpy.data.objects['RH refine sign EMERGENCY COOLING PANEL']
    hp=[header.matrix_world@Vector(p) for p in header.bound_box]
    hx0=min(p.x for p in hp);hx1=max(p.x for p in hp);hz0=min(p.z for p in hp);hz1=max(p.z for p in hp);hy=max(p.y for p in hp)
    header_face=[Vector((hx0+(hx1-hx0)*i/24,hy,hz0+(hz1-hz0)*j/8)) for i in range(25) for j in range(9)]
    def preserves_header(v):
        # The future plaque must not screen any part of the existing heading
        # panel, including its lower trim, from the intended machinery camera.
        fy=-10.784+v.y-.001
        for p in header_face:
            t=(fy-camera.y)/(p.y-camera.y)
            if not 0<t<1:continue
            q=camera+(p-camera)*t
            if x0+v.x-.05<=q.x<=x1+v.x+.05 and z0+v.z-.05<=q.z<=z1+v.z+.05:return False
        return True
    offsets=sorted([Vector((dx,.15,dz)) for dx in [i*.1 for i in range(-45,46)] for dz in [i*.05 for i in range(-20,51)]],key=lambda v:v.length)
    offset=next((v for v in offsets if preserves_header(v) and all(clear(camera,p+v) and clear(p+v+normal*1.2,p+v) for p in points+panel)),None)
    print('SAFETY_BLOCKERS',blocked,flush=True)
    assert offset is not None,'No clear nearby safety warning location'
    o.location+=offset;o.data.materials.clear();o.data.materials.append(bpy.data.materials['RH refine ivory lettering'])
    x0+=offset.x;x1+=offset.x;z0+=offset.z;z1+=offset.z;front=-10.784+offset.y-.001;back=front-.024
    K.bx(('safety warning panel','PANEL'),x0,x1,back,front,z0,z1,.002)
    owner='safety warning sightline correction';S.reset(owner)
    receivers=[(a.name,BVHTree.FromPolygons([a.matrix_world@v.co for v in a.data.vertices],[list(f.vertices) for f in a.data.polygons])) for a in bpy.data.objects if a.type=='MESH' and a.name.startswith(('RH walls mass ','RH walls concrete ','RH walls cladding ','RH walls steel '))]
    for xx in (x0+.12,x1-.12):
        for zz in (z0+.035,z1-.035):
            p=Vector((xx,back,zz));hits=[]
            for name,tree in receivers:
                loc,n,i,dist=tree.ray_cast(p+normal*.1,-normal,.85)
                if loc is not None:hits.append((dist,name,loc))
            assert hits,'Missing safety sign wall receiver'
            _,name,loc=min(hits,key=lambda x:x[0]);assert (p-loc).dot(normal)>.002
            K.prism(('safety warning spacers','STEEL'),p,loc,.008,.008,16,0,True,0)
            S.register(owner,'wall spacer','RH refine safety warning spacers STEEL',name,[loc],-normal,'wall')
            S.register(owner,'panel seat','RH refine safety warning panel PANEL','RH refine safety warning spacers STEEL',[p],-normal,'wall')
    sc['rh_safety_warning_correction']=json.dumps({'offset':list(offset),'camera':'02_machinery_coolant_eccs','glyph_samples':len(points),'panel_samples':len(panel)})
    bpy.context.view_layer.update();print('SAFETY_WARNING_PLACEMENT',sc['rh_safety_warning_correction'],flush=True)
