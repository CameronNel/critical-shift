"""Read-only final validator, loaded library and directed aperture witnesses."""
import bpy, json, hashlib, importlib.util, argparse
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).parent;DOCK=OUT.parents[3]
EXPECTED='dc608cae0a42303e614f2db3dc0cd9d50e4366dc738ac57c35957c6df34e0331'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(bpy.data.filepath)==EXPECTED
spec=importlib.util.spec_from_file_location('vd',DOCK/'validate_dock.py')
vd=importlib.util.module_from_spec(spec);spec.loader.exec_module(vd)
v=vd.Validator(argparse.Namespace(interface=str(DOCK/'contracts/interface.json'),expected_stage='full'))
v.run();v.report['passed']=not v.report['errors'];v.report['summary']={'passed_checks':sum(r['status']=='pass' for r in v.report['checks']),'failed_checks':sum(r['status']=='fail' for r in v.report['checks']),'failures':len(v.report['errors']),'warnings':len(v.report['warnings'])}
(OUT/'validator-independent.json').write_text(json.dumps(vd.json_safe(v.report),indent=2))
print('VALIDATOR_INDEPENDENT',v.report['summary'],flush=True)
native=json.loads((OUT/'native-independent.json').read_text())
native['libraries']=[{'stored_path':lib.filepath,'resolved':str(Path(bpy.path.abspath(lib.filepath)).resolve()),'exists':Path(bpy.path.abspath(lib.filepath)).is_file(),'sha256':sha(bpy.path.abspath(lib.filepath))} for lib in bpy.data.libraries]
native['library_resolution_method']='Loaded Library.filepath values normalized relative to current native source; lib.parent is provenance only. Earlier script parent-based path calculation was corrected before verdict.'
(OUT/'native-independent.json').write_text(json.dumps(native,indent=2))
shapes=v.shapes;bn=v.by_name
def hitrow(hit):return {'object':hit['shape'].name,'point':list(hit['point']),'normal':list(hit['normal']),'distance_m':hit['distance']} if hit else None
def ray(label,objects,point,direction,length):
    r=vd.nearest_ray([bn[n] for n in objects],Vector(point),Vector(direction),length)
    return {'label':label,'point':point,'direction':direction,'hit':hitrow(r)}
rays=[]
for label,x,y in [('P1',0,-.112),('D1',-5.4,3.6),('D2',-5.4,9.6),('P2',0,15.85),('SCANNER',0,7)]:
    prefixes={'P1':['South wall west','South wall east','South lintel P1'],'D1':['D1 frame jamb -1','D1 frame jamb 1','D1 frame head','CD | D1 architectural transom'],'D2':['D2 frame jamb -1','D2 frame jamb 1','D2 frame head'],'P2':['P2 frame jamb -1','P2 frame jamb 1','P2 frame head lintel'],'SCANNER':['Scanner portal column -1','Scanner portal column 1','Scanner portal lintel']}
    names=[n for n in prefixes[label] if n in bn]
    for direction in [(-1,0,0),(1,0,0),(0,0,1)]:rays.append(ray(label,names,(x,y,1.1),direction,6))
for y in [6.55,7.65,8.75]:
    for direction in [(-1,0,0),(1,0,0),(0,0,1)]:rays.append(ray('CARGO rigid liner at '+str(y),['Lead tunnel main body','Lead tunnel inner chamber'],(4.65,y,1.25),direction,2))
engagement=[]
for a,b,p in [('Scanner column inset -1','Scanner portal column -1',(-.77,7,1.35)),('Key box glass','Office key box cabinet',(-3,9.47,1.5)),('Authority stamp rubber base','CD | Stamping rubber pad',(-2.95,3.42,1.048))]:
    if b in bn:
        aa,bb=bn[a],bn[b];engagement.append({'a':a,'b':b,'point':p,'b_contains_point':bb.contains(Vector(p)),'triangle_overlap_pairs':len(aa.bvh.overlap(bb.bvh))})
materials={s.name:[m.name for m in s.obj.data.materials if m] for s in shapes}
coplanar=json.loads((OUT/'coplanar-duplicates.json').read_text());selected=[]
targets=[{'Terminal monitor housing','Terminal screen face'},{'North lintel P2','P2 frame head lintel'},{'North wall east','P2 frame jamb 1'},{'North wall west','P2 frame jamb -1'},{'Floor slab','P1 corridor floor'},{'Drainage trench recess','Floor slab'},{'D2 frame jamb 1','Office rear wall east'}]
for row in coplanar['axis_planar_overlap']:
    if set(row['objects']) not in targets:continue
    if row['plane'][0:2] not in [[0,-1],[0,1],[1,-1],[2,1]]:continue
    probes=[]
    for w in row['witnesses']:
        axis,sign,d=row['plane'];offset=Vector((0,0,0));offset[axis]=sign*.0001;p=Vector(w['point'])+offset
        contained=[s.name for s in shapes if s.name not in row['objects'] and s.contains(p)]
        probes.append({**w,'100um_outside_point':list(p),'other_closed_solids_containing_outside_point':contained})
    selected.append({**row,'material_families':{n:materials[n] for n in row['objects']},'exposure_probes':probes})
(OUT/'aperture-engagement-exposure.json').write_text(json.dumps({'source_sha256':EXPECTED,'directed_aperture_rays':rays,'aperture_method':'Exact evaluated triangle raycasts against named rigid frame surfaces only. Moving/flexible leaves excluded to measure structural aperture, not certify runtime opening behavior. Full route/SAT checks independently rerun in validator-independent.json.','engagement_classification':engagement,'selected_coplanar_exposure':selected},indent=2))
assert sha(bpy.data.filepath)==EXPECTED
assert v.report['passed']
print('FINISH_READONLY_DONE',flush=True)
