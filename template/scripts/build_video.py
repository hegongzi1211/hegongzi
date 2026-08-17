#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import os
from pathlib import Path

from plan_layouts import compile_document


ROOT = Path(__file__).resolve().parents[1]
FPS = 30
COVER_FRAMES = 45
NARRATION_TAIL_FRAMES = 15
VOICE_SCRIPT = ROOT / "scripts" / "voicebox_generate.py"
VOICE_CONFIG = ROOT / "audio-pipeline.json"
WHISPER_MODEL = Path(os.environ.get("WHISPER_MODEL_PATH", "models/ggml-small.bin"))
VOICE_FILTER = "aresample=48000"
BAD_VOICE_PATTERNS = (
    "技术站", "技术栈", "技术战", "历史策略", "历史决策", "习惯技术战",
    "技術站", "技術棧", "技術戰", "歷史策略", "歷史決策", "習慣技術戰",
    "装完Codex不知道", "裝完Codex不知道", "当然是做视频搞钱", "當然是做視頻搞錢",
)


def outline_title(document: object) -> str | None:
    if not isinstance(document, dict):
        return None
    explicit = str(document.get("title") or "").strip()
    if explicit:
        return explicit
    intro = document.get("intro") if isinstance(document.get("intro"), dict) else {}
    parts = [
        str(intro.get("title1") or "").strip(),
        str(intro.get("title2") or "").strip(),
        str(intro.get("title3") or "").strip(),
    ]
    title = "".join(part for part in parts if part)
    return title or None

REQUIRED_SCENE_FIELDS = {
    "intro": {"narration", "title1", "title2", "title3"},
    "hook": {"narration", "title", "tags"},
    "comment_cta": {"narration", "title", "keyword", "offer", "items"},
    "overview": {"narration", "title", "items"},
    "compare": {"narration", "title", "left", "right"},
    "process": {"narration", "title", "steps"},
    "case": {"narration", "title", "columns"},
    "triangle": {"narration", "title", "center", "nodes"},
    "skill_detail": {"narration", "skillName", "details"},
    "workflow": {"narration", "title", "steps"},
    "outro": set(),
}

LAYOUT_LIMITS = {
    "comment_cta": ("items", 3),
    "overview": ("items", 5),
    "compare": (None, 6),
    "process": ("steps", 4),
    "case": ("columns", 3),
    "triangle": ("nodes", 3),
    "skill_detail": ("details", 4),
    "workflow": ("steps", 6),
}

LAYOUT_MINIMUMS = {
    "comment_cta": 1,
    "overview": 2,
    "compare": 2,
    "process": 2,
    "case": 3,
    "triangle": 3,
    "skill_detail": 2,
    "workflow": 3,
}

VISUAL_FAMILIES = {
    "comment_cta": "comment-action",
    "overview": "bento-grid",
    "compare": "split-stage",
    "process": "zigzag-path",
    "case": "three-act",
    "triangle": "radial",
    "skill_detail": "spotlight-list",
    "workflow": "timeline-rail",
}


def visual_family(scene: dict) -> str | None:
    if scene.get("type") != "overview":
        return VISUAL_FAMILIES.get(scene.get("type"))
    return {
        "index": "index-grid",
        "spotlight": "spotlight-grid",
    }.get(scene.get("layoutVariant"), "bento-grid")

CONTENT_ROLES = {
    "intro": "cover", "hook": "hook", "overview": "overview", "compare": "contrast",
    "process": "process", "case": "proof", "triangle": "relationship",
    "skill_detail": "explain", "workflow": "process", "comment_cta": "cta", "outro": "cta",
}

MOTION_POLICIES = {
    "comment_cta": "评论口令放大，领取内容分层展开",
    "overview": "主项先出现，其余成组补齐", "compare": "左右进入，中间结论收束",
    "process": "沿折线路径推进", "case": "问题、做法、结果分三拍出现",
    "triangle": "中心向外展开", "skill_detail": "核心概念与解释清单分区进入",
    "workflow": "中轴时间线逐段推进",
}


