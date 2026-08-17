import { AbsoluteFill } from "remotion";
import { CinematicBackground } from "../../cinematic/CinematicBackground";
import type { IntroScene } from "../types";

const TEAL = "#20eb97";
const PINK = "#ff2b91";
const isLatin = (s: string) => Boolean(s) && [...s].every((char) => char.charCodeAt(0) <= 127);

export const Intro: React.FC<{ data: IntroScene; frameOffset: number }> = ({ data }) => {
  const titleChars = `${data.title1}${data.title2}${data.title3}`.replace(/\s/g, "").length;
  const compactBadge = titleChars > 18 || isLatin(data.title1);
  const graphItems = [...data.centerGraph.nodes.slice(0, 4), {
    title: data.centerGraph.centerText1,
    desc: data.centerGraph.centerText2,
    color: TEAL,
  }];

  return (
    <AbsoluteFill style={{ color: "#fff", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CinematicBackground variant="wide" />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(2,8,9,.86) 0%, rgba(2,8,9,.56) 58%, rgba(2,8,9,.18) 100%)" }} />
      <div data-design="cover-stage-frame" style={{ position: "absolute", inset: 34, border: "1px solid rgba(32,235,151,.16)", borderRadius: 30, boxShadow: "inset 0 0 60px rgba(32,235,151,.025), 0 0 42px rgba(0,0,0,.32)" }} />
      {data.rightBadge && (
        <div data-design="intro-floating-badge" style={{ position: "absolute", right: compactBadge ? 74 : 86, top: compactBadge ? 126 : 148, width: compactBadge ? 138 : 158, padding: compactBadge ? "13px 10px" : "16px 12px", border: `1.5px solid ${PINK}`, borderRadius: 16, textAlign: "center", background: "rgba(25,4,18,.62)", boxShadow: `0 0 20px ${PINK}26`, opacity: compactBadge ? .72 : .9 }}>
          <div style={{ fontSize: compactBadge ? 20 : 23, fontWeight: 900, color: "#fff" }}>{data.rightBadge.top}</div>
          <div style={{ marginTop: 5, color: PINK, fontSize: compactBadge ? 12 : 14, fontWeight: 800 }}>{data.rightBadge.bottom}</div>
        </div>
      )}
      <div style={{ position: "absolute", left: 52, right: 52, top: 50, height: 1, background: "linear-gradient(90deg, transparent, rgba(32,235,151,.45), transparent)" }} />
      <div style={{ position: "absolute", right: 48, top: 86, color: "rgba(255,255,255,.22)", fontFamily: "monospace", fontSize: 11, letterSpacing: 4, writingMode: "vertical-rl" }}>HGZ / CONTENT SYSTEM</div>
      <div style={{ position: "absolute", left: 70, right: 70, top: 66, bottom: 58, display: "flex", flexDirection: "column" }}>
        {/* Top badge */}
        <div style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 10, border: `1px solid ${TEAL}aa`, borderRadius: 999, padding: "9px 22px", color: TEAL, fontSize: 17, fontWeight: 900, letterSpacing: 2, background: "linear-gradient(90deg, rgba(0,27,19,.92), rgba(0,18,13,.56))", boxShadow: `0 0 22px ${TEAL}16` }}>
          <span style={{ width: 7, height: 7, borderRadius: 99, background: TEAL, boxShadow: `0 0 12px ${TEAL}` }} />{data.badge}
        </div>

        {/* Title block */}
        <div style={{ marginTop: 30 }}>
          <div style={{ fontSize: 92, lineHeight: 1.01, fontWeight: 950, letterSpacing: -3, textShadow: "0 8px 34px rgba(0,0,0,.35)" }}>
            <div style={{ color: "#fff", fontSize: isLatin(data.title1) ? 132 : undefined, lineHeight: isLatin(data.title1) ? 1.04 : undefined }}>{data.title1}</div>
            <div style={{ color: "#fff", opacity: .96 }}>{data.title2}</div>
            <div style={{ color: TEAL, textShadow: `0 0 28px ${TEAL}66` }}>{data.title3}</div>
          </div>
        </div>

        {/* Subtitle */}
        <div style={{ marginTop: 20, fontSize: 27, lineHeight: 1.4, fontWeight: 800, color: "rgba(255,255,255,.74)", letterSpacing: .2 }}>
          {data.subtitle}
        </div>

        {/* Skill name chips — 开场即列出全部 Skill 名字 */}
        {data.skillChips && data.skillChips.length > 0 && (
          <div style={{ marginTop: 26 }}>
            <div style={{ color: "#25d8ff", fontSize: 17, fontWeight: 900, marginBottom: 12, letterSpacing: 1 }}>本期 10 大核心 Skill</div>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              {data.skillChips.map((name, i) => (
                <div key={name} style={{ padding: "9px 16px", borderRadius: 999, border: `1px solid ${TEAL}77`, color: "#fff", fontSize: 17, fontWeight: 800, background: `${TEAL}0d`, display: "flex", alignItems: "center" }}>
                  <span style={{ color: TEAL, fontFamily: "monospace", fontWeight: 900, marginRight: 7 }}>{String(i + 1).padStart(2, "0")}</span>{name}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pills — 三大板块，作为目录补充 */}
        <div style={{ display: "flex", gap: 12, marginTop: 22, paddingBottom: 22 }}>
          {data.flowItems.map((item, index) => (
            <div key={item.text} style={{ padding: "10px 20px", borderRadius: 999, border: `1px solid ${item.color}88`, color: "#fff", fontSize: 19, fontWeight: 800, background: `linear-gradient(90deg, ${item.color}16, rgba(0,0,0,.15))`, boxShadow: `0 0 16px ${item.color}12` }}>
              <span style={{ color: item.color, fontFamily: "monospace", fontSize: 13, marginRight: 8 }}>0{index + 1}</span>{item.text}
            </div>
          ))}
        </div>

        {/* Middle-stage graph */}
        <div data-design="cover-graph" style={{ position: "relative", border: `1px solid ${TEAL}72`, borderRadius: 22, padding: "22px 22px 24px", background: "linear-gradient(135deg, rgba(32,235,151,.12), rgba(2,10,9,.56) 46%, rgba(255,43,145,.06))", backdropFilter: "blur(13px)", boxShadow: `0 18px 50px rgba(0,0,0,.28), 0 0 32px ${TEAL}18, inset 0 1px 0 rgba(255,255,255,.06)` }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ color: TEAL, fontSize: 17, fontWeight: 900, letterSpacing: 2 }}>{data.centerGraph.label}</div>
            <div style={{ display: "flex", gap: 6 }}>{[TEAL, "#25d8ff", PINK].map((color) => <span key={color} style={{ width: 7, height: 7, borderRadius: 99, background: color, boxShadow: `0 0 9px ${color}` }} />)}</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12, marginTop: 16 }}>
            {graphItems.map((node, i) => (
              <div key={`${node.title}-${i}`} style={{ gridColumn: i < 3 ? "span 2" : "span 3", minHeight: 86, border: `1px solid ${node.color}5c`, borderRadius: 13, padding: "14px 16px", textAlign: "left", background: `linear-gradient(135deg, ${node.color}16, rgba(0,0,0,.18))`, boxShadow: `0 0 16px ${node.color}12, inset 3px 0 0 ${node.color}` }}>
                <div style={{ display: "flex", alignItems: "center", gap: 9 }}><span style={{ color: node.color, fontFamily: "monospace", fontSize: 12 }}>0{i + 1}</span><span style={{ color: node.color, fontSize: 20, fontWeight: 900 }}>{node.title}</span></div>
                <div style={{ marginTop: 6, marginLeft: 31, color: "rgba(255,255,255,.64)", fontSize: 14, lineHeight: 1.3, fontWeight: 650 }}>{node.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom quote */}
        {data.bottomTitle && (
          <div style={{ marginTop: "auto" }}>
            <div style={{ borderLeft: "6px solid #ffd83d", padding: "17px 24px", color: "#ffd83d", fontSize: 27, fontWeight: 900, background: "linear-gradient(90deg, rgba(255,216,61,.13), rgba(255,216,61,.025))", boxShadow: "inset 0 1px 0 rgba(255,255,255,.04)" }}>
              {data.bottomTitle}
            </div>
            <div style={{ display: "flex", gap: 14, marginTop: 18 }}>
              {data.bottomCabins.map((cabin) => (
                <div key={cabin.label} style={{ flex: 1, minHeight: 75, border: `1px solid ${cabin.color}66`, borderRadius: 14, padding: "15px 17px", background: `linear-gradient(135deg, ${cabin.color}12, rgba(0,0,0,.12))`, boxShadow: `inset 3px 0 0 ${cabin.color}` }}>
                  <div style={{ color: cabin.color, fontSize: 14, fontWeight: 900 }}>{cabin.label}</div>
                  <div style={{ marginTop: 5, fontSize: 16, fontWeight: 750, color: "rgba(255,255,255,.90)" }}>{cabin.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
