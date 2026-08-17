import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export const COLORS = ["#39FF14", "#00FFFF", "#FF1493", "#8A5CFF", "#FFA500", "#E4EF37"];

export const useReveal = (delaySeconds = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return interpolate(frame, [delaySeconds * fps, (delaySeconds + 0.42) * fps], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

export const useActiveIndex = (durationInFrames: number, count: number, activeFrames?: number[]) => {
  const frame = useCurrentFrame();
  if (activeFrames && activeFrames.length > 0) {
    let idx = 0;
    for (let i = 0; i < activeFrames.length; i++) {
      if (frame >= activeFrames[i]) idx = i;
    }
    return Math.min(count - 1, idx);
  }
  const start = Math.round(durationInFrames * 0.0);
  const end = Math.round(durationInFrames * 0.72);
  const progress = Math.max(0, Math.min(0.999, (frame - start) / Math.max(1, end - start)));
  return Math.min(count - 1, Math.floor(progress * count));
};

export const getItemReveal = (frame: number, index: number, count: number, durationInFrames: number) => {
  const start = Math.round(durationInFrames * (0.0 + index * (0.18 / Math.max(1, count))));
  return interpolate(frame, [start, start + 10], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

export const LayoutFrame: React.FC<{
  label: string;
  title: string;
  subtitle?: string;
  color?: string;
  supportText?: string;
  variant?: "overview" | "compare" | "process" | "case" | "radial";
  children: React.ReactNode;
}> = ({ label, title, subtitle, color = "#39FF14", supportText, variant = "overview", children }) => {
  const head = useReveal(0.08);
  const support = useReveal(0.9);
  const leftAligned = variant === "overview" || variant === "process";
  const titlePanel = variant === "compare";
  const compact = variant === "radial";
  const showInnerFrame = variant === "overview";
  return (
    <div style={{ position: "absolute", inset: 0, padding: `${compact ? 54 : 68}px ${variant === "case" ? 82 : variant === "compare" ? 86 : 120}px 245px`, color: "#fff", fontFamily: "'PingFang SC', sans-serif" }}>
      <div style={{ position: "absolute", left: 72, right: 72, top: 42, height: 1, background: `linear-gradient(90deg, ${color}55, transparent 42%, rgba(255,255,255,.04), transparent)` }} />
      <div style={{ position: "absolute", right: 78, top: 55, color: "rgba(255,255,255,.24)", fontFamily: "monospace", fontSize: 12, letterSpacing: 3 }}>HGZ / {variant.toUpperCase()}</div>
      <div style={{ maxWidth: leftAligned ? 820 : undefined, margin: leftAligned ? 0 : "0 auto", padding: titlePanel ? "24px 32px" : 0, border: titlePanel ? `1px solid ${color}cc` : undefined, borderRadius: titlePanel ? 20 : undefined, background: titlePanel ? `linear-gradient(120deg, ${color}13, rgba(0,0,0,.18), transparent)` : undefined, boxShadow: titlePanel ? `0 14px 34px rgba(0,0,0,.2), 0 0 28px ${color}25, inset 0 1px 0 rgba(255,255,255,.06)` : undefined }}>
        <div style={{ textAlign: leftAligned ? "left" : "center", color, fontFamily: "monospace", fontSize: 24, fontWeight: 900, letterSpacing: 5, opacity: head }}>{label}</div>
        <div style={{ width: leftAligned ? 180 : 300, height: 4, margin: leftAligned ? "14px 0 20px" : "14px auto 20px", background: `linear-gradient(90deg, ${leftAligned ? color : "transparent"}, ${color}, transparent)` }} />
        <div style={{ textAlign: leftAligned ? "left" : "center", fontSize: title.length > 13 ? 50 : leftAligned ? 68 : 60, lineHeight: 1.08, fontWeight: 950, letterSpacing: -1.5, opacity: head, transform: `translateY(${(1 - head) * 18}px)`, color: titlePanel ? color : "#fff", textShadow: "0 8px 28px rgba(0,0,0,.32)" }}>{title}</div>
        {subtitle ? <div style={{ textAlign: leftAligned ? "left" : "center", marginTop: 12, fontSize: 24, color: "rgba(255,255,255,.66)", opacity: head }}>{subtitle}</div> : null}
      </div>
      <div style={{ position: "relative", marginTop: titlePanel ? 28 : compact ? 22 : variant === "case" ? 20 : 34, minHeight: compact ? 770 : variant === "case" ? 690 : 720, display: "flex", flexDirection: "column", justifyContent: "center" }}>
        {showInnerFrame ? <div style={{ position: "absolute", inset: "-18px -22px", border: "1px solid rgba(255,255,255,.035)", borderRadius: 24, background: "linear-gradient(180deg, rgba(255,255,255,.018), rgba(0,0,0,.03))", pointerEvents: "none" }} /> : null}
        {children}
      </div>
      {supportText ? (
        <div style={{ position: "absolute", left: 120, right: 120, bottom: 286, minHeight: 72, padding: "14px 24px", display: "flex", alignItems: "center", gap: 18, opacity: support, color: "rgba(255,255,255,.7)", fontSize: 22, border: `1px solid ${color}48`, borderRadius: 14, background: "linear-gradient(90deg, rgba(0,13,11,.72), rgba(4,8,7,.5))", boxShadow: `0 12px 28px rgba(0,0,0,.22), 0 0 18px ${color}10` }}>
          <div style={{ color, fontFamily: "monospace", fontSize: 12, letterSpacing: 2 }}>KEY POINT</div>
          <div style={{ flex: 1, textAlign: "center" }}>{supportText}</div>
          <div style={{ width: 150, height: 5, borderRadius: 99, background: "rgba(255,255,255,.1)" }}><div style={{ width: "72%", height: "100%", borderRadius: 99, background: color, boxShadow: `0 0 12px ${color}` }} /></div>
        </div>
      ) : null}
    </div>
  );
};
