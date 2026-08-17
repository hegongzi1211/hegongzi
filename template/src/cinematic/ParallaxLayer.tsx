import type { CSSProperties, ReactNode } from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import type { LayerDepth } from "./types";
import { layerDepthConfig } from "./types";

export const ParallaxLayer: React.FC<{
  depth: LayerDepth;
  children: ReactNode;
  x?: number;
  y?: number;
  z?: number;
  scale?: number;
  rotateX?: number;
  rotateY?: number;
  rotateZ?: number;
  opacity?: number;
  blur?: number;
  style?: CSSProperties;
}> = ({ depth, children, x = 0, y = 0, z, scale = 1, rotateX = 0, rotateY = 0, rotateZ = 0, opacity = 1, blur = 0, style }) => {
  const frame = useCurrentFrame();
  const config = layerDepthConfig[depth];
  const driftX = Math.sin(frame / 58) * config.parallax * 7;
  const driftY = Math.cos(frame / 71) * config.parallax * 5;

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        opacity,
        filter: blur ? `blur(${blur}px)` : undefined,
        transformStyle: "preserve-3d",
        transform: `translate3d(${x + driftX}px, ${y + driftY}px, ${z ?? config.z}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) rotateZ(${rotateZ}deg) scale(${scale})`,
        ...style,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
