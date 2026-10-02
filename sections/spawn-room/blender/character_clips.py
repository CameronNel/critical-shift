#!/usr/bin/env python3
"""
Gameplay clips for the crew worker (the P0 set), built as keyed poses on character_rig's two-pass composer: legs and
arms are IK to the keyed targets, so a planted foot stays planted and a hand on a handle stays on it.

A clip is a list of keys (t from 0 to 1, pose). A key lists only the channels that change; the rest carry over from the
key before (the first key starts from STAND). Every scalar channel is interpolated with a monotone cubic, so nothing
overshoots (a hand that reaches a handle stops on it) and equal neighbouring keys hold; loops interpolate periodically.
One-shots start and end on the pose the game blends from and to (STAND or CARRY). Gait clips take their legs, hips and
torso from a character_rig gait and add the keyed channels on top.

Channels (metres and degrees in armature space; the worker faces +Y and its own left is -X):
    hips          (x, y, z)              pelvis offset from rest
    pelvis        (bend, side, twist)    bend + forward, side + leans to its right, twist + turns to its left
    spine, chest  (bend, side, twist)    each on top of the bone below
    head          (bend, side, twist)    on top of the chest (bend + looks down); the neck takes half
    L, R          (x, y, z)              where the mitten closes; Ls/Rs 1 = rides on the chest (rest coordinates),
                                         0 = fixed in the world; Lb/Rb 1 = held on the prop at the clip's grip point
    Lp, Rp        (x, y, z)              elbow pole direction, chest space
    Lsh, Rsh      degrees                shoulder shrug (+ up)
    Lw, Rw        degrees                wrist flex (+ bends the same way as the elbow)
    lf, rf        (x, y, z, pitch, yaw)  ankle; pitch + toes up, yaw + toes turn to its left
    belly, pack   degrees                added to the automatic lag (the belly follows the hips' vertical acceleration)
    prop          (x, y, z, bend, side, twist)  the clip's prop (or held tool); pk 1 = rides on the chest, 0 = world

Props are preview-only (PROPS, for the renderer); a prop that is a hand tool drives the rig's Tool bone instead.
"""

import math

from mathutils import Matrix, Vector

import character_rig as RIG
from character_rig import SIDES, SX, _ankle, _rot, _slerp3

FPS = 24
_SH = {s: RIG.SEGMENTS[s + "UpperArm"][0] for s, _ in SIDES}            # shoulder joints at rest
_SHB = {s: RIG.SEGMENTS[s + "Shoulder"][0] for s, _ in SIDES}


def _grip0(side):
    h, t = RIG.SEGMENTS[side + "Hand"]
    return h + (t - h).normalized() * RIG._HAND_GRIP


def M(x, side):
    """Mirror a right-side (+X) position to `side`."""
    return (x[0] * SX[side], x[1], x[2])


HANG = (0.40, 0.12, 0.665)                       # right mitten hanging relaxed, its cuff clear of the hip and pouches
POLE_HANG = (1.0, 0.3, 0.0)                      # elbow out, a little forward: clears the hip and the back
POLE_REACH = (0.7, -0.3, -1.0)                   # elbow out and down (reaching forward)

STAND = {
    "hips": (0.0, 0.0, -0.003), "pelvis": (0.0, 0.0, 0.0), "spine": (-1.5, 0.0, 0.0), "chest": (0.0, 0.0, 0.0),
    "head": (0.0, 0.0, 0.0), "belly": 0.0, "pack": 0.0, "prop": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), "pk": 0.0,
}
for _s, _x in SIDES:
    _k = _s[0]
    STAND.update({_k: M(HANG, _s), _k + "s": 1.0, _k + "b": 0.0, _k + "p": M(POLE_HANG, _s), _k + "sh": 0.0,
                  _k + "w": 0.0})
    STAND[_k.lower() + "f"] = tuple(RIG.ANKLE_REST[_s]) + (0.0, -_x * RIG.TOE_OUT)
CHANNELS = list(STAND)


def pose(base=None, **kw):
    out = dict(base or {})
    out.update(kw)
    return out


def _brot(a):
    bend, side, twist = a
    return _rot("Z", twist) @ _rot("Y", side) @ _rot("X", -bend)


def _flat(v):
    return list(v) if isinstance(v, (tuple, list)) else [v]


# ------------------------------------------------------------------------------------------------------ interpolation