def validate_scenes(scenes: list[dict]) -> None:
    if not scenes or scenes[0].get("type") != "intro" or scenes[-1].get("type") != "outro":
        raise SystemExit("Scenes must start with intro and end with outro")
    repeated = 1
    repeated_family = 1
    previous_family = None
    for index, scene in enumerate(scenes):
        scene_type = scene.get("type")
        if scene_type not in REQUIRED_SCENE_FIELDS:
            raise SystemExit(f"Unsupported layout at scene {index + 1}: {scene_type}")
        missing = REQUIRED_SCENE_FIELDS[scene_type] - scene.keys()
        if missing:
            raise SystemExit(f"Scene {index + 1} missing fields: {', '.join(sorted(missing))}")
        if index and scene_type == scenes[index - 1].get("type"):
            repeated += 1
            if repeated > 2 and scene_type not in {"skill_detail"}:
                raise SystemExit(f"Layout repeated more than twice: {scene_type}")
        else:
            repeated = 1

        family = visual_family(scene)
        if family and family == previous_family:
            repeated_family += 1
            if repeated_family > 2:
                raise SystemExit(f"Visual geometry repeated more than twice: {family}")
        else:
            repeated_family = 1
        previous_family = family

        if scene_type in LAYOUT_LIMITS:
            field, maximum = LAYOUT_LIMITS[scene_type]
            count = len(scene.get(field, [])) if field else len(scene.get("left", {}).get("points", [])) + len(scene.get("right", {}).get("points", []))
            minimum = LAYOUT_MINIMUMS[scene_type]
            if count < minimum:
                raise SystemExit(f"Scene {index + 1} has {count} items; {scene_type} needs at least {minimum}. Choose a simpler layout or add meaningful content.")
            if count > maximum:
                raise SystemExit(f"Scene {index + 1} has {count} items; {scene_type} allows {maximum}. Split the scene instead of shrinking text.")
            title = scene.get("title") or scene.get("skillName") or ""
            if compact_len(title) > 35:
                raise SystemExit(f"Scene {index + 1} title is too long. Split the scene instead of shrinking the body layout.")

    body_types = [scene["type"] for scene in scenes if scene["type"] not in {"intro", "hook", "outro"}]
    body_families = [
        visual_family(scene)
        for scene in scenes if scene["type"] not in {"intro", "hook", "outro"}
    ]
    if len(body_families) >= 4 and len(set(body_families)) < 3:
        raise SystemExit("正文达到 4 页时至少需要 3 种视觉结构；请重新识别内容关系后再生成旁白")
    if len(body_types) >= 5 and len(set(body_types)) < 3:
        raise SystemExit("正文达到 5 页时至少需要 3 种语义版式；请先运行自动选版，不要继续套同一种页面")


def layout_audit(scenes: list[dict]) -> list[dict]:
    result = []
    for index, scene in enumerate(scenes):
        scene_type = scene["type"]
        family = visual_family(scene) or scene_type
        field = LAYOUT_LIMITS.get(scene_type, (None, 0))[0]
        count = len(scene.get(field, [])) if field else len(scene.get("left", {}).get("points", [])) + len(scene.get("right", {}).get("points", [])) if scene_type == "compare" else 0
        result.append({
            "scene": index + 1,
            "contentRole": CONTENT_ROLES[scene_type],
            "layout": scene_type,
            "geometry": family,
            "itemCount": count,
            "motion": MOTION_POLICIES.get(scene_type, "固定品牌动画"),
        })
    return result


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def voice_cache_matches(cache_path: Path, cache_key: str, required_files: list[Path]) -> bool:
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if cache.get("version") != 2 or cache.get("key") != cache_key:
        return False
    if len(required_files) != 2 or not all(path.is_file() for path in required_files):
        return False
    audio, timing = required_files
    return (
        cache.get("audio_sha256") == file_sha256(audio)
        and cache.get("timing_sha256") == file_sha256(timing)
    )


