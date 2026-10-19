"""Condenser bay finish A3: A2 (Codex, PR #107) plus authored wear, reachable controls and the map-level headroom fix.

    blender -b --factory-startup module_aaa_A2.blend --python condenser_finish_A3.py [-- --out module_aaa_A3.blend]

Owner, 2026-10-19: "Rework the room to your liking, build into the main map ... Fix everything needed to make this scene perfect."
A2 answered the palette ("more machine colour") but reads factory-new: flat paint, near-white walls, no sign of use. Its independent review
rejected it on reach (rubric hard gate 8) and on the gallery headroom under the map's squeezed roof. A3 keeps every A2 material and object
and adds, in this file only:
  * wear where use explains it (design/ART_DIRECTION.md section 9): grime at the floor line and in cavities, weeps under flanges and valves,
    oil at the pump bases, paint touch-ups on the shell, scuffs on the impact dado and column feet, low-frequency tonal variation on large
    painted fields, and slightly darker, warmer mineral walls with per-panel variation;
  * reachable controls: bevel-gear chain-wheel operators in place of the handwheels on the two overhead CW isolation valves, a chain wheel on
    the ejector steam isolation, the trip mushroom and a "CD ISOL" selector on a desk-front control housing, and an extension spindle and
    right-angle gearbox bringing the west waterbox vent wheel to the gallery. The INTERACT_* anchors move to the new grips;
  * light with key zones and falloff: battens and fill washes down, task lights and practicals up, warmer.
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
        """Chipped paint on convex edges, broken up so only some edge lengths chip. Inside ambient occlusion finds the edges: rays cast into
        the solid from a point near a convex edge hit the neighbouring face, so 1 - AO(inside) rises along the edge. (The first pass compared
        the bevel normal with the shading normal, which is zero on these smooth-shaded meshes: no chips rendered at all.)"""
        ao = self.node('ShaderNodeAmbientOcclusion', 'edge (inside AO %.3f m)' % radius, samples=8, inside=True)
        ao.inputs['Distance'].default_value = radius
        e = self.ramp(self.math('SUBTRACT', 1.0, ao.outputs['AO']), threshold, threshold + 0.25)
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
WEEPS_MACHINE = [(0.60, 3.60, 2.27, 0.05, 0.55), (0.60, 4.50, 2.27, 0.04, 0.50),       # under the west waterbox cover's lower bolts, down its red face (z 1.85..2.27)
                 (5.40, 3.75, 2.27, 0.05, 0.55), (5.40, 4.35, 2.27, 0.04, 0.50)]       # the same on the east waterbox
WEEPS_WALL = [(9.84, 3.2, 3.0, 0.10, 1.6), (9.84, 4.9, 3.0, 0.10, 1.4),                # east wall under the CW isolation valves' wall brackets
              (-2.04, 7.6, 2.6, 0.08, 1.2), (4.9, 9.5, 4.2, 0.12, 2.2)]                # west wall under the ejector discharge, north wall under a penetration
FLOOR_OIL = [(2.57, 6.6, 0.42), (4.27, 7.75, 0.38), (3.2, 4.05, 0.32),                 # pump bases and under the hotwell drain
             (2.95, 6.75, 0.16), (4.62, 7.9, 0.14), (-1.20, 7.25, 0.20)]               # seal drips beside the pumps; under the ejector skid's drain
FLOOR_WET = [(8.55, 3.2, 0.22), (8.55, 4.9, 0.18), (8.95, 7.6, 0.30)]                  # under the CW isolation valves; at the trench drain
TOUCH_UPS = [((1.55, 2.15), (2.7, 3.7), (2.05, 2.55)), ((4.15, 4.6), (2.7, 3.7), (3.62, 3.98))]   # fresher paint on the shell's south flank (clear of the CD-01 stencil)
DADO_SCUFFS = [((-1.85, -1.7), (0.0, 2.2), (0.10, 0.45)), ((-1.8, 9.6), (9.3, 9.45), (0.10, 0.45)), ((9.5, 9.65), (1.4, 7.0), (0.10, 0.45))]   # where trolleys and boots hit
MINERAL = ('Warm mineral plaster', 'Dense cast concrete', 'Basement coated concrete', 'Replacement floor patch')
MACHINE = ('A2 machine blue enamel', 'A2 waterbox oxide enamel', 'A2 hotwell graphite blue', 'Oxide orange enamel', 'Light oxide enamel', 'Astra ivory painted steel')

def wear_pass():
    for name in WEAR_MATERIALS:
        src = bpy.data.materials.get(name)
        if src is None: note('wear_skipped', material=name, why='not in A2'); continue
        mesh_users = [(o, i) for o, i in users_of({name}) if o.data.users == 1]
        if not mesh_users: continue
        mat = src.copy(); mat.name = name + ' | A3 wear'
        build(mat, name, positional=True)
        # sheet parts (thinner than 5 cm) get the same wear without edge chips: inside AO finds every point of a thin plate, not its edges
        thin = [(o, i) for o, i in mesh_users if min(o.dimensions) < 0.05] if name not in MINERAL else []
        mat_thin = None
        if thin:
            mat_thin = src.copy(); mat_thin.name = name + ' | A3 wear sheet'
            build(mat_thin, name, positional=True, edge_chips=False)
        for o, i in mesh_users:
            o.material_slots[i].link = 'OBJECT'; o.material_slots[i].material = mat_thin if (o, i) in thin else mat
        # shared meshes and curves keep the A2 material, given the attribute-free part of the same treatment (no chips: curves are thin tubes)
        build(src, name, positional=False, edge_chips=False)
        note('wear', material=name, positional_users=len(mesh_users), sheet_users=len(thin))

def build(mat, name, positional, edge_chips=True):
    """Wear sized to read at 3 to 5 m (the first A3 pass was invisible at review size): cavity and contact grime, chipped hard edges,
    vertical run-off streaks, dust on tops, grime at the bases, and on the large machine fields a quieter colour (a little less saturation,
    +-10 % tone) so the blue and red read as painted plant, not clean CG fields."""
    w = Wear(mat, positional); base, rough = w.base, w.rough
    painted = name not in MINERAL
    nz = w.node('ShaderNodeSeparateXYZ', 'world normal'); w.nt.links.new(w.node('ShaderNodeNewGeometry', 'normal').outputs['Normal'], nz.inputs[0])
    vertical = w.ramp(w.math('ABSOLUTE', nz.outputs['Z']), 0.55, 0.25)
    if painted:
        if name in ('A2 machine blue enamel', 'A2 waterbox oxide enamel', 'A2 hotwell graphite blue'):
            bw = w.node('ShaderNodeRGBToBW', 'luminance'); w.nt.links.new(base, bw.inputs[0])
            base = w.mix(base, 0.16, w.grey(bw.outputs[0]), 'MIX')                                   # quieter large fields: 16 % towards grey
            base = w.mix(base, 1.0, w.grey(w.tone(0.45, 0.10)))                                      # low-frequency paint tone, +-10 %
        cav = w.ao_grime(0.30, 1.1, 0.90)
        base = w.mix(base, cav, (0.24, 0.22, 0.19))                                                  # cavities and contact shadows collect grime
        if edge_chips and name not in ('Structural painted steel', 'Charcoal impact dado'):
            chips = w.edges(0.025, 0.20, 6.0, 0.45)                                                  # worn paint on convex edges, in broken lengths
            base = w.mix(base, chips, (0.34, 0.33, 0.31), 'MIX'); rough = w.math('ADD', rough, w.math('MULTIPLY', chips, 0.22))
        if name in MACHINE:
            grime = w.math('MULTIPLY', w.ramp(w.noise(1.6, 4.0, rough=0.62), 0.48, 0.78), 0.45, True)
            base = w.mix(base, grime, (0.50, 0.45, 0.38))                                            # handled, splashed and wiped: a broken film of grime
            rough = w.math('ADD', rough, w.math('MULTIPLY', grime, 0.15))
            streak = w.math('MULTIPLY', w.math('MULTIPLY', w.ramp(w.noise(5.0, 3.0, (1, 1, 0.07)), 0.50, 0.72), w.ramp(w.noise(0.8, 2.0), 0.35, 0.70)), vertical)
            base = w.mix(base, w.math('MULTIPLY', streak, 0.55, True), (0.52, 0.47, 0.40))           # run-off streaks on vertical faces
        dust = w.math('MULTIPLY', w.math('MULTIPLY', w.ramp(nz.outputs['Z'], 0.55, 0.92), w.ramp(w.noise(2.2, 3.0), 0.25, 0.75, 0.45, 1.0)), 0.35, True)
        base = w.mix(base, dust, (0.30, 0.28, 0.25), 'MIX'); rough = w.math('ADD', rough, w.math('MULTIPLY', dust, 0.35))     # settled dust on tops
        if positional:
            base = w.mix(base, w.floor_line(1.0, 1.6), (0.30, 0.27, 0.22))                          # splash and boot grime at machine bases
            if name in MACHINE[:5]:
                weep = w.weeps(WEEPS_MACHINE, 1.0)
                base = w.mix(base, weep, (0.46, 0.29, 0.17)); rough = w.math('ADD', rough, w.math('MULTIPLY', weep, 0.12))
            if name == 'A2 machine blue enamel':
                tu = w.boxes(TOUCH_UPS, 1.0); base = w.mix(base, tu, (1.12, 1.10, 1.14)); rough = w.math('SUBTRACT', rough, w.math('MULTIPLY', tu, 0.10))
            if name in ('Charcoal impact dado', 'Structural painted steel'):
                dado = name == 'Charcoal impact dado'
                zone = w.boxes(DADO_SCUFFS, 1.0) if dado else w.ramp(w.pos()[1].outputs['Z'], 0.35, 0.08)
                chip = w.math('MULTIPLY', zone, w.ramp(w.noise(3.5, 3.0, rough=0.5), 0.66 if dado else 0.74, 0.70 if dado else 0.77), True)   # scuffed bands, not specks
                base = w.mix(base, chip, (0.11, 0.11, 0.105) if dado else (0.12, 0.125, 0.13), 'MIX')   # worn-through dark primer on the dado; on near-black steel, only a dull scuff
                rough = w.math('ADD', rough, w.math('MULTIPLY', chip, 0.15))
        rough = w.math('ADD', rough, w.math('MULTIPLY', cav, 0.12))
    else:
        if name in ('Warm mineral plaster', 'Dense cast concrete'):
            for b in [n for n in w.nt.nodes if n.type == 'BUMP' and not n.label.startswith('A3')]:
                b.inputs['Strength'].default_value *= 0.35                                           # A2's fine grain bump read as mottle at review size
            base = w.mix(base, 0.40, (0.46, 0.44, 0.41), 'MIX')                                       # quieter grain
            base = w.mix(base, 1.0, (0.80, 0.76, 0.70))                                               # darker, warmer mineral: A2's walls read near-white
            if positional:
                _, s = w.pos()
                panel = w.node('ShaderNodeTexWhiteNoise', 'per-panel tone (1.5 x 3 m formwork)', noise_dimensions='3D')
                cell = w.vmath('FLOOR', w.vmath('MULTIPLY', w.pos()[0], (1 / 1.5, 1 / 1.5, 1 / 3.0)))
                w.nt.links.new(cell, panel.inputs['Vector'])
                base = w.mix(base, 1.0, w.grey(w.math('ADD', 0.91, w.math('MULTIPLY', panel.outputs['Value'], 0.18))))      # +-9 % per formwork panel
                runs = w.math('MULTIPLY', w.ramp(w.noise(2.4, 2.0, (1, 1, 0.10)), 0.55, 0.72), w.ramp(s.outputs['Z'], 1.0, 4.5), True)   # water marks from above
                base = w.mix(base, w.math('MULTIPLY', runs, 0.6), (0.58, 0.55, 0.49))
                base = w.mix(base, w.floor_line(0.9, 1.0), (0.40, 0.36, 0.30))
                weep = w.weeps(WEEPS_WALL, 0.85); base = w.mix(base, weep, (0.55, 0.50, 0.43))
            base = w.mix(base, w.ao_grime(0.4, 1.2, 0.7), (0.45, 0.43, 0.40))
        else:   # floor
            base = w.mix(base, 1.0, w.grey(w.tone(0.35, 0.12)))                                       # large-scale dirt, +-12 %
            if positional:
                oil = w.spots(FLOOR_OIL, 1.0); wet = w.spots(FLOOR_WET, 0.8)
                base = w.mix(base, oil, (0.22, 0.20, 0.18)); base = w.mix(base, wet, (0.62, 0.62, 0.62))
                rough = w.math('SUBTRACT', rough, w.math('ADD', w.math('MULTIPLY', oil, 0.35), w.math('MULTIPLY', wet, 0.40)))
            base = w.mix(base, w.ao_grime(0.6, 1.0, 0.85), (0.30, 0.28, 0.25))                        # grime against walls and plinths
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
def smooth(o):
    for f in o.data.polygons: f.use_smooth = True
    return o
def link_chain(name, path, axis, mat, L=0.044, W=0.026, r=0.0035, closed=False):
    """A chain of oval wire links (6 to 7 mm wire, 30 mm pitch) laid along a polyline: alternate links turn 90 degrees about the run, and
    each link overlaps the next by its wire, so the chain reads as interlocked at any distance. `axis` is the plane normal of the run
    (the wheel axis); one link in two lies in that plane."""
    pts = [Vector(p) for p in path] + ([Vector(path[0])] if closed else [])
    seglen = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]; total = sum(seglen)
    pitch = L - 4 * r; n = int(total / pitch); pitch = total / n if closed else pitch
    a, bb = L / 2 - r, W / 2 - r; axis = Vector(axis).normalized(); bm = bmesh.new()
    for k in range(n):
        d = (k + 0.5) * pitch; i = 0
        while i < len(seglen) - 1 and d > seglen[i]: d -= seglen[i]; i += 1
        t = (pts[i + 1] - pts[i]).normalized(); c = pts[i] + t * d
        side = t.cross(axis).normalized() if k % 2 else axis - t * axis.dot(t)
        side.normalize(); nrm = t.cross(side)
        ring = []
        for j in range(8):
            th = 2 * math.pi * j / 8; cc = c + t * (a * math.cos(th)) + side * (bb * math.sin(th))
            tg = (t * (-a * math.sin(th)) + side * (bb * math.cos(th))).normalized(); out = tg.cross(nrm).normalized()
            ring.append([bm.verts.new(cc + (out * math.cos(q) + nrm * math.sin(q)) * r) for q in (math.pi / 4 + m * math.pi / 2 for m in range(4))])
        for j in range(8):
            for m in range(4):
                bm.faces.new((ring[j][m], ring[(j + 1) % 8][m], ring[(j + 1) % 8][(m + 1) % 4], ring[j][(m + 1) % 4]))
    return smooth(mesh_obj(name, bm, mat))
def arc(c, u, v, R, a0, a1, n):
    """Points on the circle c + R(u cos a + v sin a), from angle a0 to a1."""
    return [Vector(c) + (u * math.cos(a0 + (a1 - a0) * i / n) + v * math.sin(a0 + (a1 - a0) * i / n)) * R for i in range(n + 1)]
def chain_wheel(tag, wc, axis, R, cast, paint):
    """A pocketed chain wheel: a dark cast pocket ring the chain sits in, between two painted guide flanges, on a six-spoke hub. Not a
    handwheel: no grip rim, and the chain runs over its top half."""
    axis = Vector(axis).normalized(); up = Vector((0, 0, 1)); tang = axis.cross(up).normalized(); parts = []
    parts.append(torus('%s chain wheel pocket ring' % tag, wc, axis, R, 0.012, cast, 32, 6))
    for s in (-1, 1): parts.append(torus('%s chain wheel flange %s' % (tag, 'AB'[s > 0]), wc + axis * (0.017 * s), axis, R + 0.010, 0.006, paint, 32, 4))
    parts.append(cylinder('%s chain wheel hub' % tag, wc - axis * 0.03, wc + axis * 0.03, 0.034, paint, 16))
    for k in range(6):
        ang = 2 * math.pi * k / 6 + math.pi / 6; d = tang * math.cos(ang) + up * math.sin(ang)
        parts.append(cylinder('%s chain wheel spoke %d' % (tag, k), wc + d * 0.03, wc + d * (R - 0.008), 0.0075, paint, 6))
    for o in parts: smooth(o)
    return tang
def chain_loop(tag, wc, axis, R, low, mat):
    """The hand chain: down both sides of the wheel to `low`, closed by a U at the bottom (the grip). Returns the strand (x, y) points."""
    axis = Vector(axis).normalized(); up = Vector((0, 0, 1)); tang = axis.cross(up).normalized()
    top = arc(wc, tang, up, R, 0.0, math.pi, 16)                                         # over the wheel, in its pocket
    a_bot, b_bot = wc - tang * R, wc + tang * R
    a_bot.z = b_bot.z = low
    u_c = (a_bot + b_bot) / 2
    bottom = arc(u_c, -tang, -up, R, 0.0, math.pi, 12)                                  # U from the -tang strand round to the +tang strand
    run = [b_bot] + top + [a_bot]                                                        # +tang strand up, over, -tang strand down
    link_chain('%s chain' % tag, run, axis, mat)
    link_chain('%s chain loop bottom' % tag, bottom, axis, mat)
    return [(a_bot.x, a_bot.y), (b_bot.x, b_bot.y)], u_c.z - R
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
    """Overhead CW isolation globes (handwheels at 3.4 m, flat on top): the handwheel gives way to a bevel-gear operator on the yoke, its
    output shaft carrying a chain wheel 0.22 m out, on whichever side of the valve the chain can drop clear to the floor. The pressure
    gauge's impulse line used to rise through the handwheel hub; it now leaves the instrument root sideways and enters the gauge from below."""
    paint, cast, galv, steel = M('A2 machine blue enamel'), M('Oiled iron'), M('Astra brushed fastener steel'), M('Astra brushed fastener steel')
    yellow = M('Service ochre enamel')
    for tag, y in (('SUPPLY', 3.2), ('RETURN', 4.9)):
        x0, R, low = 8.55, 0.13, 1.18
        removed = []
        for part in ('handwheel rim', 'handwheel spoke0', 'handwheel spoke1', 'handwheel spoke2', 'handwheel hub'):
            o = SC.objects.get('CW isol %s %s' % (tag, part))
            if o: bpy.data.objects.remove(o); removed.append(part)
        for part in ('impulse connection', 'impulse connection start cap', 'impulse connection end cap'):
            o = SC.objects.get('CW %s %s' % (tag, part))
            if o: bpy.data.objects.remove(o); removed.append(part)
        chosen = None
        for d in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            ax = Vector((d[0], d[1], 0)); wc = Vector((x0, y, 3.46)) + ax * 0.22; tang = ax.cross(Vector((0, 0, 1))).normalized()
            strands = [wc - tang * R, wc + tang * R]
            if all(clear_down(p.x, p.y, wc.z - 0.02, low - R - 0.05)[0] for p in strands + [(strands[0] + strands[1]) / 2]): chosen = (ax, wc); break
        if chosen is None: note('chain_blocked', valve=tag); continue
        ax, wc = chosen; T = 'A3 CW isol %s' % tag
        cylinder(T + ' gear operator flange', (x0, y, 3.355), (x0, y, 3.375), 0.058, paint, 20)
        cylinder(T + ' gear operator body', (x0, y, 3.375), (x0, y, 3.52), 0.050, paint, 20)
        cylinder(T + ' gear operator cap', (x0, y, 3.52), (x0, y, 3.535), 0.032, paint, 16)
        cylinder(T + ' gear operator boss', Vector((x0, y, 3.46)), Vector((x0, y, 3.46)) + ax * 0.10, 0.040, paint, 16)
        cylinder(T + ' chain wheel shaft', Vector((x0, y, 3.46)) + ax * 0.10, wc + ax * 0.035, 0.016, steel, 12)
        chain_wheel(T, wc, ax, R, cast, yellow)
        strands, grip = chain_loop(T, wc, ax, R, low, galv)
        root, gauge = Vector((x0 - 0.037, y, 3.30)), Vector((8.15, y, 3.30))
        cylinder('A3 CW %s impulse line' % tag, root, gauge, 0.010, steel, 10)
        cylinder('A3 CW %s impulse riser' % tag, gauge, (8.15, y, 3.39), 0.010, steel, 10)
        move_anchor('INTERACT_CW_ISOL_%s' % tag[0], ((strands[0][0] + strands[1][0]) / 2, (strands[0][1] + strands[1][1]) / 2, grip + 0.04))
        note('chain_operator', valve=tag, removed=removed, wheel_centre=[round(v, 3) for v in wc], side=tuple(ax.xy), grip_z=round(grip, 3))

