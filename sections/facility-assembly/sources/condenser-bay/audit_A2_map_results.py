"""Evaluate exact brief pass values from retained original-tool reports.
Commands completing successfully are not equivalent to checks passing.
"""
import argparse,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main(label,baseline):
 p=HERE/'evidence-A2'/label;v=p/'validation';base=Path(baseline)
 read=lambda name:json.loads((v/name).read_text())
 gates={};details={}
 for mode,want,file in [('normal',17,'walk_report.json'),('colliders',10,'walk_report_colliders.json'),('meltdown',20,'walk_report_meltdown.json')]:
  r=read(file);passed=sum(x['passed'] for x in r['routes']);total=len(r['routes'])
  expected_total=18 if mode=='normal' else want
  failures=[x['route'] for x in r['routes'] if not x['passed']]
  closed=sum(x['blocks'] for x in r['closed_doors'])
  gates['walk_'+mode]=passed==want and total==expected_total and (mode!='normal' or failures==['yard_to_refinery_freight (cart route)'])
  if mode!='meltdown':gates['closed_doors_'+mode]=closed==len(r['closed_doors'])==13
  details[mode]={'passed':passed,'total':total,'failures':failures,'closed':closed}
 e=read('evac_report.json')['redundancy']['condenser'];gates['condenser_evacuation']=e['routes_evacuation']==2 and not e['single_door_failures_that_cut_off'];details['evacuation']=e
 d=read('door_audit.json');gates['doors']=len(d['doors'])==45 and not d['flagged'];details['doors']={'total':len(d['doors']),'flagged':len(d['flagged'])}
 key=lambda x:(x['slab_owner'],x['over_floor_of'],x['level'])
 old={key(x) for x in json.loads((base/'floor_audit.json').read_text())['flagged']}
 now=read('floor_audit.json')['flagged'];new=[x for x in now if key(x) not in old];new_cond=[x for x in new if any('ROOM_condenser-bay' in str(k) for k in key(x))]
 gates['no_new_condenser_floor_pair']=not new_cond;details['floor']={'baseline_pairs':len(old),'candidate_pairs':len(now),'new_pairs':new,'new_condenser_pairs':new_cond}
 tris=read('perf_report.json')['rooms']['ROOM_condenser-bay']['triangles'];gates['condenser_triangles']=tris<=400000;details['triangles']=tris
 exp=json.loads((p/'export/binding_manifest.json').read_text())['reimport_check'];gates['scoped_export']=not exp['missing'] and not exp['extra'] and exp['n_bounds_mismatch']==0;details['export']=exp
 light=read('lighting.json')['views'];required=['condenser_D01','condenser_inside','condenser_escape_tunnel','stair_bottom']
 for n in required:
  row=light[n];gates['lighting_'+n]=row['median']>=.15 and row['near_black']<=.15 and row['clipped']<=.05
 details['lighting']={'total':len(light),'stock_readable':sum(x['readable'] for x in light.values()),'misses':[n for n,r in light.items() if not r['readable']],'required':{n:light[n] for n in required}}
 gates['no_new_other_lighting_miss']=set(details['lighting']['misses'])-set(required)<={'spine_mid'}
 pattern=r'INTRUSION z=([-\d.]+) (\S+) <- (\S+):'
 pairs=lambda txt:{m.groups() for m in re.finditer(pattern,txt) if 'ROOM_condenser-bay' in m.group(0)}
 overlaps=(v/'overlaps.txt').read_text();prior=(base/'overlaps.txt').read_text()
 new_intrusions=sorted(pairs(overlaps)-pairs(prior));gates['no_new_condenser_overlap_pair']=not new_intrusions;details['overlaps']={'new_condenser_pairs':new_intrusions,'scope':'Pair/height comparison against baseline; existing room/roof/connector contacts retained in raw logs, not an all-clear geometry assertion.'}
 commands=json.loads((p/'commands.json').read_text());gates['all_commands_exit_zero']=len(commands['commands'])==11 and all(x['exit_code']==0 for x in commands['commands'])
 report={'label':label,'status':'PASS' if all(gates.values()) else 'FAIL','gates':gates,'details':details,'baseline':str(base),'scope':'Exact brief map checks. Does not certify Unity runtime, original inherited high-level roof/gallery design, or art acceptance.'}
 (p/'pass-values.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'gates':gates},indent=2));raise SystemExit(0 if report['status']=='PASS' else 1)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('label');ap.add_argument('--baseline',required=True);a=ap.parse_args();main(a.label,a.baseline)
