"""
Unit tests for Audio Beat Detection, Event Alignment, and Typing Budget.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from pixelmotion.server.core.audio_engine import analyze_beats, align_internal_events, check_typing_budget


def test_audio_beats():
    snd_path = root_dir / "pixelmotion/data/test_assets/soundtrack_120bpm.mp3"
    assert snd_path.exists()

    beats = analyze_beats(str(snd_path), fps=30)
    assert 110.0 <= beats["bpm"] <= 130.0, f"BPM unexpected: {beats['bpm']}"
    assert len(beats["kick_frames"]) > 0
    assert len(beats["snare_frames"]) > 0
    print(f"  ✓ Beat detector: BPM {beats['bpm']}, {len(beats['kick_frames'])} kicks, {len(beats['snare_frames'])} snares")


def test_event_alignment():
    beats_dummy = {"snare_frames": [30, 60, 90], "kick_frames": [15, 45, 75]}
    events = [
        {"frame": 28, "name": "card_pop"},   # within 2 frames of 30
        {"frame": 63, "name": "button_click"}, # within 3 frames of 60
        {"frame": 105, "name": "off_beat"}    # far from beat
    ]
    aligned = align_internal_events(events, beats_dummy, max_nudge_frames=6)
    assert aligned[0]["frame"] == 30 and aligned[0]["beat_aligned"] is True
    assert aligned[1]["frame"] == 60 and aligned[1]["beat_aligned"] is True
    assert aligned[2]["frame"] == 105 and aligned[2]["beat_aligned"] is False
    print("  ✓ In-scene event alignment correctly nudged on-beat events.")


def test_typing_budget():
    res_fit = check_typing_budget("Automated Trade Journaling", duration_frames=120, per_char_frames=2)
    assert res_fit["fits_comfortably"] is True

    res_overflow = check_typing_budget("This is an excessively long copy text that cannot possibly fit in only thirty frames without truncating", duration_frames=30, per_char_frames=2)
    assert res_overflow["fits_comfortably"] is False
    print("  ✓ Typing budget successfully detected comfortable fit and overflow warning.")


if __name__ == "__main__":
    print("\n--- Running Audio Engine Unit Tests ---")
    test_audio_beats()
    test_event_alignment()
    test_typing_budget()
    print("All Audio Engine unit tests passed!\n")
