"""
PixelMotion Hyperframes Rendering Adapter
Provides a verified bridge for HTML-driven, zero-dependency declarative motion compositions.

Architecture & Compatibility Analysis:
- Execution Environment: Standalone HTML5/ES6 executed inside Chromium / WebKit
- Rendering Model: Pure deterministic function of normalized time `render(progress)`
- Supported Compositions: Flat walkthroughs, typed text, UI state transitions, counters, SVG reveals
- Constraints: Advanced WebGL/GLSL 3D depth passes are routed through SpatialUIEngine;
  Hyperframes is utilized for lightweight, standalone portable HTML motion artifacts.
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from pixelmotion.server.core.models import SceneData, MotionPlan


class HyperframesAdapter:
    def __init__(self):
        pass

    def can_handle_composition(self, composition_type: str) -> bool:
        """Determines if a composition is suitable for pure HTML/Hyperframes rendering."""
        pure_html_compositions = {
            "flat_walkthrough",
            "cursor_guided_interaction",
            "narrative_title_sequence",
            "animated_data_viz",
            "full_screen_interface_demo",
            "closing_product_presentation"
        }
        return composition_type in pure_html_compositions

    def compile_hyperframe(
        self,
        scene: SceneData,
        output_html_path: str,
        reference_image_path: Optional[str] = None
    ) -> str:
        """
        Compiles a single standalone Hyperframe HTML document with scrubber controls
        and deterministic requestAnimationFrame / frame-accurate capture hook.
        """
        ref_src = f"file://{Path(reference_image_path).resolve()}" if reference_image_path else ""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Hyperframes: {scene.scene_id}</title>
  <style>
    body {{
      margin: 0;
      background: #0B0E14;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      color: #F8FAFC;
      font-family: 'Inter', system-ui, sans-serif;
    }}
    #stage {{
      position: relative;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      background: #10141E;
      transform-origin: center center;
    }}
    .ui-bg {{
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      object-fit: contain;
    }}
    #cursor {{
      position: absolute;
      width: 56px; height: 56px;
      pointer-events: none;
      z-index: 1000;
      filter: drop-shadow(0 3px 6px rgba(0,0,0,0.4));
    }}
    #scrubber-ui {{
      margin-top: 12px;
      display: flex;
      gap: 16px;
      align-items: center;
      background: rgba(30, 41, 59, 0.8);
      padding: 8px 16px;
      border-radius: 8px;
    }}
  </style>
</head>
<body>
  <div id="stage">
    {"<img class='ui-bg' src='" + ref_src + "' />" if ref_src else ""}
    <svg id="cursor" viewBox="0 0 24 24">
      <path d="M4,3 L4,17 L9,13 L12,19 L14,18 L11,12 L17,12 Z"
            fill="#38BDF8" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round" />
    </svg>
    <div id="content-layer"></div>
  </div>

  <div id="scrubber-ui">
    <span>Frame: <strong id="lbl-frame">0</strong> / {scene.duration_frames}</span>
    <input type="range" id="scrubber" min="0" max="{scene.duration_frames}" value="0" style="width: 400px;" />
  </div>

  <script>
    const totalFrames = {scene.duration_frames};
    const cursorEvents = {json.dumps([cev.dict() for cev in scene.cursor_events])};

    function render(frame) {{
      document.getElementById('lbl-frame').innerText = frame;
      const progress = frame / totalFrames;

      // Cursor position interpolation
      const curEl = document.getElementById('cursor');
      if (cursorEvents.length > 0) {{
        let p1 = cursorEvents[0], p2 = cursorEvents[cursorEvents.length - 1];
        for (let i = 0; i < cursorEvents.length - 1; i++) {{
          if (frame >= cursorEvents[i].frame && frame <= cursorEvents[i+1].frame) {{
            p1 = cursorEvents[i];
            p2 = cursorEvents[i+1];
            break;
          }}
        }}
        const span = Math.max(1, p2.frame - p1.frame);
        const subP = (frame - p1.frame) / span;
        const curX = p1.x + (p2.x - p1.x) * subP;
        const curY = p1.y + (p2.y - p1.y) * subP;
        curEl.style.left = curX + 'px';
        curEl.style.top = curY + 'px';
      }}
    }}

    window.renderFrame = render;

    document.getElementById('scrubber').addEventListener('input', (e) => {{
      render(parseInt(e.target.value, 10));
    }});

    render(0);
  </script>
</body>
</html>
"""
        out_p = Path(output_html_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w") as f:
            f.write(html)

        return str(out_p.resolve())
