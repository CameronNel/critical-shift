"""Small maintained-workplace clusters with registered support contact."""
import bpy, math
import geometry as g

def table(name,x,y,w,d,h=.87):
    g.frame(name,x,y,w,d,h-.09)
    return g.box(name+'_top',(x,y,h-.025),(w,d,.05),'steel',.008)

def paper(name,x,y,z,target,title):
    o=g.box(name,(x,y,z+.001),(.21,.29,.002),'paper',0)
    g.support(o,target,'WORLD_-Z',[(x,y,z)])
    g.label(name+'_print',title,(x-.085,y+.10,z+.0022),.021,'ink',(0,0,0))
    for i in range(6):g.box(name+'_writing',(x,y+.055-i*.024,z+.0023),(.14 if i%2 else .10,.0018,.0003),'ink',0)
    return o

def tool(name,x,y,z,target,length=.35):
    # Open-ended forged wrench lying in a deliberate service tray.
    handle=g.box(name+'_handle',(x,y,z+.014),(.030,length*.7,.028),'steel',.011)
    for sy in [-1,1]:
        yy=y+sy*length*.39
        g.box(name+'_jaw_left',(x-.035,yy,z+.014),(.022,.090,.028),'steel',.005)
        g.box(name+'_jaw_right',(x+.035,yy,z+.014),(.022,.09,.028),'steel',.005)
        g.box(name+'_jaw_back',(x,yy-sy*.034,z+.014),(.064,.024,.028),'steel',.004)
    g.support(handle,target,'WORLD_-Z',[(x,y,z)])
    return handle

def tray(name,x,y,z,w=.48,d=.34,mat='pale'):
    base=g.box(name+'_base',(x,y,z+.015),(w,d,.03),mat,.006)
    for sign in [-1,1]:
        g.box(name+'_rim',(x+sign*(w/2-.012),y,z+.055),(.024,d,.08),mat,.008)
        g.box(name+'_rim',(x,y+sign*(d/2-.012),z+.055),(w,.024,.08),mat,.008)
    return base

def drain(name,x,y,w,d):
    base=g.box(name+'_recess',(x,y,.004),(w,d,.008),'darksteel',0)
    for i in range(int(w/.07)):
        g.box(name+'_grate',(x-w/2+.035+i*.07,y,.008),(.018,d,.012),'steel',.002)
    g.support(base,'Floor','WORLD_-Z',[(x,y,0)])

