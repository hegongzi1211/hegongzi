import type { CSSProperties, ReactNode } from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { CameraMovement } from "./types";

const cameraCurve = (frame: number, duration: number) =>
  interpolate(frame, [0, duration], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const getCameraTransform = (movement: CameraMovement, progress: number, intensity: number) => {
  const x = intensity * 42;
  const y = intensity * 34;
  const z = intensity * 120;
  const rotate = intensity * 2.4;

  switch (movement) {
    case "pushIn":
      return { tx: 0, ty: -y * 0.16, tz: z, rx: 0, ry: 0, scale: 1 + progress * intensity * 0.045 };
    case "pullOut":
      return { tx: 0, ty: y * 0.12, tz: -z, rx: 0, ry: 0, scale: 1.035 - progress * intensity * 0.035 };
    case "panLeft":
      return { tx: x * progress, ty: 0, tz: z * 0.25, rx: 0, ry: -rotate * 0.4, scale: 1.02 };
    case "panRight":
      return { tx: -x * progress, ty: 0, tz: z * 0.25, rx: 0, ry: rotate * 0.4, scale: 1.02 };
    case "panUp":
      return { tx: 0, ty: y * progress, tz: z * 0.2, rx: rotate * 0.25, ry: 0, scale: 1.015 };
    case "panDown":
      return { tx: 0, ty: -y * progress, tz: z * 0.2, rx: -rotate * 0.25, ry: 0, scale: 1.015 };
    case "smallOrbit":
      return {
        tx: Math.sin(progress * Math.PI * 2) * x * 0.36,
        ty: Math.cos(progress * Math.PI * 2) * y * 0.16,
        tz: z * 0.18,
        rx: Math.sin(progress * Math.PI * 2) * rotate * 0.18,
        ry: Math.cos(progress * Math.PI * 2) * rotate * 0.6,
        scale: 1.018,
      };
    case "focus":
      return { tx: -x * 0.28 * progress, ty: -y * 0.22 * progress, tz: z * 0.5, rx: rotate * 0.16, ry: rotate * 0.24, scale: 1.025 };
    case "static":
      return { tx: 0, ty: 0, tz: 0, rx: 0, ry: 0, scale: 1 };
  }
};

export const CameraRig: React.FC<{
  children: ReactNode;
  movement?: CameraMovement;
  intensity?: number;
  style?: CSSProperties;
}> = ({ children, movement = "pushIn", intensity = 0.45, style }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = cameraCurve(frame, durationInFrames);
  const camera = getCameraTransform(movement, progress, intensity);

  return (
    <AbsoluteFill
      style={{
        perspective: 1500,
        overflow: "hidden",
        background: "#020706",
        ...style,
      }}
    >
      <AbsoluteFill
        style={{
          transformStyle: "preserve-3d",
          transformOrigin: "50% 52%",
          transform: `translate3d(${camera.tx}px, ${camera.ty}px, ${camera.tz}px) rotateX(${camera.rx}deg) rotateY(${camera.ry}deg) scale(${camera.scale})`,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
