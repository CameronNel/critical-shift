"""Full-room extension of the reviewed clinical construction slice."""

# Battery housings are painted steel, not inherited near-black graphite. A
# shallow pressed face preserves their envelope and seats the service label.
for suffix in ('','.001'):
    folded_skin(s.objects['Reserve battery module'+suffix],1,-1,inset=.07,depth=.006)
    for name in ('Reserve folded side','Reserve folded cap'):
        o=s.objects[name+suffix];o.data.materials.clear();o.data.materials.append(M['blue'])

def attribute_age(mat,name,color):
    nt=mat.node_tree;p=principal(mat);base=p.inputs['Base Color']
    src=base.links[0].from_socket if base.is_linked else None
    a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name=name
    mix=nt.nodes.new('ShaderNodeMixRGB')
    if src:nt.links.new(src,mix.inputs[1])
    else:mix.inputs[1].default_value=base.default_value[:]
    mix.inputs[2].default_value=(*rgb(color),1)
    nt.links.new(a.outputs['Fac'],mix.inputs[0]);nt.links.new(mix.outputs[0],base)

def paint_surface(o,name,fn,cuts=24):
    # Planar subdivision carries hand-directed broad wear while preserving every
    # wall plane and original bound. No displacement and no automatic unwrap.
    o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=cuts,use_grid_fill=True)
    bm.to_mesh(o.data);bm.free();o.data.update()
    a=o.data.attributes.get(name) or o.data.attributes.new(name,'FLOAT','POINT')
    for v,w in zip(o.data.vertices,a.data):w.value=max(0,min(.82,fn(o.matrix_world@v.co)))

attribute_age(M['mauve'],'MED_WallAge','62595F')
attribute_age(M['navy'],'MED_WallAge','5B6069')
for o in list(s.objects):
    if o.name in ['West wall','East wall','Entry wall','Entry wall.001','Rear west wall','Rear east wall','Decon west wall','Decon east wall'] or o.name.startswith('Impact wall lining'):
        def wall_age(p):
            # Leaking upper service seam on the north west panel, wash handling
            # on the east wall, and repeated cart contact below the impact cap.
            leak=.46*math.exp(-((p.x+3.46)/.23)**2)*math.exp(-((p.y-9)/.38)**2)*math.exp(-((p.z-2.27)/.64)**2)
            wash=.32*math.exp(-((p.y-3.02)/.40)**2)*math.exp(-((p.x-4)/.25)**2)*math.exp(-((p.z-1.19)/.48)**2)
            low=.12*math.exp(-((p.z-.46)/.25)**2)*(math.exp(-((p.y-1.3)/.50)**2)+math.exp(-((p.y-4.7)/.55)**2))
            return (leak+wash+low)*(.86+.14*math.sin(p.z*13+p.y*4)**2)
        paint_surface(o,'MED_WallAge',wall_age,20)
attribute_age(M['floor'],'MED_FloorAge','49434B')
def floor_age(p):
    bed=.32*math.exp(-((p.x+2.38)/.61)**2-((p.y-4.35)/.92)**2)
    wash=.24*math.exp(-((p.x-3.45)/.32)**2-((p.y-3.05)/.48)**2)
    cart=.20*math.exp(-((p.x+3.10)/.47)**2-((p.y-1.2)/.70)**2)
    return (bed+wash+cart)*(.84+.16*math.sin(p.x*14+p.y*7)**2)
paint_surface(s.objects['Floor'],'MED_FloorAge',floor_age,44)
# Generated coordinates are normalized per mesh. Give the small decon slab
# its measured scale instead of inheriting the main slab's tile multiplier.
decon_floor=s.objects['Decon floor'];decon_material=M['floor'].copy()
decon_material.name='MED | Decon floor / measured 600mm tiles'
decon_material.node_tree.nodes['MED_600mm_measured_slab_scale'].inputs[1].default_value=tuple(decon_floor.dimensions)
decon_floor.data.materials.clear();decon_floor.data.materials.append(decon_material)

