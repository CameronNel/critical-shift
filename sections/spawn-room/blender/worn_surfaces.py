"""CC0-backed, stylized maintained wear. Deterministic and build-time only."""
import bpy, bmesh, math, random, hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
TEX=HERE.parent/'assets/textures/cc0'

def seed(name): return int(hashlib.sha256(name.encode()).hexdigest()[:8],16)

def ramp(nodes, links, socket, colours, positions=(.12,.60)):
    r=nodes.new('ShaderNodeValToRGB');r.color_ramp.interpolation='EASE'
    for e,c,p in zip(r.color_ramp.elements,colours,positions):e.position=p;e.color=(*c,1)
    links.new(socket,r.inputs[0]);return r.outputs['Color']

def noise(nodes,links,vector,scale,detail=2):
    n=nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail
    links.new(vector,n.inputs['Vector']);return n.outputs['Fac']

def mathnode(nodes,links,op,a,b):
    n=nodes.new('ShaderNodeMath');n.operation=op
    for i,v in enumerate((a,b)):
        if isinstance(v,(int,float)):n.inputs[i].default_value=v
        else:links.new(v,n.inputs[i])
    return n.outputs[0]

def bitmap(nodes,links,vector,asset,kind):
    path=TEX/(asset+'_'+kind+'_2k.jpg')
    image=bpy.data.images.get(path.name) or bpy.data.images.load(str(path),check_existing=True)
    if kind!='diff':image.colorspace_settings.name='Non-Color'
    image.pack();image.filepath='//../assets/textures/cc0/'+path.name
    # Explicit world-normal triplanar blend: built-in BOX uses object-local normals,
    # which selects the wrong projection when a wall assembly is rotated in the room.
    coord=nodes.new('ShaderNodeSeparateXYZ');links.new(vector,coord.inputs[0])
    geo=nodes.new('ShaderNodeNewGeometry');absolute=nodes.new('ShaderNodeVectorMath');absolute.operation='ABSOLUTE'
    links.new(geo.outputs['Normal'],absolute.inputs[0]);normal=nodes.new('ShaderNodeSeparateXYZ');links.new(absolute.outputs[0],normal.inputs[0])
    weights=[mathnode(nodes,links,'POWER',normal.outputs[i],8) for i in range(3)]
    total=mathnode(nodes,links,'ADD',mathnode(nodes,links,'ADD',weights[0],weights[1]),weights[2])
    layers=[]
    for i,(a,b) in enumerate([(1,2),(0,2),(0,1)]):
        uv=nodes.new('ShaderNodeCombineXYZ');links.new(coord.outputs[a],uv.inputs[0]);links.new(coord.outputs[b],uv.inputs[1])
        n=nodes.new('ShaderNodeTexImage');n.image=image;n.projection='FLAT';n.interpolation='Linear'
        n.label='CC0 Poly Haven / '+asset+' / '+kind;links.new(uv.outputs[0],n.inputs['Vector'])
        weight=mathnode(nodes,links,'DIVIDE',weights[i],total)
        weighted=nodes.new('ShaderNodeMixRGB');weighted.blend_type='MULTIPLY';weighted.inputs[0].default_value=1
        links.new(n.outputs['Color'],weighted.inputs[1]);links.new(weight,weighted.inputs[2]);layers.append(weighted.outputs[0])
    for layer in layers[1:]:
        add=nodes.new('ShaderNodeMixRGB');add.blend_type='ADD';add.inputs[0].default_value=1
        links.new(layers[0],add.inputs[1]);links.new(layer,add.inputs[2]);layers[0]=add.outputs[0]
    return layers[0]

