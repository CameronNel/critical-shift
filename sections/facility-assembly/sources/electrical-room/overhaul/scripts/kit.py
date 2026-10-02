"""Object-specific, dimensional construction using the repository's bmesh kit."""
import bpy, bmesh, math, sys, random
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[6]
sys.path.insert(0,str(ROOT/'sections/spawn-room/blender'))
from cozy_geo import B
PREFIX='EOH | '
COLL=None
ASSEMBLY=None
def collection(name):
    global COLL
    COLL=bpy.data.collections.new(PREFIX+name)
    bpy.data.collections['MODULE_electrical-room'].children.link(COLL)
    return COLL
def material(name,color,rough=.65,metal=0,bump=.0):
    m=bpy.data.materials.new(PREFIX+name);m.use_nodes=True;m.diffuse_color=(*color,1)
    nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=metal
    tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.1;noise.inputs['Detail'].default_value=2
    nt.links.new(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(*(v*.83 for v in color),1)
    ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*(min(1,v*1.08) for v in color),1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    r=nt.nodes.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=max(.1,rough-.09);r.inputs['To Max'].default_value=min(.98,rough+.09)
    nt.links.new(noise.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],bs.inputs['Roughness'])
    if bump:
        f=nt.nodes.new('ShaderNodeTexNoise');f.inputs['Scale'].default_value=95 if 'rubber' in name else 180;f.inputs['Detail'].default_value=2
        nt.links.new(tc.outputs['Object'],f.inputs['Vector']);bn=nt.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.2;bn.inputs['Distance'].default_value=bump
        nt.links.new(f.outputs['Fac'],bn.inputs['Height']);nt.links.new(bn.outputs[0],bs.inputs['Normal'])
    return m
def palette():
    return {k:material(k,*v) for k,v in {
      'cream':((.48,.46,.39),.78,0,.0005),'slate':((.075,.091,.105),.66,.12,.0002),
      'oxide':((.21,.064,.035),.59,.18,.0002),'enamel':((.38,.39,.36),.53,.24,.0002),
      'replacement':((.24,.27,.28),.62,.18,.0003),'steel':((.16,.17,.18),.4,.82,.0001),
      'zinc':((.29,.3,.31),.5,.72,.0002),'copper':((.31,.115,.045),.42,.82,.0001),
      'rubber':((.016,.02,.023),.87,0,.0004),'ceramic':((.63,.61,.51),.33,0,.00005),
      'ochre':((.43,.23,.055),.58,.14,.0002),'paper':((.64,.59,.46),.92,0,.0001),
      'ink':((.028,.037,.045),.83,0,0),'cloth':((.2,.22,.18),.94,0,.001),
      'redrubber':((.25,.031,.017),.82,0,.0003),'wood':((.11,.052,.025),.71,0,.0005),
      'coffee':((.029,.009,.003),.31,0,0),'floor':((.23,.235,.216),.83,0,.0006),
      'route':((.32,.295,.244),.77,0,.0005),'glass':((.034,.068,.075),.27,.14,0)
    }.items()}
def add(name,build):
    b=B();build(b)
    # Closed revolved profiles meet at coincident first/last rings; weld that seam.
    bmesh.ops.remove_doubles(b.bm,verts=list(b.bm.verts),dist=.0000001)
    o=b.build(PREFIX+name,floor_normalize=False);COLL.objects.link(o)
    if ASSEMBLY:o['cs_assembly']=ASSEMBLY.name
    return o
def box(name,pos,size,m,bevel=.003,rot=None):
    o=add(name,lambda b:b.box(size,pos,m,bevel=bevel,rot=rot))
    # Planar manufactured faces stay planar; tiny chamfers are dimensional.
    for p in o.data.polygons:p.use_smooth=False
    return o
def cyl(name,a,c,r,m,seg=24):
    a,c=Vector(a),Vector(c);d=c-a;rot=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix()
    o=add(name,lambda b:b.lathe([(0,0),(r,0),(r,d.length),(0,d.length)],a,m,seg=seg,rot=rot))
    for p in o.data.polygons:
        if abs(p.normal.dot(d.normalized()))>.99:p.use_smooth=False
    return o
def tube(name,path,r,m):return add(name,lambda b:b.tube(path,r,m,seg=12))
def lathe(name,pos,profile,m,seg=32,rot=None):return add(name,lambda b:b.lathe(profile,pos,m,seg=seg,rot=rot))
def text(name,body,pos,size,m,normal='X'):
    d=bpy.data.curves.new(PREFIX+name,'FONT');d.body=body;d.size=size;d.extrude=.00035;d.space_character=1.05
    o=bpy.data.objects.new(d.name,d);COLL.objects.link(o);o.location=pos
    if normal=='X':o.rotation_euler=(math.pi/2,0,math.pi/2)
    elif normal=='-X':o.rotation_euler=(math.pi/2,0,-math.pi/2)
    elif normal=='Y':o.rotation_euler=(math.pi/2,0,math.pi)
    elif normal=='-Y':o.rotation_euler=(math.pi/2,0,0)
    d.materials.append(m)
    if ASSEMBLY:o['cs_assembly']=ASSEMBLY.name
    return o
def root(name,target,anchors,direction='WORLD_-Z'):
    global ASSEMBLY
    o=bpy.data.objects.new(PREFIX+name,None);COLL.objects.link(o)
    o['cs_support_target']=target;o['cs_support_direction']=direction;o['cs_support_required']=True
    o['cs_support_anchors']=anchors;ASSEMBLY=o
    return o
def bolt(name,p,axis,m,r=.013):
    p=Vector(p);axis=Vector(axis)
    cyl(name+' washer',p,p+axis*.003,r*1.55,m)
    cyl(name+' hex head',p+axis*.003,p+axis*.015,r,m,6)
def ring(name,x,y,z,w,h,thick,depth,m):
    # Annular frame with actual empty center in a wall facing +X.
    def draw(b):
        rows=[]
        for xx in [x-depth/2,x+depth/2]:
            for ww,hh in [(w,h),(w-2*thick,h-2*thick)]:
                rows.append([b.bm.verts.new((xx,y+sy*ww/2,z+sz*hh/2)) for sy,sz in [(-1,-1),(1,-1),(1,1),(-1,1)]])
        for i in range(4):
            j=(i+1)%4
            for r1,r2 in [(0,1),(2,3),(0,2),(1,3)]:
                f=b.bm.faces.new((rows[r1][i],rows[r1][j],rows[r2][j],rows[r2][i]));f.material_index=b._idx(m)
        bmesh.ops.recalc_face_normals(b.bm,faces=list(b.bm.faces))
        bmesh.ops.bevel(b.bm,geom=list(b.bm.edges),offset=min(.002,thick*.18,depth*.18),segments=2,affect='EDGES',clamp_overlap=True)
    return add(name,draw)
def lamp(name,position,target,power,color,size=.35):
    d=bpy.data.lights.new(PREFIX+name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(d.name,d);COLL.objects.link(o);o.location=position;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    if ASSEMBLY:o['cs_assembly']=ASSEMBLY.name
    return o
def remove_members(prefixes):
    for o in list(bpy.data.objects):
        if any(o.name.startswith(x) for x in prefixes):bpy.data.objects.remove(o,do_unlink=True)
