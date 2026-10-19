"""Condenser bay finish A3: A2 (Codex, PR #107) plus authored wear, reachable controls and the map-level headroom fix.

    blender -b --factory-startup module_aaa_A2.blend --python condenser_finish_A3.py [-- --out module_aaa_A3.blend]

Owner, 2026-10-19: "Rework the room to your liking, build into the main map ... Fix everything needed to make this scene perfect."
A2 answered the palette ("more machine colour") but reads factory-new: flat paint, near-white walls, no sign of use. Its independent review
rejected it on reach (rubric hard gate 8) and on the gallery headroom under the map's squeezed roof. A3 keeps every A2 material and object
and adds, in this file only:
  * wear where use explains it (design/ART_DIRECTION.md section 9): grime at the floor line and in cavities, weeps under flanges and valves,
    oil at the pump bases, paint touch-ups on the shell, scuffs on the impact dado and column feet, low-frequency tonal variation on large
    painted fields, and slightly darker, warmer mineral walls with per-panel variation;
  * reachable controls: chain-wheel operators on the two overhead CW isolation valves, the trip button moved to a raised housing at the desk's
    front edge, a "CD ISOL" switch on the operator panel for the condenser isolation, and extension spindles bringing both waterbox vent
    wheels within reach of the gallery. The INTERACT_* anchors move to the new grips.
The headroom is fixed in the map, not here: build_compact_map.py lowers the bay 0.3 m so its own roof fits under the turbine floor unsquashed.

Localized wear needs positions that stay put when the module is linked into the map and when the map is baked, so every mesh that receives
it carries its module-space vertex positions as the attribute `A3_pos` (single-user meshes only; shared fastener meshes and curves keep the
A2 material, plus the attribute-free layers).
"""
import bpy, bmesh, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix, Euler

