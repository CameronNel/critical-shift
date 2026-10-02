"""Geometry/surfacing helpers for the owned fuel-corridor overhaul.

Reuses the repository's spawn bmesh construction library; no asset service or
external runtime dependency. Local wall assets face -Y, Z is up. Dimensions are m.
"""
from pathlib import Path
import sys, math, json
import bpy, bmesh
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'sections/spawn-room/blender'))
from cozy_geo import B

MATERIALS = {}
COLLECTIONS = {}

def linear(hexcode):
    h=hexcode.lstrip('#')
    a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)

def surface(name, color, rough=.65, metal=0, bump=.0007, scale=3.0,
            variation=.06, fiber=None, transmission=0, emission=0):
    """Meter-space broad tone and roughness; tiny material-specific relief.

    This is not a universal scratch layer. Handled damage is authored geometry.
    Vector space is world position so differently sized parts keep physical scale.
    """
    if name in MATERIALS:return MATERIALS[name]
    m=bpy.data.materials.new('FC | '+name);m.use_nodes=True
    nodes=m.node_tree.nodes;links=m.node_tree.links
    p=nodes.get('Principled BSDF');rgb=linear(color)
    m.diffuse_color=(*rgb,1);p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=transmission
    if transmission:p.inputs['IOR'].default_value=1.46
    if emission:
        p.inputs['Emission Color'].default_value=(*rgb,1)
        p.inputs['Emission Strength'].default_value=emission
    coord=nodes.new('ShaderNodeNewGeometry');coord.location=(-800,0)
    coarse=nodes.new('ShaderNodeTexNoise');coarse.inputs['Scale'].default_value=scale
    coarse.inputs['Detail'].default_value=1.2;coarse.location=(-600,120)
    links.new(coord.outputs['Position'],coarse.inputs['Vector'])
    tone=nodes.new('ShaderNodeValToRGB');tone.location=(-370,220)
    tone.color_ramp.elements[0].position=.18
    tone.color_ramp.elements[0].color=(*(v*(1-variation) for v in rgb),1)
    tone.color_ramp.elements[1].position=.82
    tone.color_ramp.elements[1].color=(*(min(1,v*(1+variation)) for v in rgb),1)
    links.new(coarse.outputs['Fac'],tone.inputs[0]);links.new(tone.outputs['Color'],p.inputs['Base Color'])
    remap=nodes.new('ShaderNodeMapRange');remap.location=(-100,40)
    remap.inputs['From Min'].default_value=.1;remap.inputs['From Max'].default_value=.9
    remap.inputs['To Min'].default_value=max(.025,rough-.07)
    remap.inputs['To Max'].default_value=min(1,rough+.07)
    links.new(coarse.outputs['Fac'],remap.inputs['Value']);links.new(remap.outputs['Result'],p.inputs['Roughness'])
    if bump:
        fine=nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=155 if metal else 90
        fine.inputs['Detail'].default_value=2;fine.location=(-570,-240)
        if fiber:
            vec=nodes.new('ShaderNodeVectorMath');vec.operation='MULTIPLY'
            vec.inputs[1].default_value=fiber;links.new(coord.outputs['Position'],vec.inputs[0])
            links.new(vec.outputs[0],fine.inputs['Vector'])
        else:links.new(coord.outputs['Position'],fine.inputs['Vector'])
        bm=nodes.new('ShaderNodeBump');bm.inputs['Strength'].default_value=.22
        bm.inputs['Distance'].default_value=bump;bm.location=(0,-170)
        links.new(fine.outputs['Fac'],bm.inputs['Height']);links.new(bm.outputs[0],p.inputs['Normal'])
    MATERIALS[name]=m
    return m

