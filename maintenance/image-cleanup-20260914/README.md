# Image cleanup, 14 September 2026

Removed 810 historical review images (1603515639 bytes of hydrated payload) on the task branch only.

Both canonical MAP.json scenes were opened in separate, read-only Blender processes before and after deletion. Their complete recorded dependency inventories, geometry digests, packed-image hashes, source-file hashes and object counts match exactly. All linked libraries resolved. No Blender file, material, poster, texture, geometry, source module, MAP.json or existing script was edited. No scene was saved or rendered.

## Retention

Retained every native image/path dependency, all source artwork, concepts, textures, PBR packs, posters, references and baseline comparison inputs. Kept all accepted condenser R34 review sets, the current spawn R17 images, and the latest review for every exterior section. All existing Markdown reports and JSON evidence remain. Only the removed historical output filenames are ignored, not arbitrary images or future revisions.

## Historical references and recovery

Some old review reports reference images deliberately pruned by this cleanup. Those references are historical, not missing map dependencies. The full path, Git blob, LFS object ID and hydrated byte size are in REMOVED_IMAGES.json. Restore an individual old image from commit `a82c7d9b80456153a0c65ca4897044a7f62c7d1c` using `git restore --source=a82c7d9b80456153a0c65ca4897044a7f62c7d1c -- path/to/image.png`, then `git lfs pull --include=path/to/image.png`.

## Scope of verification

This is a native dependency and byte-integrity audit, not a Unity test, FPS benchmark, visual render approval or independent human review. Nothing is merged into main by this task.

Deleting pointers from a branch does not purge old LFS objects or reclaim GitHub LFS quota. No history rewrite, force push, LFS remote purge, repository recreation or asset recompression was performed.
