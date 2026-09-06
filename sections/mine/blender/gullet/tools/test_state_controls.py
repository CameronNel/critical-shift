"""Test authoring-state functions against lightweight object doubles, not bpy."""
from pathlib import Path
import sys,json,types
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import build_mine as B
class ObjectDouble(dict):
 def __init__(self,name,meta,matrix):
  super().__init__(csm_id=name,csm_meta=json.dumps(meta));B.set_meta(self,meta);self.name=name+'.simulated_duplicate_suffix';self.location=types.SimpleNamespace(x=float(matrix[0,3]));self.hide_render=False;self.hidden=False
 def hide_set(self,value):self.hidden=bool(value)
class SceneDouble(dict):pass

def test():
 data=B.build_scene_data();scene=SceneDouble();scene.objects=[]
 for item in data.items:scene.objects.append(ObjectDouble(item.name,item.meta,item.matrix))
 for item in data.empties:scene.objects.append(ObjectDouble(item['name'],item['meta'],item['matrix']))
 old=sys.modules.get('bpy');sys.modules['bpy']=types.SimpleNamespace(context=types.SimpleNamespace(view_layer=types.SimpleNamespace(update=lambda:None)));assertions=0
 try:
  for sec in B.SECTORS:
   B.reset_states(scene)
   for index,stage in [(1,1),(3,2),(1,2),(5,3)]:assert B.apply_excavation_event(scene,sec,index)['state']==stage;assertions+=1
   collapsed=B.apply_excavation_event(scene,sec,7);assert collapsed['remaining_rubble']==22;assertions+=1
   for index in [1,5,12]:
    try:B.apply_excavation_event(scene,sec,index)
    except ValueError:assertions+=1
    else:raise AssertionError('Uncleared collapse was bypassed')
   for n in range(22):
    state=B.clear_next_rubble(scene,sec);assert state['remaining_rubble']==21-n;assertions+=1;assert state['state']==(3 if n==21 else 4);assertions+=1
   for other in B.SECTORS:
    if other!=sec:assert B.read_states(scene)[other]['state']==0;assertions+=1
  leaves=[o for o in scene.objects if o.get('csm_id') in [B.PREFIX+'Blast_leaf_L',B.PREFIX+'Blast_leaf_R']];before={o['csm_id']:o.location.x for o in scene.objects if o not in leaves}
  for fraction in [0.,.25,1.]:
   B.set_gate(scene,fraction)
   for o in leaves:assert abs(o.location.x-(o['csm_closed_x']+o['csm_travel']*fraction))<1e-8;assertions+=1
  for o in scene.objects:
   if o['csm_id'] in before:assert o.location.x==before[o['csm_id']]
  assertions+=1
  for bad in [float('nan'),float('inf'),-1.]:
   try:B.state_from_index(bad)
   except ValueError:assertions+=1
   else:raise AssertionError('Invalid index accepted')
 finally:
  if old is None:del sys.modules['bpy']
  else:sys.modules['bpy']=old
 report={'status':'PASS','explicit_state_assertions':assertions,'scope':'State and visibility logic on object doubles. This is NOT execution of Blender or its API.','checked':['Unlock monotonicity','Independent sectors','Uncleared collapse cannot be bypassed','Exactly 22 rubble removals before traversal unlock','Gate moves roots, not individual mesh children','Duplicate-name robustness through semantic IDs','Invalid numeric inputs rejected']}
 (ROOT/'validation').mkdir(exist_ok=True);(ROOT/'validation'/'state_controls.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':test()