def build():
    with g.use('REFINERY_UTILITIES'):
        # Two utility circuits and a restrained cable tray; no pipe maze.
        for i,z in enumerate([3.96,4.18]):
            g.tube('Utility_'+str(i),[(-7.03,-1.3,z),(-6.75,-1.3,z),(-6.75,5.72,z),(6.65,5.72,z),(6.65,.4,z),(7.03,.4,z)],.065 if i==0 else .04,'teal' if i==0 else 'steel')
            for x,y in [(-6.99,-1.3),(6.99,.4)]:g.rod('Pipe_wall_flange',(x-.028,y,z),(x+.028,y,z),.11 if i==0 else .085,'darksteel')
            for x in [-5.8,-1.7,2.8,6.2]:
                mount=g.box('Utility_wall_standoff',(x,5.96,z),(.16,.08,.20),'darksteel',.007)
                g.support(mount,'North_wall','WORLD_+Y',[(x,6.,z)],'WALL')
                g.rod('Utility_bracket',(x,5.93,z-.08),(x,5.70,z-.08),.018,'steel')
                g.torus('Utility_pipe_clamp',(x,5.72,z),.075 if i==0 else .048,.01,'darksteel',(0,math.pi/2,0))
        g.tube('Power_trunk',[(6.78,-2.,.4),(6.78,-2.,3.67),(6.78,5.6,3.67),(-6.7,5.6,3.67)],.035,'rubber')
        cabinet=g.box('Utility_cabinet',(-6.875,.35,1.65),(.25,.86,1.10),'pale',.028)
        g.support(cabinet,'West_main','WORLD_-X',[(-7.,.35,1.65)],'WALL')
        g.box('Utility_door',(-6.719,.35,1.65),(.03,.79,1.03),'teal',.016)
        g.rod('Utility_handle',(-6.68,.62,1.56),(-6.68,.62,1.74),.016,'steel')
        g.marker('ROOM','POWER_ISOLATOR',(-6.60,.60,1.5),kind='control')
        for x,y,w,d in [(-5.0,2.7,1.4,.16),(.7,3.22,1.4,.18),(3.65,3.5,.16,1.6),(-5.35,-5.05,1.2,.15)]:drain('Drain',x,y,w,d)
        # Safety corner occupies the front wall, outside the cart sweep.
        for x in [-6.25,-5.55]:
            foot=g.box('Eyewash_support_foot',(x,-5.67,.03),(.19,.19,.06),'steel');g.support(foot,'Floor','WORLD_-Z',[(x,-5.67,0)])
        g.box('Eyewash_base_crossmember',(-5.9,-5.67,.065),(.74,.09,.06),'steel',.008)
        g.rod('Eyewash_stand',(-5.9,-5.67,.05),(-5.9,-5.67,1.05),.047,'steel')
        g.tapered('Eyewash_bowl',[(-6.07,-5.79,.94),(-5.73,-5.79,.94),(-5.73,-5.55,.94),(-6.07,-5.55,.94)],[(-6.21,-5.89,1.04),(-5.59,-5.89,1.04),(-5.59,-5.43,1.04),(-6.21,-5.43,1.04)],'pale')
        for x in [-6.05,-5.75]:g.tube('Eyewash_jet',[(x,-5.76,.95),(x,-5.76,1.16),(x,-5.65,1.16)],.012,'steel')
        g.tube('Emergency_shower',[(-6.4,-5.72,.08),(-6.4,-5.72,2.55),(-5.9,-5.72,2.55)],.035,'steel')
        g.rod('Shower_head',(-5.9,-5.72,2.5),(-5.9,-5.72,2.54),.16,'pale')
        g.tube('Shower_pull',[(-6.25,-5.65,2.48),(-6.25,-5.65,1.42),(-6.10,-5.65,1.42)],.011,'yellow')
        g.marker('ROOM','EMERGENCY_SHOWER',(-6.1,-5.4,1.4),kind='control')
        extinguisher=g.rod('Extinguisher',(-4.5,-5.75,.24),(-4.5,-5.75,.89),.12,'red')
        es=g.box('Extinguisher_support_shelf',(-4.5,-5.84,.21),(.32,.32,.06),'darksteel',.006)
        g.support(es,'South_left','WORLD_-Y',[(-4.5,-6.,.21)],'WALL')
        g.support(extinguisher,es,'WORLD_-Z',[(-4.5,-5.75,.24)],'SURFACE')
        bracket=g.box('Extinguisher_bracket',(-4.5,-5.95,.38),(.30,.10,.10),'darksteel');g.support(bracket,'South_left','WORLD_-Y',[(-4.5,-6.,.38)],'WALL')
        g.tube('Extinguisher_hose',[(-4.5,-5.74,.95),(-4.3,-5.72,.90),(-4.28,-5.73,.50)],.016,'rubber')
        g.box('Extinguisher_handle',(-4.5,-5.73,.95),(.19,.06,.055),'steel',.008)
        g.label('Extinguisher_band','FIRE',(-4.5,-5.621,.63),.055,'paper',(math.pi/2,0,math.pi),align='CENTER')
        spill=g.box('Spill_kit',(-3.65,-5.58,.25),(.48,.48,.50),'yellow',.045);g.support(spill,'Floor','WORLD_-Z',[(-3.65,-5.58,0)])
        g.box('Spill_kit_lid',(-3.65,-5.58,.52),(.51,.51,.055),'darksteel',.014)
        g.label('Spill_kit_label','SPILL KIT',(-3.65,-5.322,.31),.058,'ink',(math.pi/2,0,math.pi),align='CENTER')
    with g.use('REFINERY_PROPS'):
        # Shared service trolley, hand tools and modest paperwork.
        top=table('Tool_trolley',-.1,-4.65,.95,.58,.86)
        for x in [-.47,.27]:
            for y in [-4.85,-4.45]:
                g.rod('Trolley_caster',(x-.026,y,.10),(x+.026,y,.10),.10,'rubber')
        tool('Service_wrench',-.27,-4.7,.86,top)
        paper('Batch_clipboard',.14,-4.64,.86,top,'SHIFT 07 / BATCH LOG')
        g.tube('Trolley_push_handle',[(-.64,-4.87,.71),(-.64,-4.87,1.05),(-.64,-4.43,1.05),(-.64,-4.43,.71)],.017,'steel')
        # Three crates stored together against the south wall.
        for i in range(3):
            x=2.8+i*.67;y=-5.5
            crate=g.box('Service_crate_'+str(i),(x,y,.24),(.58,.56,.48),'teal' if i<2 else 'pale',.025)
            g.support(crate,'Floor','WORLD_-Z',[(x,y,0)])
            g.box('Crate_lid',(x,y,.50),(.61,.59,.045),'darksteel',.008)
            for sx in [-1,1]:g.box('Crate_corner',(x+sx*.255,y-.287,.24),(.06,.035,.43),'darksteel',.004)
            g.box('Crate_handle',(x,y-.291,.37),(.17,.038,.048),'rubber',.01)
        # Crusher tools on a narrow wall rack: attached, handle-scale geometry.
        rack=g.box('Crusher_tool_rack',(-6.875,2.8,1.72),(.25,.95,.12),'darksteel',.006)
        g.support(rack,'West_main','WORLD_-X',[(-7.,2.8,1.72)],'WALL')
        g.tube('Crusher_pry_bar',[(-6.72,2.55,.22),(-6.72,2.55,1.61),(-6.62,2.55,1.75)],.018,'steel')
        g.rod('Shovel_handle',(-6.68,2.95,.43),(-6.68,2.95,1.76),.018,'cloth')
        g.mesh('Shovel_blade',[(-6.73,2.77,.17),(-6.60,2.77,.17),(-6.56,3.13,.17),(-6.73,3.13,.17),(-6.70,2.85,.53),(-6.62,2.85,.53),(-6.6,3.04,.53),(-6.7,3.04,.53)],[(3,2,1,0),(1,5,4,0),(2,6,5,1),(3,7,6,2),(0,4,7,3),(5,6,7,4)],'steel')
        shelf=g.box('Crusher_spares_shelf',(-6.70,4.7,1.02),(.60,.75,.05),'pale',.008)
        g.support(shelf,'West_main','WORLD_-X',[(-7.,4.7,1.02)],'WALL')
        g.box('Spare_crusher_tooth',(-6.60,4.62,1.10),(.18,.21,.11),'steel',.013)
        cloth=g.box('Maintenance_rag',(-6.64,4.90,1.057),(.25,.19,.024),'cloth',.009);g.support(cloth,shelf,'WORLD_-Z',[(-6.64,4.90,1.045)])
