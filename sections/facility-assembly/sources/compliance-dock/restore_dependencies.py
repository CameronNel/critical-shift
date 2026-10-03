"""Restore SHA-verified inherited native dependencies from ordinary Git parts.

Only writes listed repository paths whose existing bytes are the expected payload
or an LFS pointer for that exact payload. No scene construction or source edits.
Uses Python's standard library; GitHub LFS credentials are unnecessary.
"""
import argparse, hashlib, io, json, tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACK=Path(__file__).resolve().parent/'revamp/production/portable_dependencies'
p=argparse.ArgumentParser();p.add_argument('--verify-only',action='store_true');a=p.parse_args()
manifest=json.loads((PACK/'manifest.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for row in manifest['files']:
    target=(ROOT/row['path']).resolve()
    if not target.is_relative_to(ROOT):raise RuntimeError('Dependency path outside checkout')
    if target.is_file():
        data=target.read_bytes()
        if sha(data)==row['sha256']:continue
        pointer=data.decode('ascii',errors='ignore')
        if not pointer.startswith('version https://git-lfs.github.com/spec/v1') or 'oid sha256:'+row['sha256'] not in pointer:
            raise RuntimeError('Refusing to replace different existing bytes: '+row['path'])
    elif a.verify_only:raise RuntimeError('Missing dependency: '+row['path'])
    if a.verify_only:raise RuntimeError('Unhydrated dependency: '+row['path'])

class Parts(io.RawIOBase):
    def __init__(self):self.index=0;self.offset=0;self.buffer=b'';self.digest=hashlib.sha256();self.read_size=0
    def readable(self):return True
    def readinto(self,out):
        if self.offset==len(self.buffer):
            if self.index==len(manifest['parts']):return 0
            row=manifest['parts'][self.index];self.buffer=(PACK/row['path']).read_bytes();self.offset=0;self.index+=1
            if len(self.buffer)!=row['bytes'] or sha(self.buffer)!=row['sha256']:raise RuntimeError('Corrupt dependency part: '+row['path'])
            self.digest.update(self.buffer);self.read_size+=len(self.buffer)
        count=min(len(out),len(self.buffer)-self.offset);out[:count]=self.buffer[self.offset:self.offset+count];self.offset+=count;return count

if not a.verify_only:
    expected={row['path']:row for row in manifest['files']};seen=set();parts=Parts()
    with tarfile.open(fileobj=io.BufferedReader(parts),mode='r|gz') as archive:
        for member in archive:
            if not member.isfile() or member.name not in expected or member.name in seen:raise RuntimeError('Unexpected archive member')
            data=archive.extractfile(member).read();row=expected[member.name]
            if len(data)!=row['bytes'] or sha(data)!=row['sha256']:raise RuntimeError('Dependency payload differs: '+member.name)
            target=ROOT/member.name;target.parent.mkdir(parents=True,exist_ok=True)
            if not target.is_file() or sha(target.read_bytes())!=row['sha256']:target.write_bytes(data)
            seen.add(member.name)
        # Consume the gzip/tar trailing padding so every part is authenticated.
        while parts.readinto(bytearray(65536)):pass
    if seen!=set(expected) or parts.digest.hexdigest()!=manifest['archive_sha256']:raise RuntimeError('Incomplete dependency archive')
for row in manifest['files']:
    if sha((ROOT/row['path']).read_bytes())!=row['sha256']:raise RuntimeError('Restored dependency mismatch')
print('DEPENDENCIES_VERIFIED',len(manifest['files']))
