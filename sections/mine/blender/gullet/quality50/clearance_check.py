"""Sample standing clearance and gate-leaf/frame intersections in the actual scene."""
import bpy,sys,json,math,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
import controls
from geology_repairs import tree

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    s=next(s for s in bpy.data.scenes if s.get('q50_revision'));bpy.context.window.scene=s
    vv=[];ff=[];names=[]
    for o in s.objects:
        if o.type!='MESH' or o.hide_render or o.get('csm_collision_only') or o.get('q50_volumetric'):continue
        offset=len(vv);vv.extend(o.matrix_world@v.co for v in o.data.vertices)
        for poly in o.data.polygons:ff.append(tuple(offset+i for i in poly.vertices));names.append(o.name)
    bvh=BVHTree.FromPolygons(vv,ff);routes={'main':[(1.95,-13),(1.95,36)],'service':[(3,12),(6,13.9),(8.4,16),(8.2,19),(7.69,21.6),(8,24.3),(6.5,27.3),(3,28.3)]}
    results=[];problems=[]
    for name,points in routes.items():
        probes=0
        for a2,b2 in zip(points,points[1:]):
            a0=Vector((*a2,0));b0=Vector((*b2,0));n=math.ceil((b0-a0).length/.28)
            for j in range(n+1):
                base=a0.lerp(b0,j/n);base.z=-.025*max(base.y,0)
                for height in [.35,.90,1.72]:
                    origin=base+Vector((0,0,height))
                    for theta in [k*math.tau/8 for k in range(8)]:
                        d=Vector((math.cos(theta),math.sin(theta),0));hit=bvh.ray_cast(origin,d,.25);probes+=1
                        if hit[0] is not None:problems.append({'route':name,'point':list(origin),'object':names[hit[2]],'clearance_m':hit[3]})
        results.append({'route':name,'radial_probes':probes,'body_radius_m':.25,'sample_spacing_m':.28,'sample_heights_m':[.35,.9,1.72]})
    gate_original=s.objects['CSM_CTRL_BLAST_GATE'].get('csm_open_fraction',1)
    frame=[o for o in s.objects if o.type=='MESH' and any(t in o.name for t in ['Portal_buttress','Reveal_steel_jamb','Shotcrete_portal_collar','Portal_inner_lining','Pocket_guard','Gate_recess_rear'])]
    frame_tree=tree(frame);gate_conflicts=[];gate_samples=[]
    for fraction in [i/8 for i in range(9)]:
        controls.gate(s,fraction)
        for key in ['CSM_Blast_leaf_L','CSM_Blast_leaf_R']:
            leaf=s.objects[key]
            body=[o for o in leaf.children_recursive if o.type=='MESH' and any(t in o.name for t in ['Leaf_solid_core','Leaf_outer_skin','Leaf_vertical_stiffener','Leaf_cross_rib','Rail_notched_bottom_skirt','Gate_rear_'])]
            overlap=tree(body).overlap(frame_tree)
            gate_samples.append({'leaf':key,'open_fraction':fraction,'triangle_overlap_pairs':len(overlap)})
            if overlap:gate_conflicts.append(gate_samples[-1])
    controls.gate(s,gate_original)
    report={'gate_sweep_samples':gate_samples,'gate_frame_conflicts':gate_conflicts,'blender':bpy.app.version_string,'source_file':Path(bpy.data.filepath).name,'status':'PASS' if not problems and not gate_conflicts else 'REVIEW_REQUIRED','routes':results,'collisions':problems,'scope':'Sampled standing-body envelope and nine gate positions. Not a continuous character-controller or swept-collider test.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2));print('ROUTE_CLEARANCE',json.dumps(report))
if __name__=='__main__':main()
