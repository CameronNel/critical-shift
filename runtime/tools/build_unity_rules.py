"""Build canonical first-party rules for Unity. No copied C# sources or third-party game packages."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import uuid

RUNTIME = Path(__file__).resolve().parents[1]
DOTNET = RUNTIME / 'dotnet'
PROJECT = DOTNET / 'src/CriticalShift.Application/CriticalShift.Application.csproj'
DESTINATION = RUNTIME / 'unity/Assets/CriticalShift/Plugins/Rules'


def build():
    subprocess.run(['dotnet', 'build', str(PROJECT), '-c', 'Release', '-p:ContinuousIntegrationBuild=true'],
                   cwd=DOTNET, check=True)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    assemblies = sorted((PROJECT.parent / 'bin/Release/netstandard2.1').glob('CriticalShift*.dll'))
    if len(assemblies) != 8:
        raise RuntimeError('Expected Application and its seven canonical Domain assemblies.')
    for assembly in assemblies:
        path = DESTINATION / assembly.name
        shutil.copyfile(assembly, path)
        meta = Path(str(path) + '.meta')
        if not meta.exists():
            meta.write_text('fileFormatVersion: 2\nguid: ' + uuid.uuid4().hex + '''
PluginImporter:
  externalObjects: {}
  serializedVersion: 2
  iconMap: {}
  executionOrder: {}
  defineConstraints: []
  isPreloaded: 0
  isOverridable: 0
  isExplicitlyReferenced: 1
  validateReferences: 1
  platformData:
  - first:
      Any:
    second:
      enabled: 1
      settings: {}
  userData:
  assetBundleName:
  assetBundleVariant:
''')
    sources = sorted(p for p in (DOTNET / 'src').rglob('*') if p.suffix in ('.cs', '.csproj') and
                     not {'bin', 'obj'}.intersection(p.parts) and 'ProcessLifetime' not in str(p))
    sources += [DOTNET / 'Directory.Build.props', DOTNET / 'global.json']
    manifest = {'target': 'netstandard2.1', 'sources': {}, 'assemblies': {}}
    for path in sources:
        manifest['sources'][path.relative_to(RUNTIME).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in assemblies:
        manifest['assemblies'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (DESTINATION / 'rules-build.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Built 8 first-party Unity rule assemblies from canonical sources.')


if __name__ == '__main__':
    build()
