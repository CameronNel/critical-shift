"""Record reproducible native-render batch performance without implying viewport FPS."""
import json,re,hashlib,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];rev=sys.argv[1];O=R/'production/spawn-exterior-review';D=O/('renders-'+rev)
log=(R/'production'/('spawn-render-'+rev+'.log')).read_text(errors='replace');manifest=json.loads((D/'MANIFEST.json').read_text());rows=[]
for match in re.finditer(r'(\d+):(\d+\.\d+)\s+render\s+\| Saved:.*?([^/\\]+\.png)',log):
 name=match.group(3);p=D/name
 if not p.exists():continue
 data=p.read_bytes();w,h=struct.unpack('>II',data[16:24]);rows.append({'view':p.stem,'elapsed_process_seconds':int(match.group(1))*60+float(match.group(2)),'resolution':[w,h],'png_sha256':hashlib.sha256(data).hexdigest()})
report={'revision':rev,'source_sha256':manifest['source_sha256'],'engine':'EEVEE','raytracing':False,'samples':manifest.get('render_samples',32),'frames':rows,'four_frame_batch_completed':len(rows)==4 and 'FOUR_VIEWS_COMPLETE' in log,'scope':'Cold Blender load followed by four fixed native-material render frames. First timestamp includes load/setup/shader compilation. This is an offline-render stability and timing benchmark, not viewport FPS or Unity performance.','preview_fps':'UNVERIFIED','unity_runtime':'UNVERIFIED'}
(O/('RENDER_BENCHMARK_'+rev+'.json')).write_text(json.dumps(report,indent=2));print(json.dumps({'revision':rev,'frames':len(rows),'complete':report['four_frame_batch_completed']}))
