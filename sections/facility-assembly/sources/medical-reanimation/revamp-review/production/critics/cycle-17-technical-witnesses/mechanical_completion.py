from pathlib import Path
script=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation/revamp-review/production/critics/cycle-17-technical-witnesses/targeted_probe.py')
exec(compile(script.read_text().split('targets=[')[0],str(script),'exec'))
targets=[('Lower captive scissor track','Cart lift load crossmember'),('Cart lift load crossmember','Cart lower frame rail'),('Pressed caster fork','Wheel hub'),('Wheel hub','Caster rubber tyre'),('Reserve folded cap','Battery plinth'),('Battery plinth','Floor')]
out=[pair(a,b) for a,b in targets]
(W/'mechanical-completion.json').write_text(json.dumps({'source_sha256':before,'source_unchanged':hashlib.sha256((R/'module_overhaul_R2.blend').read_bytes()).hexdigest()==before,'pairs':out,'no_source_save':True},indent=2)+'\n')
print('MECHANICAL_COMPLETION_COMPLETE',len(out),flush=True)
