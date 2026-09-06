"""Authored material separation and practical-light hierarchy. Runs in the source build.

Sources: Poly Haven CC0; see tactile_manifest.json. Maps remain unmodified.
This module intentionally never loads a previous .blend.
"""
import bpy, bmesh, math
from mathutils import Vector
import worn_surfaces as w

def clean(mat):
    n=mat.node_tree.nodes; n.clear(); l=mat.node_tree.links
    p=n.new('ShaderNodeBsdfPrincipled');p.name='Principled BSDF'
    out=n.new('ShaderNodeOutputMaterial');l.new(p.outputs['BSDF'],out.inputs['Surface'])
    return n,l,p

def coords(n,l,scale=1,generated=False):
    c=n.new('ShaderNodeTexCoord' if generated else 'ShaderNodeNewGeometry')
    v=c.outputs['Generated' if generated else 'Position']
    s=n.new('ShaderNodeVectorMath');s.operation='SCALE';s.inputs[3].default_value=scale
    l.new(v,s.inputs[0]);return s.outputs[0]

def flat(n,l,v,asset,kind):
    path=w.TEX/(asset+'_'+kind+'_2k.jpg')
    im=bpy.data.images.get(path.name) or bpy.data.images.load(str(path),check_existing=True)
    if kind!='diff':im.colorspace_settings.name='Non-Color'
    im.pack();im.filepath='//../assets/textures/cc0/'+path.name
    node=n.new('ShaderNodeTexImage');node.image=im;node.label='CC0 / '+asset+' / '+kind
    l.new(v,node.inputs['Vector']);return node.outputs['Color']

def remap(n,l,s,lo,hi,imin=0,imax=1):
    r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=imin;r.inputs['From Max'].default_value=imax
    r.inputs['To Min'].default_value=lo;r.inputs['To Max'].default_value=hi;l.new(s,r.inputs[0]);return r.outputs[0]

def mix(n,l,a,b,factor,kind='MIX'):
    m=n.new('ShaderNodeMixRGB');m.blend_type=kind
    for i,value in enumerate((factor,a,b)):
        if hasattr(value,'node'):l.new(value,m.inputs[i])
        else:m.inputs[i].default_value=value
    return m.outputs[0]

def relief(n,l,p,h,strength,distance,old=None):
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=distance
    l.new(h,b.inputs['Height'])
    if old:l.new(old,b.inputs['Normal'])
    l.new(b.outputs[0],p.inputs['Normal']);return b.outputs[0]

def wall_material(mat,colour,coated=False):
    n,l,p=clean(mat);v=coords(n,l,.5)
    d=w.bitmap(n,l,v,'painted_plaster_wall','diff')
    h=w.bitmap(n,l,v,'painted_plaster_wall','disp')
    r=w.bitmap(n,l,v,'painted_plaster_wall','rough')
    bw=n.new('ShaderNodeRGBToBW');l.new(d,bw.inputs[0])
    c=w.ramp(n,l,bw.outputs[0],[tuple(x*.54 for x in colour),tuple(x*1.1 for x in colour)],(.12,.52))
    l.new(c,p.inputs['Base Color'])
    l.new(remap(n,l,r,.58 if coated else .80,.79 if coated else .97),p.inputs['Roughness'])
    p.inputs['Specular IOR Level'].default_value=.38 if coated else .3
    relief(n,l,p,h,.48,.014 if coated else .033)
    mat.diffuse_color=(*colour,1);mat['look_pass']='Trowelled mineral / separate washable coating'

def floor_material(mat,index):
    n,l,p=clean(mat);v=coords(n,l,1/3)
    d=flat(n,l,v,'concrete_floor_worn_001','diff');h=flat(n,l,v,'concrete_floor_worn_001','disp');r=flat(n,l,v,'concrete_floor_worn_001','rough')
    bw=n.new('ShaderNodeRGBToBW');l.new(d,bw.inputs[0])
    factor=.86+index*.063
    c=w.ramp(n,l,bw.outputs[0],[(.07*factor,.082*factor,.077*factor),(.24*factor,.265*factor,.24*factor)],(.024,.165))
    l.new(c,p.inputs['Base Color'])
    # Dry sealed aggregate: route burnishing catches a broad highlight, corners stay chalkier.
    l.new(remap(n,l,r,.48,.82),p.inputs['Roughness']);p.inputs['Specular IOR Level'].default_value=.42
    relief(n,l,p,h,.62,.034)
    mat.diffuse_color=(.19*factor,.21*factor,.19*factor,1);mat['look_pass']='Worn sealed concrete / 3m scan / dry roughness breakup'

def timber(mat):
    n,l,p=clean(mat);v=coords(n,l,1,True)
    d=flat(n,l,v,'wood_table_worn','diff');h=flat(n,l,v,'wood_table_worn','disp');r=flat(n,l,v,'wood_table_worn','rough')
    c=mix(n,l,d,(.32,.21,.115,1),.35);l.new(c,p.inputs['Base Color'])
    l.new(remap(n,l,r,.38,.76),p.inputs['Roughness']);p.inputs['Specular IOR Level'].default_value=.38
    p.inputs['Coat Weight'].default_value=.14;p.inputs['Coat Roughness'].default_value=.45
    relief(n,l,p,h,.35,.005)
    mat['look_pass']='Worn warm timber / restrained residual finish'

