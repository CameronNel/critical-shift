"""W06: original architectural graphics and manufactured surface separation."""
current='Architecture'
# Low retracting gates are cantilevered from their captive cassette. No fixed
# crossbar may remain across the walking aperture when the gate is retracted.
for ob in list(bpy.data.objects):
    if ob.name.startswith('Cell sliding gate header') or ob.name.startswith('Selective floor wear patch'):
        bpy.data.objects.remove(ob,do_unlink=True)
# Concept-derived broad oxide diagonals, clipped to each concrete divider.
def graphic(name,verts,mat,parent=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.update()
    ob=bpy.data.objects.new(name,me);COL[current].objects.link(ob);ob.parent=parent;me.materials.append(M[mat]);ob['assembly_member']=parent.name if parent else 'fixed-architecture';return ob
for side in [-1,1]:
    for y in [4.8,8.8,9.4,13.4]:
        x0=-6 if side<0 else 2.15;x1=x0+3.85
        for direction in [-1,1]:
            yy=y+direction*.0807
            graphic('Divider oxide lower band',[(x0,yy,.03),(x1,yy,.03),(x1,yy,.25),(x0+1.4,yy,.25),(x0+.8,yy,.54),(x0,yy,.54)],'orange')
        # Stepped steel nose reinforces the exposed aisle corner.
        box('Barrier end shoe',(side*2.21,y,.23),(.12,.185,.44),'darkpaint',bevel=.014)
        for z in [.12,.33]:cyl('Barrier anchor head',(side*2.14,y,z),.018,.03,'metal',axis='X',vertices=6)
for side in [-1,1]:
    for y,title,code in [(6.6,'RESIDUE' if side<0 else 'DRY STORE','A' if side<0 else 'C'),(11.2,'SHIELDED' if side<0 else 'QUARANTINE','B' if side<0 else 'D')]:
        p=assembly('Wall bay wayfinding',(side*5.988,y,2.23),math.pi/2 if side<0 else -math.pi/2)
        text('Wall bay title',title,(-1.35,-.001,.11),.235,'ink',p)
        text('Wall bay code','WS / '+code,(-1.35,-.001,-.16),.11,'ink',p)
        box('Wall bay underline',(0,-.002,-.28),(2.70,.002,.06),'orange',p,0)
    # Knee braces connect beam and wall-column, above all circulation envelopes.
    for y in [4.45,9.05,13.75,17.65]:
        beam('Roof knee brace',(side*5.79,y,3.85),(side*5.15,y,4.52),.10,'darkpaint')
        box('Brace wall gusset',(side*5.81,y,3.87),(.035,.23,.34),'metal',bevel=.004)
        for z in [3.77,3.97]:cyl('Gusset fastener',(side*5.78,y,z),.022,.04,'darkpaint',axis='X',vertices=6)
# Receiving booth is a purposeful place in the architectural hierarchy.
p=assembly('Inventory booth fascia',(-2.323,2.15,2.61),math.pi/2)
text('Inventory fascia title','INVENTORY / SCAN',(-1.25,-.002,-.055),.155,'paper',p)
# Substrate-specific larger planar colour patches; no shiny procedural grunge.
for key,variation,rough in [('wall',.34,.96),('floor',.32,.94),('pale',.19,.71),('paint',.20,.58),('darkpaint',.18,.73),('metal',.16,.40)]:
    m=M[key];base=m.diffuse_color[:3]
    for n in m.node_tree.nodes:
        if n.type=='VALTORGB':
            n.color_ramp.elements[0].position=.25;n.color_ramp.elements[1].position=.75
            n.color_ramp.elements[0].color=(*(c*(1-variation) for c in base),1)
            n.color_ramp.elements[1].color=(*(min(1,c*(1+variation)) for c in base),1)
        if n.type=='TEX_NOISE' and n.inputs['Scale'].default_value<10:
            n.inputs['Scale'].default_value=17 if key=='floor' else 7;n.inputs['Detail'].default_value=1.1;n.inputs['Roughness'].default_value=.7
        if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=rough-.10;n.inputs['To Max'].default_value=min(.98,rough+.08)
# Localized practical warmth and less uniform ambient fill.
for d in bpy.data.lights:
    if d.name.startswith('Practical pool'):d.energy*=.68;d.color=(1,.90,.76)
    if d.type=='SPOT':d.energy*=1.5;d.color=(1,.73,.45);d.spot_blend=.42
