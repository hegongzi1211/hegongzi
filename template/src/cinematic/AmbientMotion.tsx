import type { CSSProperties, ReactNode } from "react";
import { useCurrentFrame } from "remotion";

export const AmbientMotion: React.FC<{
  children: ReactNode;
  amount?: number;
  rotate?: number;
  speed?: number;
  style?: CSSProperties;
}> = ({ children, amount = 4, rotate = 0.45, speed = 70, style }) => {
  const frame = useCurrentFrame();
  const y = Math.sin(frame / speed) * amount;
  const x = Math.cos(frame / (speed * 1.2)) * amount * 0.45;
  const r = Math.sin(frame / (speed * 1.35)) * rotate;

  return (
    <div style={{ transform: `translate3d(${x}px, ${y}px, 0) rotate(${r}deg)`, ...style }}>
      {children}
    </div>
  );
};
