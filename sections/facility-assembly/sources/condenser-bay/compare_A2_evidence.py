"""Adapt the existing condenser comparison tool's paths and cloud CPU policy.
Numeric thresholds and image/camera/hash checks are unchanged. Adds the four
brief-mandated AAA cameras to the required main set. Does not grant art acceptance.
"""
import argparse, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parents[3] / 'sections/condenser-bay/production/compare_pack.py'

def main(warm, cold):
    required = set('C01_ENTRY C02_HERO C03_REVERSE C04_EXHAUST C05_RETURN C06_COOLING C07_OPERATOR C08_MAINT C09_ROOF C10_MATERIALS W01_ENTRY_CORNER W02_SW_TURN W03_NW W04_NE W05_SE W06_WEST_AISLE W07_EAST_PULL W08_GALLERY_TURN AAA01_WIDE_NE AAA02_PUMPS AAA03_OPERATOR AAA04_PULL_BAY'.split())
    if warm.endswith('-supplemental'):
        required = set('S01_LOCAL_U02 S02_LOCAL_CW S03_FULL_ROOF S04_GLASS S05_FEET S06_OPERATOR_WORK S07_U04_CUTAWAY'.split())
    a=json.loads((HERE/'renders-A2'/warm/'render_manifest.json').read_text())
    b=json.loads((HERE/'renders-A2'/cold/'render_manifest.json').read_text())
    for key in ['sha256','cpu_threads','linux_nice']:
        assert a['cloud_resource_adapter'][key] == b['cloud_resource_adapter'][key], 'Cloud adapter changed: '+key
    source = ORIGINAL.read_text()
    source = source.replace('ROOT=Path(__file__).resolve().parent', 'ROOT=Path('+repr(str(HERE))+')')
    source = source.replace("ROOT/'renders'/'review'", "ROOT/'renders-A2'")
    source = source.replace("ROOT/'validation'", "ROOT/'evidence-A2'")
    source = source.replace("ROOT/'critics'", "ROOT/'critics-A2'")
    line = next(x for x in source.splitlines() if x.startswith('required=('))
    source = source.replace(line, 'required='+repr(required))
    source = source.replace("manifest.get('cpu_threads')==2", "manifest.get('cpu_threads')==5")
    source = source.replace("manifest.get('process_priority')=='IDLE'", "manifest.get('process_priority')=='NICE10'")
    source = source.replace('../renders/review/', '../renders-A2/')
    (HERE/'critics-A2').mkdir(exist_ok=True)
    out=HERE/'evidence-A2'/warm;out.mkdir(parents=True,exist_ok=True)
    (out/'comparison-adapter.json').write_text(json.dumps({'original':str(ORIGINAL.relative_to(HERE.parents[3])),'original_sha256':hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'numeric_policy_changed':False,'adaptations':['A2 output paths','22 main cameras rather than 18; same seven supplements','cloud CPU five threads rather than historical Windows two','actual Linux nice10 priority rather than historical Windows IDLE'],'scope':'Cold/stability numeric screen; independent visual inspection remains required'},indent=2)+'\n')
    sys.argv=[str(ORIGINAL),warm] if cold == 'cold-'+warm else [str(ORIGINAL),warm,cold]
    exec(compile(source,str(ORIGINAL),'exec'),{'__name__':'__main__','__file__':str(ORIGINAL)})

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('warm');ap.add_argument('cold')
    args=ap.parse_args();main(args.warm,args.cold)
