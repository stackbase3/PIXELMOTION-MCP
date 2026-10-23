"""
Unit tests for Visual QA Pipeline.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from pixelmotion.server.core.visual_qa import VisualQAPipeline
from pixelmotion.server.core.models import SceneData, CompositionType, CursorEvent, DetectedRegion, UIReconstruction


def test_visual_qa():
    qa = VisualQAPipeline()

    scene = SceneData(
        scene_id="qa_test_scene",
        duration_frames=120,
        fps=30,
        composition=CompositionType.FLAT_WALKTHROUGH,
        cursor_events=[
            CursorEvent(frame=30, x=500, y=300, action="click", target_region_id="btn_1")
        ]
    )

    recons = UIReconstruction(
        reference_id="ref_1",
        source_path="/tmp/fake.png",
        dimensions=[1920, 1080],
        fidelity_score=1.0,
        locked_reference_path="/tmp/fake.png",
        regions=[
            DetectedRegion(region_id="btn_1", label="button", x=450, y=280, width=120, height=40, is_interactive=True)
        ]
    )

    report = qa.run_qa_suite("test_proj", scene, reconstruction=recons)
    assert report.checks["cursor_accuracy"] is True
    print(f"  ✓ Visual QA verification status: {report.overall_status.upper()}, Fidelity: {report.fidelity_score}")


if __name__ == "__main__":
    print("\n--- Running Visual QA Unit Tests ---")
    test_visual_qa()
    print("All Visual QA unit tests passed!\n")
