"""Final-view corrections: keep physical task lights clear of every excavation state.
Only fixture placement/contact geometry is changed. Lights are not hidden to pass.
"""
import bpy, math, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

def world_mesh(obj):
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    faces=[tuple(p.vertices) for p in obj.data.polygons]
    lo=Vector([min(v[i] for v in verts) for i in range(3)])
    hi=Vector([max(v[i] for v in verts) for i in range(3)])
    return verts,faces,lo,hi

def overlap(a,b,c,d,margin=.002):
    return all(a[i]<d[i]+margin and c[i]<b[i]+margin for i in range(3))

def groups(scene):
    result=[]
    generated=[o for o in scene.objects if o.name.startswith(('Q50_Old_task_lamp','Q50_Excavation_practical'))]
    for sec in 'ABC':
        for stage in (1,2,3):
            objs=[o for o in generated if o.get('csm_sector')==sec and o.get('csm_min_stage')==stage]
            if not objs:continue
            light=next(o for o in objs if o.type=='LIGHT')
            result.append((f'{sec}/{stage}',sec,stage,objs,light.matrix_world.translation+Vector((0,.15,-1.5))))
    for root in [o for o in scene.objects if o.type=='EMPTY' and o.name.startswith('CSM_Portable_worklight')]:
        objs=[root]+list(root.children_recursive)
        lights=[o for o in scene.objects if o.type=='LIGHT' and o.name.startswith('CSM_Portable_practical')]
        light=min(lights,key=lambda o:(o.matrix_world.translation-root.matrix_world.translation).length)
        objs.append(light);result.append((root.name,root.get('csm_sector'),root.get('csm_min_stage',0),objs,root.matrix_world.translation.copy()))
    return result

def reroute_leads(scene):
    for lead in [o for o in scene.objects if o.type=='MESH' and o.name.startswith('CSM_Power_lead') and o.parent and o.parent.name.startswith('CSM_Portable_worklight')]:
        root=lead.parent;origin=root.matrix_world.translation
        points=[Vector(p)+origin for p in [(0,.18,1.73),(0,.24,1.30),(.02,.25,.85),(.04,.21,.32),(.08,.17,.039),(.19,.10,.030),(.24,-.08,.030),(.08,-.22,.030),(-.13,-.19,.030),(-.22,-.06,.030),(-.19,.08,.030),(-.10,.13,.030)]]
        inv=lead.matrix_world.inverted();verts=[];faces=[]
        for i,c in enumerate(points):
            direction=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized()
            u=direction.cross(Vector((0,0,1)))
            if u.length<.01:u=direction.cross(Vector((1,0,0)))
            u.normalize();v=direction.cross(u)
            for j in range(8):verts.append(tuple(inv@(c+.012*(u*math.cos(j*math.tau/8)+v*math.sin(j*math.tau/8)))))
        for i in range(len(points)-1):
            for j in range(8):faces.append((i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j))
        faces.extend([tuple(reversed(range(8))),tuple(range((len(points)-1)*8,len(points)*8))])
        old=lead.data;me=bpy.data.meshes.new('Q50_Clear_coiled_power_lead');me.from_pydata(verts,[],faces);me.update()
        for mat in old.materials:me.materials.append(mat)
        lead.data=me;lead['q50_power_lead_rerouted']=True
    bpy.context.view_layer.update()

