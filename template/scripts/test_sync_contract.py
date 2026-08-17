#!/usr/bin/env python3
import json
from pathlib import Path

from build_video import (
    extract_formal_body,
    make_timeline,
    outline_narration_text,
    validate_narration_contract,
    validate_runtime_contract,
    validate_visual_contract,
)


ROOT = Path(__file__).resolve().parents[1]


script = (ROOT / "script.md").read_text(encoding="utf-8")
outline = json.loads((ROOT / "content-outline.json").read_text(encoding="utf-8"))
outro_text = json.loads((ROOT / "audio-pipeline.json").read_text(encoding="utf-8"))["outro_voice"]["text"]
formal_body = extract_formal_body(script, outro_text)
outline_body = outline_narration_text(outline)
validate_narration_contract(formal_body, outline_body)
validate_visual_contract(outline, json.loads((ROOT / "layout-scenes.json").read_text(encoding="utf-8")))

try:
    validate_visual_contract(
        {"intro": {"flowItems": [{"text": "本期新标签"}]}},
        [{"type": "hook", "tags": [{"text": "上一条旧标签"}]}],
    )
except ValueError as error:
    assert "hook 画面标签" in str(error)
else:
    raise AssertionError("stale hook tags must be rejected")


transcription = [
    {
        "text": "第一句话第二句话",
        "offsets": {"from": 0, "to": 1800},
        "tokens": [
            {"text": ch, "offsets": {"from": i * 200, "to": (i + 1) * 200}}
            for i, ch in enumerate("第一句话第二句话")
        ],
    }
]
captions = make_timeline("第一句话。第二句话。", transcription, 1800)
assert captions[0]["endMs"] <= captions[1]["startMs"], captions
assert captions[-1]["endMs"] <= 1800, captions


scenes = [
    {"type": "intro", "durationFrames": 45},
    {"type": "hook", "durationFrames": 69},
    {"type": "outro", "durationFrames": 105},
]
data = {
    "captions": captions,
    "audio": {
        "voiceover": {"startFrame": 45},
        "outro": {"startFrame": 114},
    },
}
validate_runtime_contract(data, scenes, 1800)

bad_scenes = [{**scenes[0], "durationFrames": 245}, *scenes[1:]]
try:
    validate_runtime_contract(data, bad_scenes, 1800)
except ValueError:
    pass
else:
    raise AssertionError("cover/audio mismatch must be rejected")

print("sync_contract=passed")