def write_voice_cache(cache_path: Path, cache_key: str, audio: Path, timing: Path) -> None:
    cache_path.write_text(json.dumps({
        "version": 2,
        "key": cache_key,
        "audio_sha256": file_sha256(audio),
        "timing_sha256": file_sha256(timing),
    }, indent=2) + "\n", encoding="utf-8")


def compact_len(text: str) -> int:
    return len(re.sub(r"[\s，。！？、；：,.!?;:]", "", text))


def normalize_contract_text(text: str) -> str:
    return re.sub(r"[\s，。！？、；：,.!?;:“”‘’\"'（）()\-—→+]", "", text).lower()


def extract_formal_body(script: str, outro_text: str) -> str:
    match = re.search(r"^## 正式口播\s*$", script, flags=re.MULTILINE)
    if not match:
        raise ValueError("script.md 缺少“## 正式口播”")
    formal = script[match.end():].strip()
    n_formal = normalize_contract_text(formal)
    n_outro = normalize_contract_text(outro_text)
    if not n_outro:
        raise ValueError("outro_text 不能为空")
    if not n_formal.endswith(n_outro):
        raise ValueError("正式口播必须以 audio-pipeline.json 的 outro_voice.text 结尾")
    marker_raw = len(formal)
    need = len(n_outro)
    seen = 0
    for i in range(len(formal) - 1, -1, -1):
        ch = formal[i]
        if ch not in " \t\n\r　，。！？、；：,.!?;:\u201c\u201d\u2018\u2019\"'（）()\\-—→+":
            seen += 1
        if seen == need:
            marker_raw = i
            break
    return formal[:marker_raw].strip()


def outline_narration_text(document: object) -> str:
    if not isinstance(document, dict):
        raise ValueError("content-outline.json 必须是包含 hook 和 sections 的对象")
    hook = str(document.get("hook", {}).get("narration", "")).strip()
    sections = document.get("sections", [])
    narrations = [str(section.get("narration", "")).strip() for section in sections]
    if not hook or not narrations or not all(narrations):
        raise ValueError("content-outline.json 的 hook 与每个 section 都必须填写 narration")
    return "".join([hook, *narrations])


def outline_hook_tags(document: object) -> list[str]:
    if not isinstance(document, dict):
        return []
    intro = document.get("intro") if isinstance(document.get("intro"), dict) else {}
    flow_items = intro.get("flowItems") if isinstance(intro, dict) else None
    if isinstance(flow_items, list) and flow_items:
        tags = []
        for item in flow_items[:3]:
            if isinstance(item, dict):
                tags.append(str(item.get("text") or item.get("title") or "").strip())
            else:
                tags.append(str(item).strip())
        return [tag for tag in tags if tag]
    return []


def validate_visual_contract(document: object, scenes: list[dict]) -> None:
    expected_tags = outline_hook_tags(document)
    if not expected_tags:
        return
    hook = next((scene for scene in scenes if scene.get("type") == "hook"), None)
    if not hook:
        raise ValueError("layout-scenes.json 缺少 hook 场景")
    actual_tags = []
    for item in hook.get("tags") or []:
        if isinstance(item, dict):
            actual_tags.append(str(item.get("text") or item.get("title") or "").strip())
        else:
            actual_tags.append(str(item).strip())
    expected = [normalize_contract_text(tag) for tag in expected_tags]
    actual = [normalize_contract_text(tag) for tag in actual_tags[:len(expected_tags)]]
    if actual != expected:
        raise ValueError(
            "hook 画面标签不是来自当前 content-outline.json，可能残留上一条视频文案："
            f"expected={expected_tags}, actual={actual_tags[:len(expected_tags)]}"
        )


def validate_narration_contract(formal_body: str, structured_body: str) -> None:
    formal = normalize_contract_text(formal_body)
    structured = normalize_contract_text(structured_body)
    if formal != structured:
        raise ValueError(
            "正式口播与内容结构的旁白不一致；禁止生成不同版本的音频、字幕和画面 "
            f"(script={len(formal)} chars, scenes={len(structured)} chars)"
        )


