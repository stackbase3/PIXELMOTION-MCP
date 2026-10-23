# PixelMotion MCP: Advanced AI-Powered SaaS Motion Graphics Engine

[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Remotion Extended](https://img.shields.io/badge/Remotion-4.x-purple.svg)](https://www.remotion.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**PixelMotion MCP** is a production-grade Model Context Protocol (MCP) server, 3D motion graphics engine, and AI video director for crafting cinematic SaaS product films and interactive tutorials.

Unlike ordinary video generators that merely zoom into static screenshots with basic cursor pointers, PixelMotion treats your genuine user interface as a living, dimensional visual source. It orchestrates controlled 3D panel separations, camera dollies, spatial callouts, and seamless transitions into pixel-faithful 2D walkthroughs with beat-locked rhythm.

---

## Key Pillars & Architectural Separation

PixelMotion separates production concerns into five modular layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP CLIENTS & WORKSPACES                          │
│     Claude Desktop  •  Cursor IDE  •  Zed  •  Companion Web Studio          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ JSON-RPC 2.0 (stdio / SSE)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            PIXELMOTION FASTMCP SERVER                       │
│  24 Production Tools: Reference, Reconstruction, Motion, Audio, Render, QA  │
└──────┬───────────────────────┬───────────────────────┬──────────────────────┘
       │                       │                       │
┌──────▼──────────────┐ ┌──────▼──────────────┐ ┌──────▼──────────────────────┐
│  AI MOTION DIRECTOR │ │ 3D MOTION ENGINE    │ │ UI FIDELITY ENGINE          │
│  • Narrative Beats  │ │ • Spatial UI Panels │ │ • 4-Tier Reconstruction     │
│  • Intent Reasoning │ │ • 3D Callouts/Lines │ │ • Locked Reference Layer    │
│  • Camera & Cursors │ │ • Transitions (6)   │ │ • Semantic Region Crops     │
└──────┬──────────────┘ └──────┬──────────────┘ └──────┬──────────────────────┘
       │                       │                       │
┌──────▼───────────────────────▼───────────────────────▼──────────────────────┐
│                         DUAL RENDERING & QA PIPELINE                        │
│   Remotion Components  •  Hyperframes Adapter  •  Headless Chromium Frame   │
│   Capturer  •  FFmpeg H.264 Encoder  •  Automated Visual QA Validation      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1. Model Context Protocol (FastMCP) Core
Exposes 24 real tools over standard JSON-RPC 2.0 (`stdio` and `SSE`). Compatible with Claude Desktop, Cursor, Zed, or automated agents.

### 2. UI Fidelity & 4-Tier Reconstruction Priority
Strictly preserves interface identity without synthetic redesigns:
1. **Tier 1 - Existing Source Code**: When repository components are available.
2. **Tier 2 - DOM / HTML / CSS Reconstruction**: Clean, structured semantic layout.
3. **Tier 3 - Cropped Original Assets**: High-resolution extraction for complex charts, WebGL canvases, and proprietary widgets.
4. **Tier 4 - Locked Reference Layer**: Pristine base layer ensuring 100% pixel fidelity.

### 3. Dedicated 3D Motion Graphics Engine
- **Spatial UI Compositions**: Elevates dashboard cards into spatial Z-depth with dynamic soft contact shadows.
- **3D Feature Callouts**: Connects dimensional highlight cards with curved animated SVG connectors and glowing focus frames.
- **Camera Choreography**: Deterministic dolly, orbit, spatial tracking, and match-cut transitions.
- **Advanced Transitions**: Spatial panel separation, camera-through-dashboard, perspective-to-flat collapse, 3D card rotation, and layered assembly.

### 4. AI Motion Director
Analyzes product geometry, narrative beat, and musical rhythm to generate a validated, multi-act production plan. Distinguishes between:
- Interface demonstration vs. Feature explanation
- Cinematic product opener vs. Closing call-to-action
- Data visualization vs. 3D spatial presentation

### 5. Dual Beat & Rhythm Engine
Built-in SciPy onset spectral flux detector and Librosa integration. Automatically detects tempo (BPM), classifies kick vs. snare onsets, and snaps scene cuts to 2-bar or 4-bar phrases.

### 6. Automated Visual QA Suite
Inspects output for:
- Interface pixel fidelity (MSE / PSNR diff)
- Crop boundary alignment and missing assets
- Typography legibility (12px body floor)
- Cursor targeting accuracy (verifies clicks hit actual element bounds)
- Container stream integrity (valid H.264 / AAC stream validation)

---

## 16 Scene Composition Library

| Composition Type | Key Visual Characteristic | Primary Purpose |
|---|---|---|
| `cinematic_opener` | Dolly-in camera, layered typography, ambient depth | Establish brand identity & hook |
| `dimensional_reveal` | Interface panels separated along Z-axis in 3D | Showcase complete platform scale |
| `spatial_feature_spotlight` | Hero card elevated forward with 3D connector | Deep dive into a specific feature |
| `flat_walkthrough` | Pristine 2D pixel alignment with natural cursor | Step-by-step user workflow |
| `floating_panels` | Multi-card ambient drift using deterministic math | Modern dashboard overview |
| `animated_data_viz` | Counter with elastic overshoot and live graph fill | Quantifiable ROI / outcome proof |
| `cursor_guided_interaction` | Whip-eased cursor with tip-anchored click ripple | Micro-interaction demonstration |
| `interface_macro_shot` | Extreme close-up camera focusing on fine details | Highlighting precision craftsmanship |
| `camera_through_dashboard` | Camera plunges through hero element into new scene | Dynamic scene-to-scene transition |
| `layered_dashboard_assembly` | Dispersed panels fly into place and lock flush | Modular architecture demonstration |
| `feature_comparison` | Side-by-side dimensional split | Before/after or competitor comparison |
| `ui_to_3d_transformation` | Flat interface tilts into spatial perspective | Transitioning from demo to overview |
| `3d_to_ui_transformation` | Dimensional scene settles into crisp 2D plane | Transitioning from overview to demo |
| `full_screen_interface_demo` | Unobstructed full-screen application capture | Clean product tour |
| `narrative_title_sequence` | Word-staggered type-on with 60% overlap | Highlighting key copy & messaging |
| `closing_product_presentation` | Clean brand mark, value proposition, and CTA | Memorable finale and call to action |

---

## FastMCP Tools Reference

### Reference Management
- `reference.import(project_id, file_path)`: Ingests screenshot or video frame into project.
- `reference.analyze(file_path)`: Extracts dimensions, dark/light mode, brightness, and dominant hex palette.
- `reference.detect_regions(image_path)`: Uses OpenCV contour segmentation to locate cards, charts, and tables.
- `reference.extract_asset(image_path, x, y, width, height, output_path)`: Crops exact high-resolution subpanel.
- `reference.compare(ref_image_path, comp_image_path)`: Computes MSE, PSNR, and discrepancy bounding boxes.

### UI Reconstruction
- `ui.reconstruct(project_id, reference_id, image_path)`: Builds locked reference layer and spatial panel manifest.
- `ui.validate(project_id, reference_id)`: Verifies all crops exist and match declared dimensions.
- `ui.capture_state(target_url_or_image, output_path, is_live_url)`: Uses Headless Chromium to capture real state or synthesizes verified state variations.

### Motion Direction
- `motion.generate_plan(project_id, product_name, feature_focus, duration_seconds, bpm)`: Directs multi-act production plan.
- `motion.generate_camera_path(motion_type, duration_frames, target_bbox)`: Synthesizes camera keyframe trajectory.
- `motion.generate_cursor_path(start_x, start_y, target_x, target_y, start_frame, reach_frame)`: Generates tip-anchored cursor path with whip easing.
- `motion.generate_3d_composition(panel_regions, elevation_step)`: Computes Z-depths and soft drop shadows.
- `motion.validate(project_id)`: Checks scene timing, keyframe monotonicity, and typing budgets.

### Scene & Timeline Management
- `scene.create(project_id, scene_data)`: Adds a new scene to the timeline.
- `scene.update(project_id, scene_id, updates)`: Updates an existing scene.
- `scene.preview(project_id, scene_id)`: Compiles standalone preview HTML.
- `scene.validate(scene_data)`: Validates scene boundaries and frame constraints.

### Audio & Beat Sync
- `audio.analyze_beats(audio_file_path, fps)`: Detects BPM, kick frames, snare frames, and 2-bar boundaries.
- `audio.align_events(events, beats_data, max_nudge)`: Nudges in-scene events onto musical beats.

### Rendering & Quality Assurance
- `render.preview(project_id, scene_id)`: Renders fast 960x540 preview MP4.
- `render.final(project_id, scene_id, audio_path)`: Renders 1080p master MP4 with audio muxing.
- `render.status(job_id)`: Returns realtime render progress.
- `render.cancel(job_id)`: Cancels an active rendering job.

### Export Management
- `export.video(input_mp4, output_path, preset)`: Exports with `hd_1080p`, `4k_master`, `social_9_16`, or `web_optimized`.
- `export.project(project_id, output_zip_path)`: Packages editable project archive into ZIP.
- `export.assets(project_id, output_zip_path)`: Exports extracted UI components asset pack.

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Chromium (or Google Chrome)
- FFmpeg 5.x+

```bash
git clone https://github.com/your-username/pixelmotion-mcp.git
cd pixelmotion-mcp
pip install -r requirements.txt
```

### Running FastMCP Server

#### Stdio Mode (for Claude Desktop & Cursor)
```bash
python3 pixelmotion/server/mcp_server.py
```

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "pixelmotion": {
      "command": "python3",
      "args": ["-m", "pixelmotion.server.mcp_server"]
    }
  }
}
```

#### HTTP / REST & Companion Web Studio Mode
```bash
python3 -c "from pixelmotion.server.fastmcp_compat import FastMCP; from pixelmotion.server.mcp_server import mcp; mcp.run(transport='http', port=8000)"
```
Open `http://localhost:8000/companion/index.html` to access the companion workspace.

