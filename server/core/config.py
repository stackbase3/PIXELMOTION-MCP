"""
PixelMotion Engine Configuration
Centralizes workspace paths, default settings, and storage locations.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
RENDERS_DIR = DATA_DIR / "renders"
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATES_DIR = BASE_DIR / "remotion_templates"
ENGINE_3D_DIR = BASE_DIR / "engine_3d"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_FPS = 30
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_ASPECT = "16:9"

CHROMIUM_PATH = "/usr/bin/chromium"
FFMPEG_PATH = "/usr/bin/ffmpeg"
