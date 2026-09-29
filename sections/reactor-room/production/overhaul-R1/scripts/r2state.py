import bpy
def state_mat(name,strength,st,base_dark=False):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    def drv(path,idx,expr):
        fc=nt.driver_add(path,idx) if idx is not None else nt.driver_add(path)
        d=fc.driver; d.type='SCRIPTED'; v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=st; v.targets[0].data_path='["stability"]'; d.expression=expr
    for i,e in enumerate(("min(1,2*(1-s)+0.24)","0.03+0.92*s","0.20*s")):
        drv('nodes["Principled BSDF"].inputs["Emission Color"].default_value',i,e); drv('nodes["Principled BSDF"].inputs["Base Color"].default_value',i,e)
    drv('nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,f"{strength}*(1+0.35*(1-s))*(1+0.10*sin(frame*(0.15+0.5*(1-s))))")
    return m
def emit_mat(name,rgb,strength):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value=(*[c*0.3 for c in rgb],1); b.inputs['Emission Color'].default_value=(*rgb,1); b.inputs['Emission Strength'].default_value=strength; return m
