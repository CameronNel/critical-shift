# Spawn room real-time light plan (proposed; not engine-tested)

A real-time build cannot run 14 shadowed dynamic lights. Roles are tagged on each light (`cs_rt_role`, `cs_rt_group`); no
light was changed.

| Group | Lights | Role | Why |
|---|---|---|---|
| `hall_power` | HALL_light_00..02, SERVICE_light (4 area) | dynamic key (the only dynamic lights) | main circulation; flicker and brownout events drive these four together |
| `locker_power` | LOCKER_light_00..02 (3 area) | baked + emissive fixture | static light, flicker via the emissive fixture panel |
| `briefing_and_accents` | 2 pendants, lamp, 2 neon, candle, lights (7 points) | baked + emissive fixture | small or accent sources |

Open decisions for the owner: whether locker and briefing should also react to power events (would need more dynamic
lights), the lightmap UV pass and bake resolution, and the engine-side light settings. All of it is unmeasured.
