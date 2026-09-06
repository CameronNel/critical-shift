"""Compact refinery envelope, designed thresholds and practical fixture housings."""
import math, bpy
import geometry as g

def wall(name,pos,size):
    o=g.box(name,pos,size,'wall',.012);o['collision_role']='architecture';return o

def build():
    with g.use('REFINERY_ARCHITECTURE'):
        floor=g.box('Floor',(0,0,-.13),(14,12,.26),'concrete',0)
        floor['room_width_m']=14.;floor['room_depth_m']=12.
        ceiling=g.box('Ceiling',(0,0,4.92),(14.6,12.6,.24),'wall',.008)
        wall('North_wall',(0,6.15,2.4),(14.6,.3,4.8))
        wall('West_front_pier',(-7.15,-5.55,2.4),(.3,.9,4.8))
        wall('West_main',(-7.15,1.925,2.4),(.3,8.15,4.8))
        wall('West_header',(-7.15,-3.65,3.96),(.3,2.8,1.68))
        wall('East_front_pier',(7.15,-5.55,2.4),(.3,.9,4.8))
        wall('East_main',(7.15,1.925,2.4),(.3,8.15,4.8))
        wall('East_header',(7.15,-3.65,3.96),(.3,2.8,1.68))
        wall('South_left',(-5.075,-6.15,2.4),(4.15,.3,4.8))
        wall('South_right',(3.425,-6.15,2.4),(8.05,.3,4.8))
        wall('South_header',(-1.8,-6.15,3.72),(2.4,.3,2.16))
        # Broad shallow mineral panel joints and washable lower course.
        for x in [-6,-3,0,3,6]:
            g.box('North_panel_reveal',(x,5.989,2.91),(.015,.024,3.65),'darksteel',0)
        g.box('North_dado',(0,5.98,.64),(14,.04,1.28),'dado',.005)
        g.box('North_steel_skirt',(0,5.94,.10),(14,.08,.20),'darksteel',.008)
        for x in [-6.98,6.98]:
            g.box('Side_dado',(x,1.925,.64),(.04,8.15,1.28),'dado',.005)
            g.box('Side_skirt',(x*.995,1.925,.09),(.08,8.15,.18),'darksteel',.008)
            for y in [-1.6,1.2,4.1]:
                g.box('Column_pilaster',(x*.984,y,2.4),(.14,.24,4.8),'pale',.012)
                g.box('Column_impact_guard',(x*.977,y,.42),(.19,.31,.84),'darksteel',.015)
        for y in [-4.8,-.6,3.6]:
            # Flush-top structural ribs, quiet ceiling fields between fixtures.
            g.box('Ceiling_crossbeam',(0,y,4.72),(14,.22,.16),'darksteel',.004)
            for x in [-6.8,6.8]:g.box('Ceiling_knee',(x,y,4.45),(.2,.28,.56),'darksteel',.01)
        for x in [-4,0,4]:
            g.box('Floor_maintenance_seam',(x,0,.0006),(.008,11.8,.0012),'darksteel',0)
        for y in [-3,1.8,5.7]:g.box('Floor_maintenance_seam',(0,y,.0006),(13.8,.008,.0012),'darksteel',0)
        patch=g.mesh('Concrete_replacement_patch',[(-.5,-3.1,.001),(1.3,-3.0,.001),(1.52,-4.25,.001),(-.4,-4.36,.001)],[(0,1,2,3)],'patch')
        g.support(patch,floor,'WORLD_-Z',[(-.1,-3.5,.001)])
        for points in [[(-6.9,2.6,.001),(-6.4,2.68,.001),(-6.26,2.5,.001),(-6.0,2.56,.001)],[(1.3,-3.,.001),(1.51,-2.78,.001),(1.7,-2.76,.001)]]:
            g.tube('Localized_repair_crack',points,.003,'darksteel')
        # Route only at its edges: wide center floor remains quiet.
        for y in [-.62,1.62]:
            for x in [-2.8,-1.5,-.2,1.1,2.4,3.35]:g.box('Worn_route_edge',(x,y,.0015),(.6,.035,.003),'yellow',0)
        for x,y in [(-1.8,-4.7),(3.15,-3.65)]:
            v=[(x-.16,y-.24,.002),(x+.16,y-.24,.002),(x+.16,y+.04,.002),(x+.30,y+.04,.002),(x,y+.35,.002),(x-.30,y+.04,.002),(x-.16,y+.04,.002)]
            if x>0:v=[(x+(p[1]-y),y-(p[0]-x),p[2]) for p in v]
            g.mesh('Floor_route_arrow',v,[(0,1,2,3,4,5,6)],'yellow')
        # Door dimensions stored on non-rendering architecture markers.
        portal('MINE',-7,-3.65,2.6,3.0,True)
        portal('REACTOR',7,-3.65,2.6,3.0,True)
        portal('ENTRY',-1.8,-6,2.4,2.6,False)
        g.label('Section_identity','02 / REFINING',(0,5.94,3.30),.27,'ink',align='CENTER')
        g.label('Section_subtitle','MATERIAL RECOVERY & FUEL FABRICATION',(0,5.941,3.13),.065,'ink',align='CENTER')
    with g.use('REFINERY_VALIDATION'):
        route=g.empty('PRIMARY_ROUTE',(0,.5,0),clear_width_m=2.2,bounds=[-3.35,3.7,-.6,1.6,.08,2.15])
    return floor,ceiling

