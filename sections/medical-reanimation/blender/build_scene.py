"""Original Medical / Reanimation. Primitive/material utilities adapted from our Electrical authoring source; no geometry imported. Blender 5.2; factory-empty, no external assets.

Build: blender --background --factory-startup --python build_scene.py -- --revision FINAL
Rendering is separate and MUST be invoked through the shared gpu_gate.py.
All dimensions are metres. Equipment is authored in local coordinates, front -Y.
"""
import bpy, math, json, argparse, sys, random, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
SOURCE_BYTES = Path(__file__).read_bytes()
P = argparse.ArgumentParser()
P.add_argument('--stage', choices=['slice','full'], default='full')
P.add_argument('--revision', default='R01')
P.add_argument('--output', default='')
args = P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
random.seed(1709)
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene
SC.unit_settings.system='METRIC'
SC.unit_settings.scale_length=1
SC['section']='medical-reanimation'
SC['revision']=args.revision
SC['stage']=args.stage
SC['source_sha256']=hashlib.sha256(SOURCE_BYTES).hexdigest()
COL={}
for name in ['Architecture','OCRU','Stations','Utilities','Props','Lighting','Cameras','Validation']:
    c=bpy.data.collections.new(name); SC.collection.children.link(c); COL[name]=c
current='Architecture'

def srgb(h):
    vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in vals)

