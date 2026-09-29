"""Read-only CPU inspection renders of saved PR48 integration cameras."""
import bpy,sys,json,hashlib,ctypes
from pathlib import Path
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/spawn-integration';out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.seed=73;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.denoising_use_gpu=False
s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
names=['SY CAMERA | 01-front-yard','SI | Spawn threshold','SI | Spawn east attachments','SI | Medical attachments','SY CAMERA | 03-yard-reverse']
if args and args[0].isdigit():names=[names[int(args[0])]]
rows=[]
for name in names:
    s.camera=bpy.data.objects[name];dest=out/(name.split('|')[-1].strip().replace(' ','-')+('-cold' if 'cold' in args else '')+'.png');s.render.filepath=str(dest)
    bpy.ops.render.render(write_still=True);rows.append(dict(camera=name,path=str(dest),sha256=sha(dest),matrix=[list(r) for r in s.camera.matrix_world],lens=s.camera.data.lens))
assert sha(src)==before
(out/('render-'+('-'.join(args) or 'all')+'.json')).write_text(json.dumps(dict(source_sha256=before,engine='CYCLES',device='CPU',threads=1,samples=8,seed=73,resolution=[960,540],views=rows),indent=2))
