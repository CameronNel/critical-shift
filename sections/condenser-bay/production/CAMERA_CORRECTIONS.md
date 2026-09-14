# R24 camera and gallery correction evidence

The R21–R23 camera matrices and images remain in their immutable checkpoints and review packs. No old image is relabelled. All C01–C10 / W01–W08 IDs remain required in future full packs.

R22 W04_NE points from eye height 1.62 m to floor height 0.18 m and shows almost exclusively floor. R22 W06_WEST_AISLE points north into the shift-log wall rather than along the named west aisle. Luna independently flagged W06 coverage. Their positions and lenses remain unchanged in R24; their targets turn toward the actual named route.

R23 saved geometry probe (`blender/astra_gallery_probe.py`) measured gallery floor top 4.205 m and slab underside 6.0 m: only 1.795 m headroom. Five suspension posts occupy gallery centerlines, visible obstructing W08. The solid east-deck extension overlaps the second stair flight; north decking is offset 0.225 m from its connection. These are physical defects, not camera-composition preferences.

R24 repairs this named subsystem while preserving the room frame, condenser, U04 coordinates, and U-shaped gallery arrangement. Deck elevation becomes 3.90 m, the second stair rise follows it, support rods move to deck edges with actual shoes, and the lifting beam remains over the eastern extraction apron clear of the gallery. Open bearing bars replace solid pseudo-grating. Deck/rail endpoints meet their real landings.

C04, C08, C09 and W08 retain their evidence roles and lenses, with eye height 5.45 m (approximately 1.51 m above the repaired walking surface). Previously their heights were only 0.75–1.08 m above the deck, despite standing-view labels. C04 and C09 now inspect the physically exposed flange assembly; a separately labelled section cutaway is still required to show the interior rectangular throat. No room wall is disabled in the 18-camera set. Acceptance must be based on new full warm/cold pixels and measured geometry, not this rationale.

R25 additionally moves the west gallery strip 0.40 m outboard to clear the waterbox at the lower deck level, stows the cover davits over their own housings, and routes the ejector suction above the standing volume. R24's expanded audit deliberately failed on these remaining obstructions. R24 is a diagnostic revision, not an acceptance candidate; its source files were edited during construction, so the late-collected source hash is not accepted as replay proof. R25 freezes its source checkpoint before importing any authoring modules.

The current review runner records exact positions/lenses and saved blend hash per pack. Source checkpoints retain the target coordinates as well.

R27 also repairs the demonstrated second-flight collision: saved R26 transverse body rays hit the original column at (5.55, 2.15), and the tread's inner side intersected the east waterbox. The flight shifts 0.275 m outward to centre x 5.90, retaining its direction and run; the intermediate landing extends to meet it. This one local column now bears under the existing south roof girder at (6.65, 1.25), outside the stair and tested ground routes. Both stair rail transitions are physically connected. No neighboring room was changed.

R27 extended saved audit passes stair, gallery and straight cart volumes. C08 aims down toward its maintenance deck because R25 still failed to show that surface; W04's aim is corrected to a level room view. These are documented corrections to invalid evidence, accompanying substantive geometry repairs. They do not substitute for full independent warm/cold review.