def painted(mat,roughness):
    n,l,p=clean(mat);v=coords(n,l,1,True)
    broad=w.noise(n,l,v,4.3,2);fine=w.noise(n,l,v,115,2)
    c=mat.diffuse_color[:3]
    colour=w.ramp(n,l,broad,[tuple(x*.72 for x in c),tuple(x*1.12 for x in c)],(.18,.82))
    l.new(colour,p.inputs['Base Color']);l.new(remap(n,l,broad,*roughness),p.inputs['Roughness'])
    p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.46
    relief(n,l,p,fine,.16,.0006)
    mat['look_pass']='Painted steel / low orange peel, broad finish wear'

def tread(k):
    mat=k.material('worn_safety_tread',(.11,.135,.12),.6,.85)
    n,l,p=clean(mat);v=coords(n,l,1.4)
    d=w.bitmap(n,l,v,'metal_plate','diff');h=w.bitmap(n,l,v,'metal_plate','disp');r=w.bitmap(n,l,v,'metal_plate','rough')
    l.new(mix(n,l,d,(.16,.19,.18,1),.66),p.inputs['Base Color'])
    p.inputs['Metallic'].default_value=.8;l.new(remap(n,l,r,.40,.77),p.inputs['Roughness'])
    relief(n,l,p,h,.7,.007)
    mat['look_pass']='Localized worn tread steel, thresholds only'

def dent(o):
    # Local sheet deflection, never move seams, hinges or support corners.
    bm=bmesh.new();bm.from_mesh(o.data)
    if len(bm.verts)>64:bm.free();return
    low=[min(v.co[i] for v in bm.verts) for i in range(3)];high=[max(v.co[i] for v in bm.verts) for i in range(3)]
    thin=min(range(3),key=lambda i:high[i]-low[i]);axes=[i for i in range(3) if i!=thin]
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=7,use_grid_fill=True)
    for v in bm.verts:
        u=(v.co[axes[0]]-low[axes[0]])/(high[axes[0]]-low[axes[0]])
        z=(v.co[axes[1]]-low[axes[1]])/(high[axes[1]]-low[axes[1]])
        envelope=math.sin(math.pi*u)*math.sin(math.pi*z)
        v.co[thin]+=.004*envelope*math.sin(u*6.2+z*3.1)
    bm.to_mesh(o.data);bm.free();o['look_pass']='4mm local sheet-metal deflection, border retained'

def lighting(scope):
    s=bpy.context.scene;s.world.node_tree.nodes['Background'].inputs[1].default_value=.025
    s.view_settings.exposure=.3
    # Same fixture positions. Real reflector spreads create pools instead of blanket fill.
    specifications={
        'HALL_light_00':(62,(1,.87,.69),85),
        'HALL_light_01':(46,(.93,.96,1),95),
        'HALL_light_02':(108,(.78,.88,1),145),
        'BRIEFING_light_00':(122,(1,.87,.70),108),
        'BRIEFING_light_01':(26,(.90,.94,1),100),
        'LOCKER_light_00':(172,(1,.91,.78),108),
        'LOCKER_light_01':(102,(.87,.94,1),100),
        'LOCKER_light_02':(39,(.90,.95,1),90),
        'SERVICE_light':(85,(.77,.87,1),100),
        'SLICE_practical':(115,(1,.91,.79),104),
    }
    for o in bpy.data.objects:
        if o.type!='LIGHT':continue
        key=o.name.removesuffix('_photometric')
        if key in specifications:
            power,colour,spread=specifications[key];o.data.energy=power;o.data.color=colour;o.data.spread=math.radians(spread)
            o['look_pass']='Practical reflector falloff / spatial lighting hierarchy'
    # Diffuser emission must not bypass the authored reflector pattern in Cycles.
    for m in bpy.data.materials:
        if m.name=='lamp':m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=1.1
    s['lighting_revision']='Tactile practical hierarchy 01'

def apply(k,scope):
    wall_material(k.M['wall'],(.50,.465,.385))
    wall_material(k.M['dado'],(.145,.215,.187),True)
    for i in range(5):floor_material(k.M['floor%d'%i],i)
    for key in ['paint','pale','yellow','red','blue']:painted(k.M[key],(.37,.64))
    timber(k.M['wood']);tread(k)
    # Visible metal remains distinct from paint; no chrome and no room-wide scratch pass.
    for key in ['steel','darksteel']:
        p=k.M[key].node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=1
    for o in list(bpy.data.objects):
        if o.type!='MESH':continue
        if any(t in o.name for t in ['_threshold','_kickplate']) and 'rubbed_paint' not in o.name and o.data.materials and o.data.materials[0].name=='steel':
            o.data.materials.clear();o.data.materials.append(k.M['worn_safety_tread'])
        if any(t in o.name for t in ['_back_panel','_rear_access','_service_lid']):dent(o)
    lighting(scope)
    bpy.context.view_layer.update()
    s=bpy.context.scene;s['material_revision']='Tactile CC0 01';s['source_asset_manifest']='//../assets/textures/tactile_manifest.json'
