"""
PixelMotion Reference & UI Analysis Engine
Provides OpenCV & PIL-powered:
- Reference intake and dimension verification
- Layout zone & region detection (panels, cards, navigation, metric blocks, charts)
- Asset extraction & cropping for high-fidelity preservation
- Visual diff comparison & fidelity scoring between reference and reconstruction/render.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import cv2
from PIL import Image

from pixelmotion.server.core.config import PROJECTS_DIR
from pixelmotion.server.core.models import DetectedRegion, VisualDirectionProfile


def extract_dominant_colors(image_path: str, num_colors: int = 5) -> List[str]:
    """Extract dominant hex colors from image using k-means clustering."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return ["#0F172A", "#1E293B", "#38BDF8", "#10B981", "#F59E0B"]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Resize for fast clustering
        img_small = cv2.resize(img_rgb, (150, 150)).reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(img_small, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        hex_colors = []
        for c in centers:
            r, g, b = int(c[0]), int(c[1]), int(c[2])
            hex_colors.append(f"#{r:02x}{g:02x}{b:02x}".upper())
        return hex_colors
    except Exception:
        return ["#0F172A", "#1E293B", "#38BDF8", "#10B981", "#F59E0B"]


def analyze_reference(file_path: str) -> Dict[str, Any]:
    """Analyzes a reference screenshot or video frame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Reference file not found: {file_path}")

    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Could not decode image at {file_path}")

    h, w, c = img.shape
    aspect_ratio = f"{round(w / h, 2)}:1"
    if abs(w / h - 16 / 9) < 0.05:
        aspect_ratio = "16:9"
    elif abs(w / h - 9 / 16) < 0.05:
        aspect_ratio = "9:16"
    elif abs(w / h - 1.0) < 0.05:
        aspect_ratio = "1:1"

    # Color analysis
    palette = extract_dominant_colors(str(path), 6)
    brightness = float(np.mean(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)))
    is_dark_mode = brightness < 128.0

    return {
        "file_path": str(path.resolve()),
        "file_name": path.name,
        "width": w,
        "height": h,
        "channels": c,
        "aspect_ratio": aspect_ratio,
        "is_dark_mode": is_dark_mode,
        "mean_brightness": round(brightness, 1),
        "dominant_palette": palette,
        "primary_accent": palette[2] if len(palette) > 2 else "#2563EB",
        "estimated_dpi": 72 if w <= 1920 else 144
    }


def detect_regions(image_path: str, output_crops_dir: Optional[str] = None) -> List[DetectedRegion]:
    """
    Detects semantic UI regions (header, sidebar, cards, tables, buttons, charts)
    using morphological contour segmentation.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image for region detection: {image_path}")

    orig_h, orig_w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gradient edge detection
    grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

    # Threshold and morphological dilation to join card borders
    _, thresh = cv2.threshold(grad, 25, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    detected: List[DetectedRegion] = []
    crops_path = Path(output_crops_dir) if output_crops_dir else None
    if crops_path:
        crops_path.mkdir(parents=True, exist_ok=True)

    min_area = (orig_w * orig_h) * 0.005  # at least 0.5% of total screen
    max_area = (orig_w * orig_h) * 0.95   # not entire screen

    idx = 0
    candidate_boxes = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if min_area < area < max_area:
            candidate_boxes.append((x, y, w, h, area))

    # Sort candidates by area descending to establish hierarchy
    candidate_boxes.sort(key=lambda b: b[4], reverse=True)

    # Deduplicate heavily overlapping bounding boxes
    kept_boxes = []
    for box in candidate_boxes:
        x, y, w, h, area = box
        overlap = False
        for kx, ky, kw, kh, karea in kept_boxes:
            # Check intersection over union
            ix1 = max(x, kx)
            iy1 = max(y, ky)
            ix2 = min(x + w, kx + kw)
            iy2 = min(y + h, ky + kh)
            if ix1 < ix2 and iy1 < iy2:
                inter_area = (ix2 - ix1) * (iy2 - iy1)
                iou = inter_area / float(area + karea - inter_area)
                if iou > 0.65:
                    overlap = True
                    break
        if not overlap:
            kept_boxes.append(box)

    for x, y, w, h, area in kept_boxes[:15]:  # top distinct semantic zones
        idx += 1
        # Heuristic classification based on geometry and placement
        rel_y = y / orig_h
        rel_x = x / orig_w
        rel_w = w / orig_w
        rel_h = h / orig_h

        if rel_y < 0.12 and rel_w > 0.6:
            label = "top_navigation_bar"
            interactive = False
        elif rel_x < 0.22 and rel_h > 0.5:
            label = "sidebar_navigation"
            interactive = True
        elif rel_h < 0.18 and rel_w < 0.35:
            label = "metric_kpi_card"
            interactive = False
        elif rel_w > 0.45 and rel_h > 0.25:
            label = "main_chart_panel"
            interactive = True
        elif rel_w > 0.35 and rel_h > 0.3:
            label = "data_table_panel"
            interactive = True
        else:
            label = f"panel_section_{idx}"
            interactive = True

        crop_file = None
        if crops_path:
            crop_img = img[y:y+h, x:x+w]
            crop_file_name = f"region_{idx}_{label}.png"
            crop_dest = crops_path / crop_file_name
            cv2.imwrite(str(crop_dest), crop_img)
            crop_file = str(crop_dest)

        region = DetectedRegion(
            region_id=f"reg_{idx}_{label}",
            label=label,
            x=x,
            y=y,
            width=w,
            height=h,
            confidence=0.92,
            z_index=1,
            is_interactive=interactive,
            crop_path=crop_file,
            color_profile={"mean_brightness": float(np.mean(gray[y:y+h, x:x+w]))}
        )
        detected.append(region)

    # Sort by visual reading order (top-to-bottom, left-to-right)
    detected.sort(key=lambda r: (r.y // 50, r.x))
    return detected


def extract_asset(image_path: str, x: int, y: int, width: int, height: int, output_path: str) -> str:
    """Crops and saves an exact subregion from reference image."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    orig_h, orig_w = img.shape[:2]
    x1 = max(0, min(orig_w - 1, x))
    y1 = max(0, min(orig_h - 1, y))
    x2 = max(x1 + 1, min(orig_w, x + width))
    y2 = max(y1 + 1, min(orig_h, y + height))

    cropped = img[y1:y2, x1:x2]
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_p), cropped)
    return str(out_p.resolve())


def compare_images(ref_image_path: str, comp_image_path: str) -> Dict[str, Any]:
    """
    Computes visual fidelity difference between reference and rendered/reconstructed image.
    Uses normalized Mean Squared Error (MSE), Peak Signal-to-Noise Ratio (PSNR), and difference bounding.
    """
    img_ref = cv2.imread(ref_image_path)
    img_comp = cv2.imread(comp_image_path)

    if img_ref is None or img_comp is None:
        raise ValueError("One or both images could not be loaded for comparison.")

    # Resize comparison to reference if slightly mismatched
    if img_ref.shape != img_comp.shape:
        img_comp = cv2.resize(img_comp, (img_ref.shape[1], img_ref.shape[0]))

    diff = cv2.absdiff(img_ref, img_comp)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    mse = float(np.mean((img_ref.astype(np.float32) - img_comp.astype(np.float32)) ** 2))

    max_pixel = 255.0
    psnr = 100.0 if mse == 0 else 20 * np.log10(max_pixel / np.sqrt(mse))

    # Normalized fidelity score (0.0 - 1.0)
    fidelity_score = max(0.0, min(1.0, 1.0 - (mse / (255.0 * 255.0 * 0.1))))

    # Find regions with major discrepancy
    _, diff_thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(diff_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    discrepancies = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 100:  # significant area
            discrepancies.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "area": int(w * h),
                "mean_error": float(np.mean(gray_diff[y:y+h, x:x+w]))
            })

    return {
        "fidelity_score": round(fidelity_score, 4),
        "mse": round(mse, 2),
        "psnr_db": round(float(psnr), 2),
        "is_acceptable": fidelity_score >= 0.85,
        "discrepancy_count": len(discrepancies),
        "major_discrepancies": sorted(discrepancies, key=lambda d: d["area"], reverse=True)[:5]
    }
