#!/usr/bin/env python3
"""Per-scene Voicebox generation + ordered concat.

Workaround for Voicebox's long-text continuous generation bug:
sending the full 1172-char narration as one request drops/reorders
the opening scenes. We generate each scene's narration separately
(short text -> no corruption) and concatenate in scene order.
Reuses build_video.py's proven caption/duration math.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_video as bv  # reuse validated helpers

WHISPER_MODEL = Path("/.cache/hyperframes/whisper/models/ggml-small.bin")


def compact(text: str) -> str:
    normalized = text.lower().translate(str.maketrans({"圖": "图", "視": "视", "頻": "频", "來": "来", "個": "个", "說": "说", "開": "开", "關": "关", "學": "学"}))
    return "".join(c for c in normalized if c.isalnum() or "\u4e00" <= c <= "\u9fff")


def get_json(url: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def ensure_service(url: str) -> None:
    try:
        get_json(f"{url}/health")
    except urllib.error.URLError:
        subprocess.run(["open", "-a", "Voicebox"], check=True)
        time.sleep(3)
        get_json(f"{url}/health")


def _digit_variants(text: str) -> set:
    """数字读法归一化候选：缓解 whisper 把 '10' 听成 '十' 等差异。"""
    import re
    out = set()
    cn = {"0": "零", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五",
          "6": "六", "7": "七", "8": "八", "9": "九"}
    for m in re.finditer(r"\d+", text):
        digits = m.group(0)
        if len(digits) == 1:
            out.add(text[:m.start()] + cn[digits] + text[m.end():])
        elif digits == "10":
            out.add(text[:m.start()] + "十" + text[m.end():])
    for cn_char, ar in [("十", "10"), ("一", "1"), ("二", "2"), ("两", "2"),
                        ("三", "3"), ("四", "4"), ("五", "5"), ("六", "6"),
                        ("七", "7"), ("八", "8"), ("九", "9"), ("零", "0")]:
        if cn_char in text:
            idx = text.index(cn_char)
            out.add(text[:idx] + ar + text[idx + 1:])
    return out


def find_spoken_start(raw: Path, intended_text: str, tmp: Path) -> float:
    mono = tmp / "raw-16k.wav"
    transcript_base = tmp / "raw-transcript"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", "16000", str(mono)], check=True)
    subprocess.run(["whisper-cli", "-m", str(WHISPER_MODEL), "-l", "zh", "-f", str(mono), "-ojf", "-of", str(transcript_base), "--no-prints"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    transcription = json.loads(transcript_base.with_suffix(".json").read_text(encoding="utf-8"))["transcription"]
    if not transcription:
        return 0.0
    c = compact(intended_text)
    candidates = set()
    for L in (8, 6, 5, 4, 3, 2):
        if len(c) >= L:
            candidates.add(c[:L])
    candidates |= _digit_variants(c)
    for item in transcription:
        spoken = compact(item["text"])
        for cand in candidates:
            if cand and cand in spoken:
                return max(0.0, item["offsets"]["from"] / 1000 - 0.04)
            if len(spoken) >= 2 and spoken[:2] in cand:
                return max(0.0, item["offsets"]["from"] / 1000 - 0.04)
    # 降级：取第一个有内容的语音片段起点，绝不因精确匹配失败而崩溃
    return max(0.0, transcription[0]["offsets"]["from"] / 1000 - 0.04)


def generate_scene(cfg: dict, text: str) -> Path:
    base = cfg["service_url"].rstrip("/")
    payload = {
        "profile_id": cfg["profile_id"],
        "text": text,
        "language": cfg["language"],
        "seed": cfg["seed"],
        "model_size": cfg["model_size"],
        "engine": cfg["engine"],
        "max_chunk_chars": cfg["max_chunk_chars"],
        "crossfade_ms": cfg["crossfade_ms"],
        "normalize": cfg["normalize"],
    }
    generation = get_json(f"{base}/generate", payload)
    deadline = time.time() + 900
    while time.time() < deadline:
        state = get_json(f"{base}/history/{generation['id']}")
        if state["status"] == "completed":
            break
        if state["status"] == "failed":
            raise SystemExit(f"Voicebox生成失败：{state.get('error')}")
        time.sleep(2)
    else:
        raise SystemExit("Voicebox生成超时")
    raw = Path(tempfile.mktemp(suffix=".wav"))
    with urllib.request.urlopen(f"{base}/audio/{generation['id']}", timeout=60) as response:
        raw.write_bytes(response.read())
    return raw


def main() -> None:
    cfg = json.loads((ROOT / "audio-pipeline.json").read_text(encoding="utf-8"))
    provider = cfg.get("provider")
    if provider not in ("voicebox_local", "volcengine"):
        raise SystemExit("当前Remotion模板只允许 voicebox_local 或 volcengine 配音方案")
    if provider == "voicebox_local":
        ensure_service(cfg["service_url"].rstrip("/"))

    scenes = json.loads((ROOT / "layout-scenes.json").read_text(encoding="utf-8"))
    bv.validate_scenes(scenes)
    body = [s for s in scenes if s["type"] != "outro"]
    narrations = [s.get("narration", "").strip() for s in body]
    if not all(narrations):
        missing = [str(i + 1) for i, v in enumerate(narrations) if not v]
        raise SystemExit(f"Scenes missing narration: {', '.join(missing)}")

    scene_audios: list[Path] = []
    for i, (scene, nar) in enumerate(zip(body, narrations)):
        print(f"[scene {i + 1}/{len(body)}] {scene['type']} generating...", flush=True)
        out = ROOT / "generated" / f"scene-{i:02d}.wav"
        if provider == "volcengine":
            # ve_generate.py 已直接输出 48k 单声道成品 wav（含 postprocess 与首静音裁切）
            tmp_txt = ROOT / "generated" / f"scene-{i:02d}.txt"
            tmp_txt.write_text(nar, encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "scripts" / "ve_generate.py"),
                            "--text-file", str(tmp_txt), "--output", str(out)], check=True)
        else:
            raw = generate_scene(cfg, nar)
            with tempfile.TemporaryDirectory() as tmp_name:
                tmp = Path(tmp_name)
                trim = find_spoken_start(raw, nar, tmp)
                subprocess.run([
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(raw),
                    "-af", f"atrim=start={trim:.3f},asetpts=PTS-STARTPTS,aresample=48000",
                    "-ar", "48000", "-ac", "1", str(out),
                ], check=True)
        scene_audios.append(out)
        print(f"[scene {i + 1}/{len(body)}] done -> {out.name}", flush=True)

    # ordered concat
    final = ROOT / "public" / "generated" / "narration.wav"
    final.parent.mkdir(parents=True, exist_ok=True)
    listfile = ROOT / "generated" / "scene-list.txt"
    listfile.write_text("\n".join(f"file '{a}'" for a in scene_audios), encoding="utf-8")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(final)], check=True)

    # whisper + captions (same pipeline as build_video)
    w16 = ROOT / "generated" / "narration-16k.wav"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(final), "-ac", "1", "-ar", "16000", str(w16)], check=True)
    wbase = ROOT / "generated" / "narration-timing"
    subprocess.run(["whisper-cli", "-m", str(WHISPER_MODEL), "-l", "zh", "-f", str(w16), "-ojf", "-ml", "14", "-sow", "-of", str(wbase), "--no-prints"], check=True)

    timing = json.loads(wbase.with_suffix(".json").read_text(encoding="utf-8"))
    transcription = timing["transcription"]
    transcript_text = "".join(item["text"] for item in transcription)
    contamination = [p for p in bv.BAD_VOICE_PATTERNS if p in transcript_text]
    if contamination:
        raise SystemExit(f"Voicebox整条旁白仍有参考污染，已拒绝渲染：{', '.join(contamination)}")

    total_ms = bv.duration_ms(final)
    narration_text = "".join(narrations)
    data = json.loads((ROOT / "video-data.json").read_text(encoding="utf-8"))
    data["captions"] = bv.make_timeline(narration_text, transcription, total_ms)

    if body[0]["type"] != "intro" or len(body) < 2:
        raise SystemExit("The first scene must be an intro cover followed by a body scene")

    # --- DURATIONS FROM REAL AUDIO (fixes char-ratio desync) ---
    # mapping (same as concat order): hook(body[1]) = scene-00 + scene-01 ;
    # body[i>=2] = scene-{i:02d}. So each scene's visual window exactly
    # equals its real audio segment -> captions/audio/visual all sync.
    def _wav_sec(p: Path) -> float:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
            capture_output=True, text=True, check=True,
        )
        return float(out.stdout.strip())

    seg_sec = [_wav_sec(a) for a in scene_audios]  # per body scene audio (seconds)
    body[0]["durationFrames"] = bv.COVER_FRAMES  # cover-only, no audio
    hook_sec = seg_sec[0] + seg_sec[1]
    body[1]["durationFrames"] = max(45, round(hook_sec * bv.FPS))
    for i in range(2, len(body)):
        body[i]["durationFrames"] = max(45, round(seg_sec[i] * bv.FPS))
    # ---------------------------------------------------------
    outro_start = sum(scene["durationFrames"] for scene in body)
    data["audio"] = {
        "voiceover": {"src": "generated/narration.wav", "volume": 1, "startFrame": bv.COVER_FRAMES},
        "outro": {"src": "generated/outro-voice.wav", "volume": 1, "startFrame": outro_start},
    }

    (ROOT / "video-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "layout-scenes.json").write_text(json.dumps(scenes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "generated" / "captions.json").write_text(json.dumps(data["captions"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(ROOT / "video-data.json", ROOT / "generated" / "resolved-video-data.json")
    print(f"PER_SCENE_DONE scenes={len(scenes)} audio_ms={total_ms} outro_start_frame={outro_start}")


if __name__ == "__main__":
    main()
