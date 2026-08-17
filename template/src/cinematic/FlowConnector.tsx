import { interpolate, useCurrentFrame } from "remotion";

export const FlowConnector: React.FC<{
  path: string;
  startFrame?: number;
  length?: number;
  accent?: string;
}> = ({ path, startFrame = 0, length = 420, accent = "#62ffe4" }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - startFrame;
  const draw = interpolate(localFrame, [0, 24], [length, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pulseProgress = interpolate(localFrame, [12, 76], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <svg style={{ position: "absolute", inset: 0, overflow: "visible" }} viewBox="0 0 1080 1440">
      <defs>
        <filter id={`flow-glow-${startFrame}`} x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      <path
        d={path}
        fill="none"
        stroke={accent}
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={length}
        strokeDashoffset={draw}
        opacity="0.7"
        filter={`url(#flow-glow-${startFrame})`}
      />
      <path d={path} fill="none" stroke="rgba(255,255,255,.5)" strokeWidth="1" strokeLinecap="round" strokeDasharray="6 18" strokeDashoffset={draw * 0.55} opacity="0.48" />
      <circle cx={130 + pulseProgress * 700} cy={300 + pulseProgress * 460} r="0" fill={accent} />
    </svg>
  );
};
