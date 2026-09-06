#!/usr/bin/env python3
"""Gullet material repair: real Blender/Cycles with downloaded CC0 materials.
Run from Blender, or use:
blender -b --python-exit-code 1 --python pbr/build_textured_mine.py -- --render entry
The geometry/state authoring source is preserved in geometry_source.py.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse, hashlib, importlib.util, json, math, sys, time
import bpy
import numpy as np
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MATERIALS = ROOT.parents[1]/'assets'/'pbr' if ROOT.parent.name == 'blender' else HERE/'materials'
REVISION = '1.1.0-cc0-cycles'

def srgb(hex_value):
    rgb = [int(hex_value[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb)+(1.0,)

def load_manifest():
    path = MATERIALS/'download_manifest.json'
    if not path.is_file():
        raise FileNotFoundError('Downloaded CC0 textures are required. Run pbr/download_materials.py first: '+str(path))
    manifest = json.loads(path.read_text(encoding='utf-8'))
    for asset in manifest['assets']:
        for role, item in asset['maps'].items():
            file = MATERIALS/item['path']
            if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != item['sha256']:
                raise RuntimeError('Material file missing or SHA-256 mismatch: '+str(file))
    return {a['asset']: a for a in manifest['assets']}, manifest

def nodes_for(name):
    material = bpy.data.materials.new('GULLET_PBR_'+name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    out = nodes.new('ShaderNodeOutputMaterial'); out.location = (880, 40)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (600, 40)
    bsdf.inputs['Roughness'].default_value = .7
    bsdf.inputs['Specular IOR Level'].default_value = .32
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return material, nodes, links, bsdf

def image_node(nodes, links, asset, role, coordinate, xy):
    info = asset['maps'][role]
    image = bpy.data.images.load(str(MATERIALS/info['path']), check_existing=True)
    image.colorspace_settings.name = 'sRGB' if role == 'color' else 'Non-Color'
    node = nodes.new('ShaderNodeTexImage'); node.image = image; node.location = xy
    node.label = asset['asset']+' / '+role+' / CC0'
    node.interpolation = 'Linear'; node.projection = 'BOX'; node.projection_blend = .28
    links.new(coordinate, node.inputs['Vector'])
    return node

def mapping(nodes, links, tile):
    tex = nodes.new('ShaderNodeTexCoord'); tex.location = (-1100, 30)
    scale = nodes.new('ShaderNodeVectorMath'); scale.operation = 'SCALE'; scale.location = (-890, 30)
    scale.inputs[3].default_value = 1.0/tile
    links.new(tex.outputs['Object'], scale.inputs[0])
    return scale.outputs['Vector']

def surface(name, asset, tile=2.0, saturation=.75, value=1.0, tint=None,
            tint_weight=.0, roughness=(.62,.95), bump_distance=.025, metallic=0.0):
    mat, nodes, links, p = nodes_for(name)
    mat['source_asset'] = asset['asset']; mat['source_url'] = asset['source']; mat['license'] = 'CC0-1.0'
    coord = mapping(nodes, links, tile)
    colour = image_node(nodes, links, asset, 'color', coord, (-680, 360))
    hs = nodes.new('ShaderNodeHueSaturation'); hs.location = (-390, 390)
    hs.inputs['Saturation'].default_value = saturation; hs.inputs['Value'].default_value = value
    links.new(colour.outputs['Color'], hs.inputs['Color'])
    colour_socket = hs.outputs['Color']
    if tint is not None:
        mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MIX'; mix.location = (-100, 380)
        mix.inputs[0].default_value = tint_weight; mix.inputs[2].default_value = srgb(tint)
        links.new(colour_socket, mix.inputs[1]); colour_socket = mix.outputs['Color']
    links.new(colour_socket, p.inputs['Base Color'])
    rough = image_node(nodes, links, asset, 'roughness', coord, (-680, 40))
    remap = nodes.new('ShaderNodeMapRange'); remap.location = (-370, 50)
    remap.inputs['From Min'].default_value = 0; remap.inputs['From Max'].default_value = 1
    remap.inputs['To Min'].default_value = roughness[0]; remap.inputs['To Max'].default_value = roughness[1]
    links.new(rough.outputs['Color'], remap.inputs['Value']); links.new(remap.outputs['Result'], p.inputs['Roughness'])
    # Height-based box-projected bump avoids rotating tangent normals incorrectly at projection seams.
    height = image_node(nodes, links, asset, 'height' if 'height' in asset['maps'] else 'roughness', coord, (-680,-280))
    bump = nodes.new('ShaderNodeBump'); bump.location = (250, -170)
    bump.inputs['Strength'].default_value = .48; bump.inputs['Distance'].default_value = bump_distance
    links.new(height.outputs['Color'], bump.inputs['Height']); links.new(bump.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Metallic'].default_value = metallic
    mat.diffuse_color = srgb(tint or ('7F7566' if metallic == 0 else '505358'))
    return mat

def painted(name, colour, steel, rough=.65):
    mat, nodes, links, p = nodes_for(name)
    p.inputs['Base Color'].default_value = srgb(colour)
    p.inputs['Roughness'].default_value = rough
    mat.diffuse_color = srgb(colour)
    coord = mapping(nodes, links, 1.6)
    src = image_node(nodes, links, steel, 'roughness', coord, (-650, 60))
    rg = nodes.new('ShaderNodeMapRange'); rg.location = (-230, 60)
    rg.inputs['To Min'].default_value = max(.32, rough-.07)
    rg.inputs['To Max'].default_value = min(.95, rough+.08)
    links.new(src.outputs['Color'], rg.inputs['Value']); links.new(rg.outputs['Result'], p.inputs['Roughness'])
    height = image_node(nodes, links, steel, 'height', coord, (-650, -260))
    bump = nodes.new('ShaderNodeBump'); bump.location = (270, -180)
    bump.inputs['Strength'].default_value = .16; bump.inputs['Distance'].default_value = .002
    links.new(height.outputs['Color'], bump.inputs['Height']); links.new(bump.outputs['Normal'], p.inputs['Normal'])
    mat['source_asset'] = steel['asset']; mat['license'] = 'CC0-1.0'
    mat['usage'] = 'Paint colour authored; CC0 map supplies restrained surface variation.'
    return mat

def water_material():
    mat,nodes,links,p=nodes_for('groundwater')
    p.inputs['Base Color'].default_value=srgb('46483D')
    p.inputs['Roughness'].default_value=.18
    p.inputs['Transmission Weight'].default_value=.28
    p.inputs['IOR'].default_value=1.333
    mat.diffuse_color=srgb('46483D')
    coord=mapping(nodes,links,1.0)
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9
    noise.inputs['Detail'].default_value=1.5;links.new(coord,noise.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.006
    links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
    return mat

def make_materials(assets):
    rock, gravel, concrete, steel = (assets[k] for k in ['rock_face_03','gravel_ground_01','Concrete046','Metal046B'])
    quarry = assets['quarry_wall']
    mats = {
        'rock': surface('weathered_stone',rock,3.0,.55,1.05,'8E7D69',.06,(.72,.98),.15),
        'rock_dark': surface('damp_stone',assets['rock_surface'],2.1,.60,.74,'655A50',.10,(.56,.86),.035),
        'rock_fresh': surface('fresh_stone',quarry,2.0,.28,1.38,'A99980',.24,(.74,.99),.11),
        'ground': surface('dust_and_gravel',gravel,2.4,.62,.86,'93816B',.12,(.82,.99),.035),
        'concrete': surface('cast_concrete',concrete,2.4,0.0,.52,'A39C8F',.25,(.75,.94),.015),
        'concrete_floor': surface('dust_worn_concrete',concrete,2.4,0.0,.25,'807461',.24,(.81,.97),.020),
        'steel': surface('bare_steel',steel,1.2,0.0,1.65,'737A80',.35,(.36,.67),.005,.86),
        'dark_steel': surface('dark_structural_steel',steel,1.5,0.0,.92,'45474A',.30,(.51,.79),.005,.70),
        'paint_teal': painted('equipment_teal','496D70',steel),
        'paint_cream': painted('warm_enamel','C6BCA8',steel,.68),
        'paint_ochre': painted('safety_ochre','CD933A',steel,.64),
        'paint_red': painted('oxide_red','A14930',steel,.69),
        'paint_slate': painted('slate_blue_casing','526773',steel,.71),
        'paint_roof': painted('roof_graphite','535554',steel,.79),
        'paint_cart': painted('cart_ochre','AD7737',steel,.76),
        'ore': surface('ore_inclusions',rock,1.0,.23,.48,'544D3B',.20,(.58,.84),.035,.08),
        'fabric': painted('canvas_duct','ADA089',steel,.91),
        'rubber': painted('rubber','252426',steel,.88),
        'water': water_material(),
    }
    return mats

def apply_materials(scene, mats):
    modified = 0
    structural = ('Canopy_', 'Truss_', 'Leaf_cross_rib', 'Gate_drive_cover', 'Arch_', 'Main_support', 'Support_', 'Rolled_arch_section', 'Return_loop_frame')
    for obj in scene.objects:
        if obj.type != 'MESH' or obj.get('csm_collision_only'):
            continue
        for slot in obj.material_slots:
            old = slot.material
            if old is None:
                continue
            key = old.name.removeprefix('CSM_').split('.')[0]
            use = key
            n = obj.get('csm_id',obj.name)
            if key == 'concrete' and any(k in n for k in ('Apron_concrete_slab', 'Side_apron', 'Facility_transition_floor', 'Walkway_')):
                use = 'concrete_floor'
            if key == 'paint_teal':
                if 'Welded_hopper_shell' in n:
                    use = 'paint_cart'
                elif 'Dispatch_cladding' in n:
                    use = 'paint_cream'
                elif 'Canopy_roof' in n:
                    use = 'paint_roof'
                elif 'Leaf_outer_skin' in n:
                    use = 'paint_slate'
                elif 'Facility_lower_protection' in n:
                    use = 'paint_slate'
                elif any(part in n for part in structural):
                    use = 'dark_steel'
            if use in mats:
                slot.link = 'OBJECT'; slot.material = mats[use]; modified += 1
            elif key.startswith('emissive_'):
                p = next((n for n in old.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if p and key != 'emissive_amber':
                    col = (1.0,.90,.70,1) if key == 'emissive_warm' else (.86,.92,1.0,1)
                    p.inputs['Emission Color'].default_value = col
                    p.inputs['Emission Strength'].default_value = 4.0
    return modified

def add_area(scene, name, pos, target, power, colour, size):
    light = bpy.data.lights.new('PBR_'+name,'AREA'); light.energy=power; light.color=colour; light.shape='DISK'; light.size=size
    obj=bpy.data.objects.new('PBR_'+name,light); scene.collection.objects.link(obj); obj.location=pos
    obj.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    return obj

def repair_lighting(scene):
    background = scene.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value = (.28,.33,.42,1)
    background.inputs['Strength'].default_value = .21
    for obj in scene.objects:
        if obj.type != 'LIGHT':
            continue
        name = obj.name
        if 'Overcast_sky_key' in name:
            obj.data.color = (1.0,.91,.78); obj.data.energy = 4800; obj.data.size = 12
        elif 'Portal_daylight_fill' in name:
            obj.data.color = (.78,.88,1.0); obj.data.energy = 390
        elif 'Bay_warm_bounce' in name:
            obj.data.color = (1.0,.84,.65); obj.data.energy = 430
        elif 'Mine_worklight' in name:
            # Preserve the source warm/cool rhythm but remove greenish casts.
            warm = obj.data.color[0] > obj.data.color[2]
            obj.data.color = (1.0,.78,.52) if warm else (.83,.89,1.0)
            obj.data.energy *= 1.45
        elif 'Bay_ceiling' in name:
            obj.data.color = (1.0,.89,.72); obj.data.energy *= 1.3
    sun=bpy.data.lights.new('PBR_late_day_sun','SUN'); sun.energy=.85; sun.angle=math.radians(14); sun.color=(1,.87,.71)
    ob=bpy.data.objects.new('PBR_late_day_sun',sun); scene.collection.objects.link(ob)
    ob.rotation_euler=(math.radians(25),math.radians(-32),math.radians(-28))
    add_area(scene,'portal_stone_bounce',(-3.8,-3.8,3.0),(0,3.8,2.0),160,(1,.85,.64),3.0)
    scene.view_settings.view_transform='AgX'
    try: scene.view_settings.look='AgX - Medium High Contrast'
    except TypeError: pass
    scene.view_settings.exposure=.35


def geological_relief(scene, assets):
    """Bounded coarse relief sampled from the downloaded CC0 rock height map.

    The authored tunnel silhouette remains the controlling envelope. Contact
    zones, floors and structural arches are protected from displacement.
    """
    record=assets['rock_face_03']['maps']['height']
    image=bpy.data.images.load(str(MATERIALS/record['path']),check_existing=True)
    image.colorspace_settings.name='Non-Color'
    pixels=np.empty(len(image.pixels),dtype=np.float32); image.pixels.foreach_get(pixels)
    w,h=image.size[:]; tex=pixels.reshape(h,w,4)[:,:,0]
    changed=0; largest=0.0
    def sample(a,b):
        x=(a%1.0)*(w-1);y=(b%1.0)*(h-1)
        ix=x.astype(np.int32);iy=y.astype(np.int32);dx=x-ix;dy=y-iy
        return ((1-dx)*(1-dy)*tex[iy,ix]+dx*(1-dy)*tex[iy,np.minimum(ix+1,w-1)]
                +(1-dx)*dy*tex[np.minimum(iy+1,h-1),ix]+dx*dy*tex[np.minimum(iy+1,h-1),np.minimum(ix+1,w-1)])
    for obj in scene.objects:
        if obj.type!='MESH' or 'Continuous_stratified_mine_skin' not in obj.name:continue
        if obj.get('csm_relief_revision'):continue
        mesh=obj.data;count=len(mesh.vertices)
        pos=np.empty(count*3,dtype=np.float32);normal=np.empty_like(pos)
        mesh.vertices.foreach_get('co',pos);mesh.vertices.foreach_get('normal',normal)
        pos=pos.reshape(-1,3);normal=normal.reshape(-1,3)
        weight=np.abs(normal)**4;weight/=np.maximum(weight.sum(axis=1,keepdims=True),1e-6)
        sample_height=(sample(pos[:,1]/3,pos[:,2]/3)*weight[:,0]
                       +sample(pos[:,0]/3,pos[:,2]/3)*weight[:,1]
                       +sample(pos[:,0]/3,pos[:,1]/3)*weight[:,2])
        relief=np.clip((sample_height-.50)*.48,-.16,.16)
        floor=-.025*np.maximum(pos[:,1],0)
        fade=np.clip((pos[:,2]-floor-.22)/.55,0,1)*np.clip((pos[:,1]-.9)/.7,0,1)
        distance=np.min(np.abs(pos[:,1,None]-np.array([3.8,8.2,15.,21.7,25.,30.,36.7])[None,:]),axis=1)
        fade*=np.clip((distance-.3)/.55,0,1)
        relief*=fade
        pos+=normal*relief[:,None]
        mesh.vertices.foreach_set('co',pos.ravel());mesh.update()
        obj['csm_relief_revision']='CC0 rock_face_03; bounded 0.16 m; contact protection'
        changed+=count;largest=max(largest,float(np.max(np.abs(relief))))
    return {'vertices':changed,'maximum_displacement_m':largest,'contact_zones_preserved':True}


def load_builder():
    spec=importlib.util.spec_from_file_location('gullet_material_source',ROOT/'geometry_source.py')
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    return module

def render(scene, output, keys, samples, width):
    cams={o.get('csm_camera_key'):o for o in scene.objects if o.type=='CAMERA' and o.get('csm_camera_key')}
    selected=list(cams) if keys=='all' else [x.strip() for x in keys.split(',') if x.strip()]
    if any(k not in cams for k in selected):
        raise ValueError('Unknown review camera. Available: '+', '.join(cams))
    report=[]; output.mkdir(parents=True,exist_ok=True)
    previous=output/'render_report.json'
    if previous.is_file():
        report=[r for r in json.loads(previous.read_text()) if r['camera'] not in selected]
    for key in selected:
        scene.camera=cams[key]; scene.cycles.samples=samples
        scene.render.resolution_x=width; scene.render.resolution_y=round(width*5/8); scene.render.resolution_percentage=100
        scene.render.filepath=str(output/(key+'.png'))
        t=time.time(); print('BLENDER_RENDER_START',key,flush=True)
        bpy.ops.render.render(write_still=True)
        file=Path(scene.render.filepath)
        report.append({'camera':key,'path':str(file),'seconds':time.time()-t,'bytes':file.stat().st_size,
                       'renderer':'Blender '+bpy.app.version_string+' / Cycles','samples':samples,'resolution':[width,round(width*5/8)],'camera_matrix':[list(row) for row in cams[key].matrix_world],'lens_mm':cams[key].data.lens,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
        (output/'render_report.json').write_text(json.dumps(report,indent=2))
        print('BLENDER_RENDER_COMPLETE',key,report[-1]['seconds'],flush=True)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'output_pbr')
    parser.add_argument('--render',default='')
    parser.add_argument('--samples',type=int,default=64)
    parser.add_argument('--mode',choices=['showcase','intact'],default='showcase')
    parser.add_argument('--quality',choices=['balanced','high'],default='balanced')
    parser.add_argument('--width',type=int,default=1440)
    parser.add_argument('--device',choices=['auto','cpu'],default='auto')
    parser.add_argument('--input',type=Path,help='Explicit existing source .blend for a repair iteration; optional.')
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    args=parser.parse_args(argv)
    if args.samples<1 or args.width<320: raise ValueError('samples >= 1 and width >= 320 are required')
    args.output=args.output.resolve(); args.output.mkdir(parents=True,exist_ok=True)
    assets,manifest=load_manifest()
    base=load_builder()
    if args.input:
        bpy.ops.wm.open_mainfile(filepath=str(args.input.resolve())); scene=bpy.context.scene; report={}
    else:
        data=base.build_scene_data(); report=base.basic_audit(data)
        if report['issues']:raise RuntimeError('Geometry audit failed: '+str(report['issues']))
        scene=base.create_blender_scene(data,SimpleNamespace(mode=args.mode,quality=args.quality,device=args.device))
    if not scene.get('csm_generator'):raise RuntimeError('This is not a builder-owned Gullet scene')
    if scene.get('csm_material_revision'):raise RuntimeError('Do not reapply the repair to an already repaired scene. Rebuild from source instead.')
    mats=make_materials(assets); changed=apply_materials(scene,mats); repair_lighting(scene)
    relief=geological_relief(scene, assets)
    scene.name='Critical Shift - Gullet CC0 material repair'
    scene.render.engine='CYCLES'; base.configure_device(bpy,scene,args.device)
    scene.cycles.samples=args.samples; scene.cycles.max_bounces=6; scene.cycles.diffuse_bounces=4
    scene.cycles.use_denoising=True; scene.cycles.adaptive_threshold=.04
    scene.render.resolution_x=args.width; scene.render.resolution_y=round(args.width*5/8); scene.render.resolution_percentage=100
    scene.render.image_settings.color_mode='RGB'; scene.render.image_settings.color_depth='8'; scene.render.image_settings.compression=25
    scene['csm_material_revision']=REVISION; scene['csm_visual_validation']='Actual Blender review in progress; not final production acceptance.'
    scene['csm_material_manifest']=json.dumps(manifest,separators=(',',':'))
    # Pack only scene-used images. Unused source maps remain in the CC0 material folder.
    images={node.image for mat in mats.values() for node in mat.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
    for image in images:image.pack()
    for text in bpy.data.texts:
        if text.name.startswith('GULLET_READ_ME'):
            text.clear(); text.write('GULLET / CC0 MATERIAL REPAIR\n\nBlender '+bpy.app.version_string+' / Cycles.\n'
            'Build: pbr/build_textured_mine.py\nDownloaded material sources and hashes are stored in scene metadata.\n'
            'Run register_controls.py beside build_mine.py to restore the Gullet panel after opening this file.\n'
            'Existing sector, rubble and gate controls are retained.\nUnity gameplay, colliders and performance still require integration testing.\n')
    dest=args.output/'CriticalShift_Gullet_PBR.blend'
    if dest.exists():dest=args.output/('CriticalShift_Gullet_PBR_'+time.strftime('%Y%m%d_%H%M%S')+'.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
    report.update({'revision':REVISION,'blender_version':bpy.app.version_string,'blender_build_executed':True,
                   'geological_relief':relief,'material_slots_updated':changed,'material_packs':list(assets),'blend_file':str(dest),
                   'rendered_cameras':[],'visual_acceptance':'Pending pixel review; not a production-final claim.'})
    (args.output/'build_report.json').write_text(json.dumps(report,indent=2))
    if args.render:report['rendered_cameras']=render(scene,args.output/'renders',args.render,args.samples,args.width)
    (args.output/'build_report.json').write_text(json.dumps(report,indent=2))
    print('GULLET_MATERIAL_REPAIR_COMPLETE',str(dest),flush=True)

if __name__=='__main__':main()
