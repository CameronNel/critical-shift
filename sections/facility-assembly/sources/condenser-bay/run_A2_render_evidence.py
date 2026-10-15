"""Sequential evidence worker; immutable natives, real renderer, fresh PIDs."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main(blender, resume=False):
 final=HERE/'module_aaa_A2.blend';digest=hashlib.sha256(final.read_bytes()).hexdigest()
 jobs=[('R2','checkpoints-A2/A2-R2b.blend','condenser_A2_evidence.py',['render','--label','R2','--samples','16']),('R3','module_aaa_A2.blend','condenser_A2_evidence.py',['render','--label','R3','--samples','16']),('R3-supplemental','module_aaa_A2.blend','condenser_A2_supplement.py',['--label','R3-supplemental','--samples','16']),('material-diagnostics','module_aaa_A2.blend','render_A2_material_board.py',['--label','material-diagnostics']),('R4','module_aaa_A2.blend','condenser_A2_evidence.py',['render','--label','R4','--samples','16']),('R4-supplemental','module_aaa_A2.blend','condenser_A2_supplement.py',['--label','R4-supplemental','--samples','16']),('cold-R4','module_aaa_A2.blend','condenser_A2_evidence.py',['render','--label','cold-R4','--samples','16']),('cold-R4-supplemental','module_aaa_A2.blend','condenser_A2_supplement.py',['--label','cold-R4-supplemental','--samples','16'])]
 out=HERE/'evidence-A2/render-queue';out.mkdir(exist_ok=True);report={'status':'RUNNING','final_sha256':digest,'policy':'R1 32spp diagnostic; R2+ 16spp full-size CPU OIDN, identical final/stability/cold settings. Material board 32spp. No image generation or retouching.','commands':[]}
 if resume and (out/'commands.json').exists():
  report=json.loads((out/'commands.json').read_text());assert report['final_sha256']==digest
  assert all(x['exit_code']==0 for x in report['commands'])
  report['resumed_after_environment_restart']=True
 for label,blend,script,extra in jobs:
  assert hashlib.sha256(final.read_bytes()).hexdigest()==digest,'Final native changed during evidence queue'
  completed=next((x for x in report['commands'] if x['label']==label),None)
  if completed:
   if label=='material-diagnostics':
    assert json.loads((HERE/'renders-A2'/label/'diagnostic.json').read_text())['source_sha256']==digest
   else:
    folder=HERE/'renders-A2'/label;m=json.loads((folder/'render_manifest.json').read_text())
    assert m['blend_sha256']==hashlib.sha256((HERE/blend).read_bytes()).hexdigest()
    assert len(m['cameras'])==(7 if label.endswith('-supplemental') else 22)
    for e in m['cameras']:assert hashlib.sha256((folder/(e['camera']+'.png')).read_bytes()).hexdigest()==e['sha256']
   print('A2_RENDER_RETAIN_COMPLETED',label,flush=True);continue
  if (HERE/'renders-A2'/label).exists() and script!='render_A2_material_board.py':
   assert resume,'Existing pack requires explicit resume'
   extra=[*extra,'--resume']
  subprocess.run(['df','-h','/'],check=True)
  args=[blender,'--background','--disable-autoexec','--threads','5',blend,'--python-exit-code','1','--python',script,'--',*extra]
  print('A2_RENDER_START',label,flush=True);start=time.monotonic()
  logfile=out/(label+'.log')
  if logfile.exists():
   assert resume
   logfile.rename(out/(label+'-interrupted-'+str(time.time_ns())+'.log'))
  with logfile.open('w') as f:r=subprocess.run(args,cwd=HERE,stdout=f,stderr=subprocess.STDOUT)
  report['commands'].append({'label':label,'argv':args,'cwd':str(HERE),'exit_code':r.returncode,'seconds':round(time.monotonic()-start,2)});report['status']='FAIL' if r.returncode else 'RUNNING';(out/'commands.json').write_text(json.dumps(report,indent=2)+'\n')
  print('A2_RENDER_DONE',label,r.returncode,flush=True)
  if r.returncode:raise SystemExit(r.returncode)
 report['status']='RENDERS_COMPLETE; comparison and independent review pending';(out/'commands.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--blender',required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args();main(a.blender,a.resume)
