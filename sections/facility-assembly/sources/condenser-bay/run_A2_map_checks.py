"""Run the brief's existing map tools sequentially; retain commands and raw logs.
No combined-map implementation or threshold is edited. A failed command stops the
queue and is recorded as FAIL. A successful tool run is distinct from its gates.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMBINED = HERE.parents[1] / 'combined'

def main(blender, label, resume=False):
    output = HERE / 'evidence-A2' / label
    output.mkdir(parents=True, exist_ok=True)
    log = (output / 'build.log').read_text()
    required = {
      'D01': r'CONDENSER D01 stub opened\s+([1-9]\d*)',
      'feed': r'CONDENSER pump B power riser moved to the north wall:\s+8 curve points',
      'escape': r'CONDENSER west escape door cut:\s+([1-9]\d*)',
      'ceiling': r'CONDENSER ceiling slab lowered under the turbine floor',
      'ground': r'GROUND hole over the condenser bay:\s+1 ground pieces cut',
    }
    for name, pattern in required.items():assert re.search(pattern, log), 'Fix missing build patch before proceeding: ' + name
    b = [str(Path(blender).resolve()), '--background', '--disable-autoexec', '--threads', '5', 'combined_map.blend', '--python-exit-code', '1', '--python']
    cut = output / 'plan-cut.npz'
    jobs = [
      ('performance', b + ['perf_report.py', '--', 'validation/perf_report.json']),
      ('plan-cut', b + ['plan_cut.py', '--', str(cut), '0.15','0.4','1.1','1.8','2.8','4.5','-0.6','-3.5','-5.0','-5.6']),
      ('overlaps', ['python3','check_overlaps.py',str(cut)]),
      ('walk-normal', b + ['walk_test.py','--','validation/walk_report.json']),
      ('walk-colliders', b + ['walk_test.py','--','validation/walk_report.json','--colliders']),
      ('walk-meltdown', b + ['walk_test.py','--','validation/walk_report.json','--meltdown']),
      ('evacuation', ['python3','evac_report.py']),
      ('doors', b + ['door_audit.py']),
      ('floors', b + ['floor_audit.py']),
      ('export', b + ['export_unity.py','--','export']),
      ('lighting', b + ['measure_lighting.py','--',str(output/'lighting-renders'),'validation/lighting.json']),
    ]
    report = {'label':label,'source_blend':'module_aaa_A2.blend','commands':[],'status':'RUNNING','blender':str(Path(blender).resolve()),'scope':'Existing static map checks and scoped Blender FBX round trip; no Unity engine or FPS run.'}
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report['source_sha256'] = digest(HERE/'module_aaa_A2.blend')
    report['map_sha256'] = digest(COMBINED/'combined_map.blend')
    manifest = output / 'commands.json'
    if resume and manifest.exists():
        prior = json.loads(manifest.read_text())
        assert prior['source_sha256'] == report['source_sha256']
        assert prior['map_sha256'] == report['map_sha256']
        assert all(x['exit_code'] == 0 for x in prior['commands'])
        report = prior
        report['resumed_after_environment_restart'] = True
    for name, args in jobs:
        if any(x['check'] == name for x in report['commands']):continue
        assert digest(HERE/'module_aaa_A2.blend') == report['source_sha256'], 'Source changed during the map queue'
        assert digest(COMBINED/'combined_map.blend') == report['map_sha256'], 'Map changed during the check queue'
        subprocess.run(['df','-h','/'], check=True)
        print('A2_CHECK_START', name, flush=True)
        start = time.monotonic()
        logfile = output/(name+'.log')
        if logfile.exists():
            assert resume, 'Existing unfinished log requires explicit resume'
            logfile.rename(output/(name+'-interrupted.log'))
        with logfile.open('w') as stream:
            result = subprocess.run(args, cwd=COMBINED, stdout=stream, stderr=subprocess.STDOUT)
        report['commands'].append({'check':name,'argv':args,'cwd':str(COMBINED),'exit_code':result.returncode,'seconds':round(time.monotonic()-start,2)})
        report['status'] = 'FAIL' if result.returncode else 'RUNNING'
        manifest.write_text(json.dumps(report, indent=2)+'\n')
        print('A2_CHECK_DONE', name, result.returncode, flush=True)
        if name == 'overlaps' and result.returncode == 0:
            shutil.copy2(output/(name+'.log'), COMBINED/'validation/overlaps.txt')
        if result.returncode:raise SystemExit(result.returncode)
        if name == 'performance':
            data = json.loads((COMBINED/'validation/perf_report.json').read_text())
            value = data['rooms']['ROOM_condenser-bay']['triangles']
            report['condenser_map_triangles'] = value
            print('A2_MAP_TRIANGLES', value, flush=True)
            if value > 400000:
                report['status']='FAIL_BUDGET';manifest.write_text(json.dumps(report,indent=2)+'\n')
                raise SystemExit('Condenser exceeds 400,000 map triangles; repair before continuing')
    report['status'] = 'COMMANDS_COMPLETED; pass-value audit pending'
    manifest.write_text(json.dumps(report, indent=2)+'\n')
    shutil.copytree(COMBINED/'validation', output/'validation', dirs_exist_ok=True)
    shutil.copytree(COMBINED/'export', output/'export', dirs_exist_ok=True)
    print('A2_MAP_COMMAND_QUEUE_COMPLETE', flush=True)

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--blender',required=True);ap.add_argument('--label',required=True);ap.add_argument('--resume',action='store_true')
    args=ap.parse_args();main(args.blender,args.label,args.resume)
