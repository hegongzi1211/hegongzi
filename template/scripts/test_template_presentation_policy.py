#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
video = (ROOT / "src/template/VideoTemplate.tsx").read_text(encoding="utf-8")
frame = (ROOT / "src/template/layouts/LayoutFrame.tsx").read_text(encoding="utf-8")
hook = (ROOT / "src/template/scenes/Hook.tsx").read_text(encoding="utf-8")
intro = (ROOT / "src/template/scenes/Intro.tsx").read_text(encoding="utf-8")
skill = (ROOT / "src/template/scenes/SkillDetail.tsx").read_text(encoding="utf-8")
workflow = (ROOT / "src/template/scenes/Workflow.tsx").read_text(encoding="utf-8")
captions = (ROOT / "src/template/Captions.tsx").read_text(encoding="utf-8")
types_source = (ROOT / "src/template/types.ts").read_text(encoding="utf-8")
overview_source = (ROOT / "src/template/layouts/AdaptiveLayouts.tsx").read_text(encoding="utf-8")

assert "SoundDesign" not in video, "Transition sound effects must stay disabled"
assert "duckVolume" not in video, "Narration must not be ducked for removed sound effects"
assert 'minHeight: 720' in frame, "Body layouts need a full middle-stage slot"
assert 'justifyContent: "center"' in frame and '"flex-end"' not in frame, "Every body layout should stay in the visual middle instead of dropping to the bottom"
assert 'bottom: 286' in frame and 'minHeight: 72' in frame, "Supporting information needs a visible pre-caption rail"
assert 'gridTemplateColumns: "repeat(2, 1fr)"' in hook, "Hook tags need a substantial middle-stage grid"
assert 'bottom: 286' in hook, "Hook support copy needs the same pre-caption rail"
assert "graphItems.map" in intro, "Intro must render its configured middle-stage graph"
assert intro.index("/* Pills") < intro.index("/* Middle-stage graph") < intro.index("/* Bottom quote"), "Intro must keep the approved chips, graph, footer order"
assert 'gridTemplateColumns: "repeat(6, 1fr)"' in intro, "Locked intro must keep the approved three-plus-two module grid"
assert "const graphItems = [...data.centerGraph.nodes.slice(0, 4)" in intro, "Locked intro must render four nodes plus the fixed center card"
assert 'marginTop: "auto"' in intro, "Intro footer must stay anchored near the bottom"
assert 'data-design="cover-stage-frame"' in intro, "Intro needs one coherent stage frame without changing its content structure"
assert 'data-design="cover-graph"' in intro, "Intro graph needs its own visual hierarchy"
assert 'minHeight: 540' in skill, "Skill detail content must extend through the middle stage"
assert 'padding: "128px 118px 235px"' in workflow, "Workflow must not stay pinned to the top"
assert 'wordBreak: "normal"' in captions and 'overflowWrap: "break-word"' in captions, "English names must not break in the middle unless they cannot fit"
assert "WebkitLineClamp: 2" in captions, "Captions must never render a third line"
assert '"bento" | "index" | "spotlight"' in types_source, "Overview needs three distinct reusable silhouettes"
assert 'data.layoutVariant === "spotlight"' in overview_source, "The third overview silhouette must have a real renderer"
assert 'data-design="compare-spine"' in overview_source, "Compare scenes need a distinct split-screen visual language"
assert 'data-design="process-stage"' in overview_source, "Process scenes need a distinct route visual language"
assert 'data-design="case-stage"' in overview_source, "Case scenes need a distinct editorial-column visual language"
assert 'data-design="triangle-core"' in overview_source, "Relationship scenes need a distinct radial visual language"
assert (ROOT / "WORKBUDDY.md").is_file(), "WorkBuddy needs one fixed fast-path guide"
assert (ROOT / "AGENTS.md").is_file(), "Agents need an automatic project entrypoint"
assert (ROOT / "scripts" / "render_layout_contact_sheet.py").is_file(), "All scenes need one repeatable layout review"
contact_sheet = (ROOT / "scripts" / "render_layout_contact_sheet.py").read_text(encoding="utf-8")
assert 'else 0.72' in contact_sheet, "Body contact sheets must show the settled progressive layout"

print("template_presentation_policy=passed")
