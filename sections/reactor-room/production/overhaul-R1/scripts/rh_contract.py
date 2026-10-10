"""Contract guard for the hall pass.  Objects the game or the checks bind to must survive every restyle: same name, same pivot, bounding box close.
usage: python rh_contract.py -- snapshot <in.blend> <out.json>        record the contract set of a blend
       python rh_contract.py -- check <contract.json> <blend>         report missing / moved contract objects (exit text 'CONTRACT PASS' or 'CONTRACT FAIL (n)')
Contract set = every EMPTY (ports, pivots, state), every object that carries animation or drivers outside the control room / lift (CR *), and every mesh whose name is UPPER_CASE_WITH_UNDERSCORES
(SCRAM_BUTTON, BANK_A_CARRIAGE, COOLANT_PUMP_START ...).  Empties must stay within 5 cm; meshes within 40 cm on each bbox corner (restyling may change shape, not place)."""
import bpy,sys,json,re
from mathutils import Vector
A=sys.argv[sys.argv.index("--")+1:]; MODE=A[0]
def bbox(o):
    b=[o.matrix_world@Vector(v) for v in o.bound_box]; return [min(v[i] for v in b) for i in range(3)],[max(v[i] for v in b) for i in range(3)]
UP=re.compile(r"^[A-Z0-9]+(_[A-Z0-9]+)+(\.\d+)?$")
def contract(o):
    if o.name.startswith(("CR ","CR_","COL ","RP ","RH ","LP haze","CR haze")): return False
    if o.type=='EMPTY': return True
    if o.animation_data and (o.animation_data.action or o.animation_data.drivers): return True
    return o.type=='MESH' and bool(UP.match(o.name))
if MODE=="snapshot":
    bpy.ops.wm.open_mainfile(filepath=A[1]); d={}
    for o in bpy.data.objects:
        if contract(o):
            lo,hi=bbox(o); d[o.name]={"type":o.type,"loc":list(o.matrix_world.translation),"bbox":[lo,hi]}
    json.dump(d,open(A[2],"w"),indent=0); print("contract objects:",len(d))
else:
    d=json.load(open(A[1])); bpy.ops.wm.open_mainfile(filepath=A[2]); bad=[]
    for n,r in d.items():
        o=bpy.data.objects.get(n)
        if not o: bad.append((n,"missing")); continue
        if r["type"]=='EMPTY':
            if (o.matrix_world.translation-Vector(r["loc"])).length>0.05: bad.append((n,"moved %.2f m"%(o.matrix_world.translation-Vector(r["loc"])).length))
        elif o.type=='MESH':
            lo,hi=bbox(o); dev=max(max(abs(lo[i]-r["bbox"][0][i]),abs(hi[i]-r["bbox"][1][i])) for i in range(3))
            if dev>0.40: bad.append((n,"bbox moved %.2f m"%dev))
    for b in bad[:40]: print("  ",b)
    print("CONTRACT PASS" if not bad else "CONTRACT FAIL (%d of %d)"%(len(bad),len(d)))
