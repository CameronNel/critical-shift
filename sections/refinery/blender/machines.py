"""Seven distinct production stations; dimensions in metres and world-space geometry."""
import math
import bpy
import geometry as g


def mark(machine, points):
    for role,pos in points.items():
        kind = 'control' if role in {'START','STOP','REVERSE','SPEED','EMERGENCY_RELEASE','SAFETY_BYPASS','BELT_SPEED','SCANNER_SENSITIVITY','DIVERTER','RECALIBRATION','MANUAL_OVERRIDE','PRESSURE','TEMPERATURE','INCREASE_HEAT','FILTER_BYPASS','PRESS','HIGH_SPEED','ALIGNMENT','SEAL_STAGE','APPROVE','REJECT','REPROCESS','BLEND','FALSIFY','SEND_UNINSPECTED'} else 'interaction'
        g.marker(machine,role,pos,kind=kind,reach_m=.65)


def loop(x,y,z,w,d):
    return [(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)]


def bolts(name,x,y,z,w,h):
    for sx in [-1,1]:
        for sz in [-1,1]:g.rod(name+'_bolt',(x+sx*w/2,y,z+sz*h/2),(x+sx*w/2,y-.025,z+sz*h/2),.022,'steel',6)


def plate(machine,text,x,y,z,w=.65):
    g.box(machine+'_identity_plate',(x,y,z),(w,.016,.14),'pale',.005)
    g.label(machine+'_identity',text,(x-w*.44,y-.01,z-.033),.066,'ink')


def tray(name,x,y,z,w,d,mat='steel'):
    base=g.box(name+'_base',(x,y,z),(w,d,.04),mat)
    for sy in [-1,1]:g.box(name+'_edge',(x,y+sy*(d/2-.015),z+.065),(w,.03,.13),mat)
    for sx in [-1,1]:g.box(name+'_end',(x+sx*(w/2-.015),y,z+.065),(.03,d,.13),mat)
    return base


def crusher():
    m='CRUSHER';r=g.root(m,(-5.05,4.35,0))
    with g.use('MACHINE_'+m,r):
        g.frame(m,-5.05,4.45,2.40,1.70,1.0)
        g.box('Crusher_cast_bed',(-5.05,4.45,1.04),(2.35,1.64,.20),'teal',.045)
        # Split cast cheek plates frame a real pair of opposed tooth drums.
        for y in [3.89,5.03]:
            g.box('Crusher_cast_cheek',(-5.07,y,1.78),(1.78,.16,1.20),'teal',.06)
            for x in [-5.44,-4.76]:
                g.rod('Crusher_bearing_flange',(x,y-.095,1.82),(x,y+.095,1.82),.235,'steel')
                g.rod('Crusher_bearing_cap',(x,y-.12,1.82),(x,y-.16,1.82),.15,'darksteel')
        for n,x in enumerate([-5.44,-4.76]):
            pivot=g.empty('Crusher_roller_%d_PIVOT'%n,(x,4.46,1.82),moving_part='counterrotating toothed crusher roller',axis='Y')
            with g.use('MACHINE_'+m,pivot):
                g.rod('Crusher_tooth_drum_%d'%n,(x,4.04,1.82),(x,4.89,1.82),.30,'darksteel')
                for row in range(5):
                    for tooth in range(8):
                        a=tooth*math.tau/8+row*.25
                        px,pz=x+.31*math.cos(a),1.82+.31*math.sin(a)
                        o=g.box('Crusher_replaceable_tooth',(px,4.10+row*.17,pz),(.15,.10,.16),'steel',.015)
                        o.rotation_euler[1]=-a
        # Three-sided tapered throat: the south feeder mouth stays genuinely open,
        # including the return belt below its elevated discharge.
        throat_lower=loop(-5.10,4.46,2.04,1.42,.80)
        throat_upper=loop(-5.15,4.30,2.95,1.80,1.42)
        throat=g.mesh('Crusher_feed_throat',throat_lower+throat_upper,[(1,2,6,5),(2,3,7,6),(3,0,4,7)],'teal',.008)
        skin=throat.modifiers.new('Throat sheet thickness','SOLIDIFY');skin.thickness=.035
        # Hood rises behind incoming belt, leaving the south feeder mouth open.
        g.box('Crusher_feed_hood_roof',(-5.15,4.57,3.12),(1.91,1.12,.09),'pale',.03)
        for x in [-6.09,-4.21]:g.box('Crusher_hood_side',(x,4.57,2.75),(.06,1.12,.64),'pale')
        g.box('Crusher_hood_back',(-5.15,5.10,2.75),(1.91,.06,.64),'pale')
        g.box('Crusher_service_hinged_panel',(-5.08,3.785,1.73),(1.12,.075,.60),'darksteel',.025)['moving_part']='hinged service cover'
        for x in [-5.43,-4.71]:g.rod('Crusher_service_latch',(x,3.71,1.63),(x,3.71,1.85),.024,'steel')
        bolts('Crusher_panel',-5.08,3.735,1.73,.97,.44)
        g.box('Crusher_reduction_gearbox',(-6.07,4.35,1.36),(.43,.64,.48),'teal',.04)
        g.rod('Crusher_motor',(-6.06,4.48,1.55),(-6.06,5.12,1.55),.24,'darksteel')
        for y in [4.55,4.66,4.77,4.88,4.99]:g.rod('Crusher_cooling_fin',(-6.06,y,1.55),(-6.06,y+.035,1.55),.262,'steel')
        g.tapered('Crusher_discharge_chute',loop(-3.96,4.50,1.34,.30,.66),loop(-4.75,4.50,1.51,1.11,.85),'steel')
        g.tube('Crusher_dust_extraction',[(-4.38,5.02,1.5),(-4.03,5.16,1.5),(-4.03,5.16,.46)],.095,'darksteel')
        waste=g.box('Crusher_dust_bin',(-4.08,5.15,.23),(.49,.48,.46),'pale',.025);g.support(waste,'Floor','WORLD_-Z',[(-4.08,5.15,0)])
        g.control_panel(m,-3.85,3.20,1.18,['START','STOP','REVERSE','SPEED','EMERGENCY_RELEASE','SAFETY_BYPASS'],1.16)
        g.beam('Crusher_control_stalk',(-3.85,3.29,.08),(-3.85,3.29,1.0),.08,.08)
        foot=g.box('Crusher_control_foot',(-3.85,3.29,.04),(.30,.28,.08),'steel')
        g.support(foot,'Floor','WORLD_-Z',[(-3.85,3.29,0)])
        g.tube('Crusher_control_conduit',[(-3.85,3.29,.22),(-3.85,3.70,.22),(-4.22,3.89,.22),(-4.22,3.89,1.05)],.021,'rubber')
        g.box('Crusher_southeast_service_mount',(-3.97,4.05,1.50),(.13,.32,.73),'teal')
        g.box('Crusher_side_service_panel',(-3.885,4.05,1.65),(.045,.34,.47),'darksteel',.018)['moving_part']='removable side service plate'
        g.rod('Crusher_side_service_latch',(-3.85,3.99,1.54),(-3.85,3.99,1.73),.020,'steel')
        plate(m,'CR-03  /  BREAKER',-5.05,3.795,2.21,1.12)
        g.box('Crusher_state_light',(-4.42,3.79,2.14),(.11,.035,.075),'ready')
        g.box('Crusher_body_detector',(-4.34,4.02,2.48),(.12,.10,.10),'plastic')
        mark(m,{'INPUT':(-5.15,4.2,2.78),'OUTPUT':(-3.85,4.5,1.25),'JAM_CLEARING':(-3.65,3.60,1.60),'TOOTH_DAMAGE':(-3.65,3.65,1.60),'MOTOR_OVERLOAD':(-6.14,3.70,1.40),'ACCESS_PANEL':(-3.65,3.60,1.60),'SERVICE_ACCESS':(-3.65,3.60,1.50),'PROHIBITED_OBJECT_DETECTION':(-4.35,3.91,1.6),'DUST_WASTE':(-4.08,5.15,.45)})


