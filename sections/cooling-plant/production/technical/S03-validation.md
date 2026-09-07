# Cooling Plant S03: objective validation

Status: **FAIL**. Scope: **slice**. 5 failures; 0 review items.

This report does not assign a visual score or certify final production acceptance.

Measured 638 evaluated geometry objects from a fresh headless reopen. No render or geometry changes were performed.

Failure categories: clearance: 1, envelope: 1, support: 3

Full measured evidence is in the accompanying JSON. Highest-priority failures:

- geometry_intersects_keep_clear: {"volume": "KC-BENCH", "object": "D02 recessed door leaf", "evaluated_bounds": {"min": [-4.7749996, 10.1999998, 0.01], "max": [-4.7049999, 11.4199991, 2.1900001]}, "aabb_overlap_extent_m": [0.06999969482421875, 0.01999950408935547, 2.180000066757202], "method": "evaluated_triangle_clipped_to_open_volume", "witness_m": [-4.7098455, 11.4165678, 0.0114312]}
- equipment_exceeds_declared_envelope: {"equipment": "CP-WORKBENCH", "object": "maintenance workbench", "excess_xyz_m": [0.0, 0.010000228881835938, 0.0], "actual_bounds": {"min": [-5.0500002, 12.3000002, 0.0], "max": [-2.25, 13.0100002, 1.11]}, "contract_bounds": {"min": [-5.05, 12.3, 0], "max": [-2.25, 13, 1.24]}}
- support_penetration_exceeds_tolerance: {"object": "D02 swinging leaf", "target": "D02 metal jamb", "anchor_index": 0, "anchor_m": [-4.75, 10.1800003, 0.26], "actual_prop_member": "D02 hinge pin", "actual_support_member": "D02 metal jamb", "actual_prop_contact_m": [-4.7646437, 10.1800003, 0.26], "actual_support_contact_m": [-4.6999998, 10.1800003, 0.26], "signed_gap_m": -0.06464385986328125, "support_angle_degrees": 0.0, "max_gap_m": 0.005, "max_penetration_m": 0.002, "angle_tolerance_degrees": 12.0}
- support_penetration_exceeds_tolerance: {"object": "D02 swinging leaf", "target": "D02 metal jamb", "anchor_index": 1, "anchor_m": [-4.75, 10.1800003, 1.8], "actual_prop_member": "D02 hinge pin.001", "actual_support_member": "D02 metal jamb", "actual_prop_contact_m": [-4.7646437, 10.1800003, 1.8], "actual_support_contact_m": [-4.6999998, 10.1800003, 1.8], "signed_gap_m": -0.06464385986328125, "support_angle_degrees": 0.0, "max_gap_m": 0.005, "max_penetration_m": 0.002, "angle_tolerance_degrees": 12.0}
- floating_support_contact: {"object": "removed seal on rag", "target": "folded wiping rag", "anchor_index": 0, "anchor_m": [-4.0900002, 12.7299995, 0.95], "actual_prop_member": "removed blackened seal ring", "actual_support_member": "folded wiping rag", "actual_prop_contact_m": [-4.0900002, 12.7299995, 0.959], "actual_support_contact_m": [-4.0900002, 12.7299995, 0.9389999], "signed_gap_m": 0.020000100135803223, "support_angle_degrees": 0.0, "max_gap_m": 0.005, "max_penetration_m": 0.002, "angle_tolerance_degrees": 12.0}

Final completion remains dependent on four full review cycles, independent scores of at least 90 in every required category, ten fixed-camera final renders, and a fresh-process render comparison.
