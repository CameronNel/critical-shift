"""Mine surface depot: what stands on the apron and why. Plan frame: yard x -48..-8, y -84..-60; mine axis y = -70; rail runs east from the portal, turns north at x = -22.2 and leaves through the freight gate to the refinery.

Zones (west to east, north to south):
  Portal       mine portal and vent fan, lamp room cabin (tag in and out), tag board, ore cars on the rail, track scale and its display
  Ore bays     three push-wall bays for ore grades A and B and waste rock, skid loader in front; gas store cage
  Rail dock    two loading docks either side of the freight gate: supplies in, parcels, drums, forklift, beacons, hazard threshold
  Vehicle bay  three marked bays with wheel stops (pickup, crew van, forklift), bunded diesel station beside them
  Store        three containers (spares, tools, consumables), muster area, generator in a fenced enclosure, water tank
  Porch        benches, PPE check and site rules board, recycling, planters at the cafeteria door
Clear lanes: mine lane y -71.4..-68.6, refinery rail x -23.5..-20.9 (y > -70.5), evacuation path x -29.7..-26.3 (y < -71.2), north-west service door path x -47.4..-44.8 (y > -68.8), porch x -12.6..-7.9."""
import math, random
from fe_common import *
from fe_kit import *
from fe_assets_int import STD, I, mb
from fe_assets_yard import (container, skip_bin, tank_vertical, generator, barrel, gas_rack, hand_truck, forklift, bench, planter, shrub, bollard, cable_drum, pallet, crate, fence_panel, hose_reel)
from fe_assets_caf2 import recycling_bins
from fe_hall_assets import parcel_stack
from fe_depot_assets import *
from fe_signs import sign, hanging_sign, ROT
from fe_hallops import floor_sign, strip, bay, hatch
from fe_yard import inst, YARD, RAIL_Y, RAIL_X
from fe_yard3 import FLAT_X

YELLOW = (0.92, 0.72, 0.06, 1); GREEN = (0.08, 0.35, 0.2, 1)

def post_sign(coll, name, text, x, y, facing, w, h, z, F, **kw):
    """Free-standing baked sign: steel post behind a single plate (the post sits on the side away from the viewer)."""
    off = {'E': (0.07, 0), 'W': (-0.07, 0), 'N': (0, 0.07), 'S': (0, -0.07)}[facing]
    box(name + '_post', x - 0.045, x + 0.045, y - 0.045, y + 0.045, 0.0, z + h + 0.1, F['steel_charcoal'], coll, bev=0.01)
    return sign(coll, name, text, x + off[0], y + off[1], z, facing, w, h, **kw)