def split_captions(text: str, limit: int = 18) -> list[str]:
    """Split Chinese captions without ever merging across sentence boundaries."""
    def clean(value: str) -> str:
        value = re.sub(r"\s+", " ", value).strip()
        return re.sub(r"^[，。！？、；：,.!?;:\s]+|[，。！？、；：,.!?;:\s]+$", "", value)

    def hard_split(value: str) -> list[str]:
        chunks: list[str] = []
        rest = clean(value)
        while compact_len(rest) > limit:
            semantic_tokens = ("拆成", "变成", "而是", "所以", "但是", "如果", "然后", "再去", "就能", "才能", "直接", "比如", "等你", "甚至", "实现", "继续")
            semantic_cuts = [rest.find(token) for token in semantic_tokens if 6 <= rest.find(token) <= limit]
            # Consecutive Latin words and product/version names are one atom.
            # This prevents cuts inside "Work Buddy" or "Qwen3-TTS 0.6B".
            atoms = list(re.finditer(r"[A-Za-z0-9]+(?:[-_.+/][A-Za-z0-9]+)*(?:\s+[A-Za-z0-9]+(?:[-_.+/][A-Za-z0-9]+)*)*|.", rest))
            safe_cuts = [match.end() for match in atoms if compact_len(rest[:match.end()]) <= limit]
            cut = safe_cuts[-1] if safe_cuts else atoms[0].end()
            if semantic_cuts:
                semantic_cut = max(semantic_cuts)
                cut = max((point for point in safe_cuts if point <= semantic_cut), default=cut)
            elif compact_len(rest[cut:]) < 6:
                target = (compact_len(rest) + 1) // 2
                cut = min((match.end() for match in atoms), key=lambda point: abs(compact_len(rest[:point]) - target))
            cut = cut or len(rest)
            chunks.append(clean(rest[:cut]))
            rest = clean(rest[cut:])
        if rest:
            chunks.append(rest)
        return [chunk for chunk in chunks if chunk]

    result: list[str] = []
    sentences = [part.strip() for part in re.split(r"(?<=[。！？；!?;])", text) if part.strip()]
    for sentence in sentences:
        phrases = [part.strip() for part in re.split(r"(?<=[，、：,:])", sentence) if part.strip()]
        sentence_chunks: list[str] = []
        current = ""
        for phrase in phrases:
            candidate = current + phrase
            if current and compact_len(candidate) > limit:
                sentence_chunks.extend(hard_split(current))
                current = phrase
            else:
                current = candidate
        if current:
            sentence_chunks.extend(hard_split(current))

        # Merge tiny phrases only inside the same sentence.
        merged: list[str] = []
        for chunk in sentence_chunks:
            if merged and compact_len(chunk) < 6 and compact_len(merged[-1] + chunk) <= limit:
                merged[-1] = clean(merged[-1] + chunk)
            else:
                merged.append(clean(chunk))
        result.extend(chunk for chunk in merged if chunk)

    return result if result else [clean(text)]


def caption_fits_policy(text: str) -> bool:
    if compact_len(text) <= 18:
        return True
    # A standalone product/version name is one semantic atom. It may wrap as a
    # whole word but must never be cut into misleading fragments.
    return bool(re.fullmatch(r"[A-Za-z0-9]+(?:[-_.+/][A-Za-z0-9]+)*", text.strip())) and len(text.strip()) <= 32


def duration_ms(path: Path) -> int:
    value = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], text=True).strip()
    return round(float(value) * 1000)


def ratio_to_time(ratio: float, transcription: list[dict], total_ms: int) -> int:
    lengths = [max(1, compact_len(item["text"])) for item in transcription]
    target = ratio * sum(lengths)
    consumed = 0
    for item, length in zip(transcription, lengths):
        if consumed + length >= target:
            local = max(0.0, min(1.0, (target - consumed) / length))
            start = item["offsets"]["from"]
            end = item["offsets"]["to"]
            return round(start + (end - start) * local)
        consumed += length
    return total_ms


