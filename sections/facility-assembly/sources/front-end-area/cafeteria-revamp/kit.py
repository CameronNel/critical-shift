"""Cafeteria authoring helpers; geometry reuses the existing front-end MB2 kit."""
import bpy, bmesh, math, os, sys, json
from pathlib import Path
from mathutils import Vector, Matrix, Euler
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from fe_kit import MB2, p_ring_prism, p_rbox, p_cyl, p_torus, p_cushion, p_lathe
TAU = math.tau
MATS = []; MI = {}

def material(name, color, rough=.5, metal=0, texture=None, bump=0, emission=0, sheen=0):
    name = 'CAF_R8_' + name
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metal; bs.inputs['Sheen Weight'].default_value=sheen
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
    nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if texture:
        tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeVectorMath');mp.operation='MULTIPLY'
        scale={'wood':(3,35,4),'fabric':(200,200,200),'sisal':(250,250,250),'rubber':(140,140,140),'plaster':(3,3,3)}[texture]
        mp.inputs[1].default_value=scale; nt.links.new(tc.outputs['Generated'],mp.inputs[0])
        nz=nt.nodes.new('ShaderNodeTexNoise');nz.inputs['Scale'].default_value=1;nz.inputs['Detail'].default_value=2
        nt.links.new(mp.outputs[0],nz.inputs['Vector'])
        cr=nt.nodes.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(*(c*.86 for c in color),1);cr.color_ramp.elements[1].color=(*(min(c*1.06,1) for c in color),1)
        nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']);nt.links.new(cr.outputs['Color'],bs.inputs['Base Color'])
        rv=nt.nodes.new('ShaderNodeMapRange');rv.inputs['To Min'].default_value=max(.04,rough-.05);rv.inputs['To Max'].default_value=min(.99,rough+.06)
        nt.links.new(nz.outputs['Fac'],rv.inputs[0]);nt.links.new(rv.outputs[0],bs.inputs['Roughness'])
        if bump:
            bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Distance'].default_value=.0009;bn.inputs['Strength'].default_value=bump
            nt.links.new(nz.outputs['Fac'],bn.inputs['Height']);nt.links.new(bn.outputs[0],bs.inputs['Normal'])
    return m

def palette():
    global MATS,MI
    specs=[
      ('navy',(.042,.062,.115),.48,.12,None,0),('rust',(.48,.085,.038),.54,.06,None,0),
      ('ochre',(.65,.34,.055),.45,.15,None,0),('steel',(.46,.5,.55),.32,.85,None,0),
      ('black',(.014,.019,.024),.64,.15,None,0),('rubber',(.018,.021,.025),.87,0,'rubber',.1),
      ('walnut',(.23,.105,.045),.54,0,'wood',.06),('oak',(.51,.31,.14),.48,0,'wood',.05),
      ('ivory',(.85,.79,.64),.53,0,None,0),('white',(.89,.9,.85),.48,0,None,0),
      ('field',(.07,.19,.13),.62,0,None,0),('ball',(.69,.235,.039),.83,0,'rubber',.25),
      ('sisalblack',(.025,.032,.028),.93,0,'sisal',.22),('sisalcream',(.70,.58,.39),.92,0,'sisal',.22),
      ('sisalred',(.52,.026,.017),.91,0,'sisal',.22),('sisalgreen',(.022,.23,.108),.91,0,'sisal',.22),
      ('rope',(.76,.73,.61),.98,0,None,0),('fabric_rust',(.37,.095,.045),.94,0,'fabric',.2),
      ('fabric_blue',(.1,.145,.25),.97,0,'fabric',.2),('stitch',(.43,.255,.13),.9,0,None,0),
      ('leaf',(.075,.19,.06),.83,0,None,0),('soil',(.055,.029,.018),.99,0,None,0),
      ('ceramic',(.79,.73,.60),.28,0,None,0),('food_green',(.22,.34,.048),.75,0,None,0),
      ('food_gold',(.62,.31,.075),.74,0,None,0),('food_red',(.42,.028,.017),.57,0,None,0),
      ('plaster',(.43,.29,.34),.88,0,'plaster',.08),('copper',(.45,.18,.064),.4,.7,None,0)
    ]
    MATS[:]=[material(*s) for s in specs]; MI.clear();MI.update({s[0]:i for i,s in enumerate(specs)})
    MI['led']=len(MATS);MATS.append(material('led',(.90,.31,.065),.45,emission=2.2))
    MI['lamp']=len(MATS);MATS.append(material('lamp',(.99,.80,.49),.4,emission=2.5))
    MI['redled']=len(MATS);MATS.append(material('redled',(.8,.035,.006),.5,emission=1.8))
    MI['glass']=len(MATS)
    glass=material('glass',(.74,.86,.88),.16)
    b=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Transmission Weight'].default_value=.85;b.inputs['IOR'].default_value=1.45
    MATS.append(glass)
    return MI

def mb(): return MB2(MATS)
def finish(m,name,coll,parent=None):
    ob=m.finish(name,coll);ob.parent=parent
    ob['support']='assembly'
    # Each editable component carries only the slots it actually uses.
    used=sorted({p.material_index for p in ob.data.polygons})
    mats=[ob.data.materials[i] for i in used]; remap={i:j for j,i in enumerate(used)}
    indices=[remap[p.material_index] for p in ob.data.polygons]
    ob.data.materials.clear()
    for mat in mats:ob.data.materials.append(mat)
    for p,i in zip(ob.data.polygons,indices):p.material_index=i
    # Area-weighted normals retain smooth curved pieces and planar manufactured faces.
    md=ob.modifiers.new('Manufactured surface normals','WEIGHTED_NORMAL');md.keep_sharp=True;md.weight=40
    return ob

