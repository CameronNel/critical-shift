#!/usr/bin/env python3
"""Rig check: crew worker (bare or in the hazmat suit) through its actions (character_rig and character_clips).
    python render_rig.py -- <output_dir>
env: SUIT=1 wear the suit | ACTIONS=IDLE,RUN,... | VIEWS=three_q,front,side,eye,... (see VIEWS) | FRAMES=0,6,12,...
     VIDEO=1 render every frame and encode <ACTION>_<view>.mp4 (loops twice, one-shots once) | RES=360x480 | SAMPLES=16
     EXPORT=<dir> write one FBX clip per action
The "eye" view is the first-person camera: at the eyes, following the Head bone, 60 degree vertical field of view at
16:9, with everything rigid to the head (hood, visor, face) hidden, as the game would. Clip props are preview-only.
"""
import math
import os
import subprocess
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_clips as CC  # noqa: E402
import character_rig as RIG  # noqa: E402
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402
from render_worker import backdrop  # noqa: E402

VIEWS = {"front": ((0.0, 5.0, 1.0), (0, 0, 0.95), 52), "three_q": ((-3.3, 3.6, 1.15), (0, 0, 0.92), 52),
         "side": ((5.2, 0.0, 1.0), (0, 0, 0.95), 52), "side_r": ((-4.6, 0.0, 1.0), (0, 0, 0.92), 52),
         "back": ((0.0, -5.0, 1.0), (0, 0, 0.95), 52), "legs": ((2.4, 3.0, 0.55), (0, 0, 0.45), 52),
         "legs_b": ((-2.0, -2.6, 0.55), (0, 0, 0.45), 52), "shoulders": ((0.0, 2.6, 1.45), (0, 0, 1.3), 60),
         "sh_side": ((-2.4, 0.4, 1.45), (0, 0, 1.25), 60), "sh_back": ((0.0, -2.6, 1.45), (0, 0, 1.3), 60),
         "flank_r": ((-1.9, -0.5, 0.95), (0, 0, 0.8), 55), "flank_l": ((1.9, -0.5, 0.95), (0, 0, 0.8), 55),
         "wide": ((-4.2, 4.6, 1.3), (0, 0.2, 0.75), 45), "close": ((-2.2, 2.5, 1.15), (0, 0.15, 0.78), 50),
         "close_side": ((3.2, 0.3, 1.0), (0, 0.15, 0.78), 50), "eye": None}
EYE = Vector((0.0, 0.20, 1.40))       # between the eyes, rest pose
EYE_RES = (480, 270)


def eye_shoot(cam, arm, path, res):
    """First-person frame: camera at the eyes, looking along the head's +Y."""
    dg = bpy.context.evaluated_depsgraph_get()
    pb = arm.evaluated_get(dg).pose.bones["Head"]
    Mh = arm.matrix_world @ pb.matrix @ arm.data.bones["Head"].matrix_local.inverted()
    look = Mh.to_3x3().normalized() @ Matrix.Rotation(math.pi / 2, 3, "X")     # camera -Z along the head's +Y
    cam.matrix_world = Matrix.Translation(Mh @ EYE) @ look.to_4x4()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = EYE_RES
    cam.data.sensor_fit, cam.data.sensor_height = "VERTICAL", 24.0
    cam.data.lens = 12.0 / math.tan(math.radians(30.0))
    cam.data.clip_start = 0.02
    hidden = [o for o in sc.objects if o.get("cs_head_rigid") and not o.hide_render]
    for o in hidden:
        o.hide_render = True
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False
    sc.render.resolution_x, sc.render.resolution_y = res
    cam.data.sensor_fit = "AUTO"
    cam.data.clip_start = 0.1


def _prop_mesh(kind, dims, name):
    """Simple preview stand-ins for the things a clip handles."""
    import bmesh
    bm = bmesh.new()
    col = (0.25, 0.45, 0.75, 1.0)
    if kind == "valve":
        r = dims[0]
        bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=r, radius2=r, depth=0.03,
                              matrix=Matrix.Rotation(math.pi / 2, 4, "X"))
        for a in (0.0, 60.0, 120.0):
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Rotation(math.radians(a), 4, "Y")
                                  @ Matrix.Diagonal((2 * r, 0.05, 0.03, 1.0)))
        col = (0.75, 0.12, 0.10, 1.0)
    elif kind in ("lever", "stick"):
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, dims[2] / 2)) @ Matrix.Diagonal(
            (dims[0], dims[1], dims[2], 1.0)))
        col = (0.15, 0.15, 0.15, 1.0)
    elif kind == "door":
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((dims[0] / 2, 0, dims[2] / 2)) @ Matrix.Diagonal(
            (dims[0], dims[1], dims[2], 1.0)))
        col = (0.45, 0.50, 0.55, 1.0)
    else:
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((dims[0], dims[1], dims[2], 1.0)))
        col = {"crate": (0.55, 0.38, 0.18, 1.0), "panel": (0.35, 0.38, 0.42, 1.0), "button": (0.85, 0.10, 0.08, 1.0),
               "body": (0.85, 0.55, 0.10, 1.0), "radio": (0.12, 0.12, 0.12, 1.0)}.get(kind, col)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = col
    me.materials.append(mat)
    bpy.context.scene.collection.objects.link(o)
    o["cs_preview_prop"] = True
    return o


