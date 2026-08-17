import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { AmbientMotion } from "../../cinematic/AmbientMotion";
import { CameraRig } from "../../cinematic/CameraRig";
import { CinematicBackground } from "../../cinematic/CinematicBackground";
import { GlassPanel } from "../../cinematic/GlassPanel";
import type { CommentCtaScene } from "../types";

const TEAL = "#39FF14";
const CYAN = "#00FFFF";
const PINK = "#FF1493";

export const CommentCTA: React.FC<{ data: CommentCtaScene }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pulse = interpolate(frame % 54, [0, 27, 54], [0.92, 1.04, 0.92], {
    easing: Easing.inOut(Easing.cubic),
  });
  const enter = (delay: number) => spring({
    frame: frame - delay,
    fps,
    config: { damping: 16, stiffness: 130, mass: 0.55 },
  });

  return (
    <AbsoluteFill style={{ color: "#fff", fontFamily: "'PingFang SC', sans-serif", overflow: "hidden" }}>
      <CameraRig movement="focus" intensity={0.26}>
        <AbsoluteFill style={{ transformStyle: "preserve-3d" }}>
          <AbsoluteFill style={{ transform: "translateZ(-320px) scale(1.08)" }}><CinematicBackground variant="monitor" /></AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(-110px)" }}>
            <div style={{ position: "absolute", inset: 58, border: `1px solid ${PINK}55`, borderRadius: 34, background: "radial-gradient(circle at 50% 38%, rgba(255,20,147,.12), transparent 38%), linear-gradient(180deg, rgba(5,7,9,.18), rgba(0,0,0,.04))", boxShadow: `0 0 42px ${PINK}20, inset 0 0 70px rgba(0,255,255,.03)` }} />
          </AbsoluteFill>
          <AbsoluteFill style={{ transform: "translateZ(120px)" }}>
            <div style={{ position: "absolute", left: 112, top: 112, color: PINK, fontFamily: "monospace", fontSize: 20, fontWeight: 950, letterSpacing: 4, opacity: enter(4) }}>COMMENT / ACTION</div>
            <div style={{ position: "absolute", right: 116, top: 116, color: "rgba(255,255,255,.34)", fontFamily: "monospace", fontSize: 14, letterSpacing: 3 }}>BEFORE OUTRO</div>

            <div style={{ position: "absolute", left: 94, right: 94, top: 205, textAlign: "center", transform: "translateZ(70px)" }}>
              <div style={{ fontSize: data.title.length > 13 ? 52 : 64, lineHeight: 1.08, fontWeight: 950, opacity: enter(8), textShadow: "0 12px 32px rgba(0,0,0,.35)" }}>{data.title}</div>
            </div>

            <AmbientMotion amount={4} rotate={0.22} speed={78} style={{ position: "absolute", left: 195, top: 370 }}>
              <GlassPanel startFrame={14} accent={TEAL} focused={0.9} width={690} style={{ minHeight: 250, display: "grid", placeItems: "center", textAlign: "center", transform: `perspective(1000px) translateZ(95px) rotateX(4deg) rotateY(-5deg) scale(${pulse})` }}>
                <div>
                  <div style={{ color: "rgba(255,255,255,.56)", fontSize: 24, fontWeight: 850, marginBottom: 14 }}>评论区打</div>
                  <div style={{ color: TEAL, fontSize: data.keyword.length > 4 ? 82 : 106, lineHeight: 1, fontWeight: 950, textShadow: `0 0 36px ${TEAL}88` }}>“{data.keyword}”</div>
                </div>
              </GlassPanel>
            </AmbientMotion>

            <div style={{ position: "absolute", left: 160, right: 160, top: 680, color: "rgba(255,255,255,.72)", fontSize: 27, lineHeight: 1.35, fontWeight: 850, textAlign: "center", opacity: enter(22), transform: "translateZ(60px)" }}>{data.offer}</div>

            <div style={{ position: "absolute", left: 116, right: 116, top: 805, height: 190 }}>
              {data.items.slice(0, 3).map((item, index) => {
                const progress = enter(28 + index * 6);
                return (
                  <AmbientMotion key={`${item.title}-${index}`} amount={2.2 + index * 0.2} rotate={0.14} speed={76 + index * 8} style={{ position: "absolute", left: index * 286, top: index % 2 === 0 ? 0 : 32 }}>
                    <div style={{ opacity: progress, transform: `translateY(${(1 - progress) * 28}px) translateZ(${index * 22}px) rotateY(${index === 1 ? 0 : index === 0 ? -6 : 6}deg)` }}>
                      <GlassPanel startFrame={28 + index * 6} accent={item.color} focused={index === 1 ? 0.3 : 0.12} width={262} style={{ minHeight: 132, padding: "18px 18px" }}>
                        <div style={{ color: item.color, fontFamily: "monospace", fontSize: 14, fontWeight: 950, marginBottom: 10 }}>0{index + 1}</div>
                        <div style={{ fontSize: 22, lineHeight: 1.22, fontWeight: 950 }}>{item.title}</div>
                        {item.note ? <div style={{ marginTop: 8, color: "rgba(255,255,255,.58)", fontSize: 17, lineHeight: 1.35 }}>{item.note}</div> : null}
                      </GlassPanel>
                    </div>
                  </AmbientMotion>
                );
              })}
            </div>

            {data.supportText ? <div style={{ position: "absolute", left: 160, right: 160, bottom: 255, color: CYAN, fontSize: 21, textAlign: "center", fontWeight: 850, opacity: enter(40), transform: "translateZ(80px)" }}>{data.supportText}</div> : null}
          </AbsoluteFill>
        </AbsoluteFill>
      </CameraRig>
    </AbsoluteFill>
  );
};
