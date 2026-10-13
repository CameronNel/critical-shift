from pathlib import Path
import bpy,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');source=root/'runtime/out/spawn-export-source/combined-runtime-source.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(source);records=[]
for o in bpy.data.objects['ROOM_front-end-area'].instance_collection.all_objects:
 if o.type!='LIGHT' or o.data.type!='SPOT':continue
 d=o.data;outputs=[n for n in d.node_tree.nodes if n.type=='OUTPUT_LIGHT' and n.is_active_output];assert len(outputs)==1;links=list(outputs[0].inputs['Surface'].links);assert len(links)==1 and links[0].from_node.type=='EMISSION';e=links[0].from_node;assert not e.inputs['Color'].is_linked and not e.inputs['Strength'].is_linked and tuple(e.inputs['Color'].default_value)==(1,1,1,1) and e.inputs['Strength'].default_value==1
 records.append({'name':o.name,'activeOutput':outputs[0].name,'surfaceLinkFrom':e.name,'surfaceLinkSocket':links[0].from_socket.name,'neutralColor':list(e.inputs['Color'].default_value),'strength':e.inputs['Strength'].default_value})
assert len(records)==6 and sha(source)==h
out=Path('/tmp/cs-mine-front-spot-closure-final14.json');assert not out.exists();out.write_text(json.dumps({'status':'ReadOnlySourceActiveSpotClosureVerified','sourceSnapshotSha256':h,'helperSha256':sha(Path(__file__)),'emitters':records,'limits':['No render/save; numeric fixture equivalence requires separate node enabled pixel comparison']},indent=2)+'\n');print('CS_ACTUAL_SPOT_CLOSURE_OK')