def portal(name,x,y,w,h,side):
    if side:
        for sign in [-1,1]:
            g.box(name+'_door_jamb',(x,y+sign*(w/2+.07),h/2),(.30,.14,h),'darksteel')
            g.box(name+'_hazard_bollard',(x*.984,y+sign*(w/2+.07),.52),(.25,.25,1.04),'yellow',.025)
        g.box(name+'_door_lintel',(x,y,h+.085),(.32,w+.28,.17),'darksteel')
        # Retracted roller shutter and track, leaving a real through opening.
        g.rod(name+'_shutter_drum',(x,y-w/2,h+.32),(x,y+w/2,h+.32),.20,'steel')
        for sign in [-1,1]:g.box(name+'_slide_track',(x+.02,y+sign*(w/2+.03),h/2),(.07,.045,h),'steel',.003)
        # Short external sill owns safe cart approach; no extra interior corridor.
        g.box(name+'_external_sill',(x+(-.55 if x<0 else .55),y,-.13),(1.1,w,.26),'concrete',0)
        # A short architectural reveal makes the open connector read with depth.
        outside=x+(-.55 if x<0 else .55)
        for sign in [-1,1]:g.box(name+'_threshold_return',(outside,y+sign*(w/2+.11),1.52),(1.1,.18,3.04),'dado',.01)
        g.box(name+'_threshold_soffit',(outside,y,3.09),(1.1,w+.4,.16),'darksteel',.01)
        rot=(math.pi/2,0,math.pi/2 if x<0 else -math.pi/2)
        pos=(x+(.18 if x<0 else -.18),y,h+.69)
        g.label(name+'_navigation',name+'  >',pos,.18,'ink',rot,align='CENTER')
    else:
        for sign in [-1,1]:g.box(name+'_jamb',(x+sign*(w/2+.065),y,h/2),(.13,.3,h),'darksteel')
        g.box(name+'_lintel',(x,y,h+.07),(w+.26,.3,.14),'darksteel')
        g.label(name+'_navigation','PERSONNEL',(x,y+.17,h+.25),.12,'ink',(math.pi/2,0,math.pi),align='CENTER')
    with g.use('REFINERY_VALIDATION'):
        g.empty('Door_'+name.title(),(x,y,0),width_m=w,height_m=h)
    g.marker('DISPATCH' if name=='REACTOR' else 'RECEIVING' if name=='MINE' else 'ROOM',name+'_ROUTE',(x,y,0),kind='route')

def feeder():
    root=g.root('FEEDER')
    a=(-5.15,-1.25,.32);b=(-5.15,4.2,2.78)
    with g.use('REFINERY_CONVEYORS',root):
        belt=g.conveyor('FEEDER',a,b,.76,support_ts=(.06,.50,.78),motor_at='tail')
        belt['transfer_from']='RECEIVING';belt['transfer_to']='CRUSHER'
        from mathutils import Vector
        axis=(Vector(b)-Vector(a)).normalized()
        normal=Vector((0,-axis.z,axis.y))
        for i in range(21):
            p=Vector(a)+(Vector(b)-Vector(a))*(i/21)+normal*.055
            cleat=g.box('FEEDER_cleat',p,(.70,.048,.10),'rubber',.006)
            cleat.rotation_euler.x=math.atan2(axis.z,axis.y)
        for sx in [-1,1]:
            g.beam('FEEDER_side_skirt',(a[0]+sx*.43,a[1],a[2]+.10),(b[0]+sx*.43,b[1],b[2]+.10),.035,.24,'teal')
        for t in [.22,.44,.68]:
            p=Vector(a)+(Vector(b)-Vector(a))*t+normal*.08
            g.rod('Consolidated_ore_batch',p-Vector((.2,0,0)),p+Vector((.2,0,0)),.085,'ore',12)
        g.label('Feeder_access_note','ISOLATE BEFORE CLEARING',(-4.705,.20,.83),.058,'paper',(math.pi/2,0,-math.pi/2))
    g.marker('FEEDER','INPUT',a,kind='transfer');g.marker('FEEDER','OUTPUT',b,kind='transfer')
    g.marker('FEEDER','BELT_TENSION',(-4.53,-.58,.7),kind='repair')
    g.marker('FEEDER','SERVICE_ACCESS',(-4.30,.40,1.15),kind='service')
    return root
