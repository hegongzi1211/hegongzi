#!/usr/bin/env python3
"""Re-align scene durationFrames to REAL per-scene audio durations.

Root cause of the desync: build_per_scene.py computed each scene's
durationFrames from a *character-ratio* of the full whisper timeline,
but TTS per-scene speed/pauses vary, so the visual cut points drifted
far from the real audio segment boundaries (e.g. scene[9] got 21.0s of
visual but only 11.4s of audio -> 9.6s of wrong visual over correct audio).

Fix: set durationFrames = round(real_audio_seconds * FPS) per scene, using
the exact audio-segment mapping used at concat time:
  - intro  (layout[0])  : cover-only, COVER_FRAMES (no audio)
  - hook   (layout[1])  : audio = scene-00.wav + scene-01.wav  (cover VO + hook VO)
  - layout[i] (i>=2)    : audio = scene-{i:02d}.wav
  - outro  (last)       : locked 105 frames
This makes visual scene boundaries == audio segment boundaries, so audio,
captions (already bound to the real audio timeline) and visuals all sync.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FPS = 30
COVER_FRAMES = 45


def wav_seconds(p: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main() -> None:
    layout = json.loads((ROOT / "layout-scenes.json").read_text(encoding="utf-8"))
    # body = all except outro (last)
    outro = layout[-1]
    body = layout[:-1]  # 14 entries: layout[0..13]
    n = len(body)
    assert n == 14, f"expected 14 body scenes, got {n}"

    # read real per-scene wav durations (scene-00 .. scene-(n-1))
    wavs = [(ROOT / "generated" / f"scene-{i:02d}.wav") for i in range(n)]
    for w in wavs:
        if not w.exists():
            raise SystemExit(f"missing audio segment: {w}")
    durs = [wav_seconds(w) for w in wavs]  # seconds per body scene audio

    # assign durationFrames
    # intro cover
    body[0]["durationFrames"] = COVER_FRAMES
    # hook = cover VO + hook VO
    hook_sec = durs[0] + durs[1]
    body[1]["durationFrames"] = max(45, round(hook_sec * FPS))
    # remaining body scenes
    for i in range(2, n):
        body[i]["durationFrames"] = max(45, round(durs[i] * FPS))
    # outro locked
    outro["durationFrames"] = 105

    layout = body + [outro]

    # recompute outro_start (sum of body frames; voiceover starts at COVER_FRAMES)
    outro_start = sum(s["durationFrames"] for s in body)

    # patch video-data.json audio section + mirror scene durations
    vd = json.loads((ROOT / "video-data.json").read_text(encoding="utf-8"))
    vd["audio"] = {
        "voiceover": {"src": "generated/narration.wav", "volume": 1, "startFrame": COVER_FRAMES},
        "outro": {"src": "generated/outro-voice.wav", "volume": 1, "startFrame": outro_start},
    }
    if "scenes" in vd and len(vd["scenes"]) == len(layout):
        for vs, ls in zip(vd["scenes"], layout):
            vs["durationFrames"] = ls["durationFrames"]

    (ROOT / "layout-scenes.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "video-data.json").write_text(json.dumps(vd, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # report
    print(f"{'idx':>3} {'type':12} {'durFrames':>9} {'sec':>6} {'cumAudioSec':>13}")
    cum = 0.0
    for i, s in enumerate(layout):
        sec = s["durationFrames"] / FPS
        if i == 0:
            cumstr = "(cover)"
        elif i == 1:
            cum = durs[0] + durs[1]
            cumstr = f"{cum:.2f}"
        elif i < len(body):
            cum += durs[i]
            cumstr = f"{cum:.2f}"
        else:
            cumstr = "(outro)"
        print(f"{i:>3} {s['type']:12} {s['durationFrames']:>9} {sec:>6.2f} {cumstr:>13}")
    total = sum(s["durationFrames"] for s in layout)
    print(f"TOTAL frames={total} => {total/FPS:.2f}s | outro_start(frame)={outro_start} | narration={sum(durs):.2f}s")


if __name__ == "__main__":
    main()
