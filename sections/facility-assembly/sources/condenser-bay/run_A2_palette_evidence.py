"""Sequential evidence for the owner's R5 palette correction, using existing tools.

Previous R1-R4 results remain historical and are never offered as R5 passes.
One Blender process at a time. Resume only verified completed commands against
the same saved native; partial render collectors verify every retained PNG.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMBINED = HERE.parents[1] / 'combined'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main(blender, resume, retry_stage=None, warm="R5", stable="R6"):
    assert warm in {"R5", "R5b", "R5c"} and stable in {"R6", "R6b", "R6c"}
    native = HERE / 'module_aaa_A2.blend'
    out = HERE / ('evidence-A2/palette-revision-'+warm)
    out.mkdir(exist_ok=True)
    map_out = HERE / ('evidence-A2/map-'+warm)
    map_out.mkdir(exist_ok=True)
    owner = HERE / ('renders-A2/owner-map-'+warm)
    owner.mkdir(exist_ok=True)
    cfg = json.loads((HERE/'renders-A2/owner-map/views.json').read_text())
    cfg['out'] = str(owner)
    (owner/'views.json').write_text(json.dumps(cfg, indent=2)+'\n')
    b = [blender, '--background', '--disable-autoexec', '--threads', '5']
    source = b + ['module_aaa_A2.blend', '--python-exit-code', '1', '--python']
    jobs = [
        ('room-audits', source+['condenser_A2_evidence.py','--','audit','--label',warm], HERE, out/'room-audits.log'),
        ('constraints', source+['audit_A2_constraints.py'], HERE, out/'constraints.log'),
        ('build-map', b+['--factory-startup','--python-exit-code','1','--python','build_compact_map.py'], COMBINED, map_out/'build.log'),
        ('map-checks', ['python3','run_A2_map_checks.py','--blender',blender,'--label','map-'+warm], HERE, out/'map-checks.log'),
        ('map-gates', ['python3','audit_A2_map_results.py','map-'+warm,'--baseline','evidence-A2/baseline-main82c29117/committed-validation'], HERE, out/'map-gates.log'),
        ('owner-map', b+['combined_map.blend','--python-exit-code','1','--python','render_views.py','--',str(owner/'views.json')], COMBINED, out/'owner-map.log'),
    ]
    for label, script in [
        (warm,'condenser_A2_evidence.py'),
        (warm+'-supplemental','condenser_A2_supplement.py'),
        ('material-diagnostics-'+warm,'render_A2_material_board.py'),
        (stable,'condenser_A2_evidence.py'),
        (stable+'-supplemental','condenser_A2_supplement.py'),
        ('cold-'+stable,'condenser_A2_evidence.py'),
        ('cold-'+stable+'-supplemental','condenser_A2_supplement.py'),
    ]:
        args = source+[script,'--']
        if script == 'condenser_A2_evidence.py':args += ['render']
        args += ['--label',label]
        if script != 'render_A2_material_board.py':
            args += ['--samples','16']
            if (HERE/'renders-A2'/label/'render_manifest.json').exists():args += ['--resume']
        jobs.append((label,args,HERE,out/(label+'.log')))
    for first,cold in [(warm,stable),(warm+'-supplemental',stable+'-supplemental'),(stable,'cold-'+stable),(stable+'-supplemental','cold-'+stable+'-supplemental')]:
        label = first+'--'+cold
        jobs.append((label,['python3','compare_A2_evidence.py',first,cold],HERE,out/(label+'.log')))
    jobs.append(('pack-review',['python3','pack_A2_review.py',warm,stable,'cold-'+stable,'--owner','--owner-label','owner-map-'+warm],HERE,out/'pack-review.log'))
    manifest = out/'commands.json'
    report = {'status':'RUNNING','native_sha256':digest(native),'commands':[],
              'scope':'Owner-directed machinery palette correction. Original room/map tools and numeric thresholds unchanged. Independent art review required.'}
    if resume and manifest.exists():
        report = json.loads(manifest.read_text())
        assert report['native_sha256'] == digest(native)
        # Preserve actual failures. A repaired stage needs an explicit retry;
        # only an exit-zero attempt can be retained as completed.
        assert all(c['exit_code']==0 or c['stage']==retry_stage or any(later['stage']==c['stage'] and later['exit_code']==0 for later in report['commands']) for c in report['commands'])
        if retry_stage:report.setdefault('explicit_retries',[]).append({'stage':retry_stage,'reason':'Completed three-camera preview priority metadata could not append under the original renderer guard. Preserve preview separately and render a fresh full pack; no pixel or numeric threshold changes.'})
    for label,args,cwd,log in jobs:
        assert digest(native) == report['native_sha256'], 'Native changed during evidence'
        if any(c['stage']==label and c['exit_code']==0 for c in report['commands']):
            print(warm+'_RETAIN_COMPLETED',label,flush=True)
            continue
        if label == 'map-checks' and (map_out/'commands.json').exists():args += ['--resume']
        subprocess.run(['df','-h','/'],check=True)
        print(warm+'_START',label,flush=True)
        if log.exists():
            assert resume, 'Existing unfinished log needs explicit resume'
            log.rename(log.with_name(log.stem+'-interrupted-'+str(time.time_ns())+'.log'))
        started=time.monotonic()
        with log.open('w') as f:
            result=subprocess.run(args,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
        report['commands'].append({'stage':label,'argv':args,'cwd':str(cwd),'exit_code':result.returncode,'seconds':round(time.monotonic()-started,2)})
        report['status']='FAIL' if result.returncode else 'RUNNING'
        manifest.write_text(json.dumps(report,indent=2)+'\n')
        print(warm+'_DONE',label,result.returncode,flush=True)
        if result.returncode:raise SystemExit(result.returncode)
    report['status']='NUMERIC_EVIDENCE_COMPLETE; independent art review pending'
    manifest.write_text(json.dumps(report,indent=2)+'\n')

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--blender',required=True);ap.add_argument('--resume',action='store_true');ap.add_argument('--after-preview',action='store_true');ap.add_argument('--retry-stage',choices=['R5'])
    ap.add_argument('--round',default='R5',choices=['R5','R5b','R5c']);ap.add_argument('--stability',default='R6',choices=['R6','R6b','R6c'])
    args=ap.parse_args()
    if args.after_preview:
        pid=json.loads((HERE/'evidence-A2/palette-revision-R5/preview-process.json').read_text())['pid']
        status=Path('/proc')/str(pid)/'status'
        while status.exists() and 'State:\tZ' not in status.read_text():time.sleep(5)
        preview=json.loads((HERE/'renders-A2/R5/render_manifest.json').read_text())
        assert len(preview['cameras'])==3
        assert 'Blender quit' in (HERE/'evidence-A2/palette-revision-R5/preview.log').read_text()
        for frame in preview['cameras']:assert digest(HERE/'renders-A2/R5'/(frame['camera']+'.png'))==frame['sha256']
        print('R5_PREVIEW_COMPLETE_VERIFIED',flush=True)
    main(args.blender,args.resume,args.retry_stage,args.round,args.stability)
