# C88 saved girder crossing: independent geometry review

**Candidate:** `/workspace/scratch/reactor-refinement-cycle88/hall_final.blend`  
**Source SHA-256:** `85766edcb5cf1ba1d5fa9bc624a956132885298e9c379aad3867a1fca0560cf6`  
**Source module:** `/workspace/scratch/reactor-refinement-cycle88/owned-stage/rh_walls.py` (girder generation at lines 451–524; read-only inspection)  
**Saved-mesh probe:** `/workspace/scratch/c88-girder-web-face-probe.json`  
**Probe SHA-256:** `ac2a5c164e3661def0183cae5deec9b3fd767ed041845796e282cb06fb97d15b`

## Finding

The four full-span longitudinal I-girders and the transverse I-girders overlap physically at their grid crossings. At the measured crossing near `(x=3.6, y=6.0)`, the longitudinal web occupies `x≈3.5825–3.6175`, `z=16.67–17.23`; the transverse web occupies `y≈5.9825–6.0175`, `z=16.82–17.38`. Their shared web volume is approximately `0.00050225 m³`. The transverse web also spans the longitudinal top-flange elevation (`z=17.23–17.30`). The source generates both beams continuously through the crossing and contains no local cope, terminating end plate, or separate crossing connection at that location.

This is a measured local geometry intersection, not a whole-scene collision assertion. The roof girders otherwise have modeled end plates and beam seats at their perimeter supports. The current C88 section63 camera projects this crossing inside the frame, so the requested construction/readability review can inspect the same location directly.

## Disposition

Keep **#111 girder connection construction** open. The geometry does not establish a physically clear, explicit connection at the interior crossings; the full C88 image is still needed to judge how strongly this reads as a visual defect. Do not accept #111 from the neutral-gray material change or from the existence of end plates at unrelated perimeter supports. A credible correction would make one member continuous and terminate the intersecting member at its web with a real end-plate/stiffener/fastener load path, or model a clear coped crossing with an explicit connection.
