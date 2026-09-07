"""Serialize only GPU Blender jobs across the user's independent facility chats.

python gpu_gate.py --owner cooling -- blender.exe --background ...
The OS releases the lock if a worker crashes. No other process is terminated.
"""
import argparse
import datetime
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--owner', required=True)
p.add_argument('--max-wait', type=int, default=900)
p.add_argument('command', nargs=argparse.REMAINDER)
a = p.parse_args()
cmd = a.command[1:] if a.command[:1] == ['--'] else a.command
if not cmd:
    p.error('a command is required after --')
root = Path(__file__).resolve().parent
with (root / 'gpu.lock').open('a+b') as lock:
    lock.seek(0, 2)
    if lock.tell() == 0:
        lock.write(b'0'); lock.flush()
    start = time.monotonic()
    announced = False
    while True:
        try:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            break
        except OSError:
            if not announced:
                print(f'GPU queue: {a.owner} waiting for the current job', flush=True)
                announced = True
            if time.monotonic() - start > a.max_wait:
                print('GPU queue wait expired; no process was stopped', flush=True)
                sys.exit(75)
            time.sleep(1)
    info = {'owner': a.owner, 'pid': os.getpid(), 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'running'}
    (root / 'gpu_owner.json').write_text(json.dumps(info, indent=2))
    print(f'GPU acquired: {a.owner}', flush=True)
    try:
        code = subprocess.call(cmd)
    finally:
        (root / 'gpu_owner.json').write_text(json.dumps({'status': 'idle', 'previous_owner': a.owner}))
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    sys.exit(code)
