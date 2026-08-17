import type { ComponentType } from "react";
import type { SceneData } from "../types";
import { CaseLayout, CompareLayout, OverviewLayout, ProcessLayout, TriangleLayout } from "./AdaptiveLayouts";
import { SkillDetail } from "../scenes/SkillDetail";
import { Workflow } from "../scenes/Workflow";
import { CommentCTA } from "../scenes/CommentCTA";

export type BodyScene = Exclude<SceneData, { type: "intro" | "hook" | "outro" }>;
export type BodyLayoutType = BodyScene["type"];

export const LAYOUT_CATALOG: Record<BodyLayoutType, {
  name: string;
  useWhen: string;
  maxItems: number;
}> = {
  skill_detail: { name: "单主题清单", useWhen: "一个工具、概念或方法包含 2—4 个能力点", maxItems: 4 },
  comment_cta: { name: "评论行动页", useWhen: "片尾前引导评论区领取资料或工具包", maxItems: 3 },
  workflow: { name: "纵向流程", useWhen: "步骤、阶段、操作顺序或工作流", maxItems: 6 },
  overview: { name: "概览网格", useWhen: "并列观点、功能总览或分类清单", maxItems: 5 },
  compare: { name: "左右对比", useWhen: "前后、传统与新方法、A/B 方案对照", maxItems: 6 },
  process: { name: "重点步骤", useWhen: "3—6 个需要解释的连续动作", maxItems: 6 },
  case: { name: "案例拆解", useWhen: "问题—做法—结果，或三个阶段的案例", maxItems: 3 },
  triangle: { name: "关系结构", useWhen: "三个因素共同作用、支撑或形成闭环", maxItems: 3 },
};

type BodyRenderer = ComponentType<{ scene: BodyScene }>;

const OverviewRenderer: BodyRenderer = ({ scene }) => scene.type === "overview" ? <OverviewLayout data={scene} /> : null;
const CompareRenderer: BodyRenderer = ({ scene }) => scene.type === "compare" ? <CompareLayout data={scene} /> : null;
const ProcessRenderer: BodyRenderer = ({ scene }) => scene.type === "process" ? <ProcessLayout data={scene} /> : null;
const CaseRenderer: BodyRenderer = ({ scene }) => scene.type === "case" ? <CaseLayout data={scene} /> : null;
const TriangleRenderer: BodyRenderer = ({ scene }) => scene.type === "triangle" ? <TriangleLayout data={scene} /> : null;

const SkillRenderer: BodyRenderer = ({ scene }) => scene.type === "skill_detail"
  ? <SkillDetail data={scene} frameOffset={0} />
  : null;

const WorkflowRenderer: BodyRenderer = ({ scene }) => scene.type === "workflow"
  ? <Workflow data={scene} />
  : null;

const CommentRenderer: BodyRenderer = ({ scene }) => scene.type === "comment_cta"
  ? <CommentCTA data={scene} />
  : null;

export const BODY_LAYOUTS: Record<BodyLayoutType, BodyRenderer> = {
  skill_detail: SkillRenderer,
  comment_cta: CommentRenderer,
  workflow: WorkflowRenderer,
  overview: OverviewRenderer,
  compare: CompareRenderer,
  process: ProcessRenderer,
  case: CaseRenderer,
  triangle: TriangleRenderer,
};

export const RegisteredBodyScene: React.FC<{ scene: BodyScene }> = ({ scene }) => {
  const Layout = BODY_LAYOUTS[scene.type];
  return <Layout scene={scene} />;
};
