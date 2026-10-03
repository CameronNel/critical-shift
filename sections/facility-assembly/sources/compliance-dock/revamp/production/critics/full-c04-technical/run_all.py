"""One read-only process for corrected independent probes and project validator."""
import argparse,runpy,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
for name in ['native_probe.py','uv_probe.py']:
    sys.argv=[str(HERE/name),'--','--expected-sha',a.expected_sha]
    runpy.run_path(str(HERE/name),run_name='__main__')
sys.argv=[str(ROOT/'validate_dock.py'),'--','--output',str(HERE/'validator-independent.json'),
          '--expected-stage','full','--interface',str(ROOT/'contracts/interface.json')]
runpy.run_path(str(ROOT/'validate_dock.py'),run_name='__main__')
print('ALL_READ_ONLY_PROBES_COMPLETED; process exits and releases every native handle')
