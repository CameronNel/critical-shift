"""Original numeric comparisons and lossless evidence arrangement; no art scores."""
import hashlib,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    pairs=[('R3','R4'),('R3-supplemental','R4-supplemental'),('R4','cold-R4'),('R4-supplemental','cold-R4-supplemental')]
    report={'status':'RUNNING','scope':'Numeric evidence gate, not independent art approval','commands':[]}
    out=HERE/'evidence-A2/final-comparisons';out.mkdir(exist_ok=True)
    for warm,cold in pairs:
        args=['python3','compare_A2_evidence.py',warm,cold];start=time.monotonic()
        with (out/(warm+'--'+cold+'.log')).open('w') as f:r=subprocess.run(args,cwd=HERE,stdout=f,stderr=subprocess.STDOUT)
        report['commands'].append({'argv':args,'exit_code':r.returncode,'seconds':round(time.monotonic()-start,2)})
        report['status']='FAIL' if r.returncode else 'RUNNING'
        (out/'commands.json').write_text(json.dumps(report,indent=2)+'\n')
        if r.returncode:raise SystemExit(r.returncode)
    subprocess.run(['python3','pack_A2_review.py','R3','R4','cold-R4','--owner'],cwd=HERE,check=True)
    report['status']='NUMERIC_COMPARISONS_PASS; independent full pixel review required'
    report['final_native_sha256']=hashlib.sha256((HERE/'module_aaa_A2.blend').read_bytes()).hexdigest()
    report['counts']={label:len(json.loads((HERE/'renders-A2'/label/'render_manifest.json').read_text())['cameras']) for label in ['R1','R2','R3','R3-supplemental','R4','R4-supplemental','cold-R4','cold-R4-supplemental']}
    (out/'commands.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