def desk_station():
    """Two controls the operator could not reach: the trip mushroom sat on the panel face just above the desk's back edge (0.75 m from a
    standing operator), and INTERACT_CD_ISOLATE floated inside the west waterbox at 3.17 m with no control at all. The panel's selector row
    (LOCAL, CW ISOLATE, CEP SELECT, VACUUM at 0.32 m pitch) is full, so both go on a dark desk-front control housing in the operator's hand
    zone: the trip mushroom (the original parts, turned to face up) on a yellow emergency-stop ground and collar, and a CD ISOL selector for
    the motor-operated condenser isolation, with engraved legends on the housing's front. The trip's old hole on the panel gets a blanking plate."""
    yellow, red, dark, steel, ink = M('Service ochre enamel'), M('Emergency red enamel'), M('Charcoal impact dado'), M('Structural painted steel'), M('A2 stencil light ink')
    hx, y0, y1, top = -0.80, 3.98, 4.26, 1.07
    box('A3 desk control housing', (hx, (y0 + y1) / 2, 0.97 + (top - 0.97) / 2), (0.12, y1 - y0, top - 0.97), dark)
    box('A3 desk control housing top plate', (hx, (y0 + y1) / 2, top - 0.006), (0.124, y1 - y0 + 0.004, 0.012), steel)
    pivot = Vector((-1.38, 4.05, 1.12)); R = Matrix.Rotation(-math.pi / 2, 4, 'Y')       # rotates +x (out of the panel face) to +z (up)
    moved = []
    for n in ('OP trip stem', 'OP trip mushroom', 'OP trip bezel'):
        o = SC.objects.get(n)
        if o is None: continue
        o.matrix_world = Matrix.Translation((hx, 4.05, top)) @ R @ Matrix.Translation(-pivot) @ o.matrix_world
        moved.append(n)
    cylinder('A3 trip ground plate', (hx, 4.05, top), (hx, 4.05, top + 0.004), 0.056, yellow, 24)
    smooth(torus('A3 trip guard collar', (hx, 4.05, top + 0.022), (0, 0, 1), 0.050, 0.007, yellow, 24, 6))
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2
        cylinder('A3 trip guard post %d' % k, (hx + 0.05 * math.cos(a), 4.05 + 0.05 * math.sin(a), top), (hx + 0.05 * math.cos(a), 4.05 + 0.05 * math.sin(a), top + 0.022), 0.005, yellow, 8)
    box('A3 trip blanking plate', (-1.371, 4.05, 1.12), (0.008, 0.07, 0.07), steel)          # on the panel face (x -1.375), not 36 mm off it
    cylinder('A3 CD ISOL selector boss', (hx, 4.19, top), (hx, 4.19, top + 0.03), 0.035, steel, 20)
    box('A3 CD ISOL selector knob', (hx, 4.19, top + 0.045), (0.085, 0.024, 0.03), red)
    for txt, y in (('TRIP', 4.05), ('CD ISOL', 4.19)):
        t = bpy.data.curves.new('A3 desk legend ' + txt, 'FONT'); t.body = txt; t.size = 0.026; t.align_x = 'CENTER'; t.align_y = 'CENTER'
        to = bpy.data.objects.new('A3 desk legend ' + txt, t); COLL.objects.link(to); t.materials.append(ink)
        to.location = (hx + 0.0605, y, 1.02); to.rotation_euler = (math.pi / 2, 0, math.pi / 2)    # on the housing's front face (+x, towards the operator)
    move_anchor('INTERACT_CSB_TRIP', (hx, 4.05, top + 0.05))
    move_anchor('INTERACT_CD_ISOLATE', (hx, 4.19, top + 0.05))
    note('desk_station', trip_parts=moved, housing=dict(x=hx, y=(y0, y1), top=top))

