"""
PixelMotion FastMCP Server
Implements all required Model Context Protocol tools with real execution logic:
- Reference Management: import, analyze, detect_regions, extract_asset, compare
- Reconstruction: reconstruct, validate, capture_state
- Motion Direction: generate_plan, generate_camera_path, generate_cursor_path, generate_3d_composition, validate
- Scene Management: create, update, preview, validate
- Audio: analyze_beats, align_events
- Rendering: preview, final, status, cancel
- Export: video, project, assets
"""

import os
import json
import uuid
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from pixelmotion.server.fastmcp_compat import FastMCP
from pixelmotion.server.core.config import (
    PROJECTS_DIR,
    RENDERS_DIR,
    DEFAULT_FPS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT
)
from pixelmotion.server.core.models import (
    Project,
    SceneData,
    MotionPlan,
    DetectedRegion,
    CameraKeyframe,
    CursorEvent,
    ThreeDObject,
    CompositionType
)
from pixelmotion.server.core.reference import (
    analyze_reference,
    detect_regions,
    extract_asset,
    compare_images
)
from pixelmotion.server.core.reconstruction import (
    reconstruct_ui,
    validate_reconstruction
)
from pixelmotion.server.core.browser_state import (
    capture_browser_state,
    simulate_interface_state
)
from pixelmotion.server.core.audio_engine import (
    analyze_beats,
    align_internal_events,
    check_typing_budget
)
from pixelmotion.server.core.motion_director import AIMotionDirector
from pixelmotion.server.core.scene_engine import SceneCompositionEngine
from pixelmotion.server.core.renderer import VideoRenderer
from pixelmotion.server.core.visual_qa import VisualQAPipeline
from pixelmotion.server.core.exporter import ExportManager

# Initialize Server & Engines
mcp = FastMCP(
    name="pixelmotion",
    version="1.0.0",
    description="Advanced AI-Powered SaaS Motion Graphics & Product Tutorial Engine"
)

motion_director = AIMotionDirector()
scene_engine = SceneCompositionEngine()
renderer = VideoRenderer()
visual_qa = VisualQAPipeline()
exporter = ExportManager()


