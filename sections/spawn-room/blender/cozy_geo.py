#!/usr/bin/env python3
"""
Shared low-poly geometry kit for the spawn-room cozy pass (Blender 5.2 / bpy).

Everything is built with bmesh from a handful of primitives that give real
silhouettes at low triangle counts:

    lathe   revolve an (r, z) profile      mugs, bottles, shades, poufs, hats
    tube    sweep a circle along a path    handles, hose, cables, hanger wire
    pillow  inflated square cushion        cushions
    ribbon  thin cloth swept along a line  hung towels, scarves
    prism   extruded 2D polygon            pennants, slipper soles
    box     lightly bevelled block         frames, books, boards

Local frame for floor props: base on z = 0, centred on x/y.
"""

import math

import bpy
import bmesh  # noqa: E402  (resolves only after bpy is imported)
from mathutils import Matrix, Vector

HEX = {
    "mustard": "#E3A22F", "coral": "#E0654A", "navy": "#2B3350", "denim": "#6079AD",
    "blush": "#E9B7A5", "olive": "#8A9A5B", "lilac": "#A99BC8", "white": "#ECE9F0",
    "charcoal": "#30323C", "walnut": "#6B4028", "oak": "#B98A56", "brass": "#C89B3C",
    "cork": "#B98A5B", "paper": "#F1EEF4", "sky": "#8FB4E3", "rose": "#D9788E",
    "ink": "#1D2238", "steel": "#9AA0AE", "glass": "#BFD4F0", "khaki": "#8B8460",
    "forest": "#3F5B48", "brick": "#A2483A", "coffee": "#2A1A12", "cream_paper": "#E8E2D6",
    "hazard": "#F2C230", "leaf1": "#4F7D4B", "leaf2": "#63915A", "leaf3": "#3E6642",
    "terracotta": "#C5714F", "pot_grey": "#8E93A0",
}
_mats = {}


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(key):
    h = HEX[key].lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def mat(key, rough=0.6, metal=0.0, emit=0.0):
    name = "COZY_%s_%d_%d_%d" % (key, rough * 100, metal * 100, emit)
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgb = hex_rgb(key)
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1.0)
        b.inputs["Emission Strength"].default_value = emit
    _mats[name] = m
    return m


