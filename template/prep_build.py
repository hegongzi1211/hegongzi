#!/usr/bin/env python3
"""准备 build_video.py 缓存命中：算出与音频同源的 cache key，并同步音频到 public/generated。"""
import sys, hashlib, json, importlib.util, subprocess
from pathlib import Path

ROOT = Path("/WorkBuddy/2026-07-09-11-00-55/hgz-sp-moban-remotion")
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("bv", str(ROOT / "scripts" / "build_video.py"))
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)

# 1) 复现 build_video.py 的 scenes 编译 + 校验
data = json.loads((ROOT / "video-data.json").read_text(encoding="utf-8"))
outline = json.loads((ROOT / "content-outline.json").read_text(encoding="utf-8"))
scenes_path = ROOT / "layout-scenes.json"
if scenes_path.exists():
    data["scenes"] = json.loads(scenes_path.read_text(encoding="utf-8"))
data["scenes"] = bv.compile_document(outline, data["scenes"])
print("compiled scene types:", [s["type"] for s in data["scenes"]])
for i, s in enumerate(data["scenes"]):
    if s["type"] == "skill_detail":
        print(f"  scene {i+1} skill_detail details={len(s.get('details', []))} name={s.get('skillName')}")
    elif s["type"] == "overview":
        print(f"  scene {i+1} overview items={len(s.get('items', []))}")
bv.validate_scenes(data["scenes"])
print("validate_scenes: PASS")

# 2) 复现 cache key 计算
body_scenes = [s for s in data["scenes"] if s["type"] != "outro"]
narrations = [s.get("narration", "").strip() for s in body_scenes]
narration_text = "".join(narrations[1:])
VOICE_CONFIG = bv.VOICE_CONFIG
VOICE_SCRIPT = bv.VOICE_SCRIPT
VOICE_FILTER = bv.VOICE_FILTER
cache_key = hashlib.sha256(
    narration_text.encode("utf-8")
    + VOICE_CONFIG.read_bytes()
    + VOICE_SCRIPT.read_bytes()
    + VOICE_FILTER.encode("utf-8")
).hexdigest()
(ROOT / "generated" / "narration-cache.json").write_text(
    json.dumps({"key": cache_key}, indent=2) + "\n", encoding="utf-8")
print(f"narration_text_len={len(narration_text)}")
print(f"cache_key={cache_key}")
print(f"existing generated/narration.txt len={ (ROOT/'generated'/'narration.txt').read_text(encoding='utf-8').__len__() if (ROOT/'generated'/'narration.txt').exists() else 'MISSING'}")

# 3) 同步音频到 public/generated/narration.wav（与 generated/narration.wav 同源）
raw = ROOT / "generated" / "narration-raw.wav"
pub = ROOT / "public" / "generated" / "narration.wav"
subprocess.run(
    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
     "-i", str(raw), "-af", "aresample=48000", "-c:a", "pcm_s16le", str(pub)],
    check=True)
print(f"public/generated/narration.wav written: {pub.stat().st_size} bytes")
print("PREP DONE")
