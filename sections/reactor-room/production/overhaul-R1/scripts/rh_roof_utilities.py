"""Candidate-owned roof routing, supported diameter hierarchy and legacy header."""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import crk,rh_mats,rh_stlib as S,rh_svc_lib as U
import rh_support_registry as SUPPORT

OWNER='roof utility correction'
PREFIX='RH refine '

def duct_material():
    return rh_mats.surf('RH roof utility sheet enamel',(.40,.40,.39),.44,.25,
        mottle=.10,streak=.06,edge=(.48,.48,.465),grime=.08,scale=6,bump=.002)

def components(me):
    adj=[set() for v in me.vertices]
    for e in me.edges:
        a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    seen=set()
    for i in range(len(me.vertices)):
        if i in seen:continue
        group={i};todo=[i];seen.add(i)
        while todo:
            a=todo.pop()
            for b in adj[a]-seen:seen.add(b);group.add(b);todo.append(b)
        yield group

def world_bounds(o,ids):
    p=[o.matrix_world@o.data.vertices[i].co for i in ids]
    return [min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)]

def old_loops():
    rows=[]
    for name in ('RF BATCH services RF dark','RF BATCH services RF orange'):
        o=bpy.data.objects[name]
        for ids in components(o.data):
            if len(ids)!=48:continue
            lo,hi=world_bounds(o,ids)
            if hi[0]-lo[0]<16 or hi[1]-lo[1]<16 or not 17.1<lo[2]<17.2:continue
            points=[o.matrix_world@o.data.vertices[i].co for i in sorted(ids)]
            clusters=[]
            while points:
                first=points[0];near=[v for v in points if (v-first).length<.05]
                assert len(near)==6,'Unexpected legacy utility cross section'
                clusters.append(sum(near,Vector())/6)
                points=[v for v in points if (v-first).length>=.05]
            assert len(clusters)==8
            clusters.sort(key=lambda p:math.atan2(p.y,p.x))
            rows.append(dict(object=o,ids=ids,centres=clusters))
    assert len(rows)==3,'Expected three inherited 42mm utility loops'
    return rows

def distance_xy(p,rows):
    best=100
    for row in rows:
        q=row['centres']
        for a,b in zip(q,q[1:]+q[:1]):
            d=Vector((b.x-a.x,b.y-a.y));v=Vector((p.x-a.x,p.y-a.y))
            t=max(0,min(1,v.dot(d)/d.length_squared))
            best=min(best,(v-d*t).length)
    return best

def closed_round_loop(bm,centres,inverse):
    # Rounded octagonal route; a world-Z radial frame closes without a seam twist.
    path=[]
    for i,p in enumerate(centres):
        a=p+(centres[i-1]-p).normalized()*.12
        b=p+(centres[(i+1)%8]-p).normalized()*.12
        for k in range(8):
            t=k/7;path.append(a*(1-t)**2+p*(2*t*(1-t))+b*t*t)
    rings=[]
    for i,p in enumerate(path):
        tangent=(path[(i+1)%len(path)]-path[i-1]).normalized()
        u=Vector((0,0,1));v=tangent.cross(u).normalized()
        rings.append([bm.verts.new(inverse@(p+.021*(u*math.cos(2*math.pi*k/32)+v*math.sin(2*math.pi*k/32)))) for k in range(32)])
    for i,a in enumerate(rings):
        b=rings[(i+1)%len(rings)]
        for k in range(32):
            f=bm.faces.new((a[k],a[(k+1)%32],b[(k+1)%32],b[k]));f.smooth=True


def reroute_small_loops():
    rows=old_loops();moved=0
    # Move their complete nearby junction/clip assemblies as well as the tubes.
    for name in ('RF BATCH services RF dark','RF BATCH services RF orange',
                 'RF BATCH services RF edge','RF BATCH services RF gunmetal'):
        o=bpy.data.objects[name];delta=o.matrix_world.to_3x3().inverted()@Vector((0,0,-.67))
        groups=list(components(o.data))
        for ids in groups:
            lo,hi=world_bounds(o,ids);c=Vector([(lo[k]+hi[k])/2 for k in range(3)])
            if 17.06<lo[2] and hi[2]<17.31 and distance_xy(c,rows)<.30:
                for i in ids:o.data.vertices[i].co+=delta
                moved+=1
        o.data.update()
    for name in ('RF BATCH services RF dark','RF BATCH services RF orange'):
        selected=[r for r in rows if r['object'].name==name];o=bpy.data.objects[name]
        bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
        ids=set().union(*(r['ids'] for r in selected))
        bmesh.ops.delete(bm,geom=[bm.verts[i] for i in ids],context='VERTS')
        for row in selected:
            centres=[Vector((p.x,p.y,16.50)) for p in row['centres']]
            closed_round_loop(bm,centres,o.matrix_world.inverted());row['centres']=centres
        bm.normal_update();bm.to_mesh(o.data);bm.free();o.data.update()
    bpy.context.scene['rh_roof_utility_routes']=json.dumps(dict(centre_z=16.50,radius=.021,
        segments=32,moved_legacy_components=moved,loops=[dict(object=r['object'].name,
        centres=[list(p) for p in r['centres']]) for r in rows]))
    return rows


