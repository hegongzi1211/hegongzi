#!/usr/bin/env python3
"""分段重跑 whisper，规避长音频幻觉循环，拼回标准 narration-timing.json。"""
import json
import subprocess
from pathlib import Path

ROOT = Path("/WorkBuddy/2026-07-09-11-00-55/hgz-sp-moban-remotion")
SRC = ROOT / "generated" / "narration-16k.wav"
MODEL = Path("/.cache/hyperframes/whisper/models/ggml-small.bin")
CHUNK_DIR = ROOT / "generated" / "whisper_chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)
CHUNK_SEC = 60

dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=nw=1:nk=1", str(SRC)]).strip())
n = int(dur // CHUNK_SEC) + (1 if dur % CHUNK_SEC else 0)
print(f"audio duration={dur:.1f}s  chunks={n}")

# 1) 切分（不重编码，保持时间精确）
chunk_paths = []
for i in range(n):
    start = i * CHUNK_SEC
    out = CHUNK_DIR / f"chunk_{i:02d}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-ss", str(start), "-t", str(CHUNK_SEC), "-i", str(SRC),
         "-acodec", "copy", str(out)], check=True)
    chunk_paths.append(out)
print("split done")

# 2) 逐片独立跑 whisper（片间无上下文，避免循环）
transcription = []
for i, cp in enumerate(chunk_paths):
    start_ms = i * CHUNK_SEC * 1000
    base = CHUNK_DIR / f"chunk_{i:02d}"
    subprocess.run(
        ["whisper-cli", "-m", str(MODEL), "-l", "zh", "-f", str(cp),
         "-ojf", "-ml", "14", "-sow", "-t", "8", "-of", str(base), "--no-prints"],
        check=True)
    d = json.loads((base.with_suffix(".json")).read_text(encoding="utf-8"))
    segs = d.get("transcription", [])
    # 检测本片是否陷入重复循环
    texts = [s["text"] for s in segs]
    loop_hit = any(texts.count(t) > 8 for t in set(texts) if t.strip())
    for seg in segs:
        seg["offsets"]["from"] += start_ms
        seg["offsets"]["to"] += start_ms
        for tok in seg.get("tokens") or []:
            tok["offsets"]["from"] += start_ms
            tok["offsets"]["to"] += start_ms
        transcription.append(seg)
    print(f"chunk {i:02d}: segs={len(segs)} {'LOOP!' if loop_hit else 'ok'}")

# 3) 拼回标准结构（脚本只读取 transcription）
merged = {
    "systeminfo": {},
    "model": str(MODEL),
    "params": {},
    "result": "",
    "transcription": transcription,
}
(ROOT / "generated" / "narration-timing.json").write_text(
    json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"MERGED segments={len(transcription)} total_chars={sum(len(s['text']) for s in transcription)}")
print("DONE")
