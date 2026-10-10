"""Reactor hall pass, STATIONS: rebuild of every equipment asset in collections 27 R2 STATIONS, 28 R2 HERO STATIONS, 29 R2 DRESSING 2, 22 ASSET KIT 1, 05 PERIMETER EQUIPMENT,
MF WORKFLOW MACHINERY and the WA..WF collections as real machines (housings with seams, hinged doors, vents, flanges with bolt rings, lifting lugs, anchor bolts, nameplates, gauges, lamps,
warning labels) and properly built props (drums, cones, barriers, lockers, bollards, crates), in the hall palette (rh_mats.lib(): dark Audi grey, steel, cast iron, safety colours, rubber, brass).
usage: python rh_stations.py -- <in.blend> <out.blend>
What it does:  (1) re-skins every kept interactive part (breaker levers, valve wheels, gauges, legends, fuel assemblies ...) from the old blue-grey / olive / navy / plum R2 materials to the
RH palette, (2) deletes the old box housings and merged prop meshes it replaces, (3) builds the new machines and props with crk.Kit joined per (group, material) into `RH stations ...` objects.
Helper modules (this pass only): rh_stlib.py (detail kit), rh_st_west.py (generator, reserve power A/B, repair bench), rh_st_east.py (switchgear, desk consoles, turbine, vent damper, waste cask), rh_st_south.py (pump set,
manifold with valves, EC accumulators, sampling kiosk, tool cabinets), rh_st_north.py (fuel rack, receiving table, service post, fuel cart), rh_st_props.py (lockers, chests, barriers, pallets, drums, stools, drains, bollards, extinguishers, ladder).
Materials: rh_mats.lib() plus 'RH stations audi grey' (neutral twin of the shared Audi grey), lamp amber / red / status green (small emitters) and glass.  Objects are joined per (area, material) into 'RH stations <area> <MAT>';
the three isolation valves on the checked suction line are 'Manifold valve cast body <MAT>' (clearance.py lets the pipe run pass through objects with that name).
Untouched on purpose: every EMPTY, port (collection 23 ASSET PORTS), contract mesh (SCRAM_*, COOLANT_PUMP_*, EMERGENCY_COOLING, WASTE_TRANSFER ...), the crane (re-skinned only), the stability
boards (re-skinned only), the state glow material.  Deterministic and re-runnable on hall_base.blend (delete-then-build by name)."""
import bpy,sys,os,math,re,collections
from mathutils import Vector
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import crk,rh_mats
import rh_stlib as S
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
crk.STATE=bpy.data.objects['REACTOR_STATE']
M=rh_mats.lib()
M["AUDI"]=rh_mats.surf("RH stations audi grey",(0.028,0.028,0.029),0.38,0.65,mottle=0.35,streak=0.12,edge=(0.23,0.23,0.24),grime=0.25,scale=2.0,bump=0.0)   # neutral twin of the shared RH dark audi grey (whose blue-ish grime tint trips the cr_verify purple band)
M["LAMP_A"]=rh_mats.emit("RH stations lamp amber",(1.0,0.45,0.04),2.2)
M["LAMP_R"]=rh_mats.emit("RH stations lamp red",(1.0,0.05,0.03),2.2)
M["LAMP_G"]=rh_mats.emit("RH stations lamp status green",(0.25,0.9,0.12),1.6)
def _glass():
    m=bpy.data.materials.get("RH stations glass")
    if m: return m
    m=bpy.data.materials.new("RH stations glass"); m.use_nodes=True; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value=(0.75,0.75,0.72,1); b.inputs['Roughness'].default_value=0.04; b.inputs['Alpha'].default_value=0.10; b.inputs['IOR'].default_value=1.45
    return m
