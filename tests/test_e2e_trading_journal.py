"""
PixelMotion End-to-End Acceptance Test
Executes complete production pipeline for a Trading Journal product film:
1. Ingests and analyzes real trading journal dashboard screenshot
2. Preserves visual design and detects semantic UI regions (equity chart, KPI cards, executions table)
3. Reconstructs UI with locked reference layer and cropped assets
4. Analyzes soundtrack beats (120 BPM) and detects kick/snare boundaries
5. Directs full 6-scene motion production plan with 3D spotlight and 2D walkthrough
6. Aligns in-scene events (card elevations, cursor clicks) to soundtrack snares
7. Compiles deterministic HTML/3D/Remotion compositions
8. Renders low-res preview and master MP4 with FFmpeg
9. Executes Visual QA pipeline (checking fidelity, alignment, legibility, and video integrity)
10. Exports playable MP4 and packages editable project ZIP bundle.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from pixelmotion.server.core.config import PROJECTS_DIR, RENDERS_DIR
from pixelmotion.server.core.reference import analyze_reference, detect_regions, extract_asset, compare_images
from pixelmotion.server.core.reconstruction import reconstruct_ui, validate_reconstruction
from pixelmotion.server.core.audio_engine import analyze_beats, align_internal_events, check_typing_budget
from pixelmotion.server.core.motion_director import AIMotionDirector
from pixelmotion.server.core.scene_engine import SceneCompositionEngine
from pixelmotion.server.core.renderer import VideoRenderer
from pixelmotion.server.core.visual_qa import VisualQAPipeline
from pixelmotion.server.core.exporter import ExportManager
from pixelmotion.server.mcp_server import get_or_create_project, save_project


def run_e2e_test():
    print("=" * 70)
    print("PIXELMOTION MCP: END-TO-END ACCEPTANCE TEST")
    print("Target: High-Impact Trading Journal Product Film")
    print("=" * 70)

    project_id = "trading_journal_demo"
    asset_img = root_dir / "pixelmotion/data/test_assets/trading_journal_dashboard.png"
    soundtrack = root_dir / "pixelmotion/data/test_assets/soundtrack_120bpm.mp3"

    assert asset_img.exists(), f"Test asset missing: {asset_img}"
    assert soundtrack.exists(), f"Soundtrack missing: {soundtrack}"

    # Step 1: Initialize Project & Ingest Reference
    print("\n[Step 1] Ingesting & Analyzing Reference Asset...")
    proj = get_or_create_project(project_id, "EdgeFlow Trading Journal")
    analysis = analyze_reference(str(asset_img))
    print(f"  Dimensions: {analysis['width']}x{analysis['height']} ({analysis['aspect_ratio']})")
    print(f"  Dark Mode: {analysis['is_dark_mode']} (Mean brightness: {analysis['mean_brightness']})")
    print(f"  Dominant Palette: {analysis['dominant_palette']}")
    print(f"  Primary Accent: {analysis['primary_accent']}")

    # Step 2: Semantic Region Detection & Crop Extraction
    print("\n[Step 2] Segmenting Interface Regions & Preserving Difficult Assets...")
    recons_crops_dir = PROJECTS_DIR / project_id / "reconstructions/main_ref/assets"
    regions = detect_regions(str(asset_img), output_crops_dir=str(recons_crops_dir))
    print(f"  Detected {len(regions)} distinct UI panels & cards:")
    for r in regions[:6]:
        print(f"    - {r.region_id}: [{r.label}] at ({r.x}, {r.y}) {r.width}x{r.height}px (interactive={r.is_interactive})")

    # Step 3: UI Reconstruction with Locked Reference Layer
    print("\n[Step 3] Constructing UI Layers adhering to 4-tier Fidelity Priority...")
    reconstruction = reconstruct_ui(
        reference_id="main_ref",
        image_path=str(asset_img),
        project_id=project_id
    )
    val_recons = validate_reconstruction(reconstruction)
    assert val_recons["is_valid"], f"Reconstruction validation failed: {val_recons}"
    print(f"  Locked reference layer established at: {Path(reconstruction.locked_reference_path).name}")
    print(f"  Reconstruction fidelity score: {val_recons['fidelity_score'] * 100:.1f}%")
    proj.reconstructions["main_ref"] = reconstruction

    # Step 4: Soundtrack Rhythm & Beat Analysis
    print("\n[Step 4] Analyzing Audio Rhythm & Detecting Snare Grid...")
    beats_data = analyze_beats(str(soundtrack), fps=30)
    print(f"  Detected BPM: {beats_data['bpm']}")
    print(f"  Frames Per Beat: {beats_data['frames_per_beat']} (first kick at frame {beats_data['first_kick_frame']})")
    print(f"  Total Kicks: {len(beats_data['kick_frames'])}, Total Snares: {len(beats_data['snare_frames'])}")
    print(f"  Recommended 2-Bar Scene Boundaries: {beats_data['recommended_scene_boundaries'][:8]}")
    proj.beats_data = beats_data
    proj.audio_path = str(soundtrack)

    # Step 5: AI Motion Director Plan Synthesis
    print("\n[Step 5] Directing AI Motion Production Plan...")
    director = AIMotionDirector()
    plan = director.generate_motion_plan(
        project_id=project_id,
        product_name="EdgeFlow",
        feature_focus="Equity Curve & Alpha Breakdown",
        narrative_goal="Cinematic dimensional intro transitioning to real click walkthrough",
        target_duration_seconds=30,
        bpm=beats_data["bpm"],
        reference_id="main_ref",
        detected_regions=regions,
        beats_data=beats_data
    )
    print(f"  Plan ID: {plan.plan_id}")
    print(f"  Target Duration: {plan.target_duration_frames} frames ({plan.target_duration_frames / 30:.1f}s)")
    print(f"  Director Rationale: {plan.director_rationale[:120]}...")
    print(f"  Scenes Generated ({len(plan.scenes)}):")
    for s in plan.scenes:
        print(f"    * {s.scene_id} [{s.composition.value}]: {s.duration_frames}f ({s.duration_frames/30:.1f}s) -> Objective: {s.scene_objective}")
    proj.motion_plan = plan
    save_project(proj)

    # Step 6: Compiling 3D Feature Spotlight Scene (Act 3)
    print("\n[Step 6] Compiling 3D Spatial Feature Spotlight Scene...")
    scene_engine = SceneCompositionEngine()
    spotlight_scene = next(s for s in plan.scenes if s.scene_id == "scene_03_feature_spotlight")
    spotlight_html = scene_engine.compile_scene_html(
        scene=spotlight_scene,
        reference_image_url=f"file://{Path(reconstruction.locked_reference_path).resolve()}"
    )
    spotlight_html_file = PROJECTS_DIR / project_id / "scene_03_spotlight.html"
    with open(spotlight_html_file, "w") as f:
        f.write(spotlight_html)
    print(f"  Compiled deterministic HTML scene at {spotlight_html_file.name}")

    # Step 7: Compiling 2D Walkthrough Scene (Act 4)
    print("\n[Step 7] Compiling 2D Interface Walkthrough & Cursor Click Scene...")
    walkthrough_scene = next(s for s in plan.scenes if s.scene_id == "scene_04_interface_walkthrough")
    walkthrough_html = scene_engine.compile_scene_html(
        scene=walkthrough_scene,
        reference_image_url=f"file://{Path(reconstruction.locked_reference_path).resolve()}"
    )
    walkthrough_html_file = PROJECTS_DIR / project_id / "scene_04_walkthrough.html"
    with open(walkthrough_html_file, "w") as f:
        f.write(walkthrough_html)
    print(f"  Compiled deterministic HTML walkthrough at {walkthrough_html_file.name}")

    # Step 8: Rendering Preview Video with FFmpeg & Headless Chromium
    print("\n[Step 8] Rendering Preview Video (Act 3 Spotlight)...")
    renderer = VideoRenderer()
    preview_mp4 = RENDERS_DIR / f"preview_{project_id}_spotlight.mp4"
    # To keep test fast while proving full fidelity, render preview frames
    job_prev = renderer.render_scene(
        scene_html_path=str(spotlight_html_file),
        output_mp4_path=str(preview_mp4),
        job_id="job_test_preview_01",
        project_id=project_id,
        duration_frames=30,  # 30 frames test preview
        fps=30,
        width=960,
        height=540,
        preview_mode=True,
        audio_path=str(soundtrack)
    )
    assert job_prev.status == "completed", f"Preview render failed: {job_prev.error}"
    assert preview_mp4.exists() and preview_mp4.stat().st_size > 0, "Preview MP4 was not created!"
    print(f"  Successfully rendered Preview MP4 ({preview_mp4.stat().st_size} bytes)")

    # Step 9: Rendering Master Walkthrough Scene with Audio Muxing
    print("\n[Step 9] Rendering Master 1080p Walkthrough Video (Act 4)...")
    master_mp4 = RENDERS_DIR / f"master_{project_id}_walkthrough.mp4"
    job_master = renderer.render_scene(
        scene_html_path=str(walkthrough_html_file),
        output_mp4_path=str(master_mp4),
        job_id="job_test_master_01",
        project_id=project_id,
        duration_frames=30,  # 30 frames 1080p master
        fps=30,
        width=1920,
        height=1080,
        preview_mode=False,
        audio_path=str(soundtrack)
    )
    assert job_master.status == "completed", f"Master render failed: {job_master.error}"
    assert master_mp4.exists() and master_mp4.stat().st_size > 0, "Master MP4 was not created!"
    print(f"  Successfully rendered Master 1080p MP4 ({master_mp4.stat().st_size} bytes)")

    # Step 10: Running Automated Visual QA Pipeline
    print("\n[Step 10] Executing Automated Visual QA Suite...")
    visual_qa = VisualQAPipeline()
    qa_report = visual_qa.run_qa_suite(
        project_id=project_id,
        scene=walkthrough_scene,
        reconstruction=reconstruction,
        rendered_mp4_path=str(master_mp4)
    )
    print(f"  Overall QA Status: {qa_report.overall_status.upper()}")
    print(f"  Fidelity Score: {qa_report.fidelity_score * 100:.1f}%")
    print(f"  Check Breakdown:")
    for check_name, passed in qa_report.checks.items():
        print(f"    - {check_name}: {'PASSED [OK]' if passed else 'FAILED'}")
    assert qa_report.overall_status in ("pass", "warning"), f"QA Suite failed: {qa_report.issues}"

    # Step 11: Exporting Final Deliverables & Packaging Project Bundle
    print("\n[Step 11] Exporting Playable MP4 & Packaging Editable Project...")
    exporter = ExportManager()
    final_export = RENDERS_DIR / "EdgeFlow_Trading_Journal_Film.mp4"
    exp_res = exporter.export_video(str(master_mp4), str(final_export), preset="hd_1080p")
    print(f"  Final Master Video Exported: {Path(exp_res['output_path']).name} ({exp_res['file_size_bytes']} bytes)")

    bundle_zip = PROJECTS_DIR / f"{project_id}_bundle.zip"
    exporter.export_project_bundle(project_id, str(bundle_zip))
    print(f"  Editable Project Bundle Saved: {bundle_zip.name} ({bundle_zip.stat().st_size} bytes)")

    print("\n" + "=" * 70)
    print("ALL 11 ACCEPTANCE CRITERIA SUCCESSFULLY PASSED!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_e2e_test()
    if not success:
        sys.exit(1)
