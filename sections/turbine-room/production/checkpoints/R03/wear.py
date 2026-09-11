"""Authored localized surface wear. Decals are mesh surfaces, not downloaded assets."""
import math,random
import bpy
def author(a):
    random.seed(162);a.group('05 Maintenance bay')
    a.M['primer']=a.material('Old slate primer exposed at impacts','79756C',.83,.15)
    a.M['paintpatch']=a.material('Maintenance enamel touchup','AA7045',.7,0,.1)
    a.M['handlewear']=a.material('Hand polished metal contact','899084',.4,.7)
    a.M['paperstain']=a.material('Old cellulose paper edge','b1a57c',.96)
    # Flat chips have irregular but restrained contours and follow the actual support surface.
    def patch(n,p,w,h,mat,face='S'):
        verts=[]
        for i in range(11):
            t=i*math.tau/11;r=random.uniform(.76,1.12);u=math.cos(t)*w*.5*r;v=math.sin(t)*h*.5*r
            verts.append((p[0]+u,p[1],p[2]+v) if face=='S' else ((p[0],p[1]+u,p[2]+v) if face=='E' else (p[0]+u,p[1]+v,p[2])))
        return a.mesh(n,verts,[tuple(range(11))],mat)
    # Selected door edge impacts: the steel kick plate takes most cart wear.
    for x,z,w,h in [(-2.44,.59,.12,.025),(-2.39,.63,.05,.028),(-1.56,.67,.07,.03),(-2.45,2.39,.055,.09),(-1.53,1.2,.035,.13),(-2.3,.09,.15,.03)]:
        patch('Door localized primer',(x,23.8685,z),w,h,'primer')
    for x,z,w,h in [(-2.37,.36,.14,.019),(-2.30,.33,.09,.012),(-1.78,.25,.08,.015),(-2.14,.43,.13,.01)]:patch('Kickplate cart rub',(x,23.841,z),w,h,'handlewear')
    # Flange chips clustered near the maintenance lamp mounting and floor bracket.
    for x,z,w,h in [(-3.63,.29,.038,.13),(-3.68,.35,.035,.065),(-3.65,1.01,.06,.024),(-3.66,2.32,.038,.15),(-3.76,2.37,.08,.028)]:
        patch('Column use chip',(x,20.771,z),w,h,'primer')
    # Bench fascia has a worn front working zone instead of equal chips all around.
    for y,z,w,h in [(20.24,.92,.16,.013),(20.39,.907,.055,.018),(20.5,.918,.07,.019),(21.23,.91,.05,.022),(22.58,.925,.07,.009)]:
        patch('Bench grip wear',(-2.600, y,z),w,h,'primer','E')
    # Patches on the cylindrical reservoir conform to the curved metal.
    def tankpatch(n,theta,z,w,h,mat):
        vertices=[]
        for i in range(13):
            t=i*math.tau/13;r=random.uniform(.7,1.1);angle=theta+math.cos(t)*w/.602*r
            vertices.append((-2.95+.301*math.cos(angle),18.75+.301*math.sin(angle),z+math.sin(t)*h*.5*r))
        a.mesh(n,vertices,[tuple(range(13))],mat)
    for theta,z,w,h in [(-1.15,1.29,.15,.03),(-.82,1.27,.06,.045),(-1.03,.74,.13,.04),(-.38,.87,.045,.11)]:tankpatch('Reservoir service scuff',theta,z,w,h,'primer')
    tankpatch('Old oil stand touchup',-.74,1.03,.18,.15,'paintpatch')
    # Two workers' cup rings and a faint older oil patch, using feathered vertex masks.
    def stainmat(n,color):
        m=a.material(n,color,.85);nodes=m.node_tree.nodes;links=m.node_tree.links;mix=nodes.new('ShaderNodeMixShader');tr=nodes.new('ShaderNodeBsdfTransparent');at=nodes.new('ShaderNodeAttribute');at.attribute_name='stain_alpha';links.new(at.outputs['Color'],mix.inputs[0]);links.new(tr.outputs[0],mix.inputs[1]);links.new(nodes.get('Principled BSDF').outputs[0],mix.inputs[2]);links.new(mix.outputs[0],nodes.get('Material Output').inputs[0]);return m
    a.M['stain']=stainmat('Absorbed worktop stains','574b32')
    def stain(n,x,y,rx,ry,opacity):
        v=[(x,y,1.0015)];N=35
        for i in range(N):
            t=i*math.tau/N;r=random.uniform(.85,1.12);v.append((x+rx*r*math.cos(t),y+ry*r*math.sin(t),1.0015))
        o=a.mesh(n,v,[(0,i+1,(i+1)%N+1) for i in range(N)],'stain');att=o.data.color_attributes.new(name='stain_alpha',type='FLOAT_COLOR',domain='POINT')
        for i,val in enumerate(att.data):val.color=(opacity,opacity,opacity,1) if i==0 else (0,0,0,1)
    stain('Old oil absorbed in wood',-3.30,21.04,.31,.42,.45);stain('Hand worked front wood',-2.75,20.40,.22,.39,.26);stain('Old cup spill',-3.45,22.2,.17,.19,.31)
    # Coffee ring is incomplete, variable width, and follows the tabletop exactly.
    for start,end in [(0,1.75),(2.1,3.7),(4.0,5.8)]:
        N=28;v=[]
        for r in [.071,.075]:
            for i in range(N):t=start+(end-start)*i/(N-1);v.append((-3.36+r*math.cos(t),22.47+r*math.sin(t),1.002))
        a.mesh('Dried coffee ring',v,[(i,i+1,N+i+1,N+i) for i in range(N-1)],'wooddark')
    # Timber grain contrast is softened; broad old-work patches carry age.
    mat=a.M['wood'];ramps=[n for n in mat.node_tree.nodes if n.bl_idname=='ShaderNodeValToRGB'];r=ramps[-1]
    r.color_ramp.elements[0].color=(*a.rgb('69583f'),1);r.color_ramp.elements[1].color=(*a.rgb('917951'),1)
    # A hand-marked service tag rests physically on the disassembled part's cradle.
    tag=a.box('Bearing red service tag',(-3.03,21.10,1.058),(.15,.11,.006),'paperstain',.001)
    a.text('Service tag handwriting','B1\nCHECK',(-3.09,21.12,1.062),.026,'ink','UP')
    # Forged hanging tools replace the uniform smooth torus vocabulary.
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('Hanging ring spanner','Hanging spanner shank','Lower wrench jaw')):bpy.data.objects.remove(ob,do_unlink=True)
    for idx,y in enumerate([20.4,20.9,21.4]):
        length=[.28,.34,.24][idx];x=-3.8;z=1.74
        for zz,rr in [(z,.044),(z-length,.038)]:
            o=a.ring('Forged hanging socket',(0,0,0),rr,rr*.58,.022,'steel',segments=12);o.rotation_euler[2]=math.pi/2;o.location=(x,y,zz)
        profile=[(y-.024,z-.024),(y-.014,z-.09),(y-.012,z-length+.045),(y-.024,z-length+.022),(y+.024,z-length+.022),(y+.012,z-length+.045),(y+.014,z-.09),(y+.024,z-.024)]
        N=len(profile);verts=[(x+dx,yy,zz) for dx in [-.009,.009] for yy,zz in profile];faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
        a.mesh('Forged hanging tool shank',verts,faces,'steel',.002)
    # Slight crookedness is authored as one rigid page assembly around its centre.
    # Its support remains against the wall; no floating offset is introduced.
