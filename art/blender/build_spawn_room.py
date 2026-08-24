"""
Critical Shift - Production Stylized Spawn/Start Room Builder
Complete Sea of Thieves-inspired stylized industrial sci-fi architecture, hero PPE, and devices.
"""
import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

def get_or_create_material(name, base_color=(0.5, 0.5, 0.5, 1.0), roughness=0.5, metallic=0.0, emissive=(0,0,0,1), emissive_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    
    principled.inputs['Base Color'].default_value = base_color
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Metallic'].default_value = metallic
    
    if 'Emission Color' in principled.inputs:
        principled.inputs['Emission Color'].default_value = emissive
        if 'Emission Strength' in principled.inputs:
            principled.inputs['Emission Strength'].default_value = emissive_strength
    elif 'Emission' in principled.inputs:
        principled.inputs['Emission'].default_value = emissive
        if 'Emission Strength' in principled.inputs:
            principled.inputs['Emission Strength'].default_value = emissive_strength
            
    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_palette():
    mats = {}
    mats['M_CastIron'] = get_or_create_material('M_CastIron', (0.12, 0.14, 0.16, 1.0), 0.65, 0.85)
    mats['M_SafetyTeal'] = get_or_create_material('M_SafetyTeal', (0.18, 0.46, 0.52, 1.0), 0.45, 0.15)
    mats['M_WarningOrange'] = get_or_create_material('M_WarningOrange', (0.82, 0.38, 0.10, 1.0), 0.50, 0.20)
    mats['M_HazardYellow'] = get_or_create_material('M_HazardYellow', (0.88, 0.68, 0.12, 1.0), 0.40, 0.10)
    mats['M_HazardDark'] = get_or_create_material('M_HazardDark', (0.08, 0.08, 0.09, 1.0), 0.60, 0.10)
    mats['M_ConcreteFloor'] = get_or_create_material('M_ConcreteFloor', (0.28, 0.30, 0.31, 1.0), 0.80, 0.05)
    mats['M_MetalGrate'] = get_or_create_material('M_MetalGrate', (0.15, 0.17, 0.19, 1.0), 0.55, 0.90)
    mats['M_TreatedWood'] = get_or_create_material('M_TreatedWood', (0.42, 0.28, 0.18, 1.0), 0.70, 0.0)
    mats['M_BrassHardware'] = get_or_create_material('M_BrassHardware', (0.75, 0.55, 0.22, 1.0), 0.35, 0.95)
    mats['M_SuitFabric'] = get_or_create_material('M_SuitFabric', (0.78, 0.62, 0.15, 1.0), 0.75, 0.05)
    mats['M_SuitRubber'] = get_or_create_material('M_SuitRubber', (0.12, 0.12, 0.14, 1.0), 0.40, 0.10)
    mats['M_VisorGlass'] = get_or_create_material('M_VisorGlass', (0.15, 0.45, 0.40, 1.0), 0.10, 0.80, (0.1, 0.6, 0.5, 1.0), 0.8)
    mats['M_ScreenBriefing'] = get_or_create_material('M_ScreenBriefing', (0.05, 0.25, 0.28, 1.0), 0.20, 0.10, (0.20, 0.85, 0.90, 1.0), 3.0)
    mats['M_ScreenDark'] = get_or_create_material('M_ScreenDark', (0.04, 0.06, 0.07, 1.0), 0.30, 0.20)
    mats['M_LightEmitWarm'] = get_or_create_material('M_LightEmitWarm', (0.95, 0.80, 0.50, 1.0), 0.20, 0.0, (1.0, 0.85, 0.55, 1.0), 4.5)
    mats['M_LightEmitCyan'] = get_or_create_material('M_LightEmitCyan', (0.30, 0.90, 0.95, 1.0), 0.15, 0.0, (0.30, 0.90, 1.0, 1.0), 5.0)
    mats['M_GeigerYellow'] = get_or_create_material('M_GeigerYellow', (0.92, 0.72, 0.08, 1.0), 0.35, 0.05)
    return mats

def get_or_create_collection(col_name):
    if col_name in bpy.data.collections:
        return bpy.data.collections[col_name]
    col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(col)
    return col

def add_mesh_object(name, bm, mat, collection):
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    
    obj = bpy.data.objects.new(name, me)
    if mat:
        obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_box(name, center, size, mat, collection, bevel=0.03):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale and translate
    for v in bm.verts:
        v.co.x = v.co.x * size[0] + center[0]
        v.co.y = v.co.y * size[1] + center[1]
        v.co.z = v.co.z * size[2] + center[2]
    
    if bevel > 0.001:
        # Bevel edges for chunky stylized look
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=min(bevel, min(size)*0.25), segments=1, profile=0.5, affect='EDGES')
    
    return add_mesh_object(name, bm, mat, collection)