def desk_lamp():
    """The desk lamp's head (z 1.32..1.36) stood in front of the LOCAL selector's caption (review: 'task lamp covers the initial letter'):
    moved 0.16 m to stand between LOCAL and CW ISOLATE, its post shortened 0.10 m so the head sits below the caption sightline. The head
    was a glowing white puck; it becomes a dark shade with the warm diffuser under it."""
    post, head = SC.objects.get('OP desk lamp post'), SC.objects.get('OP desk lamp')
    if not (post and head): note('desk_lamp_missing'); return
    z0 = min((post.matrix_world @ Vector(c)).z for c in post.bound_box); z1 = max((post.matrix_world @ Vector(c)).z for c in post.bound_box)
    k = (z1 - z0 - 0.10) / (z1 - z0)
    post.matrix_world = Matrix.Translation((0, 0.16, 0)) @ Matrix.Translation((0, 0, z0)) @ Matrix.Diagonal((1, 1, k, 1)) @ Matrix.Translation((0, 0, -z0)) @ post.matrix_world
    head.matrix_world = Matrix.Translation((0, 0.16, -0.10)) @ head.matrix_world
    glass = head.material_slots[0].material; head.material_slots[0].link = 'OBJECT'; head.material_slots[0].material = M('Charcoal impact dado')
    pts = [head.matrix_world @ Vector(c) for c in head.bound_box]; c = sum(pts, Vector()) / 8; zb = min(p.z for p in pts)
    rad = (max(p.x for p in pts) - min(p.x for p in pts)) / 2
    cylinder('A3 desk lamp diffuser', (c.x, c.y, zb - 0.003), (c.x, c.y, zb), rad * 0.82, glass, 20)
    note('desk_lamp', moved_y=0.16, lowered=0.10, shade='Charcoal impact dado')

