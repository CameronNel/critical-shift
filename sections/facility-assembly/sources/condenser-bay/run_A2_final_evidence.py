"""One sequential final worker: exact map gates, owner view, source camera packs."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;COMBINED=HERE.parents[1]/'combined'

def main(blender, start_stage):
 out=HERE/'evidence-A2/final-queue';out.mkdir(exist_ok=True)
 report={'status':'RUNNING','source_sha256':hashlib.sha256((HERE/'module_aaa_A2.blend').read_bytes()).hexdigest(),'commands':[]}
 jobs=[('map-checks',['python3','run_A2_map_checks.py','--blender',blender,'--label','map-R3e'],HERE),('map-pass-values',['python3','audit_A2_map_results.py','map-R3e','--baseline','evidence-A2/baseline-main-A1/committed-validation'],HERE),('owner-view',[blender,'--background','--disable-autoexec','--threads','5','combined_map.blend','--python-exit-code','1','--python','render_views.py','--',str(HERE/'renders-A2/owner-map/views.json')],COMBINED),('room-camera-packs',['python3','run_A2_render_evidence.py','--blender',blender],HERE)]
 if start_stage != 'map-checks':
  jobs=[(n,[*args,'--resume'] if n=='room-camera-packs' else args,cwd) for n,args,cwd in jobs]
  report['resume_note']='Environment restart interrupted the earlier map lighting stage. Its resumed exact commands are retained in map-R3e/commands.json; skipped stages are not rerun by this worker.'
  jobs=jobs[next(i for i,x in enumerate(jobs) if x[0]==start_stage):]
 jobs.append(('numeric-comparisons',['python3','finalize_A2_evidence.py'],HERE))
 if (out/'commands.json').exists():
  prior=json.loads((out/'commands.json').read_text());assert prior['source_sha256']==report['source_sha256']
  (out/('commands-interrupted-'+str(time.time_ns())+'.json')).write_text(json.dumps(prior,indent=2)+'\n')
  report['retained_prior_completed_commands']=prior['commands']
 for name,args,cwd in jobs:
  assert hashlib.sha256((HERE/'module_aaa_A2.blend').read_bytes()).hexdigest()==report['source_sha256'],'Final native changed during evidence collection'
  subprocess.run(['df','-h','/'],check=True);print('A2_FINAL_START',name,flush=True);start=time.monotonic()
  logfile=out/(name+'.log')
  if logfile.exists():logfile.rename(out/(name+'-prior-'+str(time.time_ns())+'.log'))
  with logfile.open('w') as f:r=subprocess.run(args,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
  report['commands'].append({'stage':name,'argv':args,'cwd':str(cwd),'exit_code':r.returncode,'seconds':round(time.monotonic()-start,2)});report['status']='FAIL' if r.returncode else 'RUNNING';(out/'commands.json').write_text(json.dumps(report,indent=2)+'\n');print('A2_FINAL_DONE',name,r.returncode,flush=True)
  if r.returncode:raise SystemExit(r.returncode)
 report['status']='EVIDENCE_RENDERED; comparisons and independent review pending';(out/'commands.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--blender',required=True);ap.add_argument('--start-stage',choices=['map-checks','map-pass-values','owner-view','room-camera-packs'],default='map-checks');a=ap.parse_args();main(a.blender,a.start_stage)