def annular(K,key,a,b,outer0,outer1,inner0,inner1,seg=64):
    a=Vector(a);b=Vector(b);axis=(b-a).normalized();length=(b-a).length
    _,u,v=S.basis(axis);bm=K.get(key);old=set(bm.verts)
    S.lathe(K,key,0,0,[(inner0,0),(outer0,0),(outer1,length),(inner1,length),(inner0,0)],seg)
    for p in bm.verts:
        if p not in old:
            q=p.co.copy();p.co=a+u*q.x+v*q.y+axis*q.z


def register(name,subject,target,points,direction=(0,0,1),kind='ceiling'):
    SUPPORT.register(OWNER,name,PREFIX+subject,PREFIX+target,points,direction,kind)


def small_hanger(K,group,centres,top,plate_bounds):
    x0,x1,y0,y1=plate_bounds
    K.bx((group+' plate','STEEL'),x0,x1,y0,y1,top-.012,top,.001)
    points=[((x0+x1)/2+dx,(y0+y1)/2+dy,top) for dx,dy in ((-.02,-.02),(.02,.02))]
    SUPPORT.register(OWNER,group+' plate onto girder',PREFIX+group+' plate STEEL','RH walls girders STEEL',points,(0,0,1),'ceiling')
    for i,p in enumerate(centres):
        p=Vector((p[0],p[1],16.50))
        centre,direction=p,Vector(centres[i][2])
        U.clamp_ring(K,(group+' clamps','STEEL'),centre,direction,.021,.04)
        z=16.50+.021*1.13
        K.prism((group+' rods','STEEL'),(p.x,p.y,z),(p.x,p.y,top-.012),.006,.006,16,0,True,0)
        register(group+' rod '+str(i),group+' rods STEEL',group+' plate STEEL',[(p.x,p.y,top-.012)])
        register(group+' clamp '+str(i),group+' clamps STEEL',group+' rods STEEL',[(p.x,p.y,z)])
        SUPPORT.register(OWNER,group+' pipe '+str(i),centres[i][3],PREFIX+group+' clamps STEEL',[(p.x,p.y,16.521)],(0,0,1),'clamp')


def line_crossing(row,axis,value,sign):
    pts=row['centres'];found=[]
    for a,b in zip(pts,pts[1:]+pts[:1]):
        den=b[axis]-a[axis]
        if abs(den)<1e-8:continue
        t=(value-a[axis])/den
        if 0<=t<=1:
            p=a+(b-a)*t
            if p[1-axis]*sign>0:found.append((p,(b-a).normalized()))
    assert found
    return found[0]


def carriers(K,rows):
    for x in (-3.6,3.6):
        for side in (-1,1):
            data=[line_crossing(r,0,x,side) for r in rows]
            yy=[p.y for p,d in data];group='roof utility north south '+str(x)+' '+str(side)
            small_hanger(K,group,[(p.x,p.y,list(d),r['object'].name) for (p,d),r in zip(data,rows)],16.6,(x-.055,x+.055,min(yy)-.065,max(yy)+.065))
    for y in (-6.,6.):
        for side in (-1,1):
            data=[line_crossing(r,1,y,side) for r in rows]
            xx=[p.x for p,d in data];group='roof utility corner '+str(y)+' '+str(side)
            small_hanger(K,group,[(p.x,p.y,list(d),r['object'].name) for (p,d),r in zip(data,rows)],16.75,(min(xx)-.065,max(xx)+.065,y-.055,y+.055))


