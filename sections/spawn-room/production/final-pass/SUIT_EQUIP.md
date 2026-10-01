# Suit equip contract (spawn room lockers)

Each locker `PPE_0n` holds one hanging suit, asset root `PPE_0n_suit` (empty), one per player/station `n = 1..4`.

Authored properties on the asset root:
- `asset_role = "equippable_suit"`
- `cs_equip_station = n`
- `cs_hide_on_equip = True`: hidden while the player wears it
- `cs_show_on_unequip = True`: reappears when it is taken off
- `cs_unequip_only_at_station = True`: it can only be taken off at its own locker

Owner decisions (2026-10-01):
1. When the player for station `n` equips the suit, the whole `PPE_0n_suit` hierarchy (suit, hook and strap; the boot dock
   `PPE_0n_boot_dock` and the locker strip light are separate and stay) is hidden or deactivated, so the locker reads
   empty with its dock.
2. The suit reappears once it is removed, and it can only be removed in the locker (at the station the suit belongs to).
   Returning it is therefore a locker interaction, not a drop anywhere in the facility.

The suit is the same asset the player character wears (`character_suit.build_hazmat`).

Not implemented here: the toggle and the locker interaction are runtime logic and were not built or tested (no Unity
project in this repo state). Open for the runtime owner: what happens to a suit that is equipped when its player
disconnects, and whether another player may take an unworn suit from a locker that is not theirs.