def light_balance():
    """A2 lit every surface evenly: nine ceiling battens (about 1 kW) plus washes on the walls, the neck and the chest, with the equipment
    task lights in the same range. The art direction asks for key zones, darker secondary spaces and visible falloff (design/ART_DIRECTION.md
    section 8), and the neighbours (turbine, cooling) are warm and dark. Battens to 45 % and warmer (about 3,800 K), fill washes to 60 %,
    the task lights over the machines, the pumps and the desk and the wall practicals +30 %."""
    changed = {}
    fills = ('neck wash', 'chest well', 'cw wall wash', 'gallery inspection light', 'gallery inspection light.001', 'CW support inspection uplight', 'gallery task')
    tasks = ('task pumps', 'task operator', 'task CD east', 'task CD south', 'Astra practical task', 'Astra practical task.001', 'Astra practical task.002')
    for o in SC.objects:
        if o.type != 'LIGHT': continue
        if o.name.startswith('batten'): k = 0.45; o.data.color = (1.0, 0.90, 0.77)
        elif o.name in fills: k = 0.60
        elif o.name in tasks: k = 1.30
        else: continue
        changed[o.name] = [round(o.data.energy, 1), round(o.data.energy * k, 1)]; o.data.energy *= k
    # fill washes have no fixture: their rectangles showed as pale reflections in glossy enamel (the "pink panel" on the east waterbox in W05)
    hidden = []
    for n in fills + ('entry wash', 'handoff wash'):
        o = SC.objects.get(n)
        if o: o.visible_glossy = False; hidden.append(n)
    note('light_balance', lights=changed, hidden_from_glossy=hidden)

