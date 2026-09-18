"""Critical Shift Fast Authoring & Optimization System for Blender 5.2 LTS.

Provides four distinct authoring modes:
  1. OVERVIEW / FAST: Entire facility visible via consolidated solid proxies (~33 objects).
  2. FOCUS EDIT: Exactly one area editable with real canonical geometry; remaining 16 areas as proxies.
  3. MATERIAL REVIEW: Evaluated material preview with dynamic distance culling and light culling.
  4. FULL QUALITY: Complete canonical source geometry, collections, lights, and quality settings restored.
"""

bl_info = {
    'name': 'Critical Shift Fast Authoring',
    'author': 'Critical Shift Team',
    'version': (1, 1, 0),
    'blender': (5, 2, 0),
    'location': 'View3D > Sidebar > Critical Shift Authoring',
    'description': 'High-performance fast authoring, focus editing, and material review system',
    'category': '3D View',
}

import bpy
from mathutils import Vector
from bpy.app.handlers import persistent
import numpy as np
import time

# ---------------------------------------------------------------------------
# Section and Collection Mappings
# ---------------------------------------------------------------------------

ROOM_SECTIONS = [
    ('spawn-room', 'Spawn'),
    ('mine', 'Mine'),
    ('refinery', 'Refinery'),
    ('fuel-corridor', 'Fuel Corridor'),
    ('reactor-room', 'Reactor'),
    ('cooling-plant', 'Cooling Plant'),
    ('turbine-room', 'Turbine'),
    ('condenser-bay', 'Condenser'),
    ('electrical-room', 'Electrical'),
    ('waste-storage', 'Waste'),
    ('medical-reanimation', 'Medical'),
    ('compliance-dock', 'Compliance'),
]

ROOM_KEYS = {sid for sid, _ in ROOM_SECTIONS}

ALL_FOCUS_ITEMS = [
    ('spawn-room', 'Spawn', 'Focus edit Spawn Room (real geometry, proxies elsewhere)'),
    ('mine', 'Mine', 'Focus edit Mine / Gullet (real geometry, proxies elsewhere)'),
    ('refinery', 'Refinery', 'Focus edit Refinery Complex (real geometry, proxies elsewhere)'),
    ('fuel-corridor', 'Fuel Corridor', 'Focus edit Fuel Corridor (real geometry, proxies elsewhere)'),
    ('reactor-room', 'Reactor', 'Focus edit Reactor Room (real geometry, proxies elsewhere)'),
    ('cooling-plant', 'Cooling Plant', 'Focus edit Cooling Plant (real geometry, proxies elsewhere)'),
    ('turbine-room', 'Turbine', 'Focus edit Turbine Room (real geometry, proxies elsewhere)'),
    ('condenser-bay', 'Condenser', 'Focus edit Condenser Bay (real geometry, proxies elsewhere)'),
    ('electrical-room', 'Electrical', 'Focus edit Electrical Room (real geometry, proxies elsewhere)'),
    ('waste-storage', 'Waste', 'Focus edit Waste Storage (real geometry, proxies elsewhere)'),
    ('medical-reanimation', 'Medical', 'Focus edit Medical Reanimation (real geometry, proxies elsewhere)'),
    ('compliance-dock', 'Compliance', 'Focus edit Compliance Dock (real geometry, proxies elsewhere)'),
    ('connections', 'Connections', 'Focus edit Horizontal Connections & Courtyard'),
    ('access', 'Vertical Access / Access', 'Focus edit Vertical Access & Stairs'),
    ('exterior', 'Exterior / Terrain', 'Focus edit Terrain, Perimeter & Exterior Work'),
    ('roof_services', 'Roof Services', 'Focus edit Roof Services & Machinery'),
    ('network', 'Network / Facility Infrastructure', 'Focus edit Network Scenery & Pipeways'),
]

SYSTEM_CACHE_PAIRS = [
    ('23_EXTERIOR_FINISH_VIEWPORT_CACHE', '22_EXTERIOR_FINISH_GEOMETRY'),
    ('21_ROOF_SERVICE_VIEWPORT_CACHE', '20_ROOF_SERVICE_GEOMETRY'),
    ('14_ACCESS_FINISH_VIEWPORT_CACHE', '13_FINISHED_ACCESS_SCENERY'),
    ('16_NETWORK_FINISH_VIEWPORT_CACHE', '15_FINISHED_NETWORK_SCENERY'),
    ('18_REACTOR_FINISH_VIEWPORT_CACHE', '17_REACTOR_EXTERIOR_FINISH'),
    ('10_NETWORK_VIEWPORT_CACHE', '09_FINISHED_HORIZONTAL_CONNECTIONS'),
]

GUIDE_COLLECTIONS = [
    '02_UNBUILT_CONNECTION_RESERVATIONS',
    '03_RESERVED_VOLUMES',
    '04_PLANNING_LABELS',
]

# Track objects hidden dynamically in Material Review distance culling
_mr_hidden_objects = set()
_keys = []

# ---------------------------------------------------------------------------
# Core State Application Helpers
# ---------------------------------------------------------------------------

def set_collection_visibility(col_name, visible, render_visible=None):
    col = bpy.data.collections.get(col_name)
    if col:
        col.hide_viewport = not visible
        if render_visible is not None:
            col.hide_render = not render_visible

def set_object_visibility(obj_name, visible, render_visible=None):
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.hide_viewport = not visible
        obj.hide_set(not visible)
        if render_visible is not None:
            obj.hide_render = not render_visible

# ---------------------------------------------------------------------------
# Mode 1: OVERVIEW / FAST
# ---------------------------------------------------------------------------

