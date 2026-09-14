# Scoped collection visibility audit

CPU-only inspection of spawn R05, turbine R03 and refinery R01 compares inherited collection/object hide_render and hide_viewport along source MODULE membership paths with actual SOURCE_REVIEW wrapper paths. All three MODULE trees have no collection hide_render/hide_viewport flags; zero original-name objects change effective visibility under these flags. The reactor hidden-QA finding therefore is not reproduced in these three module trees.

This is not a full render-visibility equivalence claim: per-view-layer exclusions/holdout, ray visibility and renamed local light copies are outside this test. A recursive wrapper is still the appropriate structural preservation fix. Evidence per-section collection-visibility-REV.json and spawn-room/collection-visibility-audit.py. No source/model writes or renders.
