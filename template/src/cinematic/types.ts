export type CameraMovement =
  | "pushIn"
  | "pullOut"
  | "panLeft"
  | "panRight"
  | "panUp"
  | "panDown"
  | "smallOrbit"
  | "focus"
  | "static";

export type LayerDepth = "background" | "environment" | "subject" | "content" | "foreground";

export const layerDepthConfig: Record<LayerDepth, { z: number; parallax: number }> = {
  background: { z: -300, parallax: 0.2 },
  environment: { z: -150, parallax: 0.4 },
  subject: { z: 0, parallax: 0.6 },
  content: { z: 120, parallax: 0.8 },
  foreground: { z: 250, parallax: 1.1 },
};