class B:
    """Tiny bmesh prop builder."""

    def __init__(self):
        self.bm = bmesh.new()
        self.mats = []

    # -- bookkeeping
    def _idx(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def _fin(self, verts, m, smooth=True):
        i = self._idx(m)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = i
            f.smooth = smooth

    def _xf(self, verts, rot=None, pos=(0, 0, 0)):
        if rot is not None:
            bmesh.ops.rotate(self.bm, verts=verts, cent=(0, 0, 0), matrix=rot)
        bmesh.ops.translate(self.bm, vec=Vector(pos), verts=verts)

    # -- primitives
    def box(self, size, pos, m, bevel=0.004, rot=None, seg=2, taper_top=0.0):
        bevel = min(bevel, min(size) * 0.3)
        vs = bmesh.ops.create_cube(self.bm, size=1.0)["verts"]
        bmesh.ops.scale(self.bm, vec=Vector(size), verts=vs)
        if taper_top:
            for v in vs:
                if v.co.z > 0:
                    v.co.x *= 1.0 - taper_top
                    v.co.y *= 1.0 - taper_top * 0.5
        self._xf(vs, rot, pos)
        self._fin(vs, m, smooth=bevel > 0)
        if bevel > 0:
            edges = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(self.bm, geom=edges, offset=bevel, segments=seg, affect="EDGES")

    def cyl(self, r, h, pos, m, r2=None, seg=16, axis="Z"):
        vs = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=seg,
                                   radius1=r, radius2=r if r2 is None else r2, depth=h)["verts"]
        if axis == "X":
            self._xf(vs, Matrix.Rotation(math.pi / 2, 3, "Y"), Vector(pos) + Vector((h / 2, 0, 0)))
        elif axis == "Y":
            self._xf(vs, Matrix.Rotation(-math.pi / 2, 3, "X"), Vector(pos) + Vector((0, h / 2, 0)))
        else:
            self._xf(vs, None, Vector(pos) + Vector((0, 0, h / 2)))
        self._fin(vs, m)

    def sph(self, r, pos, m, scale=(1, 1, 1), seg=12, ring=8):
        vs = bmesh.ops.create_uvsphere(self.bm, u_segments=seg, v_segments=ring, radius=r)["verts"]
        bmesh.ops.scale(self.bm, vec=Vector(scale), verts=vs)
        self._xf(vs, None, pos)
        self._fin(vs, m)

    def lathe(self, profile, pos, m, seg=20, rot=None, scale=(1, 1, 1), smooth=True):
        """Revolve [(r, z), ...] (bottom to top) around z. r == 0 points collapse to one vertex."""
        rows = []
        for (r, z) in profile:
            if r < 1e-6:
                rows.append([self.bm.verts.new((0.0, 0.0, z))] * seg)
            else:
                rows.append([self.bm.verts.new((r * math.cos(2 * math.pi * i / seg),
                                                r * math.sin(2 * math.pi * i / seg), z))
                             for i in range(seg)])
        allv = []
        for j in range(len(rows) - 1):
            for i in range(seg):
                a, b = rows[j][i], rows[j][(i + 1) % seg]
                c, d = rows[j + 1][(i + 1) % seg], rows[j + 1][i]
                quad = [v for k, v in enumerate((a, b, c, d)) if v not in (a, b, c, d)[:k]]
                if len(quad) >= 3:
                    try:
                        self.bm.faces.new(quad)
                    except ValueError:
                        pass
        for row in rows:
            allv.extend(row)
        allv = list({v for v in allv if v.is_valid})
        if scale != (1, 1, 1):
            bmesh.ops.scale(self.bm, vec=Vector(scale), verts=allv)
        self._xf(allv, rot, pos)
        self._fin(allv, m, smooth)
        return allv

    def tube(self, path, radius, m, seg=8, caps=True):
        """Sweep a circle along a polyline; radius is a number or f(t in 0..1)."""
        pts = [Vector(p) for p in path]
        n = len(pts)
        rf = radius if callable(radius) else (lambda t: radius)
        tangents = []
        for i in range(n):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, n - 1)]
            t = (b - a)
            tangents.append(t.normalized() if t.length > 1e-9 else Vector((0, 0, 1)))
        ref = Vector((0, 0, 1)) if abs(tangents[0].z) < 0.9 else Vector((1, 0, 0))
        normal = tangents[0].cross(ref).normalized()
        rings = []
        for i in range(n):
            tan = tangents[i]
            normal = (normal - tan * normal.dot(tan))
            normal = normal.normalized() if normal.length > 1e-9 else tan.orthogonal().normalized()
            binorm = tan.cross(normal).normalized()
            r = rf(i / max(n - 1, 1))
            ring = [self.bm.verts.new(pts[i] + (normal * math.cos(2 * math.pi * k / seg)
                                                + binorm * math.sin(2 * math.pi * k / seg)) * r)
                    for k in range(seg)]
            rings.append(ring)
        verts = [v for ring in rings for v in ring]
        for i in range(n - 1):
            for k in range(seg):
                self.bm.faces.new((rings[i][k], rings[i][(k + 1) % seg],
                                   rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
        if caps:
            for ring in (rings[0], rings[-1]):
                try:
                    self.bm.faces.new(ring)
                except ValueError:
                    pass
        self._fin(verts, m)

    def pillow(self, w, d, h, pos, m, n=9, rot=None, seam=0.004):
        """Inflated cushion: pinched at the edge seam, fullest at the centre."""
        top = {}
        bot = {}
        for i in range(n + 1):
            for j in range(n + 1):
                x = (i / n - 0.5) * w
                y = (j / n - 0.5) * d
                u = 1 - abs(2 * x / w) ** 2.6
                v = 1 - abs(2 * y / d) ** 2.6
                z = (h / 2) * (max(u, 0) * max(v, 0)) ** 0.55
                top[(i, j)] = self.bm.verts.new((x, y, seam + z))
                edge = i in (0, n) or j in (0, n)
                # the rim is a single shared seam, so the shell stays closed with no sliver faces
                bot[(i, j)] = top[(i, j)] if edge else self.bm.verts.new((x, y, seam - z))
        for i in range(n):
            for j in range(n):
                self.bm.faces.new((top[(i, j)], top[(i + 1, j)], top[(i + 1, j + 1)], top[(i, j + 1)]))
                self.bm.faces.new((bot[(i, j + 1)], bot[(i + 1, j + 1)], bot[(i + 1, j)], bot[(i, j)]))
        vs = list({v for v in list(top.values()) + list(bot.values())})
        self._xf(vs, rot, Vector(pos) + Vector((0, 0, h / 2 + seam)))
        self._fin(vs, m)

    def ribbon(self, profile, x0, x1, thick, m):
        """Thin cloth: 2D side profile [(y, z), ...] extruded along x, with thickness."""
        def offset_line(pts, d):
            out = []
            for i, (y, z) in enumerate(pts):
                a = pts[max(i - 1, 0)]
                b = pts[min(i + 1, len(pts) - 1)]
                ty, tz = b[0] - a[0], b[1] - a[1]
                L = math.hypot(ty, tz) or 1.0
                out.append((y - tz / L * d, z + ty / L * d))
            return out

        outer = offset_line(profile, thick / 2)
        inner = offset_line(profile, -thick / 2)
        loop = outer + inner[::-1]
        ends = []
        for x in (x0, x1):
            ends.append([self.bm.verts.new((x, y, z)) for (y, z) in loop])
        n = len(loop)
        for k in range(n):
            self.bm.faces.new((ends[0][k], ends[0][(k + 1) % n], ends[1][(k + 1) % n], ends[1][k]))
        for ring in ends:
            try:
                self.bm.faces.new(ring)
            except ValueError:
                pass
        self._fin(ends[0] + ends[1], m)

    def prism(self, pts, depth, m, z0=0.0):
        """Extrude a 2D polygon (x, y) along +z from z0."""
        vs = [self.bm.verts.new((x, y, z0)) for x, y in pts]
        face = self.bm.faces.new(vs)
        ext = bmesh.ops.extrude_face_region(self.bm, geom=[face])
        nv = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(self.bm, vec=(0, 0, depth), verts=nv)
        self._fin(vs + nv, m, smooth=False)

    # -- output
    def build(self, name, floor_normalize=True):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        if floor_normalize and self.bm.verts:
            z = min(v.co.z for v in self.bm.verts)
            bmesh.ops.translate(self.bm, vec=(0, 0, -z), verts=self.bm.verts)
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for m in self.mats:
            mesh.materials.append(m)
        return bpy.data.objects.new(name, mesh)


def arc(cx, cy, cz, r, a0, a1, n=10, plane="XZ"):
    """Points along a circular arc (degrees) in the XZ or XY plane."""
    pts = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / (n - 1))
        if plane == "XZ":
            pts.append((cx + r * math.cos(a), cy, cz + r * math.sin(a)))
        else:
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
    return pts


def tri_count(obj):
    me = obj.data
    me.calc_loop_triangles()
    return len(me.loop_triangles)
