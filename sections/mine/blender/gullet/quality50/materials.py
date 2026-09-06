"""Material changes for the user-approved worn, eerie Gullet revision.
Downloaded CC0 maps remain visible in the node graphs; no substitute renderer.
"""
import bpy, json
from pathlib import Path
TEX=Path(__file__).resolve().parents[3]/'assets'/'pbr'/'quality50'

def rgba(h):
    c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c)+(1.,)

def image(nodes,links,asset,role,coord):
    p=TEX/asset/(role+'.jpg')
    if not p.is_file():raise FileNotFoundError(p)
    im=bpy.data.images.load(str(p),check_existing=True)
    im.colorspace_settings.name='sRGB' if role=='color' else 'Non-Color'
    n=nodes.new('ShaderNodeTexImage');n.image=im;n.projection='BOX';n.projection_blend=.18;n.label=f'{asset} / {role} / CC0'
    links.new(coord,n.inputs['Vector']);im.pack()
    return n.outputs['Color']

def noise(nodes,links,coord,scale,detail=3):
    n=nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail;n.inputs['Roughness'].default_value=.72
    links.new(coord,n.inputs['Vector']);return n.outputs['Fac']

def ramp(nodes,links,source,stops):
    n=nodes.new('ShaderNodeValToRGB');n.color_ramp.elements.remove(n.color_ramp.elements[1])
    for i,(pos,col) in enumerate(stops):
        e=n.color_ramp.elements[0] if i==0 else n.color_ramp.elements.new(pos)
        e.position=pos;e.color=rgba(col) if isinstance(col,str) else col
    links.new(source,n.inputs['Fac']);return n.outputs['Color']