HERE = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = Path(args[args.index('--out') + 1]).resolve() if '--out' in args else HERE / 'module_aaa_A3.blend'
assert Path(bpy.data.filepath).name == 'module_aaa_A2.blend', 'open module_aaa_A2.blend (the A2 output), not %s' % bpy.data.filepath
SC = bpy.context.scene
RECEIPT = {'source': 'module_aaa_A2.blend', 'source_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(), 'changes': []}
def note(kind, **kw): RECEIPT['changes'].append(dict(kind=kind, **kw)); print('A3', kind, kw if len(str(kw)) < 300 else str(kw)[:300], flush=True)

ATTR = 'A3_pos'
WEAR_MATERIALS = ['A2 machine blue enamel', 'A2 waterbox oxide enamel', 'A2 hotwell graphite blue', 'Astra ivory painted steel', 'Structural painted steel',
                  'Charcoal impact dado', 'Oxide orange enamel', 'Light oxide enamel', 'Warm mineral plaster', 'Dense cast concrete',
                  'Basement coated concrete', 'Replacement floor patch']

# ---------------------------------------------------------------------------------------------------------------------------------------------
# Module-space positions
# ---------------------------------------------------------------------------------------------------------------------------------------------
def users_of(names):
    """(object, slot index) for every mesh slot using one of `names`."""
    out = []
    for o in SC.objects:
        if o.type != 'MESH': continue
        for i, s in enumerate(o.material_slots):
            if s.material and s.material.name in names: out.append((o, i))
    return out

def add_positions():
    n = shared = 0
    for o in {o for o, _ in users_of(set(WEAR_MATERIALS))}:
        if o.data.users > 1: shared += 1; continue
        if ATTR in o.data.attributes: o.data.attributes.remove(o.data.attributes[ATTR])
        a = o.data.attributes.new(ATTR, 'FLOAT_VECTOR', 'POINT')
        M = o.matrix_world; co = [c for v in o.data.vertices for c in (M @ v.co)]
        a.data.foreach_set('vector', co); n += 1
    note('module_positions', meshes=n, shared_meshes_skipped=shared, attribute=ATTR)

# ---------------------------------------------------------------------------------------------------------------------------------------------
# Shader building blocks
# ---------------------------------------------------------------------------------------------------------------------------------------------
class Wear:
    """Adds wear layers in front of an existing Principled BSDF's base colour and roughness."""
    def __init__(self, mat, positional):
        self.nt = mat.node_tree; self.positional = positional
        self.bs = next(n for n in self.nt.nodes if n.type == 'BSDF_PRINCIPLED')
        self.base = self.socket_or_value(self.bs.inputs['Base Color'])
        self.rough = self.socket_or_value(self.bs.inputs['Roughness'])
        self._pos = None
    def node(self, kind, label, **kw):
        n = self.nt.nodes.new(kind); n.label = 'A3 | ' + label
        for k, v in kw.items(): setattr(n, k, v)
        return n
    def socket_or_value(self, inp):
        if inp.links: return inp.links[0].from_socket
        v = inp.default_value
        n = self.node('ShaderNodeRGB' if inp.type == 'RGBA' else 'ShaderNodeValue', 'A2 constant')
        n.outputs[0].default_value = tuple(v) if inp.type == 'RGBA' else v
        return n.outputs[0]
    def math(self, op, a, b=0.0, clamp=False):
        n = self.node('ShaderNodeMath', op, operation=op, use_clamp=clamp)
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: self.nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    def vmath(self, op, a, b=None):
        n = self.node('ShaderNodeVectorMath', op, operation=op)
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (tuple, list)): n.inputs[i].default_value = x
            else: self.nt.links.new(x, n.inputs[i])
        return n.outputs['Value'] if op in ('LENGTH', 'DOT_PRODUCT', 'DISTANCE') else n.outputs['Vector']
    def ramp(self, x, a, b, lo=0.0, hi=1.0):
        """Smoothstep from a to b (a may exceed b for a falling edge)."""
        n = self.node('ShaderNodeMapRange', 'smoothstep', interpolation_type='SMOOTHSTEP', clamp=True)
        n.inputs['From Min'].default_value = a; n.inputs['From Max'].default_value = b
        n.inputs['To Min'].default_value = lo; n.inputs['To Max'].default_value = hi
        self.nt.links.new(x, n.inputs['Value']); return n.outputs['Result']
    def pos(self):
        """Module-space position: the A3_pos attribute (positional materials) or the world position (others; only used for soft noise)."""
        if self._pos is None:
            if self.positional:
                a = self.node('ShaderNodeAttribute', 'module position (A3_pos)', attribute_type='GEOMETRY', attribute_name=ATTR); v = a.outputs['Vector']
            else:
                v = self.node('ShaderNodeNewGeometry', 'world position').outputs['Position']
            s = self.node('ShaderNodeSeparateXYZ', 'module x y z'); self.nt.links.new(v, s.inputs[0]); self._pos = (v, s)
        return self._pos
    def noise(self, scale, detail=3.0, stretch=(1, 1, 1), rough=0.55):
        v, _ = self.pos()
        if stretch != (1, 1, 1): v = self.vmath('MULTIPLY', v, stretch)
        n = self.node('ShaderNodeTexNoise', 'breakup %.2f/m' % scale)
        n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = detail; n.inputs['Roughness'].default_value = rough
        self.nt.links.new(v, n.inputs['Vector']); return n.outputs['Fac']
    # --- masks ---
    def ao_grime(self, distance, power, gain):
        ao = self.node('ShaderNodeAmbientOcclusion', 'cavity grime (AO %.2f m)' % distance, samples=8)
        ao.inputs['Distance'].default_value = distance
        return self.math('MULTIPLY', self.math('POWER', self.math('SUBTRACT', 1.0, ao.outputs['AO']), power), gain, True)
    def floor_line(self, height, gain):
        _, s = self.pos()
        m = self.ramp(s.outputs['Z'], height, 0.0)
        return self.math('MULTIPLY', self.math('MULTIPLY', m, self.ramp(self.noise(3.5), 0.3, 0.7, 0.55, 1.0)), gain, True)
    def weeps(self, sources, gain):
        """Vertical weep streaks below points (x, y, z_top, half_width, length): strongest just below the source, fading downwards."""
        _, s = self.pos(); total = None
        streak = self.ramp(self.noise(24.0, 2.0, (1, 1, 0.08)), 0.35, 0.75, 0.35, 1.0)
        for x, y, z, w, l in sources:
            dx = self.math('SUBTRACT', s.outputs['X'], x); dy = self.math('SUBTRACT', s.outputs['Y'], y)
            r = self.math('SQRT', self.math('ADD', self.math('MULTIPLY', dx, dx), self.math('MULTIPLY', dy, dy)))
            m = self.math('MULTIPLY', self.ramp(r, w, w * 0.25), self.ramp(s.outputs['Z'], z - l, z - 0.02))
            m = self.math('MULTIPLY', m, self.ramp(s.outputs['Z'], z + 0.01, z - 0.03))
            total = m if total is None else self.math('MAXIMUM', total, m)
        return self.math('MULTIPLY', self.math('MULTIPLY', total, streak), gain, True)
    def spots(self, circles, gain):
        """Floor stains: (x, y, radius)."""
        _, s = self.pos(); total = None
        edge = self.ramp(self.noise(6.0, 4.0), 0.25, 0.75, 0.6, 1.0)
        for x, y, rad in circles:
            dx = self.math('SUBTRACT', s.outputs['X'], x); dy = self.math('SUBTRACT', s.outputs['Y'], y)
            r = self.math('SQRT', self.math('ADD', self.math('MULTIPLY', dx, dx), self.math('MULTIPLY', dy, dy)))
            m = self.ramp(r, rad, rad * 0.35)
            total = m if total is None else self.math('MAXIMUM', total, m)
        return self.math('MULTIPLY', self.math('MULTIPLY', total, edge), gain, True)
    def boxes(self, rects, gain):
        """Axis-aligned module-space boxes ((x0, x1), (y0, y1), (z0, z1)) with a soft, broken edge."""
        _, s = self.pos(); total = None
        for (x0, x1), (y0, y1), (z0, z1) in rects:
            m = None
            for ax, lo, hi in (('X', x0, x1), ('Y', y0, y1), ('Z', z0, z1)):
                e = 0.012 if hi - lo > 0.05 else 0.002
                k = self.math('MULTIPLY', self.ramp(s.outputs[ax], lo - e, lo + e), self.ramp(s.outputs[ax], hi + e, hi - e))
                m = k if m is None else self.math('MULTIPLY', m, k)
            total = m if total is None else self.math('MAXIMUM', total, m)
        return self.math('MULTIPLY', self.math('MULTIPLY', total, self.ramp(self.noise(18.0, 2.0), 0.2, 0.45, 0.0, 1.0)), gain, True)
    def edges(self, radius, threshold, density_scale, density_cut):
        """Chipped paint on hard edges: the bevel normal departs from the face normal near an edge; broken up so only some edge lengths chip."""
        bev = self.node('ShaderNodeBevel', 'edge (bevel %.3f m)' % radius, samples=4); bev.inputs['Radius'].default_value = radius
        geo = self.node('ShaderNodeNewGeometry', 'face normal')
        d = self.vmath('DOT_PRODUCT', bev.outputs['Normal'], geo.outputs['Normal'])
        e = self.ramp(self.math('SUBTRACT', 1.0, d), threshold * 0.5, threshold)
        brk = self.ramp(self.noise(density_scale, 4.0, rough=0.6), density_cut, density_cut + 0.06)
        return self.math('MULTIPLY', e, brk, True)
    def tone(self, scale, amount):
        """Low-frequency value variation: 1 +- amount."""
        return self.math('ADD', 1.0 - amount, self.math('MULTIPLY', self.noise(scale, 2.0), 2 * amount))
    # --- apply ---
    def mix(self, base, factor, color, blend='MULTIPLY'):
        n = self.node('ShaderNodeMixRGB', 'wear ' + blend.lower(), blend_type=blend, use_clamp=True)
        if isinstance(factor, (int, float)): n.inputs['Fac'].default_value = factor
        else: self.nt.links.new(factor, n.inputs['Fac'])
        self.nt.links.new(base, n.inputs['Color1'])
        if isinstance(color, (tuple, list)): n.inputs['Color2'].default_value = (*color, 1.0)
        else: self.nt.links.new(color, n.inputs['Color2'])
        return n.outputs['Color']
    def grey(self, value):
        c = self.node('ShaderNodeCombineColor', 'grey')
        for i in range(3): self.nt.links.new(value, c.inputs[i])
        return c.outputs['Color']
    def finish(self, base, rough):
        self.nt.links.new(base, self.bs.inputs['Base Color']); self.nt.links.new(rough, self.bs.inputs['Roughness'])