attribute_age(M['cream'],'MED_WorkWear','8C8D87')
top=s.objects['Supply bench top']
def work_wear(p):
    q=bench.matrix_world.inverted()@p
    lip=.28*math.exp(-((q.y+.425)/.016)**2)*(.55+.45*math.sin(q.x*8+.4)**2)
    work=.13*math.exp(-((q.x-.18)/.36)**2-((q.y+.16)/.19)**2)
    return lip+work
paint_surface(top,'MED_WorkWear',work_wear,30)

def sealed_wrapper(o):
    # Folded paper around a gauze stack: bevelled cardboard is the wrong form.
    lo,hi=bounds(o);sp=hi-lo;v=[];f=[];n=12
    for bottom in (False,True):
        for i in range(n+1):
            x=-1+2*i/n
            for j in range(n+1):
                y=-1+2*j/n
                xx=x*(1-.025*abs(y)**10);yy=y*(1-.025*abs(x)**10)
                # Thin crimped perimeter, broad gauze centre, two folded corners.
                rise=max(0,1-max(abs(x),abs(y))**12)**.5
                z=0 if bottom else .18+.82*rise
                if not bottom:z-=.12*math.exp(-((x+y-1.1)/.10)**2)*rise
                v.append((lo.x+(xx+1)*sp.x/2,lo.y+(yy+1)*sp.y/2,lo.z+z*sp.z))
    size=(n+1)**2
    for b in range(2):
        for i in range(n):
            for j in range(n):
                q=b*size+i*(n+1)+j;face=(q,q+1,q+n+2,q+n+1);f.append(face if b else tuple(reversed(face)))
    edge=list(range(n+1))+[i*(n+1)+n for i in range(1,n+1)]+[n*(n+1)+j for j in range(n-1,-1,-1)]+[i*(n+1) for i in range(n-1,0,-1)]
    for a,b in zip(edge,edge[1:]+edge[:1]):f.append((a,b,b+size,a+size))
    for k in range(3):
        amin=min(p[k] for p in v);amax=max(p[k] for p in v)
        v=[tuple(lo[t]+(p[t]-amin)/(amax-amin)*sp[t] if t==k else p[t] for t in range(3)) for p in v]
    replace(o,v,f,[M['paper']],smooth=True)
for name in ['Sterile pack','Sterile pack.001']:sealed_wrapper(s.objects[name])

def carton_print():
    for o in [s.objects['Sterile pack'],s.objects['Sterile pack.001']]:
        x,y,z=o.location
        text('Sterile gauze wrapper typography','STERILE / 04\nGAUZE COMPRESS',(x-.088,y+.08,z+.0154),.012,M['ink'],bench,(0,0,0))
        for i in range(8):line('Wrapper heat-seal crimps',[(x-.095,y-.105+i*.025,z+.002),(x-.087,y-.105+i*.025,z+.004)],.0006,M['age'],bench)
    for i,o in enumerate([o for o in s.objects if o.name.startswith('Sealed consumable carton')]):
        assign(o,M['carton']);x,y,z=o.location;lo,hi=bounds(o)
        text('Carton clinical stock print','CONTINUITY\nMEDICAL STOCK', (x-.15,y-.247,z+.023),.019,M['ink'],bench)
        text('Carton batch identifier','LOT 31-804 / '+str(12+i),(x-.15,y-.247,z-.050),.010,M['ink'],bench)
        for k in range(22):box('Carton inventory barcode',(x-.145+k*.007,y-.247,z-.075),(.002 if k%3 else .004,.001,.021),M['ink'],bench)
        # Fold lines are physically shallow pressed paper seams.
        for xx in (-.185,.185):line('Carton folded return',[(x+xx,y-.245,z-.087),(x+xx,y-.245,z+.085)],.0007,M['age'],bench)
group('Printed and folded clinical packaging',carton_print,'Sterile pack.001')