def get_or_create_project(project_id: str, name: Optional[str] = None) -> Project:
    proj_dir = PROJECTS_DIR / project_id
    manifest_file = proj_dir / "project.json"
    if manifest_file.exists():
        with open(manifest_file, "r") as f:
            return Project.parse_raw(f.read())

    proj_dir.mkdir(parents=True, exist_ok=True)
    proj = Project(
        project_id=project_id,
        name=name or f"Project {project_id}",
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    with open(manifest_file, "w") as f:
        f.write(proj.json(indent=2))
    return proj


def save_project(proj: Project):
    proj.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    proj_dir = PROJECTS_DIR / proj.project_id
    manifest_file = proj_dir / "project.json"
    with open(manifest_file, "w") as f:
        f.write(proj.json(indent=2))


# ============================================================================
# 1. REFERENCE MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(name="reference_import", description="Imports a reference image, video frame, or UI mockup into a project.")
def reference_import(project_id: str, file_path: str, reference_id: Optional[str] = None) -> Dict[str, Any]:
    proj = get_or_create_project(project_id)
    ref_id = reference_id or f"ref_{uuid.uuid4().hex[:6]}"
    src_p = Path(file_path)
    if not src_p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    dest_dir = PROJECTS_DIR / project_id / "references"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_p = dest_dir / f"{ref_id}_{src_p.name}"

    import shutil
    shutil.copy2(src_p, dest_p)

    analysis = analyze_reference(str(dest_p))
    ref_entry = {
        "reference_id": ref_id,
        "original_path": str(src_p.resolve()),
        "stored_path": str(dest_p.resolve()),
        "analysis": analysis
    }
    proj.references.append(ref_entry)
    save_project(proj)

    return {
        "success": True,
        "project_id": project_id,
        "reference_id": ref_id,
        "stored_path": str(dest_p.resolve()),
        "analysis": analysis
    }


@mcp.tool(name="reference_analyze", description="Analyzes color palette, typography, brightness, and dimensions of a reference.")
def reference_analyze(file_path: str) -> Dict[str, Any]:
    return analyze_reference(file_path)


@mcp.tool(name="reference_detect_regions", description="Uses OpenCV to segment semantic interface regions (cards, tables, buttons, metrics).")
def reference_detect_regions(image_path: str, output_crops_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    regions = detect_regions(image_path, output_crops_dir)
    return [r.dict() for r in regions]


@mcp.tool(name="reference_extract_asset", description="Crops an exact UI component from a reference screenshot.")
def reference_extract_asset(image_path: str, x: int, y: int, width: int, height: int, output_path: str) -> Dict[str, Any]:
    extracted = extract_asset(image_path, x, y, width, height, output_path)
    return {"success": True, "output_path": extracted, "bbox": [x, y, width, height]}


@mcp.tool(name="reference_compare", description="Compares visual fidelity between reference and rendered frame.")
def reference_compare(ref_image_path: str, comp_image_path: str) -> Dict[str, Any]:
    return compare_images(ref_image_path, comp_image_path)


# ============================================================================
# 2. UI RECONSTRUCTION TOOLS
# ============================================================================

@mcp.tool(name="ui_reconstruct", description="Builds a high-fidelity layered reconstruction with locked reference and separated spatial panels.")
def ui_reconstruct(project_id: str, reference_id: str, image_path: str) -> Dict[str, Any]:
    recons = reconstruct_ui(reference_id, image_path, project_id)
    proj = get_or_create_project(project_id)
    proj.reconstructions[reference_id] = recons
    save_project(proj)
    return recons.dict()


@mcp.tool(name="ui_validate", description="Validates that all reconstructed layers and crops are aligned and intact.")
def ui_validate(project_id: str, reference_id: str) -> Dict[str, Any]:
    proj = get_or_create_project(project_id)
    if reference_id not in proj.reconstructions:
        raise ValueError(f"Reconstruction '{reference_id}' not found in project '{project_id}'.")
    return validate_reconstruction(proj.reconstructions[reference_id])


@mcp.tool(name="ui_capture_state", description="Captures real application state using headless Chromium or synthesizes verified state variation.")
def ui_capture_state(
    target_url_or_image: str,
    output_path: str,
    is_live_url: bool = False,
    state_type: str = "active_tab",
    state_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if is_live_url:
        return capture_browser_state(target_url_or_image, output_path)
    else:
        return simulate_interface_state(target_url_or_image, output_path, state_type, state_params or {})


# ============================================================================
# 3. MOTION DIRECTION TOOLS
# ============================================================================

@mcp.tool(name="motion_generate_plan", description="AI Motion Director: Generates a complete structured motion plan for a product video.")
def motion_generate_plan(
    project_id: str,
    product_name: str,
    feature_focus: str,
    narrative_goal: str = "Demonstrate core workflow with cinematic polish",
    duration_seconds: int = 30,
    bpm: float = 120.0,
    reference_id: Optional[str] = None
) -> Dict[str, Any]:
    proj = get_or_create_project(project_id, product_name)
    regions = []
    if reference_id and reference_id in proj.reconstructions:
        regions = proj.reconstructions[reference_id].regions

    plan = motion_director.generate_motion_plan(
        project_id=project_id,
        product_name=product_name,
        feature_focus=feature_focus,
        narrative_goal=narrative_goal,
        target_duration_seconds=duration_seconds,
        fps=proj.fps,
        bpm=bpm,
        reference_id=reference_id,
        detected_regions=regions,
        beats_data=proj.beats_data
    )
    proj.motion_plan = plan
    save_project(proj)
    return plan.dict()


@mcp.tool(name="motion_generate_camera_path", description="Generates a deterministic 3D camera path for dolly, orbit, or spatial tracking.")
def motion_generate_camera_path(
    motion_type: str,
    duration_frames: int,
    target_bbox: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    from pixelmotion.engine_3d.camera_choreography import CameraChoreographer
    choreographer = CameraChoreographer()
    keyframes = choreographer.generatePath(motion_type, duration_frames, target_bbox)
    return keyframes


@mcp.tool(name="motion_generate_cursor_path", description="Generates a tip-anchored cursor trajectory with whip easing and click pause.")
def motion_generate_cursor_path(
    start_x: float,
    start_y: float,
    target_x: float,
    target_y: float,
    start_frame: int,
    reach_frame: int,
    click_duration: int = 14
) -> List[Dict[str, Any]]:
    return [
        {"frame": start_frame, "x": start_x, "y": start_y, "scale": 1.0, "action": "move"},
        {"frame": reach_frame, "x": target_x, "y": target_y, "scale": 1.0, "action": "hover"},
        {"frame": reach_frame + 6, "x": target_x, "y": target_y, "scale": 0.92, "action": "click", "click_duration": click_duration},
        {"frame": reach_frame + 6 + click_duration, "x": target_x, "y": target_y, "scale": 1.0, "action": "move"}
    ]


@mcp.tool(name="motion_generate_3d_composition", description="Configures 3D spatial separation parameters and depth callouts for an interface.")
def motion_generate_3d_composition(
    panel_regions: List[Dict[str, Any]],
    elevation_step: float = 30.0
) -> List[Dict[str, Any]]:
    objects = []
    for idx, r in enumerate(panel_regions):
        objects.append({
            "id": f"panel_{r.get('region_id', idx)}",
            "type": "panel",
            "transform": {
                "x": r.get("x", 0) - 960,
                "y": r.get("y", 0) - 540,
                "z": idx * elevation_step,
                "scale": 1.0
            },
            "depth_extrusion": 25.0 + (idx * 15.0),
            "material": "glass_slate",
            "target_region_id": r.get("region_id")
        })
    return objects


@mcp.tool(name="motion_validate", description="Validates a motion plan against rhythm, typing budgets, and camera stability.")
def motion_validate(project_id: str) -> Dict[str, Any]:
    proj = get_or_create_project(project_id)
    if not proj.motion_plan:
        raise ValueError("No motion plan exists in project.")

    results = []
    for s in proj.motion_plan.scenes:
        val = scene_engine.validate_scene(s)
        results.append(val)

    all_valid = all(r["is_valid"] for r in results)
    return {"all_valid": all_valid, "scene_validations": results}


# ============================================================================
# 4. SCENE MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(name="scene_create", description="Creates a new custom scene within a project's motion plan.")
def scene_create(project_id: str, scene_data: Dict[str, Any]) -> Dict[str, Any]:
    proj = get_or_create_project(project_id)
    if not proj.motion_plan:
        proj.motion_plan = MotionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:6]}",
            project_id=project_id,
            title="Custom Motion Plan",
            target_duration_frames=scene_data.get("duration_frames", 180),
            fps=proj.fps,
            scenes=[]
        )
    scene = SceneData.parse_obj(scene_data)
    proj.motion_plan.scenes.append(scene)
    save_project(proj)
    return scene.dict()


@mcp.tool(name="scene_update", description="Updates an existing scene in a project.")
def scene_update(project_id: str, scene_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    proj = get_or_create_project(project_id)
    if not proj.motion_plan:
        raise ValueError("No motion plan found.")

    found = None
    for i, s in enumerate(proj.motion_plan.scenes):
        if s.scene_id == scene_id:
            s_dict = s.dict()
            s_dict.update(updates)
            proj.motion_plan.scenes[i] = SceneData.parse_obj(s_dict)
            found = proj.motion_plan.scenes[i]
            break

    if not found:
        raise ValueError(f"Scene '{scene_id}' not found.")
    save_project(proj)
    return found.dict()


@mcp.tool(name="scene_preview", description="Compiles a scene into standalone HTML for instant visual preview.")
def scene_preview(project_id: str, scene_id: str) -> Dict[str, Any]:
    proj = get_or_create_project(project_id)
    if not proj.motion_plan:
        raise ValueError("Project has no motion plan.")
    scene = next((s for s in proj.motion_plan.scenes if s.scene_id == scene_id), None)
    if not scene:
        raise ValueError(f"Scene '{scene_id}' not found.")

    ref_img_path = None
    if scene.reference_id and scene.reference_id in proj.reconstructions:
        ref_img_path = proj.reconstructions[scene.reference_id].locked_reference_path

    html_content = scene_engine.compile_scene_html(
        scene=scene,
        reference_image_url=f"file://{Path(ref_img_path).resolve()}" if ref_img_path else None
    )

    out_file = PROJECTS_DIR / project_id / f"preview_{scene_id}.html"
    with open(out_file, "w") as f:
        f.write(html_content)

    return {
        "scene_id": scene_id,
        "preview_html_path": str(out_file.resolve()),
        "duration_frames": scene.duration_frames,
        "composition": scene.composition.value
    }


@mcp.tool(name="scene_validate", description="Validates scene keyframes, cursor events, and duration boundaries.")
def scene_validate(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    scene = SceneData.parse_obj(scene_data)
    return scene_engine.validate_scene(scene)


# ============================================================================
# 5. AUDIO & BEAT TOOLS
# ============================================================================

@mcp.tool(name="audio_analyze_beats", description="Detects BPM, kicks, snares, and recommended scene cuts from audio.")
def audio_analyze_beats(audio_file_path: str, fps: int = 30) -> Dict[str, Any]:
    return analyze_beats(audio_file_path, fps=fps)


@mcp.tool(name="audio_align_events", description="Nudges internal scene events onto musical beats within ±6 frames.")
def audio_align_events(events: List[Dict[str, Any]], beats_data: Dict[str, Any], max_nudge: int = 6) -> List[Dict[str, Any]]:
    return align_internal_events(events, beats_data, max_nudge_frames=max_nudge)


# ============================================================================
# 6. RENDERING & QA TOOLS
# ============================================================================

@mcp.tool(name="render_preview", description="Renders a low-resolution fast preview MP4 (960x540) for a scene.")
def render_preview(project_id: str, scene_id: str) -> Dict[str, Any]:
    preview_info = scene_preview(project_id, scene_id)
    html_path = preview_info["preview_html_path"]
    duration = preview_info["duration_frames"]

    job_id = f"job_prev_{uuid.uuid4().hex[:6]}"
    out_mp4 = RENDERS_DIR / f"preview_{project_id}_{scene_id}.mp4"

    job = renderer.render_scene(
        scene_html_path=html_path,
        output_mp4_path=str(out_mp4.resolve()),
        job_id=job_id,
        project_id=project_id,
        duration_frames=duration,
        fps=30,
        width=960,
        height=540,
        preview_mode=True
    )
    return job.dict()


@mcp.tool(name="render_final", description="Renders a high-definition 1080p master MP4 for a scene or complete project.")
def render_final(project_id: str, scene_id: str, audio_path: Optional[str] = None) -> Dict[str, Any]:
    preview_info = scene_preview(project_id, scene_id)
    html_path = preview_info["preview_html_path"]
    duration = preview_info["duration_frames"]

    job_id = f"job_master_{uuid.uuid4().hex[:6]}"
    out_mp4 = RENDERS_DIR / f"master_{project_id}_{scene_id}.mp4"

    job = renderer.render_scene(
        scene_html_path=html_path,
        output_mp4_path=str(out_mp4.resolve()),
        job_id=job_id,
        project_id=project_id,
        duration_frames=duration,
        fps=30,
        width=1920,
        height=1080,
        preview_mode=False,
        audio_path=audio_path
    )
    return job.dict()


@mcp.tool(name="render_status", description="Retrieves progress and status of an active render job.")
def render_status(job_id: str) -> Dict[str, Any]:
    job = renderer.get_job(job_id)
    if not job:
        raise ValueError(f"Render job '{job_id}' not found.")
    return job.dict()


@mcp.tool(name="render_cancel", description="Cancels an active render job.")
def render_cancel(job_id: str) -> Dict[str, Any]:
    success = renderer.cancel_job(job_id)
    return {"job_id": job_id, "cancelled": success}


# ============================================================================
# 7. EXPORT MANAGEMENT TOOLS
# ============================================================================

@mcp.tool(name="export_video", description="Exports video with optimization presets (hd_1080p, 4k_master, social_9_16, web_optimized).")
def export_video(input_mp4: str, output_path: str, preset: str = "hd_1080p") -> Dict[str, Any]:
    return exporter.export_video(input_mp4, output_path, preset=preset)


@mcp.tool(name="export_project", description="Packages complete editable project into a ZIP bundle.")
def export_project(project_id: str, output_zip_path: str) -> Dict[str, Any]:
    zip_path = exporter.export_project_bundle(project_id, output_zip_path)
    return {"project_id": project_id, "bundle_path": zip_path}


@mcp.tool(name="export_assets", description="Extracts and bundles all UI assets and crops into a zip file.")
def export_assets(project_id: str, output_zip_path: str) -> Dict[str, Any]:
    zip_path = exporter.export_assets_bundle(project_id, output_zip_path)
    return {"project_id": project_id, "assets_bundle": zip_path}


# Also register dot-notated tool aliases so clients supporting standard MCP dots work seamlessly:
tools_to_alias = [
    ("reference.import", reference_import),
    ("reference.analyze", reference_analyze),
    ("reference.detect_regions", reference_detect_regions),
    ("reference.extract_asset", reference_extract_asset),
    ("reference.compare", reference_compare),
    ("ui.reconstruct", ui_reconstruct),
    ("ui.validate", ui_validate),
    ("ui.capture_state", ui_capture_state),
    ("motion.generate_plan", motion_generate_plan),
    ("motion.generate_camera_path", motion_generate_camera_path),
    ("motion.generate_cursor_path", motion_generate_cursor_path),
    ("motion.generate_3d_composition", motion_generate_3d_composition),
    ("motion.validate", motion_validate),
    ("scene.create", scene_create),
    ("scene.update", scene_update),
    ("scene.preview", scene_preview),
    ("scene.validate", scene_validate),
    ("audio.analyze_beats", audio_analyze_beats),
    ("audio.align_events", audio_align_events),
    ("render.preview", render_preview),
    ("render.final", render_final),
    ("render.status", render_status),
    ("render.cancel", render_cancel),
    ("export.video", export_video),
    ("export.project", export_project),
    ("export.assets", export_assets),
]

for alias_name, fn in tools_to_alias:
    mcp.add_tool(fn, name=alias_name)


if __name__ == "__main__":
    import sys
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1].startswith("--transport="):
        transport = sys.argv[1].split("=")[1]
    mcp.run(transport=transport)
