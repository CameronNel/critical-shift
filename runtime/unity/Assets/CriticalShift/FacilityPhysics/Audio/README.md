# Bonk shovel tin sound

**Bonk.wav by Harrisando**, selected by the user on 2 October 2026. A pop-can
metal thud/bonk, replacing the earlier synthesized sound.

Source: https://freesound.org/people/Harrisando/sounds/466202/
Public-domain dedication: https://creativecommons.org/publicdomain/zero/1.0/
The sound page explicitly lists Creative Commons 0: commercial use and modification
are allowed without attribution or permission. Creator credit is retained here
for provenance, although it is not required by CC0.

The original WAV download requires a Freesound login. This runtime derivative uses
the publicly available **high-quality MP3 preview**, not the original lossless file:
https://cdn.freesound.org/previews/466/466202_9855691-hq.mp3

Converted to mono 48 kHz, 16-bit PCM, 1.835 s. Pitch and duration are preserved;
decoded float samples are scaled to peak 0.82 before quantization to prevent
conversion clipping. No additional reverb or synthesized layers are added. Exact
source/output hashes and conversion details are in
`runtime/validation/harrisando-bonk-evidence.json`. The superseded synthesis
generator is removed so it cannot overwrite the selected recording.

The existing WAV filename and metadata GUID are preserved. Import as mono PCM/preloaded; the
scene binder assigns it to a dedicated spatial AudioSource on BonkShovel. Sound
plays only after an accepted player hit or first solid wall/object contact; a miss
is silent. Doppler is disabled, with a 1–14 m local attenuation range.

Audio output quality/scene balance still need listening in the target Unity Player.
