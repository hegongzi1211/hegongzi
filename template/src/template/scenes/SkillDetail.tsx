import { AbsoluteFill, useCurrentFrame, spring, useVideoConfig } from "remotion";
import type { SkillDetailScene } from "../types";
import { CinematicBackground } from "../../cinematic/CinematicBackground";

interface Props {
  data: SkillDetailScene;
  frameOffset: number;
}

const BG = "#050608";

export const SkillDetail: React.FC<Props> = ({ data, frameOffset }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - frameOffset;
  const enter = (delay: number) => spring({
    frame: localFrame - delay,
    fps,
    config: { damping: 15, stiffness: 145, mass: 0.5 },
  });

  const headerProgress = enter(9);
  const titleProgress = enter(15);

  return (
    <AbsoluteFill style={{
      backgroundColor: BG,
      padding: "84px 120px 42px",
      color: "#fff",
      fontFamily: "'PingFang SC', sans-serif",
      overflow: "hidden",
    }}>
      <CinematicBackground variant="monitor" />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(2,7,9,.62), rgba(2,7,9,.10) 60%, rgba(2,7,9,.58))" }} />
      <div style={{
        textAlign: "center",
        fontFamily: "monospace",
        fontSize: 24,
        fontWeight: 900,
        color: data.mainColor,
        letterSpacing: 5,
        opacity: headerProgress,
      }}>
        {data.skillNum}
      </div>
      <div style={{ width: 300, height: 4, margin: "14px auto 22px", background: `linear-gradient(90deg, transparent, ${data.mainColor}, transparent)` }} />
      <div style={{ width: 560, height: 8, margin: "0 auto 26px", border: `1px solid ${data.mainColor}88`, borderRadius: 99, padding: 2 }}>
        <div style={{ width: `${34 + headerProgress * 56}%`, height: "100%", borderRadius: 99, background: data.mainColor, boxShadow: `0 0 16px ${data.mainColor}` }} />
      </div>

      <div style={{ marginTop: 44, display: "grid", gridTemplateColumns: "320px 1fr", gap: 24, alignItems: "stretch" }}>
        <div style={{ minHeight: 540, border: `3px solid ${data.mainColor}`, borderRadius: 20, padding: "34px 28px", display: "flex", flexDirection: "column", justifyContent: "space-between", background: `linear-gradient(155deg, ${data.mainColor}20, rgba(2,9,8,.58) 62%)`, backdropFilter: "blur(12px)", boxShadow: `0 0 28px ${data.mainColor}44, inset 0 0 30px ${data.mainColor}12`, opacity: titleProgress, transform: `translateX(${(1 - titleProgress) * -30}px)` }}>
          <div><div style={{ color: data.mainColor, fontFamily: "monospace", fontSize: 18, fontWeight: 900, letterSpacing: 3 }}>核心方法</div><div style={{ marginTop: 30, fontSize: data.skillName.length > 10 ? 47 : 58, lineHeight: 1.08, fontWeight: 950, color: data.mainColor }}>{data.skillName}</div></div>
          <div><div style={{ width: 80, height: 4, marginBottom: 20, background: data.mainColor, boxShadow: `0 0 12px ${data.mainColor}` }} /><div style={{ fontSize: 24, lineHeight: 1.45, fontWeight: 750, color: "rgba(255,255,255,.82)" }}>{data.desc}</div></div>
        </div>

        <div style={{ minHeight: 540, display: "flex", flexDirection: "column", gap: 16 }}>
          {data.details.map((detail, index) => {
            const progress = enter(29 + index * 8);
            return (
              <div key={detail.text} style={{ flex: 1, minHeight: 144, display: "grid", gridTemplateColumns: "52px 1fr", alignItems: "center", gap: 18, padding: "19px 22px", border: `1px solid ${detail.color}88`, borderLeft: `8px solid ${detail.color}`, borderRadius: 14, background: `linear-gradient(90deg, ${detail.color}1f, rgba(4,12,12,.52))`, backdropFilter: "blur(10px)", boxShadow: `0 0 18px ${detail.color}1f`, opacity: progress, transform: `translateX(${(1 - progress) * 35}px)` }}>
                <div style={{ width: 46, height: 46, borderRadius: 99, display: "grid", placeItems: "center", background: detail.color, color: "#04100d", fontSize: 22, fontWeight: 950 }}>{index + 1}</div>
                <div><div style={{ fontSize: 31, fontWeight: 950, color: detail.color }}>{detail.text}</div><div style={{ display: "flex", gap: 8, alignItems: "baseline", marginTop: 8 }}><span style={{ color: "rgba(255,255,255,.5)", fontSize: 16 }}>{detail.label}</span><span style={{ color: "#fff", fontSize: 20, fontWeight: 800 }}>{detail.value}</span></div></div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ marginTop: 44, marginBottom: 184 }}>
        <div style={{ fontSize: 20, color: data.mainColor, fontWeight: 850, letterSpacing: 3, marginBottom: 12 }}>业务闭环</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
          {(data.footerItems ?? []).map((item, index) => {
            const progress = enter(43 + index);
            return (
              <div key={item.label} style={{
                minHeight: 112,
                padding: "16px 18px",
                border: `1px solid ${item.color}88`,
                borderRadius: 10,
                background: `${item.color}12`,
                opacity: progress,
                transform: `translateY(${(1 - progress) * 24}px)`,
              }}>
                <div style={{ fontSize: 17, color: item.color, fontWeight: 900, marginBottom: 8 }}>{item.label}</div>
                <div style={{ fontSize: 23, color: "#fff", fontWeight: 800 }}>{item.value}</div>
              </div>
            );
          })}
        </div>
        {data.supportText ? (
          <div style={{
            marginTop: 24,
            minHeight: 72,
            padding: "12px 20px",
            display: "grid",
            gridTemplateColumns: "1fr 150px 52px",
            alignItems: "center",
            gap: 18,
            color: "rgba(255,255,255,.48)",
            fontSize: 18,
            letterSpacing: 1,
            border: `1px solid ${data.mainColor}44`,
            borderRadius: 12,
            background: "rgba(0,13,11,.42)",
            opacity: enter(48),
          }}>
            <div style={{ textAlign: "center" }}>{data.supportText}</div>
            <div style={{ height: 6, borderRadius: 99, background: "rgba(255,255,255,.09)", overflow: "hidden" }}>
              <div style={{ width: `${55 + enter(50) * 35}%`, height: "100%", borderRadius: 99, background: data.mainColor, boxShadow: `0 0 12px ${data.mainColor}` }} />
            </div>
            <div style={{ fontFamily: "monospace", color: data.mainColor, fontSize: 15 }}>就绪</div>
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