def build_depot(F, C):
    yard = C['YARD']; P = collection('PROTOTYPES'); rnd = random.Random(51)
    # ---------------------------------------------------------------- prototypes
    pick = site_pickup(F, P); van = crew_van(F, P); car = ore_car(F, P); piles = [ore_pile(F, P, s, 1.15, 1.0) for s in range(3)]
    cabin = site_cabin(F, P); scale = track_scale(F, P); spost = scale_post(F, P); loader = skid_loader(F, P); fuel = fuel_station(F, P)
    bays = bay_walls(F, P, 4.4, 3.4, 1.8); pole = led_pole(F, P); wstop = wheel_stop(F, P); dock = dock_platform(F, P, 5.4, 2.6, 0.95); fan = vent_fan(F, P)
    green_c = (0.2, 0.3, 0.26, 1)
    cont = [container(F, P, green_c, f'container_{i}') for i in range(3)]
    fk = forklift(F, P, (0.85, 0.5, 0.06, 1)); gas = gas_rack(F, P); ht = hand_truck(F, P); brl = [barrel(F, P, c, f'barrel_{i}') for i, c in enumerate(((0.12, 0.3, 0.45, 1), (0.55, 0.14, 0.1, 1), (0.3, 0.34, 0.3, 1)))]
    gen = generator(F, P); tank = tank_vertical(F, P, 2.6, 1.05, (0.5, 0.56, 0.6, 1), 'tank_a'); skp = skip_bin(F, P); bn = bench(F, P); plt = planter(F, P); shr = shrub(F, P, 3, 0.5)
    rec = recycling_bins(F, P); pk = [parcel_stack(F, P, s, 2) for s in range(2)]; fp = fence_panel(F, P); bol = bollard(F, P); hr = hose_reel(F, P)
    cabs = [cabin]

    # ---------------------------------------------------------------- PORTAL
    inst(fan, 'vent_fan', -46.6, -77.0, yard, rz=0.0)
    inst(cabin, 'lamp_room_cabin', -42.8, -74.4, yard, rz=0.0)
    sign(yard, 'sign_lamp_room', 'LAMP ROOM', -42.8 + 2.1, -73.1, 2.42, 'N', 1.4, 0.26, style='nav')
    post_sign(yard, 'board_tag', 'TAG IN  AND  OUT', -37.6, -72.55, 'N', 1.6, 1.0, 0.95, F, style='board', lines=['Tag in before entry  ', 'Self-rescuer  checked  ', 'Lamp and radio  checked  ', 'Tag out on exit  '])
    for i, x in enumerate((-42.2, -39.4, -36.6)):
        inst(car, f'ore_cart_{i}', x, RAIL_Y, yard, rz=0.0, support=None)
        sign(yard, f'sign_car_{i}', f'CAR {7 + i:02d}', x, RAIL_Y - 0.68, 0.72, 'S', 0.5, 0.2, style='info')
    inst(scale, 'floor_track_scale', -32.0, RAIL_Y, yard, support='floor_broken')
    inst(spost, 'scale_post', -30.0, -72.6, yard, rz=0.0)

    # ---------------------------------------------------------------- ORE BAYS (north-west) and gas store
    for i, (cx, nm, sub, pile) in enumerate(((-41.9, 'ORE  GRADE A', 'High grade', 1), (-37.4, 'ORE  GRADE B', 'Mixed', 1), (-32.9, 'WASTE  ROCK', 'To spoil', 2))):
        inst(bays, f'ore_bay_{i}', cx, -60.7, yard, rz=math.pi)
        inst(piles[pile], f'ore_pile_{i}', cx, -62.8, yard, rz=rnd.uniform(0, 6.28))
        sign(yard, f'sign_bay_{i}', nm, cx, -61.5, 0.95, 'S', 1.9, 0.5, sub=sub, style='nav')
    inst(loader, 'skid_loader', -31.0, -66.2, yard, rz=math.pi / 2 + 0.15)
    gx0, gx1, gy0, gy1 = -29.6, -26.6, -63.8, -60.7
    for k, (px, py, rz, sx) in enumerate(((-28.1, gy0, 0.0, 1.0), (gx0, -62.25, math.pi / 2, 1.03), (gx1, -62.25, math.pi / 2, 1.03))): inst(fp, f'gas_cage_{k}', px, py, yard, rz=rz, scale=(sx, 1, 0.8), support='floor')
    inst(gas, 'gas_rack_0', -28.1, -62.2, yard, rz=0.0)
    sign(yard, 'sign_gas', 'GAS STORE', -28.1, gy0 - 0.03, 1.55, 'S', 1.5, 0.4, sub='No naked flames', icon='warn', style='hazard')

    # ---------------------------------------------------------------- RAIL DOCK
    sc = (1.0, 1.0, 1.0)
    inst(dock, 'dock_west', -25.2, -62.5, yard, rz=-math.pi / 2, support='floor')
    inst(dock, 'dock_east', -19.3, -62.5, yard, rz=math.pi / 2, support='floor')
    inst(pk[0], 'dock_parcels_0', -25.2, -63.6, yard, rz=0.1, z=0.95, support='stack'); inst(pk[1], 'dock_parcels_1', -25.2, -61.4, yard, rz=-0.05, z=0.95, support='stack')
    for i, (x, y) in enumerate(((-19.4, -63.7), (-19.9, -62.8), (-19.0, -62.6))): inst(brl[i % 3], f'dock_drum_{i}', x, y, yard, rz=rnd.uniform(0, 6), z=0.95, support='stack')
    inst(ht, 'dock_hand_truck', -18.6, -61.2, yard, rz=2.4, z=0.95, support='stack')
    inst(fk, 'forklift_0', -26.9, -67.5, yard, rz=0.0)
    box('freight_beacon_L', RAIL_X - 1.62, RAIL_X - 1.48, -60.3, -60.05, 3.3, 3.5, F['emissive'], yard, rgba=(1.0, 0.6, 0.1, 1), bev=0.02)
    box('freight_beacon_R', RAIL_X + 1.48, RAIL_X + 1.62, -60.3, -60.05, 3.3, 3.5, F['emissive'], yard, rgba=(1.0, 0.6, 0.1, 1), bev=0.02)
    sign(yard, 'sign_freight', 'REFINERY FREIGHT', RAIL_X, -60.26, 3.34, 'S', 2.8, 0.4, sub='Rail only  -  trains have priority', icon='arrow_u', style='nav')
    hatch(yard, 'floor_freight_hatch', RAIL_X - 1.4, RAIL_X + 1.4, -61.2, -60.7, 14, F)
    floor_sign(yard, 'floor_stop_train', 'STOP  TRAINS', RAIL_X, -66.4, 2.2, 0.4, 'N', icon='warn', style='hazard')

    # ---------------------------------------------------------------- VEHICLE BAYS and diesel
    vx = (-39.0, -36.0, -33.0, -30.0)
    for x in vx: strip(yard, f'floor_bayline_{x}', x - 0.05, x + 0.05, -83.5, -77.8, YELLOW, F)
    strip(yard, 'floor_bayline_front', vx[0], vx[-1], -77.85, -77.75, YELLOW, F)
    for i in range(3):
        cx = (vx[i] + vx[i + 1]) / 2
        inst(wstop, f'wheel_stop_{i}', cx, -83.3, yard, rz=0.0)
        floor_sign(yard, f'floor_bay_no_{i}', f'V{i + 1}', cx, -77.45, 0.8, 0.4, 'S', style='hazard')
    inst(pick, 'site_pickup', -37.5, -80.6, yard, rz=-math.pi / 2)
    inst(van, 'crew_van', -34.5, -80.6, yard, rz=-math.pi / 2)
    inst(fk, 'forklift_1', -31.5, -81.2, yard, rz=-math.pi / 2)
    for k, (x, rz) in enumerate(((-37.5, 0.0), (-34.5, math.pi))):                                       # company plates on the vehicles
        sx = -80.6 + 0.0
    sign(yard, 'sign_pickup', 'SITE 01', -37.5 + 0.97, -80.6 - 0.6, 0.78, 'E', 0.5, 0.18, style='info')
    sign(yard, 'sign_van', 'CREW VAN', -34.5 + 1.0, -80.6 - 0.2, 1.15, 'E', 0.9, 0.22, style='nav')
    inst(fuel, 'fuel_station', -44.7, -81.6, yard, rz=0.0, support='floor')
    post_sign(yard, 'board_fuel', 'DIESEL', -41.4, -79.6, 'E', 1.4, 0.95, 1.0, F, style='hazard', lines=['Engines off  ', 'No smoking  ', 'No naked flames  ', 'Spill kit  at the pump'])
    for i, y in enumerate((-82.2, -81.0)): inst(bol, f'fuel_bollard_{i}', -40.4, y, yard)
    hatch(yard, 'floor_fuel_hatch', -42.6, -40.8, -83.2, -80.1, 10, F, vertical=True)

    # ---------------------------------------------------------------- STORE (south-east): containers, muster, power and water
    for i, (y, nm, sub) in enumerate(((-82.0, 'STORE 1', 'Spares'), (-79.1, 'STORE 2', 'Tools'), (-76.2, 'STORE 3', 'Consumables and PPE'))):
        inst(cont[i], f'container_{i}', -20.6, y, yard, rz=0.0)
        sign(yard, f'sign_store_{i}', nm, -23.63, y, 1.45, 'W', 1.0, 0.42, sub=sub, style='nav')
    mx0, mx1, my0, my1 = -24.4, -17.0, -74.6, -72.0
    strip(yard, 'floor_muster_fill', mx0, mx1, my0, my1, GREEN, F); bay(yard, 'floor_muster_edge', mx0, mx1, my0, my1, F, 0.1)
    floor_sign(yard, 'floor_muster_label', 'MUSTER B', (mx0 + mx1) / 2, (my0 + my1) / 2, 2.4, 0.55, 'S', icon='muster', style='exit')
    post_sign(yard, 'sign_muster', 'MUSTER POINT B', mx1 - 0.4, my0 + 0.3, 'N', 1.6, 0.55, 1.5, F, sub='Assemble here', icon='muster', style='exit')
    ex0, ex1, ey0, ey1 = -14.4, -10.4, -82.9, -79.0
    for k, (px, py, rz, sx) in enumerate(((-12.4, ey0, 0.0, 1.33), (-12.4, ey1, 0.0, 1.33), (ex0, -80.95, math.pi / 2, 1.3), (ex1, -80.95, math.pi / 2, 1.3))): inst(fp, f'gen_fence_{k}', px, py, yard, rz=rz, scale=(sx, 1, 0.9), support='floor')
    inst(gen, 'generator', -12.4, -80.95, yard, rz=0.0)
    sign(yard, 'sign_generator', 'GENERATOR', -12.4, ey1 + 0.03, 1.6, 'N', 1.4, 0.35, sub='Authorised staff only', icon='bolt', style='hazard') if False else post_sign(yard, 'sign_generator', 'GENERATOR', -12.4, ey1 - 0.4, 'S', 1.4, 0.35, 1.5, F, sub='Authorised staff only', icon='bolt', style='hazard')
    inst(tank, 'water_tank', -16.2, -80.0, yard)
    post_sign(yard, 'sign_water', 'WATER', -16.2, -78.6, 'S', 0.9, 0.3, 1.5, F, style='info')

    # ---------------------------------------------------------------- waste (north-east) and porch
    inst(skp, 'skip_general', -14.8, -62.3, yard, rz=0.0); inst(skp, 'skip_scrap', -11.0, -62.3, yard, rz=0.0)
    sign(yard, 'sign_skip_a', 'GENERAL WASTE', -14.8, -63.33, 0.7, 'S', 1.2, 0.26, style='nav'); sign(yard, 'sign_skip_b', 'SCRAP METAL', -11.0, -63.33, 0.7, 'S', 1.2, 0.26, style='nav')
    inst(bn, 'porch_bench_0', -10.5, -65.3, yard, rz=math.pi / 2); inst(bn, 'porch_bench_1', -10.5, -74.7, yard, rz=math.pi / 2)
    inst(rec, 'porch_recycling', -9.0, -64.6, yard, rz=math.pi / 2)
    post_sign(yard, 'board_rules', 'SITE RULES', -12.9, -72.7, 'E', 1.4, 1.0, 1.0, F, style='board', lines=['Hard hat and hi-vis  ', 'Boots on  at all times  ', '10 km/h site limit  ', 'Trains have priority  ', 'Report all incidents  '])
    post_sign(yard, 'sign_ppe_check', 'PPE CHECK', -12.9, -67.2, 'E', 1.2, 0.34, 1.7, F, sub='Before the yard', icon='hat', style='nav')
    for i, (x, y) in enumerate(((-8.9, -77.8), (-8.9, -80.2))):
        inst(plt, f'planter_{i}', x, y, yard); inst(shr, f'planter_shrub_{i}', x, y, yard, z=0.6, support=None, scale=(1.1, 1.1, 1.1))
    for i, y in enumerate((-72.4, -67.6, -61.0, -83.0)): inst(bol, f'bollard_{i}', -8.9, y, yard)
    post_sign(yard, 'sign_speed', 'SPEED 10', -17.5, -73.0, 'W', 0.8, 0.8, 1.0, F, style='hazard') if False else post_sign(yard, 'sign_speed', '10 KM/H', -15.6, -72.9, 'W', 1.0, 0.4, 1.3, F, style='hazard')

    # ---------------------------------------------------------------- gates and doors: baked signs
    sign(yard, 'sign_evac_gate', 'EVACUATION GATE', -28.0, -83.78, 2.55, 'N', 2.8, 0.45, sub='Keep clear at all times', icon='run', style='exit', lit=True)
    sign(yard, 'sign_cooling', 'COOLING PLANT', -46.0, -60.26, 2.6, 'S', 2.2, 0.4, sub='Authorised staff only', icon='bolt', style='staff')
    for i, (x, y) in enumerate(((-22.2, -59.9),)): pass

    # ---------------------------------------------------------------- lighting poles and markings
    for i, (x, y, rz) in enumerate(((-46.5, -66.4, -math.pi / 2), (-34.0, -66.8, -math.pi / 2), (-17.0, -66.8, -math.pi / 2),
                                    (-46.8, -72.6, math.pi / 2), (-31.2, -73.0, math.pi / 2), (-17.0, -72.8, math.pi / 2), (-33.5, -77.2, math.pi / 2), (-12.2, -77.2, math.pi / 2))):
        inst(pole, f'pole_{i}', x, y, yard, rz=rz)
    strip(yard, 'floor_walk_a', -46.0, -9.0, -70.0 - 0.0, -70.0 + 0.0, YELLOW, F) if False else None
    return True