def palette():
    data={
    'mineral':('#ADA89D',.88,0,.0012,1.0,.12),
    'plaster':('#C8C1B1',.88,0,.0010,1.5,.06),
    'patch':('#B9B3A2',.9,0,.0010,1.4,.08),
    'cool plaster':('#AABAB9',.88,0,.0010,1.5,.08),
    'warm plaster':('#C0AF99',.89,0,.0010,1.4,.08),
    'repaired blue enamel':('#697A85',.72,.08,.0004,3,.10),
    'navy enamel':('#394655',.62,.12,.00045,3,.08),
    'ink enamel':('#272E39',.65,.18,.00035,4,.05),
    'ochre enamel':('#BE863E',.62,.08,.0004,3,.08),
    'oxide enamel':('#945642',.67,.08,.00045,3,.07),
    'warm enamel':('#D1C7AD',.6,.1,.0003,4,.06),
    'replacement enamel':('#86919A',.65,.12,.0003,3,.07),
    'steel':('#7A8389',.42,.86,.00015,3,.08),
    'dark steel':('#444C54',.5,.78,.0002,3,.1),
    'brass':('#A08346',.45,.77,.00015,4,.09),
    'rubber':('#25272A',.94,0,.0008,8,.07),
    'floor':('#747C7F',.82,0,.0006,1,.1),
    'floor border':('#4B5968',.83,0,.0006,1,.12),
    'floor repair':('#838C8F',.86,0,.0006,1,.09),
    'bed':('#3C4043',.96,0,.0005,2,.05),
    'paper':('#D8CDB8',.97,0,.00025,12,.06),
    'canvas':('#ABA594',.98,0,.0006,8,.1),
    'cotton':('#657A91',.98,0,.00045,12,.08),
    'leather':('#625548',.89,0,.0006,5,.12),
    'wood':('#9B7650',.75,0,.0005,5,.16),
    'red':('#A84C36',.67,.08,.00045,3,.1),
    'ink':('#282B2C',.94,0,.0001,9,.025),
    'white ink':('#D8D3C2',.92,0,.0001,9,.035),
    'chip':('#88887B',.78,.36,.0003,9,.1),
    'coffee':('#35281C',.29,0,.0001,8,.08),
    }
    for k,a in data.items():surface(k,*a,fiber=(1,1,18) if k=='wood' else None)
    surface('glass','#D7E4E3',.12,0,0,variation=.015,transmission=.96)
    surface('warm diffuser','#F4DCB9',.56,0,.00005,variation=.025,emission=2)
    surface('cool diffuser','#D6E2E9',.56,0,.00005,variation=.025,emission=1.6)
    surface('amber','#E0A342',.37,0,.00005,variation=.03,emission=.8)
    surface('wood dark','#684A32',.87,0,.0004,4,.08)
    packed_reference_textures()
    return MATERIALS

def packed_reference_textures():
    """Reuse only the CC0 textures already packed in the spawn reference.

    Physical UVs, moderate value mixing and low relief keep the stylized target.
    Images are local copies; the reference file and its materials are not edited.
    """
    source=ROOT/'sections/facility-assembly/sources/spawn-room/module.blend'
    names=['wood_table_worn_diff_2k.jpg','wood_table_worn_disp_2k.jpg','wood_table_worn_rough_2k.jpg',
           'painted_plaster_wall_diff_2k.jpg','painted_plaster_wall_disp_2k.jpg','painted_plaster_wall_rough_2k.jpg',
           'metal_plate_diff_2k.jpg','metal_plate_disp_2k.jpg','metal_plate_rough_2k.jpg']
    with bpy.data.libraries.load(str(source),link=False) as (a,b):
        b.images=[n for n in names if n in a.images]
    images={i.name:i for i in b.images if i}
    for family,stem,strength,relief in [('wood','wood_table_worn',.78,.0015),('plaster','painted_plaster_wall',.42,.0018),
                                      ('cool plaster','painted_plaster_wall',.35,.0016),('warm plaster','painted_plaster_wall',.35,.0016),
                                      ('patch','painted_plaster_wall',.20,.0013),('steel','metal_plate',.16,.0002),
                                      ('dark steel','metal_plate',.13,.0002),('navy enamel','metal_plate',.12,.00015),
                                      ('warm enamel','metal_plate',.09,.00015),('oxide enamel','metal_plate',.10,.00015)]:
        m=mat(family);nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
        color=images.get(stem+'_diff_2k.jpg');height=images.get(stem+'_disp_2k.jpg');rough=images.get(stem+'_rough_2k.jpg')
        if not color:continue
        tc=nodes.new('ShaderNodeTexCoord');tc.name='Physical metre UV'
        mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs['Scale'].default_value=.7 if family=='wood' else .6
        links.new(tc.outputs['UV'],mapping.inputs[0])
        tex=nodes.new('ShaderNodeTexImage');tex.image=color;tex.name='Packed reference albedo';links.new(mapping.outputs[0],tex.inputs['Vector'])
        prior=p.inputs['Base Color'].links[0].from_socket
        mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=strength
        links.new(prior,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],p.inputs['Base Color'])
        if height:
            height.colorspace_settings.name='Non-Color'
            ht=nodes.new('ShaderNodeTexImage');ht.image=height;links.new(mapping.outputs[0],ht.inputs[0])
            bu=nodes.new('ShaderNodeBump');bu.inputs['Distance'].default_value=relief;bu.inputs['Strength'].default_value=.28
            links.new(ht.outputs['Color'],bu.inputs['Height']);links.new(bu.outputs[0],p.inputs['Normal'])
        if rough:
            rough.colorspace_settings.name='Non-Color'
            rt=nodes.new('ShaderNodeTexImage');rt.image=rough;links.new(mapping.outputs[0],rt.inputs[0])
            base_rough=p.inputs['Roughness'].default_value
            mr=nodes.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=max(.025,base_rough-.10)
            mr.inputs['To Max'].default_value=min(.98,base_rough+.08)
            links.new(rt.outputs['Color'],mr.inputs['Value']);links.new(mr.outputs['Result'],p.inputs['Roughness'])

