import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network';source=ROOT/'blender/facility_master_A06_connections.blend';dest=ROOT/'blender/facility_master_A07_horizontal_network.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.scenes=src.scenes
scenes=dst.scenes
with bpy.data.libraries.load(str(OUT/'network-R03.blend'),link=False) as (src,dst):dst.collections=['09_FINISHED_HORIZONTAL_CONNECTIONS']
for s in scenes:
 s.collection.children.link(dst.collections[0]);s.name='FACILITY_A07_HORIZONTAL_NETWORK';s['horizontal_connections']='21 routes built; R19 stairs/lift and source door actuation remain separate step 2.'
for name in ['CONNECTIONS_ALL_ROUTES_GREYBOX','02_UNBUILT_CONNECTION_RESERVATIONS']:
 c=bpy.data.collections.get(name)
 if c:c.hide_render=True;c.hide_viewport=True
bpy.data.libraries.write(str(dest),set(scenes),compress=True,path_remap='RELATIVE')
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(ROOT/'production/NETWORK_A07_MASTER.json').write_text(json.dumps({'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'A06_preserved':True,'source_sha256':before,'network_asset':'connections/network/network-R03.blend'},indent=2));print('A07_MASTER_SAVED',flush=True)
