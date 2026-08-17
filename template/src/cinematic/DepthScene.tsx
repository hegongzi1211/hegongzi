import type { ReactNode } from "react";
import { AbsoluteFill } from "remotion";
import type { CameraMovement } from "./types";
import { CameraRig } from "./CameraRig";
import { ParallaxLayer } from "./ParallaxLayer";

export const DepthScene: React.FC<{
  background?: ReactNode;
  environment?: ReactNode;
  subject?: ReactNode;
  content?: ReactNode;
  foreground?: ReactNode;
  movement?: CameraMovement;
  intensity?: number;
}> = ({ background, environment, subject, content, foreground, movement = "pushIn", intensity = 0.45 }) => (
  <CameraRig movement={movement} intensity={intensity}>
    <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
      <ParallaxLayer depth="background">{background}</ParallaxLayer>
      <ParallaxLayer depth="environment">{environment}</ParallaxLayer>
      <ParallaxLayer depth="subject">{subject}</ParallaxLayer>
      <ParallaxLayer depth="content">{content}</ParallaxLayer>
      <ParallaxLayer depth="foreground">{foreground}</ParallaxLayer>
    </AbsoluteFill>
  </CameraRig>
);
