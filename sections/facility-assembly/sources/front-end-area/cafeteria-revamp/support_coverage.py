"""Register inherited cafeteria prop contacts against actual evaluated geometry.

Architectural meshes are support targets. Independently placed props must have a
registration, or belong to a registered assembly through their parent hierarchy.
"""
import bpy
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

KINDS={'floor','rug','table','wall','hanging','overhead','soft','stack','assembly','door'}
UP=Vector((0,0,1));DOWN=Vector((0,0,-1))
WALL=[Vector((1,0,0)),Vector((-1,0,0)),Vector((0,1,0)),Vector((0,-1,0))]

def needs_registration(ob):
    if ob.type not in {'MESH','CURVE','FONT','EMPTY'} or ob.hide_render:return False
    return ob.get('support') in KINDS or ob.name.startswith(('caf_pendant_','caf_light_strip_','game_wall_shelf_','zone_'))

def covered(ob,names):
    while ob:
        if ob.name in names:return True
        ob=ob.parent
    return False

def missing_registrations(caf,registrations):
    names={r['object'] for r in registrations}
    return sorted(o.name for o in caf.all_objects if needs_registration(o) and not covered(o,names))

def complete_contacts(caf,registrations,supported):
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cache={};repairs=[]
    def world_vertices(ob):
        e=ob.evaluated_get(dg);me=e.to_mesh();points=[ob.matrix_world@v.co for v in me.vertices];e.to_mesh_clear();return points
    def tree(ob):
        if ob.name not in cache:
            e=ob.evaluated_get(dg);me=e.to_mesh()
            cache[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
            e.to_mesh_clear()
        return cache[ob.name]
    architecture=[o for o in caf.all_objects if o.type=='MESH' and o.get('support') is None and o.name.startswith(('caf_S_','caf_N_','caf_E_','caf_W_','caf_roof','kitchen_front','hatch_frame','kdoor_'))]
    architecture += [o for o in bpy.data.collections['HALL'].all_objects if o.type=='MESH' and o.name.startswith('cafhall_mid_')]
    walls=architecture+[bpy.data.objects['directory_totem']]
    roofs=[o for o in architecture if o.name.startswith('caf_roof')]
    floors=[bpy.data.objects['caf_floor'],bpy.data.objects['lounge_rug'],bpy.data.objects['game_rug']]
    tables=[o for o in caf.all_objects if o.name.startswith('caf_table_') and o.type=='MESH']
    tables += [bpy.data.objects[n] for n in ('lounge_coffee_table','lounge_side_table_0','serving_counter','kitchen_block')]
    def extremes(points,d):
        edge=max(p.dot(d) for p in points);ps=[p for p in points if edge-p.dot(d)<.00005]
        centre=sum(ps,Vector())/len(ps)
        axes=[i for i in range(3) if abs(d[i])<.5]
        selected=[centre]
        for axis in axes:
            for sign in (-1,1):selected.append(max(ps,key=lambda p:sign*p[axis]))
        return selected
    def hit(point,d,target,search=False):
        reach=1.0 if search else .1
        p,n,idx,distance=tree(target).ray_cast(point-d*reach,d,2*reach+.05)
        if p is None:return None
        angle=math.degrees(math.acos(max(-1,min(1,n.dot(-d)))))
        if angle>12:return None
        return (p-point).dot(d)
    def find(ob,directions,targets):
        points=world_vertices(ob);choices=[]
        for d in directions:
            for anchor in extremes(points,d):
                for target in targets:
                    if target==ob:continue
                    gap=hit(anchor,d,target,search=d.z>.5)
                    if gap is not None:choices.append((abs(gap),gap,target,d,anchor))
        if not choices:raise RuntimeError('No plausible support target for '+ob.name)
        return min(choices,key=lambda row:row[0])
    # Zone placards have separate original rods. Retain their lower endpoints,
    # extend their roof ends to the actual deck, and register both attachments.
    for sign in [o for o in caf.all_objects if o.name.startswith('zone_') and '_rod' not in o.name]:
        rods=[o for o in caf.all_objects if o.name.startswith(sign.name+'_rod')]
        for rod in rods:
            rod['support']='overhead';pts=world_vertices(rod);top=max(p.z for p in pts)
            row=find(rod,[UP],roofs);gap=row[1]
            if abs(gap)>.002:
                inv=rod.matrix_world.inverted()
                for v in rod.data.vertices:
                    p=rod.matrix_world@v.co
                    if p.z>top-.0001:v.co=inv@(p+UP*gap)
                repairs.append({'object':rod.name,'roof_end_extension_m':gap})
                bpy.context.view_layer.update();cache.pop(rod.name,None)
            row=find(rod,[UP],roofs);supported(rod,row[2].name,[tuple(rod.matrix_world.inverted()@row[4])],UP)
            bottom=min(p.z for p in pts);bottom_points=[p for p in pts if abs(p.z-bottom)<.0001]
            anchor=sum(bottom_points,Vector())/len(bottom_points)
            supported(sign,rod.name,[tuple(sign.matrix_world.inverted()@anchor)],UP)
    for ob in list(caf.all_objects):
        if ob.name.startswith(('caf_pendant_','caf_light_strip_')):ob['support']='overhead'
        if ob.name.startswith('game_wall_shelf_'):ob['support']='wall'
    for ob in sorted(caf.all_objects,key=lambda o:(o.get('support') not in {'floor','rug'},o.name)):
        if not needs_registration(ob) or covered(ob,{r['object'] for r in registrations}):continue
        kind=ob.get('support')
        if kind in {'floor','rug'}:directions,targets=[DOWN],floors
        elif kind in {'table','stack','soft'}:directions,targets=[DOWN],tables
        elif kind=='overhead' or ob.name.startswith('HVAC_'):directions,targets=[UP],roofs;ob['support']='overhead'
        elif kind in {'wall','door'}:directions,targets=WALL,walls
        elif ob.name.startswith('Hot_food_'):directions,targets=[DOWN],[bpy.data.objects['serving_counter']];ob['support']='table'
        else:raise RuntimeError('Unclassified independent supported prop '+ob.name)
        row=find(ob,directions,targets);gap,target,d=row[1:4]
        if not -.00201<=gap<=.00501:
            if kind=='overhead' and ob.name.startswith(('caf_pendant_','caf_light_strip_')):
                pts=world_vertices(ob);top=max(p.z for p in pts);inv=ob.matrix_world.inverted()
                for v in ob.data.vertices:
                    p=ob.matrix_world@v.co
                    if p.z>top-.0001:v.co=inv@(p+d*gap)
                repairs.append({'object':ob.name,'roof_end_extension_m':gap})
            else:
                delta=d*(gap-.001);ob.location+=delta
                repairs.append({'object':ob.name,'contact_translation_m':list(delta),'target':target.name})
            bpy.context.view_layer.update();cache.pop(ob.name,None);row=find(ob,directions,targets);target,d=row[2:4]
        points=extremes(world_vertices(ob),d);anchors=[]
        for p in points:
            gap=hit(p,d,target)
            if gap is not None and -.00201<=gap<=.00501:
                local=tuple(ob.matrix_world.inverted()@p)
                if local not in anchors:anchors.append(local)
        if not anchors:raise RuntimeError('Contact repair failed for '+ob.name)
        supported(ob,target.name,anchors,d)
    missing=missing_registrations(caf,registrations)
    if missing:raise RuntimeError('Missing cafeteria support registrations: '+', '.join(missing))
    return repairs
