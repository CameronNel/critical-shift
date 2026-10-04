"""Front-end area design data: cafeteria, hall and yard as one connected module.
Coordinates: metres, same frame as the facility plan (x east, y north, z up)."""
# ---- zones (footprints)
YARD     = (-48.0,  -8.0, -84.0, -60.0)   # x0,x1,y0,y1 (40 x 24), includes a 4 m covered porch x[-12,-8]
CAF      = ( -8.0,  26.0, -80.0, -60.0)   # 34 x 20
HALL     = ( -4.0,  32.0, -60.0, -48.0)   # 36 x 12
SPAWN    = ( -0.7,  16.7, -93.4, -80.0)   # measured 17.4 x 13.4
MEDICAL  = ( 26.0,  39.0, -74.9, -65.1)   # measured 13 x 9.8 (door on west wall)
AXIS_X = 8.0            # reactor axis: spawn door -> cafeteria aisle -> hall -> spine -> reactor
MINE_Y = -70.0          # mine axis: cafeteria west door -> porch -> yard -> mine portal
H_CAF, H_HALL, H_YARD_WALL = 5.0, 6.0, 8.0

# ---- triangle budget (design estimates, evaluated triangles; each instance counts)
# (zone, group, item, count, tris_each)
ITEMS = [
 # YARD
 ('Yard','Ground','Concrete slabs, bevelled, 4 m grid',66,40),
 ('Yard','Ground','Drain trenches and recessed puddles',5,300),
 ('Yard','Ground','Kerbs, steps and loading apron',1,4000),
 ('Yard','Mountain edge','Cliff wall and rock shelf, hero kitbash',1,85000),
 ('Yard','Mountain edge','Retaining wall and mine portal surround',1,14000),
 ('Yard','Rail','Mine cart track, rails and 64 ties',1,5000),
 ('Yard','Rail','Ore carts',2,6000),
 ('Yard','Boundary','Fence panels and vehicle gate (evacuation)',1,14000),
 ('Yard','Structures','Porch canopy and smoking shelter',1,14000),
 ('Yard','Structures','Loading canopy over the refinery gate',1,10000),
 ('Yard','Structures','Generator, fuel tank, water tank',3,7000),
 ('Yard','Structures','Pipe runs and mine-water riser',1,10000),
 ('Yard','Junk','Crate stacks (3 crates avg)',10,900),
 ('Yard','Junk','Pallets',8,600),
 ('Yard','Junk','Barrels',20,350),
 ('Yard','Junk','Cable drums',4,700),
 ('Yard','Junk','Scrap steel piles',3,3500),
 ('Yard','Junk','Tarp-covered piles',2,3000),
 ('Yard','Junk','Tyres',6,500),
 ('Yard','Junk','Cones and bollards',20,170),
 ('Yard','Furniture','Benches',3,800),
 ('Yard','Planting','Planters',6,1200),
 ('Yard','Planting','Shrubs',20,600),
 ('Yard','Planting','Trees (low-poly crowns)',4,3500),
 ('Yard','Lighting','Pole lights',5,1200),
 ('Yard','Signage','Signs, stencils, notices',12,300),
 # CAFETERIA
 ('Cafeteria','Shell','Floor, walls, high windows, door frames',1,32000),
 ('Cafeteria','Shell','Ceiling ribs and skylights',1,12000),
 ('Cafeteria','Kitchen','Serving counter and kitchen block',1,26000),
 ('Cafeteria','Dining','Chairs',24,1000),
 ('Cafeteria','Dining','Tables',6,1500),
 ('Cafeteria','Dining','Booths',3,5000),
 ('Cafeteria','Lounge','Couches',2,6000),
 ('Cafeteria','Lounge','Coffee table, shelf, TV wall',1,9000),
 ('Cafeteria','Lounge','Plants',4,2000),
 ('Cafeteria','Appliances','Vending machines',3,6000),
 ('Cafeteria','Appliances','Coffee machine, water cooler, fridge',3,4000),
 ('Cafeteria','Small props','Trays, mugs, bottles, magazines, bins',1,14000),
 ('Cafeteria','Lighting','Pendant and strip fixtures',12,1500),
 ('Cafeteria','Signage','Notice board, menu, decals',1,6000),
 # HALL
 ('Hall','Shell','Floor, walls, ceiling bays, clerestory',1,20000),
 ('Hall','Doors','Three heavy blast doors with frames and lights',3,9000),
 ('Hall','Doors','West and east end doors',2,3500),
 ('Hall','Gantry','Gantry landing, stair and rails over the spine door',1,16000),
 ('Hall','Furniture','Benches',3,900),
 ('Hall','Safety','Eyewash, first aid, fire cabinet, PPE return',1,12000),
 ('Hall','Desk','Shift desk kiosk with monitors',1,10000),
 ('Hall','Lighting','Hanging and wall lights',11,1200),
 ('Hall','Signage','Direction signs, floor route lines, status board',1,8000),
 # SHARED
 ('Shared','Roof','Roof deck, trusses and gutters over cafeteria and hall',1,37000),
 ('Shared','Structure','Portal frames, columns, wall plates',1,24000),
 ('Shared','Connectors','West colonnade, east trunk threshold, spine mouth',1,24000),
]
RESERVE_PCT = 10
TARGET = 800_000

MATERIALS = [
 ('Concrete slab (yard, hall floor)','Yard, hall'),
 ('Plaster and painted concrete wall','All'),
 ('Painted steel, charcoal (structure)','All'),
 ('Painted steel, ochre and orange accent','All'),
 ('Weathered and rusted steel','Yard, hall'),
 ('Corrugated metal','Roof, yard sheds'),
 ('Cafeteria floor tile','Cafeteria'),
 ('Rubber mat and hall floor strip','Hall, cafeteria'),
 ('Timber (benches, table tops, pallets)','All'),
 ('Laminate and counter surfaces','Cafeteria'),
 ('Glass, wired and clear','All'),
 ('Fabric upholstery','Cafeteria'),
 ('Moulded plastic (chairs, bins, cones)','All'),
 ('Signage and decal atlas','All'),
 ('Foliage atlas (planters, shrubs, trees)','Yard, cafeteria'),
 ('Rock cliff','Yard'),
 ('Crate, cardboard and tarp prop atlas','Yard, cafeteria'),
 ('Emissive lights and screens','All'),
]
def totals():
    z={}
    for zone,grp,name,n,t in ITEMS:
        z.setdefault(zone,{}); z[zone][grp]=z[zone].get(grp,0)+n*t
    return z
if __name__=='__main__':
    z=totals(); tot=0
    for k,v in z.items():
        s=sum(v.values()); tot+=s; print(f'{k:10s} {s:8,d}')
    print(f'{"TOTAL":10s} {tot:8,d}  reserve {TARGET-tot:,d} ({100*(TARGET-tot)/TARGET:.1f}%)  materials {len(MATERIALS)}')
