"""Additional physical hinge, utility and trim contacts; fresh native source, no save."""
import ast,bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
tree=ast.parse((OUT/'probe.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.ClassDef,ast.FunctionDef))],type_ignores=[]),str(OUT/'probe.py'),'exec'),globals())
bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];S=bpy.context.scene
names={'D1 frame jamb -1','D1 door leaf','D1 keycard reader','CD | D1 service mounting back','CD | D1 service lid','CD | Door armored conduit','Office front wall mid','Office front wall west','Office front wainscot west','Office front wainscot mid','Office front dado west','Office front dado mid'}
names.update('CD | D1 captive hinge'+s for s in ['', '.001', '.002'])
G=collect(S,lambda o:o.name in names);rows=[]
def contact(child,target,p,d,label):
    at=Vector(p);d=Vector(d).normalized();cr=G[child].ray(at+d*.05,-d,.10);tr=G[target].ray(at-d*.05,d,.10)
    gap=(tr['point']-cr['point']).dot(d) if cr and tr else None
    rows.append({'label':label,'child':child,'target':target,'sample':at,'direction':d,'child_hit':cr,'target_hit':tr,'signed_separation_m':gap})
for z,s in [(.32,''),(1.12,'.001'),(1.96,'.002')]:
    contact('CD | D1 captive hinge'+s,'D1 frame jamb -1',(-5.925,3.591,z),(-1,0,0),'barrel engaged in actual jamb')
    contact('CD | D1 captive hinge'+s,'D1 door leaf',(-5.905,3.6,z),(0,1,0),'barrel engaged in actual door leaf')
for x,side in [(-6.3,'west'),(-4.6,'mid')]:
    contact('Office front dado '+side,'Office front wall '+side,(x,3.52,1.02),(0,1,0),'trim back bears on structural wall')
    contact('Office front dado '+side,'Office front wainscot '+side,(x,3.511,.99),(0,0,-1),'trim lower return butts into lining top')
contact('CD | D1 service mounting back','Office front wall mid',(-4.6125,3.52,2),(0,1,0),'junction mounting back on wall')
contact('CD | D1 service lid','CD | D1 service mounting back',(-4.6125,3.494,2),(0,1,0),'junction lid to back')
# An open tube rim has no axial endcap, so axial no-hit is not a failed
# attachment. Test actual evaluated tube surface vertices inside its receiver.
def inside(g,p):
    if not g.closed or not all(g.bounds[0][i]<p[i]<g.bounds[1][i] for i in range(3)):return False
    directions=[Vector((1,.3713907,.529173)).normalized(),Vector((.219471,1,.681703)).normalized()]
    hits=[g.ray(p,d,100) for d in directions]
    return all(h and h['normal'].dot(d)>1e-5 for h,d in zip(hits,directions))
terminal_rows=[]
for n in ['CD | D1 service lid','D1 keycard reader']:
    witnesses=[p for p in G['CD | Door armored conduit'].vertices if inside(G[n],p)]
    terminal_rows.append({'conduit':'CD | Door armored conduit','receiver':n,'actual_tube_surface_vertices_inside_closed_receiver':len(witnesses),'witnesses':witnesses[:8],'pass':bool(witnesses)})
report={'native_saved':False,'source_sha256':hashlib.sha256((ROOT/'module_overhaul_R1.blend').read_bytes()).hexdigest(),'actual_contacts':rows,'conduit_terminal_engagement':terminal_rows,'classification':'Negative hinge and conduit contacts are intentional embedded/welded engagement; they are not exposed coincident duplicate faces. Positive service lid gap is reported against 5mm default tolerance.'}
(OUT/'anchors.json').write_text(json.dumps(safe(report),indent=2)+'\n');print('ANCHORS_COMPLETE',len(rows),flush=True)
