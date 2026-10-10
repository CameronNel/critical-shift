"""Seat owned door hardware on the measured formed leaves, without changing the leaves."""
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from r2lib import WALLS
import rh_support_registry as SUPPORT
OWNER='door hardware seats'

def components(mesh):
    parent=list(range(len(mesh.vertices)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for e in mesh.edges:
        a,b=map(find,e.vertices)
        if a!=b:parent[b]=a
    groups={}
    for v in mesh.vertices:groups.setdefault(find(v.index),[]).append(v.index)
    return list(groups.values())

def frame(w,p):return ((Vector((p.x,p.y))-w.P).dot(w.t),(Vector((p.x,p.y))-w.P).dot(w.n),p.z)
def point(w,u,d,z):
    p=w.pt(u,d);return Vector((p.x,p.y,z))

def build():
    SUPPORT.reset(OWNER);records=[];dg=bpy.context.evaluated_depsgraph_get();dg.update()
    for wi,family in ((4,'FUEL HANDLING'),(6,'MAIN ACCESS'),(1,'COOLING PLANT')):
        w=WALLS[wi];normal=Vector((w.n.x,w.n.y,0))
        leaves=sorted((o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(family+'.door leaf')),key=lambda o:o.name)
        assert len(leaves)==2,(family,len(leaves))
        for leaf in leaves:
            ev=leaf.evaluated_get(dg);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons]
            tree=BVHTree.FromPolygons(vs,faces);coords=[frame(w,p) for p in vs];a,b=min(p[0] for p in coords),max(p[0] for p in coords);front=max(p[1] for p in coords)
            outer=a if (a+b)/2<w.L/2 else b;inside=1 if outer==a else -1
            def surface(u,z):
                hit=tree.ray_cast(point(w,u,front+1,z),-normal,2)
                assert hit[0] is not None,(leaf.name,u,z,'no formed leaf face')
                assert hit[1].dot(normal)>.7,(leaf.name,'unexpected face normal',tuple(hit[1]))
                return frame(w,hit[0])[1]
            name='RH refine door hardware '+leaf.name+' STEEL';o=bpy.data.objects[name];inv=o.matrix_world.inverted();counts={};parts=components(o.data)
            for ci,inds in enumerate(parts):
                pts=[o.matrix_world@o.data.vertices[i].co for i in inds];q=[frame(w,p) for p in pts];us,ds,zs=zip(*q);lo,hi=min(ds),max(ds);um=(min(us)+max(us))/2;zm=(min(zs)+max(zs))/2;du=max(us)-min(us);dz=max(zs)-min(zs)
                if du>1 and .40<dz<.50:
                    role='kickplate';samples=[(um,zm),(min(us)+.02,min(zs)+.03),(max(us)-.02,min(zs)+.03),(min(us)+.02,max(zs)-.03),(max(us)-.02,max(zs)-.03)]
                elif .10<du<.12 and .17<dz<.19:
                    role='hinge plate';samples=[(outer+inside*.04,zm)]
                elif du<.04 and dz<.04 and 1.1<zm<1.5:
                    role='handle stem';samples=[(um,zm)]
                elif du<.05 and .33<dz<.35:
                    counts['grip']=counts.get('grip',0)+1;continue
                else:raise AssertionError((name,ci,du,dz,'unknown owned part'))
                counts[role]=counts.get(role,0)+1
                hits=[surface(u,z) for u,z in samples];seat=max(hits)-.0005
                if role=='handle stem':
                    rear=[i for i,d in zip(inds,ds) if abs(d-lo)<1e-5];assert len(rear)>=8
                    for i in rear:
                        p=o.matrix_world@o.data.vertices[i].co;o.data.vertices[i].co=inv@(p+normal*(seat-lo))
                else:
                    # The broad rear face, not a bevel extremum, is the bearing datum.
                    index={old:new for new,old in enumerate(inds)}
                    fs=[tuple(index[i] for i in poly.vertices) for poly in o.data.polygons if all(i in index for i in poly.vertices)]
                    part=BVHTree.FromPolygons(pts,fs)
                    backs=[]
                    for u,z in samples:
                        hit=part.ray_cast(point(w,u,lo-1,z),normal,2)
                        assert hit[0] is not None,(name,ci,'missing rear bearing face')
                        assert hit[1].dot(-normal)>.7,(name,ci,'rear bearing normal')
                        backs.append(frame(w,hit[0])[1])
                    bearing=max(backs);shift=seat-bearing
                    for i in inds:
                        p=o.matrix_world@o.data.vertices[i].co;u,d,z=frame(w,p)
                        # Flatten protruding rear bevels into the mounting plane;
                        # retain the forward bevels and the rest of the formed part.
                        new_d=max(d+shift,seat)
                        o.data.vertices[i].co=inv@(p+normal*(new_d-d))
                anchors=[tuple(point(w,u,seat,z)) for (u,z),hit in zip(samples,hits) if abs(hit-max(hits))<.001]
                assert anchors
                SUPPORT.register(OWNER,leaf.name+' '+role+' '+str(ci),name,leaf.name,anchors,tuple(-normal),'wall',gap=.0015,penetration=.002,angle=15)
                records.append({'leaf':leaf.name,'wall_index':wi,'subject':name,'component':ci,'role':role,'vertices':inds,'rear_depth_before_m':lo,'rear_depth_after_m':seat,'formed_surface_depths_m':hits,'anchors':anchors,'normal':tuple(normal)})
            assert counts=={'hinge plate':3,'handle stem':2,'grip':1,'kickplate':1},(name,counts)
            o.data.update();ev.to_mesh_clear()
    assert len(records)==36
    bpy.context.scene['rh_door_hardware_seats']=json.dumps(records)
    bpy.context.view_layer.update()
    return records