def scene_duration_frames(
    narrations: list[str],
    transcription: list[dict],
    total_ms: int,
    tail_frames: int = 0,
) -> list[int]:
    """Resolve cumulative audio boundaries once so per-scene rounding cannot drift."""
    total_chars = max(1, sum(compact_len(text) for text in narrations))
    consumed = 0
    boundaries_ms = [0]
    for narration in narrations:
        consumed += compact_len(narration)
        boundaries_ms.append(ratio_to_time(consumed / total_chars, transcription, total_ms))
    boundaries_ms[-1] = total_ms
    # Cut intermediate visuals at or just before the first caption of the next
    # semantic section. Rounding up by one frame leaves that caption on the old page.
    boundaries_frames = [value * FPS // 1000 for value in boundaries_ms]
    boundaries_frames[-1] = math.ceil(total_ms / 1000 * FPS)
    durations = [end - start for start, end in zip(boundaries_frames, boundaries_frames[1:])]
    if any(duration < 45 for duration in durations):
        raise SystemExit("旁白场景短于 1.5 秒，请合并内容，而不是用补帧制造音画错位")
    durations[-1] += tail_frames
    return durations


# ── Forced Alignment (NW) 替代字符占比法 ──────────────────────────
# 根因: ES static import JSON + webpack cache 导致 Remotion 用旧 bundle
# 渲染。同时字符占比法的 scene 边界有累积漂移(虽然此案例仅 ~1.3s)。
# 改用 whisper token 级时间戳做 forced alignment，确保画面边界 = 真实音频内容。


def _clean_for_align(s: str) -> str:
    _punct = "\t\n\r \u3000\uff0c\u3002\uff01\uff1f\u3001\uff1b\uff1a,\uff1e.!?;:[\\]_*(\uff08)\uff09\"'\u201c\u201d\u2018\u2019"
    return s.lower().translate(str.maketrans("", "", _punct))


def _flatten_transcription_tokens(transcription: list[dict]) -> list[tuple[str, int, int]]:
    chars: list[tuple[str, int, int]] = []
    for seg in transcription:
        for tok in (seg.get("tokens") or []):
            t = tok.get("text", "")
            if not t or t.startswith("[_"):
                continue
            f, o = tok["offsets"]["from"], tok["offsets"]["to"]
            for ch in t:
                if ch == " ":
                    continue
                chars.append((ch.lower(), f, o))
    return chars


def _nw_align(ref_chars: list[str], hyp_chars: list[tuple[str, int, int]]) -> dict[int, int]:
    n, m = len(ref_chars), len(hyp_chars)
    prev = [-j for j in range(m + 1)]
    bt = bytearray(n * (m + 1))
    DIAG, UP, LEFT = 1, 2, 3
    for i in range(1, n + 1):
        cur = [0] * (m + 1)
        cur[0] = -i
        r = ref_chars[i - 1]
        for j in range(1, m + 1):
            hc = hyp_chars[j - 1][0]
            match_score = 2 if r == hc else -1
            d = prev[j - 1] + match_score
            u = prev[j] - 1
            l = cur[j - 1] - 1
            best, b = d, DIAG
            if u > best:
                best, b = u, UP
            if l > best:
                best, b = l, LEFT
            cur[j] = best
            bt[(i - 1) * (m + 1) + j] = b
        prev = cur
    i, j = n, m
    ref_to_hyp: dict[int, int] = {}
    while i > 0 and j > 0:
        b = bt[(i - 1) * (m + 1) + j]
        if b == DIAG:
            ref_to_hyp[i - 1] = j - 1; i -= 1; j -= 1
        elif b == UP:
            i -= 1
        else:
            j -= 1
    return ref_to_hyp


def align_part_ranges(parts: list[str], transcription: list[dict], total_ms: int) -> list[tuple[int, int]]:
    """Align ordered source-text parts to one continuous narration transcript."""
    cleaned = [_clean_for_align(part) for part in parts]
    if any(not part for part in cleaned):
        raise ValueError("对齐文本包含空段")
    target = "".join(cleaned)
    hyp = _flatten_transcription_tokens(transcription)
    if not hyp:
        raise ValueError("Whisper 没有返回可用于对齐的 token 时间戳")
    ref_to_hyp = _nw_align(list(target), hyp)
    mapped = sorted(ref_to_hyp)
    if not mapped:
        raise ValueError("正式口播与 Whisper 转写无法对齐")

    def nearest(ref_index: int) -> int:
        return min(mapped, key=lambda value: abs(value - ref_index))

    ranges: list[tuple[int, int]] = []
    position = 0
    previous_end = 0
    for part in cleaned:
        start_ref = position
        end_ref = position + len(part) - 1
        position += len(part)
        start_hyp = ref_to_hyp[nearest(start_ref)]
        end_hyp = ref_to_hyp[nearest(end_ref)]
        start = max(previous_end, hyp[start_hyp][1])
        end = min(total_ms, max(start + 1, hyp[end_hyp][2]))
        ranges.append((start, end))
        previous_end = end
    return ranges


def align_scene_boundaries(
    narrations: list[str],
    transcription: list[dict],
    total_ms: int,
    tail_frames: int = 0,
) -> list[int]:
    ranges = align_part_ranges(narrations, transcription, total_ms)
    boundaries_ms = [0, *[start for start, _ in ranges[1:]], total_ms]
    boundaries_frames = [max(0, v * FPS // 1000) for v in boundaries_ms]
    boundaries_frames[-1] = math.ceil(total_ms / 1000 * FPS)
    durations = [end - start for start, end in zip(boundaries_frames, boundaries_frames[1:])]
    if any(d < 45 for d in durations):
        raise SystemExit("旁白场景短于 1.5 秒，请合并内容")
    durations[-1] += tail_frames

    print("alignment=forced_nw")
    for i, (duration, (start, end)) in enumerate(zip(durations, ranges)):
        print(f"  scene_align[{i}] {(end-start)/1000:.2f}s/{duration}f | {narrations[i][:32]}")

    return durations


def make_timeline(script: str, transcription: list[dict], total_ms: int) -> list[dict]:
    chunks = split_captions(script)
    ranges = align_part_ranges(chunks, transcription, total_ms)
    return [
        {"text": chunk, "startMs": start, "endMs": end}
        for chunk, (start, end) in zip(chunks, ranges)
    ]


def validate_runtime_contract(data: dict, scenes: list[dict], total_ms: int) -> None:
    if not scenes or scenes[0].get("type") != "intro" or scenes[-1].get("type") != "outro":
        raise ValueError("时间轴必须以封面开始、锁定片尾结束")
    if scenes[0].get("durationFrames") != COVER_FRAMES:
        raise ValueError(f"封面必须固定为 {COVER_FRAMES} 帧")
    audio = data.get("audio", {})
    if audio.get("voiceover", {}).get("startFrame") != COVER_FRAMES:
        raise ValueError("正文旁白必须在封面结束的同一帧开始")
    expected_outro = COVER_FRAMES + math.ceil(total_ms / 1000 * FPS) + NARRATION_TAIL_FRAMES
    actual_outro = audio.get("outro", {}).get("startFrame")
    visual_outro = sum(scene["durationFrames"] for scene in scenes[:-1])
    if actual_outro != expected_outro or visual_outro != expected_outro:
        raise ValueError(
            f"片尾起点错误：expected={expected_outro}, audio={actual_outro}, visual={visual_outro}"
        )
    previous_end = -1
    for index, caption in enumerate(data.get("captions", [])):
        start, end = caption["startMs"], caption["endMs"]
        if start < previous_end:
            raise ValueError(f"字幕第 {index + 1} 条与上一条重叠")
        if end <= start or end > total_ms:
            raise ValueError(f"字幕第 {index + 1} 条时间无效")
        if not caption_fits_policy(caption["text"]):
            raise ValueError(f"字幕第 {index + 1} 条超过单条长度限制")
        previous_end = end
    if not data.get("captions") or total_ms - data["captions"][-1]["endMs"] > 1000:
        raise ValueError("字幕没有覆盖到正文旁白结尾")


def main() -> None:
    lock_path = ROOT / "generated" / ".build.lock"
    lock_path.parent.mkdir(exist_ok=True)
    build_lock = lock_path.open("w")
    try:
        fcntl.flock(build_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("已有视频生成任务正在运行，请等待完成后再试")

    parser = argparse.ArgumentParser(description="Build the reusable HGZ Remotion video pipeline.")
    parser.add_argument("--data", default="video-data.json")
    parser.add_argument("--scenes", default="layout-scenes.json")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--output", default="out/generated-video.mp4")
    parser.add_argument("--script", default="script.md", help="Final viral spoken script contract")
    parser.add_argument("--outline", default=None, help="Generic content outline; defaults to content-outline.json when present")
    args = parser.parse_args()

    script_path = (ROOT / args.script).resolve()
    if not script_path.exists():
        raise SystemExit("缺少 script.md：必须先完成爆款口播脚本，才能生成旁白")
    run([sys.executable, str(ROOT / "scripts" / "validate_viral_script.py"), str(script_path)])

    data_path = (ROOT / args.data).resolve()
    data = json.loads(data_path.read_text(encoding="utf-8"))
    scenes_path = (ROOT / args.scenes).resolve()
    if scenes_path.exists():
        data["scenes"] = json.loads(scenes_path.read_text(encoding="utf-8"))
    outline_path = (ROOT / args.outline).resolve() if args.outline else ROOT / "content-outline.json"
    if outline_path.exists():
        outline = json.loads(outline_path.read_text(encoding="utf-8"))
        title = outline_title(outline)
        if title:
            data["title"] = title
        data["scenes"] = compile_document(outline, data["scenes"])
        try:
            validate_visual_contract(outline, data["scenes"])
        except ValueError as error:
            raise SystemExit(str(error)) from error
        print("layout_types=" + ",".join(scene["type"] for scene in data["scenes"]))
    validate_scenes(data["scenes"])
    if outline_path.exists():
        scenes_path.write_text(json.dumps(data["scenes"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    body_scenes = [scene for scene in data["scenes"] if scene["type"] != "outro"]
    narrations = [scene.get("narration", "").strip() for scene in body_scenes]
    if not all(narrations):
        missing = [str(index + 1) for index, value in enumerate(narrations) if not value]
        raise SystemExit(f"Scenes missing narration: {', '.join(missing)}")

    voice_config = json.loads(VOICE_CONFIG.read_text(encoding="utf-8"))
    provider = voice_config.get("provider")
    if provider != "voicebox_local":
        raise SystemExit("当前Remotion模板只允许使用锁定的本机Voicebox声音方案")
    script_source = script_path.read_text(encoding="utf-8")
    try:
        narration_text = extract_formal_body(script_source, voice_config["outro_voice"]["text"])
        validate_narration_contract(narration_text, "".join(narrations[1:]))
        if outline_path.exists():
            validate_narration_contract(narration_text, outline_narration_text(outline))
    except ValueError as error:
        raise SystemExit(str(error)) from error

    generated = ROOT / "generated"
    public_audio = ROOT / "public" / "generated"
    generated.mkdir(exist_ok=True)
    (generated / "layout-audit.json").write_text(json.dumps(layout_audit(data["scenes"]), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public_audio.mkdir(parents=True, exist_ok=True)
    # 封面(intro)是静音画面，其 narration 不进音频、不参与正文时长计算，
    # 否则会把封面旁白时长错误地并入 hook 场景，导致后续字幕/语音整体累积错位。
    text_path = generated / "narration.txt"
    raw_audio = generated / "narration-raw.wav"
    final_audio = public_audio / "narration.wav"
    whisper_input = generated / "narration-16k.wav"
    whisper_base = generated / "narration-timing"
    cache_key = hashlib.sha256(
        narration_text.encode("utf-8")
        + VOICE_CONFIG.read_bytes()
        + VOICE_SCRIPT.read_bytes()
        + VOICE_FILTER.encode("utf-8")
    ).hexdigest()
    cache_path = generated / "narration-cache.json"
    timing_path = whisper_base.with_suffix(".json")
    reuse_voice = voice_cache_matches(cache_path, cache_key, [final_audio, timing_path])
    text_path.write_text(narration_text, encoding="utf-8")
    if reuse_voice:
        print("voice_cache=hit")
    else:
        print("voice_cache=miss")
        run([sys.executable, str(VOICE_SCRIPT), "--text-file", str(text_path), "--output", str(raw_audio)])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw_audio), "-af", VOICE_FILTER, "-c:a", "pcm_s16le", str(final_audio)])
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(final_audio), "-ac", "1", "-ar", "16000", str(whisper_input)])
        run(["whisper-cli", "-m", str(WHISPER_MODEL), "-l", "zh", "-f", str(whisper_input), "-ojf", "-ml", "14", "-sow", "-of", str(whisper_base), "--no-prints"])
        write_voice_cache(cache_path, cache_key, final_audio, timing_path)

    timing = json.loads(timing_path.read_text(encoding="utf-8"))
    transcription = timing["transcription"]
    transcript_text = "".join(item["text"] for item in transcription)
    contamination = [pattern for pattern in BAD_VOICE_PATTERNS if pattern in transcript_text]
    if contamination:
        raise SystemExit(f"Voicebox整条旁白仍有参考污染，已拒绝渲染：{', '.join(contamination)}")
    total_ms = duration_ms(final_audio)
    data["captions"] = make_timeline(narration_text, transcription, total_ms)

    if body_scenes[0]["type"] != "intro" or len(body_scenes) < 2:
        raise SystemExit("The first scene must be an intro cover followed by a body scene")
    timed_scenes = body_scenes[1:]
    # 修复：封面旁白不并入 hook，timed_narrations 从 hook 开始（与 timed_scenes 一一对应）
    timed_narrations = narrations[1:]
    resolved_durations = align_scene_boundaries(
        timed_narrations,
        transcription,
        total_ms,
        tail_frames=NARRATION_TAIL_FRAMES,
    )
    body_scenes[0]["durationFrames"] = COVER_FRAMES
    for scene, duration in zip(timed_scenes, resolved_durations):
        scene["durationFrames"] = duration
    outro_start = sum(scene["durationFrames"] for scene in body_scenes)
    data["audio"] = {
        "voiceover": {"src": "generated/narration.wav", "volume": 1, "startFrame": COVER_FRAMES},
        "outro": {"src": "generated/outro-voice.wav", "volume": 1, "startFrame": outro_start},
    }

    try:
        validate_runtime_contract(data, data["scenes"], total_ms)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    scenes_path.write_text(json.dumps(data["scenes"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (generated / "captions.json").write_text(json.dumps(data["captions"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(data_path, generated / "resolved-video-data.json")
    print(f"voice_source=voicebox:{voice_config['profile_id']}")
    print(f"voice_model={voice_config['model_name']}:{voice_config['model_size']}")
    print(f"voice_mode={voice_config['generation_mode']}")
    print(f"outro_voice_source=voicebox:{voice_config['outro_voice']['profile_id']}")
    print(f"narration={final_audio}")
    print(f"captions={generated / 'captions.json'}")

    if args.render:
        # 强制清除 webpack / Remotion 编译缓存。
        # Root.tsx 用 ES static import 加载 video-data.json / layout-scenes.json，
        # webpack 会把 JSON 内嵌到 bundle；不清缓存则 Remotion 用旧 bundle 渲染，
        # 导致画面内容与当前 JSON 数据不一致（已确认的根因）。
        import shutil as _shutil
        for _cache_dir in [
            ROOT / "node_modules" / ".cache",
            ROOT / "node_modules" / ".remotion",
        ]:
            if _cache_dir.is_dir():
                _shutil.rmtree(_cache_dir, ignore_errors=True)
                print(f"cache_cleared={_cache_dir.name}")

        run([sys.executable, str(ROOT / "scripts" / "verify_sync.py")])
        run(["npx", "remotion", "render", "VideoTemplate", args.output, "--codec=h264", "--crf=20", "--concurrency=10", "--overwrite"])


if __name__ == "__main__":
    main()
