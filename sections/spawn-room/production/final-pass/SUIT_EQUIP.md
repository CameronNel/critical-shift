# Suit equip contract (spawn room lockers)

Each locker `PPE_0n` holds one hanging suit, asset root `PPE_0n_suit` (empty), one per player/station `n = 1..4`.

Authored properties on the asset root:
- `asset_role = "equippable_suit"`
- `cs_equip_station = n`
- `cs_hide_on_equip = True`

Intended runtime behaviour (owner request): when the player for station `n` equips the suit, the whole `PPE_0n_suit`
hierarchy (suit, hook, strap and the locker strip light is separate and stays on) is hidden or deactivated, so the locker
reads empty; the suit is the same asset the player character wears (`character_suit.build_hazmat`).

Not implemented here: the toggle itself is runtime logic and was not built or tested (no Unity project in this repo
state). Open owner decision: whether the suit reappears if the player returns or removes it.
