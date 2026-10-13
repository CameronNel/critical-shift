"""GREY-BOX TEST (2026-10-13), not the map: what the layout gains if the fuel corridor is replaced by a short straight one. Run:

    blender --background --factory-startup --python greybox_fuel_test.py -- --output <scratch>.blend

Owner question: "do you wanna rebuild the fuel corridor or is it dumb" -> "yes do the greybox test". Nothing here is a design decision or art.
Builds on build_compact_map.py (imported: same rooms, patches, stair, closed leaves) and then changes the placements:
  * the fuel corridor room is left out; a GREY box corridor (5 m wide, 5 m high) runs from the refinery fuel door north to the concourse's west end;
  * the reactor, with the turbine, electrical, condenser, stair and cooling, moves south by DY so the concourse sits just north of the refinery's north wall
    (DY is set by that clearance: corridor east leg 2.5 m off the refinery wall, the concourse centred on it);
  * the front end's 34 m spine is left out and drawn as a GREY box from the hall's north wall to the concourse (12.6 m);
  * the dock stays on the spine's east wall; waste moves to the reactor's east wall, where the reactor already has a 4 m opening closed by a patch panel
    (`East wall patch door`, module x 10.8..11.08, y 1.6..5.6), left out here;
  * the S03 transfer hall is dropped (the fuel corridor it served is gone).
Every grey part is named GREY_*. combined_map.blend is not touched; the output goes to a scratch path. Measurements: GREYBOX_FUEL_TEST.md."""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_compact_map as L                      # applies the assembly-pass overrides to build_combined_map (BM)
import build_combined_map as BM, reactor_links as R
from mathutils import Vector

REF_N = -40.3                                      # refinery north wall (outer), plan y
F01 = (-22.2, -43.6)                               # refinery fuel door, corridor start (fuel corridor F01 placement, measured)
CW = 5.0                                           # grey fuel corridor clear width
YF = REF_N + CW / 2 + 0.0                          # corridor east-leg centre: its south wall clears the refinery's north wall
DY = YF + 17.2                                     # concourse centre is reactor y - 17.2 (build_combined_map CONC: y -19.6..-14.8)
print('GREYBOX reactor moves south by %.2f m (centre y %.2f)' % (-DY, DY))

def sh(t, dy=DY): return (t[0], t[1] + dy, t[2])
place = {r[0]: r for r in BM.ROOMS}
moved = {}
for key in ('reactor-room', 'turbine-room', 'electrical-room', 'condenser-bay', 'cooling-plant'):
    k, lib, coll, loc, rz, note = place[key]; moved[key] = (k, lib, coll, sh(loc), rz, 'GREYBOX TEST: moved %.1f m south. ' % -DY + note)
WASTE = (11.62 + 0.32, DY + 3.6, 0.0)               # receiving exterior face (module y -0.32) on the reactor's east outer face x 11.6 (plan cut), rotation -90 (faces west)
k, lib, coll, loc, rz, note = place['waste-storage']; moved['waste-storage'] = (k, lib, coll, WASTE, -90.0, 'GREYBOX TEST: on the reactor east wall opening.')
BM.ROOMS = [moved.get(r[0], r) for r in BM.ROOMS if r[0] != 'fuel-corridor']
L.TURB, L.COND, L.ELEC = sh(L.TURB), sh(L.COND), sh(L.ELEC)
for kk in ('ytop', 'ybot', 'yn', 'cy0', 'cy1', 'vy'): L.ST[kk] += DY
BM.LINKS.clear()

# reactor: the stub doors as in the assembly pass, the east wall patch panel left out (waste opening)
_pr = BM.PATCHES['reactor-room']
def patch_reactor_gb(wrap, lib_coll, omit):
    _pr(wrap, lib_coll, omit); omit.add('East wall patch door')
    # the 3 m receiving opening through the east wall (module frame): wall layers, the orange wall-base guard and dressing in it split out, like the south door
    objs = [o for cc in bpy.data.collections if cc.library and os.path.basename(cc.library.filepath) == os.path.basename(BM.REACTOR_LIB) for o in cc.all_objects if o.name not in omit] + [o for o in wrap.objects if o.library is None]
    print('GREYBOX reactor east opening:', L.split_openings(wrap, omit, list(dict.fromkeys(objs)), 1, (9.7, 11.7), [(2.1, 5.1, 3.2)]), 'objects split')
