import type { CSSProperties, ReactNode } from "react";
import { interpolate, useCurrentFrame } from "remotion";

export const useFocusAmount = (start: number, end: number) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [start - 12, start + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exit = interpolate(frame, [end - 12, end + 12], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return Math.min(enter, exit);
};

export const FocusLayer: React.FC<{
  active: number;
  dimmed?: boolean;
  children: ReactNode;
  style?: CSSProperties;
}> = ({ active, dimmed = false, children, style }) => {
  const lift = active * 26;
  const opacity = dimmed ? 0.48 + active * 0.25 : 0.72 + active * 0.28;
  const brightness = dimmed ? 0.68 + active * 0.2 : 0.9 + active * 0.22;
  const blur = dimmed ? 1.4 - active : 0;

  return (
    <div
      style={{
        opacity,
        filter: `brightness(${brightness}) blur(${Math.max(0, blur)}px)`,
        transform: `translateZ(${lift}px) scale(${1 + active * 0.035})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
