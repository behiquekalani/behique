#!/usr/bin/env python3
"""
Generate a simple ambient background track for reels.
Creates a warm, emotional piano-like ambient pad using pure synthesis.
No external dependencies beyond numpy (comes with most Python installs).

Usage:
    python3 generate_ambient_music.py
    # Output: music/ambient_warm.wav
"""

import struct
import math
import os
import wave
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
MUSIC_DIR = PIPELINE_DIR / "music"
SAMPLE_RATE = 44100
DURATION = 60  # 60 seconds, will loop


def sine_wave(freq, duration, sample_rate, amplitude=0.3):
    """Generate a sine wave."""
    samples = int(duration * sample_rate)
    return [amplitude * math.sin(2 * math.pi * freq * t / sample_rate) for t in range(samples)]


def envelope(samples, attack=0.3, release=0.5, sample_rate=44100):
    """Apply attack/release envelope."""
    attack_samples = int(attack * sample_rate)
    release_samples = int(release * sample_rate)
    total = len(samples)

    result = []
    for i, s in enumerate(samples):
        if i < attack_samples:
            env = i / attack_samples
        elif i > total - release_samples:
            env = (total - i) / release_samples
        else:
            env = 1.0
        result.append(s * env)
    return result


def mix(tracks):
    """Mix multiple tracks together."""
    max_len = max(len(t) for t in tracks)
    result = [0.0] * max_len
    for track in tracks:
        for i, s in enumerate(track):
            result[i] += s
    # Normalize
    peak = max(abs(s) for s in result) or 1.0
    return [s / peak * 0.8 for s in result]


def write_wav(filename, samples, sample_rate=44100):
    """Write samples to WAV file."""
    with wave.open(str(filename), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(sample_rate)
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            w.writeframes(struct.pack('<h', int(clamped * 32767)))


def generate_ambient():
    """
    Generate warm ambient pad.
    Uses layered sine waves with slow modulation for a dreamy, emotional feel.
    Chord: Cmaj7 voicing (C3, E3, G3, B3) with subtle detuning.
    """
    MUSIC_DIR.mkdir(exist_ok=True)

    print("Generating ambient background music...")

    # Warm chord frequencies (Cmaj7 spread voicing)
    chord = [
        130.81,   # C3
        164.81,   # E3
        196.00,   # G3
        246.94,   # B3
    ]

    tracks = []

    # Layer 1: Main pad (fundamental frequencies)
    for freq in chord:
        wave_data = sine_wave(freq, DURATION, SAMPLE_RATE, amplitude=0.15)
        # Add subtle detuning (chorus effect)
        wave_data2 = sine_wave(freq * 1.003, DURATION, SAMPLE_RATE, amplitude=0.08)
        combined = [a + b for a, b in zip(wave_data, wave_data2)]
        tracks.append(envelope(combined, attack=2.0, release=3.0))

    # Layer 2: Higher octave, very quiet (shimmer)
    for freq in chord[:2]:  # Just C and E an octave up
        wave_data = sine_wave(freq * 2, DURATION, SAMPLE_RATE, amplitude=0.04)
        tracks.append(envelope(wave_data, attack=3.0, release=4.0))

    # Layer 3: Sub bass (very low C)
    sub = sine_wave(65.41, DURATION, SAMPLE_RATE, amplitude=0.1)  # C2
    tracks.append(envelope(sub, attack=2.0, release=3.0))

    # Layer 4: Slow volume modulation (breathing effect)
    mixed = mix(tracks)

    # Apply slow LFO for breathing feel
    lfo_rate = 0.08  # Very slow breathing
    modulated = []
    for i, s in enumerate(mixed):
        t = i / SAMPLE_RATE
        mod = 0.7 + 0.3 * math.sin(2 * math.pi * lfo_rate * t)
        modulated.append(s * mod)

    # Crossfade the last 2 seconds into the first 2 seconds for seamless loop
    crossfade = int(2.0 * SAMPLE_RATE)
    for i in range(crossfade):
        fade_out = 1.0 - (i / crossfade)
        fade_in = i / crossfade
        modulated[-(crossfade - i)] = (modulated[-(crossfade - i)] * fade_out +
                                        modulated[i] * fade_in)

    output = MUSIC_DIR / "ambient_warm.wav"
    write_wav(output, modulated)

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"Done: {output} ({size_mb:.1f} MB, {DURATION}s)")
    print("This will be mixed at 12% volume under narration.")


if __name__ == "__main__":
    generate_ambient()
