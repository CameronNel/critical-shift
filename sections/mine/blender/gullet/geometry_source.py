#!/usr/bin/env python3
"""Original Gullet geometry/state source, preserved independently of material repair."""
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
 raise RuntimeError(f'Incomplete Gullet geometry source. Missing={sorted(_expected-_found)}; unexpected={sorted(_found-_expected)}')
_source='\n'.join(p.read_text(encoding='utf-8').rstrip('\n') for p in _parts)+'\n'
exec(compile(_source,str(_here/'geometry_source.full.py'),'exec'),globals(),globals())
