"""Isolated metric-UV experiment on immutable F13; no builder/native writes."""
import bpy, json, math, hashlib
from pathlib import Path

ROOM=Path(__file__).resolve().parents[3]
SOURCE=ROOM/'module_compare_f13.blend'
EXPECTED='22176ab474d914156cdf5a083571c19b04c6e6e11cfa50ab8ba681013bc124a6'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=scene
bpy.context.view_layer.update()

def developed_roller_chart(o):
    # The actual convex extruded barrel profile supplies chord lengths.
    # No circular-arc approximation and no change to cap/bevel face charts.
    points=[o.matrix_world@v.co for v in o.data.vertices]
    xmin,xmax=min(p.x for p in points),max(p.x for p in points)
    cy=(min(p.y for p in points)+max(p.y for p in points))/2
    cz=(min(p.z for p in points)+max(p.z for p in points))/2
    faces=[];profile={};clusters=[]
    def cluster(q):
        point=(q.y-cy,q.z-cz)
        for i,old in enumerate(clusters):
            if math.hypot(point[0]-old[0],point[1]-old[1])<.000001:return i
        clusters.append(point);return len(clusters)-1
    for f in o.data.polygons:
        vs=[points[i] for i in f.vertices]
        if max(v.x for v in vs)-min(v.x for v in vs)<(xmax-xmin)*.7:continue
        keys={cluster(v) for v in vs}
        if len(keys)!=2:continue
        faces.append(f)
        for q in keys:profile[q]=math.atan2(clusters[q][1],clusters[q][0])
    keys=sorted(profile,key=profile.get)
    if len(keys)<8:raise RuntimeError('Insufficient convex barrel contour')
    positions={};length=0
    for i,q in enumerate(keys):
        positions[q]=length;nxt=keys[(i+1)%len(keys)]
        length+=math.hypot(clusters[nxt][0]-clusters[q][0],clusters[nxt][1]-clusters[q][1])
    layer=o.data.uv_layers['CD_Physical_1m']
    for f in faces:
        coords=[points[o.data.loops[i].vertex_index] for i in f.loop_indices]
        offsets=[positions[cluster(q)] for q in coords]
        wrap=max(offsets)-min(offsets)>length/2
        for i,q,v in zip(f.loop_indices,coords,offsets):
            layer.data[i].uv=(q.x-xmin,v+length if wrap and v<length/2 else v)
    return dict(side_faces=len(faces),profile_vertices=len(keys),perimeter_m=length)

records=[]
for name in ['Conveyor roller 0','Conveyor roller 15','Conveyor roller 28']:
    o=scene.objects[name]
    # Only a local data clone changes; saved source bytes remain immutable.
    o.data=o.data.copy();rec=developed_roller_chart(o)
    world=[o.matrix_world@v.co for v in o.data.vertices]
    uv=o.data.uv_layers['CD_Physical_1m'];ratios=[];bad=[]
    for f in o.data.polygons:
        loops=list(f.loop_indices)
        for i,j in zip(loops,loops[1:]+loops[:1]):
            a,b=o.data.loops[i].vertex_index,o.data.loops[j].vertex_index
            actual=(world[a]-world[b]).length
            if actual<.0001:continue
            ratio=(uv.data[i].uv-uv.data[j].uv).length/actual;ratios.append(ratio)
            if abs(ratio-1)>.01:bad.append(dict(face=f.index,edge=[a,b],ratio=ratio))
    rec.update(object=name,physical_edge_min_ratio=min(ratios),physical_edge_max_ratio=max(ratios),bad_edges=bad)
    records.append(rec)
assert sha(SOURCE)==EXPECTED
out=Path(__file__).with_suffix('.json')
out.write_text(json.dumps(dict(source_sha256=EXPECTED,source_unchanged=True,
                              scope='Isolated UV proof only; no current native/visual acceptance',
                              measurements=records),indent=2)+'\n')
assert not any(r['bad_edges'] for r in records),'Metric barrel development exceeds1%'
print('ISOLATED_BARREL_CHART_METRIC_PASS',len(records),flush=True)