def apply_overview_mode(scene):
    """Overview / Fast mode: lightweight proxies for entire facility, sources hidden."""
    # Ensure proxies collection is visible
    set_collection_visibility('07_FAST_WALKTHROUGH_PROXIES', True, render_visible=False)
    proxy_col = bpy.data.collections.get('07_FAST_WALKTHROUGH_PROXIES')
    if proxy_col:
        for ob in proxy_col.objects:
            if ob.name != 'WALK_PROXY_CONNECTIONS_ALL_ROUTES_GREYBOX':
                ob.hide_viewport = False
                ob.hide_set(False)

    # Enable all system caches
    for cache_name, _ in SYSTEM_CACHE_PAIRS:
        set_collection_visibility(cache_name, True, render_visible=False)

    # Keep continuous floor visible
    set_collection_visibility('08_WHOLE_MAP_FLOOR', True)

    # Hide all source rooms and exteriors
    set_collection_visibility('01_LINKED_ROOMS', False)
    set_collection_visibility('06_LINKED_EXTERIORS', False)

    # Hide all system sources
    for _, source_name in SYSTEM_CACHE_PAIRS:
        set_collection_visibility(source_name, False)
    set_collection_visibility('CONNECTION_C01_RESCUE_COURTYARD', False)
    set_collection_visibility('11_ACCESS_ARCHITECTURE', False)
    set_collection_visibility('12_ACCESS_MOVING_PARTS', False)
    set_collection_visibility('24_EXTERIOR_PRACTICAL_LIGHTS', False)
    set_collection_visibility('25_MINE_REFINERY_IDENTITIES', False)
    set_collection_visibility('26_FINE_PLANTING', False)
    set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', False)
    set_collection_visibility('30_RETAINED_INTERIOR_LIGHTING', False)
    set_collection_visibility('31_DISTANT_EXTERIOR_BACKDROP', False)
    set_collection_visibility('32_SPAWN_BAKED_DAYLIGHT', False)

    # Hide material preview collections
    set_collection_visibility('27_MATERIAL_PREVIEW', False, render_visible=False)
    set_collection_visibility('28_MATERIAL_PREVIEW_LIGHTS', False, render_visible=False)

    # Guides
    for gname in GUIDE_COLLECTIONS:
        set_collection_visibility(gname, scene.authoring_show_guides)

    # Viewport defaults for Overview
    configure_viewport(shading_type='SOLID', overlays=scene.authoring_show_overlays)

# ---------------------------------------------------------------------------
# Mode 2: FOCUS EDIT
# ---------------------------------------------------------------------------

