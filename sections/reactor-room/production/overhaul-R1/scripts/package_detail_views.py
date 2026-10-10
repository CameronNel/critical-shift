"""Verify and package the rendered originals; make a labeled review contact sheet."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import zipfile

from PIL import Image, ImageDraw, ImageFont, ImageStat

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path, help='Directory containing all ten rendered views')
root = parser.parse_args().output.resolve()
manifest = json.loads((root/'render_manifest.json').read_text())
provenance = json.loads((root/'provenance.json').read_text())
assert manifest['resolution'] == [1280,720] and manifest['preview'] is False
assert manifest['engine']=='CYCLES' and manifest['samples_max']==96
assert manifest['adaptive_min_samples']==32 and abs(manifest['adaptive_threshold']-.015)<1e-6
assert manifest['path_guiding'] is True and manifest['guiding_training_samples']==64
assert manifest['denoiser']=='OPENIMAGEDENOISE' and manifest['max_bounces']==12
assert len(manifest['views']) == 10
assert {v['name'][:2] for v in manifest['views']} == {f'{i:02}' for i in range(1,11)}
assert len({v['file'] for v in manifest['views']}) == 10
assert len({v['sha256'] for v in manifest['views']}) == 10
assert provenance['integrated_scene_sha256'] == manifest['source_sha256']
if provenance.get('candidate'):
    assert hashlib.sha256((root/'reactor_hall_refined.blend').read_bytes()).hexdigest() == manifest['source_sha256'], 'Packaged scene differs from reviewed scene'
    assert provenance['renderer_source_sha256'] == manifest['renderer_sha256'], 'Render recipe differs from recorded provenance'
    acceptance=provenance.get('independent_art_acceptance')
    assert isinstance(acceptance,dict) and acceptance.get('status')=='accepted', 'Correction candidate still lacks independent art acceptance'
    assert acceptance['source_sha256']==manifest['source_sha256']
    assert len(acceptance['accepted_issue_ids'])==140 and set(acceptance['accepted_issue_ids'])==set(range(1,141)), 'All 140 issues must be independently accepted'
    assert set(acceptance['area_scores'])=={'signage','machinery','props','floor','pool','rods','roof','walls','holistic'}
    assert acceptance['overall_score']>=90 and min(acceptance['area_scores'].values())>=85
    report_path=root/acceptance['report']
    assert report_path.is_file()
    assert hashlib.sha256(report_path.read_bytes()).hexdigest()==acceptance['report_sha256']
    assert manifest['source_sha256'] in report_path.read_text()
    independent_path=root/provenance['independent_dispositions']
    independent=json.loads(independent_path.read_text())
    assert independent['candidate']['source_sha256']==manifest['source_sha256']
    assert independent['accepted_issue_ids']==acceptance['accepted_issue_ids'] and not independent['pending_ids']
    assert not independent.get('partial_issue_ids'), 'Partial independent review rows remain unresolved'
    assert len(independent['issues'])==140 and {row['id'] for row in independent['issues']}==set(range(1,141))
    assert all(row['status'].startswith('accepted') and row['evidence']['candidate_sha256']==manifest['source_sha256']
               for row in independent['issues'])
    assert independent['score']==acceptance['overall_score'] and independent['area_scores']==acceptance['area_scores']
required_checks = {'contract', 'palette', 'piping', 'clearance',
                   'frame_rate_independence', 'control_room'}
if provenance.get('candidate'):
    required_checks |= {'bores','motion','support','floor_guidance','gantry_guard','roof_utility','rod_guide','blind_cover','door_hardware'}
assert required_checks <= provenance['checks'].keys()
for name in required_checks:
    check = provenance['checks'][name]
    assert check['status'] == 'PASS' and (root/check['log']).is_file(), name
    if provenance.get('candidate'):
        assert check['source_sha256']==manifest['source_sha256'], name
        assert hashlib.sha256((root/check['log']).read_bytes()).hexdigest()==check['log_sha256'], name
if provenance.get('candidate'):
    technical_path=root/provenance['technical_check_summary']
    technical=json.loads(technical_path.read_text())
    assert technical['source_sha256']==manifest['source_sha256'] and technical['all_pass']
    assert len(technical['checks'])==14 and all(c['pass'] and c['exit']==0 for c in technical['checks'])
    check_names={('frame_rate_independence' if c['check']=='fps' else c['check']) for c in technical['checks']}
    assert check_names==required_checks-{'control_room'}
# A assembled main manifest must retain its actual per-camera original records.
main_original_files=[]
if manifest.get('assembled_from'):
    original_views={}
    main_metadata={k:v for k,v in manifest.items() if k not in {'views','assembled_from','assembly_scope'}}
    for record in manifest['assembled_from']:
        original_path=root/record['manifest']
        assert hashlib.sha256(original_path.read_bytes()).hexdigest()==record['manifest_sha256']
        original=json.loads(original_path.read_text())
        assert {k:v for k,v in original.items() if k!='views'}==main_metadata
        for row in original['views']:
            assert row['name'] not in original_views
            original_views[row['name']]=row
            panel=original_path.parent/row['file'];raw=panel.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==row['sha256']
            assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
            main_original_files.append(panel)
        main_original_files.append(original_path)
    assert original_views=={row['name']:row for row in manifest['views']}
manifest['views'].sort(key=lambda view: view['name'])
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
label_font = ImageFont.truetype(font_path, 19)
title_font = ImageFont.truetype(font_path, 27)
note_font = ImageFont.truetype(font_path, 16)
pad, gap, thumb_w, thumb_h, label_h = 20, 16, 640, 360, 44
sheet = Image.new('RGB', (2*thumb_w+2*pad+gap, 5*(thumb_h+label_h)+gap*4+110), '#101317')
draw = ImageDraw.Draw(sheet)
draw.text((pad,18),'REACTOR HALL — TEN DETAIL VIEWS',font=title_font,fill='#eef1f5')
draw.text((pad,57),provenance['source_commit_local_time']+' source · 1280 × 720 originals · Cycles',font=note_font,fill='#b9c1cc')
checks=[]
for index, view in enumerate(manifest['views']):
    path=root/view['file']
    data=path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    width,height,depth,color=struct.unpack('>IIBB',data[16:26])
    assert (width,height,depth,color)==(1280,720,16,2), (path.name,width,height,depth,color)
    assert hashlib.sha256(data).hexdigest()==view['sha256']
    with Image.open(path) as raw:
        raw.verify()
    with Image.open(path) as raw:
        im=raw.convert('RGB')
        stat=ImageStat.Stat(im)
        assert max(stat.stddev)>8, f'Blank image: {path.name}'
        im.thumbnail((thumb_w,thumb_h), Image.Resampling.LANCZOS)
        x=pad+(index%2)*(thumb_w+gap)
        y=100+(index//2)*(thumb_h+label_h+gap)
        sheet.paste(im,(x,y))
        draw.text((x+8,y+thumb_h+10),f"{index+1:02}  {view['title']}",font=label_font,fill='#edf0f4')
    checks.append({'file':path.name,'resolution':[width,height],'bit_depth':depth,'sha256_matches':True})
sheet.save(root/'contact-sheet.jpg',quality=95,subsampling=0)
(root/'image_checks.json').write_text(json.dumps({'count':len(checks),'status':'PASS','images':checks},indent=2)+'\n')
archive=root/'reactor-hall-10-views-720p.zip'
supplemental_files=list(main_original_files)
def verify_supplement_source(data, path, family):
    """Keep reviewed originals bound to their actual historical source."""
    if data['source_sha256']==manifest['source_sha256']:
        return False
    proof_path=root/provenance['historical_supplement_carry']
    proof=json.loads(proof_path.read_text())
    assert proof['current_source_sha256']==manifest['source_sha256']
    delta_path=root/proof['delta']
    assert hashlib.sha256(delta_path.read_bytes()).hexdigest()==proof['delta_sha256']
    delta=json.loads(delta_path.read_text())
    assert delta['pass_check'] and delta['source_sha256']==proof['prior_source_sha256']
    assert set(delta['changed'])=={'RH refine legacy drums GALV','RH refine legacy drums RED',
        'RH stations props GALV','RH stations props RED','RH stations props YELLOW'}
    assert not delta['added'] and not delta['removed'] and not delta['unexpected_changes']
    if delta['candidate_sha256']!=manifest['source_sha256']:
        # Retain both actual comparisons; do not invent a cumulative snapshot.
        transitions=proof['transition_deltas'];assert len(transitions) in (1,2,3,4)
        transition_path=root/transitions[0]['path']
        assert hashlib.sha256(transition_path.read_bytes()).hexdigest()==transitions[0]['sha256']
        transition=json.loads(transition_path.read_text())
        assert transition['source_sha256']==delta['candidate_sha256']
        assert transition['pass_check']
        expected_changed={'R2 floor','BANK_A_DRIVE_COLUMN','BANK_B_DRIVE_COLUMN',
            'RP bank A absorber pins rp CHROME','RP bank B absorber pins rp CHROME',
            'RH services R2 PIPING diffuser STEEL','RH services R2 PIPING diffuser slot BLACK',
            'RH services R2 PIPING flange IRON'}
        labels=('REACTOR STABILITY','COOLANT / POWER','CONTAINMENT')
        for label in labels:
            expected_changed.add('RH refine '+label+' scale')
            expected_changed.update('RH refine board '+label+' LEVEL'+str(i) for i in range(10))
        expected_added={'RH floor service oil film'}|{
            'RH refine '+label+' scale '+str(i) for label in labels for i in (0,25,75,100)}
        assert set(transition['changed'])==expected_changed and len(transition['changed'])==41
        assert set(transition['added'])==expected_added and len(transition['added'])==13
        assert not transition['removed'] and not transition['unexpected_changes']
        assert transition['unchanged_count']==1879
        supplemental_files.append(transition_path)
        final_sha=transition['candidate_sha256']
        if len(transitions)>=2:
            last_path=root/transitions[1]['path']
            assert hashlib.sha256(last_path.read_bytes()).hexdigest()==transitions[1]['sha256']
            last=json.loads(last_path.read_text())
            assert last['source_sha256']==final_sha and last['pass_check']
            assert set(last['changed'])=={'R2 floor','RH services R2 PIPING diffuser STEEL','RH services R2 PIPING diffuser slot BLACK'}
            assert not last['added'] and not last['removed'] and not last['unexpected_changes']
            assert last['unchanged_count']==1930
            final_sha=last['candidate_sha256'];supplemental_files.append(last_path)
        if len(transitions)>=3:
            roof_path=root/transitions[2]['path']
            assert hashlib.sha256(roof_path.read_bytes()).hexdigest()==transitions[2]['sha256']
            roof=json.loads(roof_path.read_text())
            assert roof['source_sha256']==final_sha and roof['pass_check']
            assert roof['changed']==['RH walls girders STEEL']
            assert not roof['added'] and not roof['removed'] and not roof['unexpected_changes']
            assert roof['unchanged_count']==1932
            final_sha=roof['candidate_sha256'];supplemental_files.append(roof_path)
        if len(transitions)==4:
            joint_path=root/transitions[3]['path']
            assert hashlib.sha256(joint_path.read_bytes()).hexdigest()==transitions[3]['sha256']
            joint=json.loads(joint_path.read_text())
            assert joint['source_sha256']==final_sha and joint['pass_check']
            assert set(joint['changed'])=={'RH walls girders STEEL','RH walls girders GALV','RH walls girders ORANGE'}
            assert set(joint['added'])=={'RH roof crossings end plates STEEL','RH roof crossings washers GALV','RH roof crossings bolt heads GALV'}
            assert not joint['removed'] and not joint['unexpected_changes']
            assert joint['unchanged_count']==1930
            final_sha=joint['candidate_sha256'];supplemental_files.append(joint_path)
        assert final_sha==manifest['source_sha256']
    else:
        assert not proof.get('transition_deltas')
    required={'steam_tap':{38},'native_geometry':{56,71},'door_detail':{124},
              'door_hardware':{124},'mechanical':{112}}
    assert family in required
    entry=proof['families'][family]
    assert set(entry['accepted_issue_ids'])==required[family]
    assert required[family]<=set(acceptance['accepted_issue_ids'])
    records=[record for record in entry['manifests'] if record['path']==str(path.relative_to(root))]
    assert len(records)==1
    record=records[0]
    assert record['source_sha256']==data['source_sha256']
    assert record['manifest_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    if data['source_sha256']!=proof['prior_source_sha256']:
        # The one older mechanical original is the C80 lower splice. Check
        # both comparison legs rather than relying on prose for transitivity.
        assert family=='mechanical' and {v['name'] for v in data['views']}=={'51_column_splice_lower'}
        prior_delta_path=root/record['prior_delta']
        assert hashlib.sha256(prior_delta_path.read_bytes()).hexdigest()==record['prior_delta_sha256']
        prior=json.loads(prior_delta_path.read_text())
        assert prior['source_sha256']==data['source_sha256']
        assert prior['candidate_sha256']==proof['prior_source_sha256'] and prior['pass_check']
        expected={f'RH refine door hardware {door}.{leaf} STEEL'
                  for door in ('COOLING PLANT','FUEL HANDLING','MAIN ACCESS')
                  for leaf in ('door leaf','door leaf.001')}
        assert set(prior['changed'])==expected and len(prior['changed'])==6
        assert not prior['added'] and not prior['removed'] and not prior['unexpected_changes']
        prior_report=root/record['prior_carry_report']
        assert hashlib.sha256(prior_report.read_bytes()).hexdigest()==record['prior_carry_report_sha256']
        assert all(source in prior_report.read_text() for source in (data['source_sha256'],proof['prior_source_sha256']))
        supplemental_files.extend((prior_delta_path,prior_report))
    report=root/entry['report']
    assert hashlib.sha256(report.read_bytes()).hexdigest()==entry['report_sha256']
    text=report.read_text()
    assert all(source in text for source in (data['source_sha256'],
        proof['prior_source_sha256'],manifest['source_sha256']))
    supplemental_files.extend((proof_path,delta_path,report))
    return True

native_signs=provenance.get('supplemental_native_signs')
if provenance.get('candidate'):
    assert native_signs, 'Current native text evidence must be registered before final packaging'
if native_signs:
    recipe=root/native_signs['recipe']
    recipe_hash=hashlib.sha256(recipe.read_bytes()).hexdigest()
    assert recipe_hash==native_signs['recipe_sha256']
    scope=root/native_signs['scope']
    scope_data=json.loads(scope.read_text())
    assert scope_data['source_sha256']==manifest['source_sha256']
    assert scope_data['base_recipe_sha256']==manifest['renderer_sha256']
    assert scope_data['recipe_sha256']==recipe_hash and scope_data['resolution']==[640,360]
    assert set(scope_data['views'])=={'17','39','40','41','42','44'}
    # The approved native recipe keeps the canonical cameras and quality.
    # Compare the code too: only resolution and explicit task/source guards
    # may differ from the renderer used for the ten 720p originals.
    canonical=Path(__file__).with_name('render_detail_views.py').read_text()
    source_guard=("assert hashlib.sha256(source.read_bytes()).hexdigest() == '"+
                  manifest['source_sha256']+"', 'Wrong native-sign source'\n"
                  "assert args.inspection and args.views and set(args.views) <= {'17','39','40','41','42','44'}\n"
                  "assert not args.preview and args.samples == 96 and args.state in {1.0,.5,.1} and not args.save_review_scene\n")
    normalized=recipe.read_text()
    assert normalized.count(source_guard)==1
    normalized=normalized.replace(source_guard,'').replace(
        'scene.render.resolution_x = 480 if args.preview else 640',
        'scene.render.resolution_x = 480 if args.preview else 1280').replace(
        'scene.render.resolution_y = 270 if args.preview else 360',
        'scene.render.resolution_y = 270 if args.preview else 720')
    assert normalized==canonical, 'Native-sign recipe changed beyond its approved scope'
    expected={1.0:{'39_watch_instruction','40_exit_north','41_exit_west',
                   '42_exit_diagonal','44_wall_clock','17_board_direct'},
              .5:{'17_board_direct'},.1:{'17_board_direct'}}
    states=set()
    for entry in native_signs['manifests']:
        path=root/entry['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        data=json.loads(path.read_text());state=data['stability']
        assert state in expected and state not in states
        states.add(state)
        assert data['source_sha256']==manifest['source_sha256'] and data['renderer_sha256']==recipe_hash
        assert data['engine']=='CYCLES' and data['resolution']==[640,360] and not data['preview']
        assert data['samples_max']==96 and data['adaptive_min_samples']==32
        assert abs(data['adaptive_threshold']-.015)<1e-6
        assert data['path_guiding'] and data['guiding_training_samples']==64
        assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12 and data['frame']==1
        assert len(data['views'])==len(expected[state])
        assert {view['name'] for view in data['views']}==expected[state]
        for view in data['views']:
            panel=path.parent/view['file'];raw=panel.read_bytes()
            assert struct.unpack('>IIBB',raw[16:26])==(640,360,16,2)
            assert hashlib.sha256(raw).hexdigest()==view['sha256']
            supplemental_files.append(panel)
        supplemental_files.append(path)
    assert states==set(expected), 'Native board proof needs all three stability states'
    supplemental_files.extend((recipe,scope))
if manifest.get('assembled_from'):
    originals={}
    metadata={k:v for k,v in manifest.items() if k not in {'views','assembled_from','assembly_scope'}}
    for entry in manifest['assembled_from']:
        path=root/entry['manifest']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['manifest_sha256']
        original=json.loads(path.read_text())
        assert {k:v for k,v in original.items() if k!='views'}==metadata
        for view in original['views']:
            assert view['name'] not in originals
            panel=path.parent/view['file']
            raw=panel.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==view['sha256']
            assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
            originals[view['name']]=view
            supplemental_files.append(panel)
        supplemental_files.append(path)
    assert originals=={view['name']:view for view in manifest['views']}, 'Assembled main manifest differs from originals'
gauge_recipe_hash=provenance.get('supplemental_gauge_recipe_sha256')
if gauge_recipe_hash:
    proof_path=root/provenance['supplemental_gauge_sheet']
    proof=json.loads(proof_path.read_text())
    assert proof['source_sha256']==manifest['source_sha256']
    assert proof['native_panels']==16 and proof['native_resolution']==[640,360]
    names=[]
    current_recipe_seen=False
    for source in proof['panel_manifests']:
        path=root/source['path']
        data=json.loads(path.read_text())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==source['manifest_sha256']
        assert data['source_sha256']==source['source_sha256']
        assert data['resolution']==[640,360] and data['samples_max']==96 and not data['preview']
        assert data['adaptive_min_samples']==32 and data['path_guiding']
        recipe=root/source['recipe']
        assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']
        if data['source_sha256']==manifest['source_sha256']:
            assert data['renderer_sha256']==gauge_recipe_hash
            current_recipe_seen=True
        else:
            carry=root/source['carry_report']
            text=carry.read_text()
            assert data['source_sha256'] in text and manifest['source_sha256'] in text
            if 'carry_report_sha256' in source:
                assert hashlib.sha256(carry.read_bytes()).hexdigest()==source['carry_report_sha256']
            supplemental_files.append(carry)
        selected=source.get('selected_view_names')
        source_views=data['views']
        if selected is not None:
            assert len(selected)==len(set(selected)) and set(selected)<={v['name'] for v in source_views}
            source_views=[v for v in source_views if v['name'] in selected]
        for view in source_views:
            panel=path.parent/view['file']
            raw=panel.read_bytes()
            assert struct.unpack('>IIBB',raw[16:26])==(640,360,16,2)
            assert hashlib.sha256(raw).hexdigest()==view['sha256']
            names.append(view['name'][:2])
            supplemental_files.append(panel)
        supplemental_files.extend((path,recipe,path.parent/'gauge-sheet-cameras.json'))
    if not current_recipe_seen:
        assert proof.get('all_historical') is True and {16,30}<=set(acceptance['accepted_issue_ids'])
        report=root/proof['acceptance_report']
        assert hashlib.sha256(report.read_bytes()).hexdigest()==proof['acceptance_report_sha256']
        assert manifest['source_sha256'] in report.read_text()
        expected_recipe=root/provenance['supplemental_gauge_recipe']
        assert hashlib.sha256(expected_recipe.read_bytes()).hexdigest()==gauge_recipe_hash
        normalized=expected_recipe.read_text().replace(manifest['source_sha256'],'BOUND_SOURCE_SHA')
        for source in proof['panel_manifests']:
            original=root/source['recipe']
            assert original.read_text().replace(source['source_sha256'],'BOUND_SOURCE_SHA')==normalized
        supplemental_files.extend((report,expected_recipe))
    assert len(names)==16 and set(names)=={f'{i:02}' for i in range(1,17)}
    composite=root/proof['composite_path']
    assert hashlib.sha256(composite.read_bytes()).hexdigest()==proof['composite_sha256']
    supplemental_files.extend((proof_path,composite))

tap_manifest=provenance.get('supplemental_steam_tap_manifest')
if tap_manifest:
    path=root/tap_manifest
    data=json.loads(path.read_text())
    verify_supplement_source(data,path,'steam_tap')
    assert data['resolution']==[640,360] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['guiding_training_samples']==64
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==1.0
    recipe=root/provenance['supplemental_steam_tap_recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==provenance['supplemental_steam_tap_recipe_sha256']
    assert len(data['views'])==1 and data['views'][0]['name']=='17_steam_tap_weld'
    view=data['views'][0]
    panel=path.parent/view['file']
    raw=panel.read_bytes()
    assert struct.unpack('>IIBB',raw[16:26])==(640,360,16,2)
    assert hashlib.sha256(raw).hexdigest()==view['sha256']
    supplemental_files.extend((path,recipe,panel))

def verify_corrected_camera_recipe(data):
    record=provenance['supplemental_corrected_cameras']
    recipe=root/record['recipe'];scope=root/record['scope']
    recipe_hash=hashlib.sha256(recipe.read_bytes()).hexdigest()
    assert recipe_hash==record['recipe_sha256']==data['renderer_sha256']
    details=json.loads(scope.read_text())
    assert details['source_sha256']==manifest['source_sha256']
    assert details['canonical_renderer_sha256']==provenance['renderer_source_sha256']
    assert details['recipe_sha256']==recipe_hash and set(details['views'])=={'48','61','62'}
    canonical=Path(__file__).with_name('render_detail_views.py').read_text()
    expected=canonical.replace("INSPECTION_VIEWS = [\n", "INSPECTION_VIEWS = [\n"
        "    ('61_floor_service_oil','Inspection · localized oil film and reflected practical',(-8.9808,-4.6359,1.606),(-8.58,-4.24,.002),35),\n"
        "    ('62_pool_inlet_diffuser_fit','Inspection · over-rim inlet nozzle clearance',(-2.5,-2.0,-2.65),(-1.4,-3.0,-3.12),35),\n",1)
    expected=expected.replace("(0,-4.0,9.05),(0,0,9.70),28)","(0,-4.0,9.05),(0,0,8.95),20)",1)
    expected=expected.replace("choices=[f'{i:02}' for i in range(1, 49)])", "choices=[f'{i:02}' for i in range(1, 49)] + ['61','62'])",1)
    guards=("assert hashlib.sha256(source.read_bytes()).hexdigest() == '"+manifest['source_sha256']+"'\n"
        "assert not args.preview and args.samples == 96 and args.inspection\n"
        "assert args.views and set(args.views) <= {'48','61','62'}\n")
    expected=expected.replace("source = Path(bpy.data.filepath)\n", "source = Path(bpy.data.filepath)\n"+guards,1)
    assert recipe.read_text()==expected, 'Corrected camera recipe changed outside literal cameras and exact guards'
    # The exact camera recipe declares three views; accepted historical targets
    # may be narrowly carried instead of duplicating their unchanged renders.
    assert {v['name'][:2] for v in data['views']} <= {'48','61','62'}
    assert data['views']
    supplemental_files.extend((recipe,scope))

def verify_girder_section_recipe(data):
    record=provenance['supplemental_girder_section']
    recipe=root/record['recipe'];scope=root/record['scope']
    recipe_hash=hashlib.sha256(recipe.read_bytes()).hexdigest()
    assert recipe_hash==record['recipe_sha256']==data['renderer_sha256']
    details=json.loads(scope.read_text())
    assert details['source_sha256']==manifest['source_sha256']
    assert details['canonical_renderer_sha256']==provenance['renderer_source_sha256']
    assert details['recipe_sha256']==recipe_hash and details['views']==['63']
    canonical=Path(__file__).with_name('render_detail_views.py').read_text()
    expected=canonical.replace("INSPECTION_VIEWS = [\n", "INSPECTION_VIEWS = [\n"
        "    ('63_roof_girder_section','Inspection · girder end plate, washers and bolts',(3.0,5.4,16.95),(3.58,5.86,16.95),20),\n",1)
    expected=expected.replace("choices=[f'{i:02}' for i in range(1, 49)])", "choices=[f'{i:02}' for i in range(1, 49)] + ['63'])",1)
    guards=("assert hashlib.sha256(source.read_bytes()).hexdigest() == '"+manifest['source_sha256']+"'\n"
        "assert not args.preview and args.samples == 96 and args.inspection\n"
        "assert args.views == ['63']\n")
    expected=expected.replace("source = Path(bpy.data.filepath)\n", "source = Path(bpy.data.filepath)\n"+guards,1)
    assert recipe.read_text()==expected, 'Girder recipe changed outside literal camera and exact guards'
    assert len(data['views'])==1 and data['views'][0]['name']=='63_roof_girder_section'
    supplemental_files.extend((recipe,scope))

# Preserve the reviewed current-source close-ups and state comparisons alongside
# their own manifests, so the downloaded report has its supporting originals.
for dirname in ('inspection-720p', 'state-orange-720p', 'state-red-720p',
                'state-orange-main-720p', 'state-red-main-720p',
                'state-orange-inspection-720p', 'state-red-inspection-720p',
                'inspection-720p-corrected-cameras', 'inspection-720p-girder-section'):
    evidence_dir=root/'review-evidence'/provenance.get('review_evidence_cycle','c78')/dirname
    evidence_manifest=evidence_dir/'render_manifest.json'
    if not evidence_manifest.exists():
        continue
    data=json.loads(evidence_manifest.read_text())
    assert data['source_sha256']==manifest['source_sha256']
    if dirname=='inspection-720p-corrected-cameras':verify_corrected_camera_recipe(data)
    elif dirname=='inspection-720p-girder-section':verify_girder_section_recipe(data)
    else:assert data['renderer_sha256']==provenance['renderer_source_sha256']
    assert data['resolution']==[1280,720] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and data['path_guiding'] and data['guiding_training_samples']==64
    assert abs(data['adaptive_threshold']-.015)<1e-6
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==(
        .1 if 'red' in dirname else .5 if 'orange' in dirname else 1.)
    if data.get('assembled_from'):
        original_views={}
        metadata={k:v for k,v in data.items() if k not in {'views','assembled_from','assembly_scope'}}
        for entry in data['assembled_from']:
            raw_manifest=root/entry['manifest']
            assert hashlib.sha256(raw_manifest.read_bytes()).hexdigest()==entry['manifest_sha256']
            original=json.loads(raw_manifest.read_text())
            assert {k:v for k,v in original.items() if k!='views'}==metadata
            for view in original['views']:
                assert view['name'] not in original_views
                original_views[view['name']]=view
                panel=raw_manifest.parent/view['file']
                raw=panel.read_bytes()
                assert hashlib.sha256(raw).hexdigest()==view['sha256']
                assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
                supplemental_files.append(panel)
            supplemental_files.append(raw_manifest)
        assert original_views=={view['name']:view for view in data['views']}
    for view in data['views']:
        panel=evidence_dir/view['file']
        raw=panel.read_bytes()
        assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
        assert hashlib.sha256(raw).hexdigest()==view['sha256']
        supplemental_files.append(panel)
    supplemental_files.append(evidence_manifest)

if provenance.get('candidate'):
    cycle=root/'review-evidence'/provenance['review_evidence_cycle']
    for state in ('orange','red'):
        paths=[cycle/('state-'+state+suffix)/'render_manifest.json'
               for suffix in ('-720p','-main-720p')]
        completed=[path for path in paths if path.is_file()]
        assert len(completed)==1, 'One current main comparison manifest required for '+state
        comparison=json.loads(completed[0].read_text())
        assert {'04','05','06'}<={view['name'][:2] for view in comparison['views']}, 'Floor/upper rods/pool comparison incomplete for '+state

p10_manifest=provenance.get('supplemental_p10_manifest')
if p10_manifest:
    path=root/p10_manifest
    data=json.loads(path.read_text())
    assert data['source_sha256']==manifest['source_sha256']
    assert data['resolution']==[640,360] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    recipe=root/provenance['supplemental_p10_recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==provenance['supplemental_p10_recipe_sha256']
    assert len(data['views'])==1 and data['views'][0]['name']=='18_secondary_p10_casing'
    view=data['views'][0]
    panel=path.parent/view['file']
    raw=panel.read_bytes()
    assert struct.unpack('>IIBB',raw[16:26])==(640,360,16,2)
    assert hashlib.sha256(raw).hexdigest()==view['sha256']
    supplemental_files.extend((path,recipe,panel))

geometry=provenance.get('supplemental_geometry')
if geometry:
    path=root/geometry['manifest']
    data=json.loads(path.read_text())
    verify_supplement_source(data,path,'native_geometry')
    assert data['resolution']==[640,360] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['guiding_training_samples']==64
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==1.0
    recipe=root/geometry['recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==geometry['recipe_sha256']
    cameras={
        '34_floor_annulus': ([-4.6,-5.7,1.2],[-2.4,-3.8,-.15],28),
        '43_stool': ([8.2,4.2,1.15],[7,3.07,.32],40),
    }
    assert len(data['views'])==2 and {v['name'] for v in data['views']}==set(cameras)
    for view in data['views']:
        assert (view['location'],view['target'],view['lens_mm'])==cameras[view['name']]
        panel=path.parent/view['file']
        raw=panel.read_bytes()
        assert struct.unpack('>IIBB',raw[16:26])==(640,360,16,2)
        assert hashlib.sha256(raw).hexdigest()==view['sha256']
        supplemental_files.append(panel)
    scope=root/geometry['scope']
    scope_data=json.loads(scope.read_text())
    assert scope_data['source_sha256']==data['source_sha256']
    assert scope_data['base_recipe_sha256']==provenance['renderer_source_sha256']
    assert scope_data['recipe_sha256']==data['renderer_sha256']
    supplemental_files.extend((path,recipe,scope))

crane=provenance.get('supplemental_crane_identity')
if crane:
    path=root/crane['manifest']
    data=json.loads(path.read_text())
    assert data['source_sha256']==manifest['source_sha256']
    assert data['resolution']==[1280,720] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['guiding_training_samples']==64
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==1.0
    recipe=root/crane['recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==crane['recipe_sha256']
    assert len(data['views'])==1 and data['views'][0]['name']=='50_crane_identity_mount'
    view=data['views'][0]
    assert (view['location'],view['target'],view['lens_mm'])==([-4.2,1.4,15.35],[-4.2,4.195,15.04],30)
    panel=path.parent/view['file']
    raw=panel.read_bytes()
    assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
    assert hashlib.sha256(raw).hexdigest()==view['sha256']
    scope=root/crane['scope']
    scope_data=json.loads(scope.read_text())
    assert scope_data['source_sha256']==manifest['source_sha256']
    assert scope_data['base_recipe_sha256']==provenance['renderer_source_sha256']
    assert scope_data['recipe_sha256']==data['renderer_sha256']
    supplemental_files.extend((path,recipe,panel,scope))

door_detail=provenance.get('supplemental_door_detail')
if door_detail:
    path=root/door_detail['manifest']
    data=json.loads(path.read_text())
    verify_supplement_source(data,path,'door_detail')
    assert data['resolution']==[1280,720] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['guiding_training_samples']==64
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==1.0
    recipe=root/door_detail['recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==door_detail['recipe_sha256']
    assert len(data['views'])==1 and data['views'][0]['name']=='57_fuel_leaf_hardware_detail'
    view=data['views'][0]
    assert (view['location'],view['target'],view['lens_mm'])==([1.2,11.6,1.85],[1.2,14.3,1.85],28)
    panel=path.parent/view['file']
    raw=panel.read_bytes()
    assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
    assert hashlib.sha256(raw).hexdigest()==view['sha256']
    scope=root/door_detail['scope']
    scope_data=json.loads(scope.read_text())
    assert scope_data['source_sha256']==data['source_sha256']
    assert scope_data['base_recipe_sha256']==provenance['renderer_source_sha256']
    assert scope_data['recipe_sha256']==data['renderer_sha256']
    supplemental_files.extend((path,recipe,panel,scope))

    projection=root/door_detail['projection']
    projection_data=json.loads(projection.read_text())
    assert projection_data['source_sha256']==data['source_sha256'] and projection_data['pass_check']
    assert len(projection_data['parts'])==4 and all(p['inside_with_5_percent_margin'] for p in projection_data['parts'])
    supplemental_files.append(projection)

mechanical=provenance.get('supplemental_mechanical_proofs')
if mechanical:
    cameras={
        '51_column_splice_lower': ([3.1,8.6,6.6],[3.1,10.43,6.6],50),
        '52_trolley_raised': ([-8,3,16.6],[-6.5,4.6,15.7],35),
        '53_column_splice_upper': ([3.1,8.6,9.3],[3.1,10.43,9.3],50),
    }
    sources=mechanical.get('sources',[mechanical])
    names=[];current_seen=False;bounded_historical_seen=False
    for source in sources:
        path=root/source['manifest']
        data=json.loads(path.read_text())
        if 'manifest_sha256' in source:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==source['manifest_sha256']
        if data['source_sha256']==manifest['source_sha256']:
            current_seen=True
        elif provenance.get('historical_supplement_carry'):
            assert verify_supplement_source(data,path,'mechanical')
            bounded_historical_seen=True
        else:
            # Only the explicitly approved unchanged lower splice may carry.
            assert {v['name'] for v in data['views']}=={'51_column_splice_lower'}
            assert data['source_sha256']==source['source_sha256']
            carry=root/source['carry_report'];text=carry.read_text()
            assert data['source_sha256'] in text and manifest['source_sha256'] in text
            assert hashlib.sha256(carry.read_bytes()).hexdigest()==source['carry_report_sha256']
            supplemental_files.append(carry)
        assert data['resolution']==[1280,720] and data['samples_max']==96 and not data['preview']
        assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
        assert data['path_guiding'] and data['guiding_training_samples']==64
        assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
        assert data['frame']==1 and data['stability']==1.0
        recipe=root/source['recipe']
        assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==source['recipe_sha256']
        for view in data['views']:
            assert view['name'] in cameras
            assert (view['location'],view['target'],view['lens_mm'])==cameras[view['name']]
            panel=path.parent/view['file'];raw=panel.read_bytes()
            assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
            assert hashlib.sha256(raw).hexdigest()==view['sha256']
            names.append(view['name']);supplemental_files.append(panel)
        scope=root/source['scope'];scope_data=json.loads(scope.read_text())
        assert scope_data['source_sha256']==data['source_sha256']
        assert scope_data['base_recipe_sha256']==provenance['renderer_source_sha256']
        assert scope_data['recipe_sha256']==data['renderer_sha256']
        supplemental_files.extend((path,recipe,scope))
    assert (current_seen or bounded_historical_seen) and len(names)==3 and set(names)==set(cameras)

doors=provenance.get('supplemental_door_hardware')
if doors:
    path=root/doors['manifest']
    data=json.loads(path.read_text())
    verify_supplement_source(data,path,'door_hardware')
    assert data['resolution']==[640,360] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['guiding_training_samples']==64
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==1.0
    recipe=root/doors['recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==doors['recipe_sha256']
    cameras={
        '54_fuel_door_hardware': ([0,8.25,2.5],[0,14.36,2.5],24),
        '55_access_door_hardware': ([-7.75,0,2.75],[-14.36,0,2.75],22),
        '56_cooling_door_hardware': ([7.7,-7.7,2.5],[10.917,-10.917,2.5],18),
    }
    assert len(data['views'])==3 and {v['name'] for v in data['views']}==set(cameras)
    for view in data['views']:
        assert (view['location'],view['target'],view['lens_mm'])==cameras[view['name']]
        panel=path.parent/view['file']
        raw=panel.read_bytes()
        assert struct.unpack('>IIBB',raw[16:26])==(640,360,16,2)
        assert hashlib.sha256(raw).hexdigest()==view['sha256']
        supplemental_files.append(panel)
    scope=root/doors['scope']
    scope_data=json.loads(scope.read_text())
    assert scope_data['source_sha256']==data['source_sha256']
    assert scope_data['base_recipe_sha256']==provenance['renderer_source_sha256']
    assert scope_data['recipe_sha256']==data['renderer_sha256']
    supplemental_files.extend((path,recipe,scope))

valves=provenance.get('supplemental_valves')
if valves:
    path=root/valves['manifest']
    data=json.loads(path.read_text())
    assert data['source_sha256']==manifest['source_sha256']
    assert data['resolution']==[1280,720] and data['samples_max']==96 and not data['preview']
    assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
    assert data['path_guiding'] and data['guiding_training_samples']==64
    assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
    assert data['frame']==1 and data['stability']==1.0
    recipe=root/valves['recipe']
    assert hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']==valves['recipe_sha256']
    assert len(data['views'])==1 and data['views'][0]['name']=='49_valve_ids_and_cast_bodies'
    view=data['views'][0]
    assert (view['location'],view['target'],view['lens_mm'])==([-.55,-6.6,1.65],[-.55,-9.35,1.05],35)
    panel=path.parent/view['file']
    raw=panel.read_bytes()
    assert struct.unpack('>IIBB',raw[16:26])==(1280,720,16,2)
    assert hashlib.sha256(raw).hexdigest()==view['sha256']
    scope=root/valves['scope']
    scope_data=json.loads(scope.read_text())
    assert scope_data['source_sha256']==manifest['source_sha256']
    assert scope_data['base_recipe_sha256']==provenance['renderer_source_sha256']
    assert scope_data['recipe_sha256']==data['renderer_sha256']
    preflight=root/valves['preflight']
    preflight_data=json.loads(preflight.read_text())
    assert preflight_data['source_sha256']==manifest['source_sha256']
    assert preflight_data['recipe_sha256']==data['renderer_sha256'] and preflight_data['pass_check']
    assert {v['name'] for v in preflight_data['glyph_samples']}=={'RH refine V-01','RH refine V-02'}
    for glyph in preflight_data['glyph_samples']:
        assert glyph['inside_frame']==glyph['front_triangle_centroid_samples'] and not glyph['occluders']
    supplemental_files.extend((path,recipe,panel,scope,preflight))

historical_index=provenance.get('historical_carry_image_index')
if historical_index:
    index_path=root/historical_index
    historical=json.loads(index_path.read_text())
    assert historical['current_source_sha256']==manifest['source_sha256']
    assert set(historical['carry_issue_ids']) <= set(acceptance['accepted_issue_ids'])
    for bundle in historical['bundles']:
        path=root/bundle['manifest']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==bundle['manifest_sha256']
        data=json.loads(path.read_text())
        assert data['source_sha256']==bundle['source_sha256']
        assert data['engine']=='CYCLES' and not data['preview'] and data['samples_max']==96
        assert data['adaptive_min_samples']==32 and abs(data['adaptive_threshold']-.015)<1e-6
        assert data['path_guiding'] and data['guiding_training_samples']==64
        assert data['denoiser']=='OPENIMAGEDENOISE' and data['max_bounces']==12
        assert data['frame']==1 and data['stability'] in {1.0,.5,.1}
        records={v['name']:v for v in data['views']}
        for image in bundle['images']:
            panel=root/image['path']
            raw=panel.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==image['sha256']==records[image['name']]['sha256']
            width,height,depth,color=struct.unpack('>IIBB',raw[16:26])
            assert [width,height]==data['resolution'] and depth==16 and color==2
            supplemental_files.append(panel)
        supplemental_files.append(path)
        for recipe in path.parent.glob('*.py'):
            if hashlib.sha256(recipe.read_bytes()).hexdigest()==data['renderer_sha256']:
                supplemental_files.append(recipe)

# Preserve exact immutable manifest witnesses cited by the independent current review.
if provenance.get('candidate'):
    sync=json.loads((root/'validation/c89-disposition-sync.json').read_text())
    assert sync['source_sha256']==manifest['source_sha256'] and sync['accepted']==140 and sync['pending']==0
    assert sync['independent_json_sha256']==hashlib.sha256(independent_path.read_bytes()).hexdigest()
    for binding in sync.get('scoped_independent_evidence',[]):
        assert hashlib.sha256((root/binding['preserved']).read_bytes()).hexdigest()==binding['sha256']
    for binding in sync.get('reviewed_manifests',[]):
        witness=root/binding['preserved']
        assert hashlib.sha256(witness.read_bytes()).hexdigest()==binding['sha256']
        original=json.loads(witness.read_text())
        assert original['source_sha256']==manifest['source_sha256']
        assert not original['preview'] and original['samples_max']==96
        assert original['adaptive_min_samples']==32 and abs(original['adaptive_threshold']-.015)<1e-6
        assert original['path_guiding'] and original['guiding_training_samples']==64
        assert original['denoiser']=='OPENIMAGEDENOISE' and original['max_bounces']==12
        # PNGs retain their actual original manifests elsewhere in this archive.
        for view in original['views']:
            assert any(hashlib.sha256(panel.read_bytes()).hexdigest()==view['sha256']
                       for panel in supplemental_files if panel.suffix=='.png'),view['name']

main_recipe=Path(__file__).with_name('render_detail_views.py')
assert hashlib.sha256(main_recipe.read_bytes()).hexdigest()==manifest['renderer_sha256']
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
    for view in manifest['views']:
        z.write(root/view['file'],view['file'])
    for name in ['render_manifest.json','image_checks.json','provenance.json','contact-sheet.jpg']:
        z.write(root/name,name)
    z.write(main_recipe,'render_detail_views.py')
    if provenance.get('candidate'):
        z.write(root/'reactor_hall_refined.blend','reactor_hall_refined.blend')
    if (root/'README.md').is_file():
        z.write(root/'README.md','README.md')
    for path in sorted((root/'validation').rglob('*')):
        if path.is_file() and path.suffix in ('.log','.json','.md','.py','.out'):
            z.write(path,str(path.relative_to(root)))
    for path in sorted(set(supplemental_files)):
        if not str(path.relative_to(root)).startswith("validation/"):
            z.write(path,str(path.relative_to(root)))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'status':'PASS','images':len(checks),'archive':str(archive),'archive_bytes':archive.stat().st_size,
                  'render_seconds':round(sum(v['elapsed_seconds'] for v in manifest['views']),2)}))