M["GLASS"]=_glass()
OWN=["27 R2 STATIONS","28 R2 HERO STATIONS","29 R2 DRESSING 2","22 ASSET KIT 1","05 PERIMETER EQUIPMENT","MF WORKFLOW MACHINERY","WA A FUEL BAY","WB B WASTE VENT","WC C POWER WALL","WD D COOLING WALL","WE E BACKUP REPAIR WALL","WF F RIM SERVICE HANDLING"]
OBJ=lambda n: bpy.data.objects.get(n)
# ====================================================================== 0. idempotence: remove the objects of a previous run
for o in [o for o in bpy.data.objects if o.name.startswith("RH stations ")]: bpy.data.objects.remove(o,do_unlink=True)
# ====================================================================== 1. re-skin the kept parts
def key_for(o,mname):
    n=o.name.lower()
    if mname=="R2 iron":
        if "lifting eye" in n: return "YELLOW"
        if "guard" in n: return "STEEL"
        if "hub" in n: return "BLACK"
        return "STEEL"
    if mname=="R2 trim rust":
        if "orange band" in n: return "ORANGE"
        if "grip" in n: return "ORANGE"
        if n.startswith("r2 stations station stencil") or "stencil" in n: return "YELLOW"
        if "rim" in n or "spoke" in n: return "RED"
        if "tag" in n: return "YELLOW"
        return "YELLOW"
    if mname=="R2 machine enamel": return "AUDI"
    if mname=="R2 machine olive": return "AUDI_SATIN" if "chart" not in n else "STEEL"
    if mname=="R2 dado navy":
        if "bezel" in n or "ferrule" in n: return "BRASS"
        if "collar" in n or "pivot" in n or "hinge" in n or "closure" in n or "stem packing" in n or "hub" in n or "anchor" in n or "clip" in n or "header flange" in n or "cover" in n or "flange" in n: return "STEEL"
        if "handle" in n or "folded" in n or "socket" in n: return "STEEL"
        if "sample bottle" in n or "waste_transfer" in n: return "GALV"
        return "STEEL"
    if mname=="R2 wall plum lower": return "WHITE" if ("dial" in n or "legend" in n or "merged" in n or "identity" in n) else "WHITE"
    if mname=="R2 pipe lagging":
        if "stem" in n or "spindle" in n or "toggle" in n or "arm" in n or "bus" in n: return "STEEL"
        return "GALV"
    if mname=="R2 cable": return "BLACK"
    if mname=="R2 ink": return "BLACK"
    if mname=="R2 pipe coolant": return "GALV"
    return None
reskinned=0
for cn in OWN:
    c=bpy.data.collections.get(cn)
    if not c: continue
    for o in c.objects:
        if o.type not in('MESH','CURVE','FONT'): continue
        if o.name.startswith(("R2 crane","R2 board")) and False: continue
        for i,m in enumerate(o.data.materials):
            if m is None: continue
            k=key_for(o,m.name)
            if k: o.data.materials[i]=M[k]; reskinned+=1
            elif m.name=="green": o.data.materials[i]=M["LAMP_G"]; reskinned+=1
            elif m.name=="R2 status lamp": o.data.materials[i]=M["LAMP_R"]; reskinned+=1
            elif m.name=="R2 lamp amber": o.data.materials[i]=M["LAMP_A"]; reskinned+=1
            elif m.name=="R2 floor tile": pass
        if o.type=='MESH' and any(("dial" == o.name.split(".")[-1].split(" ")[0]) for _ in [0]) and False: pass
# dial faces (white) and valve wheels (safety red) by name
for o in bpy.data.objects:
    if o.type=='MESH' and re.search(r"\.dial(\.\d+)?$",o.name) and o.data.materials: o.data.materials[0]=M["WHITE"]
    if o.type=='CURVE' and re.search(r"\.(rim|spoke)(\.\d+)?$",o.name) and o.data.materials: o.data.materials[0]=M["RED"] if ("COOLANT" in o.name or "TURBINE" in o.name or "VENT" in o.name) else M["ORANGE"]
    if o.type=='CURVE' and re.search(r"needle",o.name) and o.data.materials: o.data.materials[0]=M["RED"]
    if o.type=='MESH' and re.search(r"(MF\d+ .*(ENABLE|START)$)",o.name) and o.data.materials: pass
# ====================================================================== 2. delete what is rebuilt
def kill(o):
    me=o.data if o.type=='MESH' else None; bpy.data.objects.remove(o,do_unlink=True)
    if me and me.users==0: bpy.data.meshes.remove(me)
