# -*- coding: utf-8 -*-
"""一次性重建完整视频数据（绕过被覆盖的残缺版）：
- 从 skill_content.json（干净完整源）+ layout-scenes.json.bak（视觉模板）重建 layout-scenes.json
- 14 场景：intro / hook / workflow / 10×skill_detail / outro
- 帧数按各场景旁白字数比例，总帧 = narration.wav 时长 × 30，与音频严丝合缝
- 从完整旁白文本生成字幕 captions（按句切分，时间比例对齐 0~音频时长），写入 video-data.json
"""
import json, os, re, subprocess

D = "/WorkBuddy/2026-07-09-11-00-55/hgz-sp-moban-remotion"
FPS = 30
WAV = os.path.join(D, "generated/narration.wav")

content = json.load(open(os.path.join(D, "skill_content.json"), encoding="utf-8"))
SKILLS = content["skills"]
INTRO = content["intro"]; HOOK = content["hook"]; WORKFLOW = content["workflow"]; OUTRO = content["outro"]

# 视觉模板（含 workflow）来自 .bak
bak = json.load(open(os.path.join(D, "layout-scenes.json.bak"), encoding="utf-8"))
tpl = {}
for s in bak:
    tpl.setdefault(s["type"], []).append(s)
intro_tpl = tpl["intro"][0]; hook_tpl = tpl["hook"][0]
workflow_tpl = tpl["workflow"][0]; outro_tpl = tpl["outro"][0]

def skill_narration(s):
    return (f"第 {s['num']} 个必装 Skill，{s['name']}。{s['oneLine']}。"
            f"我觉得最有用的点：{s['useful']}"
            f"它像什么？{s['like']}"
            f"主要用途：{s['usage']}。"
            f"推荐搭配：{s['pairing']}"
            f"注意事项：{s['caution']}"
            f"我的结论：{s['conclusion']}")

MAIN_COLORS = ["#FFA500", "#00FFFF", "#39FF14", "#FF1493", "#8B5CF6",
               "#FFD700", "#FF6B6B", "#4ECDC4", "#FF69B4", "#A78BFA"]
DETAIL_COLORS = ["#39FF14", "#00FFFF", "#FF1493", "#FFA500", "#FF69B4", "#FFFF00"]
DETAIL_LABELS = ["我觉得最有用的点", "像什么", "主要用途", "推荐搭配", "注意事项", "我的结论"]

# ---------- 生成完整旁白文本 narration.txt（与 narration.wav 同源） ----------
narration_full = INTRO + HOOK + WORKFLOW
for s in SKILLS:
    narration_full += skill_narration(s)
narration_full += OUTRO
with open(os.path.join(D, "generated/narration.txt"), "w", encoding="utf-8") as f:
    f.write(narration_full)
print("narration.txt 长度:", len(narration_full))

# ---------- 构建 14 场景 ----------
scenes = []
intro = dict(intro_tpl); intro["narration"] = INTRO; scenes.append(intro)
hook = dict(hook_tpl); hook["narration"] = HOOK; scenes.append(hook)
wf = dict(workflow_tpl); wf["narration"] = WORKFLOW; scenes.append(wf)
for i, s in enumerate(SKILLS):
    vals = [s["useful"], s["like"], s["usage"], s["pairing"], s["caution"], s["conclusion"]]
    details = [{"text": lab, "color": DETAIL_COLORS[j], "label": "说明", "value": v}
               for j, (lab, v) in enumerate(zip(DETAIL_LABELS, vals))]
    scenes.append({
        "type": "skill_detail",
        "durationFrames": 0,
        "showSubtitle": True,
        "skillNum": s["num"],
        "skillName": s["name"],
        "desc": s["oneLine"],
        "mainColor": MAIN_COLORS[i % len(MAIN_COLORS)],
        "details": details,
        "supportText": s["conclusion"],
        "narration": skill_narration(s),
    })
outro = dict(outro_tpl); outro["narration"] = OUTRO; scenes.append(outro)
assert len(scenes) == 14, len(scenes)

# 帧数按比例
texts = [INTRO, HOOK, WORKFLOW] + [sc["narration"] for sc in scenes[3:13]] + [OUTRO]
assert len(texts) == 14
dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", WAV]))
total_frames = int(round(dur * FPS))
print("音频时长(秒):", round(dur, 2), "| 总帧:", total_frames)
total_chars = sum(len(t) for t in texts)
for sc, t in zip(scenes, texts):
    sc["durationFrames"] = max(45, int(round(len(t) / total_chars * total_frames)))
actual = sum(sc["durationFrames"] for sc in scenes)
print("分配后总帧:", actual, "| 场景数:", len(scenes))
print("各场景帧:", [sc["durationFrames"] for sc in scenes])

# ---------- 生成字幕 captions（按句切，时间比例对齐音频） ----------
sentences = re.split(r'(?<=[。！？!?])', narration_full)
sentences = [s.strip() for s in sentences if s.strip()]
total_ms = int(round(dur * 1000))
caps = []
cum = 0
for s in sentences:
    dur_ms = len(s) / len(narration_full) * total_ms
    caps.append({"text": s, "startMs": int(round(cum)), "endMs": int(round(cum + dur_ms))})
    cum += dur_ms
# 修正末条结束时间
caps[-1]["endMs"] = total_ms
print("字幕条数:", len(caps), "| 时间跨度(秒):", caps[-1]["endMs"]/1000)

# ---------- 写出 ----------
with open(os.path.join(D, "layout-scenes.json"), "w", encoding="utf-8") as f:
    json.dump(scenes, f, ensure_ascii=False, indent=1)
print("layout-scenes.json 已写 (14 场景)")

video_data = {
    "title": "Codex 做自媒体必装十大 Skill",
    "audio": {
        "voiceover": {"src": "generated/narration.wav", "volume": 1, "startFrame": 45},
    },
    "captions": caps,
    "scenes": scenes,
}
with open(os.path.join(D, "video-data.json"), "w", encoding="utf-8") as f:
    json.dump(video_data, f, ensure_ascii=False, indent=1)
print("video-data.json 已写 (含字幕)")
