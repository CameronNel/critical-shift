# Independent technical audit — R24 material and power changes

**Artifact inspected:** `production/checkpoints/R24.blend`.\
**Revision:** R24; checkpoint, build, and validation source hash `37896096ba619770afdf2d3dfc4443b2223aadcc71a468b809a833803eb8701b`.\
**Formal validation:** PASS; 29 protected interfaces unchanged, world strength 0, 21 light checks, no reported issues. This is a read-only geometry-identity, material-scope, and fixture review; it does not certify final render acceptance or runtime behavior.

## Exact geometry and pose comparison with R23

I fingerprinted every object in R23 and R24. The two files contain the same **3,043 objects**, including **2,578 mesh objects**, with no changed, added, or missing object names or types. All mesh raw-local and evaluated vertex/topology hashes are identical. Every object world matrix is identical. The only changed mesh data-block names and material slots are the 14 nook glove pieces: two palms, two cuffs, two thumbs, and eight fingers. Thus the glove material change does not disturb R22's measured finger/palm contacts or R22's paper and ink geometry.

The R20 floor evidence is also preserved exactly: R24's mesh geometry matches R23, and the prior independent R20 check measured all 833 samples across the 27 crack-film pieces at 19.99–20.01 µm above the local evaluated floor union, with all 49 faces pointing upward. R22's independent audit established closed positive-volume joins for all eight glove fingers and +Y-facing pump marks 20.027 µm off the paper face; those object geometries are unchanged through R23 and R24.

## PPE finish isolation

`RF24_abandoned_glove_leather` is assigned to exactly those 14 nook glove parts and has no other object users. The original `RF1_leather` remains on dryer gloves, rags, bristles, apron, cushion, and other cloth/leather objects; it is not recolored by the abandoned-glove finish. `RF1_work_glove_pale_leather` remains on the Assembly work-glove meshes. This isolates the new finish from those existing cloth users.

## Worn paint coverage is preserved

Compared both `RF17_worn_traffic_RF1_ivory` and `RF17_worn_traffic_RF1_ochre` between R23 and R24. Each retains the same 11-node graph, all links, ramp positions/colors, transparent/mix coverage, and assigned objects. The only node difference is the existing Multiply MixRGB color: `(0.62, 0.65, 0.58)` becomes `(0.87, 0.89, 0.79)` in both materials. The three already-removed border fragments (`.003`, `.009`, `.014`) are absent in both checkpoints, and all surviving paint object geometry is unchanged. The revision restores contrast to surviving pigment without replacing the missing-chip coverage pattern.

## Fixture state and energy changes

R24 keeps 21 lights, each bound to a unique existing physical lens, with all source/lens world transforms identical to R23. World strength remains 0. Six failed pairs retain both source energy and lens emission at zero: PV hood 1, ceiling pendants 3 and 5, and wall service lamps 0, 1, and 2. The other 15 source/lens pairs remain active at lens emission strength 0.30. No new light or emissive surface was added.

Four existing working sources change power: ceiling pendant 4 `34→50 W`, wall service lamp 3 `13→20 W`, inspection practical `22→26 W`, and nook lamp `17→20 W`. Camera and light poses match R23 exactly across all 32 objects. The formal protected-interface check reports all 29 unchanged.

## Limits

The mesh comparison establishes geometry and pose identity against R23; it does not test shader appearance, exhaustive intersections, or user-perceived legibility. The cold original-source rebuild was still running, and final render proof remained pending at audit time.