KILL_PREFIX=("Manifold valve cast body","Manifold blind service cover","Manifold support","11 manifold skid","Header flange","Pump suction","ECCS ","Pump discharge neck","Pump discharge formed","Supply riser","Return riser","Turbine supply riser","ECCS maintained",
             "Vent valve bonnet","Throttle actuator support","Sample bottle alcove","Manifold local valve tag","14 RESERVE POWER.service door.handle","WB B vent connected riser","MERGED 22 ASSET",
             "Turbine load.","Containment sensor.","Sampling pressure.","Pump suction gauge.","EC-1.pressure","EC-2.pressure","04 WASTE.pressure","Coolant pump identification","WF F sample pipe clip","WF F pipe clip bracket",
             "08 GRID DEMAND.front access.handle","03 BANK CONTROL.front access.handle","08 GRID DEMAND.folded cheek edge","03 BANK CONTROL.folded cheek edge")
for cn in ("28 R2 HERO STATIONS","22 ASSET KIT 1"):
    for o in list(bpy.data.collections[cn].objects): kill(o)
for o in list(bpy.data.collections["29 R2 DRESSING 2"].objects):
    if o.name.startswith("R2 dress dress"): kill(o)
for o in list(bpy.data.collections["27 R2 STATIONS"].objects):
    if o.name.startswith("R2 stations bollard"): kill(o)
for cn in OWN:
    c=bpy.data.collections.get(cn)
    if not c: continue
    for o in list(c.objects):
        if o.name.startswith(KILL_PREFIX): kill(o)
# the reserve-power doors get new handles; the repair-bench plate moves to the shortened bench
for n in ("Repair identity","Repair identity.legend"):
    o=OBJ(n)
    if o and not o.get("rh_moved"): o.location.y+=0.30; o["rh_moved"]=1
# ====================================================================== 3. geometry
ST=bpy.data.collections.get("27 R2 STATIONS")
def plinth(K,g,x0,x1,y0,y1,h=0.06,m='CONC_DARK'):
    K.bx((g,m),x0,x1,y0,y1,0.0,h,0.012)
import rh_st_west as W, rh_st_east as E, rh_st_south as SO, rh_st_north as N, rh_st_props as P
import rh_support_registry as SUPPORT
SUPPORT.reset('stations props')
K=crk.Kit(); Kv=crk.Kit()
W.generator(K); W.reserve(K,'A',2.73,4.27,2.81,3.74,'l0',vent=(3.80,4.20)); W.reserve(K,'B',-5.52,-4.48,-5.44,-4.56,'l0'); W.bench(K); N.west_cart(K)
E.switchgear(K)
E.console(K,'grid',10.66,0.55,math.pi,1.28,0.93,0.25,2.23,0.27,0.17,0.65,[0.55-0.54,0.55-0.76,0.55-0.98],None,(0.45,0.55,-0.45,-0.55))
E.turbine(K); E.vent(K); E.waste(K)
SO.pump(K); SO.manifold(K,Kv); SO.ec(K); SO.sampler(K); SO.south_cabinets(K)
N.fuel_rack(K); N.fuel_table(K); N.service_post(K)
E.console(K,'bank',3.65,10.70,-math.pi/2,1.78,1.01,0.28,2.04,0.42,0.28,0.685,[x-3.65 for x in (3.06,3.34,3.63,3.92,4.21)],(0.40,-0.05),(-0.75,-0.65,0.70,0.80))
# props
for o,(yaw,m) in (((-7.105-0.148,-9.345-0.148),(math.radians(45),'YELLOW')),):
    P.locker_bank(K,o,yaw,3,0.42,'YELLOW','sw')
P.locker_bank(K,(4.69,-10.78),math.pi/2,3,-0.42,'ORANGE','s')       # local y runs to -x after the 90 degree turn: step negative keeps the row at x 4.69, 5.11, 5.52 -> mirrored below
P.locker_bank(K,(10.78,1.38),math.pi,3,-0.42,'RED','e')
for (x,y,yaw) in ((-6.41,9.94,-math.pi/4),(-7.47,8.90,-math.pi/4),(-9.94,-6.40,math.pi/4)): P.tool_chest(K,x,y,yaw,'RED' if x>-8 else 'ORANGE')
for (x,y,yaw) in ((-6.8,5.2,math.radians(108)),(7.09,-0.29,math.radians(108)),(3.40,5.60,math.radians(104))):
    P.barrier(K,x,y,yaw); P.barrier(K,x+.62*math.cos(yaw+math.pi/2),y+.62*math.sin(yaw+math.pi/2),yaw)