def sorter():
    m='SORTER';r=g.root(m,(-2.35,4.5,0))
    with g.use('MACHINE_'+m,r):
        belt=g.conveyor('Sorter',(-3.85,4.5,1.25),(-.85,4.5,1.25),.66)
        belt['transfer_from']='CRUSHER';belt['transfer_to']='PROCESSOR'
        for x in [-2.95,-2.48]:
            for y in [4.04,4.96]:g.box('Sorter_scanner_upright',(x,y,1.57),(.095,.095,.76),'teal')
        g.box('Sorter_scanner_bridge',(-2.72,4.50,1.94),(.62,1.04,.22),'pale',.035)
        g.box('Sorter_scan_lens',(-2.72,4.50,1.815),(.31,.51,.027),'glass')
        for y in [4.24,4.77]:g.box('Sorter_optical_emitter',(-2.72,y,1.79),(.38,.025,.025),'ready',.002)
        g.box('Sorter_sensor_head',(-2.72,4.005,1.58),(.30,.09,.23),'darksteel')
        pivot=g.empty('Sorter_diverter_PIVOT',(-1.55,4.78,1.34),moving_part='diverter gate',axis='Z')
        with g.use('MACHINE_'+m,pivot):
            g.rod('Sorter_diverter_shaft',(-1.55,4.78,1.24),(-1.55,4.78,1.62),.045,'steel')
            g.beam('Sorter_diverter_gate',(-1.55,4.78,1.39),(-2.10,4.21,1.39),.05,.16,'yellow')
        g.box('Sorter_gate_servo',(-1.55,4.94,1.37),(.27,.25,.22),'darksteel')
        # South discharge drops inside the removable wheeled bin.
        g.tapered('Sorter_reject_slide',loop(-2.05,3.49,.59,.59,.38),loop(-2.05,4.19,1.28,.64,.27),'steel')
        binbase=tray('Sorter_reject_bin',-2.05,3.52,.12,.73,.50,'teal')
        # Floor-contact feet underneath removable bin.
        for x in [-2.30,-1.80]:
            for y in [3.36,3.67]:
                foot=g.box('Sorter_bin_foot',(x,y,.05),(.08,.08,.10),'rubber');g.support(foot,'Floor','WORLD_-Z',[(x,y,0)])
        for y in [3.285,3.755]:g.box('Sorter_bin_wall',(-2.05,y,.34),(.73,.03,.43),'teal')
        for x in [-2.40,-1.70]:g.box('Sorter_bin_wall',(x,3.52,.34),(.03,.49,.43),'teal')
        # Representative rejected pieces physically seated on the bin floor.
        for i in range(3):
            p=(-2.26+i*.20,3.51,.21);o=g.box('Sorter_rejected_inclusion',p,(.14,.18,.14),'ore');g.support(o,binbase,'WORLD_-Z',[(p[0],p[1],.14)],'SURFACE')
        g.control_panel(m,-1.24,3.77,1.02,['BELT_SPEED','SCANNER_SENSITIVITY','DIVERTER','RECALIBRATION','MANUAL_OVERRIDE'],.78)
        g.box('Sorter_calibration_access',(-2.70,4.00,1.50),(.34,.065,.35),'teal')
        plate(m,'SO-04',-2.72,3.985,1.90,.46)
        mark(m,{'INPUT':(-3.85,4.5,1.25),'OUTPUT':(-.85,4.5,1.25),'REJECT_OUTPUT':(-2.05,3.49,.64),'REJECT_BIN':(-2.05,3.30,.55),'CALIBRATION_ACCESS':(-2.72,3.79,1.52),'SERVICE_ACCESS':(-2.62,3.80,1.46),'GATE_FAULT':(-1.57,3.91,1.35)})