# Detailed tire section, smooth shoulders and an open hub. Replaces the old
# simple cylinder within its exact measured axle/radius envelope.
for o in [o for o in s.objects if o.name.startswith('Caster rubber tyre')]:
    lo,hi=bounds(o);sp=hi-lo;axis=min(range(3),key=lambda i:sp[i]);axes=[i for i in range(3) if i!=axis];v=[];f=[];n=64
    rings=[(-.5,.36),(-.5,.82),(-.42,.97),(-.26,1),(.26,1),(.42,.97),(.5,.82),(.5,.36)]
    for z,r in rings:
        for i in range(n):
            a=i*math.tau/n;p=(lo+hi)/2;p[axis]+=z*sp[axis];p[axes[0]]+=r*sp[axes[0]]*.5*math.cos(a);p[axes[1]]+=r*sp[axes[1]]*.5*math.sin(a);v.append(tuple(p))
    for k in range(len(rings)):
        for i in range(n):f.append((k*n+i,k*n+(i+1)%n,((k+1)%len(rings))*n+(i+1)%n,((k+1)%len(rings))*n+i))
    replace(o,v,f,[M['rubber']],smooth=True)

def cart_service():
    for x in (-.27,.27):
        for y in (-.83,.83):
            box('Caster brake folded pedal',(x,y+.075,.117),(.060,.052,.014),M['ochre'],cart,.003)
            for off in (-.016,0,.016):box('Caster brake traction rib',(x+off,y+.078,.126),(.006,.040,.004),M['edge'],cart)
            cylinder('Swivel captive locking pin',(x,y,.245),.025,.020,M['steel'],cart,vertices=24)
            line('Caster brake retaining lever',[(x,y+.042,.145),(x,y+.065,.118)],.006,M['steel'],cart)
group('Transfer cart brake and retained swivel construction',cart_service,'Caster mounting plate')

def cart_deck_identity():
    plate('Transfer cart end inspection plate',(0,-1.051,.830),.22,.050,.003,M['navy'],s.objects['CART_LIFT_DECK'],.009)
    text('Transfer cart working load print','LOAD / 140 KG',(-.091,-1.053,.835),.016,M['paper'],s.objects['CART_LIFT_DECK'])
group('Transfer deck load identification',cart_deck_identity,'Cart deck')

# Cabinet fog and deposits are deliberately restrained so the clinical stock
# still reads through the glazing. Its two sliding leaves retain their parenting.
gp=principal(M['glass']);gp.inputs['Roughness'].default_value=.16
for name in ['MED_R2 | Old caster traffic marks','MED_R2 | Neglected clinical traffic']:
    obj=s.objects.get(name)
    if obj:
        for slot in obj.material_slots:
            if slot.material in (M['blood'],M['rust'],M['rubber']):slot.material=M['age']

# Fine handling marks stay attached to the worktop and use the medical working
# cluster's footprint. The room's quiet areas remain quiet.
def worktop_contact():
    for i in range(7):
        x=-.12+i*.035;y=-.30+.012*math.sin(i)
        line('Clinical handled worktop hairline',[(x,y,.9454),(x+.050+i*.004,y+.003,.9454)],.00035,M['edge'],bench)
group('Localized clinical worktop handling',worktop_contact,'Supply bench top')

# Retained machinery needs an actual route into its fixed frame, not merely a
# valid object name. These small mounting pieces bridge measured source gaps
# while retaining every equipment transform and room boundary.
def retained_contact(source,mount):
    supports.append({'object':source.name,'target':mount.name,'max_gap_m':.005,
                     'max_penetration_m':.002,'kind':'retained_component_mount'})