def create_cylinder(name, center, radius, depth, mat, collection, segments=16, rot=(0,0,0), bevel=0.02):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=depth)
    
    rot_mat = Euler(rot).to_matrix().to_4x4()
    for v in bm.verts:
        v.co = rot_mat @ v.co
        v.co.x += center[0]
        v.co.y += center[1]
        v.co.z += center[2]
        
    return add_mesh_object(name, bm, mat, collection)

# --- ARCHITECTURE BUILDER ---
def build_architecture(col, mats):
    # 1. Main Floor Slabs
    # Central Hallway Slab: bx [-3, 3], by [0, 14.5], bz [-0.15, 0.0]
    create_box("Floor_CentralHall", (0.0, 7.25, -0.08), (6.0, 14.5, 0.16), mats['M_ConcreteFloor'], col, 0.04)
    # Briefing Wing Slab: bx [-12, -3], by [4, 13], bz [-0.15, 0.0]
    create_box("Floor_BriefingWing", (-7.5, 8.5, -0.08), (9.0, 9.0, 0.16), mats['M_ConcreteFloor'], col, 0.04)
    # Locker Wing Slab: bx [3, 12], by [4, 13], bz [-0.15, 0.0]
    create_box("Floor_LockerWing", (7.5, 8.5, -0.08), (9.0, 9.0, 0.16), mats['M_ConcreteFloor'], col, 0.04)
    
    # Drainage Trench down Central Hallway
    create_box("Floor_DrainTrench_L", (-1.2, 7.25, 0.01), (0.35, 14.0, 0.04), mats['M_MetalGrate'], col, 0.01)
    create_box("Floor_DrainTrench_R", (1.2, 7.25, 0.01), (0.35, 14.0, 0.04), mats['M_MetalGrate'], col, 0.01)
    # Central Directional Floor Brass Runner
    create_box("Floor_GuideStrip", (0.0, 7.25, 0.015), (0.45, 14.0, 0.03), mats['M_BrassHardware'], col, 0.01)

    # 2. Structural Perimeter Walls
    # Outer North Wall (Entrance side): by = 0.0
    # Left wing north wall: bx [-12, -3]
    create_box("Wall_North_Brief", (-7.5, 4.0, 1.8), (9.0, 0.35, 3.6), mats['M_SafetyTeal'], col, 0.04)
    # Right wing north wall: bx [3, 12]
    create_box("Wall_North_Lockers", (7.5, 4.0, 1.8), (9.0, 0.35, 3.6), mats['M_SafetyTeal'], col, 0.04)
    
    # Entrance Portal (North End of Central Hall): by = 0.0, bx [-3, 3]
    create_box("Portal_Entrance_L", (-2.2, 0.0, 1.8), (0.6, 0.6, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Portal_Entrance_R", (2.2, 0.0, 1.8), (0.6, 0.6, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Portal_Entrance_Header", (0.0, 0.0, 3.4), (5.0, 0.6, 0.5), mats['M_WarningOrange'], col, 0.04)
    create_box("Portal_Entrance_Sign", (0.0, -0.25, 3.4), (3.6, 0.1, 0.35), mats['M_HazardYellow'], col, 0.02)
    # Shift Entrance Heavy Blast Door (recessed/open)
    create_box("Door_Entrance_PanelL", (-1.4, 0.15, 1.6), (0.9, 0.15, 3.0), mats['M_CastIron'], col, 0.03)
    create_box("Door_Entrance_PanelR", (1.4, 0.15, 1.6), (0.9, 0.15, 3.0), mats['M_CastIron'], col, 0.03)

    # Outer West Wall (Briefing Back): bx = -12.0, by [4, 13]
    create_box("Wall_West_Main", (-12.0, 8.5, 1.8), (0.4, 9.0, 3.6), mats['M_CastIron'], col, 0.04)
    # Outer East Wall (Locker Back): bx = 12.0, by [4, 13]
    create_box("Wall_East_Main", (12.0, 8.5, 1.8), (0.4, 9.0, 3.6), mats['M_CastIron'], col, 0.04)

    # Outer South Wall (Briefing South): by = 13.0, bx [-12, -3]
    create_box("Wall_South_Brief", (-7.5, 13.0, 1.8), (9.0, 0.35, 3.6), mats['M_SafetyTeal'], col, 0.04)
    # Outer South Wall (Locker South): by = 13.0, bx [3, 12]
    create_box("Wall_South_Lockers", (7.5, 13.0, 1.8), (9.0, 0.35, 3.6), mats['M_SafetyTeal'], col, 0.04)

    # S1 Corridor Transit Portal (South End of Central Hall): by = 14.2, bx [-3, 3]
    create_box("Portal_S1_L", (-2.2, 14.2, 1.8), (0.6, 0.6, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Portal_S1_R", (2.2, 14.2, 1.8), (0.6, 0.6, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Portal_S1_Header", (0.0, 14.2, 3.4), (5.0, 0.6, 0.5), mats['M_WarningOrange'], col, 0.04)
    create_box("Portal_S1_HazardTrim", (0.0, 14.45, 3.4), (3.8, 0.1, 0.35), mats['M_HazardYellow'], col, 0.02)

    # Internal Arched Partitions dividing hallway from wings
    # West Partition Columns & Header (Briefing): bx = -3.0
    create_box("Col_West_N", (-3.0, 4.2, 1.8), (0.5, 0.5, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Col_West_S", (-3.0, 12.8, 1.8), (0.5, 0.5, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Arch_West_Header", (-3.0, 8.5, 3.4), (0.45, 9.0, 0.45), mats['M_SafetyTeal'], col, 0.04)
    
    # East Partition Columns & Header (Lockers): bx = 3.0
    create_box("Col_East_N", (3.0, 4.2, 1.8), (0.5, 0.5, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Col_East_S", (3.0, 12.8, 1.8), (0.5, 0.5, 3.6), mats['M_CastIron'], col, 0.04)
    create_box("Arch_East_Header", (3.0, 8.5, 3.4), (0.45, 9.0, 0.45), mats['M_SafetyTeal'], col, 0.04)

    # 3. Ceiling Arches / Curved Ribs across Hallway
    for y_pos in [2.5, 6.0, 9.5, 13.0]:
        create_box(f"Ceiling_Arch_{y_pos}", (0.0, y_pos, 3.65), (6.2, 0.35, 0.35), mats['M_CastIron'], col, 0.03)
        # Overhead conduit pipe
        create_cylinder(f"Conduit_Hall_{y_pos}", (0.0, y_pos, 3.5), 0.06, 6.0, mats['M_BrassHardware'], col, 12, (0, math.pi/2, 0))

# --- BRIEFING HALL BUILDER ---
def build_briefing_hall(col, mats):
    # 1. Raised Dais Platform: bx [-11.5, -4.5], by [5.5, 11.5], height 0.22
    create_box("Briefing_Dais_Base", (-8.0, 8.5, 0.11), (7.0, 6.0, 0.22), mats['M_ConcreteFloor'], col, 0.03)
    create_box("Briefing_Dais_Trim", (-8.0, 8.5, 0.20), (7.2, 6.2, 0.04), mats['M_WarningOrange'], col, 0.01)
    
    # 2. Hero Master Briefing Screen Wall: bx = -11.2, by = 8.5
    # Backing structure
    create_box("Briefing_ScreenWall_Back", (-11.5, 8.5, 1.8), (0.4, 5.0, 2.8), mats['M_CastIron'], col, 0.04)
    # Frame & Cowl
    create_box("Briefing_Screen_Frame", (-11.2, 8.5, 2.0), (0.3, 4.4, 2.2), mats['M_SafetyTeal'], col, 0.04)
    # CRT Glowing Display
    create_box("Briefing_Screen_CRT", (-11.0, 8.5, 2.0), (0.12, 4.0, 1.8), mats['M_ScreenBriefing'], col, 0.02)
    # Top Status Light Bar
    create_box("Briefing_Screen_StatusTop", (-11.0, 8.5, 3.0), (0.15, 3.6, 0.12), mats['M_HazardYellow'], col, 0.01)

    # 3. Briefing Control Console Deck (in front of screen): bx = -10.4, by = 8.5
    create_box("Briefing_Console_Base", (-10.4, 8.5, 0.65), (0.8, 3.4, 0.9), mats['M_CastIron'], col, 0.03)
    create_box("Briefing_Console_TopSlant", (-10.3, 8.5, 1.15), (0.7, 3.2, 0.12), mats['M_WarningOrange'], col, 0.02)
    # Tactical buttons / switches on console
    for i in range(5):
        y_b = 7.3 + i * 0.6
        create_cylinder(f"Console_Knob_{i}", (-10.15, y_b, 1.25), 0.05, 0.08, mats['M_BrassHardware'], col, 8, (math.pi/4, 0, 0))
        create_box(f"Console_Switch_{i}", (-10.3, y_b, 1.24), (0.08, 0.12, 0.06), mats['M_HazardDark'], col, 0.01)

    # 4. Speaker Podium: bx = -6.8, by = 8.5
    create_box("Podium_Base", (-6.8, 8.5, 0.6), (0.8, 0.8, 0.8), mats['M_CastIron'], col, 0.03)
    create_box("Podium_SlantTop", (-6.8, 8.5, 1.05), (0.85, 0.85, 0.15), mats['M_TreatedWood'], col, 0.02)
    # Gooseneck Mic
    create_cylinder("Podium_MicStem", (-6.6, 8.5, 1.25), 0.015, 0.35, mats['M_BrassHardware'], col, 8, (0.2, 0, 0))
    create_cylinder("Podium_MicHead", (-6.55, 8.5, 1.45), 0.035, 0.08, mats['M_CastIron'], col, 12, (0.2, 0, 0))
    # Clipboard Manifest
    create_box("Podium_Clipboard", (-6.8, 8.5, 1.15), (0.35, 0.45, 0.03), mats['M_HazardYellow'], col, 0.01)

    # 5. Briefing Crew Benches: 3 Rows at bx = -5.2, by = 6.2, 8.5, 10.8
    for row_idx, y_bench in enumerate([6.2, 8.5, 10.8]):
        # Timber Planks
        create_box(f"Bench_Plank_{row_idx}", (-4.8, y_bench, 0.45), (0.55, 2.8, 0.08), mats['M_TreatedWood'], col, 0.02)
        # Cast Iron Legs
        create_box(f"Bench_Leg_L_{row_idx}", (-4.8, y_bench - 1.1, 0.22), (0.45, 0.15, 0.44), mats['M_CastIron'], col, 0.02)
        create_box(f"Bench_Leg_R_{row_idx}", (-4.8, y_bench + 1.1, 0.22), (0.45, 0.15, 0.44), mats['M_CastIron'], col, 0.02)

    # 6. Shift Notice Board: on South wall of briefing hall: by = 12.8, bx = -7.5
    create_box("NoticeBoard_Frame", (-7.5, 12.8, 1.8), (3.2, 0.12, 1.8), mats['M_TreatedWood'], col, 0.03)
    create_box("NoticeBoard_Surface", (-7.5, 12.72, 1.8), (3.0, 0.04, 1.6), mats['M_HazardYellow'], col, 0.01)
    # Pinned duty sheets
    for k in range(3):
        create_box(f"Notice_Sheet_{k}", (-8.3 + k * 0.8, 12.68, 1.8 + (k%2)*0.2), (0.4, 0.02, 0.55), mats['M_ScreenDark'], col, 0.01)

# --- LOCKER ROOM & HERO PPE BUILDER ---
def build_lockers_and_ppe(col, mats):
    # 1. North Locker Bank: by = 12.4, bx [4.2, 10.8] (8 Lockers)
    create_box("LockerBank_North_Frame", (7.5, 12.4, 1.4), (7.0, 0.8, 2.6), mats['M_CastIron'], col, 0.04)
    for i in range(8):
        x_lock = 4.4 + i * 0.88
        is_open = (i == 2 or i == 5)
        # Door or interior
        if not is_open:
            create_box(f"LockerDoor_N_{i}", (x_lock, 12.0, 1.4), (0.8, 0.06, 2.3), mats['M_SafetyTeal'], col, 0.02)
            # Handle & dial
            create_cylinder(f"LockerDial_N_{i}", (x_lock + 0.25, 11.95, 1.4), 0.04, 0.03, mats['M_BrassHardware'], col, 8, (math.pi/2, 0, 0))
            create_box(f"LockerHandle_N_{i}", (x_lock + 0.25, 11.95, 1.2), (0.04, 0.06, 0.25), mats['M_CastIron'], col, 0.01)
            # Number badge
            create_box(f"LockerNum_N_{i}", (x_lock, 11.95, 2.2), (0.22, 0.02, 0.12), mats['M_HazardYellow'], col, 0.01)
        else:
            # Open locker door ajar
            create_box(f"LockerDoorOpen_N_{i}", (x_lock + 0.35, 11.6, 1.4), (0.06, 0.75, 2.3), mats['M_SafetyTeal'], col, 0.02)
            # Shelves inside
            create_box(f"LockerShelf_N_{i}_1", (x_lock, 12.3, 0.8), (0.75, 0.65, 0.04), mats['M_CastIron'], col, 0.01)
            create_box(f"LockerShelf_N_{i}_2", (x_lock, 12.3, 2.1), (0.75, 0.65, 0.04), mats['M_CastIron'], col, 0.01)
            # Thermos / Personal item
            create_cylinder(f"LockerThermos_N_{i}", (x_lock - 0.15, 12.3, 0.95), 0.06, 0.25, mats['M_WarningOrange'], col, 12)

    # 2. Island Locker Bank: by = 7.5, bx [4.2, 10.8] (8 Lockers)
    create_box("LockerBank_Island_Frame", (7.5, 7.5, 1.4), (7.0, 1.0, 2.6), mats['M_CastIron'], col, 0.04)
    for i in range(8):
        x_lock = 4.4 + i * 0.88
        create_box(f"LockerDoor_I_{i}", (x_lock, 7.0, 1.4), (0.8, 0.06, 2.3), mats['M_SafetyTeal'], col, 0.02)
        create_box(f"LockerHandle_I_{i}", (x_lock + 0.25, 6.95, 1.2), (0.04, 0.06, 0.25), mats['M_CastIron'], col, 0.01)
        create_box(f"LockerNum_I_{i}", (x_lock, 6.95, 2.2), (0.22, 0.02, 0.12), mats['M_HazardYellow'], col, 0.01)

    # 3. Dressing Benches between locker banks: by = 9.8, bx [4.5, 10.5]
    create_box("Locker_Bench_Timber", (7.5, 9.8, 0.45), (6.2, 0.55, 0.08), mats['M_TreatedWood'], col, 0.02)
    create_box("Locker_Bench_LegL", (4.8, 9.8, 0.22), (0.15, 0.45, 0.44), mats['M_CastIron'], col, 0.02)
    create_box("Locker_Bench_LegM", (7.5, 9.8, 0.22), (0.15, 0.45, 0.44), mats['M_CastIron'], col, 0.02)
    create_box("Locker_Bench_LegR", (10.2, 9.8, 0.22), (0.15, 0.45, 0.44), mats['M_CastIron'], col, 0.02)

    # 4. Boot Rack & Hero Worker Boots: bx = 3.6, by = 5.2
    create_box("BootRack_Frame", (3.6, 5.2, 0.45), (0.6, 1.8, 0.9), mats['M_CastIron'], col, 0.02)
    for pair_idx in range(4):
        y_boot = 4.5 + pair_idx * 0.45
        # Left Boot
        create_box(f"HeroBoot_L_{pair_idx}", (3.5, y_boot - 0.08, 0.15), (0.32, 0.14, 0.22), mats['M_SuitRubber'], col, 0.02)
        create_box(f"HeroBoot_Toe_L_{pair_idx}", (3.65, y_boot - 0.08, 0.10), (0.12, 0.13, 0.14), mats['M_CastIron'], col, 0.01)
        # Right Boot
        create_box(f"HeroBoot_R_{pair_idx}", (3.5, y_boot + 0.08, 0.15), (0.32, 0.14, 0.22), mats['M_SuitRubber'], col, 0.02)
        create_box(f"HeroBoot_Toe_R_{pair_idx}", (3.65, y_boot + 0.08, 0.10), (0.12, 0.13, 0.14), mats['M_CastIron'], col, 0.01)

    # 5. PPE Suit Hanger Racks with 4 Hero Worker Protective Suits: bx = 11.2, by [5.0, 11.0]
    # Overhead Pipe Rack
    create_cylinder("PPE_Rack_Pipe", (11.2, 8.0, 2.4), 0.05, 6.4, mats['M_CastIron'], col, 12, (math.pi/2, 0, 0))
    create_box("PPE_Rack_PostN", (11.2, 4.8, 1.2), (0.1, 0.1, 2.4), mats['M_CastIron'], col, 0.02)
    create_box("PPE_Rack_PostS", (11.2, 11.2, 1.2), (0.1, 0.1, 2.4), mats['M_CastIron'], col, 0.02)

    # 4 Stylized Hero Suits Hanging
    for s_idx, y_suit in enumerate([5.8, 7.2, 8.8, 10.2]):
        # Hanger hook
        create_cylinder(f"Suit_Hanger_{s_idx}", (11.2, y_suit, 2.3), 0.02, 0.25, mats['M_BrassHardware'], col, 8)
        # Suit Torso (Chunky stylized hazmat body)
        create_box(f"HeroSuit_Torso_{s_idx}", (11.2, y_suit, 1.55), (0.45, 0.55, 0.75), mats['M_SuitFabric'], col, 0.04)
        # Chest Collar Seal
        create_cylinder(f"HeroSuit_Collar_{s_idx}", (11.2, y_suit, 1.95), 0.18, 0.12, mats['M_SuitRubber'], col, 12)
        # Chest Armor / Utility Harness
        create_box(f"HeroSuit_ChestPlate_{s_idx}", (11.0, y_suit, 1.6), (0.1, 0.42, 0.45), mats['M_SafetyTeal'], col, 0.02)
        create_box(f"HeroSuit_Badge_{s_idx}", (10.92, y_suit - 0.12, 1.7), (0.04, 0.12, 0.08), mats['M_HazardYellow'], col, 0.01)
        # Back Life-Support / Scrubber Cannister
        create_box(f"HeroSuit_Backpack_{s_idx}", (11.45, y_suit, 1.55), (0.22, 0.40, 0.55), mats['M_CastIron'], col, 0.03)
        create_cylinder(f"HeroSuit_Filter1_{s_idx}", (11.55, y_suit - 0.1, 1.4), 0.06, 0.22, mats['M_BrassHardware'], col, 10)
        create_cylinder(f"HeroSuit_Filter2_{s_idx}", (11.55, y_suit + 0.1, 1.4), 0.06, 0.22, mats['M_BrassHardware'], col, 10)
        # Hanging Arms (Pleated Sleeves)
        create_box(f"HeroSuit_ArmL_{s_idx}", (11.2, y_suit - 0.35, 1.4), (0.22, 0.18, 0.65), mats['M_SuitFabric'], col, 0.03)
        create_box(f"HeroSuit_GloveL_{s_idx}", (11.2, y_suit - 0.35, 1.0), (0.24, 0.19, 0.20), mats['M_SuitRubber'], col, 0.02)
        create_box(f"HeroSuit_ArmR_{s_idx}", (11.2, y_suit + 0.35, 1.4), (0.22, 0.18, 0.65), mats['M_SuitFabric'], col, 0.03)
        create_box(f"HeroSuit_GloveR_{s_idx}", (11.2, y_suit + 0.35, 1.0), (0.24, 0.19, 0.20), mats['M_SuitRubber'], col, 0.02)
        # Hanging Legs
        create_box(f"HeroSuit_LegL_{s_idx}", (11.2, y_suit - 0.15, 0.75), (0.25, 0.22, 0.8), mats['M_SuitFabric'], col, 0.03)
        create_box(f"HeroSuit_LegR_{s_idx}", (11.2, y_suit + 0.15, 0.75), (0.25, 0.22, 0.8), mats['M_SuitFabric'], col, 0.03)

    # 6. Helmet Shelf with 4 Hero Worker Helmets: bx = 9.8, by = 4.2
    create_box("HelmetShelf_Board", (9.8, 4.2, 1.5), (3.2, 0.45, 0.08), mats['M_CastIron'], col, 0.02)
    for h_idx, x_helm in enumerate([8.6, 9.4, 10.2, 11.0]):
        # Helmet Shell Dome
        create_cylinder(f"HeroHelmet_Dome_{h_idx}", (x_helm, 4.2, 1.75), 0.22, 0.32, mats['M_WarningOrange'], col, 14)
        # Top Roll-Cage Handle
        create_box(f"HeroHelmet_TopHandle_{h_idx}", (x_helm, 4.2, 1.95), (0.05, 0.25, 0.1), mats['M_CastIron'], col, 0.01)
        # Tinted Bubble Visor Glass
        create_box(f"HeroHelmet_Visor_{h_idx}", (x_helm, 4.02, 1.72), (0.28, 0.08, 0.18), mats['M_VisorGlass'], col, 0.02)
        # Dual Cheek Filter Cartridges
        create_cylinder(f"HeroHelmet_FilterL_{h_idx}", (x_helm - 0.22, 4.1, 1.65), 0.07, 0.12, mats['M_CastIron'], col, 10, (0, math.pi/2, 0))
        create_cylinder(f"HeroHelmet_FilterR_{h_idx}", (x_helm + 0.22, 4.1, 1.65), 0.07, 0.12, mats['M_CastIron'], col, 10, (0, math.pi/2, 0))

# --- SUIT INTEGRITY TEST & DECON BUILDER ---
def build_suit_integrity_and_decon(col, mats):
    # Positioned at Unity [MACHINE] SUIT INTEGRITY TEST: bx = 7.30, by = 8.05
    # 1. Octagonal Scan Pedestal
    create_cylinder("Integrity_Pedestal", (7.3, 8.05, 0.12), 1.2, 0.24, mats['M_CastIron'], col, 8)
    create_cylinder("Integrity_ScanRing", (7.3, 8.05, 0.25), 0.95, 0.04, mats['M_LightEmitCyan'], col, 16)
    
    # 2. Vertical Arched Scanner Pylons
    for a_idx, angle in enumerate([math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]):
        px = 7.3 + math.cos(angle) * 1.1
        py = 8.05 + math.sin(angle) * 1.1
        create_box(f"Integrity_Pylon_{a_idx}", (px, py, 1.5), (0.18, 0.18, 2.6), mats['M_SafetyTeal'], col, 0.02)
        # Glowing diagnostic LED strip
        create_box(f"Integrity_LedStrip_{a_idx}", (px * 0.98, py * 0.98, 1.5), (0.06, 0.06, 2.2), mats['M_LightEmitCyan'], col, 0.01)

    # 3. Overhead Circular Scan Ring
    create_cylinder("Integrity_TopRing", (7.3, 8.05, 2.8), 1.15, 0.15, mats['M_CastIron'], col, 16)
    create_cylinder("Integrity_LaserEmitter", (7.3, 8.05, 2.72), 0.9, 0.04, mats['M_LightEmitCyan'], col, 16)

    # 4. Side Diagnostic Touch Console & Umbilical
    create_box("Integrity_Console_Pillar", (5.8, 8.05, 0.6), (0.4, 0.4, 1.2), mats['M_CastIron'], col, 0.02)
    create_box("Integrity_Console_Screen", (5.8, 8.05, 1.25), (0.35, 0.35, 0.15), mats['M_ScreenBriefing'], col, 0.02)
    # Braided pressure hose to chamber
    create_cylinder("Integrity_Hose", (6.5, 8.05, 0.3), 0.04, 1.2, mats['M_SuitRubber'], col, 8, (0, math.pi/2, 0))

    # 5. Wall-Mounted Dosimeter Dispenser Station: bx = 3.4, by = 8.05
    create_box("DosimeterRack_Back", (3.4, 8.05, 1.5), (0.15, 1.4, 1.2), mats['M_CastIron'], col, 0.02)
    create_box("DosimeterRack_Header", (3.35, 8.05, 2.05), (0.1, 1.2, 0.18), mats['M_HazardYellow'], col, 0.01)
    # 8 Dosimeter Pens clipped
    for d_idx in range(6):
        y_dos = 7.55 + d_idx * 0.2
        create_cylinder(f"DosimeterPen_{d_idx}", (3.25, y_dos, 1.5), 0.025, 0.35, mats['M_BrassHardware'], col, 8)
        create_box(f"DosimeterClip_{d_idx}", (3.28, y_dos, 1.62), (0.03, 0.04, 0.06), mats['M_HazardDark'], col, 0.01)

# --- REQUISITION & HERO HARDWARE BUILDER ---
def build_requisition_and_hardware(col, mats):
    # Positioned near South Exit / Requisition: bx [-2.0, 2.0], by = 13.2
    # 1. Heavy Service Counter
    create_box("Req_Counter_Base", (-1.2, 12.8, 0.55), (2.4, 0.8, 1.1), mats['M_CastIron'], col, 0.03)
    create_box("Req_Counter_Top", (-1.2, 12.8, 1.12), (2.6, 0.9, 0.08), mats['M_TreatedWood'], col, 0.02)
    
    # 2. Explosives Storage Cage: bx = -2.2, by = 13.5
    create_box("ExplosiveCage_Frame", (-2.4, 13.4, 1.1), (1.4, 1.2, 2.2), mats['M_CastIron'], col, 0.03)
    create_box("ExplosiveCage_MeshF", (-2.4, 12.82, 1.1), (1.3, 0.04, 2.0), mats['M_MetalGrate'], col, 0.01)
    create_box("ExplosiveCage_HazardTrim", (-2.4, 12.8, 2.15), (1.35, 0.08, 0.2), mats['M_HazardYellow'], col, 0.01)
    # TNT Crates inside
    create_box("TNT_Crate_1", (-2.4, 13.4, 0.35), (0.6, 0.6, 0.45), mats['M_TreatedWood'], col, 0.02)
    create_box("TNT_Crate_Stripe_1", (-2.4, 13.1, 0.35), (0.55, 0.02, 0.2), mats['M_WarningOrange'], col, 0.01)
    create_box("TNT_Crate_2", (-2.4, 13.4, 0.75), (0.5, 0.5, 0.35), mats['M_TreatedWood'], col, 0.02)

    # 3. Hero Geiger Counters (Wall-Mounted): bx = -1.8, by = 14.1
    for g_idx, x_geiger in enumerate([-1.6, 1.6]):
        # Main Canary Yellow Housing
        create_box(f"HeroGeiger_Body_{g_idx}", (x_geiger, 14.1, 1.5), (0.35, 0.16, 0.50), mats['M_GeigerYellow'], col, 0.02)
        # Meter Dial Face
        create_box(f"HeroGeiger_Meter_{g_idx}", (x_geiger, 14.01, 1.62), (0.24, 0.02, 0.18), mats['M_ScreenDark'], col, 0.01)
        # Selector Knob
        create_cylinder(f"HeroGeiger_Knob_{g_idx}", (x_geiger - 0.08, 14.01, 1.38), 0.035, 0.04, mats['M_CastIron'], col, 8, (math.pi/2, 0, 0))
        # Sensor Wand in Side Clip
        create_cylinder(f"HeroGeiger_Wand_{g_idx}", (x_geiger + 0.14, 14.05, 1.5), 0.03, 0.38, mats['M_CastIron'], col, 8)
        create_cylinder(f"HeroGeiger_ProbeTip_{g_idx}", (x_geiger + 0.14, 14.05, 1.7), 0.032, 0.06, mats['M_BrassHardware'], col, 8)
        # Top Carrying Handle
        create_box(f"HeroGeiger_Handle_{g_idx}", (x_geiger, 14.1, 1.78), (0.22, 0.04, 0.08), mats['M_CastIron'], col, 0.01)

    # 4. Tool Crib Shadow Board: bx = 2.0, by = 13.2
    create_box("ToolBoard_Back", (2.0, 13.2, 1.6), (0.1, 1.8, 1.6), mats['M_CastIron'], col, 0.02)
    # Heavy Wrench
    create_box("Tool_Wrench", (1.92, 12.8, 1.6), (0.03, 0.12, 0.65), mats['M_CastIron'], col, 0.01)
    create_cylinder("Tool_WrenchHead", (1.92, 12.8, 1.9), 0.08, 0.03, mats['M_CastIron'], col, 6, (0, math.pi/2, 0))
    # Sledgehammer
    create_cylinder("Tool_HammerHandle", (1.92, 13.4, 1.5), 0.025, 0.8, mats['M_TreatedWood'], col, 8)
    create_box("Tool_HammerHead", (1.92, 13.4, 1.85), (0.12, 0.22, 0.14), mats['M_CastIron'], col, 0.02)

# --- LIGHTING FIXTURES BUILDER ---
def build_lighting_fixtures(col, mats):
    # Caged Industrial Bulkhead Lamps along central corridor
    for l_idx, y_lamp in enumerate([1.5, 5.0, 8.5, 12.0]):
        # Left wall lamp
        create_box(f"Lamp_Base_L_{l_idx}", (-2.85, y_lamp, 2.8), (0.1, 0.25, 0.25), mats['M_CastIron'], col, 0.01)
        create_cylinder(f"Lamp_Bulb_L_{l_idx}", (-2.75, y_lamp, 2.8), 0.08, 0.16, mats['M_LightEmitWarm'], col, 12, (0, math.pi/2, 0))
        create_box(f"Lamp_Cage_L_{l_idx}", (-2.72, y_lamp, 2.8), (0.08, 0.22, 0.22), mats['M_BrassHardware'], col, 0.01)
        # Right wall lamp
        create_box(f"Lamp_Base_R_{l_idx}", (2.85, y_lamp, 2.8), (0.1, 0.25, 0.25), mats['M_CastIron'], col, 0.01)
        create_cylinder(f"Lamp_Bulb_R_{l_idx}", (2.75, y_lamp, 2.8), 0.08, 0.16, mats['M_LightEmitWarm'], col, 12, (0, math.pi/2, 0))
        create_box(f"Lamp_Cage_R_{l_idx}", (2.72, y_lamp, 2.8), (0.08, 0.22, 0.22), mats['M_BrassHardware'], col, 0.01)

    # Overhead Pendant Lamps above Briefing Dais & Lockers
    for p_idx, pos in enumerate([(-8.0, 8.5, 3.4), (7.5, 9.8, 3.4)]):
        create_cylinder(f"Pendant_Shade_{p_idx}", pos, 0.45, 0.25, mats['M_SafetyTeal'], col, 16)
        create_cylinder(f"Pendant_Bulb_{p_idx}", (pos[0], pos[1], pos[2] - 0.08), 0.15, 0.1, mats['M_LightEmitWarm'], col, 12)
        create_cylinder(f"Pendant_Cord_{p_idx}", (pos[0], pos[1], pos[2] + 0.3), 0.02, 0.6, mats['M_CastIron'], col, 8)

    # Flashing Amber Hazard Beacon above Entrance & S1 Portal
    for b_idx, (bx, by, bz) in enumerate([(0.0, 0.15, 3.7), (0.0, 14.05, 3.7)]):
        create_cylinder(f"Beacon_Base_{b_idx}", (bx, by, bz), 0.15, 0.1, mats['M_CastIron'], col, 12)
        create_cylinder(f"Beacon_Dome_{b_idx}", (bx, by, bz + 0.12), 0.12, 0.18, mats['M_WarningOrange'], col, 12)

# --- MASTER RUNNER ---
def run():
    print("Building Critical Shift Stylized Spawn Room...")
    mats = create_palette()
    
    col_name = "01_Production_SpawnRoom"
    # If collection exists, clear old objects
    col = get_or_create_collection(col_name)
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
        
    build_architecture(col, mats)
    build_briefing_hall(col, mats)
    build_lockers_and_ppe(col, mats)
    build_suit_integrity_and_decon(col, mats)
    build_requisition_and_hardware(col, mats)
    build_lighting_fixtures(col, mats)
    
    print(f"Spawn room built successfully with {len(col.objects)} objects in collection '{col_name}'.")
    return {"ok": True, "object_count": len(col.objects), "collection": col_name}

if __name__ == '__main__':
    run()
