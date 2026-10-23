/**
 * PixelMotion 3D Spatial UI Engine
 * Orchestrates dimensional interface compositions, layered panel separations,
 * camera depth planes, restrained soft shadows, and perspective transforms.
 */

class SpatialUIEngine {
  constructor(options = {}) {
    this.containerWidth = options.width || 1920;
    this.containerHeight = options.height || 1080;
    this.perspective = options.perspective || 1400;
    this.panels = [];
    this.callouts = [];
    this.connectors = [];
  }

  /**
   * Calculates 3D CSS transform matrix for a panel given camera and local coordinates.
   */
  computePanelTransform(panel, camera, progress) {
    // Spatial separation offset: moves forward towards camera along normal
    const zOffset = (panel.z || 0) + (panel.elevation || 0) * progress;
    const rotateX = (panel.rotateX || 0) + (camera.pitch || 0);
    const rotateY = (panel.rotateY || 0) + (camera.yaw || 0);
    const rotateZ = (panel.rotateZ || 0) + (camera.roll || 0);

    // Dynamic depth shadow calculation
    const shadowY = Math.round(12 + (zOffset * 0.25));
    const shadowBlur = Math.round(24 + (zOffset * 0.4));
    const shadowOpacity = Math.min(0.65, 0.25 + (zOffset * 0.002));

    return {
      transform: `translate3d(${panel.x - camera.x}px, ${panel.y - camera.y}px, ${zOffset - (camera.z || 0)}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) rotateZ(${rotateZ}deg) scale(${panel.scale || 1.0})`,
      boxShadow: `0 ${shadowY}px ${shadowBlur}px rgba(0, 0, 0, ${shadowOpacity.toFixed(3)})`,
      zIndex: Math.round(100 + zOffset)
    };
  }

  /**
   * Renders the complete spatial scene markup given scene configuration, camera, and frame.
   */
  generateSceneMarkup(sceneData, frame) {
    const totalFrames = sceneData.duration_frames || 180;
    const t = Math.max(0, Math.min(1, frame / totalFrames));

    const cameraKeyframes = sceneData.camera?.keyframes || [];
    const activeCam = this.interpolateCamera(cameraKeyframes, frame);

    let panelsHtml = '';
    const objects = sceneData.three_d_objects || [];
    for (const obj of objects) {
      const transform = this.computePanelTransform(
        {
          x: obj.transform?.x || 0,
          y: obj.transform?.y || 0,
          z: obj.transform?.z || 0,
          elevation: obj.depth_extrusion || 40,
          rotateX: obj.transform?.rotate_x || 0,
          rotateY: obj.transform?.rotate_y || 0,
          rotateZ: obj.transform?.rotate_z || 0,
          scale: obj.transform?.scale || 1.0
        },
        activeCam,
        t
      );

      panelsHtml += `
        <div id="obj_${obj.id}" class="spatial-panel" style="
          position: absolute;
          transform-style: preserve-3d;
          transform: ${transform.transform};
          box-shadow: ${transform.boxShadow};
          z-index: ${transform.zIndex};
          opacity: ${obj.opacity || 1.0};
          border-radius: ${obj.border_radius || 8}px;
        ">
          ${obj.properties?.content || ''}
        </div>
      `;
    }

    return `
      <div class="spatial-viewport" style="
        position: relative;
        width: ${this.containerWidth}px;
        height: ${this.containerHeight}px;
        perspective: ${this.perspective}px;
        perspective-origin: 50% 50%;
        overflow: hidden;
        background: #0B0E14;
      ">
        <div class="spatial-stage" style="
          position: absolute;
          width: 100%;
          height: 100%;
          transform-style: preserve-3d;
        ">
          ${panelsHtml}
        </div>
      </div>
    `;
  }

  interpolateCamera(keyframes, frame) {
    if (!keyframes || keyframes.length === 0) {
      return { x: 0, y: 0, z: 0, pitch: 0, yaw: 0, roll: 0, fov: 45 };
    }
    if (keyframes.length === 1) return keyframes[0];

    // Find interval
    let prev = keyframes[0];
    let next = keyframes[keyframes.length - 1];
    for (let i = 0; i < keyframes.length - 1; i++) {
      if (frame >= keyframes[i].frame && frame <= keyframes[i + 1].frame) {
        prev = keyframes[i];
        next = keyframes[i + 1];
        break;
      }
    }

    if (next.frame === prev.frame) return prev;
    const progress = (frame - prev.frame) / (next.frame - prev.frame);
    // Smooth bezier ease
    const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;

    return {
      x: prev.x + (next.x - prev.x) * ease,
      y: prev.y + (next.y - prev.y) * ease,
      z: prev.z + (next.z - prev.z) * ease,
      pitch: prev.pitch + (next.pitch - prev.pitch) * ease,
      yaw: prev.yaw + (next.yaw - prev.yaw) * ease,
      roll: prev.roll + (next.roll - prev.roll) * ease,
      fov: prev.fov + (next.fov - prev.fov) * ease
    };
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SpatialUIEngine };
}
