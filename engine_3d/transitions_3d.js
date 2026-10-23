/**
 * PixelMotion 3D Transitions
 * Deterministic spatial transitions between scenes:
 * 1. Spatial Panel Separation
 * 2. Camera-Through-Interface
 * 3. Perspective-to-Flat Alignment
 * 4. 3D Card Rotation
 * 5. Layered Interface Assembly
 * 6. Dimensional Collapse
 */

class Transitions3DEngine {
  constructor() {}

  /**
   * Applies transition transforms to elements based on transition type and progress (0.0 -> 1.0).
   */
  computeTransitionState(type, progress, elements = []) {
    const p = Math.max(0, Math.min(1, progress));

    switch (type) {
      case "spatial_panel_separation":
        // Panels separate along Z and disperse subtly outward
        return elements.map((el, i) => {
          const zShift = (i + 1) * 60 * p;
          const spreadX = ((i % 2 === 0 ? 1 : -1) * (i + 1) * 30) * p;
          return {
            id: el.id,
            transform: `translate3d(${spreadX}px, 0px, ${zShift}px) rotateY(${p * -5}deg)`,
            opacity: 1.0
          };
        });

      case "perspective_to_flat":
        // Smoothly removes perspective rotation and Z offset to restore pristine 2D plane
        return elements.map((el) => {
          const rotX = (el.startRotX || 12) * (1 - p);
          const rotY = (el.startRotY || -14) * (1 - p);
          const z = (el.startZ || 80) * (1 - p);
          return {
            id: el.id,
            transform: `translate3d(0, 0, ${z}px) rotateX(${rotX}deg) rotateY(${rotY}deg)`,
            opacity: 1.0
          };
        });

      case "camera_through_interface":
        // Hero element scales up and moves past camera into next scene
        return elements.map((el) => {
          const zPush = p * 1200;
          const fadeOut = p > 0.8 ? (1 - p) / 0.2 : 1.0;
          return {
            id: el.id,
            transform: `translate3d(0, 0, ${zPush}px) scale(${1 + p * 1.5})`,
            opacity: fadeOut
          };
        });

      case "layered_interface_assembly":
        // Panels fly into place from offset coordinates with elastic landing
        return elements.map((el, i) => {
          const initialOffset = (3 - i) * 120 * (1 - p);
          const opacity = Math.min(1, p * 1.4);
          return {
            id: el.id,
            transform: `translate3d(0, ${initialOffset}px, ${(1 - p) * 100}px) scale(${0.9 + 0.1 * p})`,
            opacity: opacity
          };
        });

      case "dimensional_collapse":
        // All separated layers collapse back onto the base canvas
        return elements.map((el) => {
          return {
            id: el.id,
            transform: `translate3d(0, 0, ${(1 - p) * 120}px)`,
            opacity: 1.0
          };
        });

      default:
        return elements.map((el) => ({ id: el.id, transform: 'none', opacity: 1.0 }));
    }
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Transitions3DEngine };
}
