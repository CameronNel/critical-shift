import bpy,json,importlib.util,math
from pathlib import Path
from mathutils import Vector
r=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');p=r/'revamp/production/critics/full-c03-technical';spec=importlib.util.spec_from_file_location('v',r/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
dg=bpy.context.evaluated_depsgraph_get();shape=v.Shape(bpy.data.objects['Office key box cabinet'],dg);glass=v.Shape(bpy.data.objects['Key box glass'],dg);centre=sum((Vector(x) for x in glass.bounds),Vector())*.5
rays=[]
for axis in range(3):
 for sign in (-1,1):
  dr=Vector((0,0,0));dr[axis]=sign;h=shape.ray(centre,dr,.5);rays.append({'axis':axis,'sign':sign,'hit':list(h['point']) if h else None,'distance':h['distance'] if h else None})
key={'glasscentre':list(centre),'inside_cabinet':shape.contains(centre),'cabinet_rays':rays}
o=bpy.data.objects['Covered Trolley Draped Tarp'];me=o.data;me.calc_loop_triangles();layer=me.uv_layers['CD_Fabric_Cut_1m'];half=len(me.vertices)//2;world_area=uv_area=0;byvert={};count=0
for t in me.loop_triangles:
 if not all(i<half for i in t.vertices):continue
 count+=1;ps=[o.matrix_world@me.vertices[i].co for i in t.vertices];uv=[layer.data[i].uv.copy() for i in t.loops];world_area+=(ps[1]-ps[0]).cross(ps[2]-ps[0]).length*.5;uv_area+=abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))*.5
 for i,u in zip(t.vertices,uv):byvert.setdefault(i,[]).append(u)
discontinuous=[i for i,uvs in byvert.items() if max((a-b).length for a in uvs for b in uvs)>1e-6]
fabric={'top_vertices_index_range':[0,half-1],'top_triangles':count,'world_area_m2':world_area,'uv_area':uv_area,'uv_world_area_ratio':uv_area/world_area,'top_shared_vertex_chart_discontinuities':discontinuous,'metadata':dict(o.items())}
fabric['metadata']={k:str(x) for k,x in fabric['metadata'].items()}
(p/'fabric-key.json').write_text(json.dumps({'key_cabinet':key,'fabric':fabric},indent=2));print('FABRIC_KEY_COMPLETE',key,'fabric',fabric)
