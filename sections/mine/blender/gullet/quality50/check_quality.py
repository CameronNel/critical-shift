"""Cold-start checks on actual Blender scene data, geometry and controls."""
import bpy,sys,json,argparse,math
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import controls
from geology_repairs import tree

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    scene=next(s for s in bpy.data.scenes if s.get('q50_revision'))
    if bpy.context.window:bpy.context.window.scene=scene
    report={'blender':bpy.app.version_string,'fresh_process':True,'source_file':Path(bpy.data.filepath).name,'checks':0,'issues':[],'scope':'Actual meshes, packed images, fifty cameras, cart contacts and art-state controls; not a universal no-intersection proof or Unity runtime test.'}
    def check(ok,msg):
        report['checks']+=1
        if not ok:report['issues'].append(msg)
    cameras=[o for o in scene.objects if o.type=='CAMERA'];check(len(cameras)==50,'Exactly 50 cameras required');check({o.name for o in cameras}=={f'CAM_{i:02}' for i in range(1,51)},'Camera names')
    meshes=[o for o in scene.objects if o.type=='MESH' and not o.get('q50_volumetric')]
    for o in meshes:
        check(bool(o.data.polygons),'Empty mesh '+o.name);check(all(math.isfinite(c) for v in o.data.vertices for c in v.co),'Nonfinite vertices '+o.name)
        check(all(p.area>1e-12 for p in o.data.polygons),'Zero-area face '+o.name)
    materials={slot.material for o in meshes if not o.get('csm_collision_only') for slot in o.material_slots if slot.material}
    images={n.image for m in materials if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for im in images:check(bool(im.packed_file) and len(im.packed_file.data)>16 and im.size[0]>0,'Missing packed image '+im.name)
    report['packed_images']=len(images)
    saved=scene['csm_states_json'];gate=scene.objects['CSM_CTRL_BLAST_GATE'].get('csm_open_fraction',1)
    try:
        for sec in 'ABC':
            controls.reset(scene)
            for index,state in [(1,1),(3,2),(1,2),(5,3)]:check(controls.excavate(scene,sec,index)['state']==state,'Monotonic excavation '+sec)
            check(controls.excavate(scene,sec,7)['remaining_rubble']==22,'22 rubble pieces '+sec)
            for index in [1,5,12]:
                blocked=False
                try:controls.excavate(scene,sec,index)
                except ValueError:blocked=True
                check(blocked,'Uncleared collapse bypass '+sec)
            for i in range(22):
                st=controls.clear(scene,sec);check(st['remaining_rubble']==21-i,'Rubble decrement '+sec);check(st['state']==(3 if i==21 else 4),'Premature reopening '+sec)
            for other in 'ABC':
                if other!=sec:check(controls.read(scene)[other]['state']==0,'Cross-sector state leak')
        for frac in [0,.25,.50,.75,1]:
            controls.gate(scene,frac)
            for key in ['CSM_Blast_leaf_L','CSM_Blast_leaf_R']:
                leaf=scene.objects[key];check(abs(leaf.location.x-(leaf['csm_closed_x']+leaf['csm_travel']*frac))<1e-6,'Gate motion '+key)
    finally:scene['csm_states_json']=saved;controls.refresh(scene);controls.gate(scene,gate)
    report['cart_contacts']=[]
    rails=tree([o for o in meshes if 'Continuous_I_rail' in o.name])
    for key in ['CSM_Dispatch_cart','CSM_Loaded_haulage_cart']:
        root=scene.objects[key];check(root.get('q50_wooden_cart',False),'Wooden cart missing '+key)
        rims=[o for o in root.children if 'Cart_top_wood_rail' in o.name]
        heights=[(o.matrix_world@v.co).z+.025*max((o.matrix_world@v.co).y,0) for o in rims for v in o.data.vertices]
        check(heights and max(heights)<1.15,'Cart rim too high '+key)
        for o in [o for o in root.children if o.get('q50_wheel_radius')]:
            center=o.matrix_world@Vector((.61 if sum(v.co.x for v in o.data.vertices)>0 else -.61,0,.35))
            yy=sum((o.matrix_world@v.co).y for v in o.data.vertices)/len(o.data.vertices);xx=.55 if center.x>0 else -.55;zz=-.025*max(yy,0)
            wheel_tree=tree([o]);wh=wheel_tree.ray_cast(Vector((xx,yy,zz+.10)),Vector((0,0,1)),.6);rh=rails.ray_cast(Vector((xx,yy,zz+.50)),Vector((0,0,-1)),.6)
            gap=(wh[0].z-rh[0].z) if wh[0] is not None and rh[0] is not None else None
            report['cart_contacts'].append({'wheel':o.name,'rail_gap_m':gap});check(gap is not None and -.003<=gap<=.01,'Wheel/rail contact '+o.name+': '+str(gap))
    overlaps=[]
    for sec in 'ABC':
        rocks=[o for o in meshes if o.get('q50_fractured_block') and o.get('csm_sector')==sec]
        check(len(rocks)==22,'Rubble geometry count '+sec)
        trees=[tree([o]) for o in rocks]
        for i in range(len(rocks)):
            for j in range(i+1,len(rocks)):
                pairs=trees[i].overlap(trees[j])
                if pairs:overlaps.append({'a':rocks[i].name,'b':rocks[j].name,'triangle_pairs':len(pairs)})
    report['rubble_triangle_overlap_candidates']=overlaps
    report['status']='PASS' if not report['issues'] else 'FAIL';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2));print('Q50_COLD_START',json.dumps(report),flush=True)
    if report['issues']:raise RuntimeError('Quality checks failed: '+'; '.join(report['issues'][:15]))
if __name__=='__main__':main()
