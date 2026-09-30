#!/usr/bin/env python3
"""Rig check: crew worker (bare or in the hazmat suit) through the RUN, HOLD_SHOVEL and HOLD_PICKAXE actions.
    python render_rig.py -- <output_dir>
env: SUIT=1 wear the suit | ACTIONS=RUN,HOLD_SHOVEL,HOLD_PICKAXE | FRAMES=0,4,8,... | GIF=1 loops | EXPORT=<dir> FBX clips
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import character_rig as RIG  # noqa: E402
import character_suit as CS  # noqa: E402
import character_worker as CW  # noqa: E402
from render_character_sheet import shoot, studio  # noqa: E402
from render_worker import backdrop  # noqa: E402

VIEWS = {
    "RUN": (("side", (5.2, 0.0, 1.0), (0, 0, 0.98), 52), ("front", (0.0, 5.2, 1.0), (0, 0, 0.98), 52)),
    "HOLD_SHOVEL": (("front", (0.0, 4.0, 0.95), (0, 0, 0.90), 52), ("three_q", (-3.0, 3.0, 1.0), (0, 0, 0.90), 52),
                    ("side_r", (-4.2, 0.0, 0.95), (0, 0, 0.90), 52)),
    "HOLD_PICKAXE": (("front", (0.0, 4.0, 0.95), (0, 0, 0.90), 52), ("three_q", (3.0, 3.0, 1.0), (0, 0, 0.90), 52),
                     ("side_r", (-4.2, 0.0, 0.95), (0, 0, 0.90), 52)),
}
TOOL_FOR = {"RUN": None, "HOLD_SHOVEL": "SHOVEL", "HOLD_PICKAXE": "PICKAXE"}


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    from PIL import Image
    s, cam = studio((480, 640), 48)
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
    made = {"RUN": RIG.make_run_cycle, "HOLD_SHOVEL": RIG.make_shovel_hold, "HOLD_PICKAXE": RIG.make_pickaxe_hold}
    wanted = os.environ.get("ACTIONS", "RUN,HOLD_SHOVEL,HOLD_PICKAXE").split(",")
    for a in wanted:
        made[a](arm)
        print("RIG action", a, "ok")
    tag = "suit" if suit else "bare"
    for a in wanted:
        RIG.set_action(arm, a)
        RIG.show_tool(tools, TOOL_FOR[a])
        frames = [int(x) for x in os.environ.get("FRAMES", "0,3,6,9,12,15,18,21" if a == "RUN" else "0,12,24,36").split(",")]
        for view, loc, tgt, lens in VIEWS[a]:
            files = []
            for f in frames:
                s.frame_set(f)
                p = os.path.join(out, "%s_%s_%s_%02d.png" % (a, tag, view, f))
                shoot(cam, loc, tgt, lens, p)
                files.append(p)
            sheet = Image.new("RGB", (480 * len(files), 640), (16, 16, 10))
            for i, p in enumerate(files):
                sheet.paste(Image.open(p).convert("RGB"), (i * 480, 0))
            sheet.save(os.path.join(out, "%s_%s_%s.png" % (a, tag, view)))
        if os.environ.get("GIF") == "1":
            for view, loc, tgt, lens in VIEWS[a][:2]:
                ims = []
                nf = int(bpy.data.actions[a].frame_range[1])
                for f in range(nf):
                    s.frame_set(f)
                    p = os.path.join(out, "gif_%s_%s_%s_%02d.png" % (a, tag, view, f))
                    shoot(cam, loc, tgt, lens, p)
                    ims.append(Image.open(p).convert("P", palette=Image.ADAPTIVE))
                ims[0].save(os.path.join(out, "%s_%s_%s.gif" % (a, tag, view)), save_all=True, append_images=ims[1:],
                            duration=42, loop=0)
    if os.environ.get("EXPORT"):
        os.makedirs(os.environ["EXPORT"], exist_ok=True)
        for a in wanted:
            path = RIG.export_fbx(root, arm, os.path.join(os.environ["EXPORT"], "crew_worker_%s.fbx" % a), action=a)
            print("RIG fbx", os.path.basename(path), os.path.getsize(path) // 1024, "KB")
    print("RIG done")


if __name__ == "__main__":
    main()
