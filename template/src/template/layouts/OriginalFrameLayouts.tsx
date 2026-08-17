import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { CaseScene, CompareScene, OverviewScene, ProcessScene, TriangleScene } from "../types";

type FramedScene = OverviewScene | CompareScene | ProcessScene | CaseScene | TriangleScene;
const ACCENTS = ["#39FF14", "#00FFFF", "#FF1493", "#8A5CFF", "#FFA500", "#E4EF37"];

const useEnter = (delay: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: { damping: 16, stiffness: 145, mass: .55 } });
};

const useFocus = (duration: number, count: number) => {
  const frame = useCurrentFrame();
  const progress = Math.max(0, Math.min(.999, (frame - duration * .2) / Math.max(1, duration * .62)));
  return Math.min(count - 1, Math.floor(progress * count));
};

const getMeta = (data: FramedScene) => {
  if (data.type === "overview") return { chips: data.items.slice(0, 3).map((x) => x.title), color: data.items[0]?.color ?? ACCENTS[0], subtitle: data.subtitle };
  if (data.type === "compare") return { chips: [data.left.title, data.right.title, "效率差距"], color: data.right.color, subtitle: `${data.left.subtitle} → ${data.right.subtitle}` };
  if (data.type === "process") return { chips: data.steps.slice(0, 3).map((x) => x.title), color: data.steps[0]?.color ?? ACCENTS[0], subtitle: data.subtitle };
  if (data.type === "case") return { chips: data.columns.map((x) => x.label), color: data.columns[0]?.color ?? ACCENTS[2], subtitle: "问题 → 做法 → 结果" };
  return { chips: data.nodes.map((x) => x.title), color: data.nodes[0]?.color ?? ACCENTS[5], subtitle: "三个因素，共同支撑稳定结果" };
};

const titleSize = (title: string) => {
  if (title.length > 20) return 38;
  if (title.length > 14) return 43;
  return 58;
};

const OverviewBody: React.FC<{ data: OverviewScene }> = ({ data }) => {
  const active = useFocus(data.durationFrames, data.items.length);
  return <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
    {data.items.map((item, i) => <div key={item.title} style={{ minHeight: 82, border: `1px solid ${item.color}${i === active ? "dd" : "55"}`, borderLeft: `7px solid ${item.color}`, borderRadius: 10, padding: "14px 20px", background: i === active ? `${item.color}22` : "rgba(0,8,7,.42)", filter: `brightness(${i === active ? 1.25 : .72})`, gridColumn: i === data.items.length - 1 ? "1 / -1" : undefined }}><div style={{ fontSize: 25, color: item.color, fontWeight: 900 }}>{item.title}</div><div style={{ fontSize: 16, color: "rgba(255,255,255,.52)", marginTop: 4 }}>{item.note}</div></div>)}
  </div>;
};

const CompareBody: React.FC<{ data: CompareScene }> = ({ data }) => {
  const active = useFocus(data.durationFrames, 3);
  return <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
    {[data.left, data.right].map((side) => <div key={side.title} style={{ border: `1px solid ${side.color}88`, borderRadius: 12, padding: "20px", background: `${side.color}10` }}><div style={{ fontSize: 30, color: side.color, fontWeight: 950, textAlign: "center" }}>{side.title}</div><div style={{ fontSize: 16, color: "rgba(255,255,255,.5)", textAlign: "center", marginTop: 5 }}>{side.subtitle}</div><div style={{ display: "flex", flexDirection: "column", gap: 11, marginTop: 20 }}>{side.points.map((point, i) => <div key={point} style={{ padding: "13px 14px", borderRadius: 8, border: `1px solid ${side.color}${i === active ? "cc" : "44"}`, background: i === active ? `${side.color}20` : "rgba(0,0,0,.25)", fontSize: 21, fontWeight: 800, filter: `brightness(${i === active ? 1.25 : .72})` }}><span style={{ color: side.color, marginRight: 8 }}>{i + 1}</span>{point}</div>)}</div></div>)}
  </div>;
};