---

## End-to-End Acceptance Verification

The repository includes a comprehensive end-to-end acceptance test modeling a flagship **Trading Journal Product Film**:

```bash
python3 pixelmotion/tests/test_e2e_trading_journal.py
```

Test Results:
- **Reference Ingestion**: Analyzed 1920x1080 screenshot, dark mode, hex palette `#22758B`, `#3EBDF6`, `#161C2A`.
- **Region Segmentation**: Detected 10 semantic UI zones (Equity chart, KPI metrics, Trade executions table).
- **UI Reconstruction**: 100.0% fidelity score with locked reference layer.
- **Beat Detection**: 117.5 BPM, 35 kicks, 24 snares, 2-bar scene intervals.
- **Motion Direction**: 6-scene structured plan (900 frames / 30.0s).
- **3D Feature Spotlight (Act 3)**: Elevated performance card with 3D callout badge (`+18.4% Alpha`).
- **Real Walkthrough (Act 4)**: Perspective collapsed to flat plane, whip-eased cursor clicked `+ Log Trade` button.
- **Render Output**: 1080p MP4 rendered and audio-muxed via FFmpeg.
- **Visual QA Scorecard**: **PASS** (98.0% fidelity score across all 7 checks).
- **Export**: Saved playable master video and editable ZIP bundle.