def mat(name):return MATERIALS[name]

def coll(name):
    if name not in COLLECTIONS:
        c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
        mod=bpy.data.collections['MODULE_fuel-corridor']
        if c.name not in mod.children:mod.children.link(c)
        COLLECTIONS[name]=c
    return COLLECTIONS[name]

def transform(pos=(0,0,0), angle=0, normal=None):
    if normal is not None:
        n=Vector(normal);n.normalize();u=Vector((-n.y,n.x,0));v=-n
        r=Matrix((u,v,Vector((0,0,1)))).transposed().to_4x4()
    else:r=Matrix.Rotation(angle,4,'Z')
    r.translation=Vector(pos)
    return r

def support(o, targets, anchors, direction, kind='wall'):
    o['support_anchors']=json.dumps([list(a) for a in anchors])
    o['support_targets']=json.dumps(targets)
    o['support_direction']=direction
    o['support_max_gap']=.005;o['support_max_penetration']=.002
    o['support_angle_tolerance']=12.0
    o['fc_support_kind']=kind

def add(b,name,collection='FC | Equipment',pos=(0,0,0),angle=0,normal=None,
        target=None,anchors=None,direction=None,kind='wall',family=None,parent=None):
    o=b.build('FC | '+name,floor_normalize=False)
    coll(collection).objects.link(o);o.matrix_world=transform(pos,angle,normal)
    o['fc_revision']='overhaul-20261001';o['fc_asset_family']=family or name
    o['collision_handoff']='static_evaluated_geometry'
    # Weighted normals keep broad sheet faces planar and narrow cast edges soft.
    m=o.modifiers.new('Fabrication normals','WEIGHTED_NORMAL');m.keep_sharp=True;m.weight=50
    if target:
        dirs=direction or ((0,1,0) if kind=='wall' else (0,0,-1))
        v=o.matrix_world.to_3x3()@Vector(dirs)
        a=[o.matrix_world@Vector(p) for p in anchors]
        support(o,[target]*len(a),a,list(v),kind)
    elif parent:
        o['fc_attachment_to']=parent
        p=bpy.data.objects.get(parent)
        if p:
            world=o.matrix_world.copy();o.parent=p;o.matrix_world=world
    else:o['fc_support_kind']='structural-core'
    # Explicit metre-space UVs for editable source and future authored map baking.
    uv=o.data.uv_layers.new(name='UVMap')
    for p in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]],co[axes[1]])
    return o

