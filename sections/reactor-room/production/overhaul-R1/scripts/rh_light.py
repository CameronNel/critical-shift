"""Hall lighting rebalance (reviewer: "pool glow bathes everything at stability 1.0, walls read olive").   usage: python rh_light.py -- <in.blend> <out.blend>
The state-driven green lights (Reactor state key 1.8 kW, LP reactor beam 5.6 kW, fill low, pool surface/deep pool) are scaled down so the glow is an accent on the pool, rods and surround rather than the hall's
key light, and the roof wash spots become neutral warm white and a little stronger so walls read as concrete / Audi grey with the glow as a tint.  Scaling is applied inside the existing driver expressions
(the stability colour, the flicker and the seconds-based timing are untouched); undriven lights are scaled directly.  Run before rh_final.py."""
import bpy,sys,re
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
bpy.ops.wm.open_mainfile(filepath=SRC)
SCALE={"Reactor state key":0.38,"LP reactor beam":0.65,"LP reactor fill low":0.5,"Pool surface scattered cyan":0.6,"Cyan from deep pool":0.8}
WASH=re.compile(r"^LP (wash|roof shaft|rim)")
def scale(o,k):
    l=o.data; ad=l.animation_data; done=False
    if ad:
        for d in ad.drivers:
            if d.data_path=='energy': d.driver.expression="%.3f*(%s)"%(k,d.driver.expression); done=True
    if not done: l.energy*=k
n=0
for o in bpy.data.objects:
    if o.type!='LIGHT': continue
    if o.name in SCALE: scale(o,SCALE[o.name]); n+=1
    elif WASH.match(o.name):
        o.data.color=(0.96,0.90,0.80); scale(o,1.5 if o.name.startswith("LP wash") else 1.2); n+=1
w=bpy.context.scene.world
if w and w.node_tree:
    for nd in w.node_tree.nodes:
        if nd.type=='BACKGROUND': nd.inputs['Strength'].default_value=0.16; nd.inputs['Color'].default_value=(0.075,0.074,0.072,1.0)
print("rh_light: rebalanced",n,"lights")
bpy.ops.wm.save_as_mainfile(filepath=DST)
