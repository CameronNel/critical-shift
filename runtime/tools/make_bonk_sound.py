"""Synthesize the original tin bonk. Python standard library only; no sampled/licensed input."""
import array
import hashlib
import json
import math
from pathlib import Path
import random
import wave

RATE = 48000
DURATION = 0.54
TARGET = Path(__file__).resolve().parents[1] / 'unity/Assets/CriticalShift/FacilityPhysics/Audio/bonk_shovel_tin.wav'


def synthesize():
    noise = random.Random(7241)
    # Inharmonic sheet-metal modes: a round low 'tonk', with a bright, brief tin rim.
    modes = [(342, .58, .105), (617, .24, .072), (953, .18, .060),
             (1427, .10, .046), (2013, .055, .032), (2911, .025, .019)]
    samples = []
    previous_noise = 0
    for i in range(round(RATE * DURATION)):
        t = i / RATE
        attack = 1 - math.exp(-t / .0007)
        tone = 0
        for frequency, gain, decay in modes:
            # A short downward pitch scoop supplies the cartoon metal-pan character.
            phase = 2 * math.pi * frequency * (t + .08 * .014 * (1 - math.exp(-t / .014)))
            tone += gain * math.sin(phase) * math.exp(-t / decay)
        current_noise = noise.uniform(-1, 1)
        tap = (current_noise - previous_noise) * .052 * math.exp(-t / .004)
        previous_noise = current_noise
        tail = min(1, (DURATION - t) / .035)
        samples.append((tone * attack + tap) * max(0, tail) ** 2)
    # Remove residual DC and retain headroom. No hard clipping or added room/reverb.
    mean = sum(samples) / len(samples)
    samples = [s - mean for s in samples]
    fade = round(RATE * .004)
    for i in range(fade):
        samples[i] *= i / fade
        samples[-i - 1] *= i / fade
    scale = .82 / max(abs(s) for s in samples)
    pcm = array.array('h', [round(s * scale * 32767) for s in samples])
    import sys
    if sys.byteorder != 'little':
        pcm.byteswap()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(TARGET), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm.tobytes())
    report = {'source': 'original deterministic modal synthesis; no external samples',
              'style': 'short hollow tin tonk with a crisp rim and cartoon pitch scoop',
              'sample_rate': RATE, 'channels': 1, 'bits': 16, 'duration_seconds': DURATION,
              'peak': max(abs(s) for s in pcm) / 32768, 'rms': math.sqrt(sum(s * s for s in pcm) / len(pcm)) / 32768,
              'clipped_samples': sum(abs(s) >= 32767 for s in pcm),
              'first_sample': pcm[0], 'last_sample': pcm[-1],
              'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest()}
    assert report['clipped_samples'] == 0 and report['first_sample'] == report['last_sample'] == 0
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    synthesize()
