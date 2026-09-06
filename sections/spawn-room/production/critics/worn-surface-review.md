# Maintained wear revision — 2026-09-06

User direction: old, dirty, mildly damaged but maintained; tactile stylized concrete rather than plastic; imperfect edges without destruction. This revision explicitly authorizes free CC0 scan inputs. Reference plates 09, 10 and 27 were reinspected. Cameras and circulation requirements remain fixed.

## Slice correction trail

- **worn-slice-01:** rejected. The first wall relief was too coarse, the small plaster patch read as an applied flat mark, and equipment/PPE lacked localized use. Texture loading also created redundant packed copies. Corrected by lowering relief, cutting an actual shallow recess, adding restrained paint loss and lower-surface dirt, and reusing six named image datablocks.
- **worn-slice-02:** rejected. All 21 contacts passed and six unique textures were packed, but the garment dirt mask had an abrupt horizontal boundary and exposed substrate was too smooth. Changed the mask to a smooth falloff and gave the substrate mineral relief. All three images were inspected.
- **worn-slice-03:** all three fixed views inspected. Rough plaster, softer green dado, concrete variation, recessed joints, small corner losses and dry kickplate chips are visible. Garment staining now fades rather than forming a seam. The repair has a visible recessed edge and textured substrate. The wearable fabric remains simplified at gameplay distance. Contact audit: 21 checked, zero failures. Six unique packed maps. This is builder review, not user acceptance.

## Construction and provenance

Original CC0 JPGs are unchanged. Palette remapping, variable roughness and bump happen in Blender shaders. Real mesh changes are separate: 2 mm recessed floor joints, occasional clipped tile corners, less than 1 mm tile-top variation, up to 1.4 mm plaster waviness, localized 9 mm plaster loss, selected small edge compression and dry paint-loss polygons bonded to exact supports. No collision or route tolerances were relaxed.

## Full-room correction trail

- **worn-room-01:** rejected by the contact audit before visual acceptance. Four dry paint-loss overlays had been selected on curved vinyl chair cushions; their mounting angles failed the unchanged 12-degree tolerance. Removed that inappropriate paint treatment from cushions, which retain material-specific vinyl wear. All 29 objective checks passed. The render job was cancelled after retaining the failure reports.
- **worn-room-02:** 83 contacts and 29 objective checks passed, but the first hallway render exposed horizontal texture stretching on rotated walls. The built-in BOX projection selected axes from local normals while coordinates were world-space. Replaced it with explicit world-normal triplanar weighting and three planar projections. Retained the rejected Spawn render and cancelled the remaining renders before acceptance.

The corrected full-room review and saved-source verification are recorded below after rendering.

### worn-room-03 visual inspection

- Spawn and HallForward: world-space mapping removes the horizontal stretch. Plaster relief and smoother painted dado separate clearly; the exit door, meter and lettering remain legible. Rare recessed repairs are visible without turning the hallway into ruins.
- LockerDoor and LockerReverse: matte mineral floor, subtly dirty equipment paint and dark rubber remain distinct. The chamber glass is imperfect but still readable. No new overlap, floor trip edge or texture stretch is visible in these two views.
- BriefingDoor: seating has mottled used vinyl rather than detached paint chips; table/clipboard/mug retain their material identities. The granular floor and plaster remain subordinate to the briefing screen.
- Material_A: trowelled upper plaster, less pronounced painted dado, soft fabric texture and matte boots are distinguishable at close range. There is no abrupt garment dirt boundary or repeated band from a rotated wall projection. Painted bay surfaces retain broad maintenance streaks rather than concrete texture.
- ExitReverse: the opposite hallway direction keeps the same texture scale; portraits, hinges, doorways and signs remain clear. Floor joints are dark and recessed rather than bright raised strips.
- Walk_A/B/C: surfaces retain their scale across the route; the quiet rear wall remains quiet. The chipped tile corner visible in the briefing reverse is localized and does not create a raised edge. Door and chair clearances remain visually intact.
- Hero_A: the chamber's paint, glazing, gasket and controls read as separate materials. The word READY remains readable; the rough wall and small recessed repair do not compete with the control face.

All eleven fixed room views were inspected. No visual veto was identified for this maintained-wear revision. This is the builder's assessment, not user approval or a claim of perfection.

Both sources were regenerated in `worn-slice-final-source/` and `worn-room-final-source/` with the final world-normal mapping and the original 170mm structural floor slab retained beneath the recessed grout (no redundant full render pass for the hidden underside). The small source's 21 support contacts pass. Its three prior front-facing review views remain in `worn-slice-03/`; the full-room rotated-wall views above provide the additional mapping regression coverage. Cold-start comparisons below verify the saved final room against the reviewed surface appearance.

### Saved-source details

The fresh-open DETAIL_BriefingHuman and DETAIL_LockerWork renders were inspected. The institution's portraits and instructions remain legible, chairs retain their vinyl/metal distinction, the bench retains directional laminate grain, and the nearby clipped tile corner exposes the recessed mortar. The larger plaster loss has a textured substrate and an inset edge. Neither detail view introduced a new visual veto.

Fresh-open dependency audit: all six packed JPG SHA256 values match the verified CC0 downloads; all ten saved VIEW_3D spaces use SOLID startup. The 83 contact and 29 objective checks pass. The three initial fixed-camera comparisons have nonzero but very small mean 8-bit differences (0.0085–0.0163) after the final structural-slab rebuild; they are visually consistent, not claimed pixel-identical. Full-camera comparison is completed below.

## Final verification and recovery

All eleven cold-start camera views were compared and visually inspected. No material regression was identified. Maximum per-image mean 8-bit difference from worn-room-03 is 0.0773053; complete values are in ../worn_cold_start_comparison.json. Two detail views also pass builder review.

The final disk hash check caught a resave of the older room-06 scene (1280 objects and only two portrait images) over spawnroom.blend at 16:05. Its exact bytes were preserved in ignored logs before rebuilding with the unchanged source. The rebuilt canonical file was copied to spawnroom_worn.blend, which was opened in another fresh process. All 83 contacts, 29 objective checks, six packed-texture hashes and ten SOLID startup spaces passed again. A new Spawn render was visually inspected and compared against the previous cold render: maximum difference one 8-bit channel value, mean 0.0000478395. These files are byte-identical copies of the recovered delivery. Render/source hash provenance is retained in ../renders/final/render_provenance.json; the earlier full-cold source hash is not rewritten to pretend it belongs to the recovered file.

Final builder verdict: PASS for the maintained-wear art revision. Eleven fixed views and two detail views are in ../renders/final/. Five old state pictures remain in the historical pre-wear review directory; all six states were rechecked objectively on the new scene. The previous low-wear delivery and all rejected new iterations remain available in the review trail.
