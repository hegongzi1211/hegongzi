#!/usr/bin/env python3
import json
from copy import deepcopy
from pathlib import Path

from build_video import scene_duration_frames, validate_scenes
from plan_layouts import choose_layout, compile_document, compile_sections, plan_sections


sections = [
    {"title": "普通做法和正确做法对比", "items": ["普通", "正确"]},
    {"title": "三个因素共同形成闭环", "items": ["输入", "处理", "输出"]},
    {"title": "四步完成发布流程", "items": ["选题", "写作", "排版", "发布"]},
    {"title": "五个阶段跑通工作流", "items": ["一", "二", "三", "四", "五"]},
    {"title": "核心能力总览", "items": ["理解", "生成", "校验", "交付"]},
    {"title": "功能总览", "items": ["读取", "规划", "执行"]},
    {"title": "八项并列信息", "items": ["一", "二", "三", "四", "五", "六", "七", "八"]},
]

planned = plan_sections(sections)
assert [item["layout"] for item in planned[:4]] == ["compare", "triangle", "process", "workflow"]
assert all(item["geometry"] and item["motion"] for item in planned)
assert all(not (a["geometry"] == b["geometry"] == c["geometry"]) for a, b, c in zip(planned, planned[1:], planned[2:]))
assert len([item for item in planned if item.get("splitFromSource")]) == 2

semantic_sections = [
    {"relation": "peers", "title": "阶段一", "items": ["甲", "乙", "丙"]},
    {"relation": "detail", "title": "阶段二", "items": ["甲", "乙"]},
    {"relation": "sequence", "title": "阶段三", "steps": ["甲", "乙", "丙"]},
    {"relation": "contrast", "title": "阶段四", "items": ["甲", "乙"]},
    {"relation": "relationship", "title": "阶段五", "items": ["甲", "乙", "丙"]},
    {"relation": "case", "title": "阶段六", "columns": ["甲", "乙", "丙"]},
]
assert [choose_layout(section) for section in semantic_sections] == [
    "overview", "skill_detail", "process", "compare", "triangle", "case",
]

repeated_peer_sections = [
    {"relation": "peers", "title": "并列能力一", "items": ["甲", "乙", "丙", "丁"]},
    {"relation": "detail", "title": "单点解释", "items": ["甲", "乙", "丙"]},
    {"relation": "peers", "title": "并列能力二", "items": ["甲", "乙", "丙", "丁"]},
]
repeated_peer_plan = plan_sections(repeated_peer_sections)
assert [item.get("layoutVariant") for item in repeated_peer_plan] == [None, None, "index"], (
    "Non-consecutive peer sections need different overview geometries instead of repeating the same bento page"
)

three_peer_sections = [
    {"relation": "peers", "title": "并列能力一", "items": ["甲", "乙", "丙"]},
    {"relation": "detail", "title": "单点解释一", "items": ["甲", "乙", "丙"]},
    {"relation": "peers", "title": "并列能力二", "items": ["甲", "乙", "丙"]},
    {"relation": "detail", "title": "单点解释二", "items": ["甲", "乙", "丙"]},
    {"relation": "peers", "title": "并列能力三", "items": ["甲", "乙", "丙"]},
]
three_peer_plan = plan_sections(three_peer_sections)
peer_variants = [item.get("layoutVariant") for item in three_peer_plan if item["layout"] == "overview"]
assert peer_variants == [None, "index", "spotlight"], (
    "The third overview must use a new spotlight silhouette instead of cycling back to bento"
)

renderable = compile_sections(sections[:6])
assert [item["type"] for item in renderable[:4]] == ["compare", "triangle", "process", "workflow"]
assert "left" in renderable[0] and "right" in renderable[0]
assert len(renderable[1]["nodes"]) == 3
assert len(renderable[2]["steps"]) == 4
assert renderable[4]["type"] != renderable[5]["type"]

shell = [
    {"type": "intro", "title1": "旧封面"},
    {"type": "hook", "title": "旧钩子"},
    {"type": "outro", "userName": "【你的名字】", "locked": True},
]
compiled = compile_document({
    "intro": {"title1": "新封面", "flowItems": [{"text": "新标签一", "color": "#39FF14"}, {"text": "新标签二", "color": "#00FFFF"}]},
    "hook": {"title": "新钩子"},
    "sections": [
        *sections[:4],
        {"relation": "comment", "title": "评论区互动", "narration": "评论区打“工具包”，我把资料整理给你。", "items": ["评论区打“工具包”", "领取资料"]},
    ],
}, shell)
assert compiled[0]["title1"] == "新封面"
assert compiled[1]["title"] == "新钩子"
assert [tag["text"] for tag in compiled[1]["tags"]] == ["新标签一", "新标签二"]
assert [scene["type"] for scene in compiled[2:-1]] == ["compare", "triangle", "process", "workflow", "comment_cta"]
assert compiled[-1] == shell[-1]

timing = [
    {"text": "甲乙", "offsets": {"from": 0, "to": 3000}},
    {"text": "丙丁", "offsets": {"from": 3000, "to": 6000}},
]
durations = scene_duration_frames(["甲乙", "丙丁"], timing, 6000)
assert durations == [90, 90]
assert sum(durations) == 180

current = json.loads((Path(__file__).resolve().parents[1] / "layout-scenes.json").read_text(encoding="utf-8"))
validate_scenes(current)
fixture_body = deepcopy(renderable)
for scene in fixture_body:
    scene["narration"] = scene["title"] if "title" in scene else scene["skillName"]
fixture = [deepcopy(current[0]), deepcopy(current[1]), *fixture_body, deepcopy(current[-1])]
too_sparse = deepcopy(fixture)
overview_scene = next(scene for scene in too_sparse if scene["type"] == "overview")
overview_scene["items"] = overview_scene["items"][:1]
try:
    validate_scenes(too_sparse)
except SystemExit as error:
    assert "at least 2" in str(error)
else:
    raise AssertionError("overview with one item must be rejected instead of rendering a mostly empty page")
overview = next(scene for scene in fixture if scene["type"] == "overview")
detail = next(scene for scene in fixture if scene["type"] == "skill_detail")
try:
    validate_scenes([fixture[0], fixture[1], overview, detail, overview, detail, fixture[-1]])
except SystemExit as error:
    assert "至少需要 3 种视觉结构" in str(error)
else:
    raise AssertionError("four body scenes using only two visual geometries must be rejected before Voicebox runs")
try:
    validate_scenes([fixture[0], fixture[1], overview, detail, overview, detail, overview, fixture[-1]])
except SystemExit as error:
    assert "至少需要 3 种" in str(error)
else:
    raise AssertionError("five body scenes using only two layouts must be rejected")
print("layout_planner=passed")
