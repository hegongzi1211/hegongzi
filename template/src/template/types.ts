export interface GraphNode {
  title: string;
  desc: string;
  color: string;
  left: string;
  top: string;
}

export interface Cabin {
  label: string;
  value: string;
  color: string;
}

export interface FlowItem {
  text: string;
  color: string;
}

export interface RightBadge {
  top: string;
  bottom: string;
}

export interface CenterGraph {
  label?: string;
  centerText1: string;
  centerText2: string;
  nodes: GraphNode[];
}

export interface DetailItem {
  text: string;
  color: string;
  label: string;
  value: string;
}

export interface IntroScene {
  type: "intro";
  durationFrames: number;
  showSubtitle: boolean;
  badge: string;
  title1: string;
  title2: string;
  title3: string;
  subtitle?: string;
  rightBadge?: RightBadge;
  flowItems: FlowItem[];
  centerGraph: CenterGraph;
  bottomTitle: string;
  bottomCabins: Cabin[];
  skillChips?: string[];
  narration?: string;
}

export interface SkillDetailScene {
  type: "skill_detail";
  durationFrames: number;
  showSubtitle: boolean;
  subtitleText?: string;
  skillNum: string;
  skillName: string;
  desc: string;
  mainColor: string;
  details: DetailItem[];
  footerItems?: Cabin[];
  supportText?: string;
  narration?: string;
}

export interface HookScene {
  type: "hook";
  durationFrames: number;
  showSubtitle: boolean;
  eyebrow: string;
  title: string;
  subtitle: string;
  tags: FlowItem[];
  narration?: string;
}

export interface WorkflowScene {
  type: "workflow";
  durationFrames: number;
  showSubtitle: boolean;
  title: string;
  subtitleText?: string;
  steps: Array<{ number: string; title: string; subtitle: string; color: string }>;
  narration?: string;
}

export interface OverviewScene {
  type: "overview";
  layoutVariant?: "bento" | "index" | "spotlight";
  durationFrames: number;
  showSubtitle: boolean;
  label: string;
  title: string;
  subtitle: string;
  items: Array<{ title: string; note: string; color: string }>;
  itemStartFrames?: number[];
  supportText?: string;
  narration?: string;
}

export interface CompareScene {
  type: "compare";
  durationFrames: number;
  showSubtitle: boolean;
  label: string;
  title: string;
  left: { title: string; subtitle: string; color: string; points: string[] };
  right: { title: string; subtitle: string; color: string; points: string[] };
  supportText?: string;
  narration?: string;
}

export interface ProcessScene {
  type: "process";
  durationFrames: number;
  showSubtitle: boolean;
  label: string;
  title: string;
  subtitle: string;
  steps: Array<{ title: string; note: string; color: string }>;
  supportText?: string;
  narration?: string;
}

export interface CaseScene {
  type: "case";
  durationFrames: number;
  showSubtitle: boolean;
  label: string;
  title: string;
  columns: Array<{ label: string; title: string; note: string; color: string }>;
  supportText?: string;
  narration?: string;
}

export interface TriangleScene {
  type: "triangle";
  durationFrames: number;
  showSubtitle: boolean;
  label: string;
  title: string;
  center: string;
  nodes: Array<{ title: string; note: string; color: string }>;
  supportText?: string;
  narration?: string;
}

export interface CommentCtaScene {
  type: "comment_cta";
  durationFrames: number;
  showSubtitle: boolean;
  label: string;
  title: string;
  subtitle?: string;
  keyword: string;
  offer: string;
  items: Array<{ title: string; note: string; color: string }>;
  supportText?: string;
  narration?: string;
}

export interface OutroScene {
  type: "outro";
  durationFrames: number;
  showSubtitle: boolean;
  userName: string;
  ctaText: string;
  mainColor: string;
}

export type SceneData = IntroScene | HookScene | SkillDetailScene | WorkflowScene | OverviewScene | CompareScene | ProcessScene | CaseScene | TriangleScene | CommentCtaScene | OutroScene;

export interface AudioTrack {
  src: string;
  volume?: number;
  startFrame?: number;
}

export interface CaptionData {
  text: string;
  startMs: number;
  endMs: number;
}

export interface VideoData {
  title: string;
  scenes: SceneData[];
  metadata?: {
    durationInFrames?: number;
  };
  audio?: {
    master?: AudioTrack;
    voiceover?: AudioTrack;
    bgm?: AudioTrack;
    outro?: AudioTrack;
  };
  captions?: CaptionData[];
}
