import type { CSSProperties } from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AmbientMotion } from "./AmbientMotion";

export const FloatingScreenshot: React.FC<{
  startFrame?: number;
  focused?: number;
  width?: number;
  style?: CSSProperties;
}> = ({ startFrame = 0, focused = 0, width = 390, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - startFrame;
  const enter = spring({ frame: localFrame, fps, config: { damping: 20, stiffness: 70, mass: 0.9 } });
  const opacity = interpolate(localFrame, [0, 18], [0, 1], {
    easing: Easing.out(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AmbientMotion amount={3.4} rotate={0.22} speed={92} style={{ position: "absolute", ...style }}>
      <div
        style={{
          width,
          height: width * 1.33,
          opacity,
          borderRadius: 22,
          overflow: "hidden",
          background: "rgba(235,247,244,.96)",
          boxShadow: `0 34px 90px rgba(0,0,0,.45), 0 0 ${22 + focused * 24}px rgba(98,255,228,.24)`,
          transform: `perspective(1100px) translate3d(${(1 - enter) * 220}px, ${(1 - enter) * 42}px, ${-90 + enter * 120 + focused * 30}px) rotateX(${12 - enter * 8}deg) rotateY(${-28 + enter * 16}deg) rotateZ(${5 - enter * 5}deg) scale(${0.78 + enter * 0.22})`,
        }}
      >
        <div style={{ height: 42, background: "#101716", display: "flex", alignItems: "center", gap: 8, paddingLeft: 16 }}>
          {["#ff5f57", "#ffbd2e", "#28c840"].map((color) => (
            <div key={color} style={{ width: 12, height: 12, borderRadius: 999, background: color }} />
          ))}
          <div style={{ marginLeft: 12, width: 190, height: 14, borderRadius: 999, background: "rgba(255,255,255,.12)" }} />
        </div>
        <div style={{ padding: 24, color: "#10211f" }}>
          <div style={{ fontSize: 26, fontWeight: 900, lineHeight: 1.18 }}>解析结果</div>
          <div style={{ marginTop: 8, fontSize: 15, color: "rgba(16,33,31,.62)" }}>video-analysis.md</div>
          <div style={{ marginTop: 28, display: "grid", gap: 14 }}>
            {["音频转写完成", "关键画面识别", "流程摘要生成", "知识库同步"].map((item, index) => (
              <div key={item} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 28, height: 28, borderRadius: 9, background: index === 3 ? "#1ed6a3" : "#d9ebe7" }} />
                <div style={{ height: 15, flex: 1, borderRadius: 999, background: index === 3 ? "rgba(30,214,163,.32)" : "#d9ebe7" }} />
              </div>
            ))}
          </div>
          <div style={{ marginTop: 34, height: width * 0.48, borderRadius: 18, background: "linear-gradient(135deg, rgba(30,214,163,.20), rgba(9,35,32,.06))", border: "1px solid rgba(16,33,31,.08)" }} />
        </div>
      </div>
    </AmbientMotion>
  );
};