BM.PATCHES['reactor-room'] = patch_reactor_gb
# front end: the base patches without the spine work; the whole spine (and anything inside its volume) is left out and drawn grey
def patch_fe_gb(wrap, lib_coll, omit):
    for f in (BM.open_portal_cap, BM.clear_yard_for_shed, BM.localise_evac_sign, BM.totem_back_board): f(wrap, lib_coll, omit)
    n = 0
    for o in lib_coll.all_objects:
        if o.type in ('MESH', 'CURVE', 'FONT', 'LIGHT'):
            p = BM.wm(o).translation if o.type == 'LIGHT' else None
            if p is None:
                lo, hi = L.bbox(o); c = (lo + hi) / 2
            else: c = p
            if o.name.startswith('spine') or 'reactor_door' in o.name or (-2.6 <= c.x <= 2.6 and 32.4 <= c.y <= 66.0):
                omit.add(o.name); n += 1
    objs = [o for o in dict.fromkeys(lib_coll.all_objects) if o.name not in omit and o.name.startswith('stain_')]      # the same doorway decal clips as the map
    L.split_openings(wrap, omit, objs, 1, (-15.95, -15.6), [(8.62, 11.4, 2.6)]); L.split_openings(wrap, omit, objs, 1, (17.6, 17.95), [(8.8, 11.18, 2.6)])
    L.split_openings(wrap, omit, objs, 1, (-11.95, -11.6), [(24.83, 27.17, 2.7)]); L.split_openings(wrap, omit, objs, 0, (0.0, 0.5), [(-1.3, 1.3, 2.6)])
    L.split_openings(wrap, omit, objs, 0, (31.1, 31.9), [(-1.8, 1.8, 3.2)]); L.split_openings(wrap, omit, objs, 0, (19.4, 20.6), [(-3.0, 3.0, 3.0)])
    g = next((o for o in lib_coll.all_objects if o.name == 'context_ground'), None)
    if g is not None:
        S = L.ST; L.hole_in_slab(wrap, omit, g, S['xw'] - S['t'] - 8.0, S['xe'] + S['t'] - 8.0, S['ybot'] + 80.0, S['yn'] + S['t'] + 80.0)
    print('GREYBOX front end: spine objects left out', n)
BM.PATCHES['front-end-area'] = patch_fe_gb
BM.placeholder_fuel_shutter = lambda: None
BM.add_reactor_concourse = lambda: None

def grey(coll, name, xs, ys, zs, mat): return BM._box(coll, 'GREY_' + name, xs, ys, zs, mat)

