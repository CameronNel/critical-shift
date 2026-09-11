"""Complete original environment, preserving the existing R09 architectural layout."""
def bounded_tube(name,points,r,mat,parent=None):
    # Rounded polyline corners stay inside each authored segment envelope.
    pts=[Vector(p) for p in points];out=[pts[0]]
    for k in range(1,len(pts)-1):
        before,corner,after=pts[k-1:k+2];d=min(.09,(corner-before).length*.3,(after-corner).length*.3)
        a=corner+(before-corner).normalized()*d;b=corner+(after-corner).normalized()*d
        for j in range(7):
            t=j/6;out.append((1-t)**2*a+2*(1-t)*t*corner+t*t*b)
    out.append(pts[-1]);cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True
    sp=cu.splines.new('POLY');sp.points.add(len(out)-1)
    for p,v in zip(sp.points,out):p.co=(*v,1)
    ob=bpy.data.objects.new(name,cu);COL[current].objects.link(ob);ob.parent=parent;cu.materials.append(M[mat]);ob['assembly_member']=parent.name if parent else 'fixed-architecture';return ob
tube=bounded_tube
for key,rough,metallic in [('wall',.95,0),('floor',.94,0),('pale',.52,.1),('paint',.55,.1),('metal',.33,.85),('rubber',.95,0),('paper',.98,0)]:
    m=M[key];bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic
    for n in m.node_tree.nodes:
        if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=rough-.025;n.inputs['To Max'].default_value=min(.99,rough+.025)
        if n.type=='TEX_COORD':
            for edge in list(n.outputs['Generated'].links):
                socket=edge.to_socket;m.node_tree.links.remove(edge);m.node_tree.links.new(n.outputs['Object'],socket)
    if key in ['wall','floor']:
        nt=m.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=80;noise.inputs['Detail'].default_value=1
        bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.0015
        nt.links.new(tc.outputs['Object'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
M['linen']=material('Woven recovery linen','ABA493',.98,0,.035,.0006)
M['glass']=material('Neutral clear safety glass','D4D1C9',.09,0,0);bs=M['glass'].node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
M['task']=emission('Neutral OCRU task diffuser','EEEAE2',3)
M['screen']=emission('Amber grey phosphor','BEB9A8',.7)
def plaque(parent,body,loc,w=.48,h=.15,mat='darkpaint',size=.055):
    x,y,z=loc;box('Engraved backing '+body,(x,y,z),(w,.008,h),mat,parent,.002)
    text('Engraved '+body,body,(x-w*.43,y-.006,z-size*.35),size,'ink' if mat in ['pale','paper'] else 'paper',parent)
current='Architecture'
box('Floor',(0,4.5,-.12),(8.36,9.36,.24),'floor',bevel=.002)
box('Decon floor',(2.33,10.24,-.12),(2.06,2.12,.24),'floor',bevel=.002)
box('West wall',(-4.09,4.5,1.8),(.18,9.36,3.6),'wall')
box('East wall',(4.09,4.5,1.8),(.18,9.36,3.6),'wall')
for x in [-2.64,2.64]:box('Entry wall',(x,-.09,1.8),(3.08,.18,3.6),'wall')
box('Entry lintel',(0,-.09,3.05),(2.2,.18,1.1),'wall')
box('Rear west wall',(-1.225,9.09,1.8),(5.55,.18,3.6),'wall')
box('Rear east wall',(3.375,9.09,1.8),(1.25,.18,3.6),'wall')
box('Decon doorway lintel',(2.15,9.09,2.875),(1.2,.18,1.45),'wall')
box('Decon west wall',(1.39,10.15,1.275),(.18,2.30,2.55),'wall')
box('Decon east wall',(3.27,10.15,1.275),(.18,2.30,2.55),'wall')
box('Decon rear wall',(2.33,11.21,1.275),(2.06,.18,2.55),'wall')
box('Ceiling',(0,4.5,3.68),(8.36,9.36,.16),'wall')
box('Decon ceiling',(2.33,10.06,2.63),(2.06,2.48,.16),'wall')
for y in [1.0,3.4,6.0,8.65]:box('Ceiling cross member',(0,y,3.44),(8,.16,.24),'darkpaint',bevel=.003)
for x in [-3.7,3.7]:box('Longitudinal steel',(x,4.5,3.45),(.13,9,.22),'darkpaint',bevel=.003)
for side in [-1,1]:
    for ya,yb in [(0,2.4),(2.42,5.95),(5.97,8.98)]:
        box('Impact wall lining',(side*3.982,(ya+yb)/2,.57),(.035,yb-ya,1.14),'bus',bevel=.002)
        box('Impact cap',(side*3.955,(ya+yb)/2,1.145),(.07,yb-ya,.03),'metal',bevel=.002)
    for y in [2.4,6.0]:box('Wall panel joint',(side*3.997,y,2.3),(.008,.014,2.6),'joint',bevel=0)
for y in [1.5,3,4.5,6,7.5]:box('Floor sealed joint',(0,y,.0005),(8,.005,.001),'joint',bevel=0)
for x in [-2,0,2]:box('Floor longitudinal joint',(x,4.5,.0005),(.005,9,.001),'joint',bevel=0)
# Entry pressure leaves park beside the aperture, not across a rescue route.
for side in [-1,1]:
    box('Entry capture housing',(side*1.73,-.07,1.25),(1.22,.20,2.5),'darkpaint',bevel=.008)
    p=assembly('ENTRY_LEAF_L' if side<0 else 'ENTRY_LEAF_R',(side*1.67,.10,0));p['closed_x']=side*.55;p['open_x']=side*1.67;p['door_id']='main_entry'
    box('Pressure door lower panel',(0,0,.60),(1.10,.07,1.18),'pale',p,.01)
    box('Pressure door upper panel',(0,0,2.18),(1.10,.07,.60),'pale',p,.01)
    for x in [-.32,.32]:box('Door window side panel',(x,0,1.53),(.46,.07,.68),'pale',p,.008)
    box('Door safety glazing',(0,0,1.53),(.17,.028,.70),'glass',p,.001)
    for x in [-.095,.095]:box('Glazing frame',(x,.045,1.53),(.025,.03,.75),'metal',p,.002)
    box('Door toe protector',(0,.045,.24),(1.02,.02,.26),'darkpaint',p,.002)
    box('Door edge seal',(side*-.545,0,1.24),(.018,.095,2.43),'rubber',p,.002)
box('Door guide header',(0,.035,2.59),(4.65,.30,.18),'darkpaint',bevel=.005)
box('Entry threshold',(0,0,-.003),(2.2,.36,.006),'metal',bevel=.001)
for x in [-1.15,1.15]:box('Entry jamb',(x,.075,1.25),(.10,.15,2.5),'metal',bevel=.003)
p=assembly('Main entry identity',(0,.07,2.83),math.pi)
plaque(p,'MEDICAL  /  OCRU',(0,0,0),2.5,.25,mat='pale',size=.13)
# Rear decontamination opening keeps inherited 1.2m clearance.
for x in [1.50,2.80]:box('Decon jamb',(x,8.98,1.08),(.10,.14,2.16),'metal')
box('Decon header',(2.15,8.97,2.23),(1.4,.16,.15),'pale')
p=assembly('Decon identity',(2.15,8.89,2.47));plaque(p,'DECON',(0,0,0),1.35,.24,mat='darkpaint',size=.13)
exec(compile((Path(__file__).parent/'ocru_assembly.py').read_text(),'ocru_assembly.py','exec'))
exec(compile((Path(__file__).parent/'stations.py').read_text(),'stations.py','exec'))
exec(compile((Path(__file__).parent/'services_lighting.py').read_text(),'services_lighting.py','exec'))
exec(compile((Path(__file__).parent/'refinement.py').read_text(),'refinement.py','exec'))
exec(compile((Path(__file__).parent/'construction_corrections.py').read_text(),'construction_corrections.py','exec'))
exec(compile((Path(__file__).parent/'service_completion.py').read_text(),'service_completion.py','exec'))
exec(compile((Path(__file__).parent/'material_light_finish.py').read_text(),'material_light_finish.py','exec'))
exec(compile((Path(__file__).parent/'cameras_save.py').read_text(),'cameras_save.py','exec'))
