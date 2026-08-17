import type { CaseScene, CompareScene, OverviewScene, ProcessScene, TriangleScene } from "../types";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { AmbientMotion } from "../../cinematic/AmbientMotion";
import { CameraRig } from "../../cinematic/CameraRig";
import { CinematicBackground } from "../../cinematic/CinematicBackground";
import { FlowConnector } from "../../cinematic/FlowConnector";
import { GlassPanel } from "../../cinematic/GlassPanel";
import { getItemReveal, useActiveIndex } from "./LayoutFrame";

const CinematicHeader: React.FC<{ label: string; title: string; subtitle?: string; color?: string }> = ({ label, title, subtitle, color = "#62ffe4" }) => {
  const frame = useCurrentFrame();
  const show = interpolate(frame, [0, 22], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div style={{ position: "absolute", left: 86, top: 112, width: 820, opacity: show, transform: `translateY(${(1 - show) * 18}px) translateZ(120px)` }}>
      <div style={{ color, fontFamily: "monospace", fontSize: 20, fontWeight: 900, letterSpacing: 4 }}>{label}</div>
      <div style={{ width: 210, height: 4, marginTop: 14, background: `linear-gradient(90deg, ${color}, transparent)` }} />
      <div style={{ marginTop: 18, fontSize: title.length > 14 ? 46 : 56, lineHeight: 1.08, fontWeight: 950, textShadow: "0 10px 28px rgba(0,0,0,.34)" }}>{title}</div>
      {subtitle ? <div style={{ marginTop: 12, fontSize: 23, lineHeight: 1.32, color: "rgba(232,255,250,.66)" }}>{subtitle}</div> : null}
    </div>
  );
};

const CinematicSupport: React.FC<{ text?: string; color?: string }> = ({ text, color = "#62ffe4" }) => {
  if (!text) return null;
  return (
    <GlassPanel
      startFrame={46}
      accent={color}
      focused={0.15}
      width={760}
      style={{ position: "absolute", left: 160, bottom: 286, minHeight: 82, padding: "18px 26px", transform: "perspective(1000px) rotateX(7deg) rotateY(-4deg) translateZ(80px)" }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <div style={{ color, fontFamily: "monospace", fontSize: 13, fontWeight: 900, letterSpacing: 2 }}>KEY POINT</div>
        <div style={{ flex: 1, textAlign: "center", fontSize: 22, color: "rgba(238,255,252,.76)" }}>{text}</div>
      </div>
    </GlassPanel>
  );
};

export const OverviewLayout: React.FC<{ data: OverviewScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const active = useActiveIndex(data.durationFrames, data.items.length, data.itemStartFrames);
  const indexed = data.layoutVariant === "index";
  const spotlight = data.layoutVariant === "spotlight";
  const positions = indexed
    ? data.items.map((_, i) => ({ left: i % 2 === 0 ? 116 : 462, top: 420 + i * 128, width: i % 2 === 0 ? 450 : 472, rotate: i % 2 === 0 ? -5 : 5 }))
    : spotlight
      ? data.items.map((_, i) => i === 0
        ? { left: 110, top: 404, width: 500, rotate: -7 }
        : { left: 616, top: 394 + (i - 1) * 174, width: 354, rotate: 5 })
      : data.items.map((_, i) => ({ left: i % 2 === 0 ? 108 : 552, top: 420 + Math.floor(i / 2) * 202, width: i === active ? 420 : 392, rotate: i % 2 === 0 ? -6 : 6 }));

  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement={spotlight ? "focus" : "pushIn"} intensity={0.28}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}>
            <CinematicBackground variant="monitor" />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(-120px)" }}>
            <div style={{ position: "absolute", left: 88, top: 182, width: 910, height: 790, borderRadius: 34, border: "1px solid rgba(98,255,228,.08)", background: "linear-gradient(180deg, rgba(4,12,14,.18), rgba(3,8,8,.04))", boxShadow: "inset 0 0 60px rgba(0,0,0,.16)" }} />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <CinematicHeader label={data.label} title={data.title} subtitle={data.subtitle} />
            {data.items.map((item, i) => {
              const show = getItemReveal(frame, i, data.items.length, data.durationFrames);
              const focus = i === active ? 1 : 0;
              const position = positions[i] ?? { left: 120, top: 380, width: 380, rotate: 0 };
              return (
                <AmbientMotion key={item.title} amount={2.2 + i * 0.2} rotate={0.16} speed={74 + i * 6} style={{ position: "absolute", left: position.left, top: position.top }}>
                  <div style={{ opacity: show, transform: `translateZ(${focus * 56 + i * 12}px) scale(${1 + focus * 0.045}) rotateY(${position.rotate}deg) rotateX(3deg)`, filter: `brightness(${focus ? 1.25 : 0.78})` }}>
                    <GlassPanel startFrame={10 + i * 10} accent={item.color} focused={focus} width={position.width} style={{ minHeight: spotlight && i === 0 ? 178 : indexed ? 132 : 146 }}>
                      <div style={{ color: item.color, fontSize: spotlight && i === 0 ? 22 : 17, fontFamily: "monospace", fontWeight: 900 }}>0{i + 1}</div>
                      <div style={{ marginTop: 10, fontSize: spotlight && i === 0 ? 40 : indexed ? 25 : 29, lineHeight: 1.14, fontWeight: 950 }}>{item.title}</div>
                      {item.note ? <div style={{ marginTop: 10, fontSize: spotlight && i === 0 ? 20 : 17, lineHeight: 1.38, color: "rgba(235,255,251,.62)" }}>{item.note}</div> : null}
                    </GlassPanel>
                  </div>
                </AmbientMotion>
              );
            })}
            <CinematicSupport text={data.supportText} />
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};

