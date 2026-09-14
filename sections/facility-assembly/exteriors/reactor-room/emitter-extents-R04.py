import bpy,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
for sid,rev in [('reactor-room','R04')]:
 out=root/'exteriors'/sid;bpy.ops.wm.open_mainfile(filepath=str(out/f'exterior-{rev}.blend'),load_ui=False);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 ext=bpy.data.collections['EXTERIOR_'+sid];meshes=list({o for o in list(ext.objects)+list(bpy.data.objects) if o.type=='MESH' and not o.hide_render and (o in list(ext.objects) or any(t in o.name.lower() for t in ['roof','ceiling','shell','closure','portal','connector','wall','cap','transition']))})
 rows=[]
 for ob in bpy.data.objects:
  if ob.type!='LIGHT' or ob.data.type=='SUN':continue
  d=ob.data;center=ob.matrix_world.translation
  candidates=[]
  for mesh in meshes:
   eo=mesh.evaluated_get(dg);inv=eo.matrix_world.inverted();hit,co,no,idx=eo.closest_point_on_mesh(inv@center)
   if hit:
    world=eo.matrix_world@co;candidates.append({'mesh':mesh.name,'distance_m':(world-center).length,'closest_surface_world':list(world)})
  candidates.sort(key=lambda r:r['distance_m'])
  radius=d.shadow_soft_size if d.type in ['POINT','SPOT'] else None
  area=None
  if d.type=='AREA':
   sx=d.size;sy=d.size_y if d.shape in ['RECTANGLE','ELLIPSE'] else d.size
   pts=[ob.matrix_world@Vector((a*sx/2,b*sy/2,0)) for a,b in [(-1,-1),(-1,1),(1,-1),(1,1)]]
   crossings=[]
   for mesh in meshes:
    eo=mesh.evaluated_get(dg);inv=eo.matrix_world.inverted()
    for j in range(64):
     ang=j*2*math.pi/64;xx=math.cos(ang);yy=math.sin(ang)
     if d.shape in ['SQUARE','RECTANGLE']:
      norm=max(abs(xx),abs(yy));xx/=norm;yy/=norm
     endpoint=ob.matrix_world@Vector((xx*sx/2,yy*sy/2,0));a=inv@center;b=inv@endpoint;vec=b-a
     hit,co,no,idx=eo.ray_cast(a,vec.normalized(),distance=vec.length)
     if hit:crossings.append({'mesh':mesh.name,'hit_world':list(eo.matrix_world@co)});break
   area={'surface_crossings':crossings,'shape':d.shape,'size':sx,'size_y':sy,'normal_world':list(ob.matrix_world.to_3x3()@Vector((0,0,-1))),'emitter_rectangle_world':[list(p) for p in pts]}
  rows.append({'light':ob.name,'type':d.type,'location':list(center),'energy':d.energy,'radius_m':radius,'area':area,'nearest_exterior_surfaces':candidates[:3],'sphere_reaches_exterior':[c for c in candidates if radius is not None and c['distance_m']<radius],'nearest_roof_surfaces':[c for c in candidates if any(t in c['mesh'].lower() for t in ['roof','membrane','coping'])][:2]})
 (out/f'emitter-extents-{rev}.json').write_text(json.dumps(rows,indent=2))
 print(json.dumps({'section':sid,'crossing_lights':[{'light':r['light'],'area':r['area']} for r in rows if r['area'] and r['area']['surface_crossings']]},indent=2))