def apply_focus_edit_mode(scene):
    """Focus Edit mode: ONE real editable area + lightweight proxies everywhere else."""
    focus = scene.authoring_focus_area

    # Material preview collections stay hidden
    set_collection_visibility('27_MATERIAL_PREVIEW', False, render_visible=False)
    set_collection_visibility('28_MATERIAL_PREVIEW_LIGHTS', False, render_visible=False)

    # Proxies collection is enabled globally
    set_collection_visibility('07_FAST_WALKTHROUGH_PROXIES', True, render_visible=False)
    set_collection_visibility('08_WHOLE_MAP_FLOOR', True)

    if focus in ROOM_KEYS:
        # Focused area is a room module
        # 1. 01_LINKED_ROOMS is visible, but ONLY the focused room object is unhidden
        set_collection_visibility('01_LINKED_ROOMS', True)
        rooms_col = bpy.data.collections.get('01_LINKED_ROOMS')
        if rooms_col:
            for ob in rooms_col.objects:
                is_target = (ob.name == focus)
                ob.hide_viewport = not is_target
                ob.hide_set(not is_target)

        # 2. 06_LINKED_EXTERIORS is visible, but ONLY the focused exterior object is unhidden
        ext_target_name = f'EXTERIOR_INSTANCE_{focus}'
        set_collection_visibility('06_LINKED_EXTERIORS', True)
        ext_col = bpy.data.collections.get('06_LINKED_EXTERIORS')
        if ext_col:
            for ob in ext_col.objects:
                is_target = (ob.name == ext_target_name)
                ob.hide_viewport = not is_target
                ob.hide_set(not is_target)

        # 3. In 07_FAST_WALKTHROUGH_PROXIES:
        # HIDE proxy for focused room and its exterior; SHOW proxies for all other rooms & exteriors
        proxy_col = bpy.data.collections.get('07_FAST_WALKTHROUGH_PROXIES')
        target_room_proxy = f'WALK_PROXY_{focus}'
        target_ext_proxy = f'WALK_PROXY_{ext_target_name}'
        if proxy_col:
            for ob in proxy_col.objects:
                if ob.name in (target_room_proxy, target_ext_proxy, 'WALK_PROXY_CONNECTIONS_ALL_ROUTES_GREYBOX'):
                    ob.hide_viewport = True
                    ob.hide_set(True)
                else:
                    ob.hide_viewport = False
                    ob.hide_set(False)

        # 4. System caches: all system caches are ACTIVE; system sources HIDDEN
        for cache_name, source_name in SYSTEM_CACHE_PAIRS:
            set_collection_visibility(cache_name, True, render_visible=False)
            set_collection_visibility(source_name, False)

        set_collection_visibility('CONNECTION_C01_RESCUE_COURTYARD', False)
        set_collection_visibility('11_ACCESS_ARCHITECTURE', False)
        set_collection_visibility('12_ACCESS_MOVING_PARTS', False)
        set_collection_visibility('25_MINE_REFINERY_IDENTITIES', focus in ('mine', 'refinery'))
        set_collection_visibility('26_FINE_PLANTING', False)
        set_collection_visibility('31_DISTANT_EXTERIOR_BACKDROP', True)

        # Room-specific extras
        if focus == 'spawn-room':
            set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', True)
            set_collection_visibility('32_SPAWN_BAKED_DAYLIGHT', True)
        else:
            set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', False)
            set_collection_visibility('32_SPAWN_BAKED_DAYLIGHT', False)

        if focus == 'reactor-room':
            set_collection_visibility('17_REACTOR_EXTERIOR_FINISH', True)
            set_collection_visibility('18_REACTOR_FINISH_VIEWPORT_CACHE', False)

        # 5. Local light management for focused room
        manage_focus_lights(scene, focus)

    else:
        # Focused area is a facility system
        # All 12 rooms use PROXIES; real rooms and exteriors are hidden
        set_collection_visibility('01_LINKED_ROOMS', False)
        set_collection_visibility('06_LINKED_EXTERIORS', False)

        proxy_col = bpy.data.collections.get('07_FAST_WALKTHROUGH_PROXIES')
        if proxy_col:
            for ob in proxy_col.objects:
                if ob.name != 'WALK_PROXY_CONNECTIONS_ALL_ROUTES_GREYBOX':
                    ob.hide_viewport = False
                    ob.hide_set(False)

        # Set default state: all system caches on, sources off
        for cache_name, source_name in SYSTEM_CACHE_PAIRS:
            set_collection_visibility(cache_name, True, render_visible=False)
            set_collection_visibility(source_name, False)

        set_collection_visibility('CONNECTION_C01_RESCUE_COURTYARD', False)
        set_collection_visibility('11_ACCESS_ARCHITECTURE', False)
        set_collection_visibility('12_ACCESS_MOVING_PARTS', False)
        set_collection_visibility('24_EXTERIOR_PRACTICAL_LIGHTS', False)
        set_collection_visibility('25_MINE_REFINERY_IDENTITIES', False)
        set_collection_visibility('26_FINE_PLANTING', False)
        set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', False)
        set_collection_visibility('30_RETAINED_INTERIOR_LIGHTING', False)
        set_collection_visibility('31_DISTANT_EXTERIOR_BACKDROP', True)
        set_collection_visibility('32_SPAWN_BAKED_DAYLIGHT', False)

        if focus == 'connections':
            # Real horizontal connections & courtyard ON, cache OFF
            set_collection_visibility('09_FINISHED_HORIZONTAL_CONNECTIONS', True)
            set_collection_visibility('CONNECTION_C01_RESCUE_COURTYARD', True)
            set_collection_visibility('10_NETWORK_VIEWPORT_CACHE', False)
            set_object_visibility('WALK_PROXY_CONNECTION_C01_RESCUE_COURTYARD', False)

        elif focus == 'access':
            # Real vertical access architecture, parts, scenery ON, cache OFF
            set_collection_visibility('11_ACCESS_ARCHITECTURE', True)
            set_collection_visibility('12_ACCESS_MOVING_PARTS', True)
            set_collection_visibility('13_FINISHED_ACCESS_SCENERY', True)
            set_collection_visibility('14_ACCESS_FINISH_VIEWPORT_CACHE', False)

        elif focus == 'exterior':
            # Real exterior finish, terrain, backdrop ON, cache OFF
            set_collection_visibility('22_EXTERIOR_FINISH_GEOMETRY', True)
            set_collection_visibility('23_EXTERIOR_FINISH_VIEWPORT_CACHE', False)
            set_collection_visibility('06_LINKED_EXTERIORS', True)
            ext_col = bpy.data.collections.get('06_LINKED_EXTERIORS')
            if ext_col:
                for ob in ext_col.objects:
                    ob.hide_viewport = False
                    ob.hide_set(False)
            if proxy_col:
                for ob in proxy_col.objects:
                    if ob.name.startswith('WALK_PROXY_EXTERIOR_INSTANCE_'):
                        ob.hide_viewport = True
                        ob.hide_set(True)
            set_collection_visibility('24_EXTERIOR_PRACTICAL_LIGHTS', True)
            set_collection_visibility('25_MINE_REFINERY_IDENTITIES', True)
            set_collection_visibility('26_FINE_PLANTING', True)
            set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', True)
            set_collection_visibility('17_REACTOR_EXTERIOR_FINISH', True)
            set_collection_visibility('18_REACTOR_FINISH_VIEWPORT_CACHE', False)

        elif focus == 'roof_services':
            # Real roof services ON, cache OFF
            set_collection_visibility('20_ROOF_SERVICE_GEOMETRY', True)
            set_collection_visibility('21_ROOF_SERVICE_VIEWPORT_CACHE', False)

        elif focus == 'network':
            # Real network scenery ON, cache OFF
            set_collection_visibility('15_FINISHED_NETWORK_SCENERY', True)
            set_collection_visibility('16_NETWORK_FINISH_VIEWPORT_CACHE', False)

    # Guides
    for gname in GUIDE_COLLECTIONS:
        set_collection_visibility(gname, scene.authoring_show_guides)

    # Viewport defaults for Focus Edit
    configure_viewport(shading_type='SOLID', overlays=scene.authoring_show_overlays)

