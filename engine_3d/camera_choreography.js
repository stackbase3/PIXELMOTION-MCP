/**
 * PixelMotion 3D Camera Choreography
 * Generates smooth, deterministic camera paths:
 * - Dolly-in & dolly-out
 * - Controlled orbit & pitch shifts
 * - Spatial target tracking
 * - Match cut keyframe continuity
 */

const CameraPresets = {
  CINEMATIC_OVERVIEW: {
    start: { x: 0, y: 0, z: 250, pitch: 12, yaw: -14, roll: 0, fov: 45 },
    end: { x: 0, y: 0, z: 120, pitch: 6, yaw: -4, roll: 0, fov: 45 },
    motion: "dolly_in"
  },
  FEATURE_SPOTLIGHT: {
    start: { x: 0, y: 0, z: 150, pitch: 8, yaw: -6, roll: 0, fov: 45 },
    end: { x: 220, y: -60, z: -80, pitch: 2, yaw: 0, roll: 0, fov: 40 },
    motion: "spatial_tracking"
  },
  PERSPECTIVE_TO_FLAT: {
    start: { x: 120, y: 40, z: 80, pitch: 10, yaw: -8, roll: 0, fov: 45 },
    end: { x: 0, y: 0, z: 0, pitch: 0, yaw: 0, roll: 0, fov: 45 },
    motion: "perspective_to_flat"
  },
  CAMERA_THROUGH: {
    start: { x: 0, y: 0, z: 200, pitch: 4, yaw: 0, roll: 0, fov: 45 },
    end: { x: 0, y: 0, z: -400, pitch: 0, yaw: 0, roll: 0, fov: 50 },
    motion: "camera_through"
  }
};

class CameraChoreographer {
  constructor() {}

  /**
   * Generates a keyframe sequence for a scene based on motion type and target region.
   */
  generatePath(motionType, durationFrames, targetBBox = null, startFrame = 0) {
    const endFrame = startFrame + durationFrames;

    if (motionType === "spatial_tracking" && targetBBox) {
      // Focus on target element center
      const targetCenterX = targetBBox.x + targetBBox.width / 2.0 - 960;
      const targetCenterY = targetBBox.y + targetBBox.height / 2.0 - 540;

      return [
        {
          frame: startFrame,
          x: 0,
          y: 0,
          z: 160,
          pitch: 8,
          yaw: -10,
          roll: 0,
          fov: 45,
          easing: "slowInLand"
        },
        {
          frame: Math.round(startFrame + durationFrames * 0.4),
          x: targetCenterX * 0.5,
          y: targetCenterY * 0.5,
          z: 60,
          pitch: 4,
          yaw: -3,
          roll: 0,
          fov: 42,
          easing: "standard"
        },
        {
          frame: endFrame,
          x: targetCenterX,
          y: targetCenterY,
          z: -40,
          pitch: 0,
          yaw: 0,
          roll: 0,
          fov: 40,
          easing: "soft"
        }
      ];
    }

    if (motionType === "perspective_to_flat") {
      return [
        {
          frame: startFrame,
          x: 80,
          y: 30,
          z: 90,
          pitch: 9,
          yaw: -7,
          roll: 0,
          fov: 45,
          easing: "slowInLand"
        },
        {
          frame: endFrame,
          x: 0,
          y: 0,
          z: 0,
          pitch: 0,
          yaw: 0,
          roll: 0,
          fov: 45,
          easing: "soft"
        }
      ];
    }

    if (motionType === "dolly_in") {
      return [
        {
          frame: startFrame,
          x: 0,
          y: 0,
          z: 220,
          pitch: 10,
          yaw: -12,
          roll: 0,
          fov: 46,
          easing: "slowInLand"
        },
        {
          frame: endFrame,
          x: 0,
          y: 0,
          z: 80,
          pitch: 4,
          yaw: -4,
          roll: 0,
          fov: 45,
          easing: "soft"
        }
      ];
    }

    // Default static / subtle breath
    return [
      { frame: startFrame, x: 0, y: 0, z: 0, pitch: 0, yaw: 0, roll: 0, fov: 45, easing: "standard" },
      { frame: endFrame, x: 0, y: 0, z: 0, pitch: 0, yaw: 0, roll: 0, fov: 45, easing: "standard" }
    ];
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CameraChoreographer, CameraPresets };
}
