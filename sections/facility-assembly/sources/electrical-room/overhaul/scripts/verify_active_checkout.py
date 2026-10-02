"""Run the repo map check, retaining its receipt without overwriting historic evidence."""
import argparse, json, os, runpy, sys, traceback
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[6]
manifest=json.loads((root/'MAP.json').read_text())
historic=root/manifest['section_root']/'production/MAIN_CHECKOUT_VALIDATION.json'
previous=historic.read_bytes() if historic.exists() else None
out=Path(a.out).resolve();assert out!=historic
status=1
try:
    runpy.run_path(str(root/'sections/facility-assembly/blender/verify_map_checkout.py'),run_name='__main__')
    report=json.loads(historic.read_text())
    report['additional_scope_note']='Repo checker validates file containment, frozen accepted-source hashes and preview-control registration. It does not detect missing linked datablock names; separate electrical candidate audit records the unchanged128 inherited spawn IDs.'
    out.write_text(json.dumps(report,indent=2)+'\n')
    status=0 if report['pass'] else 1
except BaseException as exc:
    traceback.print_exc()
    out.write_text(json.dumps({'pass':False,'scope':'Active checkout wrapper failed; no new successful repo-check receipt.',
                              'error':str(exc),'traceback':traceback.format_exc()},indent=2)+'\n')
finally:
    if previous is None:historic.unlink(missing_ok=True)
    else:historic.write_bytes(previous)
print('ACTIVE_CHECKOUT_RECEIPT',str(out),'STATUS',status,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(status)