def manage_focus_lights(scene, focus_room):
    """Enable only relevant lights for the focused section; suppress distant practicals."""
    # Retained interior lights (300 lights)
    int_col = bpy.data.collections.get('30_RETAINED_INTERIOR_LIGHTING')
    if int_col:
        if focus_room == 'spawn-room':
            int_col.hide_viewport = False
            for ob in int_col.objects:
                if ob.type == 'LIGHT':
                    ob.hide_viewport = False
                    ob.hide_set(False)
        else:
            int_col.hide_viewport = True

    # Exterior practical lights (20 lights)
    ext_lights_col = bpy.data.collections.get('24_EXTERIOR_PRACTICAL_LIGHTS')
    if ext_lights_col:
        ext_lights_col.hide_viewport = False
        prefix = f"{focus_room} "
        for ob in ext_lights_col.objects:
            if ob.type == 'LIGHT':
                is_local = ob.name.startswith(prefix)
                ob.hide_viewport = not (is_local or scene.authoring_nearby_lights)
                ob.hide_set(not (is_local or scene.authoring_nearby_lights))

# ---------------------------------------------------------------------------
# Mode 3: MATERIAL REVIEW
# ---------------------------------------------------------------------------

def apply_material_review_mode(scene):
    """Material Review: evaluated preview geometry + EEVEE settings + dynamic distance culling."""
    # Hide all source rooms and exteriors
    set_collection_visibility('01_LINKED_ROOMS', False)
    set_collection_visibility('06_LINKED_EXTERIORS', False)

    # Hide all solid proxies & system caches
    set_collection_visibility('07_FAST_WALKTHROUGH_PROXIES', False, render_visible=False)
    for cache_name, source_name in SYSTEM_CACHE_PAIRS:
        set_collection_visibility(cache_name, False, render_visible=False)
        set_collection_visibility(source_name, False)

    set_collection_visibility('CONNECTION_C01_RESCUE_COURTYARD', False)
    set_collection_visibility('08_WHOLE_MAP_FLOOR', False)
    set_collection_visibility('11_ACCESS_ARCHITECTURE', False)
    set_collection_visibility('12_ACCESS_MOVING_PARTS', False)
    set_collection_visibility('24_EXTERIOR_PRACTICAL_LIGHTS', False)
    set_collection_visibility('25_MINE_REFINERY_IDENTITIES', False)
    set_collection_visibility('26_FINE_PLANTING', False)
    set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', False)
    set_collection_visibility('30_RETAINED_INTERIOR_LIGHTING', False)
    set_collection_visibility('31_DISTANT_EXTERIOR_BACKDROP', False)
    set_collection_visibility('32_SPAWN_BAKED_DAYLIGHT', False)

    # Enable material preview collections
    set_collection_visibility('27_MATERIAL_PREVIEW', True, render_visible=True)
    set_collection_visibility('28_MATERIAL_PREVIEW_LIGHTS', True, render_visible=True)

    # Lightweight EEVEE configuration
    scene.render.engine = 'BLENDER_EEVEE'
    eevee = scene.eevee
    eevee.use_raytracing = False
    eevee.use_fast_gi = False
    eevee.taa_samples = 8
    eevee.shadow_pool_size = '2048'
    eevee.shadow_resolution_scale = 0.5
    eevee.use_shadow_jitter_viewport = False

    # Configure viewport to Rendered shading
    configure_viewport(shading_type='RENDERED', overlays=scene.authoring_show_overlays)

    # Trigger distance culling update
    material_review_tick()

# ---------------------------------------------------------------------------
# Mode 4: FULL QUALITY
# ---------------------------------------------------------------------------

def apply_full_quality_mode(scene):
    """Full Quality mode: canonical original geometry, collections, lights, and EEVEE settings."""
    # Restore distance culling hidden objects
    restore_mr_hidden()

    # Hide all proxies and caches
    set_collection_visibility('07_FAST_WALKTHROUGH_PROXIES', False, render_visible=False)
    for cache_name, _ in SYSTEM_CACHE_PAIRS:
        set_collection_visibility(cache_name, False, render_visible=False)

    set_collection_visibility('27_MATERIAL_PREVIEW', False, render_visible=False)
    set_collection_visibility('28_MATERIAL_PREVIEW_LIGHTS', False, render_visible=False)

    # Unhide all 12 rooms and their objects
    set_collection_visibility('01_LINKED_ROOMS', True, render_visible=True)
    rooms_col = bpy.data.collections.get('01_LINKED_ROOMS')
    if rooms_col:
        for ob in rooms_col.objects:
            ob.hide_viewport = False
            ob.hide_set(False)

    # Unhide all 12 exteriors and their objects
    set_collection_visibility('06_LINKED_EXTERIORS', True, render_visible=True)
    ext_col = bpy.data.collections.get('06_LINKED_EXTERIORS')
    if ext_col:
        for ob in ext_col.objects:
            ob.hide_viewport = False
            ob.hide_set(False)

    # Unhide all canonical source collections
    for _, source_name in SYSTEM_CACHE_PAIRS:
        set_collection_visibility(source_name, True, render_visible=True)

    set_collection_visibility('CONNECTION_C01_RESCUE_COURTYARD', True, render_visible=True)
    set_collection_visibility('08_WHOLE_MAP_FLOOR', True, render_visible=True)
    set_collection_visibility('11_ACCESS_ARCHITECTURE', True, render_visible=True)
    set_collection_visibility('12_ACCESS_MOVING_PARTS', True, render_visible=True)
    set_collection_visibility('24_EXTERIOR_PRACTICAL_LIGHTS', True, render_visible=True)
    set_collection_visibility('25_MINE_REFINERY_IDENTITIES', True, render_visible=True)
    set_collection_visibility('26_FINE_PLANTING', True, render_visible=True)
    set_collection_visibility('29_SPAWN_APPROVED_EXTERIOR', True, render_visible=True)
    set_collection_visibility('30_RETAINED_INTERIOR_LIGHTING', True, render_visible=True)
    set_collection_visibility('31_DISTANT_EXTERIOR_BACKDROP', True, render_visible=True)
    set_collection_visibility('32_SPAWN_BAKED_DAYLIGHT', True, render_visible=True)

    # Ensure all objects in 30_RETAINED_INTERIOR_LIGHTING and 24_EXTERIOR_PRACTICAL_LIGHTS are unhidden
    int_col = bpy.data.collections.get('30_RETAINED_INTERIOR_LIGHTING')
    if int_col:
        for ob in int_col.objects:
            ob.hide_viewport = False
            ob.hide_set(False)

    ext_lights = bpy.data.collections.get('24_EXTERIOR_PRACTICAL_LIGHTS')
    if ext_lights:
        for ob in ext_lights.objects:
            ob.hide_viewport = False
            ob.hide_set(False)

    # Guides
    for gname in GUIDE_COLLECTIONS:
        set_collection_visibility(gname, scene.authoring_show_guides)

    # Restore canonical EEVEE quality settings
    scene.render.engine = 'BLENDER_EEVEE'
    eevee = scene.eevee
    eevee.use_raytracing = False
    eevee.use_fast_gi = False
    eevee.taa_render_samples = 256
    eevee.taa_samples = 64
    eevee.shadow_pool_size = '2048'
    eevee.shadow_ray_count = 4
    eevee.shadow_step_count = 12
    eevee.use_shadow_jitter_viewport = True
    eevee.shadow_resolution_scale = 1.0

    # Viewport overlays
    configure_viewport(overlays=True)

