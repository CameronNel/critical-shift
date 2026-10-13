from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity'
cs=Path('/tmp/cs-mine-normal-native-final11.cs.txt').read_text().replace('CsMineNormalFinal11','CsMineNormalCompressionFinal11').replace('/tmp/cs-mine-normal-native-final11/','/tmp/cs-mine-normal-compression-final11/')
cs=cs.replace('  foreach(var renderer in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))','''  string scratch="Assets/CriticalShift/Generated/MineNormalCompressionFinal11";if(AssetDatabase.IsValidFolder(scratch))throw new Exception("Scratch exists");AssetDatabase.CreateFolder("Assets/CriticalShift/Generated","MineNormalCompressionFinal11");
  string source=SpawnMapBuild.Folder+"Surfaces/mine-structure/spawn-normal.png";
  File.Copy(source,scratch+"/Raw.png");AssetDatabase.ImportAsset(scratch+"/Raw.png",ImportAssetOptions.ForceSynchronousImport);
  var importer=(TextureImporter)AssetImporter.GetAtPath(scratch+"/Raw.png");importer.textureType=TextureImporterType.NormalMap;importer.sRGBTexture=false;importer.maxTextureSize=4096;importer.textureCompression=TextureImporterCompression.Uncompressed;importer.filterMode=FilterMode.Trilinear;importer.anisoLevel=8;importer.npotScale=TextureImporterNPOTScale.None;importer.wrapMode=TextureWrapMode.Clamp;importer.SaveAndReimport();
  var raw=AssetDatabase.LoadAssetAtPath<Texture2D>(scratch+"/Raw.png");Debug.Log("CS_RAW_NORMAL_FORMAT "+raw.format);
  foreach(var renderer in UnityEngine.Object.FindObjectsByType<MeshRenderer>(FindObjectsSortMode.None))''',1)
cs=cs.replace('  foreach(var view in views)\n  {','  foreach(var view in views)\n  {\n   if(view.name!="R39_02_TUNNEL")continue;')
cs=cs.replace('   foreach(int mode in new[]{4})','''   foreach(int mode in new[]{4,5,6,7})''').replace('material.SetFloat("_CsDiagnostic",mode);','''{material.SetFloat("_CsDiagnostic",4);if(material.name.Contains("mine-structure_000")){if(mode==5)material.SetTexture("_BumpMap",raw);material.SetFloat("_BumpScale",mode==6 ? -.1f:mode==7 ? .1f:1);}}''')
cs=cs.replace('+"ProductionNormal"+', '+"ProductionNormal-mode"+mode+').replace('  Debug.Log("CS_MINE_PRODUCTION_NORMAL_AOV_OK;', '  EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);AssetDatabase.DeleteAsset(scratch);\n  Debug.Log("CS_MINE_PRODUCTION_NORMAL_AOV_OK;')
Path('/tmp/cs-mine-normal-compression-final11.cs.txt').write_text(cs)
csfile=folder/'CsMineNormalCompressionFinal11.cs';shaderfile=folder/'CsMineNormalCompressionFinal11.shader'
if (project/'Temp/UnityLockfile').exists() or csfile.exists() or shaderfile.exists():raise RuntimeError('Busy editor')
try:
 shutil.copyfile('/tmp/cs-mine-normal-compression-final11.cs.txt',csfile);shutil.copyfile('/tmp/cs-mine-normal-corrected-final11.shader',shaderfile)
 with (audit/'cs-mine-normal-compression-final11.wrapper.log').open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineNormalCompressionFinal11.Render','-logFile',str(audit/'cs-mine-normal-compression-final11.native.log')],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('CS_NORMAL_COMPRESSION_DONE',flush=True)
finally:
 for p in [csfile,shaderfile,csfile.with_suffix('.cs.meta'),shaderfile.with_suffix('.shader.meta')]:p.unlink(missing_ok=True)
