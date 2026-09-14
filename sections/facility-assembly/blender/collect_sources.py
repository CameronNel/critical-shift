"""Freeze room inputs without editing their authoring worktrees."""
import hashlib, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
G=Path('C:/Users/Camer/Games/critical-shift/worktrees')
E=Path('C:/Users/Camer/.codex/worktrees/ef37/critical-shift')
rows=[
 ('spawn-room',G/'spawn-reference-rebuild/sections/spawn-room','spawnroom_valorant_walk.blend',None,None),
 ('mine',G/'reactor-valorant/sections/mine','gullet/Gullet_Valorant.blend',None,'1cfa3923bb4c4b82fac99563dfe5a27747f5eb97155a3161726d4746ed973a31'),
 ('refinery',G/'refinery-compact/sections/refinery','Refinery.blend',None,'890460de55c331bba30abc80da3eb71f29d11f9f8ada6bca465cd178b43d71d8'),
 ('reactor-room',G/'reactor-valorant/sections/reactor-room','reactor_scene.blend',None,None),
 ('cooling-plant',E/'sections/cooling-plant','cooling_plant.blend','cefe9d9ea66dc9dc64c4c40aa97a395b63a0496c','cdc0b48a5af6cb11bae6a4511074cc4b9aacf4dce687503e55d3891a49bb2693'),
 ('turbine-room',E/'sections/turbine-room','turbine-room.blend','d0f01c8b15638f4410d5ec61b775ba70cc417aa0','4f6a1f0d3869933f4922f5d4012bc84671150f39270ebde938042ebaafc78f3f'),
 ('electrical-room',E/'sections/electrical-room','electrical_room.blend','5438cfc51aa6bcb5b5e4ee9012b985313667bada','01447dce65a406afa84448e440176aefd37cdda702dc0a4cd51cee366c298dfd'),
 ('waste-storage',E/'.worktrees/waste-storage/sections/waste-storage','waste_storage_integration.blend','5b9ccd5450f85455e5815d2f95efadd087ac6fc9','8ab458f9da2199a147cbb9d140a3eefb7b903eee68fb23e00a29c844770c7cf7'),
 ('medical-reanimation',E/'.worktrees/medical-reanimation/sections/medical-reanimation','medical_integration.blend','0a3b3d75cac0f42a5ea5f14dfe738ec41f256612','35d278c93cf8f385258da9e5b93ab6709d8166552ef204aca41b97231c04eb9a'),
 ('fuel-corridor',E/'.worktrees/fuel-corridor-final/sections/fuel-corridor','Fuel_Corridor.blend','9f0884db71bd8caaa0f86c38d5e8021ccd397974','a8e742a10cf5691098adabc0c2518384db3d82444517637bd67e362af4146403'),
 ('compliance-dock',G/'compliance-dock-gemini/sections/compliance-dock','compliance_dock.blend',None,None),
 ('condenser-bay',Path('C:/Users/Camer/.codex/worktrees/3671/critical-shift/sections/condenser-bay'),'condenser_bay.blend',None,'26edf558d2e03b16b841940d20973b74017a52e9f8c0c320d5ff5487c9d9ea3b'),
]
manifest=[]
for sid,section,filename,commit,expected in rows:
    original=section/'blender'/filename
    dst=ROOT/'sources'/sid;dst.mkdir(parents=True,exist_ok=True)
    frozen=dst/'accepted.blend'
    if commit:
        raw=subprocess.check_output(['git','-c',f'safe.directory={E.as_posix()}','-C',str(E),'show',f'{commit}:sections/{sid}/blender/{filename}'])
    else: raw=original.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if expected and digest!=expected: raise RuntimeError(f'{sid} source drift {digest} != {expected}; preserve and reconcile')
    if frozen.exists(): assert hashlib.sha256(frozen.read_bytes()).hexdigest()==digest
    else: frozen.write_bytes(raw)
    docs=[]
    for rel in ['interface.json','scenery/interface.json','architecture/interface.json','production/FINAL_HANDOFF.md','production/FINAL_ACCEPTANCE.md','HANDOFF.md','production/TASK_STATE.md','architecture/CONNECTIONS.md','architecture/FLOORPLAN.md']:
        src=section/rel
        if src.exists():
            out=dst/'contracts'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out);docs.append(rel)
    item=dict(id=sid,original=str(original),section=str(section),original_parent=str(original.parent),source_commit=commit,current_mutable_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),source_sha256=digest,expected_sha256=expected,frozen=f'sources/{sid}/accepted.blend',contracts=docs)
    manifest.append(item);print(sid,digest[:16],len(raw),flush=True)
(ROOT/'production/SOURCES.json').write_text(json.dumps(manifest,indent=2))