# ---------------------------------------------------------------------------
# Viewport Configuration Helpers
# ---------------------------------------------------------------------------

def configure_viewport(shading_type=None, overlays=None):
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if shading_type is not None:
                    space.shading.type = shading_type
                    if shading_type == 'SOLID':
                        space.shading.color_type = 'MATERIAL'
                        space.shading.light = 'STUDIO'
                        space.shading.show_shadows = False
                        space.shading.show_cavity = False
                if overlays is not None:
                    space.overlay.show_overlays = overlays
                space.clip_start = 0.05
                space.clip_end = 1000.0

# ---------------------------------------------------------------------------
# Distance Culling Engine (Material Review)
# ---------------------------------------------------------------------------
_mr_hidden_objects = set()
is_benchmarking = False

def restore_mr_hidden():
    for name in list(_mr_hidden_objects):
        ob = bpy.data.objects.get(name)
        if ob:
            ob.hide_viewport = False
            ob.hide_set(False)
    _mr_hidden_objects.clear()

def material_review_tick():
    try:
        if is_benchmarking:
            return 1.0
        scene = bpy.context.scene
        if scene.authoring_mode != 'MATERIAL_REVIEW':
            if _mr_hidden_objects:
                restore_mr_hidden()
            return 1.0

        if not scene.authoring_auto_cull:
            if _mr_hidden_objects:
                restore_mr_hidden()
            return 1.0

        eyes = []
        ortho = False
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    r = area.spaces.active.region_3d
                    ortho |= (r.view_perspective != 'PERSP')
                    eyes.append(r.view_location + r.view_rotation @ Vector((0, 0, r.view_distance)))

        if not eyes or ortho:
            restore_mr_hidden()
            return 0.5

        col27 = bpy.data.collections.get('27_MATERIAL_PREVIEW')
        room_distance = {}
        if col27:
            for ob in col27.objects:
                source = ob.get('preview_source')
                if source not in ROOM_KEYS:
                    continue
                pts = [ob.matrix_world @ Vector(v) for v in ob.bound_box]
                lo = [min(p[i] for p in pts) for i in range(3)]
                hi = [max(p[i] for p in pts) for i in range(3)]
                near = min(sum(max(lo[i] - e[i], 0, e[i] - hi[i]) ** 2 for i in range(3)) for e in eyes)
                room_distance[source] = near
                if source == 'mine':
                    continue
                # Hysteresis threshold: 12m if currently hidden, 17m if visible
                is_currently_hidden = ob.name in _mr_hidden_objects
                thresh = (12 if is_currently_hidden else 17) ** 2
                should_hide = near > thresh
                if should_hide:
                    if not is_currently_hidden:
                        ob.hide_viewport = True
                        ob.hide_set(True)
                        _mr_hidden_objects.add(ob.name)
                else:
                    if is_currently_hidden:
                        ob.hide_viewport = False
                        ob.hide_set(False)
                        _mr_hidden_objects.discard(ob.name)

        col28 = bpy.data.collections.get('28_MATERIAL_PREVIEW_LIGHTS')
        if col28:
            for ob in col28.objects:
                if ob.type != 'LIGHT' or ob.data.type == 'SUN':
                    continue
                loc = ob.matrix_world.translation
                near_light = min((loc - e).length_squared for e in eyes)
                should_hide = near_light > 28 ** 2
                lib_path = ob.data.library.filepath.replace('\\', '/') if ob.data.library else ''
                if '/sources/' in lib_path:
                    sid = lib_path.split('/sources/')[1].split('/')[0]
                    should_hide |= (room_distance.get(sid, 0) > 5 ** 2)

                is_hidden = ob.name in _mr_hidden_objects
                if should_hide:
                    if not is_hidden:
                        ob.hide_viewport = True
                        ob.hide_set(True)
                        _mr_hidden_objects.add(ob.name)
                else:
                    if is_hidden:
                        ob.hide_viewport = False
                        ob.hide_set(False)
                        _mr_hidden_objects.discard(ob.name)

    except Exception:
        pass
    return 1.5

