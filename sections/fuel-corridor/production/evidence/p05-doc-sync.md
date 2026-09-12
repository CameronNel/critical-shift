# P05 document synchronization note

The first temporary synchronization helper used Python's Windows default encoding and failed while writing the connection document. The document was immediately reconstructed as UTF-8 with all measured seams, equations, scope limits and P05 decisions. The helper was removed. A101 is generated from UTF-8 interface.json and its editable source; regenerate with architecture/build_plan.py. No neighboring file was changed.
