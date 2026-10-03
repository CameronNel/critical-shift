# Fixed refinery review cameras

Nine original camera matrices and lenses remain unmodified: CAM_ENTRY, CAM_MAIN_ROUTE, CAM_PROCESS, CAM_REVERSE, CAM_PINCH, CAM_MATERIAL, CAM_ASSEMBLY, CAM_DISPATCH, CAM_MINE_TO_CRUSHER. Baseline preview screenshots were CPU Cycles16 samples1280x720; formal candidate comparisons use CPU Cycles24 samples960x540, seed73, 8 bounces, AgX Medium High Contrast. Final evidence uses the same settings unless explicitly recorded.

Two supplementary fixed detail views: CAM_HERO_DETAIL (-.30,2.15,1.68) → (1.18,4.79,1.9),34mm; CAM_WORK_NOOK (-.60,-3.15,1.68) → (.92,-5.91,1.50),31mm.

Before formal full-room review, nook camera v2 was found to be blocked by the conveyor. V3 still showed an awkward inaccessible nook/pier overlap. The worker cluster was structurally relocated to the south corner and the nook evidence viewpoint replaced for slice_v4. These changes are documented; no full-room accepted camera was changed to hide a defect.

Every render batch writes actual camera matrices, lens, scene hash, settings and image hash to its manifest. Supplementary views do not replace broad gameplay views.