def mounting_return(name,source_name,target_name,width=.022,height=.012,centre=None):
    source=s.objects[source_name];target=s.objects[target_name]
    bpy.context.view_layer.update();deps_local=bpy.context.evaluated_depsgraph_get()
    def surface_tree(obj):
        ev=obj.evaluated_get(deps_local);md=ev.to_mesh()
        result=BVHTree.FromPolygons([obj.matrix_world@v.co for v in md.vertices],[tuple(p.vertices) for p in md.polygons])
        ev.to_mesh_clear();return result
    source_tree=surface_tree(source);target_tree=surface_tree(target)
    centre=Vector(centre) if centre is not None else source.matrix_world@(sum((Vector(p) for p in source.bound_box),Vector())/8)
    end=target_tree.find_nearest(centre)[0];direction=(end-centre).normalized()
    start=source_tree.ray_cast(centre,direction,(end-centre).length+.02)[0]
    if start is None or (end-start).dot(direction)<0:
        start=source_tree.find_nearest(end)[0]
    direction=(end-start).normalized()
    up=Vector((0,0,1)) if abs(direction.z)<.9 else Vector((1,0,0))
    side=direction.cross(up).normalized();up=side.cross(direction).normalized()
    cut=min(width,height)*.18
    outline=[(-width/2+cut,-height/2),(width/2-cut,-height/2),(width/2,-height/2+cut),
             (width/2,height/2-cut),(width/2-cut,height/2),(-width/2+cut,height/2),
             (-width/2,height/2-cut),(-width/2,-height/2+cut)]
    parent=target.parent
    inverse=parent.matrix_world.inverted() if parent else Matrix.Identity(4)
    verts=[tuple(inverse@(point+side*x+up*y)) for point in (start-direction*.0005,end+direction*.0005) for x,y in outline]
    faces=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    def creator():supported(mesh(name,verts,faces,M['steel'],parent),target)
    mount=group(name,creator,target.name);retained_contact(source,mount)
    return mount

for suffix in ('','.001'):
    mounting_return('Reserve drawer rear mounting return '+suffix,'Battery supported drawer rail'+suffix,'Reserve folded back',.090,.024)
    mounting_return('Battery resilient bearing pad '+suffix,'Reserve battery module'+suffix,'Battery supported drawer rail'+suffix,.180,.030)

for suffix,y in (('',8.37),('.001',6.57)):
    for z in (1.46,2.29):
        mounting_return('Glazing captive slide guide '+suffix+' '+str(z),'Clear cabinet sliding pane'+suffix,'Cabinet formed edge'+suffix,.024,.032,(3.25,y,z))

for z in (1.12,1.40):
    mounting_return('Suit service fixed mounting arm '+str(z),'Suit service enclosure','Jamb folded cover.001',.040,.018,(-1.48875,6.23,z))
mounting_return('Receiver fixed steel mounting arm','Receiver cast housing','Jamb folded cover',.030,.022)
# Seat the small existing cartridge plaque on the retained tab, rather than add
# hardware beyond its existing interface envelope. This is a 6 mm label pose,
# not an equipment or hook move; both glyph and backing remain together.
plaque=s.objects['Engraved backing C01'];glyph=s.objects['Engraved C01']
worlds={o.name:o.matrix_world.copy() for o in (plaque,glyph)}
for o in (plaque,glyph):
    world=worlds[o.name];world.translation.x-=.006;o.matrix_world=world
    pose_updates.append(o.name);bpy.context.view_layer.update()
supports.append({'object':plaque.name,'target':'Cartridge extraction tab','max_gap_m':.005,'max_penetration_m':.002,'kind':'retained_plaque_seating'})

for source_name,target_name in (('Engraved backing RECOVERY.001','Identity wall spacer'),('Engraved backing SUPPLIES','Identity wall spacer.001')):
    mounting_return('Wall plaque mounting return '+source_name,source_name,target_name,.160,.060)

for i in range(6):
    suffix='' if i==0 else '.%03d'%i
    mounting_return('Jamb captive screw bearing '+str(i),'Jamb captive fastener'+suffix,'Jamb folded cover'+('' if i<3 else '.001'),.016,.016)
