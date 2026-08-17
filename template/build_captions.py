# -*- coding: utf-8 -*-
"""分片 whisper 生成字幕 captions.json，写入 video-data.json。
每片 60s 独立跑（杜绝长音频幻觉循环），片段时间戳按绝对偏移拼接。"""
import json, subprocess, os, math

D = "/WorkBuddy/2026-07-09-11-00-55/hgz-sp-moban-remotion"
WAV = os.path.join(D, "generated/narration.wav")
MODEL = "/.cache/hyperframes/whisper/models/ggml-small.bin"
CHUNK = 60  # 秒
TMP = "/tmp/wh_chunks"
os.makedirs(TMP, exist_ok=True)

# 音频时长
dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", WAV]))
n = math.ceil(dur / CHUNK)
print(f"音频 {dur:.1f}s，分 {n} 片")

segments = []
for i in range(n):
    cwav = os.path.join(TMP, f"chunk_{i}.wav")
    coff = i * CHUNK * 1000  # 毫秒绝对偏移
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-i", WAV, "-ss", str(i * CHUNK), "-t", str(CHUNK),
         "-ar", "16000", "-ac", "1", cwav],
        check=True)
    out = os.path.join(TMP, f"chunk_{i}")
    r = subprocess.run(
        ["/opt/homebrew/bin/whisper-cli", "-m", MODEL, "-l", "zh",
         "-f", cwav, "-ojf", "-ml", "14", "-sow", "-of", out, "--no-prints"],
        capture_output=True, text=True)
    jp = out + ".json"
    if not os.path.exists(jp):
        print(f"片 {i} 无输出，跳过"); continue
    d = json.load(open(jp, encoding="utf-8"))
    tr = d.get("transcription", [])
    cnt = 0
    for seg in tr:
        txt = (seg.get("text") or "").strip()
        if not txt:
            continue
        off = seg.get("offsets", {})
        f = off.get("from", 0) + coff
        t = off.get("to", 0) + coff
        if t <= f:
            t = f + 800
        segments.append({"text": txt, "startMs": f, "endMs": t})
        cnt += 1
    print(f"片 {i}: {cnt} 段")
    os.remove(cwav)

# 去相邻重复（同文本连续段）
clean = []
for seg in segments:
    if clean and clean[-1]["text"] == seg["text"] and seg["startMs"] - clean[-1]["endMs"] < 1500:
        clean[-1]["endMs"] = max(clean[-1]["endMs"], seg["endMs"])
    else:
        clean.append(seg)

print(f"总字幕段: {len(clean)} | 首: {clean[0]['text'][:20]} | 末: {clean[-1]['text'][:20]}")
print(f"字幕时间跨度: {clean[0]['startMs']} -> {clean[-1]['endMs']} ms")

# 写回 video-data.json
vdp = os.path.join(D, "video-data.json")
vd = json.load(open(vdp, encoding="utf-8"))
vd["captions"] = clean
json.dump(vd, open(vdp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("video-data.json captions 已写")
