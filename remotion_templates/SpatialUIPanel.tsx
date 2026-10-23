// SpatialUIPanel.tsx - Remotion 3D Spatial Presentation Component
// Orchestrates dimensional panel separation, perspective camera planes,
// and soft depth shadows while strictly preserving the underlying UI pixels.

import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { easings } from "./easings";

export interface SpatialUIPanelProps {
  children: React.ReactNode;
  startFrame: number;
  durationFrames?: number;
  zElevation?: number; // target Z-elevation in pixels
  rotateX?: number;   // pitch angle in degrees
  rotateY?: number;   // yaw angle in degrees
  scale?: number;
  borderRadius?: number;
  shadowColor?: string;
  className?: string;
  style?: React.CSSProperties;
}

export const SpatialUIPanel: React.FC<SpatialUIPanelProps> = ({
  children,
  startFrame,
  durationFrames = 30,
  zElevation = 80,
  rotateX = 8,
  rotateY = -10,
  scale = 1.0,
  borderRadius = 8,
  shadowColor = "rgba(0, 0, 0, 0.45)",
  className,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - startFrame, [0, durationFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: easings.slowInLand,
  });

  const currentZ = zElevation * progress;
  const currentRotX = rotateX * progress;
  const currentRotY = rotateY * progress;
  const currentScale = 1.0 + (scale - 1.0) * progress;

  // Dynamic contact drop shadow calculation based on current elevation
  const shadowY = Math.round(8 + currentZ * 0.3);
  const shadowBlur = Math.round(16 + currentZ * 0.5);
  const shadowOpacity = Math.min(0.6, 0.2 + currentZ * 0.003);

  return (
    <div
      className={className}
      style={{
        position: "relative",
        transformStyle: "preserve-3d",
        transform: `translate3d(0px, 0px, ${currentZ}px) rotateX(${currentRotX}deg) rotateY(${currentRotY}deg) scale(${currentScale})`,
        boxShadow: `0 ${shadowY}px ${shadowBlur}px ${shadowColor}`,
        borderRadius,
        zIndex: Math.round(100 + currentZ),
        transition: "none",
        ...style,
      }}
    >
      {children}
    </div>
  );
};
