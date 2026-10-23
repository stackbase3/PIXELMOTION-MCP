import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export type AnimatedGradientTextProps = {
  children: React.ReactNode;
  startFrame?: number;
  duration?: number;
  colors?: [string, string, string];
  fontSize?: number | string;
  style?: React.CSSProperties;
};

/** Reveals a looping-free gradient sweep; deterministic at any rendered frame. */
export const AnimatedGradientText: React.FC<AnimatedGradientTextProps> = ({
  children,
  startFrame = 0,
  duration = 36,
  colors = ["#7c3aed", "#22d3ee", "#f472b6"],
  fontSize = "inherit",
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - startFrame, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const position = -100 + progress * 200;
  return (
    <span
      style={{
        display: "inline-block",
        color: "transparent",
        backgroundImage: `linear-gradient(105deg, ${colors[0]} 0%, ${colors[1]} 48%, ${colors[2]} 100%)`,
        backgroundSize: "220% 100%",
        backgroundPosition: `${position}% 50%`,
        backgroundClip: "text",
        WebkitBackgroundClip: "text",
        fontSize,
        ...style,
      }}
    >
      {children}
    </span>
  );
};
