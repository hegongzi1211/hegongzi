import "./index.css";
import { Composition } from "remotion";
import { VideoTemplate } from "./template/VideoTemplate";
import { CinematicDemoScene } from "./scenes/CinematicDemoScene";
import videoData from "../video-data.json";
import layoutScenes from "../layout-scenes.json";
import generatedCaptions from "../generated/captions.json";
import type { VideoData } from "./template/types";
import { LockedOutro } from "./template/scenes/LockedOutro";

const data = { ...videoData, scenes: layoutScenes } as VideoData;
const totalFrames = data.scenes.reduce((sum, scene) => sum + scene.durationFrames, 0);

const normalizeContractText = (text: string) =>
  text.replace(/[\s，。！？、；：,.!?;:“”‘’"'（）()\-—→+]/g, "").toLowerCase();

const assertRuntimeDataContract = () => {
  const captions = data.captions ?? [];
  if (JSON.stringify(captions) !== JSON.stringify(generatedCaptions)) {
    throw new Error("SYNC FAIL: video-data.json captions are not generated/captions.json. Run scripts/build_video.py before rendering.");
  }

  const sceneBody = data.scenes
    .filter((scene) => scene.type !== "intro" && scene.type !== "outro")
    .map((scene) => scene.narration ?? "")
    .join("");
  const captionBody = captions.map((caption) => caption.text).join("");
  if (normalizeContractText(sceneBody) !== normalizeContractText(captionBody)) {
    throw new Error("SYNC FAIL: captions text does not match scene narration. Refusing to render mismatched audio/subtitles/visuals.");
  }

  const declaredFrames = data.metadata?.durationInFrames;
  if (typeof declaredFrames === "number" && declaredFrames !== totalFrames) {
    throw new Error(`SYNC FAIL: metadata duration ${declaredFrames} does not match scene total ${totalFrames}.`);
  }
};

assertRuntimeDataContract();

const libraryTypes = ["skill_detail", "comment_cta", "overview", "compare", "process", "case", "triangle", "workflow"];
const libraryScenes = libraryTypes
  .map((type) => data.scenes.find((scene) => scene.type === type))
  .filter((scene): scene is NonNullable<typeof scene> => Boolean(scene))
  .map((scene) => ({ ...scene, durationFrames: 90 }));
const libraryData = { title: "终稿版式组件库", scenes: libraryScenes, captions: [] } as VideoData;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VideoTemplate"
        component={VideoTemplate as unknown as React.FC<Record<string, unknown>>}
        durationInFrames={totalFrames}
        fps={30}
        width={1080}
        height={1440}
        defaultProps={data}
      />
      <Composition
        id="LayoutLibraryPreview"
        component={VideoTemplate as unknown as React.FC<Record<string, unknown>>}
        durationInFrames={libraryScenes.length * 90}
        fps={30}
        width={1080}
        height={1440}
        defaultProps={libraryData}
      />
      <Composition
        id="CinematicDemoScene"
        component={CinematicDemoScene}
        durationInFrames={540}
        fps={30}
        width={1080}
        height={1440}
      />
      <Composition
        id="OutroPreview"
        component={LockedOutro}
        durationInFrames={105}
        fps={30}
        width={1080}
        height={1440}
      />
    </>
  );
};
