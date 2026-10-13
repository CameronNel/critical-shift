from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');features=root/'runtime/unity/Assets/CriticalShift/Features/Player';editor=root/'runtime/unity/Assets/CriticalShift/Bootstrap/Player/Editor';shader=features/'CsMineTransportSplitFinal12.shader';helper=editor/'CsMineTransportSplitFinal12.cs'
code=(features/'BlenderSurface.shader').read_text();code=code.replace('Shader "CriticalShift/BlenderSurface"','Shader "CriticalShift/DiagnosticTransportSplitFinal12"');code=code.replace('    Properties\n    {','    Properties\n    {\n        _CsSplit ("Diagnostic transport split", Float)=0');code=code.replace('#pragma surface surf StandardSpecular','#pragma surface surf DiagnosticTransportSplit');code=code.replace('#include "UnityStandardUtils.cginc"','#include "UnityStandardUtils.cginc"\n        #include "UnityPBSLighting.cginc"')
functions='''
        float _CsSplit;
        half4 LightingDiagnosticTransportSplit(SurfaceOutputStandardSpecular s,half3 viewDir,UnityGI gi)
        {
            half4 total=LightingStandardSpecular(s,viewDir,gi);
            float3 halfDir=Unity_SafeNormalize(gi.light.dir+viewDir);
            float nv=abs(dot(s.Normal,viewDir));float nl=saturate(dot(s.Normal,gi.light.dir));float lh=saturate(dot(gi.light.dir,halfDir));
            half3 diffuseColour=s.Albedo*(1-SpecularStrength(s.Specular));
            half3 direct=diffuseColour*gi.light.color*(DisneyDiffuse(nv,nl,lh,1-s.Smoothness)*nl);
            half3 indirect=diffuseColour*gi.indirect.diffuse;
            return half4(_CsSplit<.5 ? total.rgb : _CsSplit<1.5 ? direct : _CsSplit<2.5 ? indirect : _CsSplit<3.5 ? total.rgb-direct-indirect : half3(1,1,1),1);
        }
        void LightingDiagnosticTransportSplit_GI(SurfaceOutputStandardSpecular s,UnityGIInput data,inout UnityGI gi)
        { LightingStandardSpecular_GI(s,data,gi); }
'''
code=code.replace('        void surf(',functions+'\n        void surf(')
Path('/tmp/cs-mine-transport-split-final12.shader').write_text(code)
assert not shader.exists() and not helper.exists();shader.write_text(code);shutil.copy2('/tmp/cs-mine-transport-split-final12.cs.txt',helper)
try:subprocess.run(['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(root/'runtime/unity'),'-executeMethod','CsMineTransportSplitFinal12.Render','-logFile',str(root/'runtime/out/mine-bake-audit/transport-split-final12.native.log')],cwd=root,check=True)
finally:
 for p in [shader,helper]:p.unlink(missing_ok=True);Path(str(p)+'.meta').unlink(missing_ok=True)