# Measured sources (module metres) for localized wear. Chosen from the room's objects; see finish-A3-build.json.
WEEPS_MACHINE = [(0.60, 3.60, 2.27, 0.05, 0.42), (0.60, 4.50, 2.27, 0.04, 0.42),       # under the west waterbox cover's lower bolts, down its red face (z 1.85..2.27)
                 (5.40, 3.75, 2.27, 0.05, 0.42), (5.40, 4.35, 2.27, 0.04, 0.42)]       # the same on the east waterbox
WEEPS_WALL = [(9.84, 3.2, 3.0, 0.10, 1.6), (9.84, 4.9, 3.0, 0.10, 1.4),                # east wall under the CW isolation valves' wall brackets
              (-2.04, 7.6, 2.6, 0.08, 1.2), (4.9, 9.5, 4.2, 0.12, 2.2)]                # west wall under the ejector discharge, north wall under a penetration
FLOOR_OIL = [(2.57, 6.6, 0.42), (4.27, 7.75, 0.38), (3.2, 4.05, 0.32)]                 # pump bases and under the hotwell drain
FLOOR_WET = [(8.55, 3.2, 0.22), (8.55, 4.9, 0.18), (8.95, 7.6, 0.30)]                  # under the CW isolation valves; at the trench drain
TOUCH_UPS = [((1.55, 2.15), (2.7, 3.7), (2.05, 2.55)), ((4.15, 4.6), (2.7, 3.7), (3.62, 3.98))]   # fresher paint on the shell's south flank (clear of the CD-01 stencil)
DADO_SCUFFS = [((-1.85, -1.7), (0.0, 2.2), (0.10, 0.45)), ((-1.8, 9.6), (9.3, 9.45), (0.10, 0.45)), ((9.5, 9.65), (1.4, 7.0), (0.10, 0.45))]   # where trolleys and boots hit

