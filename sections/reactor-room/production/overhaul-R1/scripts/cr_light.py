"""Control-room lighting: warm tungsten key zones (desk row, rack, work table), cool window spill, coloured accents (CRTs, rack LEDs, TV in cr_tv).
Energies are Cycles watts for the authored scene; the engine-side lights are derived from these positions/colours/energies."""
import math
import crk
K={}
WARM=(1.0,0.68,0.38); WARM2=(1.0,0.58,0.30); COOL=(0.72,0.84,1.0)
DOWN=(0,0,0)
def build(c):
    co=c.coll; L=crk.light
    # key zone 1: three troffers over the operator desks (third tube is dying)
    for (x,fl) in ((-3.0,False),(-0.6,False),(1.2,True)):
        L(co,f"CR troffer {x}",(x,-7.06,8.47),WARM,K.get("troffer",112),'AREA',DOWN,size=(1.15,0.55),expr=("112*(1-0.85*max(0,sin(frame*2.7)*sin(frame*0.53)*sin(frame*0.19+1)-0.42)*3.0)" if fl else None))
    # key zone 2: rack batten + pendant over the work table
    L(co,"CR rack batten",(1.25,-10.3,8.47),WARM2,K.get("rack",90),'AREA',DOWN,size=(1.1,0.16))
    px,py,pz=c.PENDANT
    L(co,"CR work pendant",(px,py,pz-0.02),WARM,K.get("pendant",143),'SPOT',DOWN,spot=115,blend=0.55,soft=0.06)
    L(co,"CR work lamp",c.WORKLAMP,WARM,K.get("worklamp",25),'SPOT',(math.radians(160),0,math.radians(30)),spot=70,blend=0.6,soft=0.03)
    L(co,"CR desk lamp",c.DESKLAMP,WARM,K.get("desklamp",35),'SPOT',(math.radians(150),0,math.radians(-30)),spot=75,blend=0.6,soft=0.03)
    # cool window spill + door spill from the landing
    L(co,"CR window spill",(-1.4,-6.35,7.2),COOL,K.get("window",119),'AREA',(-math.pi/2,0,0),size=(5.4,2.2))
    L(co,"CR door spill",(-5.15,-6.8,6.7),COOL,K.get("door",45),'AREA',(0,math.pi/2,0),size=(0.9,1.8))
    # low warm bounce so far corners stay readable (but darker)
    L(co,"CR back fill",(-1.4,-10.3,8.4),WARM,K.get("fill",9.6),'AREA',DOWN,size=(5.0,2.4))
    # accents: CRT phosphor glows and rack LEDs
    for cx,col in ((-2.75,(0.2,1.0,0.3)),(-1.05,(1.0,0.55,0.1)),(0.65,(0.2,1.0,0.3))):
        L(co,f"CR crt glow {cx}",(cx,-7.15,6.50),col,K.get("crt",7),'AREA',(-math.pi/2,0,0),size=(0.30,0.22),expr="7*(0.92+0.08*sin(frame*1.7))")
    L(co,"CR rack glow low",(0.98,-10.35,5.95),(0.3,1.0,0.35),K.get("rackglow",3.0),'POINT',soft=0.05)
    L(co,"CR rack glow mid",(0.98,-10.35,6.60),(1.0,0.55,0.12),K.get("rackglow",3.0),'POINT',soft=0.05)