def show_props(action, arm):
    """Create this action's preview props; returns a per-frame updater."""
    for o in [o for o in bpy.data.objects if o.get("cs_preview_prop")]:
        bpy.data.objects.remove(o)
    rec = CC.PROPS.get(action)
    if not rec:
        return lambda f: None
    for i, (kind, dims, mat) in enumerate(rec["static"]):
        o = _prop_mesh(kind, dims, "PROP_%s_static%d" % (action, i))
        o.matrix_world = arm.matrix_world @ Matrix(mat)
    if not rec["kind"]:
        return lambda f: None
    o = _prop_mesh(rec["kind"], rec["dims"], "PROP_%s" % action)

    def update(f):
        fr = rec["frames"]
        o.matrix_world = arm.matrix_world @ fr.get(f, fr[max(k for k in fr if k <= f)] if any(k <= f for k in fr)
                                                    else fr[min(fr)])
    return update


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image
    w, h = [int(x) for x in os.environ.get("RES", "480x640").split("x")]
    s, cam = studio((w, h), int(os.environ.get("SAMPLES", "32")))
    backdrop(s)
    root, tris = CW.build_worker()
    suit = os.environ.get("SUIT") == "1"
    if suit:
        CS.build_hazmat(root)
        CS.equip(root)
    arm = RIG.build_rig(root)
    n, _ = RIG.skin_worker(root, arm)
    tools = RIG.add_tools(root, arm)
    print("RIG skinned meshes:", n)
    wanted = os.environ.get("ACTIONS", ",".join(RIG.ACTIONS)).split(",")
    for a in wanted:
        RIG.ACTIONS[a][0](arm)
        print("RIG action", a, "ok")
    tag = "suit" if suit else "bare"
    for nm in [x for x in os.environ.get("HIDE", "").split(",") if x]:
        for o in bpy.data.objects:
            if o.name == nm:
                o.hide_render = True
    views = os.environ.get("VIEWS", "three_q").split(",")
    for a in wanted:
        RIG.set_action(arm, a)
        RIG.show_tool(tools, RIG.ACTIONS[a][1])
        act = bpy.data.actions[a]
        loop = bool(act.get("cs_loop", True))
        nf = int(act.frame_range[1]) + (0 if loop else 1)
        if os.environ.get("VIDEO") == "1":
            frames = list(range(nf))
        else:
            frames = [int(x) for x in os.environ.get("FRAMES", ",".join(str(i) for i in range(0, nf, max(1, nf // 6)))).split(",")]
        props = show_props(a, arm)
        for view in views:
            files = []
            for f in frames:
                s.frame_set(f)
                props(f)
                p = os.path.join(out, "%s_%s_%s_%02d.png" % (a, tag, view, f))
                if view == "eye":
                    eye_shoot(cam, arm, p, (w, h))
                else:
                    shoot(cam, *VIEWS[view], p)
                files.append(p)
            if os.environ.get("VIDEO") == "1":
                ff = __import__("imageio_ffmpeg").get_ffmpeg_exe()
                lst = os.path.join(out, "%s_%s_%s.txt" % (a, tag, view))
                seq = files * 2 if loop else files + [files[-1]] * 12
                with open(lst, "w") as fh:
                    for p in seq:
                        fh.write("file '%s'\nduration %.5f\n" % (p, 1 / 24))
                subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf",
                                "fps=24,format=yuv420p", "-c:v", "libx264", "-crf", "20",
                                os.path.join(out, "%s_%s_%s.mp4" % (a, tag, view))], check=True)
            ims = [Image.open(p).convert("RGB") for p in files[::max(1, len(files) // 8)][:8]]
            sheet = Image.new("RGB", (ims[0].width * len(ims), ims[0].height), (16, 16, 10))
            for i, im in enumerate(ims):
                sheet.paste(im, (i * im.width, 0))
            sheet.save(os.path.join(out, "%s_%s_%s.png" % (a, tag, view)))
    if os.environ.get("EXPORT"):
        os.makedirs(os.environ["EXPORT"], exist_ok=True)
        for a in wanted:
            RIG.show_tool(tools, RIG.ACTIONS[a][1])
            path = RIG.export_fbx(root, arm, os.path.join(os.environ["EXPORT"], "crew_worker_%s.fbx" % a), action=a)
            print("RIG fbx", os.path.basename(path), os.path.getsize(path) // 1024, "KB")
    print("RIG done")


if __name__ == "__main__":
    main()