def wear_pass():
    for name in WEAR_MATERIALS:
        src = bpy.data.materials.get(name)
        if src is None: note('wear_skipped', material=name, why='not in A2'); continue
        mesh_users = [(o, i) for o, i in users_of({name}) if o.data.users == 1]
        if not mesh_users: continue
        mat = src.copy(); mat.name = name + ' | A3 wear'
        build(mat, name, positional=True)
        for o, i in mesh_users:
            o.material_slots[i].link = 'OBJECT'; o.material_slots[i].material = mat
        # shared meshes and curves keep the A2 material, given the attribute-free part of the same treatment
        build(src, name, positional=False)
        note('wear', material=name, positional_users=len(mesh_users))

def build(mat, name, positional):
    w = Wear(mat, positional); base, rough = w.base, w.rough
    painted = name not in ('Warm mineral plaster', 'Dense cast concrete', 'Basement coated concrete', 'Replacement floor patch')
    if painted:
        cav = w.ao_grime(0.22, 1.4, 0.70)
        base = w.mix(base, cav, (0.36, 0.34, 0.31))                                                  # cavities and contact shadows collect grime
        if name not in ('Structural painted steel', 'Charcoal impact dado'):
            chips = w.edges(0.006, 0.18, 9.0, 0.58)                                                  # worn paint on hard edges, broken up: some lengths only
            base = w.mix(base, chips, (0.30, 0.31, 0.32), 'MIX'); rough = w.math('ADD', rough, w.math('MULTIPLY', chips, 0.18))
        if name in ('A2 machine blue enamel', 'A2 waterbox oxide enamel'):
            base = w.mix(base, 1.0, w.grey(w.tone(0.6, 0.06)))                                       # low-frequency paint tone, +-6 %
        nz = w.node('ShaderNodeSeparateXYZ', 'world normal'); w.nt.links.new(w.node('ShaderNodeNewGeometry', 'normal').outputs['Normal'], nz.inputs[0])
        dust = w.math('MULTIPLY', w.math('MULTIPLY', w.ramp(nz.outputs['Z'], 0.55, 0.92), w.ramp(w.noise(2.2, 3.0), 0.3, 0.8, 0.4, 1.0)), 0.22, True)
        base = w.mix(base, dust, (0.50, 0.49, 0.46), 'MIX'); rough = w.math('ADD', rough, w.math('MULTIPLY', dust, 0.25))     # settled dust on tops
        if positional:
            base = w.mix(base, w.floor_line(0.6, 0.85), (0.40, 0.36, 0.31))                        # splash and boot grime at machine bases
            if name in ('A2 machine blue enamel', 'A2 waterbox oxide enamel', 'A2 hotwell graphite blue', 'Oxide orange enamel', 'Light oxide enamel'):
                weep = w.weeps(WEEPS_MACHINE, 0.75)
                base = w.mix(base, weep, (0.55, 0.36, 0.22)); rough = w.math('ADD', rough, w.math('MULTIPLY', weep, 0.12))
            if name == 'A2 machine blue enamel':
                tu = w.boxes(TOUCH_UPS, 1.0); base = w.mix(base, tu, (1.10, 1.08, 1.12)); rough = w.math('SUBTRACT', rough, w.math('MULTIPLY', tu, 0.08))
            if name in ('Charcoal impact dado', 'Structural painted steel'):
                zone = w.boxes(DADO_SCUFFS, 1.0) if name == 'Charcoal impact dado' else w.ramp(w.pos()[1].outputs['Z'], 0.35, 0.08)
                chip = w.math('MULTIPLY', zone, w.ramp(w.noise(7.0, 2.0, rough=0.4), 0.70, 0.74), True)            # few, larger chips
                base = w.mix(base, chip, (0.27, 0.28, 0.29), 'MIX'); rough = w.math('ADD', rough, w.math('MULTIPLY', chip, 0.15))   # grey primer showing
        rough = w.math('ADD', rough, w.math('MULTIPLY', cav, 0.10))
    else:
        if name in ('Warm mineral plaster', 'Dense cast concrete'):
            base = w.mix(base, 1.0, (0.78, 0.77, 0.74))                                               # slightly darker, warmer mineral: A2's walls read near-white
            if positional:
                _, s = w.pos()
                panel = w.node('ShaderNodeTexWhiteNoise', 'per-panel tone (1.5 x 3 m formwork)', noise_dimensions='3D')
                cell = w.vmath('FLOOR', w.vmath('MULTIPLY', w.pos()[0], (1 / 1.5, 1 / 1.5, 1 / 3.0)))
                w.nt.links.new(cell, panel.inputs['Vector'])
                base = w.mix(base, 1.0, w.grey(w.math('ADD', 0.93, w.math('MULTIPLY', panel.outputs['Value'], 0.14))))      # +-7 % per formwork panel
                runs = w.math('MULTIPLY', w.ramp(w.noise(3.0, 2.0, (1, 1, 0.12)), 0.58, 0.72), w.ramp(s.outputs['Z'], 1.2, 4.5), True)   # faint water marks from above
                base = w.mix(base, w.math('MULTIPLY', runs, 0.35), (0.70, 0.67, 0.62))
                base = w.mix(base, w.floor_line(0.55, 0.9), (0.46, 0.42, 0.36))
                weep = w.weeps(WEEPS_WALL, 0.6); base = w.mix(base, weep, (0.62, 0.58, 0.52))
            base = w.mix(base, w.ao_grime(0.3, 1.4, 0.5), (0.55, 0.53, 0.50))
        else:   # floor
            if positional:
                oil = w.spots(FLOOR_OIL, 0.85); wet = w.spots(FLOOR_WET, 0.7)
                base = w.mix(base, oil, (0.45, 0.43, 0.40)); base = w.mix(base, wet, (0.72, 0.72, 0.72))
                rough = w.math('SUBTRACT', rough, w.math('ADD', w.math('MULTIPLY', oil, 0.22), w.math('MULTIPLY', wet, 0.30)))
            base = w.mix(base, w.ao_grime(0.35, 1.3, 0.6), (0.50, 0.48, 0.45))
    w.finish(base, rough)

