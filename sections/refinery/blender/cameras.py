"""Permanent eye-height review cameras; no elevated acceptance views."""
import bpy, math
from mathutils import Vector
import geometry as g
from config import CAMERAS

def area(name,pos,target,power,colour,size,size_y=None):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=colour;d.shape='RECTANGLE';d.size=size;d.size_y=size_y or size
    o=bpy.data.objects.new(name,d);g.collection('REFINERY_LIGHTING').objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def build():
    scene=bpy.context.scene
    for name,(pos,target,lens) in CAMERAS.items():
        d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.05;d.clip_end=150
        o=bpy.data.objects.new(name,d);g.collection('REFINERY_CAMERAS').objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['eye_height_m']=1.68
    scene.camera=bpy.data.objects['CAM_ENTRY']
    with g.use('REFINERY_LIGHTING'):
        for i,(x,y,power,col) in enumerate([(-4.85,-2.5,320,(1,.81,.60)),(-4.4,3.25,500,(1,.84,.68)),(0,3.1,480,(.80,.89,1)),(4.8,2.3,420,(1,.88,.72)),(4.8,-2.0,360,(.78,.90,1)),(-1.5,-3.3,260,(1,.89,.73))]):
            housing=g.box('Pendant_'+str(i),(x,y,4.49),(1.36,.34,.13),'darksteel',.018)
            for sx in [-1,1]:
                px=x+sx*.5
                anchor=g.box('Pendant_ceiling_anchor',(px,y,4.79),(.11,.11,.02),'steel',.004)
                g.support(anchor,'Ceiling','WORLD_+Z',[(px,y,4.8)],'CEILING')
                g.rod('Pendant_drop',(px,y,4.77),(px,y,4.55),.008,'steel')
            g.box('Pendant_diffuser',(x,y,4.417),(1.23,.25,.017),'lamp',.012)
            area('Practical_'+str(i),(x,y,4.39),(x,y,0),power,col,1.2,.25)
        # Wide portal light is the adjoining department, not a global wash.
        area('Reactor_threshold',(7.6,-3.6,2.0),(3.5,-3.5,1.0),180,(.54,.75,1),2,2.2)
        area('Mine_threshold',(-7.8,-3.65,2.2),(-4.2,-3.5,1.1),100,(1,.65,.34),2,2)
        area('Entry_soft_bounce',(-1.8,-5.8,2.0),(-.5,2.5,1.5),45,(.87,.91,1),2,2)
    world=bpy.data.worlds.new('Refinery ambient');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.19,.23,.26,1);world.node_tree.nodes['Background'].inputs[1].default_value=.09;scene.world=world
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.seed=709
    scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=2;scene.cycles.transmission_bounces=3
    scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.55
    scene.render.film_transparent=False
