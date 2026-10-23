"""
Generates a clean, rhythmic 120 BPM soundtrack (kick on 1 & 3, snare on 2 & 4, hi-hats on 8ths)
for deterministic beat-sync testing.
"""

import numpy as np
from scipy.io import wavfile
import subprocess
from pathlib import Path

def generate_soundtrack(output_wav: str, duration_sec: float = 30.0, bpm: float = 120.0):
    sr = 22050
    total_samples = int(duration_sec * sr)
    audio = np.zeros(total_samples, dtype=np.float32)

    beat_interval = 60.0 / bpm
    frames_per_beat = int(beat_interval * sr)

    t_kick = np.linspace(0, 0.25, int(0.25 * sr), endpoint=False)
    # Pitch drop 140Hz -> 45Hz
    f_kick = np.linspace(140, 45, len(t_kick))
    kick_wave = 0.8 * np.sin(2 * np.pi * f_kick * t_kick) * np.exp(-t_kick * 14)

    t_snare = np.linspace(0, 0.2, int(0.2 * sr), endpoint=False)
    noise = np.random.normal(0, 0.5, len(t_snare))
    tone = 0.5 * np.sin(2 * np.pi * 185 * t_snare)
    snare_wave = (noise + tone) * np.exp(-t_snare * 18)

    t_hat = np.linspace(0, 0.05, int(0.05 * sr), endpoint=False)
    hat_wave = 0.25 * np.random.normal(0, 0.4, len(t_hat)) * np.exp(-t_hat * 40)

    cur_beat = 0
    while True:
        sample_idx = int(cur_beat * beat_interval * sr)
        if sample_idx >= total_samples - len(kick_wave):
            break

        # Beat within 4-beat bar (0, 1, 2, 3)
        bar_beat = cur_beat % 4

        # Hi-hat on every 8th note
        h_idx1 = sample_idx
        h_idx2 = sample_idx + frames_per_beat // 2
        if h_idx1 + len(hat_wave) < total_samples:
            audio[h_idx1:h_idx1 + len(hat_wave)] += hat_wave
        if h_idx2 + len(hat_wave) < total_samples:
            audio[h_idx2:h_idx2 + len(hat_wave)] += hat_wave

        if bar_beat in (0, 2):  # Kicks on 1 and 3
            audio[sample_idx:sample_idx + len(kick_wave)] += kick_wave
        elif bar_beat in (1, 3):  # Snares on 2 and 4
            audio[sample_idx:sample_idx + len(snare_wave)] += snare_wave

        cur_beat += 1

    # Ambient low pad drone (chord in D-minor: D, F, A)
    t_full = np.linspace(0, duration_sec, total_samples, endpoint=False)
    pad = 0.08 * (
        np.sin(2 * np.pi * 146.83 * t_full) +
        np.sin(2 * np.pi * 174.61 * t_full) +
        np.sin(2 * np.pi * 220.00 * t_full)
    )
    audio += pad

    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.9

    out_p = Path(output_wav)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_p), sr, (audio * 32767).astype(np.int16))
    print(f"Generated soundtrack at {out_p.resolve()}")

if __name__ == "__main__":
    generate_soundtrack("pixelmotion/data/test_assets/soundtrack_120bpm.wav")
