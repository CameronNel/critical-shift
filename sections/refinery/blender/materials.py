"""Controlled facility palette with material-specific roughness and bounded relief."""
import bpy, json, hashlib
from pathlib import Path
M={}
def make(name,c,rough=.7,metal=0,variation=.04,bump=0,scale=3):
    m=bpy.data.materials.new('REF_'+name);m.use_nodes=True;m.diffuse_color=(*c,1)
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    p.inputs['Specular IOR Level'].default_value=.3
    m['family']=name;m['roughness_base']=rough
    if variation:
        coord=n.new('ShaderNodeTexCoord');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=scale;t.inputs['Detail'].default_value=2
        l.new(coord.outputs['Object'],t.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(v*(1-variation) for v in c),1);ramp.color_ramp.elements[1].color=(*(min(1,v*(1+variation)) for v in c),1)
        l.new(t.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
        r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=max(.02,rough-.045);r.inputs['To Max'].default_value=min(1,rough+.05)
        l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Roughness'])
        if bump:
            fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=75;fine.inputs['Detail'].default_value=2;l.new(coord.outputs['Object'],fine.inputs['Vector'])
            b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=bump
            l.new(fine.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
    M[name]=m;return m
def build():
    specs=[('wall',(.48,.455,.395),.88,0,.14,.004,1.1),('dado',(.15,.22,.20),.79,0,.12,.001,2),
     ('teal',(.075,.20,.175),.64,.08,.16,.0007,2),('pale',(.48,.49,.42),.70,.03,.08,.0004,4),
     ('darksteel',(.045,.059,.061),.59,.60,.08,.0005,4),('steel',(.28,.34,.34),.33,.83,.06,.0004,5),
     ('rubber',(.024,.03,.031),.94,0,.09,.0008,10),('concrete',(.235,.256,.245),.91,0,.20,.004,.65),
     ('patch',(.205,.215,.19),.93,0,.16,.003,1),('yellow',(.61,.365,.055),.67,.02,.10,.0006,3),
     ('red',(.48,.055,.028),.64,.04,.04,.0003,3),('plastic',(.12,.17,.17),.43,0,.035,.0002,4),
     ('paper',(.77,.735,.63),.97,0,.015,0,2),('ink',(.028,.044,.043),.84,0,0,0,1),
     ('fuel',(.44,.48,.43),.35,.75,.065,.0003,2),('ore',(.23,.22,.145),.96,.04,.24,.007,5),
     ('cloth',(.275,.215,.12),.98,0,.08,.001,5),('screen',(.02,.068,.059),.47,0,0,0,1),
     ('dirtyfilter',(.16,.16,.125),.98,0,.12,.002,5)]
    for spec in specs:make(*spec)
    concrete_surface(M['concrete'])
    glass=make('glass',(.88,.93,.91),.035,0,0);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1.;p.inputs['IOR'].default_value=1.46
    for name,c,power in [('lamp',(1,.81,.56),4),('ready',(.19,.53,.32),1.1),('amber',(.85,.28,.03),1.4),('fault',(.80,.035,.015),2)]:
        m=make(name,c,.55,0,0);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=power

def concrete_surface(mat):
    """Existing project CC0 maps become restrained mineral variation, never raw photo colour."""
    folder=Path(__file__).resolve().parent.parent/'assets'/'textures'/'concrete'
    manifest=json.loads((folder/'provenance.json').read_text(encoding='utf-8-sig'))
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    for link in list(l):
        if link.to_socket in [p.inputs['Base Color'],p.inputs['Roughness'],p.inputs['Normal']]:l.remove(link)
    coord=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.27;l.new(coord.outputs['Object'],scale.inputs[0])
    images={}
    for role in ['color','height','roughness']:
        path=folder/(role+'.jpg');expected=manifest['maps'][role]['sha256']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError('Concrete asset hash mismatch: '+str(path))
        im=bpy.data.images.load(str(path),check_existing=True)
        if role!='color':im.colorspace_settings.name='Non-Color'
        im.pack();im.filepath='//../assets/textures/concrete/'+path.name
        tex=n.new('ShaderNodeTexImage');tex.image=im;tex.projection='BOX';tex.projection_blend=.25;l.new(scale.outputs[0],tex.inputs['Vector']);images[role]=tex.outputs['Color']
    grey=n.new('ShaderNodeRGBToBW');l.new(images['color'],grey.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.05;ramp.color_ramp.elements[0].color=(.105,.121,.112,1);ramp.color_ramp.elements[1].position=.68;ramp.color_ramp.elements[1].color=(.205,.225,.207,1)
    l.new(grey.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.81;rough.inputs['To Max'].default_value=.96;l.new(images['roughness'],rough.inputs[0]);l.new(rough.outputs[0],p.inputs['Roughness'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.30;bump.inputs['Distance'].default_value=.007;l.new(images['height'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    mat['source_asset']='ambientCG Concrete046';mat['source_license']='CC0-1.0';mat['look']='Desaturated matte mineral floor, palette remap, bounded relief'
