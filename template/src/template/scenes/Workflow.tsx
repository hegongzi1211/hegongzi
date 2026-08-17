import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import type { WorkflowScene } from "../types";
import { AmbientMotion } from "../../cinematic/AmbientMotion";
import { CinematicBackground } from "../../cinematic/CinematicBackground";
import { CameraRig } from "../../cinematic/CameraRig";
import { FlowConnector } from "../../cinematic/FlowConnector";
import { GlassPanel } from "../../cinematic/GlassPanel";

export const Workflow: React.FC<{ data: WorkflowScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const compact = data.steps.length > 4;
  const active = Math.min(
    data.steps.length - 1,
    Math.max(0, Math.floor(interpolate(frame, [0, data.durationFrames * 0.72], [0, data.steps.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }))),
  );
  const titleReveal = interpolate(frame, [0, 22], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const positions = compact
    ? [
      { left: 82, top: 380 },
      { left: 440, top: 488 },
      { left: 146, top: 608 },
      { left: 504, top: 728 },
      { left: 220, top: 854 },
      { left: 560, top: 982 },
    ]
    : [
      { left: 114, top: 410 },
      { left: 470, top: 560 },
      { left: 170, top: 725 },
      { left: 520, top: 890 },
    ];

  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement="pushIn" intensity={0.34}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}>
            <CinematicBackground variant="desk" />
          </AbsoluteFill>

          <AbsoluteFill style={{ transform: "translateZ(-100px)" }}>
            <div style={{ position: "absolute", left: 95, top: 172, width: 895, height: 840, borderRadius: 34, border: "1px solid rgba(98,255,228,.08)", background: "linear-gradient(180deg, rgba(4,12,14,.18), rgba(3,8,8,.04))", boxShadow: "inset 0 0 60px rgba(0,0,0,.16)" }} />
            <div style={{ position: "absolute", left: 175, bottom: 250, width: 730, height: 86, borderRadius: 20, background: "linear-gradient(180deg, rgba(255,195,95,.26), rgba(5,8,7,.7))", filter: "blur(.2px)", transform: "rotateX(58deg)" }} />
          </AbsoluteFill>

          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <div style={{ position: "absolute", left: 88, top: 116, width: 780, opacity: titleReveal, transform: `translateY(${(1 - titleReveal) * 16}px)` }}>
              <div style={{ color: "#62ffe4", fontFamily: "monospace", fontSize: 20, fontWeight: 900, letterSpacing: 4 }}>WORKFLOW / 2.5D</div>
              <div style={{ width: 210, height: 4, marginTop: 14, background: "linear-gradient(90deg,#62ffe4,transparent)" }} />
              <div style={{ marginTop: 18, fontSize: data.title.length > 14 ? 46 : 56, lineHeight: 1.08, fontWeight: 950, textShadow: "0 10px 28px rgba(0,0,0,.34)" }}>{data.title}</div>
              {data.subtitleText ? <div style={{ marginTop: 12, fontSize: 23, color: "rgba(232,255,250,.66)" }}>{data.subtitleText}</div> : null}
            </div>

            <svg style={{ position: "absolute", inset: 0, overflow: "visible", opacity: 0.28 }} viewBox="0 0 1080 1440">
              <path d="M 104 1090 C 310 984, 582 1030, 872 908" fill="none" stroke="rgba(98,255,228,.5)" strokeWidth="1" strokeDasharray="7 16" />
              <path d="M 178 358 C 418 244, 690 290, 886 422" fill="none" stroke="rgba(255,200,107,.22)" strokeWidth="1" />
            </svg>

            {data.steps.slice(0, positions.length).map((step, index) => {
              const from = 22 + index * Math.max(12, Math.round(data.durationFrames * 0.075));
              const focus = index === active ? 1 : 0;
              const dim = index < active - 1 ? 0.48 : 1;
              const position = positions[index];
              const next = positions[index + 1];
              return (
                <div key={`${step.number}-${step.title}`}>
                  {next ? (
                    <FlowConnector
                      path={`M ${position.left + 150} ${position.top + 68} C ${(position.left + next.left) / 2 + 80} ${(position.top + next.top) / 2 - 36}, ${(position.left + next.left) / 2 - 80} ${(position.top + next.top) / 2 + 44}, ${next.left + 68} ${next.top + 62}`}
                      startFrame={from + 12}
                      length={360}
                      accent={step.color}
                    />
                  ) : null}
                  <AmbientMotion amount={2.4 + index * 0.25} rotate={0.16} speed={76 + index * 7} style={{ position: "absolute", left: position.left, top: position.top }}>
                    <div style={{ opacity: dim, transform: `translateZ(${focus * 54 + index * 8}px) scale(${1 + focus * 0.045}) rotateY(${index % 2 === 0 ? -6 : 6}deg) rotateX(3deg)`, filter: `brightness(${focus ? 1.28 : 0.82})` }}>
                      <GlassPanel startFrame={from} accent={step.color} focused={focus} width={compact ? 316 : 360}>
                        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                          <div style={{ width: 50, height: 50, borderRadius: 15, display: "grid", placeItems: "center", color: "#06100f", background: step.color, boxShadow: `0 0 22px ${step.color}70`, fontFamily: "monospace", fontSize: 18, fontWeight: 950 }}>{step.number}</div>
                          <div style={{ minWidth: 0 }}>
                            <div style={{ fontSize: compact ? 25 : 30, lineHeight: 1.14, fontWeight: 950 }}>{step.title}</div>
                            {step.subtitle ? <div style={{ marginTop: 7, fontSize: compact ? 16 : 18, lineHeight: 1.28, color: "rgba(234,255,251,.68)", fontWeight: 700 }}>{step.subtitle}</div> : null}
                          </div>
                        </div>
                      </GlassPanel>
                    </div>
                  </AmbientMotion>
                </div>
              );
            })}

            <GlassPanel
              startFrame={Math.round(data.durationFrames * 0.58)}
              accent="#62ffe4"
              focused={0.25}
              width={760}
              style={{
                position: "absolute",
                left: 160,
                bottom: 286,
                minHeight: 86,
                padding: "18px 26px",
                transform: "perspective(1000px) rotateX(7deg) rotateY(-4deg) translateZ(80px)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
                <div style={{ color: "#62ffe4", fontFamily: "monospace", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>KEY POINT</div>
                <div style={{ flex: 1, textAlign: "center", fontSize: 22, color: "rgba(238,255,252,.76)" }}>{data.subtitleText ?? "流程不是一次铺满，而是随着口播一步步生成。"}</div>
              </div>
            </GlassPanel>
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};
