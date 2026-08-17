import { Audio } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { VideoData, SceneData } from "./types";
import { Intro } from "./scenes/Intro";
import { Hook } from "./scenes/Hook";
import { LockedOutro } from "./scenes/LockedOutro";
import { Captions } from "./Captions";
import { RegisteredBodyScene } from "./layouts/layoutRegistry";

const CyberStage: React.FC = () => {
  const frame = useCurrentFrame();
  const beamX = (frame * 2.2) % 1500 - 300;
  const scanY = (frame * 3.5) % 1500;
  return <AbsoluteFill style={{ overflow: "hidden", background: "#050807" }}>
    <AbsoluteFill style={{ background: "radial-gradient(circle at 22% 12%, rgba(32,235,151,.24), transparent 30%), radial-gradient(circle at 82% 38%, rgba(230,42,139,.18), transparent 31%), radial-gradient(circle at 30% 84%, rgba(239,206,48,.11), transparent 33%)" }} />
    <div style={{ position: "absolute", inset: -100, opacity: .1, backgroundImage: "linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px)", backgroundSize: "56px 56px" }} />
    <div style={{ position: "absolute", left: beamX, top: -100, width: 320, height: 1640, transform: "skewX(-10deg)", filter: "blur(10px)", background: "linear-gradient(90deg, transparent, rgba(35,255,151,.14), transparent)" }} />
    <div style={{ position: "absolute", left: 0, right: 0, top: scanY, height: 2, opacity: .22, background: "linear-gradient(90deg, transparent, #20eb97, transparent)", boxShadow: "0 0 18px #20eb97" }} />
  </AbsoluteFill>;
};

const SceneShell: React.FC<{ durationInFrames: number; children: React.ReactNode }> = ({ durationInFrames, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const edge = Math.round(0.3 * fps);
  const enter = interpolate(frame, [0, edge], [0, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exit = interpolate(frame, [durationInFrames - edge, durationInFrames], [1, 0], {
    easing: Easing.in(Easing.cubic),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const visibility = Math.min(enter, exit);

  return (
    <AbsoluteFill style={{ opacity: visibility, transform: `scale(${1.025 - visibility * 0.025})` }}>
      {children}
    </AbsoluteFill>
  );
};

const Scene: React.FC<{ scene: SceneData }> = ({ scene }) => {
  switch (scene.type) {
    case "intro":
      return <Intro data={scene} frameOffset={0} />;
    case "hook":
      return <Hook data={scene} />;
    case "skill_detail":
    case "comment_cta":
    case "workflow":
    case "overview":
    case "compare":
    case "process":
    case "case":
    case "triangle":
      return <RegisteredBodyScene scene={scene} />;
    case "outro":
      return <LockedOutro />;
  }
};

const Track: React.FC<{ track: NonNullable<VideoData["audio"]>["master"] }> = ({ track }) => {
  if (!track) return null;
  const startFrame = track.startFrame ?? 0;
  return (
    <Sequence from={startFrame} premountFor={30}>
      <Audio src={staticFile(track.src)} volume={() => track.volume ?? 1} />
    </Sequence>
  );
};

export const VideoTemplate: React.FC<VideoData> = ({ scenes, audio, captions = [] }) => {
  let accumulated = 0;
  const coverDuration = scenes[0]?.type === "intro" ? scenes[0].durationFrames : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#030806" }}>
      <CyberStage />
      {scenes.map((scene, index) => {
        const from = accumulated;
        accumulated += scene.durationFrames;
        return (
          <Sequence key={`${scene.type}-${index}`} from={from} durationInFrames={scene.durationFrames} premountFor={30}>
            {scene.type === "intro" ? <Scene scene={scene} /> : <SceneShell durationInFrames={scene.durationFrames}><Scene scene={scene} /></SceneShell>}
          </Sequence>
        );
      })}
      <Track track={audio?.master} />
      <Track track={audio?.voiceover} />
      <Track track={audio?.bgm} />
      <Track track={audio?.outro} />
      <Captions captions={captions} hideBeforeFrame={coverDuration} narrationStartFrame={audio?.voiceover?.startFrame ?? 0} />
    </AbsoluteFill>
  );
};