def vent_extension():
    """The west waterbox vent wheel (horizontal, 4.64 m, on top of the waterbox) is 0.97 m from the gallery. It goes up a vertical
    extension spindle, held in a guide bracket bolted to the waterbox top, to a right-angle gearbox whose output turns the same wheel
    stood on edge facing the gallery, 0.125 m in from the rail. The east wheel is already within reach (0.54 m) and stays as it was."""
    steel, paint, dark = M('Astra brushed fastener steel'), M('A2 machine blue enamel'), M('Structural painted steel')
    parts = [o for o in SC.objects if o.name.startswith('WB west vent wheel')]
    if not parts: note('vent_missing', side='west'); return
    hub = next(o for o in parts if 'hub' in o.name); c0 = sum((hub.matrix_world @ Vector(v) for v in hub.bound_box), Vector()) / 8
    zg, xw = 5.05, c0.x - 0.15
    cylinder('A3 WB west vent extension spindle', (c0.x, c0.y, c0.z - 0.04), (c0.x, c0.y, zg - 0.045), 0.012, steel, 10)
    box('A3 WB west vent gearbox', (c0.x, c0.y, zg), (0.09, 0.09, 0.09), paint)
    cylinder('A3 WB west vent gearbox shaft', (c0.x - 0.045, c0.y, zg), (xw - 0.02, c0.y, zg), 0.012, steel, 10)
    T = Matrix.Translation((xw, c0.y, zg)) @ Matrix.Rotation(-math.pi / 2, 4, 'Y') @ Matrix.Translation(-c0)
    for o in parts: o.matrix_world = T @ o.matrix_world                                   # the wheel, stood on edge facing -x (the gallery)
    # guide bracket: a flat bar standing on the waterbox top beside the spindle, a collar round the spindle at mid-height, the gearbox on top
    zt = 4.39; bx = c0.x + 0.05
    box('A3 WB west vent bracket foot', (bx, c0.y, zt + 0.005), (0.07, 0.08, 0.01), dark)
    box('A3 WB west vent bracket bar', (bx, c0.y, (zt + zg - 0.045) / 2), (0.012, 0.05, zg - 0.045 - zt), dark)
    zm = (c0.z + zg) / 2
    box('A3 WB west vent bracket arm', ((c0.x + bx) / 2, c0.y, zm), (bx - c0.x, 0.03, 0.012), dark)
    smooth(torus('A3 WB west vent spindle collar', (c0.x, c0.y, zm), (0, 0, 1), 0.019, 0.006, dark, 16, 4))
    box('A3 WB west vent bracket top', ((c0.x + bx) / 2 + 0.0, c0.y, zg - 0.05), (bx - c0.x + 0.03, 0.06, 0.01), dark)
    note('vent_extension', side='west', from_=[round(v, 3) for v in c0], gearbox_z=zg, wheel_plane_x=round(xw, 3))

