"""W22: differentiated mineral, enamel, exposed-metal and soft surface response."""
for key,rough,metallic,grain,distance,strength in [
    ('wall',.96,0,65,.0035,.32),
    ('floor',.94,0,95,.002,.25),
    ('pale',.46,.12,260,.00025,.12),
    ('paint',.50,.12,240,.00030,.12),
    ('metal',.30,.88,320,.00018,.12),
    ('rubber',.96,0,180,.0006,.20),
    ('paper',.98,0,150,.00015,.10)]:
    mat=M[key];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    for node in nt.nodes:
        if node.type=='MAP_RANGE':
            node.inputs['To Min'].default_value=max(.1,rough-.035)
            node.inputs['To Max'].default_value=min(.99,rough+.025)
        if node.type=='BUMP':
            node.inputs['Distance'].default_value=distance
            node.inputs['Strength'].default_value=strength
            for edge in node.inputs['Height'].links:
                if edge.from_node.type=='TEX_NOISE':edge.from_node.inputs['Scale'].default_value=grain
    bs.inputs['Specular IOR Level'].default_value=.25 if key in ['wall','floor','rubber','paper'] else .5
