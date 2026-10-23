"""
PixelMotion AI Motion Director
Synthesizes structured, art-directed motion production plans based on:
- Product identity and feature being explained
- Interface geometry and detected semantic regions
- Narrative beats (Hook -> Spatial Emergence -> 3D Spotlight -> Flat Walkthrough -> Proof -> Finale)
- Soundtrack beats and snare alignment
- Purposeful composition selection (restrained, no childish bouncing or gratuitous 3D)
"""

import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path

from pixelmotion.server.core.models import (
    MotionPlan,
    SceneData,
    CompositionType,
    NarrativeBeatType,
    MotionType,
    TransitionType,
    CameraPath,
    CameraKeyframe,
    CursorEvent,
    ThreeDObject,
    ThreeDObjectTransform,
    TransitionSpec,
    OverlaySpec,
    AudioEvent,
    DetectedRegion,
    VisualDirectionProfile
)


class AIMotionDirector:
    def __init__(self):
        pass

    def generate_motion_plan(
        self,
        project_id: str,
        product_name: str,
        feature_focus: str,
        narrative_goal: str = "Demonstrate core workflow with cinematic polish",
        target_duration_seconds: int = 30,
        duration_seconds: Optional[int] = None,
        fps: int = 30,
        bpm: float = 120.0,
        reference_id: Optional[str] = None,
        detected_regions: Optional[List[DetectedRegion]] = None,
        beats_data: Optional[Dict[str, Any]] = None
    ) -> MotionPlan:
        """
        Creates an end-to-end art-directed production plan with 5-6 purposeful scenes.
        """
        effective_duration_sec = duration_seconds if duration_seconds is not None else target_duration_seconds
        regions = detected_regions or []
        chart_region = next((r for r in regions if "chart" in r.label or "kpi" in r.label), None)
        button_region = next((r for r in regions if r.is_interactive), None)

        frames_per_beat = round(fps * 60.0 / bpm)
        bars_4 = frames_per_beat * 16  # ~4 bars at 120bpm = 60 frames * 4 = 240 frames (~8s)
        bars_2 = frames_per_beat * 8   # ~2 bars (~4s)

        scenes: List[SceneData] = []
        current_frame = 0

        # --- Scene 1: Cinematic Product Opener ---
        s1_duration = bars_2
        s1 = SceneData(
            scene_id="scene_01_cinematic_opener",
            duration_frames=s1_duration,
            fps=fps,
            composition=CompositionType.CINEMATIC_OPENER,
            reference_id=reference_id,
            narrative_beat=NarrativeBeatType.HOOK,
            scene_objective=f"Establish premium product identity for {product_name}",
            camera=CameraPath(
                motion_type=MotionType.DOLLY_IN,
                keyframes=[
                    CameraKeyframe(frame=0, x=0, y=0, z=300, pitch=14, yaw=-16, fov=45, easing="slowInLand"),
                    CameraKeyframe(frame=s1_duration, x=0, y=0, z=140, pitch=8, yaw=-6, fov=45, easing="soft")
                ]
            ),
            overlays=[
                OverlaySpec(
                    type="title",
                    text=f"{product_name}",
                    x=960,
                    y=480,
                    start_frame=15,
                    duration_frames=s1_duration - 20,
                    style={"font_size": 48, "font_weight": 700, "color": "#FFFFFF", "letter_spacing": "-0.02em"}
                ),
                OverlaySpec(
                    type="subtitle",
                    text=f"Next-Generation {feature_focus}",
                    x=960,
                    y=550,
                    start_frame=30,
                    duration_frames=s1_duration - 35,
                    style={"font_size": 22, "font_weight": 400, "color": "#38BDF8"}
                )
            ],
            audio_events=[
                AudioEvent(frame=0, type="kick", name="impact_kick", duration_frames=12),
                AudioEvent(frame=round(s1_duration * 0.5), type="snare", name="phrase_snare", duration_frames=8)
            ],
            transition=TransitionSpec(
                type=TransitionType.SPATIAL_PANEL_SEPARATION,
                duration_frames=24,
                easing="violentPush"
            )
        )
        scenes.append(s1)
        current_frame += s1_duration

        # --- Scene 2: Dimensional Dashboard Reveal ---
        s2_duration = bars_2 + 30
        s2_3d_objects = []
        if regions:
            for idx, r in enumerate(regions[:4]):
                s2_3d_objects.append(
                    ThreeDObject(
                        id=f"panel_{r.region_id}",
                        type="panel",
                        transform=ThreeDObjectTransform(x=r.x - 960, y=r.y - 540, z=idx * 25, scale=1.0),
                        target_region_id=r.region_id,
                        depth_extrusion=30 + (idx * 15),
                        material="glass_slate"
                    )
                )

        s2 = SceneData(
            scene_id="scene_02_dimensional_reveal",
            duration_frames=s2_duration,
            fps=fps,
            composition=CompositionType.DIMENSIONAL_REVEAL,
            reference_id=reference_id,
            narrative_beat=NarrativeBeatType.INTERFACE_EMERGENCE,
            scene_objective="Present the complete interface architecture as layered spatial tiers",
            camera=CameraPath(
                motion_type=MotionType.ORBIT,
                keyframes=[
                    CameraKeyframe(frame=0, x=-40, y=20, z=120, pitch=12, yaw=-14, fov=46, easing="slowInLand"),
                    CameraKeyframe(frame=s2_duration, x=20, y=-10, z=60, pitch=6, yaw=-4, fov=44, easing="soft")
                ]
            ),
            three_d_objects=s2_3d_objects,
            audio_events=[
                AudioEvent(frame=0, type="snare", name="layer_split_snare", duration_frames=10)
            ],
            transition=TransitionSpec(
                type=TransitionType.DEPTH_REVEAL,
                duration_frames=20,
                easing="slowInLand"
            )
        )
        scenes.append(s2)
        current_frame += s2_duration

        # --- Scene 3: 3D Spatial Feature Spotlight ---
        s3_duration = bars_2 + 30
        spotlight_x = chart_region.x if chart_region else 700
        spotlight_y = chart_region.y if chart_region else 300
        spotlight_w = chart_region.width if chart_region else 600
        spotlight_h = chart_region.height if chart_region else 350

        s3 = SceneData(
            scene_id="scene_03_feature_spotlight",
            duration_frames=s3_duration,
            fps=fps,
            composition=CompositionType.SPATIAL_FEATURE_SPOTLIGHT,
            reference_id=reference_id,
            narrative_beat=NarrativeBeatType.FEATURE_SPOTLIGHT,
            scene_objective=f"Spotlight {feature_focus} with elevated dimensional focus and callouts",
            camera=CameraPath(
                motion_type=MotionType.SPATIAL_TRACKING,
                keyframes=[
                    CameraKeyframe(frame=0, x=0, y=0, z=80, pitch=8, yaw=-6, fov=45, easing="slowInLand"),
                    CameraKeyframe(frame=round(s3_duration * 0.4), x=spotlight_x - 960 + spotlight_w / 2, y=spotlight_y - 540 + spotlight_h / 2, z=-30, pitch=3, yaw=-2, fov=42, easing="standard"),
                    CameraKeyframe(frame=s3_duration, x=spotlight_x - 960 + spotlight_w / 2, y=spotlight_y - 540 + spotlight_h / 2, z=-40, pitch=1, yaw=0, fov=40, easing="soft")
                ]
            ),
            three_d_objects=[
                ThreeDObject(
                    id="spotlight_card",
                    type="card",
                    transform=ThreeDObjectTransform(x=spotlight_x, y=spotlight_y, z=90, scale=1.04),
                    depth_extrusion=50,
                    material="matte_highlight"
                ),
                ThreeDObject(
                    id="spotlight_callout",
                    type="callout",
                    transform=ThreeDObjectTransform(x=spotlight_x + spotlight_w + 30, y=spotlight_y + 40, z=140),
                    properties={
                        "category": "Live Performance",
                        "title": "Edge Metrics",
                        "description": "Calculates real-time risk-reward ratios and expectancy curve automatically.",
                        "badge": "+18.4% Alpha"
                    }
                )
            ],
            audio_events=[
                AudioEvent(frame=20, type="kick", name="card_elevate_kick", duration_frames=8),
                AudioEvent(frame=60, type="snare", name="callout_pop_snare", duration_frames=8)
            ],
            transition=TransitionSpec(
                type=TransitionType.PERSPECTIVE_TO_FLAT,
                duration_frames=28,
                easing="slowInLand"
            )
        )
        scenes.append(s3)
        current_frame += s3_duration

        # --- Scene 4: Perspective-to-Flat Real Interface Walkthrough ---
        s4_duration = bars_4
        btn_x = button_region.x + button_region.width / 2 if button_region else 960
        btn_y = button_region.y + button_region.height / 2 if button_region else 540

        s4 = SceneData(
            scene_id="scene_04_interface_walkthrough",
            duration_frames=s4_duration,
            fps=fps,
            composition=CompositionType.FLAT_WALKTHROUGH,
            reference_id=reference_id,
            narrative_beat=NarrativeBeatType.WORKFLOW_WALKTHROUGH,
            scene_objective="Smoothly transition into the pristine 2D interface and execute verified button interaction",
            camera=CameraPath(
                motion_type=MotionType.STATIC,
                keyframes=[
                    CameraKeyframe(frame=0, x=0, y=0, z=0, pitch=0, yaw=0, fov=45, easing="standard"),
                    CameraKeyframe(frame=s4_duration, x=0, y=0, z=0, pitch=0, yaw=0, fov=45, easing="standard")
                ]
            ),
            cursor_events=[
                CursorEvent(frame=15, x=1920 + 40, y=1080 + 40, scale=1.0, action="move"),
                CursorEvent(frame=70, x=btn_x, y=btn_y, scale=1.0, action="hover", target_region_id=button_region.region_id if button_region else None),
                CursorEvent(frame=90, x=btn_x, y=btn_y, scale=0.92, action="click", click_duration=14),
                CursorEvent(frame=104, x=btn_x, y=btn_y, scale=1.0, action="move"),
                CursorEvent(frame=160, x=btn_x + 180, y=btn_y + 120, scale=1.0, action="move")
            ],
            overlays=[
                OverlaySpec(
                    type="typing",
                    text="Filter applied: Win-Rate > 65%",
                    x=btn_x,
                    y=btn_y - 48,
                    start_frame=100,
                    duration_frames=100,
                    style={"font_size": 15, "color": "#10B981", "background": "rgba(16, 185, 129, 0.15)"}
                )
            ],
            audio_events=[
                AudioEvent(frame=90, type="sfx", name="ui_click_subtle", duration_frames=6),
                AudioEvent(frame=104, type="snare", name="state_change_snare", duration_frames=8)
            ],
            transition=TransitionSpec(
                type=TransitionType.CAMERA_THROUGH,
                duration_frames=24,
                easing="violentPush"
            )
        )
        scenes.append(s4)
        current_frame += s4_duration

        # --- Scene 5: Animated Data Proof / Outcome ---
        s5_duration = bars_2
        s5 = SceneData(
            scene_id="scene_05_data_proof",
            duration_frames=s5_duration,
            fps=fps,
            composition=CompositionType.DATA_VIZ,
            reference_id=reference_id,
            narrative_beat=NarrativeBeatType.QUANTITATIVE_PROOF,
            scene_objective="Highlight high-impact metric outcome with animated counter overshoot",
            camera=CameraPath(
                motion_type=MotionType.DOLLY_IN,
                keyframes=[
                    CameraKeyframe(frame=0, x=0, y=0, z=100, pitch=4, yaw=0, fov=45, easing="slowInLand"),
                    CameraKeyframe(frame=s5_duration, x=0, y=0, z=20, pitch=0, yaw=0, fov=45, easing="soft")
                ]
            ),
            overlays=[
                OverlaySpec(
                    type="counter",
                    text="Sharpe Ratio: 2.84",
                    x=960,
                    y=520,
                    start_frame=15,
                    duration_frames=s5_duration - 25,
                    style={"font_size": 56, "font_weight": 800, "color": "#38BDF8"}
                ),
                OverlaySpec(
                    type="badge",
                    text="Automated Trade Journaling",
                    x=960,
                    y=440,
                    start_frame=10,
                    duration_frames=s5_duration - 20,
                    style={"font_size": 16, "color": "#94A3B8"}
                )
            ],
            audio_events=[
                AudioEvent(frame=0, type="kick", name="counter_start_kick", duration_frames=8),
                AudioEvent(frame=round(s5_duration * 0.7), type="snare", name="counter_settle_snare", duration_frames=8)
            ],
            transition=TransitionSpec(
                type=TransitionType.DIMENSIONAL_COLLAPSE,
                duration_frames=20,
                easing="slowInLand"
            )
        )
        scenes.append(s5)
        current_frame += s5_duration

        # --- Scene 6: Professional Closing Presentation ---
        s6_duration = bars_2
        s6 = SceneData(
            scene_id="scene_06_closing_scene",
            duration_frames=s6_duration,
            fps=fps,
            composition=CompositionType.CLOSING_SCENE,
            reference_id=reference_id,
            narrative_beat=NarrativeBeatType.CALL_TO_ACTION,
            scene_objective=f"Deliver memorable closing product presentation and call to action for {product_name}",
            camera=CameraPath(
                motion_type=MotionType.STATIC,
                keyframes=[
                    CameraKeyframe(frame=0, x=0, y=0, z=0, pitch=0, yaw=0, fov=45, easing="standard"),
                    CameraKeyframe(frame=s6_duration, x=0, y=0, z=0, pitch=0, yaw=0, fov=45, easing="standard")
                ]
            ),
            overlays=[
                OverlaySpec(
                    type="title",
                    text=f"Experience {product_name}",
                    x=960,
                    y=460,
                    start_frame=15,
                    duration_frames=s6_duration - 20,
                    style={"font_size": 52, "font_weight": 800, "color": "#FFFFFF"}
                ),
                OverlaySpec(
                    type="subtitle",
                    text="Start Journaling Free at YourDomain.com",
                    x=960,
                    y=540,
                    start_frame=30,
                    duration_frames=s6_duration - 35,
                    style={"font_size": 20, "font_weight": 500, "color": "#38BDF8"}
                )
            ],
            audio_events=[
                AudioEvent(frame=15, type="snare", name="finale_snare", duration_frames=12)
            ]
        )
        scenes.append(s6)
        current_frame += s6_duration

        total_frames = current_frame

        plan = MotionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            title=f"{product_name} - {feature_focus} Film",
            target_duration_frames=total_frames,
            fps=fps,
            bpm=bpm,
            scenes=scenes,
            visual_direction=VisualDirectionProfile(
                camera_language="cinematic_restrained",
                scene_pacing=f"snare_locked_{round(bpm)}bpm",
                transition_style="spatial_perspective_shift",
                primary_accent="#38BDF8",
                palette=["#0B0E14", "#161C2A", "#38BDF8", "#10B981", "#6366F1"]
            ),
            director_rationale=(
                f"Art-directed motion sequence balances dimensional visual storytelling with interface fidelity. "
                f"Begins with an elegant 3D spatial reveal to establish scale, moves into a 3D spotlight to isolate '{feature_focus}', "
                f"then smoothly collapses perspective into a pixel-perfect 2D walkthrough with natural cursor click mechanics, "
                f"concluding with data proof and an impactful closing brand mark."
            )
        )
        return plan