def repair(scene):
    reroute_leads(scene)
    mesh_cache={o.name:world_mesh(o) for o in scene.objects if o.type=='MESH' and not o.get('csm_collision_only') and not o.get('q50_volumetric')}
    trees={}
    def bvh(name):
        if name not in trees:trees[name]=BVHTree.FromPolygons(mesh_cache[name][0],mesh_cache[name][1],all_triangles=False)
        return trees[name]
    floor=bvh('CSM_Excavated_floor');skin=bvh('CSM_Continuous_stratified_mine_skin')
    report=[]
    depths={'A':((-3.9,17.8),(-1.,0.),[0,3.6,7.,12.7]),'B':((3.9,33.),(1.,0.),[0,3.7,7.1,12.4]),'C':((0.,39.2),(0.,1.),[0,4.5,8.8,16.3])}
    for name,sec,stage,parts,pivot in groups(scene):
        partnames={o.name for o in parts};verts=[];faces=[]
        for o in parts:
            if o.type!='MESH':continue
            v,f,_,_=mesh_cache[o.name];off=len(verts);verts.extend(v);faces.extend(tuple(i+off for i in p) for p in f)
        minimum=min(v.z for v in verts);bottom=[v for v in verts if v.z<minimum+.025]
        lo=Vector([min(v[i] for v in verts) for i in range(3)]);hi=Vector([max(v[i] for v in verts) for i in range(3)])
        candidates=[(ix*.15,iy*.15) for ix in range(-17,18) for iy in range(-17,18)]
        candidates.sort(key=lambda p:(p[0]*p[0]+p[1]*p[1],abs(p[1]),p[0]))
        obstacles=[]
        for o in scene.objects:
            if o.name not in mesh_cache or o.name in partnames:continue
            if o.get('csm_gate_index') is not None and o.get('csm_sector')==sec and int(o['csm_gate_index'])<stage:continue
            _,_,a,b=mesh_cache[o.name]
            if overlap(lo-Vector((2.8,2.8,.35)),hi+Vector((2.8,2.8,.35)),a,b):obstacles.append(o)
        original_conflicts=[];chosen=None;trials=0
        base_tree=BVHTree.FromPolygons(verts,faces,all_triangles=False)
        for ob in obstacles:
            if overlap(lo,hi,mesh_cache[ob.name][2],mesh_cache[ob.name][3]) and base_tree.overlap(bvh(ob.name)):original_conflicts.append(ob.name)
        for dx,dy in candidates:
            if sec and stage:
                entry,axis,steps=depths[sec]
                d=(pivot.x+dx-entry[0])*axis[0]+(pivot.y+dy-entry[1])*axis[1]
                lateral=abs(-(pivot.x+dx-entry[0])*axis[1]+(pivot.y+dy-entry[1])*axis[0])
                if not steps[stage-1]+.32<d<steps[stage]-.34 or lateral<.63:continue
            origin=pivot+Vector((0,0,1.0));delta=Vector((dx,dy,0))
            if delta.length>.001:
                hit=skin.ray_cast(origin,delta.normalized(),delta.length)
                if hit[0] is not None:continue
            dz=[]
            for v in bottom:
                hit=floor.ray_cast(Vector((v.x+dx,v.y+dy,8)),Vector((0,0,-1)),15)
                if hit[0] is not None:dz.append(hit[0].z-v.z)
            if not dz:continue
            delta=Vector((dx,dy,max(dz)+.0015));a,b=lo+delta,hi+delta
            test=None;failed=False;trials+=1
            for ob in obstacles:
                if not overlap(a,b,mesh_cache[ob.name][2],mesh_cache[ob.name][3]):continue
                if test is None:test=BVHTree.FromPolygons([v+delta for v in verts],faces,all_triangles=False)
                if test.overlap(bvh(ob.name)):failed=True;break
            if not failed:chosen=delta;break
        if chosen is None:raise RuntimeError('No contact-safe lamp position found for '+name+'; initial conflicts: '+str(original_conflicts))
        originals={o.name:o.matrix_world.copy() for o in parts}
        def depth(o):
            d=0
            while o.parent is not None:d+=1;o=o.parent
            return d
        for o in sorted(parts,key=depth):
            mat=originals[o.name];mat.translation+=chosen;o.matrix_world=mat;o['q50_fixture_clearance_group']=name
        bpy.context.view_layer.update()
        for o in parts:
            if o.type=='MESH':mesh_cache[o.name]=world_mesh(o);trees.pop(o.name,None)
        report.append({'group':name,'sector':sec,'stage':stage,'original_triangle_conflicts':original_conflicts,'translation_m':list(chosen),'candidate_positions_tested':trials,'final_triangle_conflicts':0,'method':'All-variant triangle-overlap test; floor-seated feet; no visibility workaround.'})
        print('FIXTURE_REPAIR',json.dumps(report[-1]),flush=True)
    return report

if __name__=='__main__':
    import sys,argparse
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    s=bpy.context.scene;r=repair(s);s['q50_revision']='quality50-r7';s['q50_fixture_clearance']=json.dumps(r)
    a.output.mkdir(parents=True,exist_ok=True);(a.output/'fixture_clearance_report.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(a.output/'Gullet_Quality50.blend'),compress=True)
