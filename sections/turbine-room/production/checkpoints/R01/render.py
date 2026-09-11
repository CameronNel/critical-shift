import bpy,json,time,sys,argparse,hashlib
from pathlib import Path
def render_set(root,revision,selection,samples=48,final=False):
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=samples;s.cycles.use_denoising=True
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='HIP';prefs.get_devices()
    found=[]
    for d in prefs.devices:d.use=d.type=='HIP';found.append({'name':d.name,'type':d.type,'used':bool(d.use)})
    if not any(d['used'] for d in found):raise RuntimeError('No HIP device available; no silent device fallback')
    s.cycles.device='GPU';s.render.use_persistent_data=True
    out=root/'production'/'renders'/('final' if final else 'review')/revision;out.mkdir(parents=True,exist_ok=True)
    names=[c[0] for c in json.loads(s['camera_contract'])] if selection=='all' else selection.split(',')
    results=[]
    for name in names:
        s.camera=bpy.data.objects[name];s.render.filepath=str(out/(name+'.png'));start=time.time();bpy.ops.render.render(write_still=True)
        results.append({'camera':name,'seconds':round(time.time()-start,2),'file':name+'.png','sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()})
        (out/'render_manifest.json').write_text(json.dumps({'revision':revision,'source_revision':s['source_revision'],'samples':samples,'resolution':[s.render.resolution_x,s.render.resolution_y],'devices':found,'renders':results},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--revision',required=True);a.add_argument('--render',default='all');a.add_argument('--samples',type=int,default=48);a.add_argument('--final',action='store_true');p=a.parse_args(sys.argv[sys.argv.index('--')+1:]);render_set(Path(__file__).resolve().parents[1],p.revision,p.render,p.samples,p.final)
