"""
Unit tests for AI Motion Director and Scene Engine.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from pixelmotion.server.core.motion_director import AIMotionDirector
from pixelmotion.server.core.scene_engine import SceneCompositionEngine
from pixelmotion.server.core.models import DetectedRegion


def test_motion_plan_generation():
    director = AIMotionDirector()
    mock_regions = [
        DetectedRegion(region_id="r1", label="main_chart_panel", x=240, y=200, width=1000, height=400, is_interactive=True),
        DetectedRegion(region_id="r2", label="action_button", x=1700, y=20, width=150, height=40, is_interactive=True)
    ]

    plan = director.generate_motion_plan(
        project_id="test_plan_proj",
        product_name="Trading Journal",
        feature_focus="Execution Analytics",
        duration_seconds=30,
        bpm=120.0,
        detected_regions=mock_regions
    )

    assert plan.target_duration_frames > 0
    assert len(plan.scenes) == 6
    print(f"  ✓ Motion director generated {len(plan.scenes)} purposeful scenes ({plan.target_duration_frames}f).")


def test_scene_validation():
    director = AIMotionDirector()
    plan = director.generate_motion_plan(
        project_id="test_val_proj",
        product_name="App",
        feature_focus="Feature"
    )
    engine = SceneCompositionEngine()
    for s in plan.scenes:
        val = engine.validate_scene(s)
        assert val["is_valid"], f"Scene {s.scene_id} invalid: {val['errors']}"
    print("  ✓ All generated scenes verified valid by SceneCompositionEngine.")


if __name__ == "__main__":
    print("\n--- Running Motion Director Unit Tests ---")
    test_motion_plan_generation()
    test_scene_validation()
    print("All Motion Director unit tests passed!\n")
