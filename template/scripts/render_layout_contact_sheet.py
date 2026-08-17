#!/usr/bin/env python3
import json
import math
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "check" / "layout-contact-sheet"
OUTPUT = ROOT / "check" / "layout-contact-sheet.png"


scenes = json.loads((ROOT / "layout-scenes.json").read_text(encoding="utf-8"))
shutil.rmtree(FRAMES, ignore_errors=True)
FRAMES.mkdir(parents=True)

start = 0
for index, scene in enumerate(scenes):
    duration = scene["durationFrames"]
    sample_ratio = 0.55 if scene["type"] in {"intro", "outro"} else 0.72
    frame = start + round(duration * sample_ratio)
    target = FRAMES / f"{index:02d}-{scene['type']}.png"
    subprocess.run(
        ["npx", "remotion", "still", "VideoTemplate", str(target), "--frame", str(frame), "--overwrite"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        check=True,
    )
    start += duration

rows = math.ceil(len(scenes) / 5)
subprocess.run(
    [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-pattern_type", "glob", "-i", str(FRAMES / "*.png"),
        "-vf", f"scale=270:360,tile=5x{rows}:padding=8:margin=8:color=0x202020",
        "-frames:v", "1", str(OUTPUT),
    ],
    check=True,
)

print(OUTPUT)