def header(K,M):
    o=bpy.data.objects.get('R2 gfx CRITICAL SHIFT ENERGY SYSTEMS')
    assert o is not None and o.type=='MESH','Missing legacy hall identity'
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    centre=sum(pts,Vector())/8
    delta=Vector((10.31-max(p.x for p in pts),3.6-centre.y,8.3-centre.z))
    o.location+=delta
    o.data.materials.clear();o.data.materials.append(bpy.data.materials['RH refine ivory lettering'])
    group='legacy hall identity'
    K.bx((group+' carrier','STEEL'),10.365,10.45,3.46,3.74,8.08,8.56,.003)
    K.bx((group+' panel','PANEL'),10.311,10.365,1.90,5.30,7.90,8.70,.006)
    receivers=[]
    for host in bpy.data.objects:
        if host.type=='MESH' and host.name.startswith(('RH walls mass ','RH walls concrete ','RH walls cladding ','RH walls steel ')) and not any(t in host.name.upper() for t in ('GLASS','LENS')):
            receivers.append((host.name,BVHTree.FromPolygons([host.matrix_world@v.co for v in host.data.vertices],[list(f.vertices) for f in host.data.polygons])))
    for yy in (3.51,3.69):
        for zz in (8.17,8.47):
            point=Vector((10.45,yy,zz));hits=[]
            for name,tree in receivers:
                loc,normal,index,distance=tree.ray_cast(point-Vector((.1,0,0)),Vector((1,0,0)),.85)
                if loc is not None:hits.append((distance,name,loc))
            assert hits,'No header wall receiver'
            _,name,loc=min(hits,key=lambda x:x[0])
            K.prism((group+' spacers','STEEL'),point,loc,.012,.012,16,0,True,0)
            SUPPORT.register(OWNER,group+' wall seat',PREFIX+group+' spacers STEEL',name,[loc],(1,0,0),'wall')
            register(group+' carrier seat',group+' carrier STEEL',group+' spacers STEEL',[point],(1,0,0),'wall')
    register(group+' panel seat',group+' panel PANEL',group+' carrier STEEL',[(10.365,3.6,8.3)],(1,0,0),'wall')
    bpy.context.view_layer.update();o.data.calc_loop_triangles()
    backs=[o.matrix_world@(sum((o.data.vertices[i].co for i in t.vertices),Vector())/3) for t in o.data.loop_triangles if abs((o.matrix_world.to_3x3()@t.normal).normalized().x)>.85]
    assert backs,'No actual glyph back faces'
    SUPPORT.register(OWNER,group+' raised letters',o.name,PREFIX+group+' panel PANEL',[backs[i] for i in (0,len(backs)//2,len(backs)-1)],(1,0,0),'wall')


def numeral_plates(K,M):
    # Legacy painted numerals sat behind the added vertical wall steel.
    # Keep their geometry and give them measured, attached raised panels.
    from r2lib import WALLS
    receivers=[]
    for host in bpy.data.objects:
        if host.type=='MESH' and host.name.startswith(('RH walls mass ','RH walls concrete ','RH walls cladding ','RH walls steel ')):
            receivers.append((host.name,BVHTree.FromPolygons([host.matrix_world@v.co for v in host.data.vertices],[list(f.vertices) for f in host.data.polygons])))
    for tag in ('02','05'):
        o=bpy.data.objects['R2 gfx '+tag];points=[o.matrix_world@v.co for v in o.data.vertices];c=sum(points,Vector())/len(points)
        w=min(WALLS,key=lambda w:abs((Vector((c.x,c.y))-w.P).dot(w.n)))
        n=Vector((w.n.x,w.n.y,0));t=Vector((w.t.x,w.t.y,0))
        front=min(p.dot(n) for p in points)+.060
        o.location+=n*.060
        u0=min(p.dot(t) for p in points)-.08;u1=max(p.dot(t) for p in points)+.08
        z0=min(p.z for p in points)-.08;z1=max(p.z for p in points)+.08
        pc=t*((u0+u1)/2)+n*(front-.006)
        group='legacy numeral '+tag
        K.box((group+' panel','PANEL'),pc.x,pc.y,z0,z1,u1-u0,.012,w.angle,0)
        plate=K.get((group+' panel','PANEL'))
        plate.normal_update();K._bevel(plate,list(plate.verts),.003)
        plate.normal_update()
        shift=n*(front-.001-max(v.co.dot(n) for v in plate.verts))
        for v in plate.verts:v.co+=shift
        back=min(v.co.dot(n) for v in plate.verts)
        plate_tree=BVHTree.FromBMesh(plate)
        for u in (u0+.05,u1-.05):
            for z in (z0+.05,z1-.05):
                point=t*u+n*back+Vector((0,0,z))
                seat,normal,index,distance=plate_tree.ray_cast(point-n*.025,n,.06)
                assert seat is not None,'Missing actual numeral panel back face'
                point=seat;hits=[]
                for name,tree in receivers:
                    loc,normal,index,distance=tree.ray_cast(point+n*.1,-n,.85)
                    if loc is not None:hits.append((distance,name,loc))
                assert hits,('No numeral wall receiver',tag,w.i,list(point),list(n),front,u0,u1)
                _,name,loc=min(hits,key=lambda h:h[0])
                K.prism((group+' spacers','STEEL'),point,loc,.010,.010,16,0,True,0)
                SUPPORT.register(OWNER,group+' wall seat',PREFIX+group+' spacers STEEL',name,[loc],-n,'wall')
                register(group+' panel seat',group+' panel PANEL',group+' spacers STEEL',[point],-n,'wall')
        bpy.context.view_layer.update();o.data.calc_loop_triangles()
        faces=[o.matrix_world@(sum((o.data.vertices[i].co for i in tr.vertices),Vector())/3) for tr in o.data.loop_triangles if abs((o.matrix_world.to_3x3()@tr.normal).normalized().dot(n))>.85]
        SUPPORT.register(OWNER,group+' lettering',o.name,PREFIX+group+' panel PANEL',[faces[i] for i in (0,len(faces)//2,len(faces)-1)],-n,'wall')


def curved_hollow(K,key,points,outer=.021,inner=.017):
    bm=K.get(key);before=set(bm.verts)
    U.sweep(bm,points,[outer]*len(points),32,False,False,True)
    outer_verts=[v for v in bm.verts if v not in before]
    before=set(bm.verts);faces=set(bm.faces)
    U.sweep(bm,points,[inner]*len(points),32,False,False,True)
    inner_verts=[v for v in bm.verts if v not in before]
    bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f not in faces])
    for k in range(32):
        j=(k+1)%32
        bm.faces.new((outer_verts[j],outer_verts[k],inner_verts[k],inner_verts[j]))
        bm.faces.new((outer_verts[-32+k],outer_verts[-32+j],inner_verts[-32+j],inner_verts[-32+k]))


def trunk(K,M,rows):
    M['ROOF_MAIN']=rh_mats.surf('RH roof distribution trunk paint',(.23,.23,.22),.42,.25,mottle=.12,grime=.08,scale=5,bump=.002)
    group='roof utility main'
    annular(K,(group,'ROOF_MAIN'),(-2.8,9.55,16.5),(2.8,9.55,16.5),.05,.05,.044,.044)
    K.bx((group+' carrier','STEEL'),-3.56,3.56,9.51,9.59,16.67,16.73,.003)
    SUPPORT.register(OWNER,group+' carrier bearings',PREFIX+group+' carrier STEEL','RH walls girders STEEL',[(-3.50,9.55,16.67),(3.50,9.55,16.67)],(0,0,-1),'bearing')
    for x in (-1.8,0.,1.8):
        U.clamp_ring(K,(group+' clamps','STEEL'),(x,9.55,16.5),(1,0,0),.05,.04)
        K.prism((group+' rods','STEEL'),(x,9.55,16.5565),(x,9.55,16.67),.008,.008,16,0,True,0)
        register(group+' rod '+str(x),group+' rods STEEL',group+' carrier STEEL',[(x,9.55,16.67)])
        register(group+' clamp '+str(x),group+' clamps STEEL',group+' rods STEEL',[(x,9.55,16.5565)])
        register(group+' pipe '+str(x),group+' ROOF_MAIN',group+' clamps STEEL',[(x,9.55,16.55)])
    small=min(rows,key=lambda r:max(abs(p.y) for p in r['centres']));yy=max(p.y for p in small['centres'])
    for side in (-1,1):
        annular(K,(group+' reducer','ROOF_MAIN'),(side*2.8,9.55,16.5),(side*3.05,9.55,16.5),.05,.021,.044,.017)
        annular(K,(group+' joint','STEEL'),(side*2.75,9.55,16.5),(side*2.78,9.55,16.5),.073,.073,.05,.05)
        S.bolts(K,group+' fasteners','STEEL',(side*2.78,9.55,16.5),(side,0,0),.063,6,.004,.008)
        path=U.Path([(side*3.05,9.55,16.5),(side*3.2,9.55,16.5),(side*3.2,yy,16.5)],.10,8)
        points,_=path.dense(.035)
        curved_hollow(K,(group+' branch','ROOF_MAIN'),points)
        annular(K,(group+' branch sleeve','STEEL'),(side*3.2-.06,yy,16.5),(side*3.2+.06,yy,16.5),.029,.029,.021,.021)
    for x in (-.9,.9):
        annular(K,(group+' identifier','ORANGE'),(x-.025,9.55,16.5),(x+.025,9.55,16.5),.051,.051,.05,.05)
    bpy.context.scene['rh_roof_utility_trunk']=json.dumps(dict(outer_radius=.05,inner_radius=.044,small_radius=.021,
        centre_z=16.5,main_endpoints=[[-2.8,9.55,16.5],[2.8,9.55,16.5]],branch_join_y=yy))


def build(K,M):
    SUPPORT.reset(OWNER)
    o=bpy.data.objects['RF BATCH services RF white'];o.data.materials.clear();o.data.materials.append(duct_material())
    rows=reroute_small_loops();carriers(K,rows);trunk(K,M,rows);header(K,M);numeral_plates(K,M)