def processor():
    m='PROCESSOR';r=g.root(m,(.55,4.45,0))
    with g.use('MACHINE_'+m,r):
        g.frame(m,.55,4.53,1.56,1.45,.67)
        g.rod('Processor_pressure_shell',(.55,4.55,1.00),(.55,4.55,2.51),.64,'teal',48)
        # Polygonal dished end caps, closed individually to avoid a flat aquarium silhouette.
        for name,zs,rs in [('bottom',[.65,.82,1.03],[.18,.50,.64]),('top',[2.50,2.69,2.79],[.64,.48,.17])]:
            verts=[(.55+rad*math.cos(i*math.tau/32),4.55+rad*math.sin(i*math.tau/32),z) for z,rad in zip(zs,rs) for i in range(32)]
            faces=[tuple(range(31,-1,-1))]+[(j*32+i,j*32+(i+1)%32,(j+1)*32+(i+1)%32,(j+1)*32+i) for j in range(2) for i in range(32)]+[tuple(range(64,96))]
            g.mesh('Processor_dished_'+name,verts,faces,'teal',.008)
        for z in [1.04,2.49]:g.torus('Processor_seam_band',(.55,4.55,z),.645,.031,'steel',(0,0,0))
        g.rod('Processor_top_mixer',(.55,4.55,2.76),(.55,4.55,3.08),.16,'darksteel')
        g.box('Processor_mixer_terminal',(.70,4.55,2.94),(.20,.24,.16),'pale')
        g.rod('Processor_access_neck',(.55,4.03,1.71),(.55,3.85,1.71),.32,'steel')
        hatch=g.rod('Processor_sealed_hatch',(.55,3.85,1.71),(.55,3.79,1.71),.35,'pale');hatch['moving_part']='bolted removable pressure hatch'
        for i in range(8):
            a=i*math.tau/8;g.rod('Processor_hatch_bolt',(.55+.30*math.cos(a),3.77,1.71+.30*math.sin(a)),(.55+.30*math.cos(a),3.74,1.71+.30*math.sin(a)),.025,'steel',6)
        g.gauge('Processor_pressure_gauge',(.13,3.90,2.23));g.gauge('Processor_temperature_gauge',(.93,3.90,2.23))
        g.tube('Processor_sorted_feed',[(-.85,4.50,1.25),(-.40,4.50,1.25),(-.40,4.55,2.05),(-.06,4.55,2.05)],.16,'steel')
        # Enclosed powered screw lift raises dry solids to the vessel charge port.
        g.tapered('Processor_screw_intake_boot',loop(-.53,4.50,1.28,.29,.33),loop(-.71,4.50,1.46,.49,.56),'teal')
        g.rod('Processor_screw_lift_casing',(-.40,4.55,1.26),(-.40,4.55,2.21),.185,'teal')
        g.rod('Processor_screw_head_gearbox',(-.40,4.55,2.21),(-.40,4.55,2.35),.21,'darksteel')
        g.rod('Processor_screw_drive_motor',(-.40,4.55,2.35),(-.40,4.55,2.61),.13,'darksteel')
        for z in [2.39,2.44,2.49,2.54]:g.rod('Processor_lift_motor_fin',(-.40,4.55,z),(-.40,4.55,z+.022),.146,'steel')
        for z in [1.52,1.91]:g.box('Processor_screw_support_bracket',(-.17,4.55,z),(.30,.10,.09),'steel')
        screw=g.empty('Processor_screw_PIVOT',(-.40,4.55,1.30),moving_part='enclosed vertical screw conveyor',axis='Z')
        with g.use('MACHINE_'+m,screw):
            g.rod('Processor_screw_shaft',(-.40,4.55,1.30),(-.40,4.55,2.23),.045,'steel')
            pts=[(-.40+.115*math.cos(i*math.tau/24),4.55+.115*math.sin(i*math.tau/24),1.32+i*.88/120) for i in range(121)]
            g.tube('Processor_screw_flight',pts,.037,'steel')
        g.marker(m,'SCREW_LIFT_SERVICE',(-.40,4.15,1.6),kind='repair')
        for x in [-.68,-.41]:g.rod('Processor_feed_flange',(x-.035,4.50,1.25),(x+.035,4.50,1.25),.21,'darksteel')
        g.tube('Processor_coolant_supply',[(1.23,5.04,.25),(1.23,5.04,2.25),(.99,5.04,2.25)],.055,'steel')
        g.tube('Processor_coolant_return',[(1.14,5.18,.25),(1.14,5.18,1.15),(.97,5.03,1.15)],.055,'steel')
        g.tube('Processor_dump_line',[(.55,4.55,.68),(.55,3.72,.68),(.55,3.72,.18)],.095,'darksteel')
        g.valve('Processor_dump_valve',(.55,3.63,.67),.12,'red')
        g.box('Processor_dump_grate',(.55,3.61,.065),(.65,.45,.05),'darksteel')
        for x in [.31,.43,.55,.67,.79]:g.box('Processor_dump_grate_bar',(x,3.61,.10),(.025,.40,.025),'steel')
        g.tube('Processor_product_line',[(1.16,4.55,1.55),(1.71,4.55,1.55),(1.96,4.45,1.42)],.13,'steel')
        # Open annular nozzle flange; its lower rim clears the receiving belt.
        g.torus('Processor_product_nozzle_flange',(1.925,4.464,1.438),.133,.016,'darksteel',(0,math.pi/2,0))
        g.valve('Processor_pressure_trim',(-.07,3.86,1.13),.12,'yellow');g.valve('Processor_temperature_trim',(1.15,3.86,1.13),.12,'teal')
        g.box('Processor_state_light',(.55,3.91,2.30),(.09,.035,.065),'ready')
        plate(m,'PV-05',.55,3.90,2.46,.45)
        mark(m,{'INPUT':(-.85,4.5,1.25),'OUTPUT':(1.96,4.45,1.2),'PRESSURE':(-.07,3.67,1.13),'TEMPERATURE':(1.15,3.67,1.13),'EMERGENCY_DUMP':(.55,3.43,.70),'PROCESSOR_DUMP':(.55,3.61,.20),'SEAL_REPAIR':(.85,3.65,1.6),'SERVICE_ACCESS':(.55,3.60,1.6),'COOLANT_CONNECTION':(1.15,4.98,1.15)})