def ejector_chain():
    """The ejector steam isolation handwheel (EJ steam isol: vertical, centre 2.15 m, at the ejector skid's west edge) is 0.72 m from the
    nearest standing spot, and the skid and the west aisle leave no floor for a step. A chain wheel bolted 0.10 m in front of the handwheel,
    its chain hanging at the aisle edge to hand height: the standard fix for a high vertical handwheel."""
    yellow, galv, steel, cast = M('Service ochre enamel'), M('Astra brushed fastener steel'), M('Structural painted steel'), M('Oiled iron')
    c = Vector((-1.20, 7.55, 2.15)); R = 0.14; low = 1.31; ax = Vector((-1, 0, 0))
    tang = ax.cross(Vector((0, 0, 1))).normalized(); strands = [c - tang * R, c + tang * R]
    blocked = [n for p in strands for ok, n in [clear_down(p.x, p.y, c.z - 0.02, low - R - 0.05)] if not ok]
    if blocked: note('ej_chain_blocked', by=blocked); return
    chain_wheel('A3 EJ steam isol', c, ax, R, cast, yellow)
    for k in range(3):
        a = 2 * math.pi * k / 3
        p = Vector((0, math.cos(a) * 0.09, math.sin(a) * 0.09)); cylinder('A3 EJ steam isol chain wheel stud %d' % k, c + p, c + p + Vector((0.10, 0, 0)), 0.007, steel, 8)
    _, grip = chain_loop('A3 EJ steam isol', c, ax, R, low, galv)
    move_anchor('INTERACT_EJ', (c.x, c.y, grip + 0.04))
    note('ej_chain', wheel_centre=[round(v, 3) for v in c], grip_z=round(grip, 3))

