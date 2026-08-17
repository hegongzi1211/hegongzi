import type { CSSProperties } from "react";
import { FocusLayer } from "./FocusSystem";
import { GlassPanel } from "./GlassPanel";

export const FlowNode: React.FC<{
  icon: string;
  title: string;
  description: string;
  status?: string;
  accent?: string;
  startFrame?: number;
  focused?: number;
  dimmed?: boolean;
  style?: CSSProperties;
}> = ({ icon, title, description, status, accent = "#62ffe4", startFrame = 0, focused = 0, dimmed = false, style }) => (
  <FocusLayer active={focused} dimmed={dimmed} style={{ position: "absolute", ...style }}>
    <GlassPanel startFrame={startFrame} accent={accent} focused={focused} width={286}>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: 14,
            display: "grid",
            placeItems: "center",
            color: accent,
            fontSize: 24,
            background: `${accent}14`,
            boxShadow: `inset 0 0 16px ${accent}1f`,
          }}
        >
          {icon}
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 25, fontWeight: 800, letterSpacing: 0, lineHeight: 1.16 }}>{title}</div>
          <div style={{ marginTop: 6, fontSize: 16, color: "rgba(227,255,250,.68)", lineHeight: 1.25 }}>{description}</div>
        </div>
      </div>
      {status ? (
        <div
          style={{
            marginTop: 14,
            display: "inline-flex",
            padding: "6px 10px",
            borderRadius: 999,
            color: accent,
            fontSize: 13,
            fontWeight: 700,
            background: `${accent}12`,
          }}
        >
          {status}
        </div>
      ) : null}
    </GlassPanel>
  </FocusLayer>
);
