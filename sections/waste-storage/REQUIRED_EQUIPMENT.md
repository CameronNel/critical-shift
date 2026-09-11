# Required equipment and operational coverage

The assignment requires receiving, segregated waste storage, casks/containers, handling, controlled access, monitoring, ventilation, maintenance and safe circulation. Counts and detailed arrangements below are authored design choices, not nuclear engineering ratings.

| Physical assembly | Count | Operational purpose / supplied detail |
|---|---:|---|
| RA01–RA03 residue overpacks | 3 | Sealed vessel, skid, collar, captive clamps, lifting eyes/trunnions, seal instrument, sampling cap, serial label |
| SC01–SC02 shielded casks | 2 | Tall sealed vessel, impact shoes, supported trunnions, bolted removable lid, lift hardware, inspection/seal controls |
| DR01–DR02 dry containers | 2 | Fork pockets, pan, corner castings, stiffened sides, gasket, hinges, pulls and latches |
| QH01 quarantine container | 1 | Separate quarantine class, open inspection lid, accessible controls, searchable hiding-volume anchor |
| CT01 transfer cart | 1 | Four casters, brakes, jack/scissor mechanism, transport saddle and formed push handle; parked empty intentionally |
| HJ01_HANDLING_JIB | 1 | Anchored mast, slewing boom, trolley, chainwheel, chain and safety-latched hook; parked clear of service routes |
| VF01_EXTRACTION | 1 | Twin filter cassettes, gasket/rims/hinges/latches, DP sampling, connected fan/motor, isolator, separated intake/exhaust paths |
| IM01_INVENTORY | 1 | Ground-floor booth, terminal, scanner, analog dose instrument, logbook, serialized tags, task lamp and operator chair |
| WB01_SEAL_REPAIR | 1 | Supported bench, tool board, seal tools, spares, cloth, fastener tray and repair case |
| Cell monitors / receiving dosimeter | 5 | Four storage monitoring heads with risers; separate receiving instrument |
| External / internal doors | 3 / 1 | Receiving, personnel and dispatch plus the monitoring-booth leaf |

Exact evaluated equipment bounds, including projecting hardware, are in `architecture/equipment-measured.json`. Nominal body dimensions in concepts are not substituted for these measurements.

Supplied host hooks include inventory, ventilation isolation, quarantine inspection, waste breach, room audio and receiving/dispatch navigation. Waste capacity/backlog, reactor waste transfer, illicit storage, exposure, inventory falsification, search/escape and incident recovery remain explicit engine-state responsibilities. Their Blender anchors do not claim implemented gameplay.
