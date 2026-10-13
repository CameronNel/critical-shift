"""Read-only native pipeline memory observations; no process control or asset edits."""
from pathlib import Path
import json,time,datetime
state=Path('/tmp/cs-main342-native-pipeline-final15-r2.json');log=Path('/tmp/cs-main342-native-final15-r2/native-memory-observations-final15-r2-main342.jsonl')
assert not log.exists()
with log.open('x') as output:
 while True:
  try:stage=json.loads(state.read_text())
  except (FileNotFoundError,json.JSONDecodeError):stage={}
  current=int(Path('/sys/fs/cgroup/memory.current').read_text());stats=dict(x.split(' ',1) for x in Path('/sys/fs/cgroup/memory.stat').read_text().splitlines())
  record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'memoryBytes':current,'shmemBytes':int(stats['shmem']),'anonBytes':int(stats['anon']),'fileBytes':int(stats['file']),'kernelBytes':int(stats['kernel']),'events':dict((k,int(v)) for k,v in (x.split() for x in Path('/sys/fs/cgroup/memory.events').read_text().splitlines())),'status':stage.get('status'),'activeStep':stage.get('activeStep')}
  output.write(json.dumps(record)+'\n');output.flush()
  if stage.get('status','').startswith(('Completed','Failed')):break
  time.sleep(2)
print('Finished read-only memory observation',flush=True)