for i in (0,2,4,6):
    suffix='' if i==0 else '.%03d'%i
    mounting_return('Access panel captive bearing '+str(i),'Access panel fastener'+suffix,'Serviceable inner access panel'+('' if i<4 else '.001'),.014,.014)
for i,target_name in enumerate(('Cartridge bank formed upright','Shelf retaining lip.002','Cartridge bank formed upright.001','Shelf retaining lip.002')):
    mounting_return('Cartridge bank folded fixing return '+str(i),'Cabinet perimeter screw'+('' if i==0 else '.%03d'%i),target_name,.020,.018)

# Pressed open channels brace the four fixed reserve frame screws. The service
# door moves freely above the lower channel; its original hinge pose is retained.
for z,indices in ((.14,(4,6)),(1.28,(5,7))):
    def chassis_channel(z=z):
        o=profile('Reserve fixed front crosschannel',[
            (-.348,z-.012),(-.264,z-.012),(-.264,z-.009),(-.344,z-.009),
            (-.344,z+.009),(-.264,z+.009),(-.264,z+.012),(-.348,z+.012)],.795,M['blue'],reserve,axis='X')
        supported(o,s.objects['Reserve folded side'])
    mount=group('Reserve fixed front crosschannel '+str(z),chassis_channel,'Reserve folded side')
    for i in indices:retained_contact(s.objects['Cabinet perimeter screw.%03d'%i],mount)
mounting_return('Decon fixture ceiling mounting return','Decon ceiling lamp','Decon ceiling',.100,.045)

# Seat the retained 3 mm telemetry indicator on its screen substrate. Keep its
# exact dimensions, object transform and graphic footprint; its back enters the
# screen by 0.5 mm, representing a fitted display layer rather than a loose strip.
graphic=s.objects['Telemetry status bar.002'];screen=s.objects['Monitor dark face']
points=[graphic.matrix_world@v.co for v in graphic.data.vertices]
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
screen_tree=BVHTree.FromPolygons([screen.matrix_world@v.co for v in screen.data.vertices],[tuple(p.vertices) for p in screen.data.polygons])
shift=screen_tree.find_nearest((lo+hi)/2)[0].y+.0005-hi.y
inverse=graphic.matrix_world.inverted()
vertices=[tuple(inverse@(point+Vector((0,shift,0)))) for point in points]
faces=[tuple(p.vertices) for p in graphic.data.polygons]
replace(graphic,vertices,faces,[M['ochre']])
supports.append({'object':graphic.name,'target':screen.name,'max_gap_m':.001,'max_penetration_m':.002,'kind':'flush_screen_graphic'})
graphic['support_components']=json.dumps([{'label':'Seated telemetry display strip','target':screen.name,'material':M['ochre'].name,'coordinate_parent':console.name}])

# Stored cases bear on paired pressed channels, not on a nearby vertical wall.
# Both case feet receive explicit downward-bearing witnesses on real cap faces.
for i in range(12):
    case=s.objects['Sealed supply case'+('' if i==0 else '.%03d'%i)]
    inverse=cabinet.matrix_world.inverted()
    points=[inverse@(case.matrix_world@Vector(p)) for p in case.bound_box]
    lo=Vector(tuple(min(p[a] for p in points) for a in range(3)));hi=Vector(tuple(max(p[a] for p in points) for a in range(3)))
    shelves=[s.objects['Supply cabinet shelf'+suffix] for suffix in ('','.001','.002')]
    def shelf_top(obj):return max((inverse@(obj.matrix_world@Vector(p))).z for p in obj.bound_box)
    shelf=max((obj for obj in shelves if shelf_top(obj)<lo.z),key=shelf_top)
    bottom=shelf_top(shelf)-.0005;top=lo.z+.0005;x=(lo.x+hi.x)/2;y=(lo.y+hi.y)/2
    feet=[x-(hi.x-lo.x)*.28,x+(hi.x-lo.x)*.28]
    def stock_feet(feet=feet,bottom=bottom,top=top,y=y,lo=lo,hi=hi,shelf=shelf):
        for xx in feet:
            o=profile('Sterile stock pressed bearing channel',[
                (xx-.014,bottom),(xx+.014,bottom),(xx+.014,top),(xx+.012,top),
                (xx+.012,bottom+.002),(xx-.012,bottom+.002),(xx-.012,top),(xx-.014,top)],
                (hi.y-lo.y)-.020,M['steel'],cabinet,axis='Y')
            o.location.y=y;supported(o,shelf)
    mount=group('Sterile stock shelf bearing '+str(i),stock_feet,shelf.name)
    supports.append({'object':case.name,'target':mount.name,'max_gap_m':.001,'max_penetration_m':.002,
        'kind':'stored_stock_downward_bearing','bearing_normal_world':[0,0,1],
        'bearing_points_world':[list(cabinet.matrix_world@Vector((xx+.013,y,lo.z))) for xx in feet]})

