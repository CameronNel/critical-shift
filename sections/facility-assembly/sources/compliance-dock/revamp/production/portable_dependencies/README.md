# Portable inherited dependencies

These 25 unchanged native payloads are mirrored as ordinary-Git compressed parts because the authenticated GitHub LFS download endpoint returned403. No original source was edited. Total archive: 847078804 bytes; 26 parts, each at most32MiB. The two inherited map/preview natives exceed GitHub's single-file limit, so they cannot be mirrored as individual Git blobs.

After cloning this task branch, run the room-root `restore_dependencies.py` with Python3. It verifies every part and full payload SHA, restores only missing/expected LFS-pointer files, and refuses to replace edited bytes. `--verify-only` checks already hydrated dependencies. This is local hydration of existing repository inputs; it does not modify their logical contents or select the overhaul in the map.

The editable overhaul source and recipes remain normal room-root files. All dependency images in the cold native inventory are packed or otherwise present.
