import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export type SpotlightCardProps = {
  children: React.ReactNode;
  startFrame?: number;
  duration?: number;
  accent?: string;
  radius?: number;
  style?: React.CSSProperties;
};

/** A restrained focus-card treatment suitable for interface walkthrough scenes. */
export const SpotlightCard: React.FC<SpotlightCardProps> = ({
  children,
  startFrame = 0,
  duration = 18,
  accent = "#8b5cf6",
  radius = 18,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - startFrame, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const lift = interpolate(progress, [0, 1], [18, 0]);
  const scale = interpolate(progress, [0, 1], [0.975, 1]);
  return (
    <div
      style={{
        position: "relative",
        borderRadius: radius,
        transform: `translateY(${lift}px) scale(${scale})`,
        opacity: progress,
        background: "linear-gradient(145deg, rgba(255,255,255,.09), rgba(255,255,255,.025))",
        border: `1px solid ${accent}66`,
        boxShadow: `0 18px 55px rgba(0,0,0,.28), 0 0 32px ${accent}20`,
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          background: `radial-gradient(380px circle at 50% 0%, ${accent}18, transparent 70%)`,
        }}
      />
      <div style={{ position: "relative" }}>{children}</div>
    </div>
  );
};
