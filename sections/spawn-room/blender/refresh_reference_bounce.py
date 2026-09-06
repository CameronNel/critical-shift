"""Refresh one documented volume at a time, preserving a saved source before work."""
import bpy,sys,json,time
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;t=time.time();rows=[]
for name in ['BOUNCE_BRIEFING','BOUNCE_HALL','BOUNCE_LOCKER']:
    bpy.ops.object.select_all(action='DESELECT');ob=bpy.data.objects[name];ob.select_set(True);bpy.context.view_layer.objects.active=ob
    print('REFRESH_ACTIVE_PROBE',name,flush=True)
    bpy.ops.object.lightprobe_cache_bake(subset='ACTIVE')
    rows.append({'probe':name,'seconds':time.time()-t})
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'spawnroom_valorant_baked.blend'),compress=True)
    (out/'progress.json').write_text(json.dumps(rows,indent=2))
print('BOUNCE_REFRESH_COMPLETE',flush=True)
