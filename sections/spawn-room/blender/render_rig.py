#!/usr/bin/env python3
"""Rig check: crew worker (bare or in the hazmat suit) through the IDLE, RUN, HOLD_* and RUN_* actions.
    python render_rig.py -- <output_dir>
env: SUIT=1 wear the suit | ACTIONS=IDLE,RUN,... | VIEWS=three_q,front,side | FRAMES=0,6,12,... (stills sheet)
     VIDEO=1 render every frame and encode <ACTION>_<view>.mp4 (looped twice) | RES=360x480 | SAMPLES=16
     EXPORT=<dir> write one FBX clip per action
"""
import os
import subprocess
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_rig as RIG  # noqa: E402
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402
from render_worker import backdrop  # noqa: E402

VIEWS = {"front": ((0.0, 5.0, 1.0), (0, 0, 0.95), 52), "three_q": ((-3.3, 3.6, 1.15), (0, 0, 0.92), 52),
         "side": ((5.2, 0.0, 1.0), (0, 0, 0.95), 52), "side_r": ((-4.6, 0.0, 1.0), (0, 0, 0.92), 52),
         "back": ((0.0, -5.0, 1.0), (0, 0, 0.95), 52), "shoulders": ((0.0, 2.6, 1.45), (0, 0, 1.3), 60), "sh_side": ((-2.4, 0.4, 1.45), (0, 0, 1.25), 60), "sh_back": ((0.0, -2.6, 1.45), (0, 0, 1.3), 60)}


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
        nf = int(bpy.data.actions[a].frame_range[1])
        if os.environ.get("VIDEO") == "1":
            frames = list(range(nf))
        else:
            frames = [int(x) for x in os.environ.get("FRAMES", ",".join(str(i) for i in range(0, nf, max(1, nf // 6)))).split(",")]
        for view in views:
            loc, tgt, lens = VIEWS[view]
            files = []
            for f in frames:
                s.frame_set(f)
                p = os.path.join(out, "%s_%s_%s_%02d.png" % (a, tag, view, f))
                shoot(cam, loc, tgt, lens, p)
                files.append(p)
            if os.environ.get("VIDEO") == "1":
                ff = __import__("imageio_ffmpeg").get_ffmpeg_exe()
                lst = os.path.join(out, "%s_%s_%s.txt" % (a, tag, view))
                with open(lst, "w") as fh:
                    for _ in range(2):
                        for p in files:
                            fh.write("file '%s'\nduration %.5f\n" % (p, 1 / 24))
                subprocess.run([ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf",
                                "fps=24,format=yuv420p", "-c:v", "libx264", "-crf", "20",
                                os.path.join(out, "%s_%s_%s.mp4" % (a, tag, view))], check=True)
            sheet = Image.new("RGB", (w * len(files[:8]), h), (16, 16, 10))
            step = max(1, len(files) // 8)
            for i, p in enumerate(files[::step][:8]):
                sheet.paste(Image.open(p).convert("RGB"), (i * w, 0))
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
