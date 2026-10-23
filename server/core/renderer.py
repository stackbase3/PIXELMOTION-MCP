"""
PixelMotion Deterministic Frame-by-Frame Renderer & FFmpeg Encoder
Executes frame-accurate Chromium rendering:
- Converts HTML to base64 data:text/html URIs for policy compliance
- Supports low-resolution previews (e.g. 960x540) and high-fidelity 1080p masters
- Employs deterministic window.renderFrame(n) loop without setTimeout race conditions
- Encodes MP4 using libx264 with proper yuv420p color matrix and even dimension padding
- Synchronizes audio track and sound cues
"""

import os
import time
import base64
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pixelmotion.server.core.config import (
    CHROMIUM_PATH,
    FFMPEG_PATH,
    RENDERS_DIR,
    DEFAULT_FPS,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT
)
from pixelmotion.server.core.models import RenderJob, SceneData


class VideoRenderer:
    def __init__(self):
        self.active_jobs: Dict[str, RenderJob] = {}

    def get_job(self, job_id: str) -> Optional[RenderJob]:
        return self.active_jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self.active_jobs:
            self.active_jobs[job_id].status = "cancelled"
            return True
        return False

    def render_scene(
        self,
        scene_html_path: str,
        output_mp4_path: str,
        job_id: str,
        project_id: str,
        duration_frames: int,
        fps: int = 30,
        width: int = 1920,
        height: int = 1080,
        preview_mode: bool = False,
        audio_path: Optional[str] = None,
        progress_callback: Optional[Callable[[float, int, int], None]] = None
    ) -> RenderJob:
        """Renders scene HTML to MP4 synchronously with progress updates."""
        job = RenderJob(
            job_id=job_id,
            project_id=project_id,
            status="rendering",
            progress=0.0,
            current_frame=0,
            total_frames=duration_frames,
            preview_mode=preview_mode,
            output_path=output_mp4_path,
            fps=fps,
            width=width,
            height=height,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        self.active_jobs[job_id] = job

        work_dir = Path("/tmp") / f"frames_{job_id}"
        work_dir.mkdir(parents=True, exist_ok=True)

        options = Options()
        options.binary_location = CHROMIUM_PATH
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--disable-gpu")

        driver = None
        try:
            with open(scene_html_path, "r", encoding="utf-8") as f:
                html_raw = f.read()
            b64_html = base64.b64encode(html_raw.encode("utf-8")).decode("utf-8")
            data_url = f"data:text/html;base64,{b64_html}"

            driver = webdriver.Chrome(options=options)
            driver.set_window_size(width, height)
            driver.get(data_url)
            time.sleep(0.5)

            step = 2 if preview_mode else 1
            render_frames = list(range(0, duration_frames, step))
            total_render_frames = len(render_frames)

            for idx, f in enumerate(render_frames):
                if job.status == "cancelled":
                    raise InterruptedError("Render cancelled by user.")

                driver.execute_script("window.renderFrame(arguments[0]);", f)
                frame_png_path = work_dir / f"frame_{idx:05d}.png"
                driver.save_screenshot(str(frame_png_path))

                job.current_frame = f
                job.progress = round((idx + 1) / float(total_render_frames), 3)
                if progress_callback:
                    progress_callback(job.progress, idx + 1, total_render_frames)

            driver.quit()
            driver = None

            # Verify frames exist
            captured_pngs = sorted(work_dir.glob("frame_*.png"))
            if not captured_pngs:
                raise RuntimeError(f"No frames were captured into {work_dir}")

            effective_fps = fps // 2 if preview_mode else fps
            out_p = Path(output_mp4_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                FFMPEG_PATH,
                "-y",
                "-framerate", str(effective_fps),
                "-i", str(work_dir / "frame_%05d.png")
            ]

            if audio_path and Path(audio_path).exists():
                cmd.extend(["-i", str(Path(audio_path).resolve()), "-c:a", "aac", "-shortest"])

            cmd.extend([
                "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18" if not preview_mode else "24",
                "-preset", "fast",
                str(out_p.resolve())
            ])

            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg failed (code {res.returncode}): {res.stderr}")

            job.status = "completed"
            job.progress = 1.0
            job.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            return job

        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            return job

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            if work_dir.exists():
                try:
                    shutil.rmtree(work_dir)
                except Exception:
                    pass
