"""Terminate secondary roof members on seated, bolted primary-web connections."""
import bpy,bmesh,json,math,hashlib
from mathutils import Matrix
import crk
import rh_support_registry as SUPPORT
STEEL='RH walls girders STEEL';GALV='RH walls girders GALV';ORANGE='RH walls girders ORANGE'
PLATES='RH roof crossings end plates STEEL'
WASHERS='RH roof crossings washers GALV';HEADS='RH roof crossings bolt heads GALV'
KEY='rh_roof_crossing_fit_geometry'
PRIMARY=(-7.5,-3.6,3.6,7.5)

def components(obj):
    me=obj.data;parents=list(range(len(me.vertices)))
    def find(v):
        while parents[v]!=v:parents[v]=parents[parents[v]];v=parents[v]
        return v
    for edge in me.edges:
        a,b=map(find,edge.vertices);parents[b]=a
    groups={}
    for vertex in me.vertices:groups.setdefault(find(vertex.index),[]).append(vertex.index)
    rows=[]
    for indices in groups.values():
        points=[me.vertices[i].co for i in indices]
        low=[min(p[k] for p in points) for k in range(3)];high=[max(p[k] for p in points) for k in range(3)]
        rows.append(dict(indices=indices,low=low,high=high,center=[(a+b)/2 for a,b in zip(low,high)],extent=[b-a for a,b in zip(low,high)]))
    return rows

def signature(objects):
    result={}
    for name in (STEEL,GALV,ORANGE,PLATES,WASHERS,HEADS):
        o=objects[name];me=o.data
        record={'vertices':[list(v.co) for v in me.vertices], 'faces':[(list(p.vertices),p.material_index,p.use_smooth) for p in me.polygons], 'edges':[(list(e.vertices),e.use_edge_sharp) for e in me.edges]}
        result[name]=hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()
    return result

def splice(obj,removed,addition):
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(removed)],context='VERTS')
    if addition is not None:bm.from_mesh(addition.data)
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    if addition is not None:
        data=addition.data;bpy.data.objects.remove(addition,do_unlink=True)
        if not data.users:bpy.data.meshes.remove(data)

def washer(kit,key,face,side,y,z):
    bm=kit.get(key);rings=[];n=32
    for distance,radius in ((0,.022),(0,.009),(.003,.022),(.003,.009)):
        rings.append([bm.verts.new((face+side*distance,y+radius*math.cos(j*2*math.pi/n),z+radius*math.sin(j*2*math.pi/n))) for j in range(n)])
    for j in range(n):
        k=(j+1)%n
        faces=((rings[0][k],rings[0][j],rings[1][j],rings[1][k]),(rings[2][j],rings[2][k],rings[3][k],rings[3][j]),(rings[0][j],rings[0][k],rings[2][k],rings[2][j]),(rings[3][j],rings[3][k],rings[1][k],rings[1][j]))
        for index,vertices in enumerate(faces):
            f=bm.faces.new(vertices if side>0 else tuple(reversed(vertices)));f.smooth=index>=2

def hex_head(kit,key,face,side,y,z):
    bm=kit.get(key);rings=[]
    for distance,radius in ((.003,.0135),(.0135,.0135),(.015,.012)):
        rings.append([bm.verts.new((face+side*distance,y+radius*math.cos(math.pi/6+j*math.pi/3),z+radius*math.sin(math.pi/6+j*math.pi/3))) for j in range(6)])
    faces=[tuple(reversed(rings[0])),tuple(rings[-1])]
    for lower,upper in zip(rings,rings[1:]):
        faces.extend((lower[j],lower[(j+1)%6],upper[(j+1)%6],upper[j]) for j in range(6))
    for vertices in faces:bm.faces.new(vertices if side>0 else tuple(reversed(vertices)))