def _slopes(ts, vs):
    """Fritsch-Carlson monotone slopes (interior points; the ends are filled by the caller)."""
    n = len(ts)
    h = [ts[i + 1] - ts[i] for i in range(n - 1)]
    d = [(vs[i + 1] - vs[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    return m


def _sorted(keys):
    """Keys in time order; keys at the same time merge (the later one wins)."""
    out = []
    for t, p in sorted(keys, key=lambda k: k[0]):
        if out and abs(out[-1][0] - t) < 1e-9:
            out[-1] = (out[-1][0], dict(out[-1][1], **p))
        else:
            out.append((float(t), dict(p)))
    return out


class Track:
    """All channels of a clip as monotone cubic splines over t in [0, 1]."""

    def __init__(self, keys, loop):
        full, cur = [], dict(STAND)
        for t, p in _sorted(keys):
            for k in p:
                if k not in STAND:
                    raise KeyError("unknown channel %r" % k)
            cur = dict(cur)
            cur.update(p)
            full.append((float(t), cur))
        if loop:
            if full[0][0] != 0.0:
                raise ValueError("a loop starts at t=0")
            if full[-1][0] < 1.0:
                full.append((1.0, full[0][1]))
        self.loop = loop
        self.ts = [t for t, _ in full]
        self.cols = {c: list(zip(*[_flat(p[c]) for _, p in full])) for c in CHANNELS}
        self.kind = {c: isinstance(STAND[c], tuple) for c in CHANNELS}
        self.m = {}
        for c, cols in self.cols.items():
            self.m[c] = [self._prep(list(vs)) for vs in cols]

    def _prep(self, vs):
        ts = self.ts
        if len(ts) == 1:
            return [0.0]
        if self.loop:
            ext_t = [ts[-2] - 1.0] + ts + [1.0 + ts[1]]
            ext_v = [vs[-2]] + vs + [vs[1]]
            return _slopes(ext_t, ext_v)[1:-1]
        return _slopes(ts, vs)                    # one-shot: zero slope at both ends (eases in and out)

    def at(self, t):
        ts = self.ts
        if self.loop:
            t %= 1.0
        t = min(max(t, ts[0]), ts[-1])
        i = 0
        while i < len(ts) - 2 and t > ts[i + 1]:
            i += 1
        out = {}
        if len(ts) == 1:
            for c, cols in self.cols.items():
                v = [col[0] for col in cols]
                out[c] = tuple(v) if self.kind[c] else v[0]
            return out
        h = ts[i + 1] - ts[i]
        u = (t - ts[i]) / h
        u2, u3 = u * u, u * u * u
        h00, h10, h01, h11 = 2 * u3 - 3 * u2 + 1, u3 - 2 * u2 + u, -2 * u3 + 3 * u2, u3 - u2
        for c, cols in self.cols.items():
            ms = self.m[c]
            v = [col[i] * h00 + ms[j][i] * h * h10 + col[i + 1] * h01 + ms[j][i + 1] * h * h11
                 for j, col in enumerate(cols)]
            out[c] = tuple(v) if self.kind[c] else v[0]
        return out


# ------------------------------------------------------------------------------------------------------ gaits

def gait_foot(p, g):
    """(flat-ankle y, sole clearance, pitch) of one foot at leg phase p (character_rig._run_foot with a slower heel
    roll and a later heel lift, for walking)."""
    s, (c0, c1) = g["duty"], g["stride"]
    v = (c1 - c0) / s
    lift = g.get("lift", 0.45) * s
    if p <= s:
        pitch = g["land"] * RIG._ss(g.get("heel", 0.06), 0.0, p) - g["push"] * (max(0.0, p - lift) / (s - lift)) ** 2
        return c0 + v * p, 0.0, pitch
    keys = [(s, Vector((c1, 0.0, -g["push"])), Vector((v, 0.0, -2 * g["push"] / (s - lift))))]
    keys += [(k[0], Vector(k[1:]), None) for k in g["swing"]]
    keys.append((1.0, Vector((c0, 0.0, g["land"])), Vector((v, -0.6, 0.0))))
    c, clear, pitch = RIG._hermite(keys, p)
    return c, max(0.0, clear), pitch


def gait_feet(q, g):
    """Forward/backward gaits: both feet on parallel tracks `width` from the middle, the right foot striking at q=0."""
    feet = {}
    for side, sx in SIDES:
        c, clear, pitch = gait_foot((q + (0.0 if side == "Right" else 0.5)) % 1.0, g)
        y, z = _ankle(c, clear, pitch)
        feet[side] = (Vector((sx * g["width"], y, z)), pitch)
    return feet


# Deliberate gaits: strides 25 % longer than a first pass (RIG.restride), the hips lower to reach them, a fuller heel
# roll and push-off, and more hip sway; every gait loops over one stride with the right foot striking at its start.
GAIT_WALK = RIG.restride(dict(strides=1, duty=0.60, stride=(0.19, -0.19), land=16.0, push=26.0, width=0.135, heel=0.10,
                              lift=0.55, swing=[(0.66, -0.17, 0.035, -26), (0.75, -0.05, 0.075, -6),
                                                (0.84, 0.09, 0.065, 6), (0.93, 0.18, 0.03, 13)],
                              hips=[(0.0, -0.058), (0.14, -0.063), (0.55, -0.026), (1.0, -0.058)],
                              lean=-3.0, yaw=8.0, roll=4.5, waddle=2.5, sway=0.036, nod=1.8, belly=7.0, pack=3.5))
GAIT_CARRY = dict(RIG.with_stride(GAIT_WALK, 0.19, -0.19), yaw=3.5, roll=4.5, waddle=3.0, sway=0.030, nod=1.2,
                  lean=2.0, hips=[(0.0, -0.064), (0.14, -0.068), (0.55, -0.040), (1.0, -0.064)])
GAIT_SPRINT = RIG.restride(dict(RIG.GAIT_CARTOON, stride=(0.10, -0.31), duty=0.32, lean=-9.0, push=32.0,
                                swing=[(0.43, -0.34, 0.09, -44), (0.54, -0.27, 0.28, -36), (0.66, -0.05, 0.33, -10),
                                       (0.78, 0.14, 0.22, 8), (0.90, 0.20, 0.07, 12)],
                                hips=[(0.0, -0.030), (0.30, -0.066), (0.70, 0.012), (0.85, 0.022), (1.0, -0.030)]))
GAIT_JOG = RIG.restride(dict(RIG.GAIT_PLAIN, stride=(0.06, -0.20), lean=-4.0, yaw=4.5, roll=4.5, waddle=3.0,
                             hips=[(0.0, -0.040), (0.30, -0.060), (0.72, -0.004), (0.86, 0.000), (1.0, -0.040)],
                             swing=[(0.45, -0.25, 0.05, -34), (0.56, -0.20, 0.12, -26), (0.68, -0.05, 0.15, -8),
                                    (0.80, 0.08, 0.12, 6), (0.90, 0.13, 0.04, 10)]))


def gait_body(g, feet_fn=None):
    """character_rig._run_body with this module's foot planner (and an optional replacement for it)."""
    def body(ph):
        D, loc, _ = RIG._run_body(ph, g)
        q = (ph * g["strides"]) % 1.0
        return D, loc, (feet_fn or gait_feet)(q, g)
    return body


def strafe_feet(direction, home=0.215, amp=0.10, duty=0.6, clear=0.06):
    """Side-stepping feet (direction -1 = to its left, +1 = to its right): each foot lands towards the travel side and
    slides back under the body, half a cycle apart, never crossing (inner ankle gap stays ~0.25 m)."""
    def feet(q, g):
        out = {}
        for side, sx in SIDES:
            p = (q + (0.0 if side == "Right" else 0.5)) % 1.0
            x0, x1 = sx * home + direction * amp, sx * home - direction * amp
            if p <= duty:
                x, z, pitch = x0 + (x1 - x0) * (p / duty), 0.0, 0.0
            else:
                u = (p - duty) / (1 - duty)
                s = u * u * (3 - 2 * u)
                x, z, pitch = x1 + (x0 - x1) * s, clear * math.sin(math.pi * u) ** 1.5, -10 * math.sin(math.pi * u)
            y, zz = _ankle(0.014, z, pitch)
            out[side] = (Vector((x, y, zz)), pitch)
        return out
    return feet


def turn_feet(direction, amp=14.0, duty=0.6, clear=0.06):
    """Turning on the spot (direction +1 = to its left): the planted feet turn back under the body while the body
    turns, each swing foot steps round to its new place; feet half a cycle apart."""
    def feet(q, g):
        out = {}
        for side, sx in SIDES:
            p = (q + (0.0 if side == "Right" else 0.5)) % 1.0
            a0, a1 = direction * amp, -direction * amp
            if p <= duty:
                a, z = a0 + (a1 - a0) * (p / duty), 0.0
            else:
                u = (p - duty) / (1 - duty)
                a, z = a1 + (a0 - a1) * u * u * (3 - 2 * u), clear * math.sin(math.pi * u) ** 1.5
            home = Vector((sx * (RIG.STANCE + 0.015), 0.014, 0.13))
            pos = _rot("Z", a) @ home
            out[side] = (Vector((pos.x, pos.y, 0.13 + z)), _rot("Z", a))
        return out
    return feet


def in_place_body(g):
    """Body for stepping on the spot (strafe, turn): a walk's sway, bob and roll without the forward-walk pelvis yaw."""
    def body(ph):
        tp = 2 * math.pi
        q = (ph * g["strides"]) % 1.0
        u = (2 * q) % 1.0
        st = math.sin(tp * (q + 0.1))
        D = {"Root": Matrix.Identity(3)}
        D["Hips"] = _rot("Y", -g["roll"] * st) @ _rot("X", g["lean"] * 0.4)
        D["Spine"] = D["Hips"] @ _rot("Y", g["roll"] * 0.6 * st) @ _rot("X", g["lean"] * 0.3)
        D["Chest"] = D["Spine"] @ _rot("Y", g["roll"] * 0.3 * st)
        D["Head"] = _rot("X", -g["nod"] * math.cos(tp * (u - 0.4)))
        D["Neck"] = _slerp3(D["Chest"], D["Head"], 0.5)
        D["Belly"] = D["Spine"] @ _rot("X", g["belly"] * math.sin(tp * (u - 0.42)))
        D["Pack"] = D["Chest"] @ _rot("X", g["pack"] * math.sin(tp * (u - 0.5)))
        loc = Vector((g["sway"] * st, 0.0, -0.025 + 0.012 * math.cos(tp * (u - 0.55))))
        return D, loc, g["feet"](q, g)
    return body


GAIT_STEP = dict(strides=1, lean=-2.0, roll=3.0, nod=1.0, belly=4.0, pack=3.0, sway=0.03)


# ------------------------------------------------------------------------------------------------------ clips

PROPS = {}      # action name -> {"kind", "dims", "frames": {frame: 4x4 armature-space matrix}, "static": [...]}
REACH = {}      # action name -> (worst distance from a mitten to its target in metres, frame, side), for checks


class Clip:
    def __init__(self, name, frames, keys, loop=False, gait=None, body=None, grips=None, prop=None, tool=None,
                 static=(), arms=None, doc=""):
        self.name, self.frames, self.loop, self.doc = name, frames, loop, doc
        self.track = Track(keys, loop)
        self.gait, self.body_fn, self.grips = gait, body, grips or {}
        self.prop, self.tool, self.static, self.arms_fn = prop, tool, list(static), arms

    def pose(self, ph):
        return self.track.at(ph)

    def hips_acc(self, ph):
        """Vertical acceleration of the keyed hips (m/s^2)."""
        e = 1.0 / self.frames
        z = [self.pose(ph + d)["hips"][2] for d in (-e, 0.0, e)]
        dt = e * self.frames / FPS
        return (z[0] - 2 * z[1] + z[2]) / (dt * dt)

    # ---- body
    def body(self, ph):
        P = self.pose(ph)
        if self.body_fn or self.gait:
            Dg, loc, feet = (self.body_fn or gait_body(self.gait))(ph)
            D = {"Root": Matrix.Identity(3)}
            D["Hips"] = _brot(P["pelvis"]) @ Dg["Hips"]
            D["Spine"] = D["Hips"] @ Dg["Hips"].inverted() @ Dg["Spine"] @ _brot(P["spine"])
            D["Chest"] = D["Spine"] @ Dg["Spine"].inverted() @ Dg["Chest"] @ _brot(P["chest"])
            D["Head"] = D["Chest"] @ Dg["Chest"].inverted() @ Dg["Head"] @ _brot(P["head"])
            D["Neck"] = _slerp3(D["Chest"], D["Head"], 0.5)
            D["Belly"] = D["Spine"] @ Dg["Spine"].inverted() @ Dg["Belly"] @ _rot("X", P["belly"])
            D["Pack"] = D["Chest"] @ Dg["Chest"].inverted() @ Dg["Pack"] @ _rot("X", P["pack"])
            return D, loc + Vector(P["hips"]) - Vector(STAND["hips"]), feet
        D = {"Root": Matrix.Identity(3)}
        D["Hips"] = _brot(P["pelvis"])
        D["Spine"] = D["Hips"] @ _brot(P["spine"])
        D["Chest"] = D["Spine"] @ _brot(P["chest"])
        D["Head"] = D["Chest"] @ _brot(P["head"])
        D["Neck"] = _slerp3(D["Chest"], D["Head"], 0.5)
        acc = self.hips_acc(ph)
        D["Belly"] = D["Spine"] @ _rot("X", max(-16.0, min(16.0, -1.2 * acc)) + P["belly"])
        D["Pack"] = D["Chest"] @ _rot("X", max(-8.0, min(8.0, 0.5 * acc)) + P["pack"])
        feet = {}
        for side, _ in SIDES:
            x, y, z, pitch, yaw = P[side[0].lower() + "f"]
            feet[side] = (Vector((x, y, z)), _rot("Z", yaw) @ _rot("X", pitch))
        return D, Vector(P["hips"]), feet

    # ---- prop and arms
    def prop_matrix(self, P, chest_def):
        x, y, z, b, s, t = P["prop"]
        Mw = Matrix.Translation((x, y, z)) @ _brot((b, s, t)).to_4x4()
        k = P["pk"]
        if k <= 0.0:
            return Mw
        Mc = chest_def @ Mw
        if k >= 1.0:
            return Mc
        loc = Mw.to_translation().lerp(Mc.to_translation(), k)
        rot = Mw.to_quaternion().slerp(Mc.to_quaternion(), k)
        return Matrix.Translation(loc) @ rot.to_matrix().to_4x4()

    def arms(self, arm):
        if self.arms_fn:                          # a whole-arm routine of character_rig (e.g. the \\o/ arms)
            return self.arms_fn(arm)

        def solve(ph, D, ev, chest_def):
            P = self.pose(ph)
            C3 = chest_def.to_3x3()
            Mp = self.prop_matrix(P, chest_def) if (self.prop or self.tool) else None
            if self.prop and Mp is not None:
                rec = PROPS.setdefault(self.name, {"kind": self.prop[0], "dims": self.prop[1], "frames": {},
                                                   "static": self.static})
                rec["frames"][round(ph * self.frames) % (self.frames if self.loop else self.frames + 1)] = Mp.copy()
            elif self.static:
                PROPS.setdefault(self.name, {"kind": None, "dims": None, "frames": {}, "static": self.static})
            free = {}
            for side, sx in SIDES:
                k = side[0]
                own = Vector(P[k])
                s = P[k + "s"]
                tgt = (chest_def @ own) * s + own * (1.0 - s)
                b = P[k + "b"]
                if b > 0.0 and Mp is not None and k in self.grips:
                    tgt = tgt.lerp(Mp @ Vector(self.grips[k]), b)
                pole = C3 @ Vector(P[k + "p"])
                D[side + "Shoulder"] = D["Chest"] @ _rot("Y", -sx * P[k + "sh"])
                S = chest_def @ _SHB[side] + D[side + "Shoulder"] @ (_SH[side] - _SHB[side])
                wrist = tgt
                lb = arm.data.bones[side + "LowerArm"]
                rl = (lb.tail_local - lb.head_local).normalized()
                for _ in range(3):                # aim the wrist so the mitten, not the wrist, closes on the target
                    Du, Dl = RIG._ik_arm(arm, side, S, wrist, pole)
                    wrist = tgt - (Dl @ rl) * RIG._HAND_GRIP
                D[side + "UpperArm"], D[side + "LowerArm"] = Du, Dl
                ub = arm.data.bones[side + "UpperArm"]
                reach = (S + Du @ (ub.tail_local - ub.head_local) + Dl @ (lb.tail_local - lb.head_local)
                         + (Dl @ rl) * RIG._HAND_GRIP - tgt).length
                f = round(ph * self.frames)
                if reach > REACH.get(self.name, (0.0, 0, ""))[0]:
                    REACH[self.name] = (reach, f, side)
                w = P[k + "w"]
                if abs(w) > 1e-3:
                    ax = (Du @ (ub.tail_local - ub.head_local)).cross(Dl @ rl)
                    ax = ax.normalized() if ax.length > 1e-4 else C3 @ Vector((1, 0, 0))
                    D[side + "Hand"] = Matrix.Rotation(math.radians(w), 3, ax) @ Dl
                else:
                    D[side + "Hand"] = Dl
                free[side] = s > 0.5 and b < 0.5          # hanging or swinging on the chest, holding nothing
            D["_free"] = free
            return Mp if self.tool else None
        return solve

    def build(self, arm):
        PROPS.pop(self.name, None)
        REACH.pop(self.name, None)
        act = RIG._compose(arm, self.frames, self.name, self.body, self.arms(arm), loop=self.loop)
        act["cs_doc"] = self.doc
        return act


CLIPS = {}


def clip(name, frames, keys, **kw):
    c = Clip(name, frames, keys, **kw)
    CLIPS[name] = c
    return c


def via(keys, t, **over):
    """`keys` plus a key at `t` taken from their own curves with the channels in `over` replaced, e.g. to take a mitten
    round the belly on its way to a reach without changing the rest of the motion."""
    return keys + [(t, dict(Track(keys, False).at(t), **over))]


def T(f, frames):
    """Key time of frame f."""
    return f / frames


def cycle(n, fn):
    """Loop keys sampled from fn(t) (a pose dict) at n even steps."""
    return [(i / n, fn(i / n)) for i in range(n)]


def arms_swing(t, fwd=0.21, back=0.16, lag=0.05, z=0.665, out=0.385, hold=None):
    """Walking arm swing in chest space, the left arm forward when the right foot strikes (t = 0)."""
    out_ = {}
    for side, sx in SIDES:
        if hold and side[0] in hold:
            continue
        a = math.cos(2 * math.pi * (t - lag - (0.0 if side == "Left" else 0.5)))
        y = 0.08 + (fwd if a > 0 else back) * a
        out_[side[0]] = (sx * (out - 0.01 * a), y, z + 0.03 * a * a + (0.03 * a if a > 0 else 0.0))
    return out_


def foot(side, y=0.014, clear=0.0, pitch=0.0, x=None, yaw=None):
    """Ankle channel of a foot whose flat-ankle y is `y`, sole `clear` above the floor, pitched about its heel/toe
    (turned out by the rig's TOE_OUT unless `yaw` is given)."""
    yy, zz = _ankle(y, clear, pitch)
    return (RIG.ANKLE_REST[side].x if x is None else x, yy, zz, pitch, -SX[side] * RIG.TOE_OUT if yaw is None else yaw)


# ------------------------------------------------------------------------------------------------------ locomotion

# IDLE is keyed on the same standing pose (STAND) every one-shot starts and ends on, so the game can blend between them
# without the arms drifting. It replaces character_rig's procedural idle.
clip("IDLE", 48, cycle(8, lambda t: {
    "spine": (0.0, 0.0, 0.0),                     # _stand_body already bends the spine
    "L": M((HANG[0] + 0.004 * math.sin(2 * math.pi * (t + 0.35)), HANG[1] + 0.012 * math.sin(2 * math.pi * (t - 0.2)),
            HANG[2] + 0.004 * math.cos(2 * math.pi * t)), "Left"),
    "R": M((HANG[0] + 0.004 * math.sin(2 * math.pi * (t + 0.15)), HANG[1] + 0.012 * math.sin(2 * math.pi * t),
            HANG[2] + 0.004 * math.cos(2 * math.pi * (t + 0.2))), "Right")}), loop=True, body=RIG._stand_body,
    doc="Standing, arms hanging, breathing and a slow weight shift (48 frames).")

WALK_N = 26
clip("WALK_F", WALK_N, cycle(8, lambda t: arms_swing(t)), loop=True, gait=GAIT_WALK,
     doc="Walk forward, arms swinging (26 frames, two steps; in place, the floor moves at 0.73 m/s).")
clip("WALK_B", WALK_N, cycle(8, lambda t: dict(arms_swing(1.0 - t, fwd=0.10, back=0.10), chest=(2.0, 0.0, 0.0))),
     loop=True, body=lambda ph: gait_body(dict(GAIT_WALK, lean=0.0))(1.0 - ph),
     doc="Walk backward: the forward walk played in reverse (toe lands first), arms swinging less (26 frames, "
         "0.73 m/s).")
for _nm, _d in (("WALK_L", -1), ("WALK_R", 1)):
    clip(_nm, 18, cycle(8, lambda t, d=_d: dict(
        L=M((0.41 + 0.025 * math.sin(2 * math.pi * t), 0.11, 0.67), "Left"),
        R=M((0.41 - 0.025 * math.sin(2 * math.pi * t), 0.11, 0.67), "Right"),
        chest=(0.0, 2.0 * d, 0.0), head=(0.0, -1.5 * d, 0.0))), loop=True,
        body=in_place_body(dict(GAIT_STEP, feet=strafe_feet(_d))),
        doc="Side-step to its %s (18 frames; in place, the floor moves at 0.44 m/s)." % ("left" if _d < 0 else "right"))
for _nm, _d in (("TURN_L", 1), ("TURN_R", -1)):
    clip(_nm, 22, cycle(4, lambda t, d=_d: dict(head=(0.0, 0.0, 8.0 * d), chest=(0.0, 0.0, 3.0 * d))), loop=True,
         body=in_place_body(dict(GAIT_STEP, feet=turn_feet(_d))),
         doc="Turn on the spot to its %s by stepping (22 frames; the body turns 47 degrees per loop, 51 deg/s)."
             % ("left" if _d > 0 else "right"))
clip("SPRINT", 14, cycle(7, lambda t: {}), loop=True, gait=GAIT_SPRINT, arms=lambda arm: RIG._arms_cheer(arm),
     doc="Sprint: the cartoon \\o/ run, quicker and longer-strided (14 frames, one stride; 2.75 m/s).")

_CROUCH = dict(hips=(0.0, -0.03, -0.11), pelvis=(20.0, 0.0, 0.0), spine=(6.0, 0.0, 0.0), chest=(2.0, 0.0, 0.0),
               head=(-18.0, 0.0, 0.0))
_AIR = dict(hips=(0.0, 0.0, 0.02), pelvis=(-2.0, 0.0, 0.0), spine=(0.0, 0.0, 0.0), chest=(-2.0, 0.0, 0.0),
            head=(4.0, 0.0, 0.0), L=M((0.40, 0.10, 1.28), "Left"), R=M((0.40, 0.10, 1.28), "Right"),
            Lp=M((1.0, -0.4, -0.3), "Left"), Rp=M((1.0, -0.4, -0.3), "Right"),
            lf=(-0.15, 0.05, 0.27, -22.0, 0.0), rf=(0.15, -0.02, 0.23, -18.0, 0.0))
clip("JUMP", 17, [
    (0.0, {}),
    (T(3, 17), dict(hips=(0.0, 0.0, 0.008), pelvis=(-3.0, 0.0, 0.0), spine=(-3.0, 0.0, 0.0), head=(6.0, 0.0, 0.0),
                    L=M((0.39, 0.18, 0.74), "Left"), R=M((0.39, 0.18, 0.74), "Right"))),     # rise and gather first
    (T(7, 17), dict(hips=(0.0, -0.04, -0.15), pelvis=(25.0, 0.0, 0.0), spine=(8.0, 0.0, 0.0), chest=(3.0, 0.0, 0.0),
                    head=(-20.0, 0.0, 0.0), L=M((0.38, -0.16, 0.71), "Left"), R=M((0.38, -0.16, 0.71), "Right"))),
    (T(9, 17), dict(L=M((0.45, 0.06, 0.80), "Left"), R=M((0.45, 0.06, 0.80), "Right"))),   # arms swing past the hips
    (T(10, 17), dict(hips=(0.0, 0.01, 0.0), pelvis=(4.0, 0.0, 0.0), spine=(0.0, 0.0, 0.0), chest=(-2.0, 0.0, 0.0),
                     head=(-4.0, 0.0, 0.0), L=M((0.30, 0.28, 1.00), "Left"), R=M((0.30, 0.28, 1.00), "Right"),
                     lf=foot("Left", pitch=-26.0), rf=foot("Right", pitch=-26.0))),
    (T(12, 17), dict(hips=(0.0, 0.0, 0.015), L=M((0.36, 0.18, 1.22), "Left"), R=M((0.36, 0.18, 1.22), "Right"),
                     lf=foot("Left", clear=0.03, pitch=-34.0), rf=foot("Right", clear=0.03, pitch=-34.0))),
    (1.0, _AIR)],
    doc="Jump take-off from standing: rise and gather, crouch deep with the arms back, spring up and tuck (17 frames, "
        "ends in the FALL pose; the game moves the body up).")
clip("FALL", 20, cycle(10, lambda t: dict(
    _AIR, L=M((0.40 + 0.03 * math.sin(2 * math.pi * (2 * t)), 0.10 + 0.07 * math.cos(2 * math.pi * 2 * t),
               1.28 + 0.05 * math.sin(2 * math.pi * (t + 0.1))), "Left"),
    R=M((0.40 + 0.03 * math.sin(2 * math.pi * (2 * t + 0.4)), 0.10 + 0.07 * math.cos(2 * math.pi * (2 * t + 0.4)),
         1.28 + 0.05 * math.sin(2 * math.pi * (t + 0.6))), "Right"),
    lf=(-0.15, 0.05 + 0.04 * math.sin(2 * math.pi * t), 0.27 + 0.04 * math.cos(2 * math.pi * t), -22.0, 0.0),
    rf=(0.15, -0.02 - 0.04 * math.sin(2 * math.pi * t), 0.23 - 0.04 * math.cos(2 * math.pi * t), -18.0, 0.0),
    head=(6.0, 0.0, 0.0))), loop=True,
    doc="Falling: arms up and paddling, legs cycling a little (20 frames).")
clip("LAND", 19, [
    (0.0, dict(_AIR, hips=(0.0, 0.0, 0.0), lf=foot("Left"), rf=foot("Right"), head=(0.0, 0.0, 0.0))),
    (T(3, 19), dict(hips=(0.0, -0.05, -0.18), pelvis=(28.0, 0.0, 0.0), spine=(9.0, 0.0, 0.0), chest=(4.0, 0.0, 0.0),
                    head=(-24.0, 0.0, 0.0), L=M((0.44, 0.24, 0.88), "Left"), R=M((0.44, 0.24, 0.88), "Right"),
                    Lp=M(POLE_HANG, "Left"), Rp=M(POLE_HANG, "Right"), Lsh=5.0, Rsh=5.0)),
    (T(7, 19), dict(hips=(0.0, -0.04, -0.16), pelvis=(24.0, 0.0, 0.0), L=M((0.43, 0.20, 0.80), "Left"),
                    R=M((0.43, 0.20, 0.80), "Right"))),                                       # hold the absorb
    (T(13, 19), dict(hips=(0.0, -0.005, -0.03), pelvis=(4.0, 0.0, 0.0), spine=(0.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0),
                     head=(-3.0, 0.0, 0.0), L=M((0.37, 0.13, 0.68), "Left"), R=M((0.37, 0.13, 0.68), "Right"),
                     Lsh=0.0, Rsh=0.0)),
    (1.0, STAND)],
    doc="Landing: knees take the impact deep, a beat to absorb it, arms out for balance, back to standing (19 frames).")


# ------------------------------------------------------------------------------------------------------ carrying

CRATE = ("crate", (0.34, 0.30, 0.28))
CRATE_GRIPS = {"L": (-0.205, -0.07, -0.01), "R": (0.205, -0.07, -0.01)}  # rear of the sides
BOX_CARRY = (0.0, 0.46, 1.05, 0.0, 0.0, 0.0)      # crate in front of the chest, top edge in the first-person view
BOX_FLOOR = (0.0, 0.61, 0.15, 0.0, 0.0, 0.0)
POLE_BOX = (1.0, -0.2, -0.6)
CARRY = dict(prop=BOX_CARRY, pk=1.0, Lb=1.0, Rb=1.0, Lp=M(POLE_BOX, "Left"), Rp=M(POLE_BOX, "Right"),
             spine=(-3.5, 0.0, 0.0), chest=(-1.0, 0.0, 0.0), head=(3.0, 0.0, 0.0))
# A stooped squat: hips back and the torso bent well forward, so the arms come down in front of the (fat) knees.
_SQUAT = dict(hips=(0.0, -0.15, -0.30), pelvis=(50.0, 0.0, 0.0), spine=(20.0, 0.0, 0.0), chest=(14.0, 0.0, 0.0),
              head=(-42.0, 0.0, 0.0), Lsh=8.0, Rsh=8.0, lf=foot("Left", x=-0.25), rf=foot("Right", x=0.25))


def full_keys(keys):
    """Keys with every channel filled in (so they can be reversed or edited)."""
    out, cur = [], dict(STAND)
    for t, p in _sorted(keys):
        cur = dict(cur)
        cur.update(p)
        out.append((t, cur))
    return out


def reverse(keys):
    return [(1.0 - t, p) for t, p in reversed(full_keys(keys))]


clip("CARRY_IDLE", 48, cycle(4, lambda t: dict(
    CARRY, chest=(-1.0 + 1.2 * math.sin(2 * math.pi * t), 0.0, 0.0), hips=(0.0, 0.0, -0.004 + 0.002 * math.sin(
        2 * math.pi * (t - 0.1))), pelvis=(0.0, 1.2 * math.sin(2 * math.pi * t), 0.0))), loop=True, prop=CRATE,
    grips=CRATE_GRIPS, doc="Standing with a crate held in front of the chest, breathing (48 frames).")
clip("CARRY_WALK", WALK_N, [(0.0, CARRY)], loop=True, gait=GAIT_CARRY, prop=CRATE, grips=CRATE_GRIPS,
     doc="Walking with the crate, shorter steps and more side-to-side (26 frames, 0.58 m/s).")
clip("CARRY_RUN", 20, [(0.0, dict(CARRY, chest=(2.0, 0.0, 0.0)))], loop=True, gait=GAIT_JOG, prop=CRATE,
     grips=CRATE_GRIPS, doc="Jogging with the crate (20 frames, one stride; 1.08 m/s).")
PICKUP_KEYS = [
    (0.0, dict(prop=BOX_FLOOR)),
    (T(5, 36), dict(prop=BOX_FLOOR, head=(20.0, 0.0, 0.0), pelvis=(4.0, 0.0, 0.0), L=(-0.40, 0.14, 0.66),
                    R=(0.40, 0.14, 0.66), Ls=0.0, Rs=0.0)),          # look down at it first; hands now in the world
    (T(13, 36), dict(_SQUAT, prop=BOX_FLOOR, L=(-0.24, 0.56, 0.17), R=(0.24, 0.56, 0.17), Ls=0.0, Rs=0.0,
                     Lp=M(POLE_BOX, "Left"), Rp=M(POLE_BOX, "Right"))),
    (T(16, 36), dict(Lb=1.0, Rb=1.0)),                                                       # grip
    (T(19, 36), dict(hips=(0.0, -0.15, -0.31), pelvis=(51.0, 0.0, 0.0))),                   # brace, take the weight
    (T(27, 36), dict(hips=(0.0, -0.05, -0.12), pelvis=(12.0, 0.0, 0.0), spine=(-2.0, 0.0, 0.0), chest=(-2.0, 0.0, 0.0),
                     head=(-6.0, 0.0, 0.0), prop=(0.0, 0.56, 0.80, 0.0, 0.0, 0.0), Lsh=0.0, Rsh=0.0,
                     lf=foot("Left"), rf=foot("Right"))),
    (T(32, 36), dict(CARRY, hips=STAND["hips"], pelvis=(0.0, 0.0, 0.0), pk=0.0)),
    (1.0, dict(CARRY, hips=STAND["hips"], pelvis=(0.0, 0.0, 0.0)))]
PICKUP_KEYS = via(PICKUP_KEYS, T(9, 36), L=(-0.32, 0.42, 0.55), R=(0.32, 0.42, 0.55))    # hands in front of the knees
PICKUP_KEYS = via(PICKUP_KEYS, T(22, 36), prop=(0.0, 0.66, 0.36, 0.0, 0.0, 0.0))        # crate up clear of the knees
clip("PICKUP", 36, PICKUP_KEYS, prop=CRATE, grips=CRATE_GRIPS,
     doc="Look down, stoop and grip the crate on the floor in front, brace, and stand up with it into CARRY "
         "(36 frames).")
clip("PLACE", 36, reverse(PICKUP_KEYS), prop=CRATE, grips=CRATE_GRIPS,
     doc="From CARRY, stoop and set the crate down in front, let go and stand up (36 frames).")
_FALL_Z = [1.05 - 4.9 * (i / 24.0) ** 2 for i in range(11)]
clip("DROP", 22, [(0.0, CARRY), (T(2, 22), dict(spine=(-5.0, 0.0, 0.0), head=(6.0, 0.0, 0.0))),   # a heave up first
                  (T(4, 22), dict(pk=0.0, Lb=0.6, Rb=0.6))]
     + [(T(4 + i, 22), dict(prop=(0.0, 0.46 + 0.006 * i, max(0.15, z), 0.0, -0.8 * i, 0.0), Lb=0.0, Rb=0.0,
                            L=M((0.40, 0.30 - 0.018 * i, 0.90 - 0.025 * i), "Left"),
                            R=M((0.40, 0.30 - 0.018 * i, 0.90 - 0.025 * i), "Right"), spine=STAND["spine"],
                            Lp=STAND["Lp"], Rp=STAND["Rp"],
                            head=(14.0, 0.0, 0.0)))
        for i, z in enumerate(_FALL_Z) if i in (2, 4, 6, 8, 10)]
     + [(T(15, 22), dict(prop=(0.0, 0.53, 0.15, 0.0, -8.0, 0.0))),
        (T(18, 22), dict(head=(10.0, 0.0, 0.0))),                                              # watch it land
        (1.0, dict(STAND, prop=(0.0, 0.53, 0.15, 0.0, -8.0, 0.0)))],
     prop=CRATE, grips=CRATE_GRIPS,
     doc="Heave the carried crate up a little, let it fall in front, watch it land, drop the arms (22 frames).")


def _fly(f0, frames, p0, v, n=4, spin=0.0):
    """Keys of a released prop flying from p0 with velocity v (m/s), from frame f0 to the end."""
    out = []
    for i in range(1, n + 1):
        f = f0 + (frames - f0) * i / n
        dt = (f - f0) / FPS
        out.append((T(f, frames), dict(prop=(p0[0], p0[1] + v[1] * dt, max(0.15, p0[2] + v[2] * dt - 4.9 * dt * dt),
                                             spin * dt, 0.0, 0.0))))
    return out


clip("THROW_UNDER", 33, [
    (0.0, CARRY),
    (T(4, 33), dict(pk=0.0, prop=BOX_CARRY)),
    (T(11, 33), dict(hips=(0.0, -0.03, -0.10), pelvis=(14.0, 0.0, 0.0), spine=(6.0, 0.0, 0.0), chest=(3.0, 0.0, 0.0),
                     head=(-20.0, 0.0, 0.0), prop=(0.0, 0.52, 0.62, -26.0, 0.0, 0.0))),
    (T(13, 33), dict(hips=(0.0, -0.03, -0.095), prop=(0.0, 0.52, 0.63, -27.0, 0.0, 0.0))),     # a beat at the bottom
    (T(18, 33), dict(hips=(0.0, 0.04, 0.0), pelvis=(-3.0, 0.0, 0.0), spine=(-5.0, 0.0, 0.0), chest=(-2.0, 0.0, 0.0),
                     head=(-4.0, 0.0, 0.0), prop=(0.0, 0.56, 1.04, 10.0, 0.0, 0.0), Lb=1.0, Rb=1.0,
                     lf=foot("Left", pitch=-14.0), rf=foot("Right", pitch=-14.0))),
    (T(20, 33), dict(Lb=0.0, Rb=0.0, L=M((0.28, 0.46, 1.12), "Left"), R=M((0.28, 0.46, 1.12), "Right"), Ls=0.0, Rs=0.0,
                     lf=foot("Left"), rf=foot("Right"))),
    (T(24, 33), dict(L=M((0.30, 0.40, 1.04), "Left"), R=M((0.30, 0.40, 1.04), "Right"), hips=(0.0, 0.01, -0.01))),
    (T(30, 33), dict(L=STAND["L"], R=STAND["R"], Ls=1.0, Rs=1.0, hips=STAND["hips"], pelvis=STAND["pelvis"],
                     spine=STAND["spine"], chest=STAND["chest"], head=STAND["head"]))]
    + _fly(18, 33, (0.0, 0.56, 1.04), (0.0, 3.2, 2.6), spin=-200.0)[1:]
    + [(1.0, dict(STAND, prop=_fly(18, 33, (0.0, 0.56, 1.04), (0.0, 3.2, 2.6), spin=-200.0)[-1][1]["prop"]))],
    prop=CRATE, grips=CRATE_GRIPS,
    doc="Underhand heave: swing the crate down deep, a beat, toss it forward-up and follow through (33 frames).")
clip("THROW_OVER", 31, [
    (0.0, CARRY),
    (T(4, 31), dict(pk=0.0, prop=BOX_CARRY)),
    (T(10, 31), dict(hips=(0.0, -0.03, -0.07), pelvis=(-4.0, 0.0, 0.0), spine=(-6.0, 0.0, 0.0), chest=(-3.0, 0.0, 0.0),
                     head=(5.0, 0.0, 0.0), prop=(0.0, 0.43, 1.05, -12.0, 0.0, 0.0), Lsh=7.0, Rsh=7.0,
                     lf=foot("Left", y=-0.13), rf=foot("Right", y=0.20))),
    (T(12, 31), dict(hips=(0.0, -0.035, -0.075))),                                             # cocked, a beat
    (T(16, 31), dict(hips=(0.0, 0.07, -0.03), pelvis=(14.0, 0.0, 0.0), spine=(5.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0),
                     head=(-6.0, 0.0, 0.0), prop=(0.0, 0.62, 1.06, 8.0, 0.0, 0.0), Lb=1.0, Rb=1.0,
                     lf=foot("Left", y=-0.13, pitch=-20.0))),
    (T(18, 31), dict(Lb=0.0, Rb=0.0, L=M((0.26, 0.62, 1.20), "Left"), R=M((0.26, 0.62, 1.20), "Right"), Ls=0.0, Rs=0.0,
                     Lsh=0.0, Rsh=0.0))]
    + _fly(16, 31, (0.0, 0.62, 1.06), (0.0, 4.0, 2.2), spin=-120.0)[1:]
    + [(T(25, 31), dict(hips=STAND["hips"], pelvis=(2.0, 0.0, 0.0), spine=STAND["spine"], chest=(0.0, 0.0, 0.0),
                        head=(0.0, 0.0, 0.0), lf=foot("Left"), rf=foot("Right"), L=STAND["L"], R=STAND["R"],
                        Ls=1.0, Rs=1.0, Lp=STAND["Lp"], Rp=STAND["Rp"])),
       (1.0, dict(STAND, prop=_fly(16, 31, (0.0, 0.62, 1.06), (0.0, 4.0, 2.2), spin=-120.0)[-1][1]["prop"]))],
    prop=CRATE, grips=CRATE_GRIPS,
    doc="Chest heave: the arms are too short to lift a crate over the hood, so it is pulled back to the chest, held a "
        "beat and thrust forward-up with a long step (31 frames).")

CART = ("crate", (0.56, 0.44, 0.86))
CART_AT = (0.0, 0.66, 0.43, 0.0, 0.0, 0.0)
CART_GRIPS = {"L": (-0.23, -0.25, 0.46), "R": (0.23, -0.25, 0.46)}   # its rear corners, near the top
PUSH = dict(prop=CART_AT, Lb=1.0, Rb=1.0, Lp=M((1.0, -0.3, -0.3), "Left"), Rp=M((1.0, -0.3, -0.3), "Right"),
            pelvis=(10.0, 0.0, 0.0), spine=(6.0, 0.0, 0.0), chest=(3.0, 0.0, 0.0), head=(-14.0, 0.0, 0.0))
clip("PUSH_IDLE", 32, cycle(4, lambda t: dict(
    PUSH, hips=(0.0, -0.06, -0.035 + 0.004 * math.sin(2 * math.pi * t)),
    chest=(3.0 + 1.0 * math.sin(2 * math.pi * t), 0.0, 0.0), lf=foot("Left", y=-0.20, pitch=-16.0),
    rf=foot("Right", y=0.06))), loop=True, prop=CART, grips=CART_GRIPS,
    doc="Leaning on a crate or cart in front, braced, ready to push (32 frames).")
clip("PUSH_WALK", WALK_N, [(0.0, dict(PUSH, hips=(0.0, -0.05, 0.0)))], loop=True,
     gait=dict(RIG.with_stride(GAIT_WALK, 0.19, -0.26), lean=-6.0), prop=CART, grips=CART_GRIPS,
     doc="Pushing the crate or cart forward, leaning into it (26 frames, 0.69 m/s).")
clip("PULL_WALK", WALK_N, [(0.0, dict(PUSH, pelvis=(-3.0, 0.0, 0.0), spine=(-2.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0),
                                    head=(-2.0, 0.0, 0.0), hips=(0.0, -0.035, -0.01),
                                    prop=(0.0, 0.66, 0.43, 0.0, 0.0, 0.0)))], loop=True,
     body=lambda ph: gait_body(dict(RIG.with_stride(GAIT_WALK, 0.19, -0.19), lean=0.0, yaw=2.0, sway=0.022))(1.0 - ph),
     prop=CART, grips=CART_GRIPS,
     doc="Walking backwards hauling the crate or cart, leaning back (26 frames, 0.58 m/s).")
BODY = ("body", (0.46, 1.30, 0.30))
clip("DRAG_BODY", 30, [(0.0, dict(prop=(0.0, 1.00, 0.26, 12.0, 0.0, 0.0), Lb=1.0, Rb=1.0, hips=(0.0, -0.10, -0.10),
                                  pelvis=(30.0, 0.0, 0.0), spine=(12.0, 0.0, 0.0), chest=(6.0, 0.0, 0.0),
                                  head=(-30.0, 0.0, 0.0), Lp=M((1.0, -0.3, -0.4), "Left"),
                                  Rp=M((1.0, -0.3, -0.4), "Right")))], loop=True,
     body=lambda ph: gait_body(dict(RIG.with_stride(GAIT_WALK, 0.16, -0.16), lean=0.0, duty=0.65, width=0.20,
                                    hips=[(0.0, -0.02), (0.15, -0.025), (0.55, 0.0), (1.0, -0.02)]))(1.0 - ph),
     prop=BODY, grips={"L": (-0.17, -0.60, 0.20), "R": (0.17, -0.60, 0.20)},
     doc="Crouched, walking backwards dragging a body by the suit's shoulder straps (30 frames, 0.39 m/s).")


# ------------------------------------------------------------------------------------------------------ interactions

def static(kind, dims, loc, rot=(0.0, 0.0, 0.0)):
    """A fixed preview prop (kind, dims, 4x4 placement as nested tuples)."""
    return (kind, dims, tuple(tuple(r) for r in (Matrix.Translation(loc) @ _brot(rot).to_4x4())))


def placement(origin, zdir, side=(1.0, 0.0, 0.0)):
    """Prop channel value putting a prop's origin at `origin` with its +Z along `zdir` (+X towards `side`)."""
    e = RIG._aim(zdir, side).to_euler("XYZ")
    return tuple(origin) + (-math.degrees(e.x), math.degrees(e.y), math.degrees(e.z))


LOOK = dict(head=(18.0, 0.0, 0.0))
clip("PRESS_BUTTON", 24, via([
    (0.0, {}),
    (T(4, 24), dict(head=(10.0, 0.0, 0.0), spine=(-3.0, 0.0, 0.0), pelvis=(-2.0, 0.0, 0.0),
                    R=(0.37, 0.24, 0.92), Rs=1.0)),                                         # look, draw the hand up
    (T(9, 24), dict(LOOK, pelvis=(6.0, 0.0, 0.0), spine=(2.0, 0.0, 0.0), R=(0.22, 0.42, 1.03), Rs=0.0,
                    Rp=(0.9, -0.3, -1.0))),
    (T(11, 24), dict(R=(0.22, 0.462, 1.03), pelvis=(7.0, 0.0, 0.0))),                       # press
    (T(14, 24), dict(R=(0.22, 0.462, 1.03))),                                               # hold it in
    (T(16, 24), dict(R=(0.22, 0.42, 1.03), pelvis=(4.0, 0.0, 0.0))),
    (1.0, STAND)], T(19, 24), R=(0.33, 0.30, 0.82)),
    static=[static("panel", (0.40, 0.04, 0.32), (0.17, 0.53, 1.03)),
            static("button", (0.07, 0.04, 0.07), (0.22, 0.50, 1.03))],
    doc="Look at a wall button, draw the right hand up, reach out and press it, hold it in, let go (24 frames).")
clip("PULL_LEVER", 31, via([
    (0.0, dict(prop=(0.24, 0.66, 0.92, -40.0, 0.0, 0.0))),
    (T(4, 31), dict(head=(12.0, 0.0, 0.0), hips=(0.0, 0.0, 0.008), spine=(-3.0, 0.0, 0.0))),      # look up at it
    (T(9, 31), dict(LOOK, pelvis=(5.0, 0.0, 0.0), spine=STAND["spine"], R=(0.24, 0.42, 1.14), Rs=0.0,
                    Rp=(0.9, -0.2, -1.0))),
    (T(11, 31), dict(Rb=1.0)),
    (T(13, 31), dict(hips=(0.0, 0.0, -0.003))),                                                   # grip, set
    (T(20, 31), dict(prop=(0.24, 0.66, 0.92, -120.0, 0.0, 0.0), pelvis=(11.0, 0.0, 0.0), hips=(0.0, -0.02, -0.06),
                     spine=(2.0, 0.0, 0.0), head=(22.0, 0.0, 0.0))),                             # weight into it
    (T(22, 31), dict(hips=(0.0, -0.02, -0.055))),                                                 # hold
    (T(24, 31), dict(Rb=0.0, R=(0.32, 0.36, 0.78))),
    (1.0, dict(STAND, prop=(0.24, 0.66, 0.92, -120.0, 0.0, 0.0)))], T(6, 31), R=(0.33, 0.30, 0.88)),
    prop=("lever", (0.035, 0.035, 0.32)), grips={"R": (0.0, 0.0, 0.29)},
    static=[static("panel", (0.34, 0.06, 0.50), (0.24, 0.70, 0.92))],
    doc="Look up at a wall lever, grab it above chest height, drop the weight into pulling it down through 80 "
        "degrees, hold, let go (31 frames).")

VALVE_AT = (0.0, 0.50, 1.00)
VALVE_R = 0.17


def _rim(a, pull=0.0):
    return (VALVE_AT[0] + VALVE_R * math.cos(math.radians(a)), VALVE_AT[1] - 0.035 - pull,
            VALVE_AT[2] + VALVE_R * math.sin(math.radians(a)))


def _valve_turn(t):
    """The hands turn the wheel 60 degrees clockwise, let go, reach back and grip again (the wheel's six spokes make
    the loop seamless)."""
    if t < 0.5:
        u = t / 0.5
        ang = 60.0 * u * u * (3 - 2 * u)
        turn, pull = ang, 0.0
    else:
        u = (t - 0.5) / 0.5
        ang, turn = 60.0 * (1.0 - u * u * (3 - 2 * u)), 60.0
        pull = 0.05 * math.sin(math.pi * u)
    lean = 4.0 + 3.0 * math.sin(2 * math.pi * t)
    return dict(prop=VALVE_AT + (0.0, turn, 0.0), R=_rim(30.0 - ang, pull), L=_rim(150.0 - ang, pull), Rs=0.0, Ls=0.0,
                Rp=(1.0, -0.2, -0.5), Lp=(-1.0, -0.2, -0.5), pelvis=(lean, 0.0, 0.0), head=(16.0, 0.0, 0.0),
                hips=(0.0, -0.03, -0.03), lf=foot("Left", y=-0.12), rf=foot("Right", y=0.06))


VALVE = ("valve", (VALVE_R, 0.0, 0.0))
clip("TURN_VALVE", 32, cycle(16, _valve_turn), loop=True, prop=VALVE,
     doc="Turning a wall valve wheel hand over hand, 60 degrees per loop (32 frames).")


def _valve_hold(t):
    j = 1.5 * math.sin(2 * math.pi * 3 * t)
    return dict(prop=VALVE_AT + (0.0, j, 0.0), R=_rim(30.0 - j), L=_rim(150.0 - j), Rs=0.0, Ls=0.0,
                Rp=(1.0, -0.2, -0.5), Lp=(-1.0, -0.2, -0.5), pelvis=(-3.0 + 1.0 * math.sin(2 * math.pi * t), 0.0, 0.0),
                spine=(-3.0, 0.0, 0.0), head=(16.0, 0.0, 0.0), hips=(0.0, -0.02, -0.05), Lsh=3.0, Rsh=3.0,
                lf=foot("Left", y=-0.16), rf=foot("Right", y=0.04))


clip("HOLD_VALVE", 32, cycle(8, _valve_hold), loop=True, prop=VALVE,
     doc="Straining on a stuck valve wheel, leaning back (32 frames).")
clip("OPEN", 31, [
    (0.0, dict(prop=(-0.42, 0.44, 0.0, 0.0, 0.0, 0.0))),
    (T(4, 31), dict(pelvis=(-3.0, 0.0, 0.0), hips=(0.0, -0.02, 0.0), head=(8.0, 0.0, 0.0))),        # sit back, look
    (T(9, 31), dict(LOOK, pelvis=(4.0, 0.0, 0.0), hips=STAND["hips"], R=(0.24, 0.38, 1.0), Rs=0.0,
                    Rp=(0.9, -0.3, -1.0))),
    (T(11, 31), dict(Rb=1.0)),
    (T(18, 31), dict(prop=(-0.42, 0.44, 0.0, 0.0, 0.0, 22.0), pelvis=(12.0, 0.0, 0.0), hips=(0.0, 0.14, -0.04),
                     rf=foot("Right", y=0.27), head=(4.0, 0.0, 0.0))),
    (T(20, 31), dict(Rb=0.0, R=(0.26, 0.56, 1.0))),
    (T(24, 31), dict(prop=(-0.42, 0.44, 0.0, 0.0, 0.0, 70.0))),
    (1.0, dict(STAND, prop=(-0.42, 0.44, 0.0, 0.0, 0.0, 85.0)))],
    prop=("door", (0.80, 0.04, 1.9)), grips={"R": (0.68, -0.05, 1.0)},
    doc="Sit back, then push a door (hinged on its left) open with the right hand, stepping into it with the weight "
        "behind it (31 frames).")
clip("INSERT", 31, via(via([
    (0.0, dict(prop=(0.40, 0.19, 0.665, 0.0, 0.0, 0.0), pk=1.0, Rb=1.0)),
    (T(9, 31), dict(LOOK, pelvis=(4.0, 0.0, 0.0), prop=(0.22, 0.43, 1.02, 0.0, 0.0, 0.0), pk=0.0,
                    Rp=(0.9, -0.3, -1.0))),
    (T(12, 31), dict(prop=(0.22, 0.44, 1.02, 0.0, 0.0, 0.0))),                                   # line it up
    (T(15, 31), dict(prop=(0.22, 0.49, 1.02, 0.0, 0.0, 0.0), pelvis=(6.0, 0.0, 0.0))),            # push it home
    (T(17, 31), dict(prop=(0.22, 0.49, 1.02, 0.0, 0.0, 0.0))),
    (T(19, 31), dict(Rb=0.0, R=(0.22, 0.43, 1.02), Rs=0.0, pelvis=(3.0, 0.0, 0.0))),
    (T(22, 31), dict(R=(0.30, 0.36, 0.92))),
    (1.0, dict(STAND, prop=(0.22, 0.49, 1.02, 0.0, 0.0, 0.0)))], T(5, 31), prop=(0.30, 0.36, 0.88, 0.0, 0.0, 0.0)),
    T(26, 31), R=(0.34, 0.28, 0.78)),
    prop=("radio", (0.07, 0.15, 0.05)), grips={"R": (0.0, -0.07, 0.0)},
    static=[static("panel", (0.36, 0.06, 0.36), (0.22, 0.58, 1.02))],
    doc="Bring a cartridge or fuse up to a wall slot at chest height, line it up, push it home, let go (31 frames).")
clip("CONNECT_PORT", 36, via(via([
    (0.0, dict(prop=(0.40, 0.19, 0.665, 0.0, 0.0, 0.0), pk=1.0, Rb=1.0)),
    (T(9, 30), dict(pelvis=(5.0, 0.0, 0.0), spine=(2.0, 0.0, 0.0), hips=(0.0, -0.03, -0.05), head=(16.0, 0.0, 0.0),
                    prop=(0.18, 0.48, 0.97, 0.0, 0.0, 0.0), pk=0.0, Rp=(0.9, -0.3, -1.0),
                    L=(-0.16, 0.54, 1.00), Ls=0.0, Lp=(-0.9, -0.3, -1.0))),
    (T(13, 30), dict(prop=(0.18, 0.55, 0.97, 0.0, 0.0, 0.0))),
    (T(17, 30), dict(prop=(0.18, 0.55, 0.97, 0.0, 70.0, 0.0), Rw=8.0)),
    (T(19, 30), dict(Rb=0.0, R=(0.22, 0.46, 0.95), Rs=0.0, Rw=0.0)),
    (T(23, 30), dict(L=M(HANG, "Left"), Ls=1.0, Lp=STAND["Lp"])),
    (1.0, dict(STAND, prop=(0.18, 0.55, 0.97, 0.0, 70.0, 0.0)))], T(4, 30),
        prop=(0.34, 0.38, 0.88, 0.0, 0.0, 0.0), L=(-0.35, 0.36, 0.88)), T(24, 30), R=(0.32, 0.36, 0.86)),
    prop=("radio", (0.06, 0.14, 0.06)), grips={"R": (0.0, -0.07, 0.0)},
    static=[static("panel", (0.50, 0.20, 0.70), (0.12, 0.72, 0.97))],
    doc="Plug a service cable into the suit port of a worker in the OCRU, steadying it with the left hand, and twist "
        "it locked (36 frames).")
clip("POINT", 26, [
    (0.0, {}),
    (T(4, 26), dict(R=(0.40, 0.16, 0.84), Rs=1.0, chest=(0.0, 0.0, 3.0), head=(5.0, 0.0, 2.0))),     # gather
    (T(9, 26), dict(R=(0.19, 0.47, 1.21), Rs=1.0, Rp=(1.0, -0.2, -0.6), chest=(0.0, 0.0, -5.0), pelvis=(0.0, 0.0, -2.0),
                    head=(-2.0, 0.0, -4.0), Rw=-10.0)),
    (T(18, 26), dict(R=(0.19, 0.48, 1.22))),                                                       # hold the point
    (1.0, STAND)],
    doc="Gather, point straight ahead with the right arm (a ping), hold it, then drop it (26 frames).")
clip("RADIO", 48, cycle(8, lambda t: dict(
    prop=(0.36, 0.13, 1.30, 0.0, -20.0, 0.0), pk=1.0, Rb=1.0, Rp=(1.0, -0.2, -0.3), Rsh=6.0,
    head=(3.0 * math.sin(2 * math.pi * 2 * t), 7.0, -4.0), chest=(0.0, 1.5, 0.0),
    L=M((0.33, 0.12, 0.66), "Left"))), loop=True, prop=("radio", (0.07, 0.05, 0.15)), grips={"R": (0.0, 0.0, -0.05)},
    doc="Holding a radio against the side of the hood and talking, head tilted into it (48 frames).")


def stagger(name, push, doc):
    """Hit reaction: the body is shoved along `push` (x, y), a foot steps out to catch it, then back to standing."""
    px, py = push
    lead = "Right" if px > 0 or (px == 0 and py > 0) else "Left"
    ks = lead[0].lower() + "f"
    x0 = RIG.ANKLE_REST[lead].x
    return clip(name, 26, [
        (0.0, {}),
        (T(3, 22), dict(pelvis=(14.0 * py, 12.0 * px, 0.0), spine=(9.0 * py, 7.0 * px, 0.0),
                        chest=(7.0 * py, 5.0 * px, 0.0), head=(-12.0 * py, -9.0 * px, 0.0),
                        hips=(0.05 * px, 0.04 * py, -0.03), Lsh=5.0, Rsh=5.0,
                        L=M((0.40 + 0.06 * abs(px), 0.10 + 0.12 * py, 0.80), "Left"),
                        R=M((0.40 + 0.06 * abs(px), 0.10 + 0.12 * py, 0.80), "Right"))),
        (T(6, 22), {ks: foot(lead, y=0.014 + 0.15 * py, x=x0 + 0.125 * px, clear=0.08, pitch=-8.0)}),
        (T(9, 22), dict({ks: foot(lead, y=0.014 + 0.27 * py, x=x0 + 0.25 * px)}, hips=(0.10 * px, 0.10 * py, -0.07),
                        pelvis=(6.0 * py, 4.0 * px, 0.0), spine=(2.0 * py, 2.0 * px, 0.0), chest=(2.0 * py, 0.0, 0.0),
                        head=(-4.0 * py, -2.0 * px, 0.0))),
        (T(13, 22), dict(hips=(0.075 * px, 0.075 * py, -0.035), pelvis=(0.0, 0.0, 0.0), spine=STAND["spine"],
                         chest=(0.0, 0.0, 0.0), head=(0.0, 0.0, 0.0), L=STAND["L"], R=STAND["R"], Lsh=0.0, Rsh=0.0)),
        (T(17, 22), {ks: foot(lead, y=0.014 + 0.12 * py, x=x0 + 0.10 * px, clear=0.07, pitch=-6.0),
                     "hips": (0.02 * px, 0.02 * py, -0.01)}),
        (1.0, STAND)], doc=doc)


stagger("STAGGER_F", (0.0, 1.0), "Shoved from behind: lurch forward, catch it with a step, recover (26 frames).")
stagger("STAGGER_B", (0.0, -1.0), "Hit from the front: rock back, step back, recover (26 frames).")
stagger("STAGGER_L", (-1.0, 0.0), "Shoved to its left: lean, side-step, recover (26 frames).")
stagger("STAGGER_R", (1.0, 0.0), "Shoved to its right: lean, side-step, recover (26 frames).")

# Lying on the floor (the end of a ragdoll): the pelvis turned 90 degrees, the hips low, the body along +Y from the
# root, so it stands up on the root.
PRONE = dict(hips=(0.0, -0.20, -0.47), pelvis=(90.0, 0.0, 0.0), spine=(0.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0),
             head=(-35.0, 0.0, 0.0), L=(-0.40, 0.16, 0.10), R=(0.40, 0.16, 0.10), Ls=0.0, Rs=0.0,
             Lp=(-0.6, 0.0, 1.0), Rp=(0.6, 0.0, 1.0), lf=(-0.155, -0.74, 0.098, -160.0, 0.0),
             rf=(0.155, -0.74, 0.098, -160.0, 0.0))
SUPINE = dict(hips=(0.0, 0.15, -0.47), pelvis=(-90.0, 0.0, 0.0), spine=(0.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0),
              head=(20.0, 0.0, 0.0), L=(-0.42, -0.22, 0.10), R=(0.42, -0.22, 0.10), Ls=0.0, Rs=0.0,
              Lp=(-0.6, 0.0, -1.0), Rp=(0.6, 0.0, -1.0), lf=(-0.155, 0.73, 0.146, 75.0, 0.0),
              rf=(0.155, 0.73, 0.146, 75.0, 0.0))
UP = dict(L=M(HANG, "Left"), R=M(HANG, "Right"), Ls=1.0, Rs=1.0, Lp=STAND["Lp"], Rp=STAND["Rp"])
GETUP_FRONT_KEYS = [
    (0.0, PRONE),
    (T(10, 42), dict(hips=(0.0, -0.22, -0.40), pelvis=(70.0, 0.0, 0.0), spine=(-6.0, 0.0, 0.0),
                     chest=(-6.0, 0.0, 0.0), head=(-25.0, 0.0, 0.0), L=(-0.32, 0.30, 0.05), R=(0.32, 0.30, 0.05),
                     Lp=(-0.6, -0.3, 0.5), Rp=(0.6, -0.3, 0.5), lf=(-0.155, -0.70, 0.223, -95.0, 0.0),
                     rf=(0.155, -0.70, 0.223, -95.0, 0.0))),
    (T(18, 42), dict(hips=(0.0, -0.20, -0.30), pelvis=(60.0, 0.0, 0.0), spine=(4.0, 0.0, 0.0), chest=(4.0, 0.0, 0.0),
                     head=(-30.0, 0.0, 0.0), L=(-0.30, 0.32, 0.05), R=(0.30, 0.32, 0.05), Lp=(-0.8, -0.5, 0.0),
                     Rp=(0.8, -0.5, 0.0), lf=(-0.155, -0.52, 0.223, -95.0, 0.0), rf=(0.155, -0.52, 0.223, -95.0, 0.0))),
    (T(22, 42), dict(rf=(0.155, -0.22, 0.273, -50.0, 0.0))),            # the right foot swings forward, toes clear
    (T(26, 42), dict(hips=(0.0, -0.18, -0.32), pelvis=(40.0, 0.0, 0.0), spine=(8.0, 0.0, 0.0), chest=(6.0, 0.0, 0.0),
                     head=(-26.0, 0.0, 0.0), L=(-0.30, 0.20, 0.30), R=(0.31, 0.27, 0.56),
                     rf=foot("Right", y=0.08), lf=(-0.155, -0.50, 0.223, -95.0, 0.0))),
    (T(30, 42), dict(lf=(-0.155, -0.30, 0.253, -50.0, 0.0))),          # the back foot swings forward, toes clear
    (T(34, 42), dict(UP, hips=(0.0, -0.06, -0.14), pelvis=(16.0, 0.0, 0.0), spine=(6.0, 0.0, 0.0),
                     chest=(2.0, 0.0, 0.0), head=(-12.0, 0.0, 0.0), lf=foot("Left", y=-0.10, pitch=-20.0))),
    (1.0, STAND)]
GETUP_FRONT_KEYS = via(GETUP_FRONT_KEYS, T(32, 42), L=(-0.44, 0.30, 0.58), R=(0.44, 0.30, 0.58), Ls=0.0, Rs=0.0)
clip("GETUP_FRONT", 48, GETUP_FRONT_KEYS,
    doc="Get up from lying face down: push up, knees under, one foot planted, stand (48 frames; the body lies along "
        "+Y from the root and stands up on it).")
clip("GETUP_BACK", 50, [
    (0.0, SUPINE),
    (T(10, 44), dict(hips=(0.0, 0.10, -0.46), pelvis=(-50.0, 0.0, 0.0), spine=(20.0, 0.0, 0.0),
                     chest=(14.0, 0.0, 0.0), head=(10.0, 0.0, 0.0), L=(-0.46, -0.18, 0.06), R=(0.46, -0.18, 0.06),
                     Lp=(-0.8, -0.2, 0.3), Rp=(0.8, -0.2, 0.3), lf=(-0.14, 0.62, 0.146, 40.0, 0.0),
                     rf=(0.14, 0.62, 0.146, 40.0, 0.0))),
    (T(20, 44), dict(hips=(0.0, 0.02, -0.48), pelvis=(-24.0, 0.0, 0.0), spine=(14.0, 0.0, 0.0),
                     chest=(8.0, 0.0, 0.0), head=(-6.0, 0.0, 0.0), L=(-0.44, -0.02, 0.06), R=(0.44, 0.14, 0.30),
                     lf=foot("Left", y=0.30, x=-0.28), rf=foot("Right", y=0.28, x=0.28))),
    (T(30, 44), dict(hips=(0.0, 0.0, -0.30), pelvis=(34.0, 0.0, 0.0), spine=(14.0, 0.0, 0.0), chest=(6.0, 0.0, 0.0),
                     head=(-28.0, 0.0, 0.0), L=(-0.40, 0.40, 0.55), R=(0.40, 0.40, 0.55), Lp=(-1.0, -0.3, -0.4),
                     Rp=(1.0, -0.3, -0.4), lf=foot("Left", y=0.10, x=-0.24), rf=foot("Right", y=0.10, x=0.24))),
    (T(37, 44), dict(UP, hips=(0.0, -0.02, -0.12), pelvis=(14.0, 0.0, 0.0), spine=(4.0, 0.0, 0.0),
                     chest=(0.0, 0.0, 0.0), head=(-10.0, 0.0, 0.0), lf=foot("Left", y=0.04),
                     rf=foot("Right", y=0.04))),
    (1.0, STAND)],
    doc="Get up from lying on the back: sit up, feet in, rock forward onto the feet, stand (50 frames).")
clip("SUIT_UP", 64, [
    (0.0, {}),
    (T(8, 56), dict(hips=(0.0, -0.05, -0.20), pelvis=(28.0, 0.0, 0.0), spine=(14.0, 0.0, 0.0), chest=(6.0, 0.0, 0.0),
                    head=(-20.0, 0.0, 0.0), L=(-0.36, 0.14, 0.44), R=(0.36, 0.14, 0.44), Ls=0.0, Rs=0.0,
                    Lp=(-1.0, -0.2, -0.3), Rp=(1.0, -0.2, -0.3))),              # hands on the outside of the thighs
    (T(20, 56), dict(hips=STAND["hips"], pelvis=(0.0, 0.0, 0.0), spine=(-2.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0),
                     head=(10.0, 0.0, 0.0), L=(-0.30, 0.34, 1.00), R=(0.30, 0.34, 1.00))),
    (T(24, 56), dict(L=(-0.27, 0.36, 1.04), R=(0.27, 0.36, 1.04))),                # tug the straps out in front
    (T(30, 56), dict(L=M(HANG, "Left"), Ls=1.0, Lp=STAND["Lp"], R=(0.07, 0.40, 0.84), Rp=(1.0, 0.0, -0.4),
                     head=(22.0, 0.0, 0.0))),                                       # zip tab pulled out in front
    (T(36, 56), dict(R=(0.07, 0.40, 1.10), head=(16.0, 0.0, 0.0))),
    (T(42, 56), dict(R=(0.38, 0.12, 1.30), L=(-0.38, 0.12, 1.30), Ls=0.0, Lp=(-1.0, -0.2, -0.3), Rp=(1.0, -0.2, -0.3),
                     Lsh=8.0, Rsh=8.0, head=(-4.0, 0.0, 0.0))),                     # seat the hood by its sides
    (T(47, 56), dict(R=(0.37, 0.16, 1.24), L=(-0.37, 0.16, 1.24))),
    (1.0, STAND)],
    doc="Suit up: bend and pull the suit up the legs, settle it on the shoulders, zip the front, seat the hood with "
        "both hands (64 frames).")


def _cabinet(depth):
    """Open-fronted cabinet (locker, OCRU) standing behind the root."""
    y = -depth / 2 - 0.05
    return [static("panel", (0.92, depth, 0.04), (0.0, y, -0.02)),
            static("panel", (0.04, depth, 1.95), (-0.46, y, 0.975)),
            static("panel", (0.04, depth, 1.95), (0.46, y, 0.975)),
            static("panel", (0.92, 0.04, 1.95), (0.0, y - depth / 2, 0.975))]


def step_out(lead_y=-0.45, stumble=0.0):
    """Keys stepping forward out of a cabinet: standing `lead_y` behind the root, right foot then left."""
    return [
        (T(9, 24), dict(rf=foot("Right", y=lead_y + 0.27, clear=0.08, pitch=-6.0), hips=(0.0, lead_y + 0.10, 0.0))),
        (T(12, 24), dict(UP, rf=foot("Right", y=0.02), hips=(0.0, lead_y * 0.45, -0.03 - 0.03 * stumble),
                         pelvis=(4.0 + 8.0 * stumble, 0.0, 0.0))),
        (T(16, 24), dict(lf=foot("Left", y=-0.20, clear=0.07, pitch=-10.0), hips=(0.0, -0.06, -0.01))),
        (T(19, 24), dict(lf=foot("Left"), hips=(0.0, 0.0, -0.01), pelvis=(0.0, 0.0, 0.0), head=(0.0, 0.0, 0.0))),
        (1.0, STAND)]


clip("LOCKER_EXIT", 28, [
    (0.0, dict(hips=(0.0, -0.46, -0.01), lf=foot("Left", y=-0.45), rf=foot("Right", y=-0.45), head=(6.0, 0.0, 0.0),
               R=(0.30, -0.22, 1.02), Rs=0.0, Rp=(0.9, -0.3, -0.8))),
    (T(5, 24), dict(R=(0.30, -0.10, 1.04), pelvis=(4.0, 0.0, 0.0)))] + step_out(),
    static=_cabinet(0.70),
    doc="Step out of a locker (standing 0.45 m behind the root inside it): push the door, step, step, stand "
        "(28 frames).")
SLUMP = dict(hips=(0.0, -0.36, -0.05), pelvis=(6.0, 0.0, 0.0), spine=(10.0, 0.0, 0.0), chest=(8.0, 0.0, 0.0),
             head=(30.0, 4.0, 0.0), L=M((0.37, -0.16, 0.62), "Left"), R=M((0.37, -0.16, 0.62), "Right"), Ls=0.0,
             Rs=0.0, Lsh=-4.0, Rsh=-4.0, lf=foot("Left", y=-0.38), rf=foot("Right", y=-0.36))
SLUMP_W = dict(SLUMP, L=(-0.37, -0.14, 0.62), R=(0.37, -0.14, 0.62))
clip("REANIM_IDLE", 48, cycle(4, lambda t: dict(SLUMP_W, chest=(8.0 + 1.5 * math.sin(2 * math.pi * t), 0.0, 0.0),
                                                head=(30.0, 4.0, 2.0 * math.sin(2 * math.pi * t)))), loop=True,
     static=_cabinet(0.80),
     doc="Slumped inside the OCRU cabinet (0.4 m behind the root), knees soft, head down, barely breathing "
         "(48 frames).")
clip("REANIM_JOLT", 18, [
    (0.0, SLUMP_W),
    (T(2, 16), dict(hips=(0.0, -0.36, 0.0), pelvis=(-2.0, 0.0, 0.0), spine=(-6.0, 0.0, 0.0), chest=(-4.0, 0.0, 0.0),
                    head=(-8.0, 0.0, 0.0), L=(-0.46, -0.30, 0.90), R=(0.46, -0.30, 0.90), Lsh=10.0, Rsh=10.0,
                    Lp=(-1.0, -0.2, -0.3), Rp=(1.0, -0.2, -0.3))),
    (T(5, 16), dict(SLUMP_W, spine=(13.0, 0.0, 0.0), head=(36.0, 4.0, 0.0))),
    (T(8, 16), dict(spine=(4.0, 0.0, 0.0), head=(18.0, 2.0, 0.0), hips=(0.0, -0.36, -0.03))),
    (1.0, SLUMP_W)],
    static=_cabinet(0.80), doc="A reanimation shock: the body snaps straight, arms flung out, and slumps back "
                               "(18 frames).")
clip("REANIM_EXIT", 28, [
    (0.0, SLUMP_W),
    (T(5, 24), dict(SLUMP_W, hips=(0.0, -0.36, -0.01), pelvis=(2.0, 0.0, 0.0), spine=(0.0, 0.0, 0.0),
                    chest=(0.0, 0.0, 0.0), head=(-6.0, 0.0, 8.0), L=(-0.36, -0.22, 0.74), R=(0.36, -0.22, 0.74),
                    Lsh=0.0, Rsh=0.0))] + step_out(-0.36, stumble=1.0),
    static=_cabinet(0.80),
    doc="Waking in the OCRU: head up, look round, stumble out with two steps (28 frames).")

DIG_GRIPS = {"R": (0.0, 0.0, 0.27), "L": (0.0, 0.0, 0.0)}      # right hand on the D-handle, left down the shaft


def _shovel(grip, toward, side=(1.0, 0.0, 0.0)):
    """Shovel placement with the D-handle grip at `grip` and the blade pointing towards `toward`."""
    z = (Vector(grip) - Vector(toward)).normalized()
    return placement(Vector(grip) - z * DIG_GRIPS["R"][2], z, side)


DIG_BODY = dict(hips=(0.0, -0.08, -0.14), pelvis=(30.0, 0.0, 0.0), spine=(8.0, 0.0, 0.0), chest=(4.0, 0.0, 0.0),
                head=(-8.0, 0.0, 0.0), Lb=1.0, Rb=1.0, Rp=(1.0, 0.1, -0.4), Lp=(-0.8, -0.2, -1.0),
                lf=foot("Left", y=0.06, x=-0.15), rf=foot("Right", y=-0.10, x=0.15))
_DIG_READY = _shovel((0.16, 0.20, 0.80), (-0.04, 1.0, 0.0))
clip("SHOVEL_DIG", 40, [
    (0.0, dict(DIG_BODY, prop=_DIG_READY)),
    (T(7, 36), dict(prop=_shovel((0.16, 0.26, 0.70), (-0.04, 1.06, -0.10)), pelvis=(33.0, 0.0, 0.0))),
    (T(13, 36), dict(prop=_shovel((0.17, 0.30, 0.60), (-0.04, 1.06, -0.10)), hips=(0.0, -0.08, -0.21),
                     pelvis=(38.0, 0.0, 0.0), spine=(10.0, 0.0, 0.0))),
    (T(20, 36), dict(prop=_shovel((0.18, 0.20, 0.76), (0.02, 0.95, 0.45)), hips=(0.0, -0.07, -0.10),
                     pelvis=(22.0, 0.0, 0.0), spine=(6.0, 0.0, 0.0))),
    (T(26, 36), dict(prop=_shovel((0.06, 0.18, 0.84), (0.64, 0.62, 0.52), (0.6, 0.6, 0.6)),
                     pelvis=(18.0, 0.0, -14.0), chest=(4.0, 0.0, -10.0), head=(-8.0, 0.0, 10.0))),
    (T(30, 36), dict(pelvis=(22.0, 0.0, -8.0), chest=(4.0, 0.0, -4.0), head=(-8.0, 0.0, 4.0))),
    (1.0, dict(DIG_BODY, prop=_DIG_READY))],
    loop=True, tool="SHOVEL", grips=DIG_GRIPS,
    doc="Digging with the shovel in both hands (right on the D-handle): stab, lever, lift and toss the load to the "
        "right (40 frames).")


def register():
    """Add every clip to character_rig.ACTIONS (builder, held tool)."""
    for name, c in CLIPS.items():
        RIG.ACTIONS[name] = (c.build, c.tool)


register()