def empty(name,coll,loc=(0,0,0),parent=None):
    o=bpy.data.objects.new(name,None);coll.objects.link(o);o.location=loc;o.parent=parent;return o
def collection(name,parent=None):
    c=bpy.data.collections.new(name);(parent or bpy.context.scene.collection).children.link(c);return c
def curve(name,pts,r,mat,coll,parent=None,closed=False,res=3):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=res
    s=cu.splines.new('POLY');s.points.add(len(pts)-1)
    for v,p in zip(s.points,pts):v.co=(*p,1)
    s.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);coll.objects.link(o);cu.materials.append(MATS[MI[mat]]);o.parent=parent;o['support']='assembly';return o
def rectline(m,x,y,z,w,h,t,mi):
    for yy in (-h/2,h/2):m.rbox(x,y+yy,z,w,t,.0015,0,mi=MI[mi])
    for xx in (-w/2,w/2):m.rbox(x+xx,y,z,t,h,.0015,0,mi=MI[mi])
def panel(name,loc,w,h,img,coll,rot=(0,0,0),parent=None,lit=0):
    matname='CAF_R8_image_'+img+('_lit' if lit else '')
    mat=bpy.data.materials.get(matname)
    if not mat:
        mat=bpy.data.materials.new(matname);mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
        im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(HERE/'textures'/img),check_existing=True)
        nt.links.new(im.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.57
        if lit:nt.links.new(im.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=lit
    me=bpy.data.meshes.new(name);me.from_pydata([(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)],[],[(0,1,2,3)])
    uv=me.uv_layers.new(name='UVMap')
    for l,p in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):l.uv=p
    me.materials.append(mat);o=bpy.data.objects.new(name,me);coll.objects.link(o);o.location=loc;o.rotation_euler=rot;o.parent=parent;o['support']='assembly';return o

def screw(m,p,axis=(0,-1,0),r=.005):
    p=Vector(p);d=Vector(axis);m.between(p,p+d*.003,r,seg=8,mi=MI['steel']);q=p+d*.0033
    tangent=Vector((1,0,0)) if abs(d.x)<.9 else Vector((0,1,0))
    m.between(q-tangent*r*.64,q+tangent*r*.64,.0007,seg=4,mi=MI['black'])

def tapered(m,loc,lower,upper,h,mi):
    bx,by=lower;tx,ty=upper;cx,cy,cz=loc
    bm=bmesh.new();v=[]
    for z,w,d in [(cz-h/2,bx,by),(cz+h/2,tx,ty)]:
      v.extend([bm.verts.new((cx+sx*w/2,cy+sy*d/2,z)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]])
    for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bmesh.ops.bevel(bm,geom=bm.edges[:],offset=.003,segments=2,affect='EDGES')
    m.add(bm,mi=MI[mi])

def bounds(objects):
    points=[o.matrix_world@Vector(v) for o in objects if o.type in ('MESH','CURVE','FONT') for v in o.bound_box]
    return [[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
def triangles(objects):
    dg=bpy.context.evaluated_depsgraph_get();total=0
    for o in objects:
      if o.type not in ('MESH','CURVE','FONT'):continue
      e=o.evaluated_get(dg);me=e.to_mesh();total+=sum(len(p.vertices)-2 for p in me.polygons);e.to_mesh_clear()
    return total
def camera(name,loc,target,lens=48,coll=None):
    dat=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,dat);(coll or bpy.context.scene.collection).objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();dat.lens=lens;dat.clip_start=.03;dat.clip_end=300;return o
def area(name,loc,target,energy,size,color,coll=None):
    dat=bpy.data.lights.new(name,'AREA');dat.energy=energy;dat.shape='DISK';dat.size=size;dat.color=color
    o=bpy.data.objects.new(name,dat);(coll or bpy.context.scene.collection).objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
def pack():
    for im in bpy.data.images:
      if im.filepath and not im.packed_file:
        im.pack();im.filepath='//textures/'+Path(im.filepath).name
    for f in bpy.data.fonts:
      if f.filepath!='<builtin>' and not f.packed_file:f.pack()
def render_settings(samples=48,res=(1200,1000)):
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=samples;s.cycles.use_denoising=True
    s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=4
    s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100
    s.view_settings.view_transform='Khronos PBR Neutral';s.view_settings.exposure=-.5
    s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=5

def studio(asset,root,kind):
    st=collection('REVIEW_STUDIO');m=mb();m.rbox(0,0,-.55 if kind=='dartboard' else -.06,200,200,.12,0,mi=MI['black']);finish(m,'Review floor',st)
    bpy.context.scene.world=bpy.data.worlds.new('Review world');bpy.context.scene.world.use_nodes=True
    bpy.context.scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.12,.14,.17,1)
    bpy.context.scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
    bb=bounds(asset.all_objects);centre=Vector([(bb[0][i]+bb[1][i])/2 for i in range(3)])
    size=max(bb[1][i]-bb[0][i] for i in range(3))
    cam=camera('ASSET_HERO',centre+Vector((size*1.27,-size*1.65,size*.85)),centre,50,st)
    if kind=='dartboard':cam.location=(1.02,-2.10,.56);cam.rotation_euler=(Vector((0,-.1,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=58
    bpy.context.scene.camera=cam
    area('Key softbox',centre+Vector((size*.6,-size*.8,size*1.35)),centre,180*size,1.8*size,(1,.91,.82),st)
    area('Cool rim',centre+Vector((-size*.7,size*.8,size*.9)),centre,220*size,size,(.73,.83,1),st)
    area('Front fill',centre+Vector((-size,-size*.9,size*.4)),centre,80*size,size,(.87,.9,1),st)
    return st