---

## Attribution & License

This project forks and significantly extends the foundational Remotion templates and scripts created by **Noam Dorr** under the MIT License.

PixelMotion MCP extensions copyright (c) 2026. Distributed under the MIT License. See `LICENSE` for details.

## Additional Remotion motion templates

Three independently authored templates are included in `remotion_templates/`:

- `AnimatedGradientText.tsx` for a deterministic text-gradient sweep.
- `DrawPath.tsx` for SVG path drawing with a traveling endpoint marker.
- `SpotlightCard.tsx` for a subtle product-feature card reveal.

They use Remotion frame hooks and React, and can be imported into a composition after copying the files into your Remotion project's source tree. For example: `import { SpotlightCard } from "./SpotlightCard";`. See [UPSTREAM_NOTICES.md](UPSTREAM_NOTICES.md) for the upstream license review and provenance notes; Remotion itself is under a custom license, not MIT.

## Railway-hosted remote MCP (Claude)

This repo includes a Dockerfile and `railway.toml` for a Railway deployment. The ASGI app exposes stateless MCP Streamable HTTP at `/mcp` and a health check at `/health`. For a Railway deployment, configure `PIXELMOTION_API_TOKEN` as a Railway secret variable before starting: protected MCP/API calls require `Authorization: Bearer <token>`. Full deployment and Claude connector steps are in [RAILWAY_CLAUDE_SETUP.md](RAILWAY_CLAUDE_SETUP.md). Review Railway usage pricing before deployment.