const ProcessBody: React.FC<{ data: ProcessScene }> = ({ data }) => {
  const active = useFocus(data.durationFrames, data.steps.length);
  return <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>{data.steps.map((step, i) => <div key={step.title} style={{ minHeight: 78, display: "grid", gridTemplateColumns: "54px 1fr", alignItems: "center", border: `1px solid ${step.color}${i === active ? "dd" : "55"}`, borderLeft: `8px solid ${step.color}`, borderRadius: 10, padding: "11px 20px", background: i === active ? `${step.color}22` : "rgba(0,8,7,.42)", filter: `brightness(${i === active ? 1.25 : .7})`, transform: `translateX(${i === active ? 8 : 0}px)` }}><div style={{ color: step.color, fontFamily: "monospace", fontSize: 18, fontWeight: 900 }}>0{i + 1}</div><div><div style={{ fontSize: 27, fontWeight: 900 }}>{step.title}</div><div style={{ fontSize: 16, color: "rgba(255,255,255,.5)", marginTop: 3 }}>{step.note}</div></div></div>)}</div>;
};

const CaseBody: React.FC<{ data: CaseScene }> = ({ data }) => {
  const active = useFocus(data.durationFrames, data.columns.length);
  return <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 15 }}>{data.columns.map((column, i) => <div key={column.label} style={{ minHeight: 310, border: `1px solid ${column.color}88`, borderTop: `7px solid ${column.color}`, borderRadius: 12, padding: "20px 16px", textAlign: "center", background: i === active ? `${column.color}1f` : "rgba(0,8,7,.42)", filter: `brightness(${i === active ? 1.25 : .7})`, transform: `translateY(${i === active ? -8 : 0}px)` }}><div style={{ color: column.color, fontSize: 17, fontWeight: 900 }}>{column.label}</div><div style={{ fontSize: 29, fontWeight: 950, marginTop: 36 }}>{column.title}</div><div style={{ width: 58, height: 3, background: column.color, margin: "20px auto" }} /><div style={{ fontSize: 18, lineHeight: 1.45, color: "rgba(255,255,255,.64)" }}>{column.note}</div></div>)}</div>;
};

const TriangleBody: React.FC<{ data: TriangleScene }> = ({ data }) => {
  const active = useFocus(data.durationFrames, data.nodes.length);
  const pos = [{ left: 20, top: 20 }, { right: 20, top: 20 }, { left: 280, top: 250 }];
  return <div style={{ position: "relative", height: 450 }}><svg style={{ position: "absolute", inset: 0 }} width="840" height="450"><path d="M150 90 L690 90 L420 350 Z" fill="rgba(35,255,151,.025)" stroke="rgba(255,255,255,.18)" strokeWidth="2" /></svg><div style={{ position: "absolute", left: 335, top: 125, width: 170, height: 170, borderRadius: 999, display: "grid", placeItems: "center", border: "2px solid #E4EF37", background: "rgba(228,239,55,.1)", fontSize: 25, fontWeight: 950 }}>{data.center}</div>{data.nodes.map((node, i) => <div key={node.title} style={{ position: "absolute", width: 280, minHeight: 120, border: `1px solid ${node.color}99`, borderLeft: `7px solid ${node.color}`, borderRadius: 11, padding: "19px", textAlign: "center", background: `${node.color}12`, filter: `brightness(${i === active ? 1.28 : .7})`, transform: `scale(${i === active ? 1.06 : 1})`, ...pos[i] }}><div style={{ fontSize: 28, color: node.color, fontWeight: 950 }}>{node.title}</div><div style={{ fontSize: 17, color: "rgba(255,255,255,.55)", marginTop: 6 }}>{node.note}</div></div>)}</div>;
};

const Body: React.FC<{ data: FramedScene }> = ({ data }) => {
  if (data.type === "overview") return <OverviewBody data={data} />;
  if (data.type === "compare") return <CompareBody data={data} />;
  if (data.type === "process") return <ProcessBody data={data} />;
  if (data.type === "case") return <CaseBody data={data} />;
  return <TriangleBody data={data} />;
};

