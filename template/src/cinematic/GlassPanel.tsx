import type { CSSProperties, ReactNode } from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AmbientMotion } from "./AmbientMotion";

export const GlassPanel: React.FC<{
  children: ReactNode;
  startFrame?: number;
  accent?: string;
  focused?: number;
  width?: number;
  style?: CSSProperties;
}> = ({ children, startFrame = 0, accent = "#62ffe4", focused = 0, width = 300, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - startFrame;
  const pop = spring({
    frame: localFrame,
    fps,
    config: { damping: 18, stiffness: 92, mass: 0.8 },
  });
  const opacity = interpolate(localFrame, [0, 12], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AmbientMotion amount={2.8} rotate={0.25} speed={84}>
      <div
        style={{
          position: "relative",
          width,
          minHeight: 112,
          padding: "22px 24px",
          color: "white",
          opacity,
          borderRadius: 18,
          border: `1px solid ${accent}66`,
          background: "linear-gradient(145deg, rgba(9,22,24,.74), rgba(4,9,10,.54))",
          backdropFilter: "blur(18px)",
          boxShadow: `0 24px 70px rgba(0,0,0,.38), 0 0 ${20 + focused * 20}px ${accent}33, inset 0 1px 0 rgba(255,255,255,.18)`,
          transform: `perspective(1000px) translateZ(${focused * 28}px) rotateX(${3 - focused * 1.2}deg) rotateY(${-7 + focused * 4}deg) scale(${0.82 + pop * 0.18 + focused * 0.025})`,
          transformOrigin: "50% 60%",
          overflow: "hidden",
          ...style,
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(120deg, rgba(255,255,255,.16), transparent 24%, transparent 72%, rgba(255,255,255,.06))",
            pointerEvents: "none",
          }}
        />
        <div style={{ position: "relative", zIndex: 1 }}>{children}</div>
      </div>
    </AmbientMotion>
  );
};
