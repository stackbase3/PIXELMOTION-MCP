"""
PixelMotion Core Models & Data Schemas
Validated Pydantic models for scenes, motion direction, 3D composition, camera choreography, and QA.
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class CompositionType(str, Enum):
    CINEMATIC_OPENER = "cinematic_opener"
    DIMENSIONAL_REVEAL = "dimensional_reveal"
    FLAT_WALKTHROUGH = "flat_walkthrough"
    SPATIAL_FEATURE_SPOTLIGHT = "spatial_feature_spotlight"
    FLOATING_PANELS = "floating_panels"
    DATA_VIZ = "animated_data_viz"
    CURSOR_GUIDED = "cursor_guided_interaction"
    MACRO_SHOT = "interface_macro_shot"
    CAMERA_THROUGH = "camera_through_dashboard"
    LAYERED_ASSEMBLY = "layered_dashboard_assembly"
    FEATURE_COMPARISON = "feature_comparison"
    UI_TO_3D = "ui_to_3d_transformation"
    THREE_D_TO_UI = "3d_to_ui_transformation"
    FULL_SCREEN_DEMO = "full_screen_interface_demo"
    NARRATIVE_TITLE = "narrative_title_sequence"
    CLOSING_SCENE = "closing_product_presentation"


class NarrativeBeatType(str, Enum):
    HOOK = "hook"
    PROBLEM_SETUP = "problem_setup"
    INTERFACE_EMERGENCE = "interface_emergence"
    FEATURE_SPOTLIGHT = "feature_spotlight"
    WORKFLOW_WALKTHROUGH = "workflow_walkthrough"
    QUANTITATIVE_PROOF = "quantitative_proof"
    SYNTHESIS = "synthesis"
    CALL_TO_ACTION = "call_to_action"


class MotionType(str, Enum):
    DOLLY_IN = "dolly_in"
    DOLLY_OUT = "dolly_out"
    ORBIT = "orbit"
    PAN = "pan"
    MATCH_CUT = "match_cut"
    STATIC = "static"
    SPATIAL_TRACKING = "spatial_tracking"


class TransitionType(str, Enum):
    SPATIAL_PANEL_SEPARATION = "spatial_panel_separation"
    CAMERA_THROUGH = "camera_through_interface"
    PERSPECTIVE_TO_FLAT = "perspective_to_flat"
    CARD_ROTATION = "3d_card_rotation"
    DEPTH_REVEAL = "depth_based_reveal"
    LAYERED_ASSEMBLY = "layered_interface_assembly"
    DIMENSIONAL_COLLAPSE = "dimensional_collapse"
    MASK_REVEAL = "mask_reveal"
    IRIS_REVEAL = "iris_reveal"
    CUT = "hard_cut"


class PreservationStrategy(str, Enum):
    CODE_INSPECTION = "code_inspection"
    DOM_RECONSTRUCTION = "dom_reconstruction"
    CROPPED_ORIGINAL = "cropped_original"
    LOCKED_SCREENSHOT = "locked_screenshot"


class VisualDirectionProfile(BaseModel):
    camera_language: str = "cinematic_restrained"
    scene_pacing: str = "snare_locked"
    transition_style: str = "spatial_perspective_shift"
    typography: str = "clean_sans"
    composition: str = "golden_ratio_depth"
    depth_level: float = 0.65
    lighting: str = "soft_studio_directional"
    motion_intensity: float = 0.70
    interface_treatment: str = "crisp_pixel_perfect"
    primary_accent: str = "#2563EB"
    palette: List[str] = Field(default_factory=lambda: ["#0F172A", "#1E293B", "#38BDF8", "#10B981", "#F59E0B"])
    font_stack: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"


class DetectedRegion(BaseModel):
    region_id: str
    label: str
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    z_index: int = 0
    parent_id: Optional[str] = None
    is_interactive: bool = False
    crop_path: Optional[str] = None
    color_profile: Optional[Dict[str, Any]] = None
    text_content: Optional[str] = None


class UIReconstruction(BaseModel):
    reference_id: str
    source_path: str
    dimensions: List[int] = Field(default_factory=lambda: [1920, 1080])
    fidelity_score: float = 1.0
    preservation_strategy: PreservationStrategy = PreservationStrategy.LOCKED_SCREENSHOT
    locked_reference_path: str
    regions: List[DetectedRegion] = Field(default_factory=list)
    html_markup: Optional[str] = None
    css_styles: Optional[str] = None


class CameraKeyframe(BaseModel):
    frame: int
    x: float = 0.0
    y: float = 0.0
    z: float = 800.0
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    fov: float = 45.0
    easing: str = "standard"


class CameraPath(BaseModel):
    keyframes: List[CameraKeyframe] = Field(default_factory=list)
    target: Optional[List[float]] = None
    motion_type: MotionType = MotionType.STATIC


class CursorEvent(BaseModel):
    frame: int
    x: float
    y: float
    scale: float = 1.0
    action: str = "move"  # move, click, hover, drag, scroll
    target_region_id: Optional[str] = None
    click_duration: int = 14
    text: Optional[str] = None


class ThreeDObjectTransform(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotate_x: float = 0.0
    rotate_y: float = 0.0
    rotate_z: float = 0.0
    scale: float = 1.0


class ThreeDObject(BaseModel):
    id: str
    type: str  # panel, card, callout, connector, highlight_frame, grid, light
    transform: ThreeDObjectTransform = Field(default_factory=ThreeDObjectTransform)
    target_region_id: Optional[str] = None
    material: str = "matte_glass"
    opacity: float = 1.0
    color: Optional[str] = None
    border_radius: float = 8.0
    depth_extrusion: float = 4.0
    properties: Dict[str, Any] = Field(default_factory=dict)


class TransitionSpec(BaseModel):
    type: TransitionType = TransitionType.PERSPECTIVE_TO_FLAT
    duration_frames: int = 24
    direction: str = "left-to-right"
    easing: str = "slowInLand"
    params: Dict[str, Any] = Field(default_factory=dict)


class OverlaySpec(BaseModel):
    type: str  # title, badge, callout, counter, subtitle, typing
    text: str
    x: float
    y: float
    start_frame: int
    duration_frames: int
    style: Dict[str, Any] = Field(default_factory=dict)


class AudioEvent(BaseModel):
    frame: int
    type: str  # kick, snare, beat, sfx, voiceover
    name: str
    duration_frames: int = 10


class SceneData(BaseModel):
    scene_id: str
    duration_frames: int = 180
    fps: int = 30
    composition: CompositionType = CompositionType.DIMENSIONAL_REVEAL
    reference_id: Optional[str] = None
    narrative_beat: NarrativeBeatType = NarrativeBeatType.INTERFACE_EMERGENCE
    scene_objective: str = "Reveal the core dashboard in dimensional perspective"
    ui_layers: List[str] = Field(default_factory=list)
    camera: CameraPath = Field(default_factory=CameraPath)
    cursor_events: List[CursorEvent] = Field(default_factory=list)
    motion_events: List[Dict[str, Any]] = Field(default_factory=list)
    three_d_objects: List[ThreeDObject] = Field(default_factory=list)
    overlays: List[OverlaySpec] = Field(default_factory=list)
    audio_events: List[AudioEvent] = Field(default_factory=list)
    transition: Optional[TransitionSpec] = None


class MotionPlan(BaseModel):
    plan_id: str
    project_id: str
    title: str
    target_duration_frames: int
    fps: int = 30
    bpm: float = 120.0
    scenes: List[SceneData] = Field(default_factory=list)
    visual_direction: VisualDirectionProfile = Field(default_factory=VisualDirectionProfile)
    director_rationale: str = ""


class VisualQAReport(BaseModel):
    project_id: str
    scene_id: Optional[str] = None
    overall_status: str = "pass"  # pass, warning, fail
    fidelity_score: float = 1.0
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    checks: Dict[str, bool] = Field(default_factory=lambda: {
        "ui_alignment": True,
        "cropping_accuracy": True,
        "text_legibility": True,
        "camera_framing": True,
        "cursor_accuracy": True,
        "audio_sync": True,
        "rendering_integrity": True
    })
    recommendations: List[str] = Field(default_factory=list)


class RenderJob(BaseModel):
    job_id: str
    project_id: str
    scene_id: Optional[str] = None
    status: str = "pending"  # pending, rendering, completed, failed, cancelled
    progress: float = 0.0
    current_frame: int = 0
    total_frames: int = 0
    preview_mode: bool = False
    output_path: Optional[str] = None
    fps: int = 30
    width: int = 1920
    height: int = 1080
    error: Optional[str] = None
    created_at: str = ""
    completed_at: Optional[str] = None


class Project(BaseModel):
    project_id: str
    name: str
    aspect_ratio: str = "16:9"
    fps: int = 30
    width: int = 1920
    height: int = 1080
    created_at: str = ""
    updated_at: str = ""
    references: List[Dict[str, Any]] = Field(default_factory=list)
    reconstructions: Dict[str, UIReconstruction] = Field(default_factory=dict)
    motion_plan: Optional[MotionPlan] = None
    audio_path: Optional[str] = None
    beats_data: Optional[Dict[str, Any]] = None
    render_jobs: List[RenderJob] = Field(default_factory=list)
    qa_reports: List[VisualQAReport] = Field(default_factory=list)