def mineral(mat,asset,colour,distance,wall=False):
    n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
    for link in list(l):
        if link.to_node==p:l.remove(link)
    coord=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.5
    l.new(coord.outputs['Position'],scale.inputs[0]);v=scale.outputs[0]
    diffuse=bitmap(n,l,v,asset,'diff');height=bitmap(n,l,v,asset,'disp');rough=bitmap(n,l,v,asset,'rough')
    gray=n.new('ShaderNodeRGBToBW');l.new(diffuse,gray.inputs[0])
    # Narrow palette and smooth ramp suppress raw scan chroma and photographic speckle.
    c=ramp(n,l,gray.outputs[0],[tuple(x*.68 for x in colour),tuple(x*1.12 for x in colour)],(.10,.52))
    broad=noise(n,l,coord.outputs['Position'],1.6,2)
    drift=ramp(n,l,broad,[(.63,.61,.55),(1,1,.96)],(.28,.75))
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.44
    l.new(c,mix.inputs[1]);l.new(drift,mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
    rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=.78;rr.inputs['To Max'].default_value=.98
    l.new(rough,rr.inputs[0]);l.new(rr.outputs[0],p.inputs['Roughness'])
    p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.17
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.48;bump.inputs['Distance'].default_value=distance
    l.new(height,bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    if wall:
        sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Position'],sep.inputs[0])
        low=mathnode(n,l,'SUBTRACT',.5,sep.outputs['Z']);low=mathnode(n,l,'MULTIPLY',low,1.3)
        grime=n.new('ShaderNodeMixRGB');grime.blend_type='MULTIPLY';grime.inputs[2].default_value=(.40,.36,.27,1)
        l.new(low,grime.inputs[0]);l.new(mix.outputs[0],grime.inputs[1]);l.new(grime.outputs[0],p.inputs['Base Color'])
    mat['surface_treatment']='CC0 scan remapped through restrained palette, metric projection, height and roughness'

def materials(k):
    mineral(k.M['wall'],'plastered_wall',(.57,.53,.44),.018,True)
    mineral(k.M['dado'],'plastered_wall',(.22,.285,.245),.005,True)
    for i in range(5):mineral(k.M['floor%d'%i],'concrete_floor',tuple(v*(.89+.052*i) for v in (.25,.265,.225)),.017)
    k.material('exposed_plaster',(.245,.215,.17),.96,0,.3,.01,12)
    mineral(k.M['exposed_plaster'],'plastered_wall',(.245,.215,.17),.012)
    k.material('old_grout',(.073,.070,.058),.96,0,.30,.004,16)
    k.material('rubbed_edge',(.29,.275,.23),.88,.18,.22,.002,22)
    # Every remaining surface family gets use and tactile response appropriate to its construction.
    for key in ['paint','pale','yellow','plastic','steel','darksteel','rubber','cloth','seam','wood','paper','vinyl','enamel','visor','glass','red','blue']:
        mat=k.M[key];n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
        tex=n.new('ShaderNodeTexCoord');v=tex.outputs['Generated']
        broad=noise(n,l,v,6.5,3);fine=noise(n,l,v,85,2)
        original=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].is_linked else None
        tint=ramp(n,l,broad,[(.49,.455,.365),(1,.975,.89)],(.24,.67))
        mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5 if key in ['rubber','cloth','wood'] else .30
        if original:l.new(original,mix.inputs[1])
        else:mix.inputs[1].default_value=p.inputs['Base Color'].default_value
        l.new(tint,mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
        if key in ['cloth','seam','rubber']:
            sep=n.new('ShaderNodeSeparateXYZ');l.new(v,sep.inputs[0])
            falloff=n.new('ShaderNodeMapRange');falloff.interpolation_type='SMOOTHERSTEP'
            falloff.inputs['From Min'].default_value=.03;falloff.inputs['From Max'].default_value=.55 if key!='rubber' else .42
            falloff.inputs['To Min'].default_value=1;falloff.inputs['To Max'].default_value=0
            l.new(sep.outputs['Z'],falloff.inputs[0]);lower=falloff.outputs[0]
            dirt=mathnode(n,l,'MULTIPLY',lower,mathnode(n,l,'MULTIPLY',broad,.74))
            stain=n.new('ShaderNodeMixRGB');stain.blend_type='MULTIPLY';stain.inputs[2].default_value=(.39,.32,.23,1)
            l.new(dirt,stain.inputs[0]);l.new(mix.outputs[0],stain.inputs[1]);l.new(stain.outputs[0],p.inputs['Base Color'])
        if key not in ['glass','visor']:
            rough={'cloth':(.88,.98),'seam':(.89,.99),'rubber':(.82,.98),'wood':(.68,.94),'steel':(.40,.70),'darksteel':(.55,.82),'enamel':(.35,.64),'plastic':(.61,.85)}.get(key,(.70,.93))
            rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=rough[0];rr.inputs['To Max'].default_value=rough[1]
            l.new(broad,rr.inputs[0]);l.new(rr.outputs[0],p.inputs['Roughness'])
            old=p.inputs['Normal'].links[0].from_socket if p.inputs['Normal'].is_linked else None
            bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.0018 if key in ['cloth','rubber','wood'] else .0008
            l.new(fine,bump.inputs['Height'])
            if old:l.new(old,bump.inputs['Normal'])
            l.new(bump.outputs[0],p.inputs['Normal'])
            if key not in ['steel','darksteel']:p.inputs['Specular IOR Level'].default_value=.18
        else:
            rr=n.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=.055 if key=='glass' else .19;rr.inputs['To Max'].default_value=.14 if key=='glass' else .34
            l.new(broad,rr.inputs[0]);l.new(rr.outputs[0],p.inputs['Roughness'])
        mat['surface_treatment']='Material-specific wear, variable roughness and restrained relief'

def tile_floor(k,obj):
    """One support mesh: irregular tile perimeters, recessed mortar, no raised trip edges."""
    xs=[v.co.x+obj.location.x for v in obj.data.vertices];ys=[v.co.y+obj.location.y for v in obj.data.vertices]
    x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys)
    rng=random.Random(seed(obj.name));verts=[];faces=[];indices=[]
    def poly(points,material):
        start=len(verts);verts.extend(points);faces.append(tuple(range(start,len(verts))));indices.append(material)
    poly([(x0,y0,-.002),(x1,y0,-.002),(x1,y1,-.002),(x0,y1,-.002)],5)
    # Retain the original 170mm structural slab beneath the recessed grout surface.
    perimeter=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    poly([(*q,-.17) for q in reversed(perimeter)],5)
    for i,a in enumerate(perimeter):
        b=perimeter[(i+1)%4];poly([(*a,-.17),(*b,-.17),(*b,-.002),(*a,-.002)],5)
    for ix in range(math.floor(x0),math.ceil(x1)):
        for iy in range(math.floor(y0),math.ceil(y1)):
            a,b=max(x0,ix)+.003,min(x1,ix+1)-.003;c,d=max(y0,iy)+.003,min(y1,iy+1)-.003
            if b<=a or d<=c:continue
            cut=rng.uniform(.014,.065) if rng.random()<.18 else rng.uniform(.001,.006)
            points=[(a+cut,c),(b-.003,c),(b,c+.003),(b,d-.004),(b-.004,d),(a+.004,d),(a,d-.004),(a,c+cut)]
            center=((a+b)/2,(c+d)/2,-rng.uniform(0,.0007));index=rng.choices(range(5),[1,2,6,2,1])[0]
            # Corner loss reveals darker cement below. Top varies less than a millimetre.
            for i in range(len(points)):
                pa=points[i];pb=points[(i+1)%len(points)]
                poly([(*pa,0),(*pb,0),center],index)
                poly([(*pa,0),(*pa,-.002),(*pb,-.002),(*pb,0)],5)
    data=bpy.data.meshes.new(obj.name+'_worn_tiles');data.from_pydata(verts,[],faces);data.update()
    obj.data=data;obj.location=(0,0,0)
    for i in range(5):data.materials.append(k.M['floor%d'%i])
    data.materials.append(k.M['old_grout'])
    for p,i in zip(data.polygons,indices):p.material_index=i
    for child in list(bpy.data.objects):
        if child.name.startswith(obj.name+'_joint'):bpy.data.objects.remove(child,do_unlink=True)
    obj['surface_treatment']='Chamfered and chipped corners, actual 2mm recessed joints, per-tile mineral variation'

def worn_wall(k,o):
    """Subtle real plaster waviness. Keep attachments inside the existing contact tolerances."""
    if len(o.data.vertices)!=8:return
    dims=o.dimensions
    if dims.z<1.2 or min(dims.x,dims.y)>.20:return
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=20,use_grid_fill=True)
    thin=0 if dims.x<dims.y else 1;long=1-thin
    lo=min(v.co[thin] for v in bm.verts);hi=max(v.co[thin] for v in bm.verts)
    u0=min(v.co[long] for v in bm.verts);u1=max(v.co[long] for v in bm.verts)
    z0=min(v.co.z for v in bm.verts);z1=max(v.co.z for v in bm.verts)
    for v in bm.verts:
        if min(abs(v.co[thin]-lo),abs(v.co[thin]-hi))<1e-5:
            u=(v.co[long]-u0)/(u1-u0);z=(v.co.z-z0)/(z1-z0)
            weight=math.sin(math.pi*u)*math.sin(math.pi*z)
            v.co[thin]+=.0014*weight*math.sin(v.co[long]*8.3+v.co.z*5.7)
    bm.to_mesh(o.data);bm.free();o['surface_treatment']='Real trowelled surface waviness, maximum 1.4mm'