def material(name, color, rough=.6, metal=0, variation=.035, bump=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*srgb(color),1); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*srgb(color),1)
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if variation or bump:
        tc=nt.nodes.new('ShaderNodeTexCoord'); n=nt.nodes.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value=2.8; n.inputs['Detail'].default_value=2.1; n.inputs['Roughness'].default_value=.55
        nt.links.new(tc.outputs['Generated'],n.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        rgb=srgb(color)
        ramp.color_ramp.elements[0].position=.15; ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[0].color=(*(v*(1-variation) for v in rgb),1)
        ramp.color_ramp.elements[1].color=(*(min(1,v*(1+variation)) for v in rgb),1)
        nt.links.new(n.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        rem=nt.nodes.new('ShaderNodeMapRange'); rem.inputs['From Min'].default_value=0; rem.inputs['From Max'].default_value=1
        rem.inputs['To Min'].default_value=max(.1,rough-.045); rem.inputs['To Max'].default_value=min(1,rough+.05)
        nt.links.new(n.outputs['Fac'],rem.inputs['Value']); nt.links.new(rem.outputs['Result'],bs.inputs['Roughness'])
        if bump:
            fine=nt.nodes.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=115; fine.inputs['Detail'].default_value=1.5
            nt.links.new(tc.outputs['Generated'],fine.inputs['Vector'])
            b=nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.22; b.inputs['Distance'].default_value=bump
            nt.links.new(fine.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
    return m

M={
 'wall':material('Warm precast concrete','B9B1A1',.90,variation=.04,bump=0),
 'floor':material('Dry ground concrete','777064',.92,variation=.07,bump=.001),
 'patch':material('Replacement concrete','A3A39A',.87,variation=.04,bump=.005),
 'joint':material('Elastomer joint filler','49433D',.95,variation=0),
 'paint':material('Oxide orange painted steel','BA7247',.72,.08,.065,0),
 'pale':material('Warm grey enamel','C7C0AE',.76,.08,.04,0),
 'bus':material('Galvanized bus casing','64615C',.73,.32,.035,0),
 'darkpaint':material('Structural warm graphite','343331',.79,.12,.025,0),
 'metal':material('Brushed galvanized steel','898781',.46,.85,.025,0),
 'edge':material('Exposed steel at contact wear','918D82',.55,.7,.015),
 'undercoat':material('Exposed ochre primer','8C7556',.82,.08,.07),
 'dirt':material('Dried contact grime','514B42',.94,0,.05),
 'rubber':material('Insulating rubber','252422',.91,0,.035,.002),
 'black':material('Switch housing phenolic','272625',.48,0,.035,.001),
 'yellow':material('Ochre safety enamel','CEAC57',.57,.08,.04),
 'orange':material('Standby ochre enamel','B56A3D',.75,.08,.045,0),
 'red':material('Isolator vermilion','A54833',.5,.12,.03),
 'copper':material('Bus copper - aged','8A5B3B',.46,.75,.035),
 'ceramic':material('Porcelain standoff','B7ADA0',.33,.05,.015),
 'paper':material('Work order paper','C6C1AD',.98,0,.02),
 'ink':material('Printed charcoal','262626',.93,0,0),
 'cloth':material('Cotton electrician rag','96846C',.98,0,.065,.002),
 'scuff':material('Localized contact abrasion','746B5C',.85,0,.02),
}
def emission(name, color, energy):
    m=material(name,color,.35,0,0); bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Emission Color'].default_value=(*srgb(color),1);bs.inputs['Emission Strength'].default_value=energy;return m
M['lamp']=emission('Warm prismatic diffuser','FFF0CB',4)
M['green']=emission('Energized pilot lens','E5BF70',.4)
M['amber']=emission('Transfer pilot lens','F5B359',1)
M['glass']=material('Instrument glass','545453',.34,.1,.01)
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.25

def link(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    COL[current].objects.link(o)
    return o

def finish(o,name,mat,parent=None,bevel=0):
    o.name=name; link(o)
    if mat:o.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    if parent:o.parent=parent
    if o.type=='MESH':
        o['assembly_member']=parent.name if parent else 'fixed-architecture'
        if bevel:
            mod=o.modifiers.new('Manufactured edge treatment','BEVEL');mod.width=bevel;mod.segments=2
            mod=o.modifiers.new('Face weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=30
    return o

def box(name,loc,dims,mat,parent=None,bevel=.004):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat,parent,bevel)

def cyl(name,loc,r,depth,mat,parent=None,axis='Z',vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc)
    o=bpy.context.object
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    elif axis=='X':o.rotation_euler[1]=math.pi/2
    finish(o,name,mat,parent,min(.002,depth*.12,r*.08) if r>.012 and depth>=.012 else 0)
    for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
    return o

def ring(name,loc,r,thick,mat,parent=None,axis='Z'):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,location=loc,major_radius=r,minor_radius=thick)
    o=bpy.context.object
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    elif axis=='X':o.rotation_euler[1]=math.pi/2
    finish(o,name,mat,parent,0)
    for p in o.data.polygons:p.use_smooth=True
    return o

def tube(name,points,r,mat,parent=None):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);COL[current].objects.link(o);o.data.materials.append(M[mat]);o.parent=parent
    o['assembly_member']=parent.name if parent else 'fixed-architecture';return o

def beam(name,a,b,w,mat,parent=None):
    mid=(Vector(a)+Vector(b))/2;o=box(name,mid,(w,w,(Vector(b)-Vector(a)).length),mat,parent, min(.003,w/5));o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler();return o

def text(name,body,loc,size,mat='paper',parent=None,rot=(math.pi/2,0,0),align='LEFT'):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.00015;cu.align_x=align
    o=bpy.data.objects.new(name,cu);COL[current].objects.link(o);o.location=loc;o.rotation_euler=rot;o.parent=parent;cu.materials.append(M[mat]);o['assembly_member']=parent.name if parent else 'fixed-architecture';return o

SUP=[]
def assembly(name,loc=(0,0,0),rot=0,support=None,anchors=None,direction=None,parent=None):
    o=bpy.data.objects.new(name,None);COL[current].objects.link(o);o.location=loc;o.rotation_euler[2]=rot
    o['assembly_root']=True
    if parent:o.parent=parent
    if support:
        o['support_target']=support; o['support_anchors']=json.dumps(anchors or [[0,0,0]])
        o['support_direction']=json.dumps(direction or ([0,0,1] if support.startswith('Ceiling') else [0,0,-1]))
        SUP.append(o)
    return o

def fasteners(name,xs,zs,y,parent,mat='metal',r=.012):
    for x in xs:
        for z in zs:
            cyl(name,(x,y,z),r,.008,mat,parent,'Y',8)
            box('Screwdriver slot',(x,y-.0045,z),(r*1.12,.001,r*.16),'black',parent,.0003)

def plaque(parent,body,loc,w=.48,h=.15,mat='darkpaint',size=.055):
    x,y,z=loc;box('Recessed engraved plate',(x,y,z),(w,.008,h),mat,parent,.002)
    text('Engraved '+body,body,(x-w*.43,y-.006,z-size*.35),size,'paper',parent)

def handle(parent,x,y,z,mat='metal',height=.19):
    for zz in [z-height/2,z+height/2]:cyl('Handle mounting boss',(x,y+.025,zz),.021,.07,mat,parent,'Y')
    beam('Formed pull grip',(x,y-.015,z-height/2),(x,y-.015,z+height/2),.026,mat,parent)

def gauge(parent,x,y,z,r=.115,label='A',needle=.4):
    cyl('Instrument cast bezel',(x,y,z),r,.065,'darkpaint',parent,'Y',48)
    ring('Rolled bezel rim',(x,y-.036,z),r*.90,r*.043,'metal',parent,'Y')
    cyl('Ivory instrument dial',(x,y-.035,z),r*.84,.003,'paper',parent,'Y',48)
    for i in range(9):
        a=math.radians(-125+i*31.25);p=(x+math.sin(a)*r*.72,y-.04,z+math.cos(a)*r*.72)
        q=(x+math.sin(a)*r*.61,y-.04,z+math.cos(a)*r*.61);beam('Calibration tick',p,q,.006,'ink',parent)
    a=needle;beam('Meter needle',(x,y-.046,z),(x+math.sin(a)*r*.63,y-.046,z+math.cos(a)*r*.63),.006,'red',parent)
    cyl('Needle pivot',(x,y-.049,z),.012,.007,'black',parent,'Y')
    text('Meter unit',label,(x,y-.051,z-r*.49),r*.28,'ink',parent,align='CENTER')
    for xx,zz in [(x-r*.71,z),(x+r*.71,z)]:cyl('Dial fixing pin',(xx,y-.043,zz),.003,.004,'metal',parent,'Y',8)

def rotary(parent,x,y,z,color='black',label=None):
    cyl('Selector escutcheon',(x,y,z),.065,.022,'metal',parent,'Y')
    box('Mechanical selector',(x,y-.035,z),(.025,.065,.098),color,parent,.006)
    if label:plaque(parent,label,(x,y+.004,z-.11),.21,.045,size=.018)

def wear(parent,x,y,z,w=.1):
    # Authored contact chips: sparse and planar, not universal noise.
    verts=[(x-w/2,y,z),(x-w*.1,y,z+.007),(x+w*.45,y,z+.004),(x+w/2,y,z-.003),(x+w*.17,y,z-.008),(x-w*.45,y,z-.004)]
    me=bpy.data.meshes.new('Contact chip');me.from_pydata(verts,[],[list(range(6))]);me.update();o=bpy.data.objects.new('Localized chipped paint',me);COL[current].objects.link(o);o.parent=parent;me.materials.append(M['edge']);o['assembly_member']=parent.name

def contact_scars(parent,x,y,z,w=.18,h=.07,seed=1):
    # Irregular, purpose-placed abrasion islands; no uniform edge-wear generator.
    rng=random.Random(seed)
    for k in range(12):
        xx=x+rng.uniform(-w/2,w/2);zz=z+rng.uniform(-h/2,h/2)
        rx=rng.uniform(.007,.036);rz=rng.uniform(.002,.009)
        vv=[(xx+math.cos(i*math.tau/7)*rx*rng.uniform(.7,1.15),y,zz+math.sin(i*math.tau/7)*rz*rng.uniform(.5,1.2)) for i in range(7)]
        me=bpy.data.meshes.new('Authored handling abrasion');me.from_pydata(vv,[],[list(range(7))]);me.update();ob=bpy.data.objects.new('Wear at repeatedly handled edge',me);COL[current].objects.link(ob);ob.parent=parent;me.materials.append(M['undercoat' if k%3 else 'edge']);ob['assembly_member']=parent.name

def folded_panel(parent,loc,w,h,mat='paint'):
    # Press-formed instrument panel with an inward sloping return and clipped corners.
    x,y,z=loc
    def outline(ww,hh,cc,yy):
        return [(x+xx,yy,z+zz) for xx,zz in [(-ww/2+cc,-hh/2),(ww/2-cc,-hh/2),(ww/2,-hh/2+cc),(ww/2,hh/2-cc),(ww/2-cc,hh/2),(-ww/2+cc,hh/2),(-ww/2,hh/2-cc),(-ww/2,-hh/2+cc)]]
    vv=outline(w,h,.045,y)+outline(w-.10,h-.10,.028,y+.037)
    ff=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]+[tuple(range(8,16))]
    me=bpy.data.meshes.new('Press formed recess');me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new('Folded instrument recess',me);COL[current].objects.link(o);o.parent=parent;me.materials.append(M[mat]);o['assembly_member']=parent.name
    so=o.modifiers.new('Sheet steel gauge','SOLIDIFY');so.thickness=.002



exec(compile((Path(__file__).parent/'medical_scene.py').read_text(),str(Path(__file__).parent/'medical_scene.py'),'exec'))
