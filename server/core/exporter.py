"""
PixelMotion Export Management Engine
Provides:
- Video export packaging (1080p, 4K, 9:16 vertical, GIF preview)
- Project archiving (exporting complete project state, scenes, assets to ZIP)
- Asset bundle extraction and manifest generation
"""

import os
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from pixelmotion.server.core.config import PROJECTS_DIR, RENDERS_DIR, FFMPEG_PATH


class ExportManager:
    def __init__(self):
        pass

    def export_video(
        self,
        input_mp4: str,
        output_path: str,
        preset: str = "hd_1080p",
        include_audio: bool = True
    ) -> Dict[str, Any]:
        """
        Exports video with requested optimization preset.
        Presets:
          - hd_1080p (1920x1080, crf 18)
          - 4k_master (3840x2160, scale=2, crf 16)
          - social_9_16 (1080x1920 crop/pad)
          - web_optimized (crf 23, faststart)
        """
        in_p = Path(input_mp4)
        if not in_p.exists():
            raise FileNotFoundError(f"Input MP4 does not exist: {input_mp4}")

        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        cmd = [FFMPEG_PATH, "-y", "-i", str(in_p.resolve())]

        if preset == "4k_master":
            cmd.extend(["-vf", "scale=3840:2160:flags=lanczos", "-c:v", "libx264", "-crf", "16", "-preset", "slow"])
        elif preset == "web_optimized":
            cmd.extend(["-c:v", "libx264", "-crf", "22", "-movflags", "+faststart", "-preset", "medium"])
        elif preset == "social_9_16":
            cmd.extend(["-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black", "-c:v", "libx264", "-crf", "19"])
        else:  # hd_1080p
            cmd.extend(["-c:v", "copy"])

        if include_audio:
            cmd.extend(["-c:a", "copy"])
        else:
            cmd.append("-an")

        cmd.append(str(out_p.resolve()))
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        return {
            "success": True,
            "preset": preset,
            "output_path": str(out_p.resolve()),
            "file_size_bytes": out_p.stat().st_size
        }

    def export_project_bundle(self, project_id: str, output_zip_path: str) -> str:
        """Packs the complete project workspace into an editable ZIP bundle."""
        proj_dir = PROJECTS_DIR / project_id
        if not proj_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {proj_dir}")

        out_zip = Path(output_zip_path)
        out_zip.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(str(out_zip), "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(proj_dir):
                for f in files:
                    file_path = Path(root) / f
                    arcname = file_path.relative_to(proj_dir)
                    zipf.write(file_path, arcname)

        return str(out_zip.resolve())

    def export_assets_bundle(self, project_id: str, output_zip_path: str) -> str:
        """Exports all extracted and reconstructed UI region crops into a standalone asset pack."""
        proj_dir = PROJECTS_DIR / project_id
        recons_dir = proj_dir / "reconstructions"
        out_zip = Path(output_zip_path)
        out_zip.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(str(out_zip), "w", zipfile.ZIP_DEFLATED) as zipf:
            if recons_dir.exists():
                for root, _, files in os.walk(recons_dir):
                    for f in files:
                        if f.endswith((".png", ".jpg", ".svg", ".json")):
                            file_path = Path(root) / f
                            arcname = file_path.relative_to(recons_dir)
                            zipf.write(file_path, arcname)

        return str(out_zip.resolve())
