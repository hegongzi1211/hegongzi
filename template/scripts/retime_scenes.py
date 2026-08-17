#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path

from build_video import COVER_FRAMES, duration_ms, scene_duration_frames


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    layout_path = ROOT / "layout-scenes.json"
    data_path = ROOT / "video-data.json"
    timing_path = ROOT / "generated" / "narration-timing.json"
    narration_path = ROOT / "public" / "generated" / "narration.wav"
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))
    transcription = json.loads(timing_path.read_text(encoding="utf-8"))["transcription"]

    body = [scene for scene in layout if scene["type"] != "outro"]
    timed_scenes = body[1:]
    narrations = [scene.get("narration", "").strip() for scene in timed_scenes]
    durations = scene_duration_frames(narrations, transcription, duration_ms(narration_path))
    body[0]["durationFrames"] = COVER_FRAMES
    for scene, duration in zip(timed_scenes, durations):
        scene["durationFrames"] = duration
    outro = layout[-1]
    resolved = [*body, outro]
    outro_start = sum(scene["durationFrames"] for scene in body)

    data["scenes"] = resolved
    data["audio"] = {
        "voiceover": {"src": "generated/narration.wav", "volume": 1, "startFrame": COVER_FRAMES},
        "outro": {"src": "generated/outro-voice.wav", "volume": 1, "startFrame": outro_start},
    }
    layout_path.write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(data_path, ROOT / "generated" / "resolved-video-data.json")
    print("scene_frames=" + ",".join(str(value) for value in durations))
    print(f"outro_start={outro_start}")


if __name__ == "__main__":
    main()
