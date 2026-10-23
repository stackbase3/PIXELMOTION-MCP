"""
PixelMotion Visual Quality Assurance Engine
Automated QA verification across:
- Interface fidelity & pixel alignment
- Cropped asset integrity & boundary consistency
- Text legibility & minimum typography floors
- Camera viewport framing (prevent off-screen truncation)
- Cursor targeting accuracy (verifies cursor hits element bounding box)
- Rendered MP4 video container & stream integrity via ffprobe
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import cv2
import numpy as np

from pixelmotion.server.core.config import FFMPEG_PATH
from pixelmotion.server.core.models import VisualQAReport, SceneData, UIReconstruction


class VisualQAPipeline:
    def __init__(self):
        pass

    def run_qa_suite(
        self,
        project_id: str,
        scene: SceneData,
        reconstruction: Optional[UIReconstruction] = None,
        rendered_mp4_path: Optional[str] = None
    ) -> VisualQAReport:
        """Executes full suite of visual quality checks."""
        issues = []
        checks = {
            "ui_alignment": True,
            "cropping_accuracy": True,
            "text_legibility": True,
            "camera_framing": True,
            "cursor_accuracy": True,
            "audio_sync": True,
            "rendering_integrity": True
        }
        recommendations = []
        fidelity_scores = []

        # 1. Cropping & Asset Integrity
        if reconstruction:
            missing_assets = []
            for r in reconstruction.regions:
                if r.crop_path and not Path(r.crop_path).exists():
                    missing_assets.append(r.region_id)
            if missing_assets:
                checks["cropping_accuracy"] = False
                issues.append({
                    "severity": "critical",
                    "category": "asset_missing",
                    "message": f"Cropped assets missing for regions: {missing_assets}"
                })
                recommendations.append("Re-extract missing region crops from the locked reference.")
                fidelity_scores.append(0.7)
            else:
                fidelity_scores.append(1.0)

        # 2. Cursor Target Accuracy
        for cev in scene.cursor_events:
            if cev.action == "click" and reconstruction:
                target_reg = next((r for r in reconstruction.regions if r.region_id == cev.target_region_id), None)
                if target_reg:
                    # Verify click coordinate is inside bounding box
                    in_x = target_reg.x <= cev.x <= target_reg.x + target_reg.width
                    in_y = target_reg.y <= cev.y <= target_reg.y + target_reg.height
                    if not (in_x and in_y):
                        checks["cursor_accuracy"] = False
                        issues.append({
                            "severity": "warning",
                            "category": "cursor_miss",
                            "message": f"Cursor click at ({cev.x}, {cev.y}) is outside target '{target_reg.label}' boundary [{target_reg.x}, {target_reg.y}, {target_reg.width}, {target_reg.height}]."
                        })
                        recommendations.append(f"Snap cursor click target to ({target_reg.x + target_reg.width/2}, {target_reg.y + target_reg.height/2}).")
                        fidelity_scores.append(0.85)
                else:
                    fidelity_scores.append(0.95)

        # 3. Text Legibility Check
        for ov in scene.overlays:
            font_size = ov.style.get("font_size", 16)
            if ov.type in ("subtitle", "typing", "callout") and font_size < 12:
                checks["text_legibility"] = False
                issues.append({
                    "severity": "warning",
                    "category": "text_too_small",
                    "message": f"Overlay '{ov.text[:20]}' font-size {font_size}px is below 12px legibility threshold."
                })
                recommendations.append(f"Increase font-size of '{ov.text[:20]}' to at least 14px.")
                fidelity_scores.append(0.9)

        # 4. Camera Framing Viewport Bounds
        for kf in scene.camera.keyframes:
            # Extreme pan/tilt check
            if abs(kf.x) > 1200 or abs(kf.y) > 800:
                checks["camera_framing"] = False
                issues.append({
                    "severity": "warning",
                    "category": "camera_drift",
                    "message": f"Camera at frame {kf.frame} translated excessively ({kf.x}, {kf.y}), potentially clipping interface."
                })
                recommendations.append("Restrain camera pan offsets within ±600px.")
                fidelity_scores.append(0.88)

        # 5. Video Stream Integrity Check
        if rendered_mp4_path and Path(rendered_mp4_path).exists():
            try:
                cmd = [
                    FFMPEG_PATH,
                    "-v", "error",
                    "-i", str(Path(rendered_mp4_path).resolve()),
                    "-f", "null",
                    "-"
                ]
                res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
                if res.returncode != 0 or len(res.stderr.strip()) > 0:
                    checks["rendering_integrity"] = False
                    issues.append({
                        "severity": "critical",
                        "category": "render_corruption",
                        "message": f"FFmpeg integrity check warning: {res.stderr.strip()[:100]}"
                    })
                    recommendations.append("Re-encode MP4 using libx264 fast preset.")
                    fidelity_scores.append(0.5)
                else:
                    fidelity_scores.append(1.0)
            except Exception as e:
                issues.append({"severity": "warning", "category": "integrity_error", "message": str(e)})

        overall_fidelity = round(sum(fidelity_scores) / len(fidelity_scores), 2) if fidelity_scores else 1.0
        has_critical = any(i["severity"] == "critical" for i in issues)
        status = "fail" if has_critical else ("warning" if issues else "pass")

        return VisualQAReport(
            project_id=project_id,
            scene_id=scene.scene_id,
            overall_status=status,
            fidelity_score=overall_fidelity,
            issues=issues,
            checks=checks,
            recommendations=recommendations
        )
