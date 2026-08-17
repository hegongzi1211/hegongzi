import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { HookScene } from "../types";
import { CinematicBackground } from "../../cinematic/CinematicBackground";

export const Hook: React.FC<{ data: HookScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: frame - 8, fps, config: { damping: 18, stiffness: 130, mass: 0.6 } });
  const sweep = interpolate(frame, [0, 1.6 * fps], [-420, 1080], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CinematicBackground variant="monitor" />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(2,7,9,.72), rgba(2,7,9,.12) 62%, rgba(2,7,9,.54))" }} />
      <div style={{ position: "absolute", left: 72, right: 72, top: 54, height: 1, background: "linear-gradient(90deg, rgba(255,216,61,.6), transparent 46%)" }} />
      <div style={{ position: "absolute", right: 78, top: 68, color: "rgba(255,255,255,.24)", fontFamily: "monospace", fontSize: 12, letterSpacing: 3 }}>OPENING / HOOK</div>
      <div style={{ position: "absolute", top: 224, left: 110, right: 110, textAlign: "center" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 12, color: "#ffd83d", fontSize: 28, fontWeight: 900, letterSpacing: 3 }}><span style={{ width: 44, height: 1, background: "#ffd83d" }} />{data.eyebrow}<span style={{ width: 44, height: 1, background: "#ffd83d" }} /></div>
        <div style={{ fontSize: data.title.length > 14 ? 66 : 80, lineHeight: 1.08, fontWeight: 950, marginTop: 24, opacity: enter, transform: `translateY(${(1 - enter) * 24}px)`, textShadow: "0 10px 34px rgba(0,0,0,.34)" }}>{data.title}</div>
        <div data-design="hook-stage" style={{ position: "relative", width: 820, margin: "74px auto 0", padding: "34px", display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20, border: "1px solid rgba(255,255,255,.10)", borderRadius: 24, background: "linear-gradient(145deg, rgba(4,20,22,.38), rgba(0,0,0,.16))", backdropFilter: "blur(12px)", boxShadow: "0 18px 40px rgba(0,0,0,.2)" }}>
          {data.tags.map((tag, index) => {
            const progress = spring({ frame: frame - 28 - index * 4, fps, config: { damping: 16, stiffness: 140, mass: 0.45 } });
            return <div key={tag.text} style={{ minHeight: 120, display: "flex", alignItems: "center", gap: 18, border: `1px solid ${tag.color}88`, color: "#fff", borderRadius: 16, padding: "18px 22px", fontSize: 25, fontWeight: 850, textAlign: "left", background: `linear-gradient(135deg, ${tag.color}20, rgba(0,0,0,.28))`, boxShadow: `0 12px 24px rgba(0,0,0,.2), inset 4px 0 0 ${tag.color}`, opacity: progress, transform: `translateY(${(1 - progress) * 16}px)` }}><span style={{ color: tag.color, fontFamily: "monospace", fontSize: 14 }}>0{index + 1}</span>{tag.text}</div>;
          })}
        </div>
      </div>
      <div style={{ position: "absolute", left: 150, right: 150, bottom: 286, minHeight: 72, padding: "14px 28px", display: "grid", placeItems: "center", border: "1px solid rgba(255,216,61,.42)", borderRadius: 14, color: "#d9c979", fontSize: 23, fontWeight: 800, letterSpacing: 2, background: "rgba(255,216,61,.05)", boxShadow: "0 0 18px rgba(255,216,61,.10)" }}>{data.subtitle}</div>
      <div style={{ position: "absolute", left: sweep, top: 0, width: 180, height: "100%", background: "linear-gradient(90deg, transparent, rgba(0,255,164,.14), transparent)", transform: "skewX(-12deg)" }} />
    </AbsoluteFill>
  );
};
