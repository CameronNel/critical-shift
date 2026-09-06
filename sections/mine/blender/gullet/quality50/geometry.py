"""Purpose-built worn timber carts and contact-safe environmental repairs."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
COLLECTION=None

def collection(scene):
    global COLLECTION
    COLLECTION=bpy.data.collections.new('Q50_AUTHORED_AGE_AND_CARTS')
    scene.collection.children.link(COLLECTION)
    return COLLECTION

def mesh(name,verts,faces,mat,parent=None,loc=(0,0,0),rot=(0,0,0)):
    me=bpy.data.meshes.new('Q50_GEO_'+name);me.from_pydata(verts,[],faces);me.update()
    uv=me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        a=max(range(3),key=lambda i:abs(poly.normal[i]));pair=((1,2),(0,2),(0,1))[a]
        for j in poly.loop_indices:
            v=me.vertices[me.loops[j].vertex_index].co;uv.data[j].uv=(v[pair[0]],v[pair[1]])
    o=bpy.data.objects.new('Q50_'+name,me);COLLECTION.objects.link(o);o.data.materials.append(mat)
    if parent:o.parent=parent
    o.location=loc;o.rotation_euler=rot;o['csm_id']=o.name;o['q50_authored']=True
    return o

def box(name,loc,size,mat,parent=None,rot=(0,0,0),bevel=.004):
    x,y,z=[a*.5 for a in size]
    vv=[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)]
    ff=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
    o=mesh(name,vv,ff,mat,parent,loc,rot)
    if bevel:
        m=o.modifiers.new('Manufactured edge, not inflated bevel','BEVEL');m.width=bevel;m.segments=1
    return o

def curve(name,paths,radius,mat,parent=None):
    cu=bpy.data.curves.new('Q50_CURVE_'+name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=radius;cu.bevel_resolution=1
    for points in paths:
        if len(points)<2:continue
        s=cu.splines.new('POLY');s.points.add(len(points)-1)
        for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new('Q50_'+name,cu);COLLECTION.objects.link(o);cu.materials.append(mat)
    if parent:o.parent=parent
    o['csm_id']=o.name;o['q50_authored']=True
    return o

def cylinder(name,a,b,r,mat,parent=None,n=16):
    a,b=Vector(a),Vector(b);d=b-a
    u=d.cross(Vector((0,0,1)))
    if u.length<1e-5:u=d.cross(Vector((0,1,0)))
    u.normalize();w=d.normalized().cross(u)
    verts=[tuple(c+r*(u*math.cos(i*math.tau/n)+w*math.sin(i*math.tau/n))) for c in (a,b) for i in range(n)]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,mat,parent)

def plank(name,loc,size,mat,parent=None,rot=(0,0,0),seed=1,rotted=False):
    """Long grain follows local X; individually chipped, uneven plank edges."""
    rng=random.Random(seed);L,W,H=size;vv=[];N=14
    for i in range(N+1):
        x=(i/N-.5)*L
        for sy,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            end=rng.uniform(-.012,.008) if i in (0,N) else 0
            chip=rng.uniform(0,.018 if rotted else .008) if i in (0,1,N-1,N) else rng.uniform(0,.002)
            vv.append((x+end,sy*(W/2-chip),sz*(H/2-rng.uniform(0,.002))+math.sin(i*.6+seed)*.0014))
    ff=[(3,2,1,0),tuple(range(4*N,4*N+4))]
    for i in range(N):
        for j in range(4):ff.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    o=mesh(name,vv,ff,mat,parent,loc,rot);o['q50_material']='rotted wood' if rotted else 'rough wood'
    return o

def wheel(name,side,y,mat,parent):
    # Gauge and tread height match the existing rails, not a scaled-down wheelset.
    profile=[(-.128,.238),(-.108,.238),(-.102,.200),(.055,.200),(.069,.170),(.069,.057),(-.128,.057)]
    vv=[];n=36
    for ax,r in profile:
        for j in range(n):
            a=j*math.tau/n;vv.append((side*(.610+ax),y+r*math.cos(a),.350+r*math.sin(a)))
    ff=[]
    for i in range(len(profile)):
        for j in range(n):
            f=(i*n+j,i*n+(j+1)%n,((i+1)%len(profile))*n+(j+1)%n,((i+1)%len(profile))*n+j)
            ff.append(f if side==1 else tuple(reversed(f)))
    o=mesh(name,vv,ff,mat,parent);o['q50_wheel_radius']=.2;o['q50_tread_bottom_local']=.15
    cylinder(name+'_hub',(side*.647,y,.35),(side*.711,y,.35),.075,mat,parent,24)
    for j in range(5):
        a=j*math.tau/5;yy=y+.12*math.cos(a);zz=.35+.12*math.sin(a)
        cylinder(name+'_bolt',(side*.681,yy,zz),(side*.693,yy,zz),.013,mat,parent,6)
    return o

def new_carts(scene,m):
    report=[]
    for ci,key in enumerate(['CSM_Dispatch_cart','CSM_Loaded_haulage_cart']):
        root=scene.objects.get(key)
        if root is None:raise RuntimeError('Missing original cart root '+key)
        removed=list(root.children_recursive)
        for child in reversed(removed):bpy.data.objects.remove(child,do_unlink=True)
        for x in [-.44,.44]:box('Cart_chassis',(x,0,.48),(.09,1.65,.09),m['iron'],root)
        for y in [-.49,.49]:
            box('Cart_crossmember',(0,y,.48),(1.2,.09,.09),m['iron'],root)
            cylinder('Cart_axle',(-.67,y,.35),(.67,y,.35),.038,m['iron'],root)
            for side in [-1,1]:
                wheel('Flanged_iron_wheel',side,y,m['iron'],root)
                box('Bearing_block',(side*.43,y,.40),(.12,.17,.12),m['iron'],root,bevel=.012)
                for z in [.457,.467,.477]:box('Short_leaf_spring',(side*.43,y,z),(.07,.38,.007),m['iron'],root,bevel=.001)
        for i in range(5):
            plank('Cart_floor_plank',(-.436+i*.218,0,.567),(1.48,.211,.061),m['wood'][(i+ci)%5],root,(0,0,math.pi/2),ci*30+i)
        for course in range(3):
            z=.651+course*.130
            for side in [-1,1]:
                plank('Cart_side_plank',(side*(.550+.023*course),0,z),(1.555,.055,.123),m['wood'][(course+side+ci)%5],root,(0,0,math.pi/2),ci*100+course*12+side)
                plank('Cart_end_plank',(0,side*.802,z),(1.067+.044*course,.055,.123),m['wood'][(course+2+ci)%5],root,seed=40+course+side+ci*20)
        for side in [-1,1]:
            for y in [-.754,.754]:
                box('Cart_rust_corner_strap',(side*.616,y,.792),(.018,.07,.390),m['iron'],root,bevel=.002)
                for z in [.649,.780,.910]:cylinder('Cart_strap_rivet',(side*.623,y,z),(side*.639,y,z),.014,m['iron'],root,8)
            plank('Cart_top_wood_rail',(side*.601,0,.993),(1.67,.066,.052),m['wood'][(ci+2)%5],root,(0,0,math.pi/2),11+ci+side)
            plank('Cart_bumper',(0,side*.912,.465),(1.00,.103,.10),m['wood'][0],root,seed=331+side)
        curve('Cart_push_iron',[[(-.42,-.77,.67),(-.44,-1.09,.88),(.44,-1.09,.88),(.42,-.77,.67)]],.021,m['iron'],root)
        cylinder('Cart_wood_push_grip',(-.33,-1.09,.88),(.33,-1.09,.88),.032,m['wood'][3],root)
        cylinder('Cart_brake_arm',(.49,-.51,.40),(.49,-1.04,.89),.018,m['iron'],root)
        cylinder('Cart_brake_wood_grip',(.49,-1.04,.87),(.49,-1.11,1.01),.024,m['wood'][1],root)
        for y in [-.49,.49]:box('Cart_brake_shoe',(.42,y+.177,.32),(.095,.032,.11),m['iron'],root,bevel=.003)
        for name,loc,kind in [('SOCKET_CART_PUSH',(0,-1.11,.88),'push_handle'),('SOCKET_CART_LOAD',(0,0,.75),'ore_load')]:
            o=bpy.data.objects.new('Q50_'+name+f'_{ci}',None);COLLECTION.objects.link(o);o.parent=root;o.location=loc;o['csm_socket_type']=kind;o['csm_id']=o.name
        rng=random.Random(506+ci)
        for i in range(7 if ci else 3):
            x=[-.32,0,.32][i%3];y=-.48+(i//3)*.40
            verts=[(-.075,-.10,0),(.08,-.095,0),(.095,.07,.01),(-.05,.095,0),(-.04,-.04,.07),(.045,.025,.105)]
            faces=[(0,3,2,1),(0,1,4),(1,5,4),(1,2,5),(2,3,5),(3,4,5),(3,0,4)]
            o=mesh('Cart_residual_ore',verts,faces,m['mineral'],root,(x,y,.600),rot=(0,0,rng.uniform(-.3,.3)));o['csm_ore_chunk']=True
        curve('Cart_floor_dust',[[(-.4,-.68,.600),(-.1,-.70,.600),(.40,-.68,.600)],[(.46,-.6,.600),(.46,0,.600),(.46,.65,.600)]],.008,m['dirt'],root)
        root['q50_wooden_cart']=True;root['q50_rim_above_floor_m']=1.10;root['q50_body_width_m']=1.25;root['q50_body_length_m']=1.67
        report.append({'root':key,'removed_meshes_and_empties':len(removed),'wooden_body':True,'rim_above_floor_m':1.10,'old_rim_above_floor_m':1.53,'rail_gauge_preserved_m':1.10,'world_transform':[list(row) for row in root.matrix_world]})
    return report

def roughen_panels(scene):
    done=[]
    targets=[o for o in scene.objects if o.type=='MESH' and any(s in o.name for s in ['Leaf_outer_skin','Door_folded_skin','Cabinet_back','Door_recess'])]
    for idx,o in enumerate(targets):
        o.data=o.data.copy();me=o.data
        bm=bmesh.new();bm.from_mesh(me)
        long_edges=[e for e in bm.edges if e.calc_length()>.16]
        if long_edges:bmesh.ops.subdivide_edges(bm,edges=long_edges,cuts=8,use_grid_fill=True)
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(me);bm.free();me.update()
        xs=[v.co.x for v in me.vertices];zs=[v.co.z for v in me.vertices]
        xmin,xmax=min(xs),max(xs);zmin,zmax=min(zs),max(zs)
        for v in me.vertices:
            x,y,z=v.co;fade=min(1,max(0,min(x-xmin,xmax-x,z-zmin,zmax-z)/.10))
            dent=(.0018*math.sin(x*7+idx)*math.sin(z*5+.5)+.0012*math.sin(x*17+z*14))
            v.co.y+=fade*dent
        me.update();o['q50_physical_dents_m']=.003;done.append(o.name)
    return done

def planar_patch(name,center,u,v,halfsize,mat,parent=None,seed=0):
    rng=random.Random(seed);c=Vector(center);u=Vector(u);v=Vector(v);sx,sy=halfsize
    verts=[tuple(c)];N=13
    for i in range(N):
        a=i*math.tau/N;r=rng.uniform(.64,1.)
        verts.append(tuple(c+r*(u*(math.cos(a)*sx)+v*(math.sin(a)*sy))))
    return mesh(name,verts,[(0,i+1,(i+1)%N+1) for i in range(N)],mat,parent)

def surface_age(scene,m):
    made=0
    for idx,o in enumerate(list(scene.objects)):
        if o.type!='MESH' or o.get('csm_collision_only'):continue
        if any(s in o.name for s in ['Leaf_outer_skin','Door_folded_skin','Cabinet_back']):
            bb=[Vector(v) for v in o.bound_box];lo=Vector([min(p[i] for p in bb) for i in range(3)]);hi=Vector([max(p[i] for p in bb) for i in range(3)])
            rng=random.Random(223+idx)
            for k in range(13):
                x=rng.uniform(lo.x+.10,hi.x-.10);z=rng.uniform(lo.z+.12,hi.z-.16)
                planar_patch('Paint_loss_to_rust',(x,lo.y-.004,z),(1,0,0),(0,0,1),(rng.uniform(.025,.08),rng.uniform(.055,.19)),m['iron'],o,k+idx)
                if k%3==0:
                    length=min(rng.uniform(.15,.6),z-lo.z-.05)
                    planar_patch('Downward_rust_bleed',(x,lo.y-.0045,z-length*.45),(1,0,0),(0,0,1),(.007,length*.5),m['stain'],o,k+332)
                made+=1
    for i,(x,y) in enumerate([(-2.8,-9.8),(3.4,-5.4),(1.85,-10.2),(-4.2,-2.8),(4.9,-11.7)]):
        rng=random.Random(i+782);points=[]
        for j in range(12):points.append((x+j*.072+rng.uniform(-.03,.03),y+j*.041+rng.uniform(-.04,.04),.0055))
        curve('Concrete_hairline_crack',[points],.0024,m['dirt']);made+=1
    z=-.025*21.55
    for i in range(20):
        rng=random.Random(452+i);y=20.2+rng.random()*2.7
        planar_patch('Sump_mineral_tideline',(8.401,y,z-.16),(0,1,0),(0,0,1),(.12,.075),m['stain'],seed=i)
    return {'physical_wear_clusters':made,'sump_tideline_patches':20}