export const OriginalFrameLayout: React.FC<{ data: FramedScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const meta = getMeta(data);
  const header = useEnter(7);
  const title = useEnter(13);
  const content = useEnter(23);
  const footer = useEnter(38);
  const sweep = interpolate(frame, [0, 36], [-240, 1100], { easing: Easing.inOut(Easing.cubic), extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const footerItems = meta.chips.slice(0, 3);
  return <AbsoluteFill className="cyber-background" style={{ padding: "58px 120px 42px", color: "#fff", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
    <div style={{ textAlign: "center", color: meta.color, fontFamily: "monospace", fontSize: 24, fontWeight: 900, letterSpacing: 5, opacity: header }}>{data.label}</div>
    <div style={{ width: 230, height: 4, margin: "14px auto 18px", background: `linear-gradient(90deg, transparent, ${meta.color}, transparent)` }} />
    <div style={{ width: 520, height: 9, margin: "0 auto 24px", border: `1px solid ${meta.color}88`, borderRadius: 99, padding: 2 }}><div style={{ width: "78%", height: "100%", borderRadius: 99, background: `linear-gradient(90deg, ${meta.color}, #fff8, transparent)`, boxShadow: `0 0 12px ${meta.color}` }} /></div>

    <div style={{ border: `3px solid ${meta.color}`, borderRadius: 20, minHeight: 190, padding: "27px 34px", display: "grid", placeItems: "center", textAlign: "center", boxShadow: `0 0 28px ${meta.color}3d, inset 0 0 24px ${meta.color}0e`, opacity: title, transform: `scale(${.96 + title * .04})` }}><div><div style={{ maxWidth: 790, margin: "0 auto", fontSize: titleSize(data.title), lineHeight: 1.12, fontWeight: 950, color: meta.color, textWrap: "balance" }}>{data.title}</div><div style={{ marginTop: 12, fontSize: 24, fontWeight: 700, color: "rgba(255,255,255,.82)" }}>{meta.subtitle}</div></div></div>

    <div style={{ display: "flex", justifyContent: "center", gap: 15, marginTop: 24, opacity: content }}>{meta.chips.map((chip, i) => <div key={chip} style={{ border: `1px solid ${ACCENTS[i % ACCENTS.length]}`, color: ACCENTS[i % ACCENTS.length], borderRadius: 999, padding: "9px 20px", fontSize: 19, fontWeight: 850 }}>{chip}</div>)}</div>
    <div style={{ marginTop: 28, opacity: content, transform: `translateY(${(1 - content) * 20}px)` }}><Body data={data} /></div>

    <div style={{ position: "absolute", left: 120, right: 120, bottom: 252, opacity: footer }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>{footerItems.map((item, i) => <div key={item} style={{ minHeight: 76, border: `1px solid ${ACCENTS[i]}66`, borderRadius: 8, padding: "13px 15px", background: `${ACCENTS[i]}0e` }}><div style={{ color: ACCENTS[i], fontSize: 14, fontFamily: "monospace", fontWeight: 900 }}>0{i + 1}</div><div style={{ marginTop: 5, fontSize: 20, fontWeight: 800 }}>{item}</div></div>)}</div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 140px 42px", gap: 14, alignItems: "center", marginTop: 18, color: "rgba(255,255,255,.44)", fontSize: 16 }}><div style={{ textAlign: "center" }}>{data.supportText}</div><div style={{ height: 5, borderRadius: 99, background: "rgba(255,255,255,.09)" }}><div style={{ width: "74%", height: "100%", borderRadius: 99, background: meta.color, boxShadow: `0 0 10px ${meta.color}` }} /></div><div style={{ color: meta.color, fontFamily: "monospace" }}>就绪</div></div>
    </div>
    <div style={{ position: "absolute", left: sweep, top: 0, width: 150, height: "100%", transform: "skewX(-12deg)", background: `linear-gradient(90deg, transparent, ${meta.color}18, transparent)`, pointerEvents: "none" }} />
  </AbsoluteFill>;
};
