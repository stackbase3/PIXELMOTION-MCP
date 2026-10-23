import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export type DrawPathProps = {
  /** SVG path `d` string. */
  d: string;
  startFrame?: number;
  duration?: number;
  color?: string;
  strokeWidth?: number;
  viewBox?: string;
  width?: number | string;
  height?: number | string;
  showHead?: boolean;
  style?: React.CSSProperties;
};

/** Animates an SVG stroke with a stable marker following its visible endpoint. */
export const DrawPath: React.FC<DrawPathProps> = ({
  d,
  startFrame = 0,
  duration = 30,
  color = "#67e8f9",
  strokeWidth = 3,
  viewBox = "0 0 100 100",
  width = "100%",
  height = "100%",
  showHead = true,
  style,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - startFrame, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pathRef = React.useRef<SVGPathElement>(null);
  const [length, setLength] = React.useState(0);
  React.useLayoutEffect(() => {
    if (pathRef.current) setLength(pathRef.current.getTotalLength());
  }, [d]);
  const point = pathRef.current && length > 0
    ? pathRef.current.getPointAtLength(length * progress)
    : null;
  return (
    <svg viewBox={viewBox} width={width} height={height} style={{ overflow: "visible", ...style }}>
      <path
        ref={pathRef}
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={length || 1}
        strokeDashoffset={(length || 1) * (1 - progress)}
      />
      {showHead && progress > 0 && point && (
        <circle cx={point.x} cy={point.y} r={strokeWidth * 1.7} fill={color} />
      )}
    </svg>
  );
};
