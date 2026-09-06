#!/usr/bin/env python3
"""Canonical Critical Shift Gullet build entrypoint.

The production builder is split into ordered UTF-8 source fragments so it can
live cleanly in the repository's text-only upload path. This launcher
reconstructs the source in memory and executes it as one module. Do not edit a
generated concatenation; edit the appropriate source part instead.
"""
from pathlib import Path

_here=Path(__file__).resolve().parent
_parts=sorted((_here/'source_parts').glob('build_mine.part*.pyfrag'))
_expected={
 'build_mine.part01.pyfrag','build_mine.part02a.pyfrag','build_mine.part02b.pyfrag','build_mine.part02c.pyfrag',
 'build_mine.part03.pyfrag','build_mine.part04.pyfrag','build_mine.part05.pyfrag','build_mine.part06.pyfrag',
 'build_mine.part07.pyfrag','build_mine.part08.pyfrag','build_mine.part09a.pyfrag','build_mine.part09b.pyfrag','build_mine.part10.pyfrag'
}
_found={p.name for p in _parts}
if _found!=_expected:
 missing=sorted(_expected-_found);extra=sorted(_found-_expected)
 raise RuntimeError(f'Incomplete Gullet builder source. Missing={missing}; unexpected={extra}')
_source='\n'.join(p.read_text(encoding='utf-8').rstrip('\n') for p in _parts)+'\n'
exec(compile(_source,str(_here/'build_mine.full.py'),'exec'),globals(),globals())
