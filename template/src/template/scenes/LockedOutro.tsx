import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

const BUTTONS = [
  { color: "#ff2d75", glow: "rgba(255,45,117,.6)", label: "点赞", icon: "♥" },
  { color: "#ff6b00", glow: "rgba(255,107,0,.6)", label: "关注", icon: "+" },
  { color: "#00ffaa", glow: "rgba(0,255,170,.55)", label: "评论", icon: "◆" },
  { color: "#00d4ff", glow: "rgba(0,212,255,.55)", label: "转发", icon: "↗" },
] as const;

export const LockedOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const avatar = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });
  const title = spring({ frame: frame - 12, fps, config: { damping: 16, stiffness: 140 } });
  const subtitleOpacity = interpolate(frame, [22, 36], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scanY = interpolate(frame % 45, [0, 44], [-180, 1500]);
  const glitching = frame % 60 > 42 && frame % 60 < 51;
  const glitchX = glitching ? Math.sin(frame * 2.5) * 3 : 0;

  return (
    <AbsoluteFill style={{ overflow: "hidden", color: "#fff", fontFamily: "'PingFang SC', sans-serif" }}>
      <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 40%, rgba(0,212,255,.10), transparent 34%), radial-gradient(circle at 50% 66%, rgba(255,45,117,.10), transparent 38%)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: scanY, height: 3, background: "linear-gradient(90deg, transparent, rgba(0,255,255,.5), rgba(255,0,200,.5), transparent)", boxShadow: "0 0 22px rgba(0,255,255,.4)" }} />
      {[[40, 40], [960, 40], [40, 1320], [960, 1320]].map(([left, top], i) => <div key={`${left}-${top}`} style={{ position: "absolute", left, top, width: 80, height: 80, borderTop: i < 2 ? "2px solid rgba(0,255,170,.35)" : undefined, borderBottom: i >= 2 ? "2px solid rgba(0,255,170,.35)" : undefined, borderLeft: i % 2 === 0 ? "2px solid rgba(0,255,170,.35)" : undefined, borderRight: i % 2 ? "2px solid rgba(0,255,170,.35)" : undefined }} />)}

      {Array.from({ length: 8 }).map((_, i) => {
        const angle = i / 8 * Math.PI * 2 + t * .3;
        const radius = 380 + Math.sin(t * 1.5 + i) * 60;
        return <div key={i} style={{ position: "absolute", left: 540 + Math.cos(angle) * radius, top: 720 + Math.sin(angle) * radius * .7, width: 4, height: 4, borderRadius: 99, background: i % 2 ? "#ff2d75" : "#00d4ff", boxShadow: `0 0 14px ${i % 2 ? "#ff2d75" : "#00d4ff"}`, opacity: .35 }} />;
      })}

      <div style={{ position: "absolute", left: 420, top: 300, width: 240, height: 240, opacity: avatar, scale: .4 + avatar * .6, translate: `0 ${(1 - avatar) * 50}px` }}>
        <div style={{ position: "absolute", inset: -18, borderRadius: 999, border: "2px solid rgba(0,212,255,.55)", boxShadow: "0 0 24px rgba(0,212,255,.35)", rotate: `${t * 40}deg` }} />
        <div style={{ position: "absolute", inset: -30, borderRadius: 999, border: "1.5px dashed rgba(255,0,180,.38)", rotate: `${-t * 25}deg` }} />
        <div style={{ position: "absolute", inset: -7, borderRadius: 999, border: "3px solid rgba(0,255,170,.65)", boxShadow: "0 0 30px rgba(0,255,170,.38), 0 0 75px rgba(0,255,170,.18)" }} />
        <div style={{ width: "100%", height: "100%", borderRadius: 999, overflow: "hidden", border: "3px solid #e91e8c", background: "#fff", boxShadow: "0 0 35px rgba(233,30,140,.55), 0 0 80px rgba(233,30,140,.25)" }}>
          <Img src={staticFile("outro/avatar.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top center" }} />
        </div>
        <div style={{ marginTop: 16, textAlign: "center", color: "rgba(0,255,170,.58)", fontFamily: "monospace", fontSize: 13, letterSpacing: 2 }}>◆ SYS.ONLINE · AI.CREATOR</div>
      </div>

      <div style={{ position: "absolute", left: 0, right: 0, top: 615, textAlign: "center", opacity: title, translate: `0 ${(1 - title) * 30}px` }}>
        <div style={{ fontSize: 48, fontWeight: 850, letterSpacing: 6, color: "rgba(255,255,255,.86)", marginBottom: 8 }}>我是【你的名字】</div>
        {glitching && <><div style={{ position: "absolute", left: 0, right: 0, top: 58, color: "#ff2d75", fontSize: 100, fontWeight: 950, letterSpacing: 8, translate: `${glitchX + 3}px 0`, opacity: .85 }}>关注我</div><div style={{ position: "absolute", left: 0, right: 0, top: 58, color: "#00d4ff", fontSize: 100, fontWeight: 950, letterSpacing: 8, translate: `${glitchX - 3}px 0`, opacity: .85 }}>关注我</div></>}
        <div style={{ position: "relative", fontSize: 100, fontWeight: 950, letterSpacing: 8, textShadow: "0 0 24px rgba(233,30,140,.65), 0 0 60px rgba(0,212,255,.25)" }}>关注我</div>
        <div style={{ width: 360, height: 2, margin: "8px auto 0", background: "linear-gradient(90deg, transparent, #00d4ff, #ff2d75, #00ffaa, transparent)", boxShadow: "0 0 12px rgba(0,212,255,.5)" }} />
        <div style={{ marginTop: 18, fontSize: 30, fontWeight: 700, letterSpacing: 3, color: "rgba(210,240,255,.86)", opacity: subtitleOpacity }}>学习更多 AI 知识</div>
      </div>

      <div style={{ position: "absolute", left: 0, right: 0, top: 960, display: "flex", justifyContent: "center", gap: 38 }}>
        {BUTTONS.map((button, i) => {
          const progress = spring({ frame: frame - 32 - i * 8, fps, config: { damping: 18, stiffness: 160 } });
          return <div key={button.label} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: progress, scale: .3 + progress * .7, translate: `0 ${(1 - progress) * 25}px` }}><div style={{ width: 76, height: 76, borderRadius: 99, display: "grid", placeItems: "center", border: `2px solid ${button.color}`, color: button.color, fontSize: 32, fontWeight: 900, background: "rgba(0,0,0,.34)", boxShadow: `0 0 20px ${button.glow}, inset 0 0 18px ${button.glow}` }}>{button.icon}</div><div style={{ color: button.color, fontFamily: "monospace", fontSize: 23, fontWeight: 800, letterSpacing: 2 }}>[{button.label}]</div></div>;
        })}
      </div>

      <div style={{ position: "absolute", left: 70, right: 70, bottom: 66, display: "flex", justifyContent: "space-between", fontFamily: "monospace", fontSize: 13, letterSpacing: 2, color: "rgba(0,255,170,.42)" }}><span>// CREATOR</span><span>RENDER · READY</span><span>{Math.floor(t)}s ELAPSED</span></div>
    </AbsoluteFill>
  );
};