# ---------------------------------------------------------------------------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------------------------------------------------------------------------
COLL = bpy.data.collections.new('17 A3 access fixes')
MODULE = next(c for c in bpy.data.collections if c.name == 'MODULE_condenser-bay')
MODULE.children.link(COLL)
M = lambda n: bpy.data.materials[n]

def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); COLL.objects.link(o); return o
def box(name, c, size, mat, rot=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if rot: bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=rot, verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts); return mesh_obj(name, bm, mat)
def cylinder(name, a, b, r, mat, seg=16):
    a, b = Vector(a), Vector(b); d = b - a; bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix()
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=q, verts=bm.verts); bmesh.ops.translate(bm, vec=(a + b) / 2, verts=bm.verts)
    return mesh_obj(name, bm, mat)
def torus(name, c, normal, R, r, mat, seg=24, ring=6):
    bm = bmesh.new()
    for i in range(seg):
        u = 2 * math.pi * i / seg
        for j in range(ring):
            v = 2 * math.pi * j / ring
            bm.verts.new(((R + r * math.cos(v)) * math.cos(u), (R + r * math.cos(v)) * math.sin(u), r * math.sin(v)))
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(ring):
            a = i * ring + j; b = ((i + 1) % seg) * ring + j; c2 = ((i + 1) % seg) * ring + (j + 1) % ring; d = i * ring + (j + 1) % ring
            bm.faces.new((bm.verts[a], bm.verts[b], bm.verts[c2], bm.verts[d]))
    q = Vector((0, 0, 1)).rotation_difference(Vector(normal).normalized()).to_matrix()
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=q, verts=bm.verts); bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    return mesh_obj(name, bm, mat)
def chain(name, top, bottom_z, mat, pitch=0.045):
    """A galvanized chain strand: links alternating between the two vertical planes, as one mesh."""
    bm = bmesh.new(); top = Vector(top); n = int((top.z - bottom_z) / pitch)
    for i in range(n):
        z = top.z - (i + 0.5) * pitch; t = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=(0.012, 0.004, pitch * 0.6) if i % 2 else (0.004, 0.012, pitch * 0.6), verts=t)
        bmesh.ops.translate(bm, vec=(top.x, top.y, z), verts=t)
    return mesh_obj(name, bm, mat)