def cw_tags():
    """The CW SUPPLY and RETURN wall tags (z 3.44..3.60) sat behind the new chain wheels and chains in the views along the east wall:
    both raised 0.25 m, still over their pipes."""
    moved = []
    for n in ('CW tag SUPPLY', 'CW tag t SUPPLY', 'CW tag RETURN', 'CW tag t RETURN'):
        o = SC.objects.get(n)
        if o: o.matrix_world = Matrix.Translation((0, 0, 0.25)) @ o.matrix_world; moved.append(n)
    note('cw_tags_raised', objects=moved, dz=0.25)

def intersections():
    """New parts that cut into existing ones (contacts are intended where parts are bolted or seated; anything else is a defect to fix)."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get(); new = [o for o in COLL.objects if o.type == 'MESH']
    def box_of(o):
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]; return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
    old = [(o, box_of(o)) for o in SC.objects if o.type == 'MESH' and o.name not in COLL.objects and not o.hide_render]
    hits = []
    for o in new:
        lo, hi = box_of(o); bo = BVHTree.FromObject(o, dg)
        for q, (ql, qh) in old:
            if any(hi[i] < ql[i] or lo[i] > qh[i] for i in range(3)): continue
            if bo.overlap(BVHTree.FromObject(q, dg)): hits.append((o.name, q.name))
    RECEIPT['intersections'] = hits; print('A3 intersections', len(hits)); [print('A3 X', a, '|', b) for a, b in hits]

# ---------------------------------------------------------------------------------------------------------------------------------------------
add_positions()
wear_pass()
chain_operators(); desk_station(); desk_lamp(); vent_extension(); ejector_chain(); cw_tags(); light_balance(); intersections()
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
