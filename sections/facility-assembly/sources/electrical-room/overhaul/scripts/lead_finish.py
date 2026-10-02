"""Refit stored test leads and trolley cables without moving their fixtures."""
import math
import bpy
from mathutils import Vector, Matrix


def smooth_path(points, steps=10):
    """Endpoint-preserving Catmull-Rom sampling for relaxed cable bends."""
    p = [Vector(v) for v in points]
    out = []
    for i in range(len(p)-1):
        a, b, c, d = p[max(0,i-1)], p[i], p[i+1], p[min(len(p)-1,i+2)]
        for j in range(steps):
            t = j/steps
            out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
    out.append(tuple(p[-1]))
    return out


def apply(k, m):
    scene = bpy.context.scene
    assert not scene.get('electrical_lead_finish_revision')
    changed = []
    before_names = {o.name for o in scene.objects}
    support_checks = []
    endpoint_checks = []
    def replace(name, factory):
        old = bpy.data.objects[k.PREFIX+name]
        old_mesh = old.data
        temp = factory()
        assert old.matrix_world == temp.matrix_world
        old.data = temp.data
        bpy.data.objects.remove(temp, do_unlink=True)
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        changed.append(old.name)
        return old
    def added(o):
        return o

    k.COLL = bpy.data.collections[k.PREFIX+'Service history and safety']
    k.ASSEMBLY = bpy.data.objects[k.PREFIX+'Rear test lead storage']
    for index, x in enumerate([3.64,4.30]):
        suffix = '' if index == 0 else '.001'
        color = m['redrubber'] if index == 0 else m['rubber']
        # Four visibly separate, oval windings. Their tops rest on the same
        # horizontal saddle; their widths, bottom droop and lay vary by turn.
        path = []
        for j in range(193):
            turns = j/48
            angle = turns*math.tau
            width = .181+.018*math.sin(turns*1.93+index*.8)
            height = .448+.035*math.sin(turns*1.37+index*1.1)
            drift = (.013 if index == 0 else -.019)*(1-math.cos(angle))/2
            path.append((x+width*math.sin(angle)*(1+.055*math.sin(2*angle))+drift,
                         16.065+turns*.026+.003*math.sin(angle),
                         1.551-height*(1-math.cos(angle))/2))
        replace('Coiled test lead'+suffix,
                lambda: k.tube('Refit temporary coil',path,.0065,color))
        # A returned saddle catches all four top windings. Its horizontal run
        # is explicit so support can be measured rather than inferred visually.
        hook_path = [(x,16.335,1.55),(x,16.29,1.55),(x,16.265,1.534),
                     (x,16.245,1.532),(x,16.20,1.532),(x,16.15,1.532),
                     (x,16.10,1.532),(x,16.055,1.532),(x,16.025,1.532),
                     (x,16.005,1.546),(x,16.005,1.59)]
        hook = replace('Lead reel hook'+suffix,
                       lambda: k.tube('Refit temporary saddle',hook_path,.0125,m['zinc']))
        bpy.context.view_layer.update()
        for turn in range(4):
            point = Vector((x,16.065+turn*.026,1.65))
            hit, location, normal, face = hook.ray_cast(point,Vector((0,0,-1)))
            gap = 1.551-.0065-location.z if hit else None
            assert hit and abs(gap)<.0015, (index,turn,gap)
            support_checks.append({'coil':index,'winding':turn,'support_gap_m':gap})
        # Closing keeper and formed backing cleat secure the coil bundle.
        added(k.box('Lead saddle returned keeper',(x,16.015,1.579),(.052,.026,.018),m['slate'],.004))
        added(k.bolt('Lead saddle keeper fixing',(x,16.002,1.579),(0,-1,0),m['zinc'],.008))
        added(k.box('Lead saddle mounting cleat',(x,16.323,1.55),(.072,.018,.10),m['zinc'],.003))
        for dx in [-.021,.021]:
            added(k.bolt('Lead saddle cleat fixing',(x+dx,16.314,1.55),(0,-1,0),m['steel'],.006))
        tail = smooth_path([path[-1],(x+.045,16.035,1.49),(x+.083,16.013,1.29),
                            (x+.043,16.055,1.09),(x+.06,16.10,.925)],14)
        replace('Test lead hanging tail'+suffix,
                lambda: k.tube('Refit temporary hanging tail',tail,.0065,color))
        grip = [(0,0),(.010,0),(.014,.006),(.023,.012),(.023,.025),
                (.016,.032),(.016,.078),(.010,.10),(0,.10)]
        replace('Lead terminal insulated grip'+suffix,
                lambda: k.lathe('Refit temporary probe boot',(x+.06,16.10,.80),grip,m['ochre'],32))
        added(k.lathe('Stored probe tapered strain relief',(x+.06,16.10,.90),
                      [(0,0),(.010,0),(.008,.025),(0,.025)],color,24))
        for z in [.842,.854,.866,.878]:
            added(k.lathe('Stored probe grip rib',(x+.06,16.10,z),
                          [(.015,0),(.017,0),(.017,.004),(.015,.004),(.015,0)],m['ochre'],24))
        # The second end is a shrouded plug held in an open spring clip.
        plug_x, plug_y = x-.075, 16.18
        added(k.tube('Stored lead second-end bend',smooth_path([
            path[0],(x-.023,16.025,1.575),(plug_x,16.08,1.585),
            (plug_x,plug_y,1.565)],12),.0065,color))
        added(k.lathe('Stored lead shrouded plug',(plug_x,plug_y,1.565),
                      [(0,0),(.009,0),(.015,.014),(.015,.045),(.020,.049),
                       (.020,.054),(.013,.059),(.013,.073),(.007,.073),
                       (.007,.060),(0,.060)],color,32))
        added(k.cyl('Stored lead plug contact',(plug_x,plug_y,1.625),
                    (plug_x,plug_y,1.635),.004,m['zinc']))
        added(k.tube('Lead plug clip returned stem',[
            (plug_x,16.33,1.60),(plug_x,16.24,1.60),(plug_x,plug_y+.019,1.60)],.005,m['zinc']))
        clip = [(plug_x+.018*math.cos(math.radians(30)+j*math.radians(300)/32),
                 plug_y+.018*math.sin(math.radians(30)+j*math.radians(300)/32),1.60) for j in range(33)]
        added(k.tube('Lead plug open spring clip',clip,.003,m['zinc']))

    # Soft, seated trolley leads retain their exact jack and probe endpoints.
    for j,(x,base_y,color) in enumerate([(-4.25,1.87,m['redrubber']),(-4.30,1.91,m['rubber'])]):
        suffix = '' if j == 0 else '.001'
        old = bpy.data.objects[k.PREFIX+'Resting test lead'+suffix]
        original_endpoints=[sum((v.co for v in old.data.vertices[:12]),Vector())/12,
                            sum((v.co for v in old.data.vertices[-12:]),Vector())/12]
        k.ASSEMBLY = bpy.data.objects[old['cs_assembly']]
        jack_y = [1.64,1.675][j]
        points = [(-4.45,jack_y,.980),(-4.45,jack_y,.994),
                  (-4.426,jack_y,1.006),(-4.400,jack_y,.997),
                  (-4.375,jack_y,.960),(-4.340,jack_y-.025,.910),
                  (-4.335,1.58+j*.018,.884),(-4.245+j*.020,1.585+j*.025,.877),
                  (-4.205+j*.018,1.69+j*.02,.877),(-4.232+j*.013,1.79+j*.026,.877),
                  (x,base_y,.887)]
        cable=replace('Resting test lead'+suffix,
                      lambda: k.tube('Refit temporary trolley cable',smooth_path(points,14),.003,color))
        new_endpoints=[sum((v.co for v in cable.data.vertices[:12]),Vector())/12,
                       sum((v.co for v in cable.data.vertices[-12:]),Vector())/12]
        errors=[(a-b).length for a,b in zip(original_endpoints,new_endpoints)]
        assert max(errors)<1e-6,errors
        endpoint_checks.append({'cable':cable.name,'endpoint_errors_m':errors})
    scene['electrical_lead_finish_revision'] = 1
    new_names = sorted(o.name for o in scene.objects if o.name not in before_names)
    return {'changed_existing_mesh_objects':changed,'added_objects':new_names,
            'measured_winding_supports':support_checks,
            'measured_trolley_endpoints':endpoint_checks,
            'trolley_jack_and_probe_endpoints_preserved':True}