P.spill_pallet(K,-3.49,5.30,1.34,1.42); P.spill_pallet(K,6.85,-3.34,1.34,1.42)
for (x,y,m,z) in ((-3.84,4.93,'GALV',0.135),(-3.14,4.93,'YELLOW',0.135),(-3.84,5.67,'RED',.135),(-3.14,5.67,'RED',.135),(6.52,-3.70,'GALV',0.135),(7.18,-3.70,'YELLOW',0.135),(6.52,-2.98,'RED',.135),(7.18,-2.98,'GALV',.135)):
    S.drum(K,'drum',x,y,m,0.88,0.29,'STEEL',z)
for (x,y) in ((7.0,3.07),(1.7,5.8)): P.stool(K,x,y)
for (x,y,yaw) in ((5.8,-5.0,-0.35),(-4.75,-3.9,0.35),(-5.2,3.1,-0.1),(-1.9,6.5,0.5),(3.65,-6.5,0.5),(-6.95,-.60,0)): P.drain(K,x,y,yaw)
BOLL=[(9.0,-2.6),(9.0,1.6),(8.3,-5.7),(8.3,-1.95),(-8.0,-4.75),(-8.0,-2.6),(-8.75,3.0),(-8.75,4.1),(-8.75,-5.8),(-8.75,-4.6),(-5.7,8.75),(-2.5,8.75),(-10.0,6.4),(-7.95,6.4),(-7.95,8.5),(2.4,9.4),(4.9,9.4),(8.6,5.7),(10.5,5.7),(0.85,-7.85),(4.3,-7.85),(-4.3,-7.8),(8.78,9.68),(6.48,9.73),(5.76,7.71),(8.8,6.73)]
BOLL[0]=(8.62,-2.6)
BOLL[3]=(8.3,-1.56)
BOLL[22]=(9.1,7.1)
for (x,y) in BOLL: P.bollard(K,x,y)
for (x,y) in ((5.12,3.8),(-0.65,6.65),(5.07,-4.0),(5.50,-3.10),(4.77,-7.08)): S.cone(K,'cone',x,y)
P.extinguisher(K,5.75,-10.70,'+y'); P.extinguisher(K,10.70,3.35,'-x'); P.extinguisher(K,-5.75,10.70,'-y'); P.ladder(K,10.52,4.55)
AREA={}
for area,gs in (("west","gen resA resB bench cart"),("east","grid turb vent waste"),("south","pump mani ec samp tcab"),("north","bank frack ftab spost"),("props","lock chest barr drum stool drain boll cone ext ladd")):
    for g_ in gs.split(): AREA[g_]=area
AREA['pal']='spill pallets'
# Keep cone surfaces addressable by the scoped finishing pass.
AREA['cone']='props cone'
SUPPORT.reset('stations equipment')
for group in ('gen','resA','resB','bench','grid','turb','vent','waste','pump','mani','ec','samp','tcab','bank','frack','ftab','spost','cone'):
    anchors=[]
    for (g_,mk),bm in K.bm.items():
        if g_!=group: continue
        bm.normal_update()
        for f in bm.faces:
            if f.normal.z<-.98 and all(abs(v.co.z)<.00001 for v in f.verts):
                anchors.append(tuple(f.calc_center_median()))
    subject='RH stations '+AREA.get(group,group)
    SUPPORT.register('stations equipment',group,subject,'RH pool coping CONC_POUR' if group=='samp' else 'R2 floor',anchors)
SUPPORT.register('stations equipment','fuel cart caster seats','RH stations west','R2 floor',[(x,y,0) for x,y in ((-9.72,6.78),(-9.72,8.12),(-8.28,6.78),(-8.28,8.12))])
def regroup(K):
    """join the per-machine groups into one object per (area, material): keeps the hall's object count low"""
    K2=crk.Kit()
    for (g_,mk),bm in list(K.bm.items()):
        tgt=K2.get((AREA.get(g_,g_),mk)); me=bpy.data.meshes.new("_t"); bm.to_mesh(me); tgt.from_mesh(me); bpy.data.meshes.remove(me); bm.free()
    return K2
K=regroup(K)
coll=bpy.data.collections["27 R2 STATIONS"]
NEW=K.build(coll,"RH stations",M)
NEWV=Kv.build(coll,"Manifold",M)
print("RH stations objects",len(NEW)+len(NEWV),"tris",sum(len(p.vertices)-2 for o in NEW+NEWV for p in o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=DST)
