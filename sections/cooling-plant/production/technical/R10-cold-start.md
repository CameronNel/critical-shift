# R10 cold-start evidence



**REVIEW** — fresh saved-file render comparison; artifact unchanged: True.



Two independent Blender processes cold-open the same saved artifact. Ten primary cameras rendered through shared GPU gate. Exact decoded RGB equality; no numerical tolerance used.



Blender file SHA256: `cdc0b48a5af6cb11bae6a4511074cc4b9aacf4dce687503e55d3891a49bb2693`



| Camera | Equal decoded pixels | Changed channels | Maximum difference /255 |

|---|---|---:|---:|

| C01_ENTRY | False | 1177 | 8 |

| C02_HERO | False | 1747 | 9 |

| C03_REVERSE | False | 1868 | 7 |

| C04_ROUTE | False | 388 | 1 |

| C05_PUMP_A | False | 382 | 1 |

| C06_EXCHANGER | False | 2113 | 7 |

| C07_PINCH | False | 646 | 1 |

| C08_WORKSHOP | False | 211 | 1 |

| C09_BUNDLE_BAY | False | 1354 | 8 |

| C10_MATERIALS | False | 563 | 1 |



Saved Blender artifact survival and render repeatability only; not whole-map or game-engine verification.
