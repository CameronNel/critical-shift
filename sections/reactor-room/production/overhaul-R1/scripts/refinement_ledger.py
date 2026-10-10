"""The owner's 140 requested corrections; evidence, not builder claims, closes items."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'review' / 'issue_ledger.json'
TITLES = '''MAIN ACCESS header lettering buried
FUEL HANDLING header lettering buried
Unsupported orange trim below transfer columns
Emergency-control legend inside pedestal
CONTAINMENT board obstructed
COOLANT / POWER board obstructed
REACTOR STABILITY board obstructed
EMERGENCY COOLING plaque obstructed
STANDBY GENERATOR plaque obstructed
RESERVE POWER A plaque obstructed
Duplicate control-bank headings
Faint obstructed WATCH THE GREEN instruction
Overhead EXIT contrast
Wall EXIT contrast
D1/D2 identifiers subdued
Gauge information readability
Switchgear channel identification
Pressure-vessel identification
Valve and circuit identification
Anonymous coloured label strips
Turbine primary casing silhouette
Turbine end cap construction
Turbine coupling transition
Turbine front guard construction
Turbine base support construction
Exhaust transition construction
Stack duct section proportions
Cabinet control grouping
Cabinet access door construction
Gauge housing depth
Handwheel hub/spoke proportions
Pressure vessel shell construction
Paired vessel functional variation
Vessel support construction
Level indicator mounts
Blind pipe termination
Valve body readability
Pipe joint type distinction
Pipe branch junctions
Pipe support attachments
Yellow caged machine identity
Secondary equipment silhouettes
Drum reinforcing hoops and proportions
Drum bung and lid construction
Yellow drum fitting proportion
Drum steel material response
Drum identification
Drum grouping and contact
Cone silhouette
Cone weighted base
Cone coarse grime
Portable barrier silhouette
Barrier frame/support construction
Bollard floor mounting
Bollard cap/finish
Stool construction
Containment tray construction
Puddle wet response
Puddle edges and shape
Puddle drainage relationships
Wet/oil/dirt separation
Physical slab joints
Slab material variation
Crack relief
Crack branch hierarchy
Route paint wear
White directional arrow shape
Route marking continuity
Rectangular drain construction
Circular cover seating
Drainage channel recess depth
Loose grille underside/contact
Equipment floor contact
Floor movement/wear pattern
Floor visual noise
Pool rim layer consolidation
Pool rim thickness hierarchy
Pool yellow marking repetition
Pool rim neutral material readability
Rail post terminations
Rail base attachment
Rail intersection joints
Pool gate construction
Pool lining joint depth
Pool wall port construction
Pool wall staining origins
Pool depth marking contrast
Water plane/depth readability
Pool control operating-face review
Pool service penetrations
Rod cluster primary hierarchy
Drive/absorber distinction
Rod collar construction
Mechanical/status-light separation
Rod guide seating
Bank housing panel structure
Bank frame corner construction
Bank service access
Housing conduit entry
Controlled paired-bank variation
Bank suspension connection
Rod metallic roughness
Bank label/status hierarchy
Lower bank service identification
Housing louvre depth
Crane bridge silhouette
Crane end carriage/running gear
Trolley motor/drum construction
Crane track/support relationship
Girder section readability
Girder connection construction
Column splice construction
Roof panel section depth
Roof panel restrained variation
Cable/service type distinction
Cable termination check
Ceiling service diameter hierarchy
Roof fixture housing/mount
Crane identification/specification
Existing crane maintenance access readability
Concrete panel joint depth
Wall floor/plinth transition
Door leaf construction
Door operating hardware
Door return staining
Circular vent depth
Upper pane frame/recess variation
Upper ledge/bracket supports
Wall box mounting/construction
Clock quantity/readability
Text curve resolution/spacing
Doorway task-lamp identity
Neutral wall illumination
Neutral roof illumination
Dark machinery light separation
Material family response distinction
Material-specific wear
Focal hierarchy
Physical signage visibility audit
Geometry support/intersection audit'''.splitlines()
assert len(TITLES) == 140

def area(i):
    return next(a for end,a in [(20,'signage'),(42,'machinery'),(57,'props'),
        (75,'floor'),(90,'pool'),(105,'rods'),(120,'roof'),(132,'walls'),(140,'holistic')] if i<=end)

def save(rows):
    PATH.parent.mkdir(parents=True,exist_ok=True)
    PATH.write_text(json.dumps({'schema':1,'baseline':'hall-detail-720p-20261007',
        'completion_rule':'Every item needs implementation or demonstrated existing correctness, technical evidence where applicable, and independent visual disposition.',
        'issues':rows},indent=2)+'\n')
    lines=['# Reactor hall: 140-item correction ledger','',
        'Status is per item. Implemented is awaiting evidence; verified requires independent review.',
        '', '| ID | Area | Issue | Status | Implementation / evidence |',
        '|---:|---|---|---|---|']
    for r in rows:
        ev='; '.join(r['implementation']+r['evidence']).replace('|','/')
        lines.append(f"| {r['id']} | {r['area']} | {r['title']} | {r['status']} | {ev} |")
    (PATH.parent/'ISSUE_LEDGER.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    if not PATH.exists():
        save([dict(id=i,title=t,area=area(i),status='pending',implementation=[],evidence=[],reviewer=None)
            for i,t in enumerate(TITLES,1)])
    else: save(json.loads(PATH.read_text())['issues'])
