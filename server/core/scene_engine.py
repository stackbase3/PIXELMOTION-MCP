"""
PixelMotion Scene Composition Engine
Manages the library of 16 compositional scene types, validates frame timing,
and synthesizes deterministic HTML/CSS/JS compositions for rendering.
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional
from pathlib import Path

from pixelmotion.server.core.models import (
    SceneData,
    CompositionType,
    CameraKeyframe,
    CursorEvent,
    ThreeDObject,
    OverlaySpec
)


class SceneCompositionEngine:
    def __init__(self):
        pass

    def validate_scene(self, scene: SceneData) -> Dict[str, Any]:
        """Validates scene constraints and frame monotonicity."""
        errors = []
        warnings = []

        if scene.duration_frames <= 0:
            errors.append("Scene duration must be greater than 0 frames.")

        last_frame = -1
        for ev in scene.cursor_events:
            if ev.frame < 0 or ev.frame > scene.duration_frames:
                warnings.append(f"Cursor event at frame {ev.frame} is outside scene duration [0, {scene.duration_frames}].")
            if ev.frame < last_frame:
                errors.append(f"Cursor event frames must be non-decreasing. Got {ev.frame} after {last_frame}.")
            last_frame = ev.frame

        last_cam_frame = -1
        for kf in scene.camera.keyframes:
            if kf.frame < last_cam_frame:
                errors.append(f"Camera keyframes must be strictly increasing. Got {kf.frame} after {last_cam_frame}.")
            last_cam_frame = kf.frame

        return {
            "is_valid": len(errors) == 0,
            "scene_id": scene.scene_id,
            "composition": scene.composition.value,
            "errors": errors,
            "warnings": warnings
        }

    def compile_scene_html(
        self,
        scene: SceneData,
        reference_image_url: Optional[str] = None,
        crop_assets: Optional[Dict[str, str]] = None,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Compiles a scene into a self-contained, deterministic HTML document.
        Converts reference images to base64 data URIs for robust, sandbox-compliant rendering.
        """
        ref_src = ""
        if reference_image_url:
            raw_path = reference_image_url.replace("file://", "")
            p = Path(raw_path)
            if p.exists():
                try:
                    with open(p, "rb") as img_f:
                        b64_data = base64.b64encode(img_f.read()).decode("utf-8")
                    ref_src = f"data:image/png;base64,{b64_data}"
                except Exception:
                    ref_src = reference_image_url
            else:
                ref_src = reference_image_url

        # 3D Objects serialization with strict json.dumps
        objects_json_str = json.dumps([obj.dict() for obj in scene.three_d_objects])
        camera_keyframes_json_str = json.dumps([kf.dict() for kf in scene.camera.keyframes])
        cursor_events_json_str = json.dumps([cev.dict() for cev in scene.cursor_events])
        overlays_json_str = json.dumps([ov.dict() for ov in scene.overlays])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{scene.scene_id}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: {width}px;
      height: {height}px;
      overflow: hidden;
      background: #0B0E14;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      user-select: none;
    }}
    #viewport {{
      position: relative;
      width: {width}px;
      height: {height}px;
      perspective: 1400px;
      perspective-origin: 50% 50%;
      overflow: hidden;
    }}
    #stage {{
      position: absolute;
      width: 100%;
      height: 100%;
      transform-style: preserve-3d;
    }}
    .ui-locked-layer {{
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      transform-style: preserve-3d;
    }}
    .ui-locked-layer img {{
      width: 100%;
      height: 100%;
      display: block;
      object-fit: fill;
    }}
    .spatial-card {{
      position: absolute;
      transform-style: preserve-3d;
      border-radius: 8px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
      transition: none;
    }}
    #cursor {{
      position: absolute;
      width: 56px;
      height: 56px;
      pointer-events: none;
      z-index: 1000;
      transform-origin: 0% 0%;
      filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4)) drop-shadow(0 1px 3px rgba(56,189,248,0.5));
    }}
    .ripple {{
      position: absolute;
      border: 3px solid #38BDF8;
      border-radius: 50%;
      pointer-events: none;
      z-index: 999;
      transform: translate(-50%, -50%);
    }}
    .overlay-element {{
      position: absolute;
      z-index: 500;
      pointer-events: none;
    }}
  </style>
