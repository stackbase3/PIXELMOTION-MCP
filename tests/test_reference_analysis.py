"""
Unit tests for Reference Analysis, Region Detection, and Visual Diff Comparison.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from pixelmotion.server.core.reference import analyze_reference, detect_regions, extract_asset, compare_images


def test_reference_analysis():
    img_path = root_dir / "pixelmotion/data/test_assets/trading_journal_dashboard.png"
    assert img_path.exists()

    analysis = analyze_reference(str(img_path))
    assert analysis["width"] == 1920
    assert analysis["height"] == 1080
    assert analysis["aspect_ratio"] == "16:9"
    assert analysis["is_dark_mode"] is True
    print(f"  ✓ Reference analysis: {analysis['width']}x{analysis['height']}, dark_mode={analysis['is_dark_mode']}")


def test_region_detection():
    img_path = root_dir / "pixelmotion/data/test_assets/trading_journal_dashboard.png"
    crops_dir = root_dir / "pixelmotion/data/test_assets/temp_crops"
    regions = detect_regions(str(img_path), output_crops_dir=str(crops_dir))
    assert len(regions) > 0, "No regions detected!"
    print(f"  ✓ Region detection found {len(regions)} semantic components.")


def test_visual_compare():
    img_path = root_dir / "pixelmotion/data/test_assets/trading_journal_dashboard.png"
    comp = compare_images(str(img_path), str(img_path))
    assert comp["fidelity_score"] == 1.0
    assert comp["is_acceptable"] is True
    print(f"  ✓ Visual compare self-test fidelity score: {comp['fidelity_score']}")


if __name__ == "__main__":
    print("\n--- Running Reference Analysis Unit Tests ---")
    test_reference_analysis()
    test_region_detection()
    test_visual_compare()
    print("All Reference Analysis unit tests passed!\n")