def clear_down(x, y, z_top, z_bottom, ignore=()):
    """True when a vertical line at (x, y) from z_top down to z_bottom meets no geometry (rays down from just below z_top)."""
    dg = bpy.context.evaluated_depsgraph_get(); o = Vector((x, y, z_top - 0.01))
    for dx, dy in ((0, 0), (0.015, 0), (-0.015, 0), (0, 0.015), (0, -0.015)):
        hit, loc, _, _, ob, _ = SC.ray_cast(dg, o + Vector((dx, dy, 0)), Vector((0, 0, -1)), distance=z_top - z_bottom)
        if hit and ob.name not in ignore: return False, ob.name
    return True, None

def move_anchor(name, loc):
    a = SC.objects.get(name)
    if a is None: note('anchor_missing', anchor=name); return
    old = tuple(round(v, 3) for v in a.matrix_world.translation); a.location = loc
    note('anchor_moved', anchor=name, old=old, new=tuple(round(v, 3) for v in loc))

# ---------------------------------------------------------------------------------------------------------------------------------------------
# Reach fixes
# ---------------------------------------------------------------------------------------------------------------------------------------------
def chain_operators():
    """Overhead CW isolation globes (handwheels at 3.4 m, flat on top): a bevel-gear chain-wheel operator on each stem and a chain loop to hand
    height, dropped on whichever side of the valve is clear to the floor."""
    gear, steel, yellow, galv = M('Structural painted steel'), M('Astra brushed fastener steel'), M('Service ochre enamel'), M('Astra brushed fastener steel')
    for tag, y in (('SUPPLY', 3.2), ('RETURN', 4.9)):
        x0, z_hub = 8.55, 3.44
        gb = box('A3 CW isol %s chain gearbox' % tag, (x0, y, z_hub + 0.06), (0.11, 0.11, 0.10), gear)
        chosen = None
        for d in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            wx, wy = x0 + d[0] * 0.22, y + d[1] * 0.22                          # wheel 0.22 m out on its shaft: strands 0.26 m from the stem, clear of the 0.17 m handwheel
            tang = Vector((d[1], d[0], 0))
            strands = [(wx + tang.x * 0.13, wy + tang.y * 0.13), (wx - tang.x * 0.13, wy - tang.y * 0.13)]
            ok = all(clear_down(sx, sy, z_hub + 0.04, 1.0)[0] for sx, sy in strands)
            if ok: chosen = (d, wx, wy, tang, strands); break
        if chosen is None: note('chain_blocked', valve=tag); continue
        d, wx, wy, tang, strands = chosen; wc = Vector((wx, wy, z_hub + 0.06))
        shaft = cylinder('A3 CW isol %s chain wheel shaft' % tag, (x0, y, wc.z), wc, 0.018, steel, 12)
        rim = torus('A3 CW isol %s chain wheel' % tag, wc, (d[0], d[1], 0), 0.13, 0.011, yellow)
        for k in range(3):
            a = 2 * math.pi * k / 3; off = tang * math.cos(a) * 0.12 + Vector((0, 0, 1)) * math.sin(a) * 0.12
            cylinder('A3 CW isol %s chain wheel spoke %d' % (tag, k), wc, wc + off, 0.008, yellow, 8)
        low = 1.05
        for k, (sx, sy) in enumerate(strands):
            chain('A3 CW isol %s chain %s' % (tag, 'AB'[k]), (sx, sy, wc.z - 0.005), low + 0.06, galv)
        cylinder('A3 CW isol %s chain loop bottom' % tag, (strands[0][0], strands[0][1], low + 0.06), (strands[1][0], strands[1][1], low + 0.06), 0.008, galv, 8)
        tag_plate = box('A3 CW isol %s chain tag' % tag, (strands[0][0], strands[0][1], 1.55), (0.006 if d[0] else 0.07, 0.07 if d[0] else 0.006, 0.045), yellow)
        move_anchor('INTERACT_CW_ISOL_%s' % tag[0], (sum(s[0] for s in strands) / 2, sum(s[1] for s in strands) / 2, low + 0.12))
        note('chain_operator', valve=tag, wheel_centre=[round(v, 3) for v in wc], side=d, grip_z=low + 0.06)