# ---------------------------------------------------------------------------
# Dispatch & Update Callbacks
# ---------------------------------------------------------------------------

def update_authoring_state(self, context):
    scene = context.scene
    mode = scene.authoring_mode
    if mode == 'OVERVIEW':
        apply_overview_mode(scene)
    elif mode == 'FOCUS_EDIT':
        apply_focus_edit_mode(scene)
    elif mode == 'MATERIAL_REVIEW':
        apply_material_review_mode(scene)
    elif mode == 'FULL_QUALITY':
        apply_full_quality_mode(scene)

def update_focus_area(self, context):
    scene = context.scene
    if scene.authoring_mode == 'FOCUS_EDIT':
        apply_focus_edit_mode(scene)

def update_guides(self, context):
    scene = context.scene
    for gname in GUIDE_COLLECTIONS:
        set_collection_visibility(gname, scene.authoring_show_guides)

def update_overlays(self, context):
    configure_viewport(overlays=context.scene.authoring_show_overlays)

# ---------------------------------------------------------------------------
# Cache Operations & Partial Rebuilding
# ---------------------------------------------------------------------------

def rebuild_single_proxy(scene, section_name):
    """Rebuilds evaluated consolidated proxy mesh for a single section."""
    proxy_col = bpy.data.collections.get('07_FAST_WALKTHROUGH_PROXIES')
    if not proxy_col:
        return False

    dg = bpy.context.evaluated_depsgraph_get()
    items = []
    for inst in dg.object_instances:
        if not inst.show_self or inst.object.type not in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            continue
        parent = inst.parent.name if inst.parent else ''
        if parent == section_name:
            items.append((inst.object.original, inst.matrix_world.copy()))

    if not items:
        return False

    chunks = []
    materials = []
    material_map = {}
    nv = nl = nf = 0

    for original, matrix in items:
        obj = original.evaluated_get(dg)
        mesh = obj.to_mesh(preserve_all_data_layers=False, depsgraph=dg)
        if not mesh or not mesh.polygons:
            obj.to_mesh_clear()
            continue

        v = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get('co', v)
        v = v.reshape(-1, 3)
        m = np.asarray(matrix, dtype=np.float32)
        v = v @ m[:3, :3].T + m[:3, 3]

        loop = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', loop)
        starts = np.empty(len(mesh.polygons), dtype=np.int32)
        mesh.polygons.foreach_get('loop_start', starts)
        totals = np.empty(len(mesh.polygons), dtype=np.int32)
        mesh.polygons.foreach_get('loop_total', totals)
        mi = np.empty(len(mesh.polygons), dtype=np.int32)
        mesh.polygons.foreach_get('material_index', mi)
        smooth = np.empty(len(mesh.polygons), dtype=np.bool_)
        mesh.polygons.foreach_get('use_smooth', smooth)

        mapping = []
        for slot in obj.material_slots:
            mat = slot.material
            key = mat.as_pointer() if mat else 0
            if key not in material_map:
                material_map[key] = len(materials)
                materials.append(mat)
            mapping.append(material_map[key])
        if not mapping:
            if 0 not in material_map:
                material_map[0] = len(materials)
                materials.append(None)
            mapping = [material_map[0]]
        mi = np.asarray(mapping, dtype=np.int32)[np.minimum(mi, len(mapping) - 1)]

        if np.linalg.det(m[:3, :3]) < 0:
            for start, total in zip(starts, totals):
                loop[start:start + total] = loop[start:start + total][::-1]

        chunks.append((v, loop + nv, starts + nl, totals, mi, smooth))
        nv += len(v)
        nl += len(loop)
        nf += len(starts)
        obj.to_mesh_clear()

    mesh_name = f'WALK_MESH_{section_name}'
    proxy_name = f'WALK_PROXY_{section_name}'
    existing_ob = bpy.data.objects.get(proxy_name)
    if existing_ob:
        mesh = existing_ob.data
        mesh.clear_geometry()
    else:
        mesh = bpy.data.meshes.new(mesh_name)
        existing_ob = bpy.data.objects.new(proxy_name, mesh)
        proxy_col.objects.link(existing_ob)

    mesh.vertices.add(nv)
    mesh.loops.add(nl)
    mesh.polygons.add(nf)
    mesh.vertices.foreach_set('co', np.concatenate([c[0] for c in chunks]).ravel())
    mesh.loops.foreach_set('vertex_index', np.concatenate([c[1] for c in chunks]))
    mesh.polygons.foreach_set('loop_start', np.concatenate([c[2] for c in chunks]))
    mesh.polygons.foreach_set('loop_total', np.concatenate([c[3] for c in chunks]))
    mesh.materials.clear()
    for mat in materials:
        mesh.materials.append(mat)
    mesh.polygons.foreach_set('material_index', np.concatenate([c[4] for c in chunks]))
    mesh.polygons.foreach_set('use_smooth', np.concatenate([c[5] for c in chunks]))
    mesh.update(calc_edges=True)
    existing_ob.hide_render = True
    existing_ob['source_instance'] = section_name
    return True

# ---------------------------------------------------------------------------
# UI Operators
# ---------------------------------------------------------------------------

class CRITICALSHIFT_OT_set_mode(bpy.types.Operator):
    bl_idname = 'critical_shift.set_mode'
    bl_label = 'Set Authoring Mode'
    bl_description = 'Switch facility authoring mode'
    mode: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.authoring_mode = self.mode
        return {'FINISHED'}

