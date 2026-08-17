#!/usr/bin/env python3
"""Plan visually distinct layouts from a generic content outline.

Input JSON: [{"title": "...", "text": "...", "items": ["..."]}]
The output is a production plan. It never changes voice, captions, or outro.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LAYOUT_META = {
    "comment_cta": ("cta", "comment-action", "口令先放大，领取内容再展开"),
    "compare": ("contrast", "split-stage", "左右同时进入，中间结论收束"),
    "case": ("proof", "three-act", "问题、做法、结果分三拍出现"),
    "triangle": ("relationship", "radial", "中心结论先出现，三个节点同步展开"),
    "process": ("process", "zigzag-path", "沿路径分段推进并高亮当前步骤"),
    "workflow": ("process", "timeline-rail", "时间轴逐段推进，末端显示结果"),
    "skill_detail": ("explain", "spotlight-list", "核心概念先出现，解释项成组展开"),
    "overview": ("overview", "bento-grid", "主项先出现，其余内容成组补齐"),
}

LAYOUT_CAPACITY = {"comment_cta": 3, "compare": 6, "case": 3, "triangle": 3, "process": 4, "workflow": 6, "skill_detail": 4, "overview": 5}
RELATION_LAYOUTS = {
    "comment": "comment_cta",
    "comment_cta": "comment_cta",
    "peers": "overview",
    "detail": "skill_detail",
    "sequence": "process",
    "workflow": "workflow",
    "contrast": "compare",
    "relationship": "triangle",
    "case": "case",
}
ACCENTS = ("#39FF14", "#00FFFF", "#FF1493", "#FFA500", "#8B5CF6", "#E4EF37")
ORDINAL_RE = re.compile(r"(第一|第二|第三|第四|第五|第六|第七|第八|第九|第十)[，,、]")
COMMENT_CTA_KEYWORDS = ("清单", "SOP", "模板", "模板包", "提示词", "检查表", "资料", "资料包", "工具包")


def item_count(section: dict) -> int:
    items = section.get("items") or section.get("steps") or section.get("columns") or []
    if items:
        return len(items)
    return len(section.get("left", {}).get("points", [])) + len(section.get("right", {}).get("points", []))


def choose_layout(section: dict) -> str:
    explicit = section.get("layout") or section.get("type")
    if explicit in LAYOUT_META:
        return explicit
    if is_comment_cta(section):
        return "comment_cta"
    relation = section.get("relation")
    if relation in RELATION_LAYOUTS:
        return RELATION_LAYOUTS[relation]
    text = f"{section.get('title', '')}{section.get('text', '')}{section.get('narration', '')}{section.get('contentRole', '')}"
    count = item_count(section)
    if re.search(r"对比|以前|现在|传统|区别|vs|VS|前后|错误.+正确|普通.+高阶", text) and count >= 2:
        return "compare"
    if re.search(r"案例|结果|实测|复盘|问题.+做法.+结果", text) and count == 3:
        return "case"
    if re.search(r"共同|三要素|支撑|闭环|关系|组成", text) and count == 3:
        return "triangle"
    if re.search(r"步骤|流程|先.+再|第一|第二|第三|路径|阶段", text) and count >= 2:
        return "process" if count <= 4 else "workflow"
    if re.search(r"工具|技能|能力|功能|方法|技巧|概念", text) and 2 <= count <= 4:
        return "skill_detail"
    return "overview"


def alternate(layout: str, previous_geometry: str | None, section: dict) -> str:
    """Avoid repeating the same silhouette when another valid layout exists."""
    geometry = LAYOUT_META[layout][1]
    if geometry != previous_geometry:
        return layout
    count = item_count(section)
    if layout == "overview" and 2 <= count <= 4:
        return "skill_detail"
    if layout == "skill_detail" and count >= 3:
        return "overview"
    if layout == "process":
        return "workflow"
    if layout == "workflow" and count <= 4:
        return "process"
    return layout


def density(section: dict) -> str:
    count = item_count(section)
    longest = max((len(str(item)) for item in section.get("items", [])), default=0)
    return "high" if count >= 5 or longest > 20 else "medium" if count >= 3 else "low"


def _item(value: object, index: int) -> dict:
    if isinstance(value, dict):
        title = str(value.get("title") or value.get("text") or value.get("label") or f"要点 {index + 1}")
        note = str(value.get("note") or value.get("subtitle") or value.get("value") or "")
        return {"title": title, "note": note, "color": value.get("color") or ACCENTS[index % len(ACCENTS)]}
    return {"title": str(value), "note": "", "color": ACCENTS[index % len(ACCENTS)]}


def _items(section: dict) -> list[dict]:
    values = section.get("items") or section.get("steps") or section.get("columns") or []
    return [_item(value, index) for index, value in enumerate(values)]


def compile_section(section: dict, index: int, layout: str, variant: str | None = None) -> dict:
    """Convert one generic semantic section into the real Remotion scene schema."""
    items = _items(section)
    base = {
        "type": layout,
        "durationFrames": int(section.get("durationFrames", 180)),
        "showSubtitle": bool(section.get("showSubtitle", True)),
        "narration": str(section.get("narration") or section.get("text") or "").strip(),
        "label": str(section.get("label") or f"内容 {index + 1:02d}"),
        "title": str(section.get("title") or f"核心内容 {index + 1}"),
    }
    if section.get("supportText"):
        base["supportText"] = str(section["supportText"])

    if layout == "comment_cta":
        base["keyword"] = str(section.get("keyword") or infer_comment_keyword(section))
        base["offer"] = str(section.get("offer") or section.get("supportText") or "把资料整理给你")
        base["subtitle"] = str(section.get("subtitle") or f"评论区打“{base['keyword']}”")
        base["items"] = items[:3] or [
            {"title": f"评论区打“{base['keyword']}”", "note": "领取本期资料", "color": ACCENTS[0]},
            {"title": "我整理给你", "note": base["offer"], "color": ACCENTS[1]},
        ]
    elif layout == "overview":
        base["subtitle"] = str(section.get("subtitle") or section.get("summary") or "核心信息一页看清")
        base["items"] = items
        if variant:
            base["layoutVariant"] = variant
    elif layout == "compare":
        if section.get("left") and section.get("right"):
            base["left"] = section["left"]
            base["right"] = section["right"]
        else:
            midpoint = max(1, (len(items) + 1) // 2)
            groups = (items[:midpoint], items[midpoint:] or items[:1])
            labels = section.get("groupTitles") or ["原来", "现在"]
            base["left"] = {
                "title": str(labels[0]), "subtitle": "旧方式", "color": ACCENTS[2],
                "points": [item["title"] for item in groups[0]],
            }
            base["right"] = {
                "title": str(labels[1]), "subtitle": "新方式", "color": ACCENTS[1],
                "points": [item["title"] for item in groups[1]],
            }
    elif layout == "process":
        base["subtitle"] = str(section.get("subtitle") or section.get("summary") or "按顺序完成关键动作")
        base["steps"] = items
    elif layout == "case":
        labels = ("问题", "做法", "结果")
        base["columns"] = [
            {"label": labels[i] if i < len(labels) else f"阶段 {i + 1}", **item}
            for i, item in enumerate(items[:3])
        ]
    elif layout == "triangle":
        base["center"] = str(section.get("center") or section.get("summary") or section.get("title") or "核心结果")
        base["nodes"] = items[:3]
    elif layout == "workflow":
        base.pop("label", None)
        base["subtitleText"] = str(section.get("subtitle") or section.get("summary") or "完整路径逐步跑通")
        base["steps"] = [
            {"number": str(i + 1), "title": item["title"], "subtitle": item["note"], "color": item["color"]}
            for i, item in enumerate(items)
        ]
    elif layout == "skill_detail":
        base.pop("label", None)
        base["skillNum"] = str(section.get("skillNum") or f"{index + 1:02d}")
        base["skillName"] = base.pop("title")
        base["desc"] = str(section.get("subtitle") or section.get("summary") or "核心能力拆解")
        base["mainColor"] = str(section.get("mainColor") or ACCENTS[index % len(ACCENTS)])
        base["details"] = [
            {"text": item["title"], "color": item["color"], "label": "说明", "value": item["note"]}
            for item in items
        ]
    return base


def compile_sections(sections: list[dict]) -> list[dict]:
    planned = plan_sections(sections)
    return [
        compile_section(section, index, section["layout"], section.get("layoutVariant"))
        for index, section in enumerate(planned)
    ]


def compile_document(document: object, current_scenes: list[dict]) -> list[dict]:
    """Compile an outline into real scenes while preserving the locked outro."""
    if isinstance(document, list):
        sections = document
        overrides: dict = {}
    elif isinstance(document, dict):
        sections = document.get("sections", [])
        overrides = document
    else:
        raise ValueError("content outline must be a JSON array or object")
    if not sections:
        raise ValueError("content outline has no sections")
    validate_outline_structure(sections)

    intro = next((scene for scene in current_scenes if scene.get("type") == "intro"), None)
    hook = next((scene for scene in current_scenes if scene.get("type") == "hook"), None)
    outro = next((scene for scene in reversed(current_scenes) if scene.get("type") == "outro"), None)
    if not intro or not hook or not outro:
        raise ValueError("current scenes must contain intro, hook and outro")
    intro_override = overrides.get("intro", {})
    hook_override = overrides.get("hook", {})
    resolved_intro = {**intro, **intro_override, "type": "intro", "durationFrames": 45}
    resolved_hook = {**hook, **hook_override, "type": "hook"}
    if "tags" not in hook_override:
        resolved_hook["tags"] = hook_tags_from_outline(intro_override, sections)
    return [resolved_intro, resolved_hook, *compile_sections(sections), outro]


def hook_tags_from_outline(intro: object, sections: list[dict]) -> list[dict]:
    """Derive hook badges from the current outline so old video tags cannot survive."""
    if isinstance(intro, dict):
        flow_items = intro.get("flowItems")
        if isinstance(flow_items, list) and flow_items:
            return [_flow_tag(item, index) for index, item in enumerate(flow_items[:3])]
    tags = []
    for section in sections:
        title = str(section.get("title") or "").strip()
        if title:
            tags.append(title)
        if len(tags) == 3:
            break
    return [_flow_tag(item, index) for index, item in enumerate(tags)]


def _flow_tag(value: object, index: int) -> dict:
    if isinstance(value, dict):
        text = str(value.get("text") or value.get("title") or value.get("label") or f"标签 {index + 1}")
        return {"text": text, "color": value.get("color") or ACCENTS[index % len(ACCENTS)]}
    return {"text": str(value), "color": ACCENTS[index % len(ACCENTS)]}


def validate_outline_structure(sections: list[dict]) -> None:
    """Reject outline shapes that make visuals drift away from narration."""
    last_section_text = section_text(sections[-1])
    if "评论" not in last_section_text or not any(keyword in last_section_text for keyword in COMMENT_CTA_KEYWORDS):
        raise ValueError(
            "content-outline.json 缺少片尾前评论区互动 section。"
            "最后一个 section 必须引导评论区互动，例如："
            "最后，如果你想要这期的工具包，评论区打“工具包”，我把判断标准整理给你。"
        )
    recommended_keyword = suggest_comment_keyword(sections)
    if recommended_keyword != "清单" and re.search(r"打[“\"]?清单[”\"]?", last_section_text):
        raise ValueError(
            "评论区互动口令太泛：当前内容更适合使用 "
            f"“{recommended_keyword}”，不要每条视频都写“清单”。"
        )
    for index, section in enumerate(sections, 1):
        narration = str(section.get("narration") or section.get("text") or "")
        ordinals = ORDINAL_RE.findall(narration)
        if len(ordinals) >= 3:
            raise ValueError(
                "content-outline.json 结构不合格：第 "
                f"{index} 个 section 一次讲了 {len(ordinals)} 个编号要点。"
                "请把“第一/第二/第三...”拆成独立 sections，"
                "不要把多个方法塞进一个 overview 页面。"
            )


def is_comment_cta(section: dict) -> bool:
    relation = str(section.get("relation") or section.get("layout") or section.get("type") or "")
    label = str(section.get("label") or "")
    title = str(section.get("title") or "")
    subtitle = str(section.get("subtitle") or "")
    narration = str(section.get("narration") or section.get("text") or "")
    return (
        relation in {"comment", "comment_cta"}
        or "评论区互动" in f"{label}{title}"
        or "评论区打" in subtitle
        or re.search(r"评论区打[“\"]?.+?[”\"]?", narration) is not None
    )


def suggest_comment_keyword(sections: list[dict]) -> str:
    text = "".join(section_text(section) for section in sections)
    if re.search(r"WorkBuddy|Codex|Skill|工具|插件|Agent|MCP", text, re.I):
        return "工具包"
    if re.search(r"模板|版式|框架|组件", text):
        return "模板包"
    if re.search(r"提示词|prompt", text, re.I):
        return "提示词"
    if re.search(r"检查|避坑|审计|复盘|校验", text):
        return "检查表"
    if re.search(r"SOP|流程|步骤|工作流|操作", text, re.I):
        return "SOP"
    if re.search(r"资料|资源|文档|案例库", text):
        return "资料包"
    return "清单"


def infer_comment_keyword(section: dict) -> str:
    text = section_text(section)
    for keyword in COMMENT_CTA_KEYWORDS:
        if keyword in text:
            return keyword
    return "资料包"


def section_text(section: dict) -> str:
    parts = [
        str(section.get("label") or ""),
        str(section.get("title") or ""),
        str(section.get("subtitle") or ""),
        str(section.get("supportText") or ""),
        str(section.get("narration") or section.get("text") or ""),
    ]
    for item in section.get("items") or []:
        if isinstance(item, dict):
            parts.extend(str(item.get(key) or "") for key in ("title", "text", "label", "note", "subtitle", "value"))
        else:
            parts.append(str(item))
    return "".join(parts)


def split_oversized(sections: list[dict]) -> list[dict]:
    result: list[dict] = []
    for section in sections:
        field = next((key for key in ("items", "steps", "columns") if section.get(key)), "items")
        items = section.get(field, [])
        capacity = LAYOUT_CAPACITY[choose_layout(section)]
        if len(items) <= capacity:
            result.append(section)
            continue
        chunks = [items[index:index + capacity] for index in range(0, len(items), capacity)]
        for index, chunk in enumerate(chunks, 1):
            result.append({**section, "title": f"{section.get('title', '')} · {index}/{len(chunks)}", field: chunk, "splitFromSource": True})
    return result


def plan_sections(sections: list[dict]) -> list[dict]:
    planned: list[dict] = []
    previous_geometry: str | None = None
    overview_count = 0
    for section in split_oversized(sections):
        layout = alternate(choose_layout(section), previous_geometry, section)
        role, geometry, motion = LAYOUT_META[layout]
        variant = None
        if layout == "overview":
            variant_cycle = (None, "index", "spotlight")
            variant = variant_cycle[overview_count % len(variant_cycle)]
            if variant == "index":
                geometry = "index-grid"
                motion = "编号轨道先出现，并列内容分组展开"
            elif variant == "spotlight":
                geometry = "spotlight-grid"
                motion = "主观点先占据左侧舞台，补充信息在右侧依次展开"
        if layout == "overview":
            overview_count += 1
        planned.append({
            **section,
            "contentRole": role,
            "layout": layout,
            "geometry": geometry,
            "density": density(section),
            "motion": motion,
            **({"layoutVariant": variant} if variant else {}),
        })
        previous_geometry = geometry
    return planned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sections = json.loads(args.input.read_text(encoding="utf-8"))
    result = json.dumps(plan_sections(sections), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