def desk_station():
    """Two controls the operator could not reach: the trip mushroom sat on the panel face just above the desk's back edge (0.75 m from a
    standing operator), and INTERACT_CD_ISOLATE floated inside the west waterbox at 3.17 m with no control at all. The panel's selector row
    (LOCAL, CW ISOLATE, CEP SELECT, VACUUM at 0.32 m pitch) is full, so both go on a raised desk-front control housing in the operator's hand
    zone: the trip mushroom (the original parts, turned to face up) and a CD ISOL selector for the motor-operated condenser isolation, with
    a printed legend on the housing's front. The trip's old hole on the panel gets a blanking plate."""
    yellow, red, dark, steel = M('Service ochre enamel'), M('Emergency red enamel'), M('Charcoal impact dado'), M('Structural painted steel')
    hx, y0, y1, top = -0.80, 3.98, 4.26, 1.07
    box('A3 desk control housing', (hx, (y0 + y1) / 2, 0.97 + (top - 0.97) / 2), (0.12, y1 - y0, top - 0.97), yellow)
    box('A3 desk control housing top plate', (hx, (y0 + y1) / 2, top - 0.006), (0.124, y1 - y0 + 0.004, 0.012), dark)
    pivot = Vector((-1.38, 4.05, 1.12)); R = Matrix.Rotation(-math.pi / 2, 4, 'Y')       # rotates +x (out of the panel face) to +z (up)
    moved = []
    for n in ('OP trip stem', 'OP trip mushroom', 'OP trip bezel'):
        o = SC.objects.get(n)
        if o is None: continue
        o.matrix_world = Matrix.Translation((hx, 4.05, top)) @ R @ Matrix.Translation(-pivot) @ o.matrix_world
        moved.append(n)
    box('A3 trip blanking plate', (-1.335, 4.05, 1.12), (0.008, 0.07, 0.07), steel)
    cylinder('A3 CD ISOL selector boss', (hx, 4.19, top), (hx, 4.19, top + 0.03), 0.035, steel, 20)
    box('A3 CD ISOL selector knob', (hx, 4.19, top + 0.045), (0.085, 0.024, 0.03), red)
    for txt, y in (('TRIP', 4.05), ('CD ISOL', 4.19)):
        t = bpy.data.curves.new('A3 desk legend ' + txt, 'FONT'); t.body = txt; t.size = 0.018; t.align_x = 'CENTER'; t.align_y = 'CENTER'
        to = bpy.data.objects.new('A3 desk legend ' + txt, t); COLL.objects.link(to); t.materials.append(M('Printed dark ink'))
        to.location = (hx + 0.0605, y, 1.02); to.rotation_euler = (math.pi / 2, 0, math.pi / 2)    # on the housing's front face (+x, towards the operator)
    move_anchor('INTERACT_CSB_TRIP', (hx, 4.05, top + 0.05))
    move_anchor('INTERACT_CD_ISOLATE', (hx, 4.19, top + 0.05))
    note('desk_station', trip_parts=moved, housing=dict(x=hx, y=(y0, y1), top=top))

def desk_lamp():
    """The desk lamp's head (z 1.32..1.36) stood in front of the LOCAL selector's caption (review: 'task lamp covers the initial letter'):
    moved 0.16 m to stand between LOCAL and CW ISOLATE, its post shortened 0.10 m so the head sits below the caption sightline."""
    post, head = SC.objects.get('OP desk lamp post'), SC.objects.get('OP desk lamp')
    if not (post and head): note('desk_lamp_missing'); return
    z0 = min((post.matrix_world @ Vector(c)).z for c in post.bound_box); z1 = max((post.matrix_world @ Vector(c)).z for c in post.bound_box)
    k = (z1 - z0 - 0.10) / (z1 - z0)
    post.matrix_world = Matrix.Translation((0, 0.16, 0)) @ Matrix.Translation((0, 0, z0)) @ Matrix.Diagonal((1, 1, k, 1)) @ Matrix.Translation((0, 0, -z0)) @ post.matrix_world
    head.matrix_world = Matrix.Translation((0, 0.16, -0.10)) @ head.matrix_world
    note('desk_lamp', moved_y=0.16, lowered=0.10)

def light_balance():
    """A2's nine ceiling battens (about 1 kW of the room's 1.8 kW) wash every surface evenly; the art direction asks for key zones, darker
    secondary spaces and visible falloff (design/ART_DIRECTION.md section 8). Battens -35 %, equipment task lights +10 %."""
    changed = {}
    for o in SC.objects:
        if o.type != 'LIGHT': continue
        k = 0.65 if o.name.startswith('batten') else 1.10 if o.name in ('task pumps', 'task operator', 'task CD east', 'task CD south') else None
        if k: changed[o.name] = [round(o.data.energy, 1), round(o.data.energy * k, 1)]; o.data.energy *= k
    note('light_balance', lights=changed)