class CRITICALSHIFT_OT_reload_libraries(bpy.types.Operator):
    bl_idname = 'critical_shift.reload_libraries'
    bl_label = 'Reload Linked Sources'
    bl_description = 'Reload all linked Blender library modules from disk'

    def execute(self, context):
        reloaded = 0
        for lib in bpy.data.libraries:
            try:
                lib.reload()
                reloaded += 1
            except Exception as e:
                print(f"Failed to reload library {lib.name}: {e}")
        bpy.context.view_layer.update()
        self.report({'INFO'}, f"Reloaded {reloaded} linked libraries")
        update_authoring_state(None, context)
        return {'FINISHED'}

class CRITICALSHIFT_OT_rebuild_focus_proxy(bpy.types.Operator):
    bl_idname = 'critical_shift.rebuild_focus_proxy'
    bl_label = 'Rebuild Focus Proxy'
    bl_description = 'Rebuild evaluated solid proxy mesh for the currently selected focus area'

    def execute(self, context):
        focus = context.scene.authoring_focus_area
        if focus not in ROOM_KEYS:
            self.report({'WARNING'}, f"Partial proxy rebuilding supported for room sections (current: {focus})")
            return {'CANCELLED'}
        set_collection_visibility('01_LINKED_ROOMS', True)
        set_object_visibility(focus, True)
        bpy.context.view_layer.update()
        success = rebuild_single_proxy(context.scene, focus)
        update_authoring_state(None, context)
        if success:
            self.report({'INFO'}, f"Rebuilt solid proxy for {focus}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Could not rebuild proxy for {focus}")
            return {'CANCELLED'}

class CRITICALSHIFT_OT_restore_full_quality(bpy.types.Operator):
    bl_idname = 'critical_shift.restore_full_quality'
    bl_label = 'Restore Full Quality'
    bl_description = 'Restore all canonical original geometry, collections, lights, and quality settings'

    def execute(self, context):
        context.scene.authoring_mode = 'FULL_QUALITY'
        self.report({'INFO'}, "Restored canonical Full Quality state")
        return {'FINISHED'}

class CRITICALSHIFT_OT_benchmark_redraw(bpy.types.Operator):
    bl_idname = 'critical_shift.benchmark_redraw'
    bl_label = 'Benchmark Viewport Redraw'
    bl_description = 'Measure actual 30-frame viewport redraw performance in current mode'

    def execute(self, context):
        frames = 30
        start = time.perf_counter()
        for _ in range(frames):
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        elapsed = time.perf_counter() - start
        fps = frames / elapsed if elapsed > 0 else 0
        context.scene['last_benchmark_fps'] = round(fps, 1)
        self.report({'INFO'}, f"Viewport Redraw: {fps:.1f} FPS ({frames} frames in {elapsed:.3f}s)")
        return {'FINISHED'}

# ---------------------------------------------------------------------------
# N-Panel UI
# ---------------------------------------------------------------------------

class CRITICALSHIFT_PT_authoring(bpy.types.Panel):
    bl_label = 'Critical Shift Authoring'
    bl_idname = 'CRITICALSHIFT_PT_authoring'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Critical Shift Authoring'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # --- MODE SELECTOR ---
        box = layout.box()
        box.label(text="Authoring Mode:", icon='SCENE_DATA')
        row = box.row(align=True)
        for m_id, m_label, m_icon in [
            ('OVERVIEW', 'Overview', 'VIEW_PAN'),
            ('FOCUS_EDIT', 'Focus Edit', 'EDITMODE_HLT'),
            ('MATERIAL_REVIEW', 'Materials', 'SHADING_RENDERED'),
            ('FULL_QUALITY', 'Full Quality', 'COLOR'),
        ]:
            col = row.column(align=True)
            if scene.authoring_mode == m_id:
                col.alert = True
            props = col.operator('critical_shift.set_mode', text=m_label, icon=m_icon)
            props.mode = m_id

        # Mode description / warning
        if scene.authoring_mode == 'FULL_QUALITY':
            alert_box = layout.box()
            alert_box.alert = True
            alert_box.label(text="WARNING: FULL QUALITY MAY BE SLOW (~2-5 FPS)", icon='ERROR')
        elif scene.authoring_mode == 'OVERVIEW':
            box.label(text="Fast map navigation via lightweight proxies (60+ FPS)")
        elif scene.authoring_mode == 'FOCUS_EDIT':
            box.label(text="1 real editable area + lightweight proxies everywhere else")
        elif scene.authoring_mode == 'MATERIAL_REVIEW':
            box.label(text="Evaluated material cache + camera distance culling")

        # --- FOCUS AREA SELECTION ---
        if scene.authoring_mode == 'FOCUS_EDIT':
            fbox = layout.box()
            fbox.label(text="Active Focus Area:", icon='OBJECT_DATA')
            fbox.prop(scene, 'authoring_focus_area', text="")

        # --- DISPLAY & LIGHT OPTIONS ---
        obox = layout.box()
        obox.label(text="Display & Performance Options:", icon='PREFERENCES')
        col = obox.column(align=True)
        col.prop(scene, 'authoring_show_guides', text="Show Reserved Guides")
        col.prop(scene, 'authoring_show_overlays', text="Show 3D Viewport Overlays")
        if scene.authoring_mode == 'FOCUS_EDIT':
            col.prop(scene, 'authoring_nearby_lights', text="Enable Nearby Lights")
        if scene.authoring_mode == 'MATERIAL_REVIEW':
            col.prop(scene, 'authoring_auto_cull', text="Auto-Cull Distant Geometry")

        # --- ACTIONS ---
        abox = layout.box()
        abox.label(text="Authoring Actions:", icon='TOOL_SETTINGS')
        col = abox.column(align=True)
        col.operator('critical_shift.reload_libraries', icon='FILE_REFRESH')
        if scene.authoring_mode == 'FOCUS_EDIT':
            col.operator('critical_shift.rebuild_focus_proxy', icon='MOD_SIMPLIFY')
        if scene.authoring_mode != 'FULL_QUALITY':
            col.operator('critical_shift.restore_full_quality', icon='CHECKMARK')

        # --- PERFORMANCE / STATS READOUT ---
        sbox = layout.box()
        sbox.label(text="Performance & State:", icon='INFO')
        sbox.label(text=f"Current Mode: {scene.authoring_mode}")
        if scene.authoring_mode == 'FOCUS_EDIT':
            sbox.label(text=f"Focused Area: {scene.authoring_focus_area}")

        # Compute visible counts safely
        vis_sources = 0
        vis_proxies = 0
        vis_lights = 0
        try:
            rooms_col = bpy.data.collections.get('01_LINKED_ROOMS')
            if rooms_col and not rooms_col.hide_viewport:
                vis_sources += sum(1 for o in rooms_col.objects if not o.hide_viewport and not o.hide_get())
            proxy_col = bpy.data.collections.get('07_FAST_WALKTHROUGH_PROXIES')
            if proxy_col and not proxy_col.hide_viewport:
                vis_proxies += sum(1 for o in proxy_col.objects if not o.hide_viewport and not o.hide_get())
            for o in scene.objects:
                if o.type == 'LIGHT' and not o.hide_viewport and not o.hide_get():
                    vis_lights += 1
        except Exception:
            pass

        row = sbox.row()
        row.label(text=f"Visible Sources: {vis_sources}")
        row.label(text=f"Proxies: {vis_proxies}")
        sbox.label(text=f"Active Scene Lights: {vis_lights}")

        # Benchmark operator & result
        row = sbox.row(align=True)
        row.operator('critical_shift.benchmark_redraw', text="Benchmark Viewport Redraw", icon='TIME')
        if 'last_benchmark_fps' in scene:
            row.label(text=f"{scene['last_benchmark_fps']} FPS")

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