def basic(name,colour,roughness=.90,metallic=0.):
    m=bpy.data.materials.new('Q50_'+name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba(colour);p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic;p.inputs['Specular IOR Level'].default_value=.24
    m.diffuse_color=rgba(colour)
    return m,p

def rough_detail(m,p,scale=42,distance=.004):
    n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexCoord')
    v=noise(n,l,t.outputs['Object'],scale,4)
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.62;b.inputs['Distance'].default_value=distance;l.new(v,b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
    r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.78;r.inputs['To Max'].default_value=.98;l.new(v,r.inputs['Value']);l.new(r.outputs['Result'],p.inputs['Roughness'])
    return m

def make_wood(index=0,rotten=False):
    m,p=basic(('rotten_timber_' if rotten else 'cart_timber_')+str(index),'65533B' if rotten else '84613B')
    n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexCoord')
    mapn=n.new('ShaderNodeVectorMath');mapn.operation='MULTIPLY';mapn.inputs[1].default_value=(.52,3.5,3.5);l.new(t.outputs['Object'],mapn.inputs[0])
    shift=n.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(index*.291,index*.113,0);l.new(mapn.outputs['Vector'],shift.inputs[0]);coord=shift.outputs['Vector']
    col=image(n,l,'Wood060','color',coord)
    hs=n.new('ShaderNodeHueSaturation');hs.inputs['Saturation'].default_value=.62;hs.inputs['Value'].default_value=(.60 if rotten else .97)+index*.06;l.new(col,hs.inputs['Color'])
    coarse=noise(n,l,t.outputs['Object'],2.6,3)
    damp=ramp(n,l,coarse,[(.28,(0,0,0,1)),(.70,(.55,.55,.55,1))])
    mix=n.new('ShaderNodeMixRGB');l.new(damp,mix.inputs[0]);l.new(hs.outputs['Color'],mix.inputs[1]);mix.inputs[2].default_value=rgba('343329' if rotten else '4B4132');l.new(mix.outputs[0],p.inputs['Base Color'])
    height=image(n,l,'Wood060','height',coord);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.72;b.inputs['Distance'].default_value=.008;l.new(height,b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.80;r.inputs['To Max'].default_value=.98;l.new(image(n,l,'Wood060','roughness',coord),r.inputs['Value']);l.new(r.outputs[0],p.inputs['Roughness'])
    m['q50_surface']='actual rough timber grain, abrasion and moisture';m['license']='CC0-1.0';m['source']='https://ambientcg.com/view?id=Wood060'
    return m

def make_rust():
    m,p=basic('pitted_iron','554435',.87,.4);n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexCoord');coord=t.outputs['Object']
    col=image(n,l,'Metal026','color',coord)
    mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.48;mix.inputs[2].default_value=rgba('4E3729');l.new(col,mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
    b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.006;b.inputs['Strength'].default_value=.75;l.new(image(n,l,'Metal026','height',coord),b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    p.inputs['Roughness'].default_value=.86;m['q50_surface']='oxidized rough metal';m['license']='CC0-1.0';return m

def weather_existing(scene):
    used={slot.material for o in scene.objects if o.type=='MESH' and not o.get('csm_collision_only') for slot in o.material_slots if slot.material}
    records=[]
    for m in sorted(used,key=lambda x:x.name):
        if not m.use_nodes:continue
        n=m.node_tree.nodes;l=m.node_tree.links
        p=next((a for a in n if a.type=='BSDF_PRINCIPLED'),None)
        if p is None:continue
        lower=m.name.lower()
        if any(x in lower for x in ['emissive','water','scuff']):continue
        metal=any(x in lower for x in ['steel','slate','enamel','ochre','oxide_red','equipment','roof','paint_','casing'])
        stone=any(x in lower for x in ['stone','concrete','gravel','ground','rock','ore'])
        label='label_' in lower
        coord=n.new('ShaderNodeTexCoord');coord.label='Measured surface weathering'
        broad=noise(n,l,coord.outputs['Object'],3.8 if metal else .85,3)
        fine=noise(n,l,coord.outputs['Object'],155 if metal else 72,4)
        old=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
        mix=n.new('ShaderNodeMixRGB');mix.label='Localized corrosion' if metal else 'Moisture, dirt and mineral variation'
        if old:l.new(old,mix.inputs[1])
        else:mix.inputs[1].default_value=p.inputs['Base Color'].default_value
        if metal:
            mask=ramp(n,l,broad,[(.34,(.04,.04,.04,1)),(.55,(.12,.12,.12,1)),(.68,(.82,.82,.82,1))])
            rust=image(n,l,'Metal026','color',coord.outputs['Object'])
            tone=n.new('ShaderNodeMixRGB');tone.inputs[0].default_value=.55;tone.inputs[2].default_value=rgba('7A4527');l.new(rust,tone.inputs[1]);l.new(tone.outputs[0],mix.inputs[2]);l.new(mask,mix.inputs[0])
        else:
            mask=ramp(n,l,broad,[(.2,(.01,.01,.01,1)),(.7,((.22 if label else .40),)*3+(1,))])
            l.new(mask,mix.inputs[0]);mix.inputs[2].default_value=rgba('514938' if stone else '4F493B')
        l.new(mix.outputs[0],p.inputs['Base Color'])
        rg=n.new('ShaderNodeMapRange');rg.label='No uniform smooth coating';rg.inputs['To Min'].default_value=.76 if metal else .85;rg.inputs['To Max'].default_value=.97 if metal else .995;l.new(fine,rg.inputs['Value']);l.new(rg.outputs['Result'],p.inputs['Roughness'])
        p.inputs['Specular IOR Level'].default_value=.23
        if 'Coat Weight' in p.inputs:p.inputs['Coat Weight'].default_value=0
        prev=p.inputs['Normal'].links[0].from_socket if p.inputs['Normal'].is_linked else None
        bump=n.new('ShaderNodeBump');bump.label='Visible material-scale pitting';bump.inputs['Strength'].default_value=.65;bump.inputs['Distance'].default_value=.0045 if metal else (.001 if label else .009)
        l.new(fine,bump.inputs['Height'])
        if prev:l.new(prev,bump.inputs['Normal'])
        l.new(bump.outputs['Normal'],p.inputs['Normal'])
        if metal:
            pits=n.new('ShaderNodeBump');pits.inputs['Strength'].default_value=.55;pits.inputs['Distance'].default_value=.006
            l.new(image(n,l,'Metal026','height',coord.outputs['Object']),pits.inputs['Height']);l.new(bump.outputs['Normal'],pits.inputs['Normal']);l.new(pits.outputs['Normal'],p.inputs['Normal'])
        m['q50_weathered']=True;m['q50_roughness_min']=rg.inputs['To Min'].default_value;m['q50_rust']=metal
        records.append({'material':m.name,'roughness_min':m['q50_roughness_min'],'rust':metal,'bump':True})
    wood=[make_wood(i) for i in range(5)];rot=make_wood(0,True);iron=make_rust()
    for o in scene.objects:
        if o.type=='MESH' and not o.get('csm_collision_only'):
            for slot in o.material_slots:
                if slot.material and 'timber' in slot.material.name.lower() and not slot.material.name.startswith('Q50_'):
                    slot.link='OBJECT';slot.material=wood[sum(map(ord,o.name))%len(wood)]
    dirt,p=basic('crevice_dirt','29271F');rough_detail(dirt,p,48,.006)
    mineral,p=basic('mineral_deposits','746953');rough_detail(mineral,p,78,.009)
    web,p=basic('dusty_spider_silk','B7AE97',.96);p.inputs['Specular IOR Level'].default_value=.14
    stain,p=basic('damp_iron_bleed','553C29');rough_detail(stain,p,26,.0015)
    return {'wood':wood,'rot':rot,'iron':iron,'dirt':dirt,'web':web,'stain':stain,'mineral':mineral},records
