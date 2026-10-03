# Independent technical audit — R22

**Artifact inspected:** `production/checkpoints/R22.blend`.\
**Revision:** R22; checkpoint, build, and validation source hash `9ffd4ca114f5d1c3d597a38539d3405449487b9efcd4e4149fb0b756647e1bd9`.\
**Formal validation:** PASS; 29 protected interfaces unchanged, world strength 0, 21 light checks, no reported issues. This is a read-only geometry, material-use, and fixture review; it is not a visual score or runtime certification.

## Finger roots now join the palms

I tested each evaluated glove-finger mesh against its matching palm with an exact Boolean intersection. All eight pairs produce closed intersection meshes with positive volume:

| Finger | Palm | Intersection volume |
| --- | --- | ---: |
| `Glove finger` | Work glove palm | 3.917×10⁻⁶ m³ |
| `Glove finger.001` | Work glove palm | 4.313×10⁻⁶ m³ |
| `Glove finger.002` | Work glove palm | 3.507×10⁻⁶ m³ |
| `Glove finger.003` | Work glove palm | 1.142×10⁻⁶ m³ |
| `Glove finger.004` | Work glove palm.001 | 3.992×10⁻⁶ m³ |
| `Glove finger.005` | Work glove palm.001 | 4.192×10⁻⁶ m³ |
| `Glove finger.006` | Work glove palm.001 | 3.848×10⁻⁶ m³ |
| `Glove finger.007` | Work glove palm.001 | 5.322×10⁻⁷ m³ |

The minimum vertex-to-surface distances range from 0.259 to 1.000 mm; the positive Boolean volumes confirm actual joins despite those surface clearances. This closes the R19 outer-finger gaps.

## Printed diagram marks are seated

The paper's evaluated front face is planar at `y=−6.30912 m` and faces +Y. The replacement ring (48 faces) and three line marks (one face each) also face +Y. All 108 evaluated mark vertices ray-hit that face and sit at `y=−6.30910 m`, a measured 20.027 µm offset. The marks are now thin surface geometry rather than rods/ring sections floating millimeters above or partly embedded in the sheet.

## Residue materials stay on indoor surfaces

The R22 residue material copies are assigned to the interior north acoustic bays and six side flush panels. The edited shared floor materials also remain confined indoors: `RF18_indoor_worn_concrete` is used by `Floor` and the repaired screed; `RF1_epoxy` by the process and fabrication fields; and the four `RF1_screed_*` materials by the 24 worked floor panels. `RF1_concrete` remains assigned only to the two exterior sills. No changed floor or copied wall residue material has an exterior-sill user.

## Fixture and composition constraints

Compared R15 with R22: all 11 camera and 21 light world matrices match at `1e−9` tolerance. R22 retains 21 existing light objects, each paired with its physical lens; the six failed fixtures have both zero source energy and zero lens emission. The 15 working sources remain attached to their paired fixture lenses, with emission strength 0.30. World strength remains zero. R22 changes energies on existing task, threshold, service, and bulkhead fixtures; I found no external source or fill light.

## Limits

The Boolean results establish local glove-root joins, not exhaustive intersections elsewhere in the scene. Mark sampling verifies face alignment and offset, not rendered legibility. The residue review checks material assignments and shared users, not the final rendered appearance. This review makes no runtime or exhaustive-collision claim; the cold rebuild and full render batch were still running at audit time.
