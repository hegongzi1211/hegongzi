#!/usr/bin/env python3
"""Fail closed when narration, captions, scenes, or cached timing are from different builds."""
import json
from pathlib import Path

from build_video import (
    duration_ms,
    extract_formal_body,
    normalize_contract_text,
    outline_narration_text,
    validate_narration_contract,
    validate_visual_contract,
    validate_runtime_contract,
    voice_cache_matches,
)


ROOT = Path(__file__).resolve().parents[1]
SCENES = ROOT / "layout-scenes.json"
DATA = ROOT / "video-data.json"
CAPTIONS = ROOT / "generated" / "captions.json"
TIMING = ROOT / "generated" / "narration-timing.json"
AUDIO = ROOT / "public" / "generated" / "narration.wav"
CACHE = ROOT / "generated" / "narration-cache.json"


scenes = json.loads(SCENES.read_text(encoding="utf-8"))
data = json.loads(DATA.read_text(encoding="utf-8"))
generated_captions = json.loads(CAPTIONS.read_text(encoding="utf-8"))
outline = json.loads((ROOT / "content-outline.json").read_text(encoding="utf-8"))
voice = json.loads((ROOT / "audio-pipeline.json").read_text(encoding="utf-8"))
formal_body = extract_formal_body(
    (ROOT / "script.md").read_text(encoding="utf-8"),
    voice["outro_voice"]["text"],
)
scene_body = "".join(
    scene.get("narration", "").strip()
    for scene in scenes
    if scene.get("type") not in {"intro", "outro"}
)
validate_narration_contract(formal_body, outline_narration_text(outline))
validate_narration_contract(formal_body, scene_body)
try:
    validate_visual_contract(outline, scenes)
except ValueError as error:
    raise SystemExit(f"SYNC FAIL: {error}") from error

if data.get("captions") != generated_captions:
    raise SystemExit("SYNC FAIL: video-data.json 与 generated/captions.json 不是同一版字幕")

caption_body = "".join(caption["text"] for caption in data.get("captions", []))
if normalize_contract_text(caption_body) != normalize_contract_text(formal_body):
    raise SystemExit("SYNC FAIL: 字幕文字不是来自 script.md 正式口播")

audio_ms = duration_ms(AUDIO)
try:
    validate_runtime_contract(data, scenes, audio_ms)
except ValueError as error:
    raise SystemExit(f"SYNC FAIL: {error}") from error

cache = json.loads(CACHE.read_text(encoding="utf-8"))
if not voice_cache_matches(CACHE, cache.get("key", ""), [AUDIO, TIMING]):
    raise SystemExit("SYNC FAIL: 旁白、Whisper 时间轴与缓存清单不是同一批次")

print(
    "SYNC OK: script, outline, scenes, narration, captions, timing, cover, "
    "tail pause, and outro share one build."
)
