"""
PixelMotion Audio & Beat Synchronization Engine
Dual-mode beat detector:
1. Native SciPy/NumPy spectral novelty & onset tracker (zero external network/librosa required)
2. Librosa integration when installed
Supports:
- Kick and snare classification
- Scene boundary suggestions on 2-bar intervals
- In-scene event alignment (nudge clicks & reveals to nearest beat)
- Typing budget verification against frame durations
"""

import os
import json
import math
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from scipy import signal
from scipy.io import wavfile

from pixelmotion.server.core.config import FFMPEG_PATH


def convert_to_wav(audio_path: str, temp_wav_path: str) -> str:
    """Uses ffmpeg to decode any input audio (mp3, aac, ogg, wav) into standard mono 22050Hz WAV."""
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", audio_path,
        "-ac", "1",
        "-ar", "22050",
        temp_wav_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return temp_wav_path


def detect_beats_scipy(wav_path: str, fps: int = 30, bpm_override: Optional[float] = None) -> Dict[str, Any]:
    """
    Analyzes audio rhythm using SciPy spectral flux onset envelope and autocorrelation tempo estimation.
    """
    sr, data = wavfile.read(wav_path)
    if data.dtype == np.int16:
        y = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        y = data.astype(np.float32) / 2147483648.0
    else:
        y = data.astype(np.float32)

    duration = len(y) / float(sr)
    total_frames = int(round(duration * fps))

    # Compute spectrogram with hop_length 512, n_fft 2048
    hop_length = 512
    n_fft = 2048
    freqs, times, Sxx = signal.spectrogram(y, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)

    # Spectral flux / onset novelty curve (half-wave rectified difference)
    log_Sxx = np.log1p(100.0 * np.abs(Sxx))
    flux = np.diff(log_Sxx, axis=1)
    flux = np.maximum(0.0, flux)
    onset_env = np.sum(flux, axis=0)
    # Smooth onset envelope
    b, a = signal.butter(2, 0.1)
    onset_smoothed = signal.filtfilt(b, a, onset_env)
    times_env = times[:len(onset_smoothed)]

    # Peak detection for onsets
    min_dist = int(0.2 * (sr / hop_length))  # at least 200ms apart
    peaks, _ = signal.find_peaks(onset_smoothed, height=np.mean(onset_smoothed) * 1.2, distance=min_dist)

    # Estimate tempo (BPM) via autocorrelation
    if bpm_override:
        bpm = float(bpm_override)
    else:
        corr = signal.correlate(onset_smoothed - np.mean(onset_smoothed), onset_smoothed - np.mean(onset_smoothed), mode="full")
        corr = corr[len(corr)//2:]
        # BPM search range: 60 - 180
        fps_env = sr / float(hop_length)
        min_lag = int(60.0 / 180.0 * fps_env)
        max_lag = int(60.0 / 60.0 * fps_env)
        if max_lag < len(corr):
            lag_peak = min_lag + np.argmax(corr[min_lag:max_lag])
            bpm = round((60.0 * fps_env) / lag_peak, 1)
        else:
            bpm = 120.0

    frames_per_beat = max(1, round(fps * 60.0 / bpm))
    onset_times = times_env[peaks] if len(peaks) > 0 else np.array([])

    # Separate into kick (dominant low frequencies < 250Hz) and snare (> 1000Hz)
    kicks = []
    snares = []
    low_band_idx = np.where(freqs < 250)[0]
    high_band_idx = np.where(freqs > 1000)[0]

    for p in peaks:
        t_sec = times[p]
        f_frame = int(round(t_sec * fps))
        # inspect spectral centroid around peak
        low_energy = np.sum(Sxx[low_band_idx, p]) if len(low_band_idx) > 0 else 0
        high_energy = np.sum(Sxx[high_band_idx, p]) if len(high_band_idx) > 0 else 0
        if low_energy > high_energy:
            kicks.append(f_frame)
        else:
            snares.append(f_frame)

    beat_frames = [int(round(t * fps)) for t in onset_times]
    kick_frames = sorted(set(kicks))
    snare_frames = sorted(set(snares))

    first_kick = kick_frames[0] if kick_frames else (beat_frames[0] if beat_frames else 0)

    # 2-bar scene boundaries
    frames_per_bar = frames_per_beat * 4
    scene_spacing = frames_per_bar * 2
    recommended_boundaries = [0]
    cur = first_kick
    while cur < total_frames:
        if cur > 0 and cur not in recommended_boundaries:
            recommended_boundaries.append(cur)
        cur += scene_spacing
    if recommended_boundaries[-1] != total_frames:
        recommended_boundaries.append(total_frames)

    return {
        "bpm": bpm,
        "fps": fps,
        "frames_per_beat": frames_per_beat,
        "first_kick_frame": first_kick,
        "duration_seconds": round(duration, 3),
        "total_frames": total_frames,
        "snare_frames": snare_frames,
        "kick_frames": kick_frames,
        "beat_frames": beat_frames,
        "recommended_scene_boundaries": recommended_boundaries,
        "warnings": []
    }


def analyze_beats(audio_file_path: str, fps: int = 30, bpm: Optional[float] = None, output_json: Optional[str] = None) -> Dict[str, Any]:
    """Analyzes beats and rhythm from audio file."""
    audio_path = Path(audio_file_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    temp_wav = audio_path.parent / f"temp_{audio_path.stem}.wav"
    convert_to_wav(str(audio_path), str(temp_wav))

    try:
        data = detect_beats_scipy(str(temp_wav), fps=fps, bpm_override=bpm)
    finally:
        if temp_wav.exists():
            temp_wav.unlink()

    if output_json:
        out_p = Path(output_json)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w") as f:
            json.dump(data, f, indent=2)

    return data


def align_internal_events(events: List[Dict[str, Any]], beats_data: Dict[str, Any], max_nudge_frames: int = 6) -> List[Dict[str, Any]]:
    """
    Nudges internal scene events (clicks, card pop-ins, scale punches) onto the nearest
    kick or snare beat within ±max_nudge_frames.
    """
    target_beats = sorted(set(beats_data.get("snare_frames", []) + beats_data.get("kick_frames", [])))
    if not target_beats:
        return events

    aligned_events = []
    for ev in events:
        original_frame = ev.get("frame", 0)
        # Find nearest beat
        best_beat = min(target_beats, key=lambda b: abs(b - original_frame))
        delta = best_beat - original_frame
        aligned_ev = dict(ev)
        if abs(delta) <= max_nudge_frames:
            aligned_ev["frame"] = best_beat
            aligned_ev["beat_aligned"] = True
            aligned_ev["nudge_delta"] = delta
        else:
            aligned_ev["beat_aligned"] = False
            aligned_ev["nudge_delta"] = 0
        aligned_events.append(aligned_ev)

    return aligned_events


def check_typing_budget(text: str, duration_frames: int, per_char_frames: int = 2) -> Dict[str, Any]:
    """
    Checks if a typed text sequence fits safely inside scene duration.
    Leaves 20% hold margin at the end so text is readable before scene cut.
    """
    char_count = len(text)
    required_frames = char_count * per_char_frames
    safe_budget = int(duration_frames * 0.8)
    fits = required_frames <= safe_budget

    return {
        "text_length": char_count,
        "required_frames": required_frames,
        "available_frames": duration_frames,
        "safe_budget_frames": safe_budget,
        "fits_comfortably": fits,
        "slack_frames": duration_frames - required_frames,
        "warning": None if fits else f"Text of {char_count} chars needs {required_frames}f, exceeding safe budget of {safe_budget}f."
    }