def surface_scar(k,name,target,center,axis_u,axis_v,normal,radius,seed_value,mat='exposed_plaster'):
    """Cut a shallow irregular plaster loss into the support wall itself."""
    rng=random.Random(seed_value);c=Vector(center);u=Vector(axis_u);v=Vector(axis_v);n=Vector(normal)
    count=22;points=[]
    for j in range(count):
        a=j*math.tau/count;r=radius*rng.uniform(.69,1.12)
        points.append(c+u*(math.cos(a)*r)+v*(math.sin(a)*r*.46))
    # Cut into the existing wall: visible substrate is genuinely recessed, never a floating decal.
    verts=[tuple(q+n*.012) for q in points]+[tuple(c+(q-c)*.87-n*.009) for q in points]
    faces=[tuple(range(count-1,-1,-1)),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    cutter=k.mesh(name+'_cutter',verts,faces,mat)
    bm=bmesh.new();bm.from_mesh(cutter.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cutter.data);bm.free()
    if k.M[mat].name not in target.data.materials:target.data.materials.append(k.M[mat])
    mod=target.modifiers.new(name+'_recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    target['surface_treatment']='Trowelled plaster with localized irregular 9mm recessed spall/repair'
    return target

def paint_chips(k,o):
    """Small adhered wear islands on selected touch/impact faces; deterministic per part."""
    rng=random.Random(seed(o.name));bb=[Vector(v) for v in o.bound_box]
    lo=Vector([min(v[i] for v in bb) for i in range(3)]);hi=Vector([max(v[i] for v in bb) for i in range(3)])
    if len(o.data.vertices)!=8 or hi.x-lo.x<.08 or hi.y-lo.y<.012 or hi.z-lo.z<.012:return
    # Front face is local -Y; use mostly low front corners and the grasp zone.
    verts=[];faces=[]
    for j in range(7):
        x=lo.x+(hi.x-lo.x)*rng.uniform(.20,.80)
        z=lo.z+(hi.z-lo.z)*rng.uniform(*((.43,.57) if hi.z-lo.z<.10 else (.12,.26)))
        width=min((hi.x-lo.x)*.16,rng.uniform(.012,.055));height=min((hi.z-lo.z)*.1,rng.uniform(.003,.013))
        pts=[(x-width,o.bound_box[0][1]-.0003,z),(x-width*.55,lo.y-.0003,z+height),(x+width*.8,lo.y-.0003,z+height*.7),(x+width,lo.y-.0003,z),(x,lo.y-.0003,z-height*.35)]
        start=len(verts);verts.extend(pts);faces.append(tuple(range(start,len(verts))))
    scar=k.mesh(o.name+'_rubbed_paint',verts,faces,'rubbed_edge')
    scar.parent=o;scar.matrix_parent_inverse.identity()
    # The chip geometry is authored in the support object's local coordinates.
    scar['surface_treatment']='Localized dry paint loss on low impact edge'
    k.support(scar,o,'LOCAL_+Y',[tuple(Vector(verts[0]))],'WALL')

def geometry(k,scope):
    bpy.context.view_layer.update()
    objects=list(bpy.data.objects)
    floors=[o for o in objects if o.type=='MESH' and o.name in ['FACILITY_floor','SLICE_floor']]
    for o in floors:tile_floor(k,o)
    objects=list(bpy.data.objects)
    for o in objects:
        if o.type!='MESH' or not o.data.materials:continue
        mat=o.data.materials[0]
        if mat and mat.name=='wall' and 'ceiling' not in o.name:worn_wall(k,o)
        # Local dents in sheet steel and laminate edges, excluding support feet and standing platforms.
        if any(s in o.name for s in ['_laminate_slat','_service_access','_back_panel','_carcass']):
            for vert in o.data.vertices:
                if vert.co.z>0 and vert.co.x<0:vert.co.x+=.0018
            o['surface_treatment']='Small asymmetric edge compression from use'
        if any(s in o.name for s in ['_return_lip','_folded_shelf','_kickplate','_threshold','_service_lid','_rear_access','_laminate_slat']):
            paint_chips(k,o)
    if scope=='slice':
        target=bpy.data.objects['SLICE_wall_main']
        surface_scar(k,'SLICE_plaster_repair',target,(1.56,0,1.46),(1,0,0),(0,0,1),(0,-1,0),.30,19)
    else:
        # Intentional clusters: lower wall by the bench, entry threshold, locker service wall.
        for name,t,c,u,n,r,s in [
            ('HALL_lower_repair','HALL_left_ops',(-1.7,6.8,1.40),(0,1,0),(1,0,0),.34,9),
            ('LOCKER_old_repair','LOCKER_far',(8.1,2.85,1.46),(0,1,0),(-1,0,0),.38,17),
            ('BRIEFING_repaint','BRIEFING_north',(-2.55,6.1,1.41),(1,0,0),(0,-1,0),.27,35)]:
            target=bpy.data.objects.get(t)
            if target:surface_scar(k,name,target,c,u,(0,0,1),n,r,s)
    bpy.context.view_layer.update()
