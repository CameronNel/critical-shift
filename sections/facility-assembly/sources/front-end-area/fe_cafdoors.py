"""Cafeteria doors (leaves, frames, hold-open sliding set) and every cafeteria sign. All lettering is baked into the sign atlas."""
from fe_kit import *
from fe_doors import *
from fe_signs import sign, hanging_sign

def build_cafe_doors_and_signs(F, C):
    caf, yard, hall = C['CAFETERIA'], C['YARD'], C['HALL']; P = collection('PROTOTYPES')
    la = leaf_airlock(F, P); lg = leaf_glazed(F, P); lm = leaf_medical(F, P); ls = leaf_staff(F, P); lsl = sliding_panel(F, P)
    # ---- spawn airlock, south wall (x 6.7..9.3): two pressure-door leaves, closed
    place_leaf(la, 'airlock_leaf_L', caf, 'x', 6.62, -80.0, 1.5, '+'); place_leaf(la, 'airlock_leaf_R', caf, 'x', 9.38, -80.0, 1.5, '+', mirror=True)
    box('airlock_threshold', 6.7, 9.3, -80.12, -79.88, 0.0, 0.025, F['steel_charcoal'], caf, bev=0.006)
    box('airlock_header_hazard', 6.6, 9.4, -79.86, -79.83, 2.62, 2.7, F['signage'], caf, rgba=(0.92, 0.72, 0.05, 1))
    # ---- yard door, west wall (y -71.5..-68.5): two glazed leaves, the north one ajar
    place_leaf(lg, 'yard_leaf_S', caf, 'y', -8.0, -71.58, 1.5, '+'); place_leaf(lg, 'yard_leaf_N', caf, 'y', -8.0, -68.42, 1.5, '+', mirror=True)
    box('yard_threshold', -8.15, -7.85, -71.5, -68.5, 0.0, 0.02, F['steel_charcoal'], caf, bev=0.005)
    # ---- medical door, east wall (y -71.1..-68.9): two white leaves, closed
    place_leaf(lm, 'med_leaf_S', caf, 'y', 26.0, -71.3, 1.5, '-'); place_leaf(lm, 'med_leaf_N', caf, 'y', 26.0, -68.7, 1.5, '-', mirror=True)
    box('med_threshold', 25.85, 26.15, -71.1, -68.9, 0.0, 0.02, F['steel_charcoal'], caf, bev=0.005)
    # ---- kitchen staff door in the kitchen's west wall (y -62.9..-62.0), ajar into the kitchen
    for nm, (y0, y1, z0, z1) in {'kdoor_wall_S': (-64.0, -62.95, 0, 3.3), 'kdoor_wall_N': (-62.0, -60.15, 0, 3.3), 'kdoor_head': (-62.95, -62.0, 2.1, 3.3)}.items():
        box(nm, 13.9, 14.05, y0, y1, z0, z1, F['plaster'], caf)
    for s_, yy in (('S', -62.97), ('N', -61.98)): box(f'kdoor_jamb_{s_}', 13.86, 14.1, yy - 0.03, yy + 0.03, 0, 2.12, F['steel_charcoal'], caf, bev=0.006)
    box('kdoor_lintel', 13.86, 14.1, -63.0, -61.95, 2.1, 2.16, F['steel_charcoal'], caf, bev=0.006)
    place_leaf(ls, 'kitchen_staff_leaf', caf, 'y', 13.98, -62.93, 0.55, '+')
    # ---- hall opening, north wall (x 5..11): automatic sliding panels parked on the hall side, header rail and sensor
    box('hall_door_rail', 3.2, 12.8, -59.78, -59.5, 3.62, 3.78, F['steel_charcoal'], hall, bev=0.01)
    for nm, x0 in (('hall_slide_L', 3.4), ('hall_slide_R', 11.1)): place_leaf(lsl, nm, hall, 'x', x0, -59.58, 0.0, '+')
    box('hall_door_sensor', 7.8, 8.2, -59.8, -59.68, 3.5, 3.6, F['plastic'], hall, rgba=(0.1, 0.1, 0.12, 1), bev=0.01)
    # ---- signs: wayfinding over every door (interior face), exterior name plates, lit exit signs
    sign(caf, 'sign_airlock_in', 'ARRIVAL AIRLOCK', 8.0, -79.83, 2.78, 'N', 2.6, 0.46, sub='Staff entry  -  badge required', icon='door', style='nav')
    sign(caf, 'sign_airlock_leaf_L', 'AIRLOCK', 7.34, -79.9, 1.55, 'N', 0.5, 0.16, style='hazard') if False else None
    sign(caf, 'sign_yard_in', 'YARD', -7.83, -70.0, 3.0, 'E', 2.2, 0.42, sub='Salvage yard  -  mine entrance', icon='arrow_l', style='nav')
    sign(caf, 'sign_exit_yard', 'EXIT', -7.83, -70.0, 3.5, 'E', 0.9, 0.3, icon='arrow_l', style='exit', lit=True)
    sign(yard, 'sign_cafeteria_out', 'CAFETERIA', -8.16, -70.0, 3.0, 'W', 3.0, 0.55, sub='Staff arrival  -  canteen  -  lounge', icon='cutlery', style='nav')
    sign(caf, 'sign_medical_in', 'MEDICAL', 25.83, -70.0, 2.62, 'W', 2.2, 0.55, sub='Reanimation ward', icon='cross', style='med')
    sign(caf, 'sign_hall_in', 'HALL', 8.0, -60.17, 3.68, 'S', 4.6, 0.7, sub='Refinery  -  reactor  -  dock', icon='arrow_u', style='nav')
    sign(hall, 'sign_hall_in_n', 'CAFETERIA', 8.0, -59.83, 3.82, 'N', 2.8, 0.42, sub='Dining  -  lounge  -  medical', icon='cutlery', style='nav')
    sign(caf, 'sign_staff_only', 'STAFF ONLY', 13.9, -62.45, 2.2, 'W', 0.9, 0.22, style='staff')
    # hanging zone signs (double-sided), readable from the airlock lane
    hanging_sign(caf, 'zone_dining', 'DINING HALL', 19.3, -70.0 - 5.0, 3.35, 'S', 2.5, 0.5, sub='Hot meals  -  drinks  -  snacks', icon='cutlery', F=F)
    hanging_sign(caf, 'zone_lounge', 'LOUNGE', -4.2, -73.4, 3.35, 'S', 2.0, 0.48, sub='Quiet seating', icon='sofa', style='green', F=F)
    hanging_sign(caf, 'zone_game', 'GAME ROOM', -3.6, -67.6, 3.35, 'S', 2.2, 0.48, sub='Foosball  -  basketball  -  darts', icon='game', style='nav', F=F)
    hanging_sign(caf, 'zone_serving', 'SERVING', 20.2, -67.6, 3.1, 'S', 2.2, 0.5, sub='Order at the kiosk or the counter', icon='cutlery', style='nav', F=F)
    hanging_sign(caf, 'zone_order', 'ORDER HERE', 13.1, -68.6, 1.95, 'S', 1.2, 0.34, icon='arrow_d', style='board', F=F)
    sign(caf, 'sign_drinks', 'DRINKS', 25.83, -72.9, 2.35, 'W', 0.9, 0.28, icon='cup', style='info')
    sign(caf, 'sign_tray_return', 'TRAYS', 25.83, -75.6, 2.1, 'W', 0.8, 0.24, style='info')
    # menu boards over the serving hatch (baked menu text)
    for k, (title, lines) in enumerate((('SOUP & BREAD', ['Tomato and basil  3.20', 'Leek and potato  3.20', 'Bread roll  0.80']),
                                       ('HOT MEALS', ['Pie of the day  6.50', 'Vegetable lasagne  6.20', 'Rice and curry  6.00']),
                                       ('DRINKS & SNACKS', ['Tea and coffee  1.50', 'Fresh juice  1.80', 'Fruit pot  1.00']))):
        sign(caf, f'menu_board_{k}', title, 15.35 + k * 3.2 + 1.5, -64.17, 2.45, 'S', 3.0, 0.82, style='board', lines=lines)
    # ---- wall graphics: large baked slogan plates and rules boards
    sign(caf, 'banner_slogan', 'PEOPLE KEEP OPERATIONS MOVING', 14.0, -79.83, 3.1, 'N', 3.4, 0.62, sub='Critical Shift', style='nav')
    sign(caf, 'banner_safer', 'SAFER TOGETHER', 2.0, -79.83, 3.1, 'N', 3.3, 0.6, sub='Report hazards to your shift lead', style='green')
    sign(caf, 'banner_recycle', 'RECYCLING', 25.83, -77.6, 1.5, 'W', 1.6, 0.34, icon='arrow_d', style='green')
    sign(caf, 'rules_game', 'GAME ROOM RULES', -7.2, -60.17, 2.55, 'S', 1.7, 1.0, style='board', lines=['Wipe tables after use  ', 'Return the balls  ', 'Quiet after 22:00  ', 'Be kind  '])
    sign(caf, 'sign_lounge_wall', 'LOUNGE', -7.83, -78.2, 2.9, 'E', 1.3, 0.36, icon='sofa', style='green')
    sign(caf, 'neon_game', 'GAME ROOM', -3.6, -60.17, 3.25, 'S', 2.6, 0.55, sub='Foosball  -  basketball  -  darts', icon='game', style='nav', lit=True)
    sign(caf, 'board_allergen', 'ALLERGEN INFORMATION', 13.9, -61.15, 1.45, 'W', 1.7, 1.15, style='board', lines=['Ask staff before ordering  ', 'Nuts  -  see counter  ', 'Dairy  -  see counter  ', 'Gluten  -  see counter  '])
    sign(caf, 'board_directory', 'DIRECTORY', 10.8, -66.58, 0.55, 'S', 0.8, 1.45, style='board', lines=['Dining hall  east  ', 'Serving  east  ', 'Lounge  west  ', 'Game room  west  ', 'Hall  north  ', 'Yard  west  ', 'Medical  east  '])
    sign(caf, 'sign_wash_hands', 'WASH YOUR HANDS', 13.9, -63.55, 1.35, 'W', 0.95, 0.26, style='med')
    # branded wall band along every cafeteria wall
    from fe_assets_caf2 import wall_band
    wall_band(F, caf, 'band_S', 'x', -79.83, -7.4, 25.4, 3.3, 'N', excl=[(6.5, 9.5)]); wall_band(F, caf, 'band_N', 'x', -60.17, -7.4, 25.4, 3.3, 'S', excl=[(4.5, 11.5)])
    wall_band(F, caf, 'band_W', 'y', -7.83, -79.6, -60.4, 3.3, 'E', excl=[(-71.7, -68.3)]); wall_band(F, caf, 'band_E', 'y', 25.83, -79.6, -60.4, 3.3, 'W', excl=[(-71.4, -68.6)])