const CompareSide: React.FC<{ side: CompareScene["left"]; index: number; activePoint: number; durationFrames: number }> = ({ side, index, activePoint, durationFrames }) => {
  const frame = useCurrentFrame();
  const show = getItemReveal(frame, index, 2, durationFrames);
  const focused = activePoint % 2 === index ? 1 : 0.15;
  return (
    <AmbientMotion amount={2.8} rotate={0.16} speed={78 + index * 8} style={{ position: "absolute", left: index === 0 ? 92 : 550, top: 410 }}>
      <div style={{ opacity: show, transform: `translateZ(${focused * 58}px) rotateY(${index === 0 ? -8 : 8}deg) rotateX(3deg) scale(${1 + focused * 0.045})`, filter: `brightness(${focused ? 1.25 : 0.78})` }}>
        <GlassPanel startFrame={14 + index * 10} accent={side.color} focused={focused} width={430} style={{ minHeight: 520 }}>
          <div style={{ color: side.color, fontFamily: "monospace", fontSize: 18, fontWeight: 900 }}>{index === 0 ? "LEFT" : "RIGHT"}</div>
          <div style={{ marginTop: 14, fontSize: 44, color: side.color, fontWeight: 950, textShadow: `0 0 18px ${side.color}66`, lineHeight: 1.05, wordBreak: "break-word" }}>{side.title}</div>
          <div style={{ fontSize: 19, color: "rgba(235,255,251,.58)", marginTop: 9 }}>{side.subtitle}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 32 }}>
            {side.points.slice(0, 4).map((point, i) => {
              const itemShow = getItemReveal(frame, i + 1, side.points.length + 1, durationFrames);
              const active = i === activePoint || activePoint % Math.max(1, side.points.length) === i;
              return (
                <div key={point} style={{ border: `1px solid ${side.color}${active ? "cc" : "44"}`, borderRadius: 12, padding: "14px 16px", fontSize: 21, lineHeight: 1.25, fontWeight: 850, background: active ? `${side.color}1e` : "rgba(0,0,0,.20)", opacity: itemShow, transform: `translateY(${(1 - itemShow) * 18}px)`, filter: `brightness(${active ? 1.22 : 0.8})` }}>
                  <span style={{ color: side.color, marginRight: 10 }}>{i + 1}</span>{point}
                </div>
              );
            })}
          </div>
        </GlassPanel>
      </div>
    </AmbientMotion>
  );
};

export const CompareLayout: React.FC<{ data: CompareScene }> = ({ data }) => {
  const activePoint = useActiveIndex(data.durationFrames, Math.max(data.left.points.length, data.right.points.length, 2));
  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement="smallOrbit" intensity={0.22}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}><CinematicBackground variant="wide" /></AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(-120px)" }}>
            <div style={{ position: "absolute", left: 88, top: 182, width: 910, height: 790, borderRadius: 34, border: "1px solid rgba(98,255,228,.08)", background: "linear-gradient(180deg, rgba(4,12,14,.18), rgba(3,8,8,.04))", boxShadow: "inset 0 0 60px rgba(0,0,0,.16)" }} />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <CinematicHeader label={data.label} title={data.title} color={data.left.color} />
            <svg style={{ position: "absolute", inset: 0, overflow: "visible" }} viewBox="0 0 1080 1440">
              <path d="M540 350 C512 520, 512 760, 540 1015" fill="none" stroke="rgba(255,255,255,.16)" strokeWidth="2" strokeDasharray="8 14" />
            </svg>
            <CompareSide side={data.left} index={0} activePoint={activePoint} durationFrames={data.durationFrames} />
            <CompareSide side={data.right} index={1} activePoint={activePoint} durationFrames={data.durationFrames} />
            <div style={{ position: "absolute", left: 502, top: 650, width: 76, height: 76, display: "grid", placeItems: "center", borderRadius: 999, color: "#fff", fontFamily: "monospace", fontSize: 18, fontWeight: 950, border: "1px solid rgba(255,255,255,.28)", background: "rgba(3,8,7,.86)", boxShadow: "0 0 30px rgba(98,255,228,.22)", transform: "translateZ(80px)" }}>VS</div>
            <CinematicSupport text={data.supportText} color={data.left.color} />
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};

