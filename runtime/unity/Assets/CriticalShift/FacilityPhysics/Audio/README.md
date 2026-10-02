# Bonk shovel tin sound

Original 0.54-second mono, 48 kHz, 16-bit PCM sound, synthesized for this task from
inharmonic sheet-metal modes, a short pitch scoop and a quiet transient. No external
recordings, samples or third-party content were used. Intended character: a clean,
hollow vintage-cartoon tin "tonk", with a short bright rim and no added reverb.

Regenerate with `python runtime/tools/make_bonk_sound.py` (standard library only).
The checked-in WAV is the Unity runtime asset. Import as mono PCM/preloaded; the
scene binder assigns it to a dedicated spatial AudioSource on BonkShovel. Sound
plays only after an accepted player hit or first solid wall/object contact; a miss
is silent. Doppler is disabled, with a 1–14 m local attenuation range.

Audio output quality/scene balance still need listening in the target Unity Player.