def apply(scene,objects):
    if KEY in scene:
        previous=json.loads(scene[KEY]);assert previous['mesh_signatures']==signature(objects),'Roof crossing geometry changed after correction'
        return previous['result']
    for name in (STEEL,GALV,ORANGE):
        assert objects[name].type=='MESH' and objects[name].matrix_world==Matrix.Identity(4)
        assert len(objects[name].data.materials)==1
    all_steel=components(objects[STEEL]);secondary=[r for r in all_steel if abs(abs(r['center'][1])-6)<.002]
    assert len(secondary)==46 and all(abs(r['center'][1]-6)<.002 or abs(r['center'][1]+6)<.002 for r in secondary)
    for row in secondary:
        dx,dy,dz=row['extent']
        assert (dx>20 and abs(dy-.035)<.003 and abs(dz-.56)<.003) or (dx>20 and abs(dy-.42)<.003 and abs(dz-.07)<.003) or (abs(dx-.03)<.003 and abs(dy-.30)<.003 and abs(dz-.56)<.003) or (abs(dx-.02)<.003 and abs(dy-.46)<.003 and abs(dz-.74)<.003),row
    coat=objects[STEEL].data.materials[0];galvanized=objects[GALV].data.materials[0];orange=objects[ORANGE].data.materials[0]
    for name in (PLATES,WASHERS,HEADS):assert name not in objects
    replacement=crk.Kit();connections=crk.Kit();support_rows=[];spans=[]
    for y in (-6.,6.):
        row_parts=[r for r in secondary if abs(r['center'][1]-y)<.002]
        original_web=next(r for r in row_parts if r['extent'][0]>20 and abs(r['extent'][1]-.035)<.003)
        xmin,xmax=original_web['low'][0],original_web['high'][0]
        # Existing perimeter end plates lie 10..30 mm inside the original ends.
        endpoints=[xmin+.03]
        for x in PRIMARY:endpoints.extend((x-.0355,x+.0355))
        endpoints.append(xmax-.03)
        for a,b in zip(endpoints[::2],endpoints[1::2]):
            length=b-a;assert length>3
            spans.append({'y':y,'start_x':a,'end_x':b,'bottom_z':16.75,'top_z':17.19})
            replacement.bx(('secondary','STEEL'),a,b,y-.21,y+.21,16.75,16.82,.008)
            replacement.bx(('secondary','STEEL'),a,b,y-.21,y+.21,17.12,17.19,.008)
            replacement.bx(('secondary','STEEL'),a,b,y-.0175,y+.0175,16.82,17.12,0)
            count=max(1,int(length/1.2))
            for i in range(count+1):
                station=a+.35+(length-.70)*i/count
                # Two seated half-stiffeners; neither passes through the web.
                for lo,hi in ((y-.15,y-.0175),(y+.0175,y+.15)):
                    replacement.bx(('secondary','STEEL'),station-.015,station+.015,lo,hi,16.82,17.12,0)
            lo=max(a,xmin+.4);hi=min(b,xmax-.4)
            if hi>lo:replacement.bx(('stripe','ORANGE'),lo,hi,y-.2125,y+.2125,16.82,16.825,0)
        # Outer cap height follows the shallower secondary profile. Its bottom
        # and the existing bearing pads/braces remain at their original levels.
        for x in (xmin+.02,xmax-.02):replacement.bx(('secondary','STEEL'),x-.01,x+.01,y-.23,y+.23,16.73,17.21,.004)
        for x in PRIMARY:
            for side in (-1,1):
                inner=x+side*.0175;outer=x+side*.0355
                connections.bx(('end plates','STEEL'),min(inner,outer),max(inner,outer),y-.21,y+.21,16.73,17.21,.002)
                # Bolt pattern clears the secondary web and both flange bands.
                for offset in (-.14,.14):
                    for z in (16.85,17.09):
                        washer(connections,('washers','GALV'),outer,side,y+offset,z)
                        hex_head(connections,('bolt heads','GALV'),outer,side,y+offset,z)
                        support_rows.append(('washer',outer,side,y+offset,z))
                support_rows.append(('plate',inner,side,y,0))
                support_rows.append(('beam',outer,side,y,0))
    collection=objects[STEEL].users_collection[0]
    new=replacement.build(collection,'RH crossing replacement',{'STEEL':coat,'ORANGE':orange})
    by_name={o.name:o for o in new}
    splice(objects[STEEL],{i for r in secondary for i in r['indices']},by_name['RH crossing replacement secondary STEEL'])
    old_stripes=[r for r in components(objects[ORANGE]) if abs(abs(r['center'][1])-6)<.002]
    assert len(old_stripes)==2
    splice(objects[ORANGE],{i for r in old_stripes for i in r['indices']},by_name['RH crossing replacement stripe ORANGE'])
    # Preserve all primary fittings and all six bearing pads; lower only eight
    # upper perimeter bolt heads to match the shorter transverse end caps.
    upper=[]
    for row in components(objects[GALV]):
        cx,cy,cz=row['center'];dx,dy,dz=row['extent']
        if abs(abs(cx)-10.675)<.004 and min(abs(cy-y-o) for y in (-6,6) for o in (-.14,.14))<.003 and abs(cz-17.35)<.003:
            assert max(dx,dy,dz)<.04;upper.append(row)
    assert len(upper)==8
    for row in upper:
        for i in row['indices']:objects[GALV].data.vertices[i].co.z-=.26
    objects[GALV].data.update()
    created=connections.build(collection,'RH roof crossings',{'STEEL':coat,'GALV':galvanized})
    assert {o.name for o in created}=={PLATES,WASHERS,HEADS}
    SUPPORT.reset('roof crossing connections')
    for index,(kind,x,side,y,z) in enumerate(support_rows):
        direction=(-side,0,0)
        if kind=='plate':
            anchors=[(x,y+dy,height) for dy in (-.16,.16) for height in (16.89,17.05)]
            SUPPORT.register('roof crossing connections','end plate '+str(index),PLATES,STEEL,anchors,direction,'suspension',gap=.0002,penetration=.0002)
        elif kind=='beam':
            anchors=[(x,y+dy,height) for dy in (-.10,.10) for height in (16.77,17.16)]
            SUPPORT.register('roof crossing connections','secondary end '+str(index),STEEL,PLATES,anchors,direction,'suspension',gap=.0002,penetration=.0002)
        else:
            anchors=[(x,y+.016*math.cos(a),z+.016*math.sin(a)) for a in (0,math.pi/2,math.pi,3*math.pi/2)]
            SUPPORT.register('roof crossing connections','washer '+str(index),WASHERS,PLATES,anchors,direction,'suspension',gap=.0002,penetration=.0002)
            front=x+side*.003
            anchors=[(front,y+.0105*math.cos(a),z+.0105*math.sin(a)) for a in (0,math.pi/2,math.pi,3*math.pi/2)]
            SUPPORT.register('roof crossing connections','bolt head '+str(index),HEADS,WASHERS,anchors,direction,'suspension',gap=.0002,penetration=.0002)
    result={'primary_members':'Four original continuous primary I-girders unchanged','transverse_segments':spans,'interior_end_plates':16,'external_hex_heads':64,'annular_washers':64,'upper_perimeter_heads_lowered':8,'primary_flange_clearance_m':{'lower':.08,'upper':.04},'scope':'Secondary members terminate on plates seated on actual primary web faces. Primary members, perimeter bearing pads/posts/braces, roof utility geometry, lights, exposure and animation unchanged.'}
    scene[KEY]=json.dumps({'mesh_signatures':signature(objects),'result':result},sort_keys=True)
    return result