def dryer():
    m='DRYER';r=g.root(m,(3.10,4.45,0))
    with g.use('MACHINE_'+m,r):
        g.frame(m,3.10,4.53,2.25,1.48,.71)
        # Chamfered insulated tunnel has visible dark inner passage and separate panels.
        cross=[(-.69,.85),(-.69,1.88),(-.46,2.15),(.46,2.15),(.69,1.88),(.69,.85)]
        verts=[(x,4.51+y,z) for x in [1.98,4.22] for y,z in cross]
        faces=[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
        g.mesh('Dryer_insulated_tunnel',verts,faces,'pale',.035)
        for x in [2.02,4.18]:
            g.box('Dryer_portal_header',(x,4.51,1.97),(.14,1.22,.20),'darksteel')
            for y in [3.88,5.14]:g.box('Dryer_portal_side',(x,y,1.41),(.14,.12,.98),'darksteel')
        belt=g.conveyor('Dryer_transfer',(1.96,4.45,1.20),(4.46,4.45,1.20),.52)
        belt['transfer_from']='PROCESSOR';belt['transfer_to']='DRYER'
        for x in [2.25,4.00]:
            for y in [4.25,4.39,4.53,4.67]:g.box('Dryer_thermal_curtain',(x,y,1.58),(.025,.13,.67),'rubber',.002)
        g.box('Dryer_sealed_access_door',(3.11,3.79,1.48),(1.46,.10,.83),'teal',.045)['moving_part']='hinged insulated dryer access'
        g.box('Dryer_door_seal',(3.11,3.735,1.48),(1.34,.022,.71),'rubber',.02)
        g.box('Dryer_door_skin',(3.11,3.71,1.48),(1.28,.022,.65),'teal',.025)
        for x in [2.65,3.57]:g.rod('Dryer_door_cam_latch',(x,3.65,1.40),(x,3.65,1.61),.027,'steel')
        g.rod('Dryer_blower_housing',(3.22,4.76,2.22),(3.22,4.76,2.60),.35,'teal')
        g.rod('Dryer_blower_motor',(3.22,4.76,2.61),(3.22,4.76,2.87),.15,'darksteel')
        g.tube('Dryer_recirculation_duct',[(3.22,4.76,2.42),(3.84,4.76,2.42),(3.84,4.76,2.05)],.15,'steel')
        g.tube('Dryer_exhaust',[(2.45,4.97,2.06),(2.45,5.18,2.54),(2.45,5.18,3.75),(3.16,5.18,3.75),(3.16,6.04,3.75)],.115,'darksteel')
        g.rod('Dryer_exhaust_wall_flange',(3.16,5.95,3.75),(3.16,6.01,3.75),.17,'steel')
        cartridge=g.empty('Dryer_filter_cartridge',(2.38,3.77,1.60),moving_part='slide-out filter cassette',axis='Y')
        with g.use('MACHINE_'+m,cartridge):
            g.box('Dryer_removable_filter',(2.38,3.77,1.60),(.56,.17,.35),'darksteel',.014)
            for x in [2.16+i*.055 for i in range(9)]:g.box('Dryer_filter_pleat',(x,3.67,1.60),(.024,.02,.25),'dirtyfilter',.001)
            g.box('Dryer_filter_pull',(2.38,3.62,1.77),(.25,.06,.025),'steel')
        g.tube('Dryer_filter_intake_duct',[(2.38,3.85,1.60),(2.17,4.06,1.60),(2.17,4.06,2.32),(3.01,4.76,2.32)],.095,'darksteel')
        g.frame('Dryer_output_stand',4.66,4.45,.56,.92,1.08)
        catch=tray('Dryer_dried_output_tray',4.58,4.45,1.14,.48,.81,'teal')
        for y in [4.23,4.44,4.65]:
            o=g.box('Dryer_dried_material_batch',(4.60,y,1.215),(.25,.15,.11),'ore',.019)
            g.support(o,catch,'WORLD_-Z',[(4.60,y,1.16)],'SURFACE')
            o['runtime_type']='dried_material';o['carryable']=True
        g.marker(m,'DRIED_MATERIAL_PICKUP',(4.58,3.93,1.30),kind='carry_pickup')
        g.control_panel(m,3.64,3.53,1.08,['INCREASE_HEAT','MOISTURE_CHECK','FILTER_BYPASS'],.84)
        g.rod('Dryer_sample_port',(4.13,3.94,1.28),(4.13,3.78,1.28),.07,'steel')
        g.box('Dryer_fault_light',(3.91,3.75,1.91),(.075,.035,.075),'amber')
        plate(m,'DR-06',3.40,3.685,1.71,.48)
        mark(m,{'INPUT':(1.96,4.45,1.2),'OUTPUT':(4.46,4.45,1.2),'BLOCKED_FILTER':(2.38,3.55,1.60),'DRYER_FILTER':(2.38,3.55,1.60),'FILTER_REPAIR':(2.38,3.55,1.60),'FIRE_FAULT':(3.13,3.50,1.48),'TEMPERATURE_ACCESS':(3.60,3.34,1.10),'SERVICE_ACCESS':(3.11,3.49,1.48)})


class West:
    """Map front=-Y workshop coordinates to west-facing benches without root rotation."""
    def __init__(self,x,y):self.x=x;self.y=y
    def p(self,a,b,z):return (self.x+b,self.y-a,z)
    def box(self,name,p,size,mat,bevel=.01):return g.box(name,self.p(*p),(size[1],size[0],size[2]),mat,bevel)
    def rod(self,name,a,b,r,mat,verts=24):return g.rod(name,self.p(*a),self.p(*b),r,mat,verts)
    def label(self,name,text,p,size=.05,mat='ink'):return g.label(name,text,self.p(*p),size,mat,(math.pi/2,0,-math.pi/2))
    def marker(self,m,role,p,kind='interaction'):return g.marker(m,role,self.p(*p),kind=kind,reach_m=.65)
    def tray(self,name,p,w,d,mat='steel'):
        a,b,z=p;base=self.box(name+'_base',p,(w,d,.035),mat)
        for sx in [-1,1]:self.box(name+'_rim',(a+sx*(w/2-.015),b,z+.045),(.03,d,.09),mat)
        for sy in [-1,1]:self.box(name+'_rim',(a,b+sy*(d/2-.015),z+.045),(w,.03,.09),mat)
        return base
    def panel(self,m,p,labels,width=.72):
        a,b,z=p;self.box(m+'_Control_enclosure',p,(width,.15,.37),'pale',.025)
        for i,title in enumerate(labels):
            u=a-width*.33+(i%3)*width*.33;v=z+.075-(i//3)*.16
            self.rod(m+'_'+title+'_button',(u,b-.08,v),(u,b-.12,v),.026,'red' if title=='STOP' else 'plastic')
            self.label(m+'_'+title+'_engraving',title.replace('_',' '),(u-.09,b-.081,v-.050),.025)
            self.marker(m,title,(u,b-.17,v),'control')


def fuel(t,name,a,b,z,target=None,empty=False):
    parent=g.empty(name+'_PICKUP_ROOT',t.p(a,b,z),carryable=True,runtime_type='empty_casing' if empty else 'fuel_assembly',moving_part='carryable fuel unit')
    coll='MACHINE_'+('ASSEMBLY' if name.startswith('Assembly') else 'INSPECTION' if name.startswith('Inspection') else 'DISPATCH')
    with g.use(coll,parent):
        if empty:
            n=24;verts=[]
            for h,r in [(0,.085),(.36,.085),(.36,.066),(.024,.066)]:
                verts.extend([t.p(a+r*math.cos(i*math.tau/n),b+r*math.sin(i*math.tau/n),z+h) for i in range(n)])
            faces=[(k*n+i,k*n+(i+1)%n,((k+1)%4)*n+(i+1)%n,((k+1)%4)*n+i) for k in range(4) for i in range(n)]
            g.mesh(name+'_open_sleeve',verts,faces,'fuel',.003)
            t.rod(name+'_dark_inner_floor',(a,b,z+.024),(a,b,z+.03),.066,'darksteel')
            o=t.rod(name+'_bottom',(a,b,z),(a,b,z+.02),.085,'fuel')
        else:
            o=t.rod(name+'_casing',(a,b,z),(a,b,z+.44),.085,'fuel',16)
            for h in [.055,.345]:t.rod(name+'_retention_band',(a,b,z+h),(a,b,z+h+.035),.092,'darksteel',16)
            t.rod(name+'_seal',(a,b,z+.43),(a,b,z+.455),.073,'yellow',16)
            t.rod(name+'_terminal',(a,b,z+.455),(a,b,z+.48),.037,'steel',12)
        if target:g.support(o,target,'WORLD_-Z',[t.p(a,b,z)],'SURFACE')
    return parent


def assembly():
    m='ASSEMBLY';r=g.root(m,(5.40,1.5,0));t=West(5.4,1.5)
    with g.use('MACHINE_'+m,r):
        g.frame(m,5.4,1.5,1.25,2.02,.86)
        deck=t.box('Assembly_worktop',(0,0,.94),(2.03,1.24,.12),'steel',.025)
        for a in [-.54,.54]:
            t.box('Assembly_press_pillar',(a,.24,1.63),(.17,.23,1.31),'teal',.02)
            t.rod('Assembly_guide_column',(a,-.04,1.02),(a,-.04,2.19),.055,'steel')
        t.box('Assembly_crown',(0,.14,2.28),(1.34,.58,.22),'teal',.045)
        t.rod('Assembly_hydraulic_cylinder',(0,.15,2.36),(0,.15,2.72),.17,'darksteel')
        ram=g.empty('Assembly_ram_PIVOT',t.p(0,.12,1.70),moving_part='press ram',axis='Z')
        with g.use('MACHINE_'+m,ram):
            t.rod('Assembly_hydraulic_ram',(0,.15,1.63),(0,.15,2.30),.067,'steel')['moving_part']='press hydraulic ram'
            t.box('Assembly_moving_crosshead',(0,.08,1.73),(1.02,.44,.16),'steel',.02)
            t.rod('Assembly_press_die',(0,.04,1.51),(0,.04,1.66),.14,'darksteel')
        t.box('Assembly_die_nest',(0,-.02,1.045),(.43,.42,.09),'darksteel')
        for a in [-.15,.15]:t.box('Assembly_alignment_fixture',(a,-.02,1.13),(.065,.33,.13),'steel')
        guard=g.empty('Assembly_guard_PIVOT',t.p(-.61,-.35,1.17),moving_part='hinged safety guard',axis='Z')
        with g.use('MACHINE_'+m,guard):
            t.box('Assembly_guard_glazing',(0,-.35,1.64),(1.18,.024,.85),'glass',.006)
            for a in [-.61,.61]:t.box('Assembly_guard_side',(a,-.35,1.64),(.045,.045,.93),'yellow')
            for z in [1.18,2.10]:t.box('Assembly_guard_edge',(0,-.35,z),(1.26,.045,.045),'yellow')
            t.rod('Assembly_guard_handle',(.45,-.41,1.47),(.45,-.41,1.73),.023,'darksteel')
        rack=t.box('Assembly_casing_rack',(-.80,.11,1.055),(.31,.78,.07),'teal')
        for b in [-.13,.11,.35]:fuel(t,'Assembly_empty_casing',-.8,b,1.09,rack,empty=True)
        comp=t.tray('Assembly_component_tray',(.79,.17,1.025),.35,.65)
        for b in [-.04,.15,.34]:
            o=t.rod('Assembly_fuel_component',(.79,b,1.045),(.79,b,1.11),.056,'ore',12);g.support(o,comp,'WORLD_-Z',[t.p(.79,b,1.045)],'SURFACE')
        out=t.tray('Assembly_completed_cradle',(.77,-.34,1.025),.35,.32,'teal');fuel(t,'Assembly_completed_fuel',.77,-.34,1.045,out)
        t.panel(m,(0,-.72,1.09),['PRESS','HIGH_SPEED','ALIGNMENT','SEAL_STAGE','STOP'],.92)
        t.box('Assembly_ID_plate',(0,-.166,2.29),(.70,.018,.12),'pale');t.label('Assembly_identity','FA-07  /  PRESS',(-.30,-.18,2.26),.052)
        for role,p in {'INPUT':(.79,.17,1.13),'CASING_INPUT':(-.80,-.32,1.25),'ALIGNMENT_FIXTURE':(0,-.51,1.14),'JAM_CLEARING':(0,-.53,1.50),'SERVICE_ACCESS':(-.45,-.55,1.52),'OUTPUT':(.77,-.34,1.30),'OUTPUT_PICKUP':(.77,-.55,1.30),'FUEL_OUTPUT':(.77,-.55,1.30)}.items():t.marker(m,role,p)


def inspection():
    m='INSPECTION';r=g.root(m,(5.30,-1.2,0));t=West(5.3,-1.2)
    with g.use('MACHINE_'+m,r):
        g.frame(m,5.3,-1.2,1.32,1.95,.85)
        t.box('Inspection_bench_apron',(0,0,.82),(1.96,1.28,.28),'teal',.025)
        deck=t.box('Inspection_work_surface',(0,0,1.00),(2.02,1.35,.085),'pale',.025)
        t.box('Inspection_scanner_foot',(-.36,.04,1.095),(.56,.57,.105),'darksteel')
        for a in [-.66,-.06]:t.box('Inspection_scanner_upright',(a,.16,1.39),(.095,.15,.66),'teal')
        t.box('Inspection_scanner_crossbar',(-.36,.16,1.75),(.74,.35,.13),'teal',.025)
        t.box('Inspection_sensor_lens',(-.36,.13,1.673),(.25,.19,.025),'glass')
        nest=t.tray('Inspection_fuel_cradle',(-.36,-.08,1.155),.34,.38,'steel');fuel(t,'Inspection_sample_fuel',-.36,-.08,1.175,nest)
        t.box('Inspection_screen_mount',(.38,.34,1.37),(.08,.10,.62),'darksteel')
        t.box('Inspection_results_housing',(.38,.25,1.63),(.58,.13,.40),'darksteel',.025)
        t.box('Inspection_results_display',(.38,.178,1.63),(.50,.009,.30),'screen',.008)
        t.label('Inspection_estimate','EST. PURITY  92%',(.15,.169,1.705),.039,'paper')
        t.label('Inspection_confidence','CONFIDENCE  68%',(.15,.169,1.64),.034,'amber')
        t.label('Inspection_uncertainty','SAMPLE / +/- 7%',(.15,.169,1.58),.033,'paper')
        for i,(name,mat) in enumerate([('APPROVED','teal'),('REJECTED','red'),('REPROCESS','yellow')]):
            a=-.66+i*.64
            tr=t.tray('Inspection_'+name+'_tray',(a,-.48,1.06),.56,.29,mat)
            t.label('Inspection_'+name+'_label',name,(a-.22,-.635,1.092),.035,'paper')
            t.marker(m,{'APPROVED':'APPROVE','REJECTED':'REJECT','REPROCESS':'REPROCESS'}[name],(a,-.71,1.17),'control')
        t.panel(m,(.41,-.83,1.00),['BLEND','FALSIFY','SEND_UNINSPECTED'],.91)
        t.box('Inspection_ID_plate',(-.42,-.675,.85),(.65,.012,.12),'pale');t.label('Inspection_identity','QI-08  /  SAMPLE',(-.72,-.686,.819),.050)
        for role,p in {'INPUT':(-.36,-.37,1.43),'INSPECTION_INPUT':(-.36,-.37,1.43),'OUTPUT':(-.66,-.48,1.22),'DISPATCH_PICKUP':(-.66,-.73,1.22),'SERVICE_ACCESS':(-.68,-.53,1.42),'SCANNER_CALIBRATION':(-.36,-.36,1.60),'OVERRIDE':(.45,-.65,1.30)}.items():t.marker(m,role,p)


def dispatch():
    m='DISPATCH';r=g.root(m,(5.35,-3.45,0));t=West(5.35,-3.45)
    with g.use('MACHINE_'+m,r):
        trolley=g.empty('Dispatch_trolley_PIVOT',(5.35,-3.45,.20),moving_part='fuel delivery trolley',axis='X',runtime_type='carry_cart')
        with g.use('MACHINE_'+m,trolley):
            deck=t.box('Dispatch_trolley_deck',(0,0,.33),(1.20,.80,.09),'teal',.025)
            for a in [-.47,.47]:
                for b in [-.29,.29]:
                    t.rod('Dispatch_castor_swivel',(a,b,.19),(a,b,.28),.055,'steel')
                    wheel=t.rod('Dispatch_rubber_wheel',(a-.038,b,.115),(a+.038,b,.115),.115,'rubber');wheel['moving_part']='swivel wheel'
                    g.support(wheel,'Floor','WORLD_-Z',[t.p(a,b,0)])
            for a in [-.52,.52]:t.rod('Dispatch_handle_upright',(a,.32,.35),(a,.32,1.12),.028,'steel')
            t.rod('Dispatch_push_handle',(-.52,.32,1.12),(.52,.32,1.12),.035,'rubber')
            for a in [-.55,.55]:t.box('Dispatch_sideguard',(a,0,.49),(.05,.79,.26),'teal')
            for b in [-.35,.35]:t.box('Dispatch_endguard',(0,b,.46),(1.10,.04,.20),'teal')
            rack=t.box('Dispatch_fuel_rack',(0,0,.425),(1.03,.59,.10),'darksteel',.015)
            for a in [-.36,0,.36]:
                for b in [-.14,.14]:fuel(t,'Dispatch_loaded_fuel',a,b,.475,rack)
            t.box('Dispatch_ID_plate',(0,-.376,.48),(.60,.014,.13),'pale');t.label('Dispatch_identity','RD-09  /  REACTOR',(-.27,-.385,.447),.042)
        for role,p in {'INPUT':(0,-.58,.75),'OUTPUT':(0,.57,.75),'CARRY_PICKUP':(0,-.58,.77),'DISPATCH':(0,-.66,1.05),'BRAKE':(.46,-.44,.85),'SERVICE_ACCESS':(.50,-.48,.85)}.items():t.marker(m,role,p)
        g.marker(m,'REACTOR_ROUTE',(6.40,-3.45,.2),kind='route',direction='EAST')


def service_details():
    """Small purposeful service clusters, each with an explicit physical support."""
    def workledge(name,x,y,w,d,z):
        g.frame(name,x,y,w,d,z-.075)
        return g.box(name+'_top',(x,y,z-.022),(w,d,.044),'steel',.008)
    def supported_box(name,pos,size,mat,target):
        o=g.box(name,pos,size,mat,.005)
        g.support(o,target,'WORLD_-Z',[(pos[0],pos[1],pos[2]-size[2]/2)],'SURFACE')
        return o
    def sheet(name,x,y,z,target,text,w=.19,d=.24):
        board=supported_box(name+'_board',(x,y,z+.006),(w+.015,d+.018,.012),'darksteel',target)
        g.box(name+'_paper',(x,y,z+.0128),(w,d,.0016),'paper',0)
        g.box(name+'_clip',(x,y+d*.43,z+.017),(.07,.023,.007),'steel')
        g.label(name+'_heading',text,(x-w*.43,y+d*.28,z+.014),.018,'ink',(0,0,0))
        for i in range(5):g.box(name+'_writing',(x,y+.012-i*.025,z+.014),(w*.73,.002,.0004),'ink',0)
        return board
    def glove(name,x,y,z,target):
        o=supported_box(name+'_palm',(x,y,z+.014),(.085,.12,.028),'cloth',target)
        for i in range(4):g.box(name+'_finger',(x-.031+i*.021,y+.083,z+.012),(.018,.07-.008*abs(i-1),.024),'cloth',.007)
        g.box(name+'_thumb',(x+.055,y+.015,z+.013),(.048,.035,.026),'cloth',.008)
        g.box(name+'_cuff',(x,y-.071,z+.012),(.105,.041,.024),'rubber',.006)
        return o
    def wrench(name,x,y,z,target):
        o=supported_box(name+'_handle',(x,y,z+.012),(.024,.18,.024),'steel',target)
        for sign in [-1,1]:
            g.box(name+'_jaw_back',(x,y+sign*.10,z+.012),(.07,.023,.024),'steel')
            for side in [-1,1]:g.box(name+'_jaw',(x+side*.028,y+sign*.13,z+.012),(.016,.07,.024),'steel')
        return o
    with g.use('MACHINE_SORTER',bpy.data.objects['ROOT_SORTER']):
        ledge=workledge('Sorter_calibration_ledge',-3.18,3.70,.60,.42,1.04)
        sheet('Sorter_calibration_clipboard',-3.32,3.70,1.04,ledge,'CAL / 07')
        sample=supported_box('Sorter_calibration_reference',(-3.03,3.74,1.085),(.14,.16,.09),'pale',ledge)
        for i in range(3):g.box('Sorter_reference_density_band',(-3.07+i*.04,3.74,1.132),(.018,.12,.005),'darksteel',0)
        g.marker('SORTER','CALIBRATION_SAMPLE',(-3.03,3.43,1.13),kind='carry_pickup')
    with g.use('MACHINE_PROCESSOR',bpy.data.objects['ROOT_PROCESSOR']):
        ledge=workledge('Processor_service_ledge',.55,3.49,.88,.34,.87)
        gasket=g.torus('Processor_replacement_gasket',(.29,3.49,.883),.085,.013,'rubber',(0,0,0))
        g.support(gasket,ledge,'WORLD_-Z',[(.375,3.49,.87)],'SURFACE')
        wrench('Processor_seal_wrench',.76,3.49,.87,ledge)
        can=g.rod('Processor_seal_lubricant',(.52,3.50,.87),(.52,3.50,1.055),.045,'pale')
        g.support(can,ledge,'WORLD_-Z',[(.52,3.50,.87)],'SURFACE')
        g.rod('Processor_lubricant_cap',(.52,3.50,1.055),(.52,3.50,1.08),.035,'plastic')
    with g.use('MACHINE_DRYER',bpy.data.objects['ROOT_DRYER']):
        ledge=workledge('Dryer_filter_service_ledge',2.50,3.54,.91,.36,.91)
        for x,name,mat in [(2.19,'Spare','paper'),(2.51,'Removed_dirty','dirtyfilter')]:
            frame=supported_box('Dryer_'+name+'_filter_frame',(x,3.54,.935),(.27,.25,.05),'darksteel',ledge)
            for i in range(9):g.box('Dryer_'+name+'_pleat',(x-.10+i*.025,3.54,.967),(.013,.20,.014),mat,.001)
        glove('Dryer_heat_glove',2.80,3.50,.91,ledge)
    with g.use('MACHINE_ASSEMBLY',bpy.data.objects['ROOT_ASSEMBLY']):
        t=West(5.40,1.50);deck=bpy.data.objects['Assembly_worktop']
        # Side of the worktop beside the casing rack, outside the moving guard.
        x,y,z=t.p(-.79,-.44,1.00);glove('Assembly_work_glove',x,y,z,deck)
        x,y,z=t.p(.84,.52,1.00)
        tool=supported_box('Assembly_alignment_tool',(x,y,z+.014),(.11,.17,.028),'steel',deck)
        g.box('Assembly_alignment_tool_prongs',(x+.03,y,z+.048),(.028,.17,.05),'steel')
    with g.use('MACHINE_INSPECTION',bpy.data.objects['ROOT_INSPECTION']):
        t=West(5.30,-1.20);deck=bpy.data.objects['Inspection_work_surface']
        x,y,z=t.p(.80,.13,1.0425);sheet('Inspection_batch_record',x,y,z,deck,'BATCH 041',.19,.24)
        x,y,z=t.p(.80,.44,1.0425)
        sample=supported_box('Inspection_comparison_sample',(x,y,z+.035),(.10,.15,.07),'fuel',deck)


def build():
    for fn in [crusher,sorter,processor,dryer,assembly,inspection,dispatch]:fn()
    service_details()

