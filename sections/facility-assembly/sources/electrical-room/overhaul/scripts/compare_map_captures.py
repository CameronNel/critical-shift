"""Compare assembled-map pixels with explicit same-module integration provenance."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

p=argparse.ArgumentParser()
for name in ['previous','cold','previous-integration','cold-integration','previous-audit','cold-audit','out']:
    p.add_argument('--'+name,required=True)
p.add_argument('--require-identical-pixels',action='store_true',help='Optional bit-exact criterion, separate from provenance and independent visual acceptance')
a=p.parse_args();prior=Path(a.previous);cold=Path(a.cold)
read=lambda path:json.loads(Path(path).read_text())
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
left=read(prior/'manifest.json');right=read(cold/'manifest.json')
li=read(a.previous_integration);ri=read(a.cold_integration)
la=read(a.previous_audit);ra=read(a.cold_audit)
failures=[];results=[]
if li['module_sha256']!=ri['module_sha256']:failures.append('electrical source bytes differ')
if li['main_before_sha256']!=ri['main_before_sha256']:failures.append('canonical base map differs')
for manifest,receipt,audit in [(left,li,la),(right,ri,ra)]:
    if not (manifest['source_sha256']==receipt['candidate_sha256']==audit['candidate_sha256']):
        failures.append('candidate provenance differs')
    if not (receipt['module_sha256']==audit['module_sha256'] and receipt['main_before_sha256']==audit['base_sha256']):
        failures.append('module/base audit provenance differs')
    if not (receipt['main_unchanged'] and receipt['dependency_hashes_unchanged'] and not receipt['neighbor_transforms_changed']):
        failures.append('integration changed base/dependencies/neighbors')
    if not (audit['pass'] and audit['module_legacy_id_compatibility_pass'] and audit['inherited_missing_ids_unchanged']
            and audit['pre_promotion_base_missing_ids_unchanged'] and not audit['missing_object_data']):
        failures.append('bounded link audit failed')
if la['candidate_missing_id_count']!=ra['candidate_missing_id_count']:failures.append('inherited missing-ID count differs')
for key in ['blender','embedded_python','samples','resolution','renderer']:
    if left[key]!=right[key]:failures.append('capture settings differ:'+key)
lm={v['camera']:v for v in left['views']};rm={v['camera']:v for v in right['views']}
expected={'EI_C01_Entry','EI_C03_Reverse','EI_C04_Route','EI_W01_Turbine_Return','EI_W02_Waste_Approach'}
if set(lm)!=expected or set(rm)!=expected:failures.append('five actual-map view sets differ')
for name in sorted(set(lm)&set(rm)):
    if any(lm[name][key]!=rm[name][key] for key in ['matrix','lens']):failures.append('camera differs:'+name)
    lp=prior/(name+'.png');rp=cold/(name+'.png')
    if sha(lp)!=lm[name]['sha256'] or sha(rp)!=rm[name]['sha256']:failures.append('invalid image hash:'+name)
    with Image.open(lp) as il,Image.open(rp) as ir:
        l=il.convert('RGB');r=ir.convert('RGB')
        if l.size!=r.size:failures.append('dimensions differ:'+name);continue
        diff=ImageChops.difference(l,r);stat=ImageStat.Stat(diff);identical=diff.getbbox() is None
        results.append({'camera':name,'decoded_pixels_identical':identical,'mean_absolute_difference_8bit_rgb':stat.mean,
                        'maximum_channel_difference_8bit':max(v[1] for v in diff.getextrema())})
        if not identical and a.require_identical_pixels:failures.append('assembled-map pixels differ:'+name)
report={'mode':'same_module_assembled_candidate_stability','scope':'Two separately saved assembled candidates with the same electrical source and canonical base/dependencies. Candidate bytes may differ through relative source paths or save metadata; this is not a same-candidate-byte cold test or runtime certification.',
        'module_sha256':ri['module_sha256'],'base_sha256':ri['main_before_sha256'],
        'previous_candidate_sha256':li['candidate_sha256'],'current_candidate_sha256':ri['candidate_sha256'],
        'candidate_bytes_identical':li['candidate_sha256']==ri['candidate_sha256'],
        'views':results,'all_decoded_pixels_identical':len(results)==5 and all(v['decoded_pixels_identical'] for v in results),
        'require_identical_pixels':a.require_identical_pixels,
        'visual_acceptance':'Not assigned by this script. Independent reviewer must assess the complete images and measured differences.',
        'failures':failures,'pass':not failures}
Path(a.out).write_text(json.dumps(report,indent=2)+'\n')
print('ASSEMBLED_MAP_STABILITY',report['pass'],'PIXELS_IDENTICAL',report['all_decoded_pixels_identical'])
raise SystemExit(0 if not failures else 1)