for y in (4.20,5.05):
    mounting_return('Organic continuity plaque standoff '+str(y),'Engraved backing ORGANIC CONTINUITY','Inner removable liner.001',.060,.025,(-3.81875,y,2.15))

# The retained release card stays at the cot foot in a real folded chart holder,
# with an outboard return ahead of the cushion and a foot on the bed pan.
def chart_holder():
    o=profile('Recovery foot chart folded holder',[
        (-1.10,.699),(-1.08,.699),(-1.08,.7675),(-.925,.7675),
        (-.925,.7695),(-1.082,.7695),(-1.082,.701),(-1.10,.701)],.198,M['steel'],recovery,axis='X')
    o.location.x=-.32;supported(o,s.objects['Recovery bed pan'])
mount=group('Recovery foot chart holder',chart_holder,'Recovery bed pan')
retained_contact(s.objects['Recovery release slip'],mount)

for i in (1,3,5,7):
    mounting_return('Top fascia captive bearing '+str(i),'Top removable fascia fixing.%03d'%i,'MED_R2 | OCRU stepped cast pressure beam',.018,.018)
for i in (1,7):
    mounting_return('Upper access panel bearing '+str(i),'Access panel fastener.%03d'%i,'Serviceable inner access panel'+('' if i<4 else '.001'),.014,.014)
for z in (1.52,1.99):
    mounting_return('Service latch fixed bearing '+str(z),'Orange latch rail.001','Jamb folded cover.001',.022,.025,(-1.44675,6.59460,z))
mounting_return('Pressure gauge captive spindle','Needle pivot','Ivory instrument dial',.012,.012)

def seat_relief(name,target_name):
    obj=s.objects[name];target=s.objects[target_name]
    bpy.context.view_layer.update();deps_local=bpy.context.evaluated_depsgraph_get()
    ev=target.evaluated_get(deps_local);md=ev.to_mesh()
    tree=BVHTree.FromPolygons([target.matrix_world@v.co for v in md.vertices],[tuple(p.vertices) for p in md.polygons]);ev.to_mesh_clear()
    own=obj.evaluated_get(deps_local);om=own.to_mesh();points=[obj.matrix_world@v.co for v in om.vertices];own.to_mesh_clear()
    centre=sum(points,Vector())/len(points);surface,normal,index,distance=tree.find_nearest(centre)
    minimum=min((point-surface).dot(normal) for point in points)
    world=obj.matrix_world.copy();world.translation+=normal*(.0003-minimum);obj.matrix_world=world
    pose_updates.append(obj.name);bpy.context.view_layer.update()
    supports.append({'object':obj.name,'target':target.name,'max_gap_m':.005,'max_penetration_m':.002,'kind':'seated_surface_art'})
seat_relief('Service jamb narrow edge scuff','Jamb folded cover')
seat_relief('Service jamb narrow edge scuff.002','Jamb folded cover.001')
seat_relief('Meter unit','Ivory instrument dial')