def vent_extensions():
    """Waterbox vent wheels (4.64 m) out of reach (west 0.97 m) or marginal (east) from the gallery: moved onto an angled extension spindle
    towards the nearest gallery run (west wheel 0.155 m west and 0.45 m up, clear above the rail at x 0.6; east wheel 0.10 m east, 0.30 m up)."""
    steel = M('Astra brushed fastener steel')
    for side, dx, dz in (('west', -0.155, 0.45), ('east', +0.10, 0.30)):     # west: lifted over the gallery rail (top 5.02) so the wheel can overhang it
        parts = [o for o in SC.objects if o.name.startswith('WB %s vent wheel' % side)]
        if not parts: note('vent_missing', side=side); continue
        hub = next(o for o in parts if 'hub' in o.name); c0 = sum((hub.matrix_world @ Vector(v) for v in hub.bound_box), Vector()) / 8
        T = Matrix.Translation((dx, 0, dz))
        for o in parts: o.matrix_world = T @ o.matrix_world
        cylinder('A3 WB %s vent extension spindle' % side, c0, c0 + Vector((dx, 0, dz)), 0.012, steel, 10)
        cylinder('A3 WB %s vent spindle guide' % side, c0 + Vector((dx * 0.4, 0, dz * 0.4)), c0 + Vector((dx * 0.55, 0, dz * 0.55)), 0.022, M('Structural painted steel'), 12)
        note('vent_extension', side=side, from_=[round(v, 3) for v in c0], raise_m=dz, step_x=dx)

def ejector_chain():
    """The ejector steam isolation handwheel (EJ steam isol: vertical, centre 2.15 m, at the ejector skid's west edge) is 0.72 m from the
    nearest standing spot, and the skid and the west aisle leave no floor for a step. A chain wheel bolted 0.10 m in front of the handwheel,
    its chain hanging at the aisle edge to hand height: the standard fix for a high vertical handwheel."""
    yellow, galv, steel = M('Service ochre enamel'), M('Astra brushed fastener steel'), M('Structural painted steel')
    c = Vector((-1.20, 7.55, 2.15)); R = 0.14
    strands = [(c.x, c.y - R), (c.x, c.y + R)]
    blocked = [n for sx, sy in strands for ok, n in [clear_down(sx, sy, c.z - 0.02, 1.05)] if not ok]
    if blocked: note('ej_chain_blocked', by=blocked); return
    torus('A3 EJ steam isol chain wheel', c, (1, 0, 0), R, 0.011, yellow)
    for k in range(3):
        a = 2 * math.pi * k / 3
        p = Vector((0, math.cos(a) * 0.09, math.sin(a) * 0.09)); cylinder('A3 EJ steam isol chain wheel stud %d' % k, c + p, c + p + Vector((0.10, 0, 0)), 0.007, steel, 8)
    for k, (sx, sy) in enumerate(strands): chain('A3 EJ steam isol chain %s' % 'AB'[k], (sx, sy, c.z - 0.01), 1.17, galv)
    cylinder('A3 EJ steam isol chain loop bottom', (c.x, strands[0][1], 1.17), (c.x, strands[1][1], 1.17), 0.008, galv, 8)
    box('A3 EJ steam isol chain tag', (c.x, strands[0][1], 1.55), (0.006, 0.07, 0.045), yellow)
    move_anchor('INTERACT_EJ', (c.x, c.y, 1.23))
    note('ej_chain', wheel_centre=[round(v, 3) for v in c], grip_z=1.17)

# ---------------------------------------------------------------------------------------------------------------------------------------------
add_positions()
wear_pass()
chain_operators(); desk_station(); desk_lamp(); vent_extensions(); ejector_chain(); light_balance()
dg = bpy.context.evaluated_depsgraph_get()
tris = 0
for o in SC.objects:
    if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render:
        me = o.evaluated_get(dg).to_mesh(); tris += sum(len(p.vertices) - 2 for p in me.polygons); o.evaluated_get(dg).to_mesh_clear()
RECEIPT['evaluated_triangles'] = tris; print('A3 triangles', tris)
assert tris <= 400000, tris
bpy.ops.wm.save_as_mainfile(filepath=str(OUT), compress=True)
RECEIPT['output'] = OUT.name; RECEIPT['output_sha256'] = hashlib.sha256(OUT.read_bytes()).hexdigest()
(HERE / 'finish-A3-build.json').write_text(json.dumps(RECEIPT, indent=1) + '\n')
print('A3 saved', OUT, flush=True)