</head>
<body>
  <div id="viewport">
    <div id="stage">
      <div id="base-layer" class="ui-locked-layer">
        {"<img id='ref-img' src='" + ref_src + "' />" if ref_src else ""}
      </div>
      <div id="objects-layer"></div>
      <div id="callouts-layer"></div>
    </div>
    <div id="overlays-layer"></div>
    <!-- Tip-anchored SVG Cursor -->
    <svg id="cursor" viewBox="0 0 24 24" style="display: none;">
      <path d="M4,3 L4,17 L9,13 L12,19 L14,18 L11,12 L17,12 Z"
            fill="#38BDF8" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round" />
    </svg>
    <div id="ripples-container"></div>
  </div>

  <script>
    const sceneConfig = {{
      durationFrames: {scene.duration_frames},
      composition: "{scene.composition.value}",
      cameraKeyframes: {camera_keyframes_json_str},
      threeDObjects: {objects_json_str},
      cursorEvents: {cursor_events_json_str},
      overlays: {overlays_json_str}
    }};

    function interpolateCamera(frame) {{
      const kfs = sceneConfig.cameraKeyframes;
      if (!kfs || kfs.length === 0) return {{ x: 0, y: 0, z: 0, pitch: 0, yaw: 0, roll: 0, fov: 45 }};
      if (kfs.length === 1) return kfs[0];

      let prev = kfs[0], next = kfs[kfs.length - 1];
      for (let i = 0; i < kfs.length - 1; i++) {{
        if (frame >= kfs[i].frame && frame <= kfs[i+1].frame) {{
          prev = kfs[i];
          next = kfs[i+1];
          break;
        }}
      }}
      if (next.frame === prev.frame) return prev;
      const progress = (frame - prev.frame) / (next.frame - prev.frame);
      const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;

      return {{
        x: prev.x + (next.x - prev.x) * ease,
        y: prev.y + (next.y - prev.y) * ease,
        z: prev.z + (next.z - prev.z) * ease,
        pitch: prev.pitch + (next.pitch - prev.pitch) * ease,
        yaw: prev.yaw + (next.yaw - prev.yaw) * ease,
        roll: prev.roll + (next.roll - prev.roll) * ease,
        fov: prev.fov + (next.fov - prev.fov) * ease
      }};
    }}

    function interpolateCursor(frame) {{
      const evs = sceneConfig.cursorEvents;
      if (!evs || evs.length === 0) return null;

      let prev = null, next = null;
      for (let i = 0; i < evs.length; i++) {{
        if (evs[i].frame <= frame) prev = evs[i];
        if (evs[i].frame >= frame && !next) next = evs[i];
      }}
      if (!prev && next) return next;
      if (prev && !next) return prev;
      if (!prev && !next) return null;
      if (prev.frame === next.frame) return prev;

      const p = (frame - prev.frame) / (next.frame - prev.frame);
      const ease = Math.pow(p, 2.5);

      return {{
        x: prev.x + (next.x - prev.x) * ease,
        y: prev.y + (next.y - prev.y) * ease,
        scale: prev.scale + (next.scale - prev.scale) * p,
        action: prev.action
      }};
    }}

    window.renderFrame = function(frame) {{
      const total = sceneConfig.durationFrames;
      const t = Math.max(0, Math.min(1, frame / total));

      // 1. Update Camera
      const cam = interpolateCamera(frame);
      const stage = document.getElementById('stage');
      stage.style.transform = `translate3d(${{-cam.x}}px, ${{-cam.y}}px, ${{-cam.z}}px) rotateX(${{cam.pitch}}deg) rotateY(${{cam.yaw}}deg) rotateZ(${{cam.roll}}deg)`;

      // 2. Update 3D Objects & Panels
      const objectsLayer = document.getElementById('objects-layer');
      objectsLayer.innerHTML = '';
      sceneConfig.threeDObjects.forEach(obj => {{
        const zShift = (obj.transform.z || 0) + (obj.depth_extrusion || 0) * Math.sin(t * Math.PI);
        const cardDiv = document.createElement('div');
        cardDiv.className = 'spatial-card';
        cardDiv.style.left = (obj.transform.x || 0) + 'px';
        cardDiv.style.top = (obj.transform.y || 0) + 'px';
        cardDiv.style.transform = `translate3d(0, 0, ${{zShift}}px) scale(${{obj.transform.scale || 1}})`;
        
        if (obj.type === 'callout') {{
          cardDiv.innerHTML = `
            <div style="padding: 14px 18px; background: rgba(15,23,42,0.92); border: 1px solid #38BDF8; border-radius: 8px; color: #FFF; width: 280px;">
              <div style="font-size: 11px; color: #38BDF8; font-weight: 700; text-transform: uppercase;">${{obj.properties.category || 'Feature'}}</div>
              <div style="font-size: 16px; font-weight: 700; margin: 4px 0;">${{obj.properties.title || ''}}</div>
              <div style="font-size: 12px; color: #94A3B8;">${{obj.properties.description || ''}}</div>
              ${{obj.properties.badge ? `<span style="display:inline-block; margin-top:8px; padding:2px 8px; background:rgba(56,189,248,0.2); color:#38BDF8; font-size:11px; border-radius:4px;">${{obj.properties.badge}}</span>` : ''}}
            </div>
          `;
        }}
        objectsLayer.appendChild(cardDiv);
      }});

      // 3. Update Cursor
      const cursorEl = document.getElementById('cursor');
      const cur = interpolateCursor(frame);
      if (cur) {{
        cursorEl.style.display = 'block';
        const tipOffsetX = 4 * (56 / 24) * cur.scale;
        const tipOffsetY = 3 * (56 / 24) * cur.scale;
        cursorEl.style.left = (cur.x - tipOffsetX) + 'px';
        cursorEl.style.top = (cur.y - tipOffsetY) + 'px';
        cursorEl.style.transform = `scale(${{cur.scale}}) rotate(-4deg)`;
      }} else {{
        cursorEl.style.display = 'none';
      }}

      // 4. Click Ripples
      const ripplesCont = document.getElementById('ripples-container');
      ripplesCont.innerHTML = '';
      sceneConfig.cursorEvents.forEach(ev => {{
        if (ev.action === 'click' && frame >= ev.frame && frame <= ev.frame + (ev.click_duration || 14)) {{
          const rp = (frame - ev.frame) / (ev.click_duration || 14);
          const ripple = document.createElement('div');
          ripple.className = 'ripple';
          ripple.style.left = ev.x + 'px';
          ripple.style.top = ev.y + 'px';
          ripple.style.width = (rp * 70) + 'px';
          ripple.style.height = (rp * 70) + 'px';
          ripple.style.opacity = (1 - rp).toString();
          ripplesCont.appendChild(ripple);
        }}
      }});

      // 5. Update Overlays
      const overlaysLayer = document.getElementById('overlays-layer');
      overlaysLayer.innerHTML = '';
      sceneConfig.overlays.forEach(ov => {{
        if (frame >= ov.start_frame && frame <= ov.start_frame + ov.duration_frames) {{
          const localF = frame - ov.start_frame;
          const enterP = Math.min(1, localF / 15);
          const el = document.createElement('div');
          el.className = 'overlay-element';
          el.style.left = ov.x + 'px';
          el.style.top = ov.y + 'px';
          el.style.transform = `translate(-50%, -50%) translateY(${{(1 - enterP) * 12}}px)`;
          el.style.opacity = enterP.toString();
          el.style.fontSize = (ov.style.font_size || 24) + 'px';
          el.style.fontWeight = ov.style.font_weight || '600';
          el.style.color = ov.style.color || '#FFFFFF';
          el.style.textAlign = 'center';
          el.innerText = ov.text;
          overlaysLayer.appendChild(el);
        }}
      }});

      return {{ frame, total, status: 'rendered' }};
    }};

    window.renderFrame(0);
  </script>
</body>
</html>
"""
        return html
