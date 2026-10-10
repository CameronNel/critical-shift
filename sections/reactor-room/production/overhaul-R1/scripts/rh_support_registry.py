"""Candidate-owned support anchors, written by builders into the saved scene."""
import bpy,json,math

KEY='rh_support_registry'
def reset(owner):
    rows=json.loads(bpy.context.scene.get(KEY,'[]'))
    bpy.context.scene[KEY]=json.dumps([r for r in rows if r['owner']!=owner])

def register(owner,name,subject,target,anchors,direction=(0,0,-1),kind='floor',**limits):
    rows=json.loads(bpy.context.scene.get(KEY,'[]'))
    ident=owner+':'+name+':'+str(len([r for r in rows if r['owner']==owner]))
    rows.append(dict(owner=owner,id=ident,name=name,subject=subject,target=target,
        anchors=[list(p) for p in anchors],direction=list(direction),kind=kind,
        gap=limits.get('gap',.005),penetration=limits.get('penetration',.002),angle=limits.get('angle',12)))
    bpy.context.scene[KEY]=json.dumps(rows)

def world(origin,yaw,points):
    c,s=math.cos(yaw),math.sin(yaw)
    return [(origin[0]+c*x-s*y,origin[1]+s*x+c*y,z) for x,y,z in points]
