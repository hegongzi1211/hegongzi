import { AbsoluteFill, useCurrentFrame, spring } from "remotion";
import type { OutroScene } from "../types";

interface Props {
  data: OutroScene;
  frameOffset: number;
}

const BG = "#050608";

export const Outro: React.FC<Props> = ({ data, frameOffset }) => {
  const frame = useCurrentFrame();
  const localFrame = frame - frameOffset;

  const nameProg = spring({ frame: localFrame - 10, fps: 30, config: { damping: 14, stiffness: 150, mass: 0.5 } });
  const ctaProg = spring({ frame: localFrame - 30, fps: 30, config: { damping: 14, stiffness: 130, mass: 0.5 } });
  const lineProg = spring({ frame: localFrame - 20, fps: 30, config: { damping: 12, stiffness: 120, mass: 0.4 } });

  return (
    <AbsoluteFill style={{
      background: `
        radial-gradient(circle at 50% 40%, ${data.mainColor}20 0%, transparent 60%),
        radial-gradient(circle at 50% 80%, ${data.mainColor}10 0%, transparent 50%),
        ${BG}
      `,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      color: "#fff", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden",
    }}>

      {/* Decorative line */}
      <div style={{
        width: 120, height: 3, borderRadius: 2, background: data.mainColor,
        marginBottom: 30, boxShadow: `0 0 20px ${data.mainColor}60`,
        opacity: lineProg, transform: `scaleX(${lineProg})`,
      }} />

      {/* User name */}
      <div style={{
        fontSize: 52, fontWeight: 900, color: "#fff", letterSpacing: 4, marginBottom: 12,
        opacity: nameProg, transform: `translateY(${(1 - nameProg) * 20}px)`,
      }}>
        {data.userName}
      </div>

      {/* CTA text */}
      <div style={{
        fontSize: 20, color: data.mainColor, fontWeight: 600, letterSpacing: 2,
        opacity: ctaProg, transform: `translateY(${(1 - ctaProg) * 15}px)`,
      }}>
        {data.ctaText}
      </div>

      {/* Decorative line bottom */}
      <div style={{
        width: 80, height: 2, borderRadius: 1, background: data.mainColor,
        marginTop: 30, boxShadow: `0 0 15px ${data.mainColor}40`,
        opacity: spring({ frame: localFrame - 40, fps: 30, config: { damping: 14, stiffness: 120, mass: 0.4 } }),
        transform: `scaleX(${spring({ frame: localFrame - 40, fps: 30, config: { damping: 14, stiffness: 120, mass: 0.4 } })})`,
      }} />

    </AbsoluteFill>
  );
};