def post_build_gb():
    root = bpy.context.scene.collection.children['COMBINED_MAP']; c = bpy.data.collections.new('GREYBOX'); root.children.link(c)
    m = BM._mat('GREYBOX concrete', (0.5, 0.5, 0.5), 0.9); lit = BM._mat('GREYBOX lamp', (1.0, 0.95, 0.85), 0.5, 0.0, 4.0)
    t = 0.3; H = 5.0
    # fuel corridor: leg 1 north from the refinery door, leg 2 east to the concourse west end (x -10.8)
    x0, x1 = F01[0] - CW / 2, F01[0] + CW / 2; yb, yt = YF - CW / 2, YF + CW / 2; xe = -10.8
    grey(c, 'fuel floor 1', (x0 - t, x1 + t), (F01[1], yt + t), (-0.3, 0.0), m); grey(c, 'fuel floor 2', (x1, xe), (yb - t, yt + t), (-0.3, 0.0), m)
    grey(c, 'fuel roof', (x0 - t, xe), (F01[1], yt + t), (H, H + 0.25), m)
    grey(c, 'fuel wall west', (x0 - t, x0), (F01[1], yt + t), (0, H), m); grey(c, 'fuel wall north', (x0 - t, xe), (yt, yt + t), (0, H), m)
    grey(c, 'fuel wall east 1', (x1, x1 + t), (F01[1], yb), (0, H), m); grey(c, 'fuel wall south 2', (x1, xe), (yb - t, yb), (0, H), m)
    # concourse (same size as build_combined_map CONC, shifted), tunnel into the reactor south door
    C = dict(BM.CONC); cy0, cy1 = C['y0'] + DY, C['y1'] + DY; ro = C['roof']
    grey(c, 'concourse floor', (C['x0'], 5.85), (cy0 - t, cy1 + t), (-0.3, 0.0), m); grey(c, 'concourse roof', (C['x0'], 6.15), (cy0 - t, cy1 + t), (ro, ro + 0.25), m)
    grey(c, 'concourse south wall', (C['x0'], 5.85), (cy0 - t, cy0), (0, ro), m)
    grey(c, 'concourse north wall west', (C['x0'], -2.5), (cy1, cy1 + t), (0, ro), m); grey(c, 'concourse north wall east', (2.5, 5.85), (cy1, cy1 + t), (0, ro), m)
    ty1 = DY - 10.0
    grey(c, 'tunnel floor', (-2.8, 2.8), (cy1, ty1), (-0.3, 0.0), m); grey(c, 'tunnel roof', (-2.8, 2.8), (cy1, ty1), (H, H + 0.25), m)
    grey(c, 'tunnel wall west', (-2.8, -2.5), (cy1, ty1), (0, H), m); grey(c, 'tunnel wall east', (2.5, 2.8), (cy1, ty1), (0, H), m)
    # spine: hall north wall (y -48) to the concourse's north edge, west wall open onto the concourse, east wall open onto the dock P1
    sy0, sy1 = -48.0, cy1; dk = L.DOCK[1]
    grey(c, 'spine floor', (5.85, 10.15), (sy0, sy1), (-0.3, 0.0), m); grey(c, 'spine roof', (5.85, 10.15), (sy0, sy1 + t), (4.2, 4.45), m)
    grey(c, 'spine end wall', (5.85, 10.15), (sy1, sy1 + t), (0, 4.2), m)
    grey(c, 'spine wall west', (5.85, 6.15), (sy0, cy0), (0, 4.2), m)
    grey(c, 'spine wall east south', (9.85, 10.15), (sy0, dk - 1.3), (0, 4.2), m); grey(c, 'spine wall east north', (9.85, 10.15), (dk + 1.3, sy1), (0, 4.2), m)
    grey(c, 'spine wall east lintel', (9.85, 10.15), (dk - 1.3, dk + 1.3), (2.6, 4.2), m)
    for i, (x, y, z) in enumerate(((8, -45, 4.1), (8, -40, 4.1), (-14, YF, 4.9), (-22.2, -38, 4.9), (0, cy0 + 2.4, 5.8))):
        ld = bpy.data.lights.new('GREY light %d' % i, 'AREA'); ld.energy = 200; ld.size = 1.5; lo = bpy.data.objects.new('GREY light %d' % i, ld); lo.location = (x, y, z); c.objects.link(lo)
    # waste threshold through the reactor east wall opening (module x 10.8..11.62, y 1.6..5.6): floor, jambs either side of the 3.0 m receiving door, lintel
    oy = DY + 3.6
    grey(c, 'waste threshold floor', (10.8, 11.62), (oy - 2.0, oy + 2.0), (-0.3, 0.0), m)
    grey(c, 'waste jamb south', (10.8, 11.62), (oy - 2.0, oy - 1.5), (0, 5.0), m); grey(c, 'waste jamb north', (10.8, 11.62), (oy + 1.5, oy + 2.0), (0, 5.0), m)
    grey(c, 'waste lintel', (10.8, 11.62), (oy - 1.5, oy + 1.5), (3.2, 5.0), m)
    L.add_condenser_stair(root)
    print('GREYBOX parts', len(c.objects))
BM.add_door_placeholders = post_build_gb

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if '--output' not in a: raise SystemExit('give --output <scratch path>; this test never writes combined_map.blend')
    out = a[a.index('--output') + 1]
    if os.path.abspath(out) == os.path.join(HERE, 'combined_map.blend'): raise SystemExit('refusing to overwrite combined_map.blend')
    BM.build('compliance-dock', out)