def polygon(b, pts, depth, material, pos=(0,0,0), rot=None,bevel=0):
    before=set(b.bm.verts);b.prism(pts,depth,material)
    vs=[v for v in b.bm.verts if v not in before]
    if bevel:
        edges=list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(b.bm,geom=edges,offset=min(bevel,depth*.3),segments=3,affect='EDGES')
        b._fin([v for v in b.bm.verts if v not in before],material,True)
        vs=[v for v in b.bm.verts if v not in before]
    b._xf(vs,rot,pos)

def merge(b,other,pos=(0,0,0),rot=None):
    """Append an authored component and explicitly remap its material slots."""
    bm=other.bm.copy();mapping={i:b._idx(m) for i,m in enumerate(other.mats)}
    for f in bm.faces:f.material_index=mapping[f.material_index]
    for v in bm.verts:v.co=(rot@v.co if rot is not None else v.co)+Vector(pos)
    mesh=bpy.data.meshes.new('FC temporary component');bm.to_mesh(mesh);bm.free()
    b.bm.from_mesh(mesh);bpy.data.meshes.remove(mesh);other.bm.free()

def ring(b,r,thickness,pos,material,axis='Z',seg=32):
    rot={'Z':None,'Y':Matrix.Rotation(math.pi/2,3,'X'),'X':Matrix.Rotation(math.pi/2,3,'Y'),'NX':Matrix.Rotation(-math.pi/2,3,'Y')}[axis]
    b.lathe([(r-thickness,0),(r,0),(r,thickness),(r-thickness,thickness),(r-thickness,0)],pos,material,seg=seg,rot=rot)

def bolt(b,pos,r=.009,axis='Y',material='steel'):
    rot={'Z':None,'Y':Matrix.Rotation(math.pi/2,3,'X'),'X':Matrix.Rotation(math.pi/2,3,'Y'),'NX':Matrix.Rotation(-math.pi/2,3,'Y')}[axis]
    profile=[(0,0),(r*1.25,0),(r*1.25,r*.25),(r,r*.25),(r,r*.8),
             (r*.82,r*.92),(r*.39,r*.92),(r*.39,r*.48),(0,r*.48)]
    b.lathe(profile,pos,mat(material),seg=12,rot=rot)

