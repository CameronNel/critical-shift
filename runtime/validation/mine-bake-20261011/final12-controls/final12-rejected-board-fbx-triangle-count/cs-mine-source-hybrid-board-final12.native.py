from pathlib import Path
import subprocess,shutil,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';output=Path('/tmp/cs-mine-source-hybrid-board-final12');audit=root/'runtime/out/mine-bake-audit';proof=json.loads((output/'provenance.json').read_text())
for name,digest in proof['files'].items():
 if hashlib.sha256((output/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('Stale bounded Source '+name)
if hashlib.sha256((root/'runtime/out/spawn-export-source/combined-runtime-source.blend').read_bytes()).hexdigest()!=proof['sourceBlenderSha256']:raise RuntimeError('Changed Source blend')
selection=json.loads((output/'selection.json').read_text());selection['flatSourceWorldMatrix']=[value for row in selection['sourceWorldMatrix'] for value in row];(output/'selection-native.json').write_text(json.dumps(selection,indent=2)+'\n')
folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';features=project/'Assets/CriticalShift/Features/Player';helper=folder/'CsMineSourceHybridBoardFinal12.cs';shader=features/'CsMineSourceHybridBoardFinal12.shader'
assert not helper.exists() and not shader.exists()
shutil.copy2('/tmp/cs-mine-source-hybrid-board-final12.cs.txt',helper);shutil.copy2('/tmp/cs-mine-source-hybrid-board-final12.shader',shader)
try:
 with (audit/'source-hybrid-board-final12.wrapper.log').open('w') as log:
  process=subprocess.Popen(['xvfb-run','-a','-s','-screen 0 640x360x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineSourceHybridBoardFinal12.Render','-logFile',str(audit/'source-hybrid-board-final12.native.log')],cwd=root,stdout=log,stderr=subprocess.STDOUT)
  print('BOUNDED_NATIVE_PID',process.pid,flush=True);status=process.wait();print('BOUNDED_NATIVE_EXIT',status,flush=True)
  if status:raise SystemExit(status)
 print('CS_BOUNDED_HYBRID_READY_FOR_REVIEW',flush=True)
finally:
 for p in [helper,shader]:p.unlink(missing_ok=True);Path(str(p)+'.meta').unlink(missing_ok=True)
