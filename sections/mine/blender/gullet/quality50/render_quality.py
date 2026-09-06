"""Render real Cycles views with declared excavation/gate states."""
import bpy,json,sys,argparse,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from cameras import set_review_state
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def camera_probe(scene,camera):
    verts=[];faces=[];names=[]
    for o in scene.objects:
        if o.type!='MESH' or o.hide_render or o.get('csm_collision_only') or o.get('q50_volumetric'):continue
        off=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
        for p in o.data.polygons:faces.append(tuple(off+i for i in p.vertices));names.append(o.name)
    bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
    eye=camera.matrix_world.translation;rot=camera.matrix_world.to_3x3();view=camera.data.view_frame(scene=scene);nearest=[]
    for u,v in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
        x=max(p.x for p in view)*u;y=max(p.y for p in view)*v;z=view[0].z
        d=(rot@Vector((x,y,z))).normalized();hit=bvh.ray_cast(eye,d,100)
        if hit[0] is not None:nearest.append({'distance':round(hit[3],5),'object':names[hit[2]],'ray':[u,v]})
    return {'minimum_forward_hit_m':min([r['distance'] for r in nearest],default=None),'rays':nearest,'near_plane_clear':not any(r['distance']<camera.data.clip_start+.005 for r in nearest)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--batch',type=int,default=None);p.add_argument('--views',default='');p.add_argument('--width',type=int,default=1100);p.add_argument('--samples',type=int,default=32)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)
    scene=next(s for s in bpy.data.scenes if s.get('q50_revision'))
    if bpy.context.window:bpy.context.window.scene=scene
    rows=json.loads(scene['q50_cameras']);selected={int(x) for x in a.views.split(',') if x} if a.views else None
    rows=[r for i,r in enumerate(rows) if (selected is None or i+1 in selected) and (a.batch is None or i//10==a.batch)]
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=a.samples;scene.cycles.use_denoising=True
    scene.render.resolution_x=a.width;scene.render.resolution_y=round(a.width*688/1100);scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.use_file_extension=True
    report=[]
    for row in rows:
        set_review_state(scene,row);scene.camera=scene.objects[row['id']];diagnostics=camera_probe(scene,scene.camera)
        dest=a.output/(row['id']+'.png');scene.render.filepath=str(dest);start=time.time();bpy.ops.render.render(write_still=True)
        report.append({'camera':row,'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'seconds':round(time.time()-start,2),'diagnostics':diagnostics,'engine':'Cycles','blender':bpy.app.version_string})
        print('Q50_RENDER',json.dumps(report[-1]),flush=True)
        (a.output/(f'batch_{a.batch}.json' if a.batch is not None else 'render_report.json')).write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
