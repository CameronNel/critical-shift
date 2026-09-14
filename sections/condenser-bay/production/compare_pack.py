"""Honest numeric cold comparison and browsable fixed-camera review gallery."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
rev=sys.argv[1]
comparison_pack=sys.argv[2] if len(sys.argv)>2 else 'cold-'+rev
comparison_kind='stability' if len(sys.argv)>2 else 'cold'
warm=ROOT/'renders'/'review'/rev
cold=ROOT/'renders'/'review'/comparison_pack
out=ROOT/'validation'/rev
out.mkdir(parents=True,exist_ok=True)
wm=json.loads((warm/'render_manifest.json').read_text())
cm=json.loads((cold/'render_manifest.json').read_text())
wby={c['camera']:c for c in wm['cameras']}; cby={c['camera']:c for c in cm['cameras']}
required=(set('S01_LOCAL_U02 S02_LOCAL_CW S03_FULL_ROOF S04_GLASS S05_FEET S06_OPERATOR_WORK S07_U04_CUTAWAY'.split()) if rev.endswith('-supplemental') else set('C01_ENTRY C02_HERO C03_REVERSE C04_EXHAUST C05_RETURN C06_COOLING C07_OPERATOR C08_MAINT C09_ROOF C10_MATERIALS W01_ENTRY_CORNER W02_SW_TURN W03_NW W04_NE W05_SE W06_WEST_AISLE W07_EAST_PULL W08_GALLERY_TURN'.split()))
assert set(wby)==set(cby)==required, 'Incomplete or mismatched camera evidence'
for field in ['engine','samples','resolution','blend_sha256']:
    assert wm.get(field) is not None and wm[field]==cm.get(field), f'Mismatched {field}'
if wm.get('engine')=='CYCLES':
    for field in ['device','cpu_threads','process_priority','gpu_denoising','gpu_backend','gpu_devices','hardware_raytracing','persistent_data']:
        assert wm.get(field)==cm.get(field), f'Resource/backend setting differs: {field}'
    for manifest in (wm,cm):
        if manifest.get('device')=='CPU':
            assert manifest.get('cpu_threads')==2 and manifest.get('process_priority')=='IDLE' and manifest.get('gpu_denoising') is False, 'Historical CPU policy differs'
        else:
            assert manifest.get('device')=='GPU' and manifest.get('gpu_backend')=='HIP' and manifest.get('gpu_devices'), 'Unverified GPU backend'
    assert wm.get('render_settings') and wm['render_settings']==cm.get('render_settings'), 'CPU render settings differ'
    assert wm.get('renderer_source_sha256') and wm['renderer_source_sha256']==cm.get('renderer_source_sha256'), 'Warm/cold renderer source differs'
rows=[]
html=['<!doctype html><meta charset="utf-8"><title>Condenser '+rev+' — review, not acceptance</title>',
      '<style>body{background:#202326;color:#eee;font:16px system-ui;margin:32px}section{margin:24px 0}img{width:49%;vertical-align:top}a{color:#e7b36c}</style>',
      '<h1>Condenser '+rev+' — review evidence</h1><p>Left: '+rev+'. Right: '+comparison_pack+'. Acceptance is recorded by the independent critic.</p>']
for name in sorted(wby):
    for field in ['location','lens','matrix_world']:
        assert wby[name].get(field) is not None and wby[name][field]==cby[name].get(field), f'Camera {field} differs: {name}'
    assert wby[name].get('process_id') and cby[name].get('process_id'), f'Missing process identity: {name}'
    a=warm/(name+'.png'); b=cold/(name+'.png')
    assert hashlib.sha256(a.read_bytes()).hexdigest()==wby[name]['sha256'], f'Warm image changed: {name}'
    assert hashlib.sha256(b.read_bytes()).hexdigest()==cby[name]['sha256'], f'Cold image changed: {name}'
    ia=np.asarray(Image.open(a).convert('RGB'),dtype=np.int16)
    ib=np.asarray(Image.open(b).convert('RGB'),dtype=np.int16)
    assert ia.shape==ib.shape==(1080,1920,3), f'Wrong image dimensions: {name}'
    d=np.abs(ia-ib)
    rows.append({'camera':name,'resolution':[ia.shape[1],ia.shape[0]],
                 'warm_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),
                 'cold_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),
                 'max_channel_delta_255':int(d.max()),'mean_channel_delta_255':float(d.mean()),
                 'changed_pixel_fraction':float(np.any(d,axis=2).mean()),
                 'fraction_pixels_delta_gt8':float(np.any(d>8,axis=2).mean()),
                 'warm_process_id':wby[name].get('process_id'),'cold_process_id':cby[name].get('process_id'),
                 'separate_process':wby[name].get('process_id')!=cby[name].get('process_id')})
    html.append(f'<section><h2>{name}</h2><img src="../renders/review/{rev}/{name}.png"><img src="../renders/review/{comparison_pack}/{name}.png"></section>')
summary={'revision':rev,'count':len(rows),'same_saved_blend':wm.get('blend_sha256')==cm.get('blend_sha256'),
         'comparison_pack':comparison_pack,'comparison_kind':comparison_kind,
         'all_separate_process':all(r['separate_process'] for r in rows),
         'all_1920x1080':all(r['resolution']==[1920,1080] for r in rows),
         'worst_mean_delta_255':max(r['mean_channel_delta_255'] for r in rows),
         'visual_acceptance':'independent pixel review required','cameras':rows}
# A conservative numeric screen, separate from the critic's visual decision.
# Preserve the full report even when a pair fails; never turn a report-only
# subprocess exit code into a claimed successful cold/stability check.
limits=({'maximum_channel_delta_255':32,'mean_channel_delta_255':0.10,'fraction_pixels_delta_gt8':0.001} if wm.get('device')=='GPU' else {'maximum_channel_delta_255':2,'mean_channel_delta_255':0.01,'fraction_pixels_delta_gt8':0.0})
summary['numeric_tolerance']=limits
summary['numeric_match']=all(r['max_channel_delta_255']<=limits['maximum_channel_delta_255'] and r['mean_channel_delta_255']<=limits['mean_channel_delta_255'] and r['fraction_pixels_delta_gt8']<=limits['fraction_pixels_delta_gt8'] for r in rows)
summary['status']='PASS' if summary['all_separate_process'] and summary['all_1920x1080'] and summary['numeric_match'] else 'FAIL'
(out/(comparison_kind+'-comparison.json')).write_text(json.dumps(summary,indent=2))
(ROOT/'critics'/('astra-'+rev+('-stability' if comparison_kind=='stability' else '')+'-gallery.html')).write_text('\n'.join(html))
print(json.dumps({k:v for k,v in summary.items() if k!='cameras'},indent=2))
raise SystemExit(0 if summary['status']=='PASS' else 1)