@persistent
def on_save_pre(dummy):
    """Restore temporary states before saving to prevent corrupting saved state."""
    restore_mr_hidden()

@persistent
def on_load_post(dummy):
    """On load, initialize authoring system safely and apply default mode."""
    bpy.context.preferences.inputs.walk_navigation.use_gravity = False
    scene = bpy.context.scene
    if hasattr(scene, 'authoring_mode'):
        apply_overview_mode(scene)
    if not bpy.app.timers.is_registered(material_review_tick):
        bpy.app.timers.register(material_review_tick, persistent=True)

# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = [
    CRITICALSHIFT_OT_set_mode,
    CRITICALSHIFT_OT_reload_libraries,
    CRITICALSHIFT_OT_rebuild_focus_proxy,
    CRITICALSHIFT_OT_restore_full_quality,
    CRITICALSHIFT_OT_benchmark_redraw,
    CRITICALSHIFT_PT_authoring,
]

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass

    bpy.types.Scene.authoring_mode = bpy.props.EnumProperty(
        name="Authoring Mode",
        items=[
            ('OVERVIEW', 'Overview / Fast', 'Fast navigation via lightweight proxies'),
            ('FOCUS_EDIT', 'Focus Edit', 'Single editable area with surrounding proxies'),
            ('MATERIAL_REVIEW', 'Material Review', 'Real material inspection with distance culling'),
            ('FULL_QUALITY', 'Full Quality', 'Restore canonical full scene (may be slow)'),
        ],
        default='OVERVIEW',
        update=update_authoring_state,
    )

    bpy.types.Scene.authoring_focus_area = bpy.props.EnumProperty(
        name="Focus Area",
        items=ALL_FOCUS_ITEMS,
        default='spawn-room',
        update=update_focus_area,
    )

    bpy.types.Scene.authoring_show_guides = bpy.props.BoolProperty(
        name="Show Reserved Guides",
        default=False,
        update=update_guides,
    )

    bpy.types.Scene.authoring_show_overlays = bpy.props.BoolProperty(
        name="Show Viewport Overlays",
        default=False,
        update=update_overlays,
    )

    bpy.types.Scene.authoring_nearby_lights = bpy.props.BoolProperty(
        name="Nearby Lights",
        default=True,
        update=update_focus_area,
    )

    bpy.types.Scene.authoring_auto_cull = bpy.props.BoolProperty(
        name="Auto-Cull Distant Geometry",
        default=True,
    )

    if on_save_pre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(on_save_pre)
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)
    if not bpy.app.timers.is_registered(material_review_tick):
        bpy.app.timers.register(material_review_tick, persistent=True)

def unregister():
    if bpy.app.timers.is_registered(material_review_tick):
        bpy.app.timers.unregister(material_review_tick)
    if on_save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(on_save_pre)
    if on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post)

    try:
        del bpy.types.Scene.authoring_mode
        del bpy.types.Scene.authoring_focus_area
        del bpy.types.Scene.authoring_show_guides
        del bpy.types.Scene.authoring_show_overlays
        del bpy.types.Scene.authoring_nearby_lights
        del bpy.types.Scene.authoring_auto_cull
    except Exception:
        pass

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass

if __name__ == '__main__':
    register()
