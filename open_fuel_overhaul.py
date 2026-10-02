"""Open the canonical map with its live fuel module instead of the old fuel cache.

blender --python open_fuel_overhaul.py
Headless proof: blender -b --python open_fuel_overhaul.py -- --render C03_HERO

All other current-map assets and transforms are retained. This is a disposable
live view, not a rewrite of the canonical map or its immutable preview cache.
"""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parent
MAP=ROOT/'sections/facility-assembly/blender/facility_environment.blend'
FUEL=ROOT/'sections/facility-assembly/sources/fuel-corridor/module.blend'

def exclude_map_fill_from_fuel(module,instance):
    """Keep map daylight helpers off fuel receivers without changing other rooms.

    Receiver collections are dependency lists, not extra scene membership.
    Include both the instance and its prototype surfaces because Cycles evaluates
    collection instances through the prototype geometry. Preserve any preexisting
    receiver exclusions on a private copy rather than replacing their policy.
    """
    targets=[instance]+[o for o in module.all_objects if o.type in {'MESH','FONT','CURVE','SURFACE'}]
    shared=bpy.data.collections.get('INTEGRATION | Fuel daylight exclusions')
    if shared is None:shared=bpy.data.collections.new('INTEGRATION | Fuel daylight exclusions')
    def exclude(collection):
        for target in targets:
            if target.name not in collection.objects:collection.objects.link(target)
        for target in targets:
            index=collection.objects.find(target.name)
            assert index>=0,'Missing fuel light receiver'
            collection.collection_objects[index].light_linking.link_state='EXCLUDE'
    exclude(shared)
    records=[]
    for light in bpy.context.scene.objects:
        if light.type!='LIGHT' or light.data.type!='SUN' or light.hide_render:continue
        previous=light.light_linking.receiver_collection
        owned_name='INTEGRATION | Fuel daylight exclusions | '+light.name
        if previous and previous not in [shared,bpy.data.collections.get(owned_name)]:
            receiver=bpy.data.collections.get(owned_name)
            if receiver is None:
                receiver=previous.copy();receiver.name=owned_name
        else:receiver=previous or shared
        exclude(receiver);light.light_linking.receiver_collection=receiver
        records.append({'light':light.name,'receiver_collection':receiver.name,
                        'fuel_receivers_excluded':len(targets),'energy_retained':light.data.energy,
                        'outside_fuel_receivers':'unchanged'})
    instance['fc_lighting_policy']=json.dumps({'scope':'Fuel receivers only; no helper suns or sky-bounce lights illuminate the enclosed corridor.',
                                              'map_world':'Original physical outdoor sky retained; no room ambient fill added.',
                                              'excluded_map_helpers':records})
    return records

def install_live_fuel():
    """Install into the already opened authoring map; safe to call repeatedly."""
    cached=bpy.data.objects.get('VC | Roof-finished MATERIAL_PREVIEW_fuel-corridor')
    assert cached and cached.type=='MESH','Canonical fuel cache changed; inspect before using this helper'
    cached.hide_render=True;cached.hide_set(True)
    # Exact old fuel fixture names, taken from the protected module baseline.
    build=json.loads((ROOT/'sections/fuel-corridor/production/BUILD_MANIFEST.json').read_text())
    assert build['stage']=='full' and hashlib.sha256(FUEL.read_bytes()).hexdigest()==build['sha256'],'Fuel source and production manifest differ; rebuild or restore a verified pair'
    names={o['name'] for o in build['baseline_asset_inventory'] if o['type']=='LIGHT'}
    hidden=[]
    for ob in bpy.context.scene.objects:
        if ob.type=='LIGHT' and ob.name.startswith('VC | Restored INTERIOR_') and ob.name.removeprefix('VC | Restored INTERIOR_') in names:
            ob.hide_render=True;ob.hide_set(True);hidden.append(ob.name)
    module=next((c for c in bpy.data.collections if c.library and c.name=='MODULE_fuel-corridor' and Path(bpy.path.abspath(c.library.filepath)).resolve()==FUEL),None)
    if module is None:
        with bpy.data.libraries.load(str(FUEL),link=True) as (src,dst):
            assert 'MODULE_fuel-corridor' in src.collections
            dst.collections=['MODULE_fuel-corridor']
        module=dst.collections[0]
    collection=bpy.data.collections.get('INTEGRATION | Live fuel overhaul') or bpy.data.collections.new('INTEGRATION | Live fuel overhaul')
    if collection.name not in bpy.context.scene.collection.children:bpy.context.scene.collection.children.link(collection)
    inst=bpy.data.objects.get('FUEL_OVERHAUL_LIVE') or bpy.data.objects.new('FUEL_OVERHAUL_LIVE',None)
    if inst.name not in collection.objects:collection.objects.link(inst)
    inst.instance_type='COLLECTION';inst.instance_collection=module
    placement=json.loads((ROOT/'sections/facility-assembly/production/LAYOUT_A12.json').read_text())['placements']['fuel-corridor']
    inst.matrix_world=Matrix.LocRotScale(Vector(placement['translation']),Matrix.Rotation(__import__('math').radians(placement['rotation_z_degrees']),4,'Z').to_quaternion(),Vector(placement['scale']))
    inst['source_module']='//sections/facility-assembly/sources/fuel-corridor/module.blend';inst['scope']='Live fuel replacement; main file untouched'
    exclude_map_fill_from_fuel(module,inst)
    bpy.context.view_layer.update()
    assert module.library and len(module.all_objects)>100
    return module,inst,cached,hidden

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render');ap.add_argument('--out');opts=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    before=hashlib.sha256(MAP.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(MAP),load_ui=False)
    module,inst,cached,hidden=install_live_fuel()
    report={'schema':'fuel-live-map-integration/1','canonical_map_sha256_before':before,'canonical_map_sha256_after':hashlib.sha256(MAP.read_bytes()).hexdigest(),'module_sha256':hashlib.sha256(FUEL.read_bytes()).hexdigest(),'linked_collection':module.name,'module_objects':len(module.all_objects),'placement':[list(r) for r in inst.matrix_world],'hidden_old_cache':cached.name,'hidden_old_lights':hidden,'source_registry_and_frozen_snapshots':'unchanged','saved_main':False}
    report['lighting_policy']=json.loads(inst['fc_lighting_policy'])
    report['lighting_installer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if opts.render:
        camera=next(o for o in module.all_objects if o.name==opts.render and o.type=='CAMERA')
        sc=bpy.context.scene;sc.camera=camera;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=32;sc.cycles.seed=7;sc.cycles.use_denoising=True
        sc.render.resolution_x=960;sc.render.resolution_y=640;sc.render.resolution_percentage=100
        sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.15
        out=Path(opts.out).resolve() if opts.out else ROOT/'sections/fuel-corridor/production/renders/integration'/('main_'+opts.render+'.png')
        out.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(out);sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
        report['render']=str(out.relative_to(ROOT));report['render_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
    (ROOT/'sections/fuel-corridor/production/MAIN_LINK_VALIDATION.json').write_text(json.dumps(report,indent=2))
    print('LIVE_FUEL_IN_MAP',len(module.all_objects),'objects',len(hidden),'old lights hidden',flush=True)
    assert report['canonical_map_sha256_before']==report['canonical_map_sha256_after']
if __name__=='__main__':main()