export const ProcessLayout: React.FC<{ data: ProcessScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const active = useActiveIndex(data.durationFrames, data.steps.length);
  const positions = data.steps.map((_, i) => ({ left: i % 2 === 0 ? 98 : 560, top: 382 + i * 126, width: 390, rotate: i % 2 === 0 ? -7 : 7 }));

  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement="panRight" intensity={0.24}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}>
            <CinematicBackground variant="desk" />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(-120px)" }}>
            <div style={{ position: "absolute", left: 88, top: 182, width: 910, height: 790, borderRadius: 34, border: "1px solid rgba(98,255,228,.08)", background: "linear-gradient(180deg, rgba(4,12,14,.18), rgba(3,8,8,.04))", boxShadow: "inset 0 0 60px rgba(0,0,0,.16)" }} />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <CinematicHeader label={data.label} title={data.title} subtitle={data.subtitle} color={data.steps[0]?.color} />
            {data.steps.slice(0, positions.length).map((step, i) => {
              const show = getItemReveal(frame, i, data.steps.length, data.durationFrames);
              const focus = i === active ? 1 : 0;
              const position = positions[i];
              const next = positions[i + 1];
              return (
                <div key={step.title}>
                  {next ? (
                    <FlowConnector
                      path={`M ${position.left + 270} ${position.top + 70} C ${(position.left + next.left) / 2 + 110} ${(position.top + next.top) / 2 - 42}, ${(position.left + next.left) / 2 - 110} ${(position.top + next.top) / 2 + 44}, ${next.left + 120} ${next.top + 70}`}
                      startFrame={24 + i * 14}
                      length={360}
                      accent={step.color}
                    />
                  ) : null}
                  <AmbientMotion amount={2.4 + i * 0.2} rotate={0.16} speed={78 + i * 6} style={{ position: "absolute", left: position.left, top: position.top }}>
                    <div style={{ opacity: show, transform: `translateZ(${focus * 58 + i * 10}px) scale(${1 + focus * 0.045}) rotateY(${position.rotate}deg) rotateX(3deg)`, filter: `brightness(${focus ? 1.28 : 0.76})` }}>
                      <GlassPanel startFrame={10 + i * 10} accent={step.color} focused={focus} width={position.width}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                          <span style={{ color: step.color, fontSize: 18, fontFamily: "monospace", fontWeight: 900 }}>STEP 0{i + 1}</span>
                          <span style={{ width: 42, height: 42, display: "grid", placeItems: "center", borderRadius: 99, background: step.color, color: "#06100f", fontFamily: "monospace", fontWeight: 950 }}>{i + 1}</span>
                        </div>
                        <div style={{ marginTop: 14, fontSize: 29, lineHeight: 1.14, fontWeight: 950 }}>{step.title}</div>
                        {step.note ? <div style={{ marginTop: 9, fontSize: 17, lineHeight: 1.36, color: "rgba(235,255,251,.62)" }}>{step.note}</div> : null}
                      </GlassPanel>
                    </div>
                  </AmbientMotion>
                </div>
              );
            })}
            <CinematicSupport text={data.supportText} color={data.steps[active]?.color} />
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};

