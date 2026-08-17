import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { AmbientMotion } from "../cinematic/AmbientMotion";
import { CinematicBackground } from "../cinematic/CinematicBackground";
import { DepthScene } from "../cinematic/DepthScene";
import { FloatingScreenshot } from "../cinematic/FloatingScreenshot";
import { FlowConnector } from "../cinematic/FlowConnector";
import { FlowNode } from "../cinematic/FlowNode";
import { GlassPanel } from "../cinematic/GlassPanel";
import { useFocusAmount } from "../cinematic/FocusSystem";

const titleStyle = {
  fontFamily: "PingFang SC, Arial, sans-serif",
  letterSpacing: 0,
} as const;

const EnvironmentLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const glow = 0.52 + Math.sin(frame / 46) * 0.12;

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 160,
          top: 160,
          width: 760,
          height: 310,
          borderRadius: 30,
          background: "linear-gradient(160deg, rgba(10,28,27,.72), rgba(2,5,5,.82))",
          border: "1px solid rgba(125,255,228,.10)",
          boxShadow: `0 0 ${60 * glow}px rgba(82,255,220,.11), inset 0 0 60px rgba(0,0,0,.32)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 260,
          top: 542,
          width: 580,
          height: 70,
          borderRadius: 18,
          background: "linear-gradient(180deg, rgba(255,187,91,.28), rgba(15,18,14,.78))",
          filter: "blur(.2px)",
          boxShadow: "0 32px 90px rgba(0,0,0,.42)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 196,
          top: 116,
          width: 78,
          height: 300,
          borderRadius: 999,
          background: "linear-gradient(180deg, rgba(255,214,133,.22), rgba(255,214,133,0))",
          filter: "blur(12px)",
        }}
      />
    </AbsoluteFill>
  );
};

const SubjectLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const breathe = 1 + Math.sin(frame / 54) * 0.012;

  return (
    <AbsoluteFill>
      <AmbientMotion amount={3} rotate={0.16} speed={80} style={{ position: "absolute", left: 405, top: 615 }}>
        <div style={{ transform: `scale(${breathe})`, transformOrigin: "50% 100%" }}>
          <div
            style={{
              width: 206,
              height: 238,
              borderRadius: "72px 72px 54px 54px",
              background: "linear-gradient(155deg, rgba(230,255,250,.92), rgba(124,168,160,.86))",
              boxShadow: "0 34px 80px rgba(0,0,0,.42), inset 0 1px 0 rgba(255,255,255,.65)",
            }}
          >
            <div style={{ position: "absolute", left: 46, top: 62, display: "flex", gap: 44 }}>
              <div style={{ width: 22, height: 22, borderRadius: 999, background: "#10211f", boxShadow: "0 0 18px rgba(98,255,228,.75)" }} />
              <div style={{ width: 22, height: 22, borderRadius: 999, background: "#10211f", boxShadow: "0 0 18px rgba(98,255,228,.75)" }} />
            </div>
            <div
              style={{
                position: "absolute",
                left: 58,
                top: 124,
                width: 90,
                height: 12,
                borderRadius: 999,
                background: "rgba(16,33,31,.55)",
              }}
            />
            <div
              style={{
                position: "absolute",
                left: 72,
                top: 174,
                width: 62,
                height: 34,
                borderRadius: 12,
                display: "grid",
                placeItems: "center",
                fontSize: 16,
                fontWeight: 900,
                color: "#10211f",
                background: "rgba(98,255,228,.42)",
              }}
            >
              AI
            </div>
          </div>
        </div>
      </AmbientMotion>
    </AbsoluteFill>
  );
};

const ContentLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const whisperFocus = useFocusAmount(300, 420);
  const resultFocus = useFocusAmount(420, durationInFrames);
  const dimEarly = frame > 300 ? 1 : 0;
  const stageText =
    frame < 90 ? "输入一个视频链接" : frame < 180 ? "下载后拆成音频和画面" : frame < 300 ? "分别交给 Whisper 和 Vision" : frame < 420 ? "讲到哪里，焦点就推到哪里" : "最后生成知识库笔记";
  const headlineOpacity = interpolate(frame, [0, 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ ...titleStyle, color: "white" }}>
      <div
        style={{
          position: "absolute",
          left: 120,
          top: 142,
          width: 650,
          opacity: headlineOpacity,
          transform: "translateZ(80px)",
        }}
      >
        <div style={{ fontSize: 22, color: "#62ffe4", fontWeight: 800 }}>2.5D DEMO</div>
        <div style={{ marginTop: 12, fontSize: 48, lineHeight: 1.08, fontWeight: 950 }}>
          <div>AI 工作室里的</div>
          <div>视频解析流程</div>
        </div>
        <div style={{ marginTop: 18, fontSize: 24, lineHeight: 1.32, color: "rgba(230,255,250,.72)" }}>{stageText}</div>
      </div>

      <FlowConnector path="M 246 426 C 284 472, 322 510, 374 548" startFrame={84} length={280} />
      <FlowConnector path="M 438 608 C 368 668, 306 718, 272 792" startFrame={180} length={310} />
      <FlowConnector path="M 518 610 C 612 666, 674 720, 716 792" startFrame={180} length={340} accent="#ffc86b" />
      <FlowConnector path="M 315 855 C 420 928, 540 928, 675 874" startFrame={408} length={430} accent="#7dffb7" />

      <FlowNode
        icon="URL"
        title="视频链接"
        description="所有内容从一个链接开始"
        status="0-3s"
        startFrame={12}
        focused={frame < 92 ? 0.9 : 0.15}
        dimmed={Boolean(dimEarly)}
        style={{ left: 128, top: 336 }}
      />
      <FlowNode
        icon="DL"
        title="下载视频"
        description="先拿到原始素材"
        status="3-6s"
        startFrame={92}
        focused={frame >= 90 && frame < 180 ? 0.92 : 0.18}
        dimmed={frame > 300}
        style={{ left: 352, top: 516 }}
      />
      <FlowNode
        icon="AU"
        title="音频"
        description="进入 Whisper 转写"
        startFrame={184}
        focused={whisperFocus}
        dimmed={frame > 420}
        style={{ left: 118, top: 782 }}
      />
      <FlowNode
        icon="VI"
        title="画面"
        description="进入视觉模型理解"
        accent="#ffc86b"
        startFrame={202}
        focused={whisperFocus * 0.8}
        dimmed={frame > 420}
        style={{ left: 640, top: 786 }}
      />
      <FlowNode
        icon="KB"
        title="知识库笔记"
        description="声音和画面汇聚成结构化结果"
        accent="#7dffb7"
        startFrame={420}
        focused={resultFocus}
        style={{ left: 380, top: 1024 }}
      />

      <FloatingScreenshot startFrame={430} focused={resultFocus} width={330} style={{ right: 180, top: 286 }} />

      {frame < 430 ? (
        <GlassPanel
          startFrame={260}
          focused={whisperFocus}
          width={344}
          style={{
            position: "absolute",
            left: 138,
            top: 1082,
            minHeight: 0,
            transform: `perspective(900px) rotateX(7deg) rotateY(-8deg) translateZ(${80 + whisperFocus * 30}px)`,
          }}
        >
          <div style={{ fontSize: 18, color: "rgba(230,255,250,.68)", lineHeight: 1.35 }}>不是切页面，而是在同一个镜头里把重点推到前景。</div>
        </GlassPanel>
      ) : null}
    </AbsoluteFill>
  );
};

const ForegroundLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const scan = (frame * 2.1) % 1220;

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: -80,
          top: scan,
          width: 1240,
          height: 2,
          background: "linear-gradient(90deg, transparent, rgba(98,255,228,.32), transparent)",
          boxShadow: "0 0 22px rgba(98,255,228,.28)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: -90,
          bottom: 96,
          width: 1220,
          height: 210,
          background: "linear-gradient(0deg, rgba(0,0,0,.58), transparent)",
          filter: "blur(2px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          right: 44,
          top: 186,
          width: 3,
          height: 940,
          background: "linear-gradient(180deg, transparent, rgba(255,200,107,.25), transparent)",
          filter: "blur(1px)",
        }}
      />
    </AbsoluteFill>
  );
};

export const CinematicDemoScene: React.FC = () => (
  <DepthScene
    movement="pushIn"
    intensity={0.54}
    background={<CinematicBackground />}
    environment={<EnvironmentLayer />}
    subject={<SubjectLayer />}
    content={<ContentLayer />}
    foreground={<ForegroundLayer />}
  />
);