def frame(b,w,h,t,depth,y,z,material,r=.035):
    """Hollow, capped rounded rectangular frame in X/Z; its cavity stays open."""
    def loop(w,h,r):
        points=[]
        for cx,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),
                            (-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
            for i in range(4):
                a=math.radians(start+i*30)
                points.append((cx+r*math.cos(a),cz+r*math.sin(a)))
        return points
    outer=loop(w,h,min(r,min(w,h)*.2));inner=loop(w-2*t,h-2*t,max(.003,r-t))
    rows=[]
    for yy in [y-depth/2,y+depth/2]:
        rows.append(([b.bm.verts.new((x,yy,zz+z)) for x,zz in outer],
                     [b.bm.verts.new((x,yy,zz+z)) for x,zz in inner]))
    for i in range(16):
        j=(i+1)%16
        quads=[(rows[0][0][i],rows[0][0][j],rows[1][0][j],rows[1][0][i]),
               (rows[0][1][j],rows[0][1][i],rows[1][1][i],rows[1][1][j])]
        for row in rows:quads.append((row[0][i],row[1][i],row[1][j],row[0][j]))
        for q in quads:b.bm.faces.new(q)
    b._fin([v for row in rows for sub in row for v in sub],material,False)

def circular_aperture_sheet(b,w,h,y,depth,hole_z,r,material):
    """A pressure-leaf sheet with a genuine through aperture and capped returns."""
    bottom=.056;top=bottom+h
    angles=[i*2*math.pi/48 for i in range(48)]
    angles += [math.atan2(z-hole_z,x)%(2*math.pi) for x in [-w/2,w/2] for z in [bottom,top]]
    angles=sorted(set(round(a,9) for a in angles));rows=[]
    for yy in [y-depth/2,y+depth/2]:
        outer=[];inner=[]
        for a in angles:
            dx,dz=math.cos(a),math.sin(a);ts=[]
            if abs(dx)>1e-7:ts.append((w/2 if dx>0 else -w/2)/dx)
            if abs(dz)>1e-7:ts.append(((top if dz>0 else bottom)-hole_z)/dz)
            t=min(ts)
            outer.append(b.bm.verts.new((dx*t,yy,hole_z+dz*t)))
            inner.append(b.bm.verts.new((dx*r,yy,hole_z+dz*r)))
        rows.append((outer,inner))
    for i in range(len(angles)):
        j=(i+1)%len(angles)
        for outer,inner in rows:b.bm.faces.new((outer[i],outer[j],inner[j],inner[i]))
        b.bm.faces.new((rows[0][0][i],rows[1][0][i],rows[1][0][j],rows[0][0][j]))
        b.bm.faces.new((rows[0][1][i],rows[0][1][j],rows[1][1][j],rows[1][1][i]))
    b._fin([v for row in rows for loop in row for v in loop],material,False)

def channel(b,w,d,h,pos,material,th=.006):
    """An open C section; folded sides, never a solid box with painted lines."""
    x,y,z=pos
    b.box((w,th,h),(x,y+d/2-th/2,z),material,bevel=.0015)
    for s in [-1,1]:
        b.box((th,d,h),(x+s*(w/2-th/2),y,z),material,bevel=.0015)
        b.box((w*.18,th,h),(x+s*(w*.41),y-d/2+th/2,z),material,bevel=.0015)

def label(body,pos,size=.08,name=None,material='white ink',angle=0,normal=None,parent=None):
    cu=bpy.data.curves.new('FC | Type '+body[:24],'FONT');cu.body=body
    cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.0002;cu.bevel_depth=.00004
    cu.space_character=1.1
    font=ROOT/'sections/spawn-room/assets/fonts/DejaVuSans.ttf'
    if not font.exists():font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    if font.exists():
        loaded=next((f for f in bpy.data.fonts if Path(f.filepath).name=='DejaVuSans.ttf'),None) or bpy.data.fonts.load(str(font),check_existing=True);cu.font=loaded
    o=bpy.data.objects.new('FC | '+(name or 'Type '+body[:24]),cu);coll('FC | Lettering').objects.link(o)
    o.matrix_world=transform(pos,angle,normal)@Matrix.Rotation(math.pi/2,4,'X')
    cu.materials.append(mat(material));o['fc_revision']='overhaul-20261001'
    o['fc_asset_family']='screen-printed lettering';o['fc_attachment_to']=parent or 'painted substrate'
    p=bpy.data.objects.get(parent) if parent else None
    if p:
        world=o.matrix_world.copy();o.parent=p;o.matrix_world=world
    return o

def light(name,pos,target,energy,color,size=.7,shape='DISK',size_y=None,parent=None):
    d=bpy.data.lights.new('FC | '+name,'AREA');d.energy=energy;d.color=color;d.shape=shape;d.size=size
    if size_y is not None:d.size_y=size_y
    o=bpy.data.objects.new('FC | '+name,d);coll('FC | Practicals').objects.link(o)
    T=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_matrix().to_4x4()
    T.translation=Vector(pos);o.matrix_world=T
    o['fc_revision']='overhaul-20261001';o['fc_fixture']=parent or name;o['baked_plus_emissive_fixture']=True
    p=bpy.data.objects.get(parent) if parent else None
    if p:
        world=o.matrix_world.copy();o.parent=p;o.matrix_world=world
    return o

def rounded_path(points,steps=5):
    """Catmull-Rom curved bends; no hard kink in a flexible cable/handle."""
    p=[Vector(v) for v in points];out=[]
    for i in range(len(p)-1):
        p0=p[max(0,i-1)];p1=p[i];p2=p[i+1];p3=p[min(len(p)-1,i+2)]
        for j in range(steps):
            t=j/steps
            out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    out.append(p[-1]);return out

def wear(b, start, axis, length=.12, width=.003, seed=0):
    """Sparse physical exposed-metal nicks. No uniform damage on every edge."""
    import random
    r=random.Random(seed)
    for i in range(4):
        c=Vector(start)+Vector(axis)*(length*(i+.25+r.random()*.4)/4)
        b.box((length*.10,width,.0007),c,mat('chip'),bevel=.0002,rot=Matrix.Rotation(r.uniform(-.12,.12),3,'Z'))