export const CaseLayout: React.FC<{ data: CaseScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const active = useActiveIndex(data.durationFrames, data.columns.length);
  const positions = [{ left: 88, top: 440, rotate: -9 }, { left: 382, top: 560, rotate: 0 }, { left: 676, top: 690, rotate: 9 }];
  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement="pushIn" intensity={0.24}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}><CinematicBackground variant="monitor" /></AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(-120px)" }}>
            <div style={{ position: "absolute", left: 88, top: 182, width: 910, height: 790, borderRadius: 34, border: "1px solid rgba(98,255,228,.08)", background: "linear-gradient(180deg, rgba(4,12,14,.18), rgba(3,8,8,.04))", boxShadow: "inset 0 0 60px rgba(0,0,0,.16)" }} />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <CinematicHeader label={data.label} title={data.title} color={data.columns[0]?.color} />
            {data.columns.slice(0, 3).map((column, i) => {
              const show = getItemReveal(frame, i, data.columns.length, data.durationFrames);
              const focus = i === active ? 1 : 0.12;
              const position = positions[i] ?? positions[0];
              return (
                <AmbientMotion key={column.label} amount={2.6 + i * 0.2} rotate={0.18} speed={78 + i * 7} style={{ position: "absolute", left: position.left, top: position.top }}>
                  <div style={{ opacity: show, transform: `translateZ(${i * 26 + focus * 58}px) rotateY(${position.rotate}deg) rotateX(3deg) scale(${1 + focus * 0.05})`, filter: `brightness(${focus ? 1.25 : 0.78})` }}>
                    <GlassPanel startFrame={12 + i * 12} accent={column.color} focused={focus} width={320} style={{ minHeight: i === 1 ? 350 : 310 }}>
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <span style={{ color: column.color, fontFamily: "monospace", fontSize: 17, fontWeight: 900 }}>{column.label}</span>
                        <span style={{ fontSize: 48, color: `${column.color}66`, fontWeight: 950 }}>0{i + 1}</span>
                      </div>
                      <div style={{ marginTop: 36, fontSize: 32, lineHeight: 1.14, fontWeight: 950 }}>{column.title}</div>
                      <div style={{ width: 74, height: 3, margin: "22px 0", background: column.color, boxShadow: `0 0 12px ${column.color}` }} />
                      {column.note ? <div style={{ fontSize: 19, lineHeight: 1.42, color: "rgba(235,255,251,.64)" }}>{column.note}</div> : null}
                    </GlassPanel>
                  </div>
                </AmbientMotion>
              );
            })}
            <CinematicSupport text={data.supportText} color={data.columns[active]?.color} />
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};

export const TriangleLayout: React.FC<{ data: TriangleScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const active = useActiveIndex(data.durationFrames, data.nodes.length);
  const positions = [{ left: 98, top: 424, rotate: -8 }, { left: 628, top: 424, rotate: 8 }, { left: 360, top: 794, rotate: 0 }];
  return (
    <AbsoluteFill style={{ color: "white", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement="focus" intensity={0.24}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}><CinematicBackground variant="wide" /></AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(-120px)" }}>
            <div style={{ position: "absolute", left: 88, top: 182, width: 910, height: 790, borderRadius: 34, border: "1px solid rgba(98,255,228,.08)", background: "linear-gradient(180deg, rgba(4,12,14,.18), rgba(3,8,8,.04))", boxShadow: "inset 0 0 60px rgba(0,0,0,.16)" }} />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <CinematicHeader label={data.label} title={data.title} color="#E4EF37" />
            <svg style={{ position: "absolute", inset: 0, filter: "drop-shadow(0 0 10px rgba(228,239,55,.16))" }} viewBox="0 0 1080 1440">
              <path d="M238 540 L540 655 L842 540 L540 910 Z" fill="rgba(228,239,55,.025)" stroke="rgba(228,239,55,.20)" strokeWidth="2" strokeDasharray="8 12" />
            </svg>
            <div style={{ position: "absolute", left: 420, top: 605, width: 240, height: 240, borderRadius: 999, display: "grid", placeItems: "center", textAlign: "center", border: "1px solid #E4EF37", background: "radial-gradient(circle, rgba(228,239,55,.22), rgba(5,9,7,.86) 68%)", boxShadow: "0 0 40px rgba(228,239,55,.26), inset 0 0 24px rgba(228,239,55,.12)", fontSize: 30, lineHeight: 1.16, fontWeight: 950, transform: "translateZ(78px)" }}>
              <div><div style={{ color: "#E4EF37", fontFamily: "monospace", fontSize: 12, letterSpacing: 2, marginBottom: 9 }}>CORE</div>{data.center}</div>
            </div>
            {data.nodes.slice(0, 3).map((node, i) => {
              const show = getItemReveal(frame, i, data.nodes.length, data.durationFrames);
              const focus = i === active ? 1 : 0.12;
              const position = positions[i] ?? positions[0];
              return (
                <AmbientMotion key={node.title} amount={2.4 + i * 0.25} rotate={0.18} speed={78 + i * 7} style={{ position: "absolute", left: position.left, top: position.top }}>
                  <div style={{ opacity: show, transform: `translateZ(${focus * 58 + i * 18}px) rotateY(${position.rotate}deg) rotateX(3deg) scale(${1 + focus * 0.045})`, filter: `brightness(${focus ? 1.28 : 0.76})` }}>
                    <GlassPanel startFrame={14 + i * 10} accent={node.color} focused={focus} width={330} style={{ minHeight: 164, textAlign: "center" }}>
                      <div style={{ fontSize: 34, color: node.color, fontWeight: 950, textShadow: `0 0 16px ${node.color}66`, lineHeight: 1.1 }}>{node.title}</div>
                      {node.note ? <div style={{ fontSize: 18, color: "rgba(235,255,251,.58)", marginTop: 10, lineHeight: 1.36 }}>{node.note}</div> : null}
                    </GlassPanel>
                  </div>
                </AmbientMotion>
              );
            })}
            <CinematicSupport text={data.supportText} color="#E4EF37" />
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};
